"""Spec 009: CPC18 Normalization.

Normalizes CPC18 into common representation at the GameID level.
- Stage 1: Exact reconstruction for simple problems (LotNum=1, LotShape='-').
- Stage 2: Empirical reconstruction for complex problems via Apay/Bpay marginals.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from cognitive_graph.common.features import compute_features

RAW_CSV = ROOT / "data/raw/cpc18/all_CPC18_raw_data.csv"
COMMON_OUT = ROOT / "data/interim/cpc18_common.parquet"
FEATURES_OUT = ROOT / "data/interim/cpc18_features.parquet"
REPORT_OUT = ROOT / "outputs/reports/cpc18_normalization_summary.md"
QUALITY_CSV = ROOT / "outputs/tables/cpc18_reconstruction_quality.csv"


def load_raw():
    return pd.read_csv(RAW_CSV)


def get_game_meta(raw):
    """Extract one row per GameID with parametric info."""
    cols = ["GameID", "Ha", "pHa", "La", "LotShapeA", "LotNumA",
            "Hb", "pHb", "Lb", "LotShapeB", "LotNumB", "Amb", "Corr", "Set"]
    return raw[cols].drop_duplicates("GameID").sort_values("GameID").reset_index(drop=True)


def is_simple(row):
    return (row["LotNumA"] == 1 and row["LotShapeA"] == "-" and
            row["LotNumB"] == 1 and row["LotShapeB"] == "-")


def reconstruct_exact(row):
    """Exact reconstruction for simple games."""
    pHa, Ha, La = row["pHa"], row["Ha"], row["La"]
    pHb, Hb, Lb = row["pHb"], row["Hb"], row["Lb"]

    if pHa == 1.0:
        options_a = [[1.0, float(Ha)]]
    elif pHa == 0.0:
        options_a = [[1.0, float(La)]]
    else:
        options_a = [[pHa, float(Ha)], [round(1 - pHa, 10), float(La)]]

    if pHb == 1.0:
        options_b = [[1.0, float(Hb)]]
    elif pHb == 0.0:
        options_b = [[1.0, float(Lb)]]
    else:
        options_b = [[pHb, float(Hb)], [round(1 - pHb, 10), float(Lb)]]

    return options_a, options_b


def reconstruct_empirical(game_id, raw_game):
    """Empirical reconstruction from Apay/Bpay marginal distributions."""
    def marginal(values):
        counts = values.value_counts()
        total = counts.sum()
        probs = (counts / total).sort_index()
        # Normalize to exactly 1.0
        probs = probs / probs.sum()
        return [[round(float(p), 10), float(v)] for v, p in probs.items()]

    options_a = marginal(raw_game["Apay"])
    options_b = marginal(raw_game["Bpay"])
    return options_a, options_b


def build_common(raw, meta):
    """Build problem-level common representation."""
    rows = []
    raw_grouped = raw.groupby("GameID")

    for _, gm in meta.iterrows():
        gid = gm["GameID"]
        game_raw = raw_grouped.get_group(gid)
        simple = is_simple(gm)

        if simple:
            options_a, options_b = reconstruct_exact(gm)
            method = "exact"
            notes = ""
        else:
            options_a, options_b = reconstruct_empirical(gid, game_raw)
            method = "empirical"
            notes = "Marginal distribution from Apay/Bpay across all trials for this GameID"

        rows.append({
            "dataset": "cpc18",
            "game_id": int(gid),
            "set": int(gm["Set"]),
            "ambiguity": bool(gm["Amb"]),
            "corr": int(gm["Corr"]),
            "options_A": json.dumps(options_a),
            "options_B": json.dumps(options_b),
            "reconstruction_method": method,
            "reconstruction_notes": notes,
            "n_participants": int(game_raw["SubjID"].nunique()),
            "n_trials_per_participant": 25,
            "n_total_rows": len(game_raw),
            "mean_choice_B": float(game_raw["B"].mean()),
            "feedback_available": bool(game_raw["Feedback"].any()),
        })

    return pd.DataFrame(rows)


def build_features(common_df):
    """Compute features for each problem."""
    feat_rows = []
    for _, row in common_df.iterrows():
        feats = compute_features({"options_A": row["options_A"], "options_B": row["options_B"]})
        feats["game_id"] = row["game_id"]
        feat_rows.append(feats)
    return pd.DataFrame(feat_rows)


def build_quality_table(common_df, meta):
    """Compare empirical EVs against parametric EVs."""
    rows = []
    for _, row in common_df.iterrows():
        gid = row["game_id"]
        gm = meta[meta["GameID"] == gid].iloc[0]
        options_a = json.loads(row["options_A"])
        options_b = json.loads(row["options_B"])

        emp_ev_a = sum(p * v for p, v in options_a)
        emp_ev_b = sum(p * v for p, v in options_b)
        par_ev_a = gm["pHa"] * gm["Ha"] + (1 - gm["pHa"]) * gm["La"]
        par_ev_b = gm["pHb"] * gm["Hb"] + (1 - gm["pHb"]) * gm["Lb"]

        rows.append({
            "game_id": gid,
            "set": int(gm["Set"]),
            "reconstruction_method": row["reconstruction_method"],
            "lotnum_a": int(gm["LotNumA"]),
            "lotnum_b": int(gm["LotNumB"]),
            "n_unique_apay": len(options_a),
            "n_unique_bpay": len(options_b),
            "parametric_ev_a": round(par_ev_a, 6),
            "empirical_ev_a": round(emp_ev_a, 6),
            "ev_error_a": round(abs(emp_ev_a - par_ev_a), 6),
            "parametric_ev_b": round(par_ev_b, 6),
            "empirical_ev_b": round(emp_ev_b, 6),
            "ev_error_b": round(abs(emp_ev_b - par_ev_b), 6),
            "n_draws": row["n_total_rows"],
        })
    return pd.DataFrame(rows)


def validate(common_df, raw):
    """Run validation checks."""
    issues = []
    # choice_B binary
    non_binary = raw[~raw["B"].isin([0, 1])]
    if len(non_binary) > 0:
        issues.append(f"Non-binary B values: {len(non_binary)} rows")

    # Probability sums
    prob_issues_a = 0
    prob_issues_b = 0
    for _, row in common_df.iterrows():
        opts_a = json.loads(row["options_A"])
        opts_b = json.loads(row["options_B"])
        sum_a = sum(p for p, _ in opts_a)
        sum_b = sum(p for p, _ in opts_b)
        if abs(sum_a - 1.0) > 1e-4:
            prob_issues_a += 1
        if abs(sum_b - 1.0) > 1e-4:
            prob_issues_b += 1

    return {
        "choice_b_binary": len(non_binary) == 0,
        "prob_issues_a": prob_issues_a,
        "prob_issues_b": prob_issues_b,
        "issues": issues,
    }


def generate_report(raw, common_df, features_df, quality_df, validation):
    lines = []
    lines.append("# CPC18 Normalization Summary\n")
    lines.append(f"Generated: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M')} UTC\n")

    # Overview
    lines.append("## Overview\n")
    lines.append(f"- Total raw rows: {len(raw):,}")
    lines.append(f"- Unique GameIDs normalized: {common_df['game_id'].nunique()}")
    lines.append(f"- Unique participants: {raw['SubjID'].nunique()}")
    n_exact = (common_df["reconstruction_method"] == "exact").sum()
    n_empirical = (common_df["reconstruction_method"] == "empirical").sum()
    lines.append(f"- Exact reconstruction: {n_exact} GameIDs")
    lines.append(f"- Empirical reconstruction: {n_empirical} GameIDs")
    lines.append("")

    # Stage 1
    lines.append("## Stage 1: Exact Normalization\n")
    exact_q = quality_df[quality_df["reconstruction_method"] == "exact"]
    exact_rows = raw[raw["GameID"].isin(common_df[common_df["reconstruction_method"] == "exact"]["game_id"])]
    lines.append(f"- GameIDs: {n_exact}")
    lines.append(f"- Raw rows covered: {len(exact_rows):,}")
    lines.append(f"- Max EV error A: {exact_q['ev_error_a'].max():.6f}")
    lines.append(f"- Max EV error B: {exact_q['ev_error_b'].max():.6f}")
    lines.append("")

    # Stage 2
    lines.append("## Stage 2: Empirical Normalization\n")
    lines.append("*Reconstructed outcome distributions represent the experienced marginal distribution")
    lines.append("of Apay/Bpay, not necessarily the generative parametric lottery decomposition.*\n")
    emp_q = quality_df[quality_df["reconstruction_method"] == "empirical"]
    emp_rows = raw[raw["GameID"].isin(common_df[common_df["reconstruction_method"] == "empirical"]["game_id"])]
    lines.append(f"- GameIDs: {n_empirical}")
    lines.append(f"- Raw rows covered: {len(emp_rows):,}")
    lines.append(f"- Mean EV error A: {emp_q['ev_error_a'].mean():.4f}")
    lines.append(f"- Mean EV error B: {emp_q['ev_error_b'].mean():.4f}")
    lines.append(f"- Max EV error A: {emp_q['ev_error_a'].max():.4f}")
    lines.append(f"- Max EV error B: {emp_q['ev_error_b'].max():.4f}")
    lines.append("")

    # Feature summary
    lines.append("## Feature Summary\n")
    num_cols = ["n_outcomes_A", "n_outcomes_B", "ev_A", "ev_B", "ev_diff",
                "max_value_A", "max_value_B", "max_value_diff", "min_value_A", "min_value_B"]
    lines.append("| Feature | Mean | Std | Min | Max |")
    lines.append("|---------|------|-----|-----|-----|")
    for col in num_cols:
        s = features_df[col]
        lines.append(f"| {col} | {s.mean():.3f} | {s.std():.3f} | {s.min():.3f} | {s.max():.3f} |")
    lines.append("")

    cat_cols = ["has_safe_option_A", "has_safe_option_B", "ev_max_conflict",
                "higher_ev_option", "higher_max_option"]
    for col in cat_cols:
        lines.append(f"- **{col}**: {features_df[col].value_counts().to_dict()}")
    lines.append("")

    # Set distribution
    lines.append("## Set Distribution\n")
    set_stats = raw.groupby("Set").agg(
        rows=("GameID", "count"),
        participants=("SubjID", "nunique"),
        games=("GameID", "nunique"),
    ).reset_index()
    lines.append("| Set | Rows | Participants | Games |")
    lines.append("|-----|------|--------------|-------|")
    for _, r in set_stats.iterrows():
        lines.append(f"| {int(r['Set'])} | {int(r['rows']):,} | {int(r['participants'])} | {int(r['games'])} |")
    lines.append("")

    # Missing RT
    lines.append("## Missing RT\n")
    rt_stats = raw.groupby("Set").agg(
        total=("RT", "size"), missing=("RT", lambda x: x.isna().sum())
    ).reset_index()
    rt_stats["pct_missing"] = (rt_stats["missing"] / rt_stats["total"] * 100).round(1)
    lines.append("| Set | Total | Missing RT | % Missing |")
    lines.append("|-----|-------|-----------|-----------|")
    for _, r in rt_stats.iterrows():
        lines.append(f"| {int(r['Set'])} | {int(r['total']):,} | {int(r['missing']):,} | {r['pct_missing']}% |")
    lines.append("")

    # Validation
    lines.append("## Validation Results\n")
    lines.append(f"- choice_B binary (all 0/1): {'✓' if validation['choice_b_binary'] else '✗'}")
    lines.append(f"- Probability sum issues (A): {validation['prob_issues_a']}")
    lines.append(f"- Probability sum issues (B): {validation['prob_issues_b']}")
    lines.append("")

    # Assumptions
    lines.append("## Assumptions\n")
    lines.append("1. Apay/Bpay represent realized payoffs from the full option (including La/lottery split).")
    lines.append("2. Empirical marginals approximate the true outcome distribution with ~2500+ draws per GameID.")
    lines.append("3. For simple games, the parametric formula exactly describes the outcome distribution.")
    lines.append("4. pHa/pHb in the CSV are already 0–1 probabilities (not percentages).")
    lines.append("5. CPC18 Sets 1–5 subsume CPC15; CPC15 is not normalized separately.")
    lines.append("")

    # Open questions
    lines.append("## Open Questions\n")
    lines.append("1. Whether RT is available for Sets 8–9 (appears to be available based on data).")
    lines.append("2. Whether empirical distributions for correlated games (Corr≠0) properly reflect the marginal.")
    lines.append("3. Whether the 25-trial structure is consistent across all participants and games.")
    lines.append("")

    return "\n".join(lines)


def main():
    print("Loading raw CPC18 data...")
    raw = load_raw()
    print(f"  {len(raw):,} rows, {raw['SubjID'].nunique()} participants, {raw['GameID'].nunique()} GameIDs")

    meta = get_game_meta(raw)

    print("Building common representation...")
    common_df = build_common(raw, meta)
    n_exact = (common_df["reconstruction_method"] == "exact").sum()
    n_emp = (common_df["reconstruction_method"] == "empirical").sum()
    print(f"  Exact: {n_exact}, Empirical: {n_emp}")

    print("Computing features...")
    features_df = build_features(common_df)

    print("Building reconstruction quality table...")
    quality_df = build_quality_table(common_df, meta)
    emp_q = quality_df[quality_df["reconstruction_method"] == "empirical"]
    print(f"  Empirical mean EV error: A={emp_q['ev_error_a'].mean():.4f}, B={emp_q['ev_error_b'].mean():.4f}")

    print("Validating...")
    validation = validate(common_df, raw)
    print(f"  Binary check: {'OK' if validation['choice_b_binary'] else 'FAIL'}")
    print(f"  Prob sum issues: A={validation['prob_issues_a']}, B={validation['prob_issues_b']}")

    print("Saving outputs...")
    COMMON_OUT.parent.mkdir(parents=True, exist_ok=True)
    common_df.to_parquet(COMMON_OUT, index=False)
    print(f"  {COMMON_OUT}")

    features_df.to_parquet(FEATURES_OUT, index=False)
    print(f"  {FEATURES_OUT}")

    QUALITY_CSV.parent.mkdir(parents=True, exist_ok=True)
    quality_df.to_csv(QUALITY_CSV, index=False)
    print(f"  {QUALITY_CSV}")

    print("Generating report...")
    report = generate_report(raw, common_df, features_df, quality_df, validation)
    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.write_text(report)
    print(f"  {REPORT_OUT}")

    print("Done.")


if __name__ == "__main__":
    main()
