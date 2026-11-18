# Pump TDH Visualizer

A standalone desktop visualization application for pump and piping calculations. The graphical interface is built with **PySide6 (Qt)** and charts are rendered with **Matplotlib**.

## Why PySide6?

This is a native desktop application, not a browser-based dashboard. Qt provides resizable windows, desktop controls, file dialogs, tabs and a foundation for richer engineering workflows. Matplotlib is embedded directly in the Qt interface.

## Current features

- Select horizontal (X) and vertical (Y) chart parameters independently.
- Adjust the selected flow rate with a slider and highlight the nearest calculated data point.
- Load calculation results from CSV.
- Matplotlib navigation toolbar (zoom, pan, save).
- Separate tabs for the chart, a conceptual hydraulic sketch and source data.
- Keep visualization separate from the calculation engine in `pump-tdh-calculator`.

> The included CSV is illustrative sample data only. It is not a verified pump curve or a site design result.

## Run locally

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies and launch:

```bash
pip install -r requirements.txt
python app.py
```

## CSV data interface

The CSV must contain these columns:

| Column | Meaning | Unit |
|---|---|---|
| `flow_m3_h` | Flow rate | m³/h |
| `tdh_m` | Total Dynamic Head | m |
| `velocity_m_s` | Pipe velocity | m/s |
| `major_loss_m` | Major head loss | m |
| `minor_loss_m` | Minor head loss | m |
| `hydraulic_power_kw` | Hydraulic power | kW |
| `shaft_power_kw` | Shaft power | kW |
| `electrical_power_kw` | Electrical input power | kW |
| `pump_efficiency_pct` | Pump efficiency | % |

The slider currently selects the nearest row in the loaded dataset. It does not interpolate or recalculate hydraulic results. The next integration step is to define a calculation-sweep export in `pump-tdh-calculator`, then connect the actual calculation engine.

## Project structure

```text
pump-tdh-visualizer/
├── app.py
├── requirements.txt
├── examples/
│   └── sample_results.csv
└── docs/
    └── VISUALIZATION_GUIDE_FA.md
```

## Roadmap

1. Validate the desktop GUI and CSV workflow.
2. Define a stable calculation-sweep export format.
3. Recalculate hydraulic results when flow changes.
4. Add scenario comparison, pump/system curves and multiple axes.
5. Improve the hydraulic sketch and add chart export.

See [Persian visualization guide](docs/VISUALIZATION_GUIDE_FA.md).
