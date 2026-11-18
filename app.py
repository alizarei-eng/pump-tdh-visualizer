from pathlib import Path
import sys

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QMainWindow, QMessageBox, QPushButton,
    QSlider, QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from matplotlib.patches import Circle

ROOT = Path(__file__).parent
SAMPLE_FILE = ROOT / "examples" / "sample_results.csv"

PARAMETERS = {
    "Flow rate (m³/h)": "flow_m3_h",
    "Total Dynamic Head (m)": "tdh_m",
    "Velocity (m/s)": "velocity_m_s",
    "Major head loss (m)": "major_loss_m",
    "Minor head loss (m)": "minor_loss_m",
    "Hydraulic power (kW)": "hydraulic_power_kw",
    "Shaft power (kW)": "shaft_power_kw",
    "Electrical power (kW)": "electrical_power_kw",
    "Pump efficiency (%)": "pump_efficiency_pct",
}


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, width=9, height=5, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        super().__init__(self.figure)


class PumpVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pump TDH Visualizer")
        self.resize(1250, 850)
        self.data = pd.read_csv(SAMPLE_FILE)
        self.data_path = "Illustrative sample data"
        self._build_ui()
        self._validate_data()
        self._configure_flow_slider()
        self.update_chart()
        self.update_sketch()
        self.update_table()

    def _build_ui(self):
        central = QWidget()
        root = QVBoxLayout(central)

        header = QHBoxLayout()
        title = QLabel("PUMP TDH VISUALIZER")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")
        self.source_label = QLabel(self.data_path)
        self.source_label.setStyleSheet("color: #64748b;")
        load_button = QPushButton("Load CSV…")
        load_button.clicked.connect(self.load_csv)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.source_label)
        header.addWidget(load_button)
        root.addLayout(header)

        controls = QGroupBox("Chart configuration")
        grid = QGridLayout(controls)
        self.x_combo = QComboBox()
        self.y_combo = QComboBox()
        self.x_combo.addItems(PARAMETERS.keys())
        self.y_combo.addItems(PARAMETERS.keys())
        self.x_combo.setCurrentIndex(0)
        self.y_combo.setCurrentIndex(1)
        self.x_combo.currentIndexChanged.connect(self.update_chart)
        self.y_combo.currentIndexChanged.connect(self.update_chart)
        grid.addWidget(QLabel("Horizontal axis (X)"), 0, 0)
        grid.addWidget(self.x_combo, 0, 1)
        grid.addWidget(QLabel("Vertical axis (Y)"), 0, 2)
        grid.addWidget(self.y_combo, 0, 3)

        self.flow_label = QLabel("Selected flow rate")
        self.flow_value = QLabel("—")
        self.flow_value.setStyleSheet("font-size: 17px; font-weight: 700;")
        self.flow_slider = QSlider(Qt.Horizontal)
        self.flow_slider.valueChanged.connect(self._on_slider_changed)
        grid.addWidget(self.flow_label, 1, 0)
        grid.addWidget(self.flow_slider, 1, 1, 1, 2)
        grid.addWidget(self.flow_value, 1, 3)
        root.addWidget(controls)

        self.tabs = QTabWidget()
        chart_page = QWidget()
        chart_layout = QVBoxLayout(chart_page)
        self.chart_canvas = MplCanvas()
        self.toolbar = NavigationToolbar2QT(self.chart_canvas, self)
        chart_layout.addWidget(self.toolbar)
        chart_layout.addWidget(self.chart_canvas)
        self.metrics = QLabel()
        self.metrics.setStyleSheet(
            "padding: 10px; background: #eef2f7; border-radius: 6px; font-size: 13px;"
        )
        chart_layout.addWidget(self.metrics)
        self.tabs.addTab(chart_page, "Interactive chart")

        sketch_page = QWidget()
        sketch_layout = QVBoxLayout(sketch_page)
        self.sketch_canvas = MplCanvas(height=3)
        sketch_layout.addWidget(self.sketch_canvas)
        sketch_layout.addWidget(QLabel(
            "Conceptual schematic only — not a scaled piping or construction drawing."
        ))
        self.tabs.addTab(sketch_page, "Hydraulic sketch")

        table_page = QWidget()
        table_layout = QVBoxLayout(table_page)
        self.table = QTableWidget()
        table_layout.addWidget(self.table)
        self.tabs.addTab(table_page, "Source data")
        root.addWidget(self.tabs, 1)

        self.setCentralWidget(central)
        self.statusBar().showMessage("Ready")

    def _validate_data(self):
        missing = [col for col in PARAMETERS.values() if col not in self.data.columns]
        if missing:
            raise ValueError("CSV is missing columns: " + ", ".join(missing))
        self.data = self.data.dropna(subset=["flow_m3_h"]).copy()
        self.data = self.data.sort_values("flow_m3_h").reset_index(drop=True)
        if len(self.data) < 2:
            raise ValueError("At least two valid flow-rate rows are required.")

    def _configure_flow_slider(self):
        self.min_flow = float(self.data["flow_m3_h"].min())
        self.max_flow = float(self.data["flow_m3_h"].max())
        self.flow_slider.setRange(0, 1000)
        initial = min(max(150.0, self.min_flow), self.max_flow)
        self.flow_slider.setValue(round(
            1000 * (initial - self.min_flow) / (self.max_flow - self.min_flow)
        ))
        self._on_slider_changed()

    def selected_flow(self):
        fraction = self.flow_slider.value() / 1000
        return self.min_flow + fraction * (self.max_flow - self.min_flow)

    def _on_slider_changed(self):
        if not hasattr(self, "min_flow"):
            return
        q = self.selected_flow()
        self.flow_value.setText(f"{q:.1f} m³/h")
        self.update_chart()

    def load_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open calculator results", str(ROOT), "CSV files (*.csv)"
        )
        if not path:
            return
        try:
            new_data = pd.read_csv(path)
            old_data = self.data
            self.data = new_data
            self._validate_data()
            self.data_path = Path(path).name
            self.source_label.setText(self.data_path)
            self._configure_flow_slider()
            self.update_table()
            self.update_chart()
            self.statusBar().showMessage(f"Loaded {path}", 5000)
        except Exception as exc:
            self.data = old_data if "old_data" in locals() else self.data
            QMessageBox.critical(self, "CSV loading error", str(exc))

    def update_chart(self, *_):
        if not hasattr(self, "chart_canvas") or not hasattr(self, "min_flow"):
            return
        x_label = self.x_combo.currentText()
        y_label = self.y_combo.currentText()
        x_col, y_col = PARAMETERS[x_label], PARAMETERS[y_label]
        valid = self.data.dropna(subset=[x_col, y_col]).sort_values(x_col)
        fig = self.chart_canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        if valid.empty:
            ax.text(0.5, 0.5, "No valid values for the selected parameters",
                    ha="center", va="center", transform=ax.transAxes)
        else:
            ax.plot(valid[x_col], valid[y_col], marker="o", linewidth=2,
                    label="Calculation data")
            q = self.selected_flow()
            idx = (self.data["flow_m3_h"] - q).abs().idxmin()
            point = self.data.loc[idx]
            if pd.notna(point[x_col]) and pd.notna(point[y_col]):
                ax.scatter([point[x_col]], [point[y_col]], s=115, zorder=5,
                           label=f"Nearest available point: Q={point['flow_m3_h']:.2f}")
                ax.annotate(
                    f"Q = {point['flow_m3_h']:.2f} m³/h\n{y_label}: {point[y_col]:.3g}",
                    (point[x_col], point[y_col]), xytext=(10, 12),
                    textcoords="offset points",
                )
            ax.legend()
            self.metrics.setText(
                f"Nearest data point  |  Q: {point['flow_m3_h']:.2f} m³/h"
                f"    TDH: {point['tdh_m']:.2f} m"
                f"    Velocity: {point['velocity_m_s']:.2f} m/s"
                f"    Hydraulic power: {point['hydraulic_power_kw']:.2f} kW"
            )
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(f"{y_label} vs. {x_label}")
        ax.grid(True, alpha=0.3)
        self.chart_canvas.draw_idle()

    def update_sketch(self):
        fig = self.sketch_canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 3)
        ax.axis("off")
        ax.plot([0.5, 1.7, 1.7, 0.5, 0.5], [0.6, 0.6, 2.2, 2.2, 0.6], lw=2)
        ax.plot([0.55, 1.65], [1.25, 1.25], lw=1.5)
        ax.text(1.1, 2.45, "Source tank", ha="center")
        ax.plot([1.7, 3.2], [1.25, 1.25], lw=2)
        ax.add_patch(Circle((3.65, 1.25), 0.42, fill=False, lw=2))
        ax.annotate("", xy=(3.9, 1.25), xytext=(3.45, 1.25),
                    arrowprops={"arrowstyle": "->", "lw": 1.5})
        ax.text(3.65, 0.55, "Pump", ha="center")
        ax.plot([4.07, 8.8], [1.25, 1.25], lw=2)
        ax.annotate("", xy=(6.0, 1.25), xytext=(5.2, 1.25),
                    arrowprops={"arrowstyle": "->", "lw": 1.5})
        ax.plot([8.8, 9.5, 9.5, 8.8], [0.6, 0.6, 2.2, 2.2], lw=2)
        ax.plot([8.85, 9.45], [1.25, 1.25], lw=1.5)
        ax.text(9.15, 2.45, "Destination", ha="center")
        ax.text(6.4, 1.55, "Pipeline", ha="center")
        ax.set_title("Simplified hydraulic system")
        self.sketch_canvas.draw_idle()

    def update_table(self):
        if not hasattr(self, "table"):
            return
        self.table.setRowCount(len(self.data))
        self.table.setColumnCount(len(self.data.columns))
        self.table.setHorizontalHeaderLabels([str(c) for c in self.data.columns])
        for row_idx, (_, row) in enumerate(self.data.iterrows()):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.table.setItem(row_idx, col_idx, item)
        self.table.resizeColumnsToContents()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = PumpVisualizer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
