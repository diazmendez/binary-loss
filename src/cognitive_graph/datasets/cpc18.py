"""Loader for the CPC18 dataset."""

import pandas as pd

from cognitive_graph.paths import DATA_RAW

_DIR = DATA_RAW / "cpc18"


def load() -> dict:
    """Load CPC18 raw CSV file.

    Returns dict with key 'raw' — a DataFrame.
    Note: CPC18_dictionary.pdf is not loaded programmatically.
    """
    path = _DIR / "all_CPC18_raw_data.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}")
    return {"raw": pd.read_csv(path)}
