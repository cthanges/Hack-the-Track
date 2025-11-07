# Race Engineer — Streamlit MVP

This is a minimal prototype that replays lap-level CSV data and provides simple pit-window and caution recommendations.

How to run (local):

1. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the Streamlit app:

```powershell
streamlit run app.py
```

Usage notes:
- The app will attempt to find lap_time CSV files under `Datasets/` automatically.
- Select a file and vehicle ID, then step through laps or run a replay. Use the sidebar to tune the target stint and pit cost.

Files created:
- `src/data_loader.py` — helpers to find/load lap_time CSVs.
- `src/simulator.py` — small lap-level replay engine.
- `src/analytics/pit_strategy.py` — naive pit-window heuristic.
- `src/analytics/caution_handler.py` — naive caution rules.

This is an MVP intended for local experimentation. Next steps: add telemetry-level replay, richer degradation/prediction models, and a nicer UI.
