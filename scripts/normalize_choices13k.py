"""Normalize choices13k into common representation and compute features.

Produces:
  data/interim/choices13k_common.parquet
  data/interim/choices13k_features.parquet
  outputs/reports/choices13k_feature_summary.md
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pandas as pd

from cognitive_graph.common.features import compute_features
from cognitive_graph.datasets import choices13k
from cognitive_graph.paths import DATA_INTERIM, OUTPUTS

PROB_TOL = 1e-6  # tolerance for probability sum validation


def validate_and_normalize():
    data = choices13k.load()
    problems = data["problems"]  # dict keyed by string index
    selections = data["selections"]  # DataFrame

    # --- Validation 1: JSON keys are row indices of the CSV ---
    # JSON has 14568 keys ("0".."14567"), one per CSV row.
    # CSV Problem column is the problem ID (1..13006), with some problems
    # appearing in multiple rows (different block/feedback conditions).
    n_json = len(problems)
    n_csv = len(selections)
    if n_json == n_csv:
        id_alignment = (
            f"JSON keys are row indices (0..{n_json-1}), matching {n_csv} CSV rows. "
            f"CSV has {selections['Problem'].nunique()} unique Problem IDs "
            f"(some problems appear in multiple block/feedback conditions)."
        )
    else:
        id_alignment = (
            f"SIZE MISMATCH: JSON has {n_json} entries, CSV has {n_csv} rows."
        )

    # --- Build common representation ---
    rows = []
    validation_issues = {"prob_sum_A": 0, "prob_sum_B": 0, "missing_bRate": 0}

    for row_idx, sel_row in selections.iterrows():
        json_key = str(row_idx)

        if json_key not in problems:
            continue

        prob = problems[json_key]
        options_a = prob["A"]  # [[prob, value], ...]
        options_b = prob["B"]

        # Validate probability sums
        sum_a = sum(o[0] for o in options_a)
        sum_b = sum(o[0] for o in options_b)
        if abs(sum_a - 1.0) > PROB_TOL:
            validation_issues["prob_sum_A"] += 1
        if abs(sum_b - 1.0) > PROB_TOL:
            validation_issues["prob_sum_B"] += 1

        brate = sel_row["bRate"]
        if pd.isna(brate) or not (0.0 <= brate <= 1.0):
            validation_issues["missing_bRate"] += 1

        rows.append({
            "dataset": "choices13k",
            "problem_id": int(sel_row["Problem"]),
            "feedback": bool(sel_row["Feedback"]),
            "block": int(sel_row["Block"]),
            "ambiguity": bool(sel_row["Amb"]),
            "corr": int(sel_row["Corr"]),
            "n": int(sel_row["n"]),
            "options_A": json.dumps(options_a),
            "options_B": json.dumps(options_b),
            "bRate": float(brate) if not pd.isna(brate) else None,
            "bRate_std": float(sel_row["bRate_std"]) if not pd.isna(sel_row["bRate_std"]) else None,
        })

    common_df = pd.DataFrame(rows)

    # --- Compute features ---
    feature_rows = []
    feature_errors = 0
    for _, row in common_df.iterrows():
        try:
            feats = compute_features(row.to_dict())
            feats["problem_id"] = row["problem_id"]
            feature_rows.append(feats)
        except Exception:
            feature_errors += 1

    features_df = pd.DataFrame(feature_rows)

    # --- Save parquet files ---
    DATA_INTERIM.mkdir(parents=True, exist_ok=True)
    common_path = DATA_INTERIM / "choices13k_common.parquet"
    features_path = DATA_INTERIM / "choices13k_features.parquet"
    common_df.to_parquet(common_path, index=False)
    features_df.to_parquet(features_path, index=False)

    print(f"Common representation: {len(common_df)} rows → {common_path}")
    print(f"Features: {len(features_df)} rows → {features_path}")

    # --- Generate summary report ---
    report_lines = generate_report(common_df, features_df, validation_issues,
                                   id_alignment, feature_errors)
    report_dir = OUTPUTS / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "choices13k_feature_summary.md"
    report_path.write_text("\n".join(report_lines))
    print(f"Report: {report_path}")


def generate_report(common_df, features_df, validation_issues, id_alignment, feature_errors):
    lines = [
        "# choices13k: Common Representation & Feature Summary",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Validation Results",
        "",
        f"- **ID alignment**: {id_alignment}",
        f"- **Problems normalized**: {len(common_df)}",
        f"- **Probability sum issues (Option A)**: {validation_issues['prob_sum_A']}",
        f"- **Probability sum issues (Option B)**: {validation_issues['prob_sum_B']}",
        f"- **Missing/invalid bRate**: {validation_issues['missing_bRate']}",
        f"- **Feature computation errors**: {feature_errors}",
        "",
        "## Common Representation",
        "",
        "| Field | Description |",
        "|-------|-------------|",
        "| dataset | Always 'choices13k' |",
        "| problem_id | 1-indexed problem identifier |",
        "| feedback | Whether feedback was provided |",
        "| block | Block number (1–5) |",
        "| ambiguity | Whether Option B is ambiguous |",
        "| corr | Correlation between options (-1/0/1) |",
        "| n | Number of participants |",
        "| options_A | JSON: [[prob, value], ...] from c13k_problems.json |",
        "| options_B | JSON: [[prob, value], ...] from c13k_problems.json |",
        "| bRate | Aggregate B-choice rate |",
        "| bRate_std | Std dev of B-choice rate |",
        "",
        "## Feature Distributions",
        "",
    ]

    # Numeric feature stats
    numeric_cols = [
        "n_outcomes_A", "n_outcomes_B", "ev_A", "ev_B", "ev_diff",
        "max_value_A", "max_value_B", "max_value_diff",
        "min_value_A", "min_value_B",
    ]
    lines.append("### Numeric Features")
    lines.append("")
    lines.append("| Feature | Mean | Std | Min | Median | Max |")
    lines.append("|---------|------|-----|-----|--------|-----|")
    for col in numeric_cols:
        if col in features_df.columns:
            s = features_df[col]
            lines.append(
                f"| {col} | {s.mean():.3f} | {s.std():.3f} | {s.min():.3f} | {s.median():.3f} | {s.max():.3f} |"
            )
    lines.append("")

    # Boolean/categorical features
    lines.append("### Categorical Features")
    lines.append("")

    for col in ["has_safe_option_A", "has_safe_option_B", "ev_max_conflict"]:
        if col in features_df.columns:
            counts = features_df[col].value_counts()
            lines.append(f"- **{col}**: True={counts.get(True, 0)}, False={counts.get(False, 0)}")

    for col in ["higher_ev_option", "higher_max_option"]:
        if col in features_df.columns:
            counts = features_df[col].value_counts()
            parts = ", ".join(f"{k}={v}" for k, v in counts.items())
            lines.append(f"- **{col}**: {parts}")

    lines.append("")

    # bRate vs EV analysis
    lines.append("### bRate vs Expected Value")
    lines.append("")
    merged = features_df.merge(common_df[["problem_id", "bRate"]], on="problem_id")
    valid = merged.dropna(subset=["bRate"])
    if len(valid) > 0:
        # When EV_A > EV_B, do people choose A (low bRate)?
        ev_a_higher = valid[valid["ev_diff"] > 0]
        ev_b_higher = valid[valid["ev_diff"] < 0]
        ev_equal = valid[valid["ev_diff"] == 0]
        lines.append(f"- Problems where EV(A) > EV(B): {len(ev_a_higher)}, mean bRate = {ev_a_higher['bRate'].mean():.3f}")
        lines.append(f"- Problems where EV(B) > EV(A): {len(ev_b_higher)}, mean bRate = {ev_b_higher['bRate'].mean():.3f}")
        lines.append(f"- Problems where EV(A) = EV(B): {len(ev_equal)}, mean bRate = {ev_equal['bRate'].mean():.3f}")
        corr = valid["ev_diff"].corr(valid["bRate"])
        lines.append(f"- Correlation(ev_diff, bRate): {corr:.4f}")
    lines.append("")

    # Assumptions
    lines.append("## Assumptions")
    lines.append("")
    lines.append("1. JSON keys are CSV row indices (0-based). Each JSON entry corresponds to one CSV row.")
    lines.append("2. CSV Problem column is the problem ID; some problems appear in multiple rows (different block/feedback).")
    lines.append("3. c13k_problems.json is authoritative for option/outcome/probability structure.")
    lines.append("4. Each [prob, value] pair in JSON represents an explicit outcome.")
    lines.append("5. A 'safe' option is one with a single outcome or any outcome with probability 1.0.")
    lines.append("6. bRate aggregates across all participants for that problem-condition row.")
    lines.append("")

    return lines


if __name__ == "__main__":
    validate_and_normalize()
