# Race Engineer — Streamlit MVP

Real-time analytics tool that simulates race-engineering decision-making for optimal pit strategy and caution responses.

## Features

### Race Strategy
- **Optimal Pit Window Calculator**: Multi-lap optimizer that evaluates candidate pit stops and selects the timing that minimizes total race time
- **Tyre Degradation Model**: Linear degradation model (configurable seconds/lap) OR auto-detected from telemetry lateral G forces
- **Caution Handler**: Adjusts pit recommendations when yellow flags reduce pit-time cost
- **Interactive Tuning**: Adjust pit cost, degradation rate, target stint, and race length via UI controls

### Data Replay
- **Lap-Level Replay**: Step through or auto-replay lap timing data with real-time recommendations
- **Telemetry-Level Replay**: High-frequency sensor data replay (100+ Hz) with lap aggregation
- **Dual Mode Support**: Choose between lap times or telemetry files in UI

### Telemetry Analytics
- **Auto-Degradation Detection**: Estimates tire wear from actual lateral acceleration data
- **Real-Time Anomaly Detection**: Alerts for mechanical issues (RPM drops, brake lockups, sensor errors)
- **Performance Monitoring**: Detects significant performance drops that may indicate damage

## How It Works

The optimizer evaluates multiple candidate pit laps (e.g., lap 11, 12, 13...) and for each strategy computes:
1. Time remaining on worn tyres before pit
2. Pit time cost
3. Time on fresh tyres after pit (with degradation reset)
4. Total expected race time

It selects the pit lap that minimizes total time and reports the expected time saved vs. no-pit baseline.

## How to Run (Local)

1. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the Streamlit app:

```powershell
streamlit run app.py
```

3. Run tests:

```powershell
pip install pytest
pytest -v
```

## Usage Notes

### Lap Time Mode (Default)
- The app will find lap_time CSV files under `Datasets/` automatically
- Select a file and vehicle ID, then step through laps or run a replay
- Degradation rate is manually configured in sidebar

### Telemetry Mode (Advanced)
1. Select **"Telemetry"** in the Data Type radio button
2. Choose a telemetry CSV file (or it will auto-detect)
3. Select vehicle ID
4. **Degradation is auto-detected** from lateral G forces (early vs late laps)
5. Click **"Run Anomaly Check"** to scan for mechanical issues

### Sidebar Controls
- **Target stint**: Fallback max stint length (laps)
- **Pit time cost**: Time lost in pit (seconds)
- **Tyre degradation**: Lap time increase per lap (seconds/lap) — auto-detected in telemetry mode
- **Total race laps**: Used to compute remaining laps for optimization window

## Files

### Core Modules
- `src/data_loader.py` — Helpers to find/load lap_time CSVs
- `src/telemetry_loader.py` — **Robust telemetry data loader** with data quality handling (see [TELEMETRY_GUIDE.md](TELEMETRY_GUIDE.md))
- `src/simulator.py` — Lap-level and **telemetry-level replay engines** (SimpleSimulator, TelemetrySimulator)

### Analytics
- `src/analytics/pit_strategy.py` — **Multi-lap pit window optimizer** with telemetry-based degradation estimation
- `src/analytics/caution_handler.py` — Caution decision logic
- `src/analytics/anomaly_detection.py` — **Real-time anomaly detection** (engine, brakes, performance)

### Testing
- `tests/test_pit_strategy.py` — Unit tests for pit optimizer (4 tests)
- `tests/test_telemetry_loader.py` — Unit tests for telemetry loader (14 tests)
- `tests/test_telemetry_integration.py` — **Integration tests for telemetry features** (11 tests)

**Total: 29 tests, all passing ✓**

## Telemetry Support

The project includes comprehensive telemetry data handling with robust data quality fixes:
- **Vehicle ID parsing**: Handles `GR86-{chassis}-{car_number}` format
- **Lap #32768 detection**: Automatically detects and corrects ECU lap counter errors
- **Timestamp handling**: Distinguishes `meta_time` (reliable) from `timestamp` (ECU)
- **14 telemetry parameters**: Speed, throttle, braking, acceleration, steering, GPS, etc.
- **Data validation**: Quality reports with warnings and diagnostics

See [TELEMETRY_GUIDE.md](TELEMETRY_GUIDE.md) for detailed documentation and examples.

## Next Steps

- Integrate telemetry-based degradation (actual G-forces vs fixed rate)
- Add sector-level replay using distance-from-start telemetry
- Incorporate fuel model and compound-specific degradation curves
- Traffic and field-position modeling for undercut/overcut scenarios
- Probabilistic caution modeling (expected value with risk)
- Monte Carlo simulation for uncertainty quantification
- Richer UI with degradation charts and pit window visualization
