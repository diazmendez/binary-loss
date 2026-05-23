"""Spec 011: CPC18 Learning Dynamics.

Analyzes whether EV failure changes across blocks/trials, and whether
block 1 (no feedback) looks more like choices13k while blocks 2-5 reduce failure.

Critical: block and feedback are perfectly confounded (block 1 = no feedback always).
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW_CSV = ROOT / "data/raw/cpc18/all_CPC18_raw_data.csv"
CPC_COMMON = ROOT / "data/interim/cpc18_common.parquet"
CPC_FEATURES = ROOT / "data/interim/cpc18_features.parquet"

REPORT_OUT = ROOT / "outputs/reports/cpc18_learning_dynamics.md"
BLOCK_CSV = ROOT / "outputs/tables/cpc18_block_level_choice.csv"
TRIAL_CSV = ROOT / "outputs/tables/cpc18_trial_level_ev_consistency.csv"
FIG_DIR = ROOT / "outputs/figures"

C13K_FAILURE_RATE = 24.9  # from spec 006


def load_data():
    raw = pd.read_csv(RAW_CSV, usecols=["SubjID", "GameID", "Set", "Trial", "block", "B", "Feedback"])
    features = pd.read_parquet(CPC_FEATURES)
    common = pd.read_parquet(CPC_COMMON)[["game_id", "ambiguity", "reconstruction_method"]]

    # Merge features
    raw = raw.merge(features[["game_id", "ev_diff", "ev_max_conflict", "has_safe_option_A",
                              "has_safe_option_B", "n_outcomes_B"]],
                    left_on="GameID", right_on="game_id", how="left")
    raw = raw.merge(common, left_on="GameID", right_on="game_id", how="left", suffixes=("", "_dup"))
    raw.drop(columns=[c for c in raw.columns if c.endswith("_dup")], inplace=True)

    # Exclude EV ties
    n_tied = (raw["ev_diff"] == 0).sum()
    n_tied_games = raw[raw["ev_diff"] == 0]["GameID"].nunique()
    raw_notie = raw[raw["ev_diff"] != 0].copy()

    # Compute trial-level EV consistency
    raw_notie["ev_consistent"] = np.where(
        raw_notie["ev_diff"] > 0,
        (raw_notie["B"] == 0).astype(int),
        (raw_notie["B"] == 1).astype(int),
    )
    return raw_notie, n_tied_games


def block_level_table(df):
    """One row per GameID × block."""
    grouped = df.groupby(["GameID", "block"]).agg(
        mean_B=("B", "mean"),
        ev_consistency=("ev_consistent", "mean"),
        n_participants=("SubjID", "nunique"),
    ).reset_index()

    # Add features (one per GameID)
    game_info = df.drop_duplicates("GameID")[["GameID", "ev_diff", "ev_max_conflict",
                                              "ambiguity", "reconstruction_method"]]
    grouped = grouped.merge(game_info, on="GameID")
    grouped["feedback"] = (grouped["block"] > 1).astype(int)
    grouped = grouped.rename(columns={"GameID": "game_id"})
    return grouped


def trial_level_table(df):
    """One row per trial (1-25), aggregated across all GameIDs."""
    grouped = df.groupby("Trial").agg(
        mean_ev_consistency=("ev_consistent", "mean"),
        mean_B=("B", "mean"),
        n_observations=("B", "count"),
    ).reset_index().rename(columns={"Trial": "trial"})
    grouped["block"] = ((grouped["trial"] - 1) // 5) + 1
    return grouped


def overall_by_block(df):
    return df.groupby("block")["ev_consistent"].mean()


def overall_by_trial(df):
    return df.groupby("Trial")["ev_consistent"].mean()


def stratified_by_block(df, var, categories=None):
    """EV consistency by block, stratified by a variable."""
    if categories is not None:
        df = df.copy()
        df[var] = categories
    return df.groupby([var, "block"])["ev_consistent"].mean().unstack(fill_value=np.nan)


def per_game_shifts(df):
    """Compute early (block 1) vs late (block 5) shifts per GameID."""
    game_block = df.groupby(["GameID", "block"]).agg(
        mean_B=("B", "mean"),
        ev_consistency=("ev_consistent", "mean"),
    ).reset_index()

    early = game_block[game_block["block"] == 1].set_index("GameID")
    late = game_block[game_block["block"] == 5].set_index("GameID")

    shifts = pd.DataFrame({
        "early_mean_B": early["mean_B"],
        "late_mean_B": late["mean_B"],
        "early_ev_consistency": early["ev_consistency"],
        "late_ev_consistency": late["ev_consistency"],
    })
    shifts["learning_shift"] = shifts["late_ev_consistency"] - shifts["early_ev_consistency"]
    shifts["b_rate_shift"] = shifts["late_mean_B"] - shifts["early_mean_B"]
    shifts.index.name = "game_id"

    # Add features
    game_info = df.drop_duplicates("GameID")[["GameID", "ev_diff", "ev_max_conflict",
                                              "ambiguity", "reconstruction_method",
                                              "has_safe_option_A", "n_outcomes_B"]]
    game_info = game_info.set_index("GameID")
    shifts = shifts.join(game_info)
    return shifts.reset_index()


def make_figures(df, block_ev, trial_ev):
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    # Figure 1: EV failure by block
    fig, ax = plt.subplots(figsize=(6, 4))
    blocks = block_ev.index
    failure_rates = (1 - block_ev.values) * 100
    ax.plot(blocks, failure_rates, "o-", color="#4C72B0", linewidth=2, markersize=8)
    ax.axhline(C13K_FAILURE_RATE, color="gray", linestyle="--", linewidth=1, label=f"choices13k ({C13K_FAILURE_RATE}%)")
    ax.axvline(1.5, color="red", linestyle=":", alpha=0.5, label="Feedback onset")
    ax.set_xlabel("Block")
    ax.set_ylabel("EV Failure Rate (%)")
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_title("CPC18 EV Failure Rate by Block")
    ax.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "cpc18_ev_failure_by_block.png", dpi=150)
    plt.close()

    # Figure 2: EV failure by trial
    fig, ax = plt.subplots(figsize=(8, 4))
    trials = trial_ev.index
    failure_rates = (1 - trial_ev.values) * 100
    ax.plot(trials, failure_rates, "-", color="#4C72B0", linewidth=1.5)
    ax.axhline(C13K_FAILURE_RATE, color="gray", linestyle="--", linewidth=1, label=f"choices13k ({C13K_FAILURE_RATE}%)")
    for b in [5.5, 10.5, 15.5, 20.5]:
        ax.axvline(b, color="lightgray", linestyle="-", linewidth=0.8)
    ax.axvline(5.5, color="red", linestyle=":", alpha=0.7, label="Feedback onset")
    ax.set_xlabel("Trial")
    ax.set_ylabel("EV Failure Rate (%)")
    ax.set_title("CPC18 EV Failure Rate by Trial")
    ax.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "cpc18_ev_failure_by_trial.png", dpi=150)
    plt.close()

    # Figure 3: EV/max conflict by block
    fig, ax = plt.subplots(figsize=(6, 4))
    for val, label, color in [(False, "No conflict", "#4C72B0"), (True, "EV/Max conflict", "#DD8452")]:
        sub = df[df["ev_max_conflict"] == val]
        by_block = sub.groupby("block")["ev_consistent"].mean()
        ax.plot(by_block.index, (1 - by_block.values) * 100, "o-", color=color, label=label, linewidth=2)
    ax.axvline(1.5, color="red", linestyle=":", alpha=0.5, label="Feedback onset")
    ax.set_xlabel("Block")
    ax.set_ylabel("EV Failure Rate (%)")
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_title("EV Failure by Block: EV/Max Conflict")
    ax.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "cpc18_ev_max_conflict_by_block.png", dpi=150)
    plt.close()


def generate_report(df, n_tied_games, block_ev, trial_ev_table, shifts_df, block_table):
    lines = []
    lines.append("# CPC18 Learning Dynamics\n")
    lines.append(f"Generated: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M')} UTC\n")

    # Overview
    lines.append("## Overview\n")
    lines.append("Analyzes whether EV failure in CPC18 changes across blocks and trials.")
    lines.append(f"Excluded {n_tied_games} GameIDs with ev_diff=0 (EV ties).\n")
    lines.append("**Critical confound**: Block 1 is always no-feedback; blocks 2–5 always have feedback.")
    lines.append("Block and feedback effects cannot be separated.\n")

    # Overall by block
    lines.append("## Overall EV-Consistency by Block\n")
    block_failure = (1 - block_ev) * 100
    lines.append("| Block | Feedback | EV Failure Rate |")
    lines.append("|-------|----------|----------------|")
    for b in block_ev.index:
        fb = "No" if b == 1 else "Yes"
        lines.append(f"| {b} | {fb} | {block_failure[b]:.1f}% |")
    lines.append("")
    lines.append(f"Block 1 → Block 2 drop: {block_failure.iloc[0] - block_failure.iloc[1]:.1f} percentage points")
    lines.append(f"Block 2 → Block 5 change: {block_failure.iloc[1] - block_failure.iloc[4]:.1f} percentage points\n")
    lines.append("![EV Failure by Block](../figures/cpc18_ev_failure_by_block.png)\n")

    # Overall by trial
    lines.append("## Overall EV-Consistency by Trial\n")
    lines.append("![EV Failure by Trial](../figures/cpc18_ev_failure_by_trial.png)\n")
    # Within-block dynamics
    trial_data = trial_ev_table.copy()
    b1 = trial_data[trial_data["block"] == 1]["mean_ev_consistency"]
    b2_5 = trial_data[trial_data["block"] > 1]["mean_ev_consistency"]
    lines.append(f"- Block 1 (trials 1–5) range: {(1-b1.max())*100:.1f}% – {(1-b1.min())*100:.1f}%")
    lines.append(f"- Blocks 2–5 (trials 6–25) range: {(1-b2_5.max())*100:.1f}% – {(1-b2_5.min())*100:.1f}%")
    lines.append("")

    # Stratified analysis
    lines.append("## Stratified Analysis\n")

    strat_vars = [
        ("ambiguity", "Ambiguity"),
        ("ev_max_conflict", "EV/Max Conflict"),
        ("has_safe_option_A", "Safe Option A"),
        ("reconstruction_method", "Reconstruction Method"),
    ]
    for var, label in strat_vars:
        strat = stratified_by_block(df, var)
        lines.append(f"### {label}\n")
        lines.append(f"| {label} | Block 1 | Block 2 | Block 3 | Block 4 | Block 5 | Shift (B5−B1) |")
        lines.append("|---|---|---|---|---|---|---|")
        for cat in strat.index:
            vals = strat.loc[cat]
            shift = vals[5] - vals[1] if 5 in vals.index and 1 in vals.index else np.nan
            row_vals = " | ".join(f"{(1-v)*100:.1f}%" if not np.isnan(v) else "—" for v in [vals.get(b, np.nan) for b in range(1, 6)])
            shift_str = f"{-shift*100:.1f}pp" if not np.isnan(shift) else "—"
            lines.append(f"| {cat} | {row_vals} | {shift_str} |")
        lines.append("")

    # n_outcomes_B grouped
    df_copy = df.copy()
    df_copy["n_outcomes_B_group"] = pd.cut(df_copy["n_outcomes_B"], bins=[0, 2, 4, 6, 100], labels=["1-2", "3-4", "5-6", "7+"])
    strat = stratified_by_block(df_copy, "n_outcomes_B_group")
    lines.append("### N Outcomes B\n")
    lines.append("| Group | Block 1 | Block 2 | Block 3 | Block 4 | Block 5 | Shift (B5−B1) |")
    lines.append("|---|---|---|---|---|---|---|")
    for cat in strat.index:
        vals = strat.loc[cat]
        shift = vals[5] - vals[1] if 5 in vals.index and 1 in vals.index else np.nan
        row_vals = " | ".join(f"{(1-v)*100:.1f}%" if not np.isnan(v) else "—" for v in [vals.get(b, np.nan) for b in range(1, 6)])
        shift_str = f"{-shift*100:.1f}pp" if not np.isnan(shift) else "—"
        lines.append(f"| {cat} | {row_vals} | {shift_str} |")
    lines.append("")

    lines.append("![EV/Max Conflict by Block](../figures/cpc18_ev_max_conflict_by_block.png)\n")

    # Per-GameID learning shifts
    lines.append("## Per-GameID Learning Shifts\n")
    lines.append(f"- Mean learning_shift: {shifts_df['learning_shift'].mean():.4f}")
    lines.append(f"- Median learning_shift: {shifts_df['learning_shift'].median():.4f}")
    n_improved = (shifts_df["learning_shift"] > 0).sum()
    n_worsened = (shifts_df["learning_shift"] < 0).sum()
    n_unchanged = (shifts_df["learning_shift"] == 0).sum()
    lines.append(f"- Improved (shift > 0): {n_improved}")
    lines.append(f"- Worsened (shift < 0): {n_worsened}")
    lines.append(f"- Unchanged: {n_unchanged}")
    lines.append("")

    # EV/max conflict × learning
    lines.append("### EV/Max Conflict × Learning\n")
    for val, label in [(True, "Conflict"), (False, "No conflict")]:
        sub = shifts_df[shifts_df["ev_max_conflict"] == val]
        lines.append(f"- {label}: mean shift = {sub['learning_shift'].mean():.4f}, "
                     f"early failure = {(1-sub['early_ev_consistency'].mean())*100:.1f}%, "
                     f"late failure = {(1-sub['late_ev_consistency'].mean())*100:.1f}%")
    lines.append("")

    # Ambiguity × learning
    lines.append("### Ambiguity × Learning\n")
    for val, label in [(True, "Ambiguous"), (False, "Non-ambiguous")]:
        sub = shifts_df[shifts_df["ambiguity"] == val]
        lines.append(f"- {label}: mean shift = {sub['learning_shift'].mean():.4f}, "
                     f"early failure = {(1-sub['early_ev_consistency'].mean())*100:.1f}%, "
                     f"late failure = {(1-sub['late_ev_consistency'].mean())*100:.1f}%")
    lines.append("")

    # Top 20 improvers and anti-learners
    top_improve = shifts_df.nlargest(20, "learning_shift")
    top_worsen = shifts_df.nsmallest(20, "learning_shift")
    lines.append("### Top 20 Largest Positive Learning Shifts\n")
    lines.append("| game_id | early_fail | late_fail | shift | ev_max_conflict | ambiguity |")
    lines.append("|---------|-----------|----------|-------|-----------------|-----------|")
    for _, r in top_improve.iterrows():
        lines.append(f"| {int(r['game_id'])} | {(1-r['early_ev_consistency'])*100:.1f}% | {(1-r['late_ev_consistency'])*100:.1f}% | {r['learning_shift']:.3f} | {r['ev_max_conflict']} | {r['ambiguity']} |")
    lines.append("")

    lines.append("### Top 20 Largest Negative Learning Shifts (Anti-Learning)\n")
    lines.append("| game_id | early_fail | late_fail | shift | ev_max_conflict | ambiguity |")
    lines.append("|---------|-----------|----------|-------|-----------------|-----------|")
    for _, r in top_worsen.iterrows():
        lines.append(f"| {int(r['game_id'])} | {(1-r['early_ev_consistency'])*100:.1f}% | {(1-r['late_ev_consistency'])*100:.1f}% | {r['learning_shift']:.3f} | {r['ev_max_conflict']} | {r['ambiguity']} |")
    lines.append("")

    # Comparison to choices13k
    lines.append("## Comparison to choices13k\n")
    b1_failure = (1 - block_ev.iloc[0]) * 100
    b5_failure = (1 - block_ev.iloc[4]) * 100
    overall_failure = (1 - df["ev_consistent"].mean()) * 100
    lines.append(f"| Condition | EV Failure Rate |")
    lines.append(f"|-----------|----------------|")
    lines.append(f"| choices13k (all) | {C13K_FAILURE_RATE}% |")
    lines.append(f"| CPC18 block 1 (no feedback) | {b1_failure:.1f}% |")
    lines.append(f"| CPC18 blocks 2–5 (feedback) | {(1 - df[df['block']>1]['ev_consistent'].mean())*100:.1f}% |")
    lines.append(f"| CPC18 block 5 only | {b5_failure:.1f}% |")
    lines.append(f"| CPC18 overall | {overall_failure:.1f}% |")
    lines.append("")
    if b1_failure > overall_failure:
        lines.append(f"Block 1 failure ({b1_failure:.1f}%) is closer to choices13k ({C13K_FAILURE_RATE}%) than the CPC18 overall ({overall_failure:.1f}%).")
        lines.append("This suggests that feedback/experience in later blocks partially explains the lower CPC18 failure rate.")
    lines.append("")

    # Limitations
    lines.append("## Limitations\n")
    lines.append("- Feedback and block are perfectly confounded (block 1 = no feedback always).")
    lines.append("- Cannot separate experience (repeated trials) from information (feedback) effects.")
    lines.append("- CPC18 is experience-based repeated choice; choices13k may be description-based.")
    lines.append("- Empirical reconstruction for 122/270 GameIDs.")
    lines.append("- This is exploratory, not causal proof.")
    lines.append("- Individual differences are averaged out.")
    lines.append("")

    # Assumptions
    lines.append("## Assumptions\n")
    lines.append("1. EV-consistency is a meaningful measure of rational choice.")
    lines.append("2. Aggregating across participants within GameID × block is appropriate.")
    lines.append("3. The feedback × block confound is acknowledged but not resolvable.")
    lines.append("4. Trial order within a block reflects temporal sequence.")
    lines.append("")

    return "\n".join(lines)


def main():
    print("Loading data...")
    df, n_tied_games = load_data()
    print(f"  {len(df):,} trial rows (excluding {n_tied_games} tied GameIDs)")
    print(f"  {df['GameID'].nunique()} GameIDs")

    print("Computing block-level table...")
    block_table = block_level_table(df)

    print("Computing trial-level table...")
    trial_table = trial_level_table(df)

    print("Computing overall by block/trial...")
    block_ev = overall_by_block(df)
    trial_ev = overall_by_trial(df)
    print(f"  Block 1 failure: {(1-block_ev.iloc[0])*100:.1f}%")
    print(f"  Block 5 failure: {(1-block_ev.iloc[4])*100:.1f}%")

    print("Computing per-GameID shifts...")
    shifts_df = per_game_shifts(df)
    print(f"  Mean learning shift: {shifts_df['learning_shift'].mean():.4f}")

    print("Generating figures...")
    make_figures(df, block_ev, trial_ev)

    print("Saving tables...")
    BLOCK_CSV.parent.mkdir(parents=True, exist_ok=True)
    block_table.to_csv(BLOCK_CSV, index=False)
    print(f"  {BLOCK_CSV}")
    trial_table.to_csv(TRIAL_CSV, index=False)
    print(f"  {TRIAL_CSV}")

    print("Generating report...")
    report = generate_report(df, n_tied_games, block_ev, trial_table, shifts_df, block_table)
    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.write_text(report)
    print(f"  {REPORT_OUT}")

    print("Done.")


if __name__ == "__main__":
    main()
