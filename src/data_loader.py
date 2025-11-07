import os
import glob
import pandas as pd
from typing import List

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATASETS_DIR = os.path.join(ROOT, 'Datasets')


def list_lap_time_files() -> List[str]:
    """Return absolute paths to lap_time CSV files under Datasets/ (recursively)."""
    pattern = os.path.join(DATASETS_DIR, '**', '*lap_time*.*')
    files = glob.glob(pattern, recursive=True)
    # filter by common csv extensions
    return [f for f in files if f.lower().endswith('.csv') or f.lower().endswith('.txt')]


def load_lap_time(path: str) -> pd.DataFrame:
    """Load a lap_time CSV and parse a timestamp column if present.

    Expect columns like: lap, timestamp, value, vehicle_id (based on dataset samples).
    """
    df = pd.read_csv(path, dtype=str)
    # try to coerce common column names and types
    for c in ['timestamp', 'value']:
        if c in df.columns:
            try:
                df[c] = pd.to_datetime(df[c], errors='coerce')
            except Exception:
                pass
    return df


def vehicle_ids_from_lap_time(df: pd.DataFrame) -> List[str]:
    if 'vehicle_id' in df.columns:
        return sorted(df['vehicle_id'].dropna().unique().tolist())
    return []


def filter_vehicle_laps(df: pd.DataFrame, vehicle_id: str) -> pd.DataFrame:
    if 'vehicle_id' in df.columns:
        d = df[df['vehicle_id'] == vehicle_id].copy()
    else:
        d = df.copy()
    # sort by timestamp if available
    if 'timestamp' in d.columns:
        d = d.sort_values('timestamp')
    return d.reset_index(drop=True)
