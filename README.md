# Pump TDH Visualizer

An independent visualization application for pump and piping calculations. It uses **Streamlit** for interactive controls and **Matplotlib** for engineering plots.

## Current features

- Choose the horizontal (X) and vertical (Y) chart parameters independently.
- Change the selected flow rate with a slider and highlight the nearest calculated data point.
- Upload calculation results as CSV.
- View key hydraulic values and a simple hydraulic system sketch.
- Keep visualization separate from the calculation engine in `pump-tdh-calculator`.

> The included CSV is illustrative sample data only. It is not a verified pump curve or a site design result.

## Run locally

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install and run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## CSV data interface

The uploaded CSV must contain these columns:

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

The flow slider highlights the nearest row in the supplied dataset. It does not currently interpolate or recalculate hydraulic results. This is deliberate: the visualizer must not silently duplicate the equations in the calculator.

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

1. Validate the first interactive chart and CSV workflow.
2. Define a stable export format in `pump-tdh-calculator`.
3. Connect the visualizer to real calculation outputs.
4. Add scenario comparison and multiple curves.
5. Improve the hydraulic sketch and add chart export.

## Language

See [Persian visualization guide](docs/VISUALIZATION_GUIDE_FA.md).
