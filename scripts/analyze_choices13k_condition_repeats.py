"""Spec 008: choices13k Condition Repeats Analysis.

Analyzes the 1,562 repeated Problem IDs to understand within-problem
effects of feedback and block on choice behavior.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from itertools import combinations

ROOT = Path(__file__).resolve().parent.parent
COMMON = ROOT / "data/interim/choices13k_common.parquet"
FEATURES = ROOT / "data/interim/choices13k_features.parquet"
REPORT_OUT = ROOT / "outputs/reports/choices13k_condition_repeats.md"
ROWS_CSV = ROOT / "outputs/tables/choices13k_repeated_problem_rows.csv"
PAIRS_CSV = ROOT / "outputs/tables/choices13k_repeated_problem_pairs.csv"


def load_data():
    common = pd.read_parquet(COMMON)
    features = pd.read_parquet(FEATURES)
    df = pd.concat([common, features.drop(columns=["problem_id"])], axis=1)
    return df


def identify_repeated(df):
    """Step 1: Identify repeated problems."""
    counts = df["problem_id"].value_counts()
    repeated_ids = counts[counts > 1].index
    repeated = df[df["problem_id"].isin(repeated_ids)].copy()
    dist = counts[counts > 1].value_counts().sort_index()
    return repeated, repeated_ids, dist


def validate_structure(repeated):
    """Step 2: Validate structural identity across repeated rows."""
    struct_cols = ["options_A", "options_B", "ev_A", "ev_B", "ev_diff",
                   "max_value_A", "max_value_B", "min_value_A", "min_value_B",
                   "n_outcomes_A", "n_outcomes_B"]
    grouped = repeated.groupby("problem_id")[struct_cols]
    n_identical = 0
    n_differ = 0
    differing_ids = []
    for pid, group in grouped:
        if group.nunique().max() <= 1:
            n_identical += 1
        else:
            n_differ += 1
            differing_ids.append(pid)
    return n_identical, n_differ, differing_ids


def compare_conditions(repeated):
    """Step 3: Which condition variables differ between rows of same problem."""
    cond_vars = ["feedback", "block", "ambiguity", "corr", "n"]
    results = {}
    grouped = repeated.groupby("problem_id")[cond_vars]
    for var in cond_vars:
        results[var] = sum(1 for _, g in grouped if g[var].nunique() > 1)

    # Most common combination
    combos = []
    for _, g in grouped:
        differing = tuple(v for v in cond_vars if g[v].nunique() > 1)
        if differing:
            combos.append(differing)
    combo_counts = pd.Series(combos).value_counts()
    return results, combo_counts


def make_pairs(repeated):
    """Step 4: Create pairwise comparisons."""
    pairs = []
    feature_cols_shared = ["ev_diff", "ev_max_conflict", "n_outcomes_B"]

    for pid, group in repeated.groupby("problem_id"):
        group_sorted = group.sort_values(["block", "feedback"]).reset_index(drop=True)
        if len(group_sorted) == 2:
            row_pairs = [(0, 1)]
        else:
            row_pairs = list(combinations(range(len(group_sorted)), 2))

        for i, j in row_pairs:
            r1, r2 = group_sorted.iloc[i], group_sorted.iloc[j]
            pairs.append({
                "problem_id": pid,
                "bRate_row1": r1["bRate"], "bRate_row2": r2["bRate"],
                "bRate_diff": r2["bRate"] - r1["bRate"],
                "absolute_bRate_diff": abs(r2["bRate"] - r1["bRate"]),
                "feedback_row1": r1["feedback"], "feedback_row2": r2["feedback"],
                "block_row1": r1["block"], "block_row2": r2["block"],
                "ambiguity_row1": r1["ambiguity"], "ambiguity_row2": r2["ambiguity"],
                "corr_row1": r1["corr"], "corr_row2": r2["corr"],
                "n_row1": r1["n"], "n_row2": r2["n"],
                "ev_diff": r1["ev_diff"],
                "ev_max_conflict": r1["ev_max_conflict"],
                "n_outcomes_B": r1["n_outcomes_B"],
            })
    return pd.DataFrame(pairs)


def feedback_analysis(pairs_df):
    """Step 5: Feedback-focused analysis."""
    # Filter pairs where feedback differs
    fb_pairs = pairs_df[pairs_df["feedback_row1"] != pairs_df["feedback_row2"]].copy()
    # Reorient: compute feedback_bRate - no_feedback_bRate
    fb_pairs["bRate_feedback"] = np.where(fb_pairs["feedback_row2"], fb_pairs["bRate_row2"], fb_pairs["bRate_row1"])
    fb_pairs["bRate_no_feedback"] = np.where(fb_pairs["feedback_row1"] == False, fb_pairs["bRate_row1"], fb_pairs["bRate_row2"])  # noqa: E712
    fb_pairs["fb_effect"] = fb_pairs["bRate_feedback"] - fb_pairs["bRate_no_feedback"]

    stats = {
        "n_pairs": len(fb_pairs),
        "mean_diff": fb_pairs["fb_effect"].mean(),
        "median_diff": fb_pairs["fb_effect"].median(),
        "n_increases": (fb_pairs["fb_effect"] > 0).sum(),
        "n_decreases": (fb_pairs["fb_effect"] < 0).sum(),
        "n_unchanged": (fb_pairs["fb_effect"] == 0).sum(),
    }

    # Stratifications
    # By ambiguity (use row1 since structure is same)
    fb_pairs["ambiguity"] = fb_pairs["ambiguity_row1"]
    strat_ambiguity = fb_pairs.groupby("ambiguity")["fb_effect"].agg(["mean", "median", "count"])

    # By ev_max_conflict
    strat_conflict = fb_pairs.groupby("ev_max_conflict")["fb_effect"].agg(["mean", "median", "count"])

    # By EV-predicted option
    fb_pairs["ev_predicted"] = np.select(
        [fb_pairs["ev_diff"] > 0, fb_pairs["ev_diff"] < 0],
        ["A", "B"], default="tie"
    )
    strat_ev = fb_pairs.groupby("ev_predicted")["fb_effect"].agg(["mean", "median", "count"])

    # By n_outcomes_B grouped
    fb_pairs["n_outcomes_B_group"] = pd.cut(fb_pairs["n_outcomes_B"], bins=[0, 2, 4, 6, 9], labels=["1-2", "3-4", "5-6", "7-9"])
    strat_nout = fb_pairs.groupby("n_outcomes_B_group", observed=True)["fb_effect"].agg(["mean", "median", "count"])

    return stats, strat_ambiguity, strat_conflict, strat_ev, strat_nout


def block_analysis(pairs_df):
    """Step 6: Block-focused analysis."""
    block_pairs = pairs_df[pairs_df["block_row1"] != pairs_df["block_row2"]].copy()
    block_pairs["block_diff_bRate"] = block_pairs["bRate_row2"] - block_pairs["bRate_row1"]  # later - earlier

    stats = {
        "n_pairs": len(block_pairs),
        "mean_diff": block_pairs["block_diff_bRate"].mean(),
        "median_diff": block_pairs["block_diff_bRate"].median(),
        "n_increases": (block_pairs["block_diff_bRate"] > 0).sum(),
        "n_decreases": (block_pairs["block_diff_bRate"] < 0).sum(),
        "n_unchanged": (block_pairs["block_diff_bRate"] == 0).sum(),
    }
    return stats, block_pairs


def generate_report(df, repeated, repeated_ids, dist, n_identical, n_differ,
                    cond_results, combo_counts, pairs_df,
                    fb_stats, strat_ambiguity, strat_conflict, strat_ev, strat_nout,
                    block_stats, block_pairs):
    lines = []
    lines.append("# choices13k: Condition Repeats Analysis\n")
    lines.append(f"Generated: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M')} UTC\n")

    # Summary counts
    lines.append("## Summary Counts\n")
    lines.append(f"- Total rows: {len(df):,}")
    lines.append(f"- Unique problem_id values: {df['problem_id'].nunique():,}")
    lines.append(f"- Repeated problem_id values: {len(repeated_ids):,}")
    lines.append(f"- Total rows for repeated problems: {len(repeated):,}")
    lines.append("")
    lines.append("Rows per repeated problem:\n")
    lines.append("| Rows | Count |")
    lines.append("|------|-------|")
    for n_rows, count in dist.items():
        lines.append(f"| {n_rows} | {count} |")
    lines.append("")

    # Structural identity
    lines.append("## Structural Identity Validation\n")
    lines.append(f"- Structurally identical across rows: **{n_identical}** / {len(repeated_ids)}")
    lines.append(f"- Structure differs: **{n_differ}**")
    if n_differ > 0:
        lines.append(f"- ⚠️ Differing problem_ids: {n_differ} (possible data issue)")
    else:
        lines.append("- ✓ All repeated problems have identical gamble structure across conditions.")
    lines.append("")

    # Condition variable differences
    lines.append("## Condition Variable Differences\n")
    lines.append("| Variable | N problems where it differs |")
    lines.append("|----------|---------------------------|")
    for var, count in cond_results.items():
        lines.append(f"| {var} | {count} |")
    lines.append("")
    lines.append("Most common combinations of differing variables:\n")
    lines.append("| Combination | Count |")
    lines.append("|-------------|-------|")
    for combo, count in combo_counts.head(10).items():
        lines.append(f"| {', '.join(combo)} | {count} |")
    lines.append("")

    # Feedback effect
    lines.append("## Feedback Effect (Within-Problem)\n")
    lines.append(f"Pairs where feedback differs: **{fb_stats['n_pairs']}**\n")
    lines.append(f"- Mean bRate difference (feedback − no feedback): **{fb_stats['mean_diff']:.4f}**")
    lines.append(f"- Median bRate difference: **{fb_stats['median_diff']:.4f}**")
    lines.append(f"- Feedback increases bRate (more B): {fb_stats['n_increases']}")
    lines.append(f"- Feedback decreases bRate (less B): {fb_stats['n_decreases']}")
    lines.append(f"- Unchanged: {fb_stats['n_unchanged']}")
    lines.append("")

    lines.append("### Stratified by Ambiguity\n")
    lines.append("| Ambiguity | Mean Δ | Median Δ | N |")
    lines.append("|-----------|--------|----------|---|")
    for idx, row in strat_ambiguity.iterrows():
        lines.append(f"| {idx} | {row['mean']:.4f} | {row['median']:.4f} | {int(row['count'])} |")
    lines.append("")

    lines.append("### Stratified by EV/Max Conflict\n")
    lines.append("| EV/Max Conflict | Mean Δ | Median Δ | N |")
    lines.append("|-----------------|--------|----------|---|")
    for idx, row in strat_conflict.iterrows():
        lines.append(f"| {idx} | {row['mean']:.4f} | {row['median']:.4f} | {int(row['count'])} |")
    lines.append("")

    lines.append("### Stratified by EV-Predicted Option\n")
    lines.append("| EV Predicts | Mean Δ | Median Δ | N |")
    lines.append("|-------------|--------|----------|---|")
    for idx, row in strat_ev.iterrows():
        lines.append(f"| {idx} | {row['mean']:.4f} | {row['median']:.4f} | {int(row['count'])} |")
    lines.append("")

    lines.append("### Stratified by N Outcomes B\n")
    lines.append("| Group | Mean Δ | Median Δ | N |")
    lines.append("|-------|--------|----------|---|")
    for idx, row in strat_nout.iterrows():
        lines.append(f"| {idx} | {row['mean']:.4f} | {row['median']:.4f} | {int(row['count'])} |")
    lines.append("")

    # Block effect
    lines.append("## Block Effect (Within-Problem)\n")
    lines.append(f"Pairs where block differs: **{block_stats['n_pairs']}**\n")
    lines.append(f"- Mean bRate difference (later block − earlier block): **{block_stats['mean_diff']:.4f}**")
    lines.append(f"- Median bRate difference: **{block_stats['median_diff']:.4f}**")
    lines.append(f"- bRate increases with block: {block_stats['n_increases']}")
    lines.append(f"- bRate decreases with block: {block_stats['n_decreases']}")
    lines.append(f"- Unchanged: {block_stats['n_unchanged']}")
    lines.append("")

    # Top 30 largest changes
    lines.append("## Top 30 Largest Within-Problem bRate Changes\n")
    top30 = pairs_df.nlargest(30, "absolute_bRate_diff")
    lines.append("| # | problem_id | bRate_row1 | bRate_row2 | abs_diff | feedback_r1 | feedback_r2 | block_r1 | block_r2 |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for i, (_, row) in enumerate(top30.iterrows(), 1):
        lines.append(f"| {i} | {int(row['problem_id'])} | {row['bRate_row1']:.3f} | {row['bRate_row2']:.3f} | {row['absolute_bRate_diff']:.3f} | {row['feedback_row1']} | {row['feedback_row2']} | {int(row['block_row1'])} | {int(row['block_row2'])} |")
    lines.append("")

    # Interpretation notes
    lines.append("## Interpretation Notes\n")
    lines.append("- Within-problem comparisons control for gamble structure, isolating condition effects.")
    lines.append("- Feedback effect direction indicates whether outcome information shifts choices toward or away from B.")
    lines.append("- Block effects should NOT be interpreted as learning without confirming temporal ordering within participants.")
    lines.append("")

    # Limitations
    lines.append("## Limitations\n")
    lines.append("- Block interpretation uncertainty: it is unclear whether block represents temporal ordering within the same participant group.")
    lines.append("- Small n per problem (15–33 participants per row).")
    lines.append("- Aggregate bRate may mask individual-level heterogeneity.")
    lines.append("- No correction for multiple comparisons in stratified analyses.")
    lines.append("")

    # Next steps
    lines.append("## Next Steps\n")
    lines.append("- Investigate whether feedback effect interacts with EV failure (do failures become consistent with feedback?).")
    lines.append("- Consider mixed-effects models if individual-level data becomes available.")
    lines.append("- Use condition repeats as validation for graph-based representations (same node, different edge weights by condition).")
    lines.append("")

    return "\n".join(lines)


def main():
    print("Loading data...")
    df = load_data()
    print(f"  Loaded {len(df)} rows")

    print("Step 1: Identifying repeated problems...")
    repeated, repeated_ids, dist = identify_repeated(df)
    print(f"  Repeated problem_ids: {len(repeated_ids)}")
    print(f"  Total rows for repeated: {len(repeated)}")

    print("Step 2: Validating structural identity...")
    n_identical, n_differ, _ = validate_structure(repeated)
    print(f"  Identical: {n_identical}, Differ: {n_differ}")

    print("Step 3: Comparing condition variables...")
    cond_results, combo_counts = compare_conditions(repeated)
    for var, count in cond_results.items():
        print(f"  {var} differs: {count}")

    print("Step 4: Creating pairwise comparisons...")
    pairs_df = make_pairs(repeated)
    print(f"  Pairs created: {len(pairs_df)}")

    print("Step 5: Feedback analysis...")
    fb_stats, strat_ambiguity, strat_conflict, strat_ev, strat_nout = feedback_analysis(pairs_df)
    print(f"  Feedback pairs: {fb_stats['n_pairs']}")
    print(f"  Mean feedback effect: {fb_stats['mean_diff']:.4f}")

    print("Step 6: Block analysis...")
    block_stats, block_pairs = block_analysis(pairs_df)
    print(f"  Block pairs: {block_stats['n_pairs']}")
    print(f"  Mean block effect: {block_stats['mean_diff']:.4f}")

    print("Step 7: Saving output tables...")
    ROWS_CSV.parent.mkdir(parents=True, exist_ok=True)
    row_cols = ["problem_id", "feedback", "block", "ambiguity", "corr", "n",
                "bRate", "bRate_std", "ev_A", "ev_B", "ev_diff", "n_outcomes_B", "ev_max_conflict"]
    repeated[row_cols].to_csv(ROWS_CSV, index=False)
    print(f"  Saved: {ROWS_CSV} ({len(repeated)} rows)")

    pairs_df.to_csv(PAIRS_CSV, index=False)
    print(f"  Saved: {PAIRS_CSV} ({len(pairs_df)} rows)")

    print("Step 8: Generating report...")
    report = generate_report(df, repeated, repeated_ids, dist, n_identical, n_differ,
                             cond_results, combo_counts, pairs_df,
                             fb_stats, strat_ambiguity, strat_conflict, strat_ev, strat_nout,
                             block_stats, block_pairs)
    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.write_text(report)
    print(f"  Saved: {REPORT_OUT}")

    print("Done.")


if __name__ == "__main__":
    main()
