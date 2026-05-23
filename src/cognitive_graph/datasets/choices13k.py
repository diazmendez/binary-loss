"""Loader for the choices13k dataset."""

import json

import pandas as pd

from cognitive_graph.paths import DATA_RAW

_DIR = DATA_RAW / "choices13k"


def load() -> dict:
    """Load choices13k raw files.

    Returns dict with keys:
        'problems' — list of dicts from c13k_problems.json
        'selections' — DataFrame from c13k_selections.csv
    """
    problems_path = _DIR / "c13k_problems.json"
    selections_path = _DIR / "c13k_selections.csv"

    if not problems_path.exists():
        raise FileNotFoundError(f"Missing: {problems_path}")
    if not selections_path.exists():
        raise FileNotFoundError(f"Missing: {selections_path}")

    with open(problems_path) as f:
        problems = json.load(f)

    selections = pd.read_csv(selections_path)

    return {"problems": problems, "selections": selections}
