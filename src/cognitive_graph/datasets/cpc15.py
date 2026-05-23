"""Loader for the CPC15 dataset."""

import pandas as pd

from cognitive_graph.paths import DATA_RAW

_DIR = DATA_RAW / "cpc15"

_FILES = {
    "exp1": "RawDataExperiment1sorted.csv",
    "exp2": "RawDataExperiment2sorted.csv",
    "exp3": "RawDataExperiment3.csv",
}


def load() -> dict:
    """Load CPC15 raw CSV files.

    Returns dict with keys 'exp1', 'exp2', 'exp3' — each a DataFrame.
    """
    result = {}
    for key, filename in _FILES.items():
        path = _DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing: {path}")
        result[key] = pd.read_csv(path)
    return result
