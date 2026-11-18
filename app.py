from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

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


@st.cache_data
def load_sample_data():
    return pd.read_csv(SAMPLE_FILE)


def make_chart(data: pd.DataFrame, x_col: str, y_col: str, selected_flow: float):
    fig, ax = plt.subplots(figsize=(10, 5.8))
    ordered = data.sort_values(x_col)
    ax.plot(ordered[x_col], ordered[y_col], marker="o", linewidth=2, label="Calculated data")

    nearest = (data["flow_m3_h"] - selected_flow).abs().idxmin()
    point = data.loc[nearest]
    ax.scatter(
        [point[x_col]],
        [point[y_col]],
        s=110,
        zorder=5,
        label=f"Selected Q ≈ {point['flow_m3_h']:.1f} m³/h",
    )
    ax.annotate(
        f"Q = {point['flow_m3_h']:.1f} m³/h\n{point[y_col]:.3g}",
        (point[x_col], point[y_col]),
        xytext=(10, 12),
        textcoords="offset points",
    )
    ax.set_xlabel(next(label for label, key in PARAMETERS.items() if key == x_col))
    ax.set_ylabel(next(label for label, key in PARAMETERS.items() if key == y_col))
    ax.set_title("Hydraulic performance")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    return fig, point


def draw_hydraulic_sketch():
    fig, ax = plt.subplots(figsize=(10, 2.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")

    # Source tank
    ax.plot([0.5, 1.7, 1.7, 0.5, 0.5], [0.6, 0.6, 2.2, 2.2, 0.6], linewidth=2)
    ax.plot([0.55, 1.65], [1.25, 1.25], linewidth=1.5)
    ax.text(1.1, 2.45, "Source tank", ha="center")

    # Pipe and pump symbol
    ax.plot([1.7, 3.2], [1.25, 1.25], linewidth=2)
    pump = plt.Circle((3.65, 1.25), 0.42, fill=False, linewidth=2)
    ax.add_patch(pump)
    ax.annotate("", xy=(3.9, 1.25), xytext=(3.45, 1.25),
                arrowprops={"arrowstyle": "->", "linewidth": 1.5})
    ax.text(3.65, 0.55, "Pump", ha="center")

    # Delivery pipe and destination
    ax.plot([4.07, 8.8], [1.25, 1.25], linewidth=2)
    ax.annotate("", xy=(6.0, 1.25), xytext=(5.2, 1.25),
                arrowprops={"arrowstyle": "->", "linewidth": 1.5})
    ax.plot([8.8, 9.5, 9.5, 8.8], [0.6, 0.6, 2.2, 2.2], linewidth=2)
    ax.plot([8.85, 9.45], [1.25, 1.25], linewidth=1.5)
    ax.text(9.15, 2.45, "Destination", ha="center")
    ax.text(6.4, 1.55, "Pipeline", ha="center")
    ax.text(5.1, 0.75, "Flow direction →", ha="center")
    ax.set_title("Simplified hydraulic system sketch")
    fig.tight_layout()
    return fig


st.set_page_config(page_title="Pump TDH Visualizer", page_icon="📈", layout="wide")
st.title("Pump TDH Visualizer")
st.caption("Interactive engineering charts powered by Matplotlib")

with st.sidebar:
    st.header("Data source")
    uploaded = st.file_uploader("Upload calculator results (CSV)", type=["csv"])
    st.caption("Expected columns are listed in the project README.")

try:
    data = pd.read_csv(uploaded) if uploaded is not None else load_sample_data()
except Exception as exc:
    st.error(f"Could not read the CSV file: {exc}")
    st.stop()

missing = [column for column in PARAMETERS.values() if column not in data.columns]
if missing:
    st.error("The CSV is missing required columns: " + ", ".join(missing))
    st.stop()

data = data.dropna(subset=["flow_m3_h"]).sort_values("flow_m3_h")
if len(data) < 2:
    st.error("At least two valid flow-rate rows are required.")
    st.stop()

if uploaded is None:
    st.info("You are viewing illustrative sample data. It is not a verified pump or site calculation.")

st.subheader("Interactive chart")
col_x, col_y = st.columns(2)
with col_x:
    x_label = st.selectbox("Horizontal axis (X)", list(PARAMETERS), index=0)
with col_y:
    y_label = st.selectbox("Vertical axis (Y)", list(PARAMETERS), index=1)

min_flow = float(data["flow_m3_h"].min())
max_flow = float(data["flow_m3_h"].max())
default_flow = min(max(150.0, min_flow), max_flow)
selected_flow = st.slider(
    "Change flow rate (m³/h)",
    min_value=min_flow,
    max_value=max_flow,
    value=default_flow,
    step=max((max_flow - min_flow) / 100, 0.1),
)

fig, selected = make_chart(
    data,
    PARAMETERS[x_label],
    PARAMETERS[y_label],
    selected_flow,
)
st.pyplot(fig, use_container_width=True)
plt.close(fig)

metric_cols = st.columns(4)
metric_cols[0].metric("Nearest flow", f"{selected['flow_m3_h']:.2f} m³/h")
metric_cols[1].metric("TDH", f"{selected['tdh_m']:.2f} m")
metric_cols[2].metric("Velocity", f"{selected['velocity_m_s']:.2f} m/s")
metric_cols[3].metric("Hydraulic power", f"{selected['hydraulic_power_kw']:.2f} kW")

with st.expander("Show selected row and source data"):
    st.write("The marker snaps to the nearest available CSV row; it does not interpolate new hydraulic results.")
    st.dataframe(data, use_container_width=True)

st.subheader("Hydraulic sketch")
sketch = draw_hydraulic_sketch()
st.pyplot(sketch, use_container_width=True)
plt.close(sketch)

st.caption("Next integration step: export calculation sweeps from pump-tdh-calculator in this CSV format.")
