"""
Spec 026: CPC18 Clustered Trial-Level Robustness Check
Tests whether the block-related decline in EV failure survives clustering by participant.
"""

import numpy as np
import pandas as pd
from pathlib import Path

OUT_TABLES = Path("outputs/tables")
OUT_REPORTS = Path("outputs/reports")
OUT_TABLES.mkdir(parents=True, exist_ok=True)
OUT_REPORTS.mkdir(parents=True, exist_ok=True)


def load_trial_data():
    """Load raw CPC18 trials, merge ev_diff, compute ev_failure."""
    raw = pd.read_csv("data/raw/cpc18/all_CPC18_raw_data.csv",
                      usecols=["SubjID", "GameID", "Trial", "B", "block"])
    feat = pd.read_parquet("data/interim/cpc18_features.parquet")[["game_id", "ev_diff"]]
    feat = feat.rename(columns={"game_id": "GameID"})

    df = raw.merge(feat, on="GameID")
    # Exclude EV ties
    df = df[df["ev_diff"] != 0].copy()
    # ev_diff = ev_A - ev_B in this dataset.
    # If ev_diff > 0: A is EV-optimal. Choosing B=1 is failure.
    # If ev_diff < 0: B is EV-optimal. Choosing B=0 is failure.
    df["ev_failure"] = np.where(df["ev_diff"] > 0, df["B"], 1 - df["B"]).astype(int)
    return df


def run_naive_logistic(df):
    """Standard logistic regression ignoring clustering."""
    import statsmodels.api as sm
    X = sm.add_constant(df["block"].values)
    y = df["ev_failure"].values
    model = sm.Logit(y, X).fit(disp=0)
    coef = model.params[1]
    se = model.bse[1]
    ci = model.conf_int()[1]  # row index 1
    return {
        "model": "naive_logistic",
        "predictor": "block",
        "coefficient": coef,
        "se": se,
        "ci_lower": ci[0],
        "ci_upper": ci[1],
        "p_value": model.pvalues[1],
        "odds_ratio": np.exp(coef),
        "n_observations": len(df),
        "n_clusters_subj": df["SubjID"].nunique(),
        "n_clusters_game": df["GameID"].nunique(),
        "notes": ""
    }


def run_gee(df):
    """GEE with exchangeable correlation, clustered by SubjID."""
    from statsmodels.genmod.generalized_estimating_equations import GEE
    from statsmodels.genmod.families import Binomial
    from statsmodels.genmod.cov_struct import Exchangeable

    # Sort by cluster for GEE
    df_sorted = df.sort_values("SubjID").reset_index(drop=True)

    model = GEE.from_formula(
        "ev_failure ~ block",
        groups="SubjID",
        family=Binomial(),
        cov_struct=Exchangeable(),
        data=df_sorted
    )
    result = model.fit()
    coef = result.params["block"]
    se = result.bse["block"]
    ci = result.conf_int().loc["block"]
    return {
        "model": "gee_exchangeable",
        "predictor": "block",
        "coefficient": coef,
        "se": se,
        "ci_lower": ci[0],
        "ci_upper": ci[1],
        "p_value": result.pvalues["block"],
        "odds_ratio": np.exp(coef),
        "n_observations": len(df_sorted),
        "n_clusters_subj": df_sorted["SubjID"].nunique(),
        "n_clusters_game": df_sorted["GameID"].nunique(),
        "notes": f"exchangeable corr={result.cov_struct.summary()}"
    }


def run_cluster_robust(df):
    """Logistic regression with cluster-robust SEs (sandwich) by SubjID."""
    import statsmodels.api as sm
    X = sm.add_constant(df["block"].values)
    y = df["ev_failure"].values
    groups = df["SubjID"].values
    model = sm.Logit(y, X).fit(disp=0, cov_type="cluster",
                                cov_kwds={"groups": groups})
    coef = model.params[1]
    se = model.bse[1]
    ci = model.conf_int()[1]  # row index 1
    return {
        "model": "cluster_robust_logistic",
        "predictor": "block",
        "coefficient": coef,
        "se": se,
        "ci_lower": ci[0],
        "ci_upper": ci[1],
        "p_value": model.pvalues[1],
        "odds_ratio": np.exp(coef),
        "n_observations": len(df),
        "n_clusters_subj": df["SubjID"].nunique(),
        "n_clusters_game": df["GameID"].nunique(),
        "notes": "sandwich SE clustered by SubjID"
    }


def write_report(results, df):
    """Write markdown report."""
    # Descriptive rates by block
    block_rates = df.groupby("block")["ev_failure"].mean()

    naive = next(r for r in results if r["model"] == "naive_logistic")
    gee = next((r for r in results if r["model"] == "gee_exchangeable"), None)
    cluster = next((r for r in results if r["model"] == "cluster_robust_logistic"), None)

    primary = gee if gee else cluster

    lines = [
        "# CPC18 Clustered Trial-Level Robustness Check",
        "",
        "## Purpose",
        "",
        "Address the concern that trial-level CIs assume independence. Observations are",
        "nested within participants (926 participants × ~750 trials each). This check",
        "tests whether the block-related decline in EV failure survives clustering.",
        "",
        "## Descriptive Rates by Block",
        "",
        "| Block | EV Failure Rate | N trials |",
        "|-------|----------------|----------|",
    ]
    for b in sorted(block_rates.index):
        n = (df["block"] == b).sum()
        lines.append(f"| {b} | {block_rates[b]:.4f} ({block_rates[b]*100:.1f}%) | {n:,} |")

    lines += [
        "",
        f"Total observations: {len(df):,} (after excluding 14 GameIDs with ev_diff = 0)",
        f"Participants: {df['SubjID'].nunique()}",
        f"Games: {df['GameID'].nunique()}",
        "",
        "## Method",
        "",
    ]

    if gee:
        lines.append("Primary method: GEE with binomial family and exchangeable correlation")
        lines.append("structure, clustered by participant (SubjID). This accounts for")
        lines.append("within-participant correlation in the standard errors.")
    elif cluster:
        lines.append("Primary method: Logistic regression with cluster-robust (sandwich)")
        lines.append("standard errors, clustered by participant (SubjID).")

    lines += [
        "",
        "Fallback: Cluster-robust logistic regression (sandwich estimator).",
        "Comparison: Naive logistic regression (independent observations).",
        "",
        "## Results",
        "",
        "### Naive (Independent Observations)",
        "",
        f"- Coefficient (block): {naive['coefficient']:.5f}",
        f"- SE: {naive['se']:.5f}",
        f"- 95% CI: [{naive['ci_lower']:.5f}, {naive['ci_upper']:.5f}]",
        f"- OR: {naive['odds_ratio']:.4f}",
        f"- p-value: {naive['p_value']:.2e}",
        "",
    ]

    if gee:
        lines += [
            "### GEE (Exchangeable Correlation, Clustered by Participant)",
            "",
            f"- Coefficient (block): {gee['coefficient']:.5f}",
            f"- SE: {gee['se']:.5f}",
            f"- 95% CI: [{gee['ci_lower']:.5f}, {gee['ci_upper']:.5f}]",
            f"- OR: {gee['odds_ratio']:.4f}",
            f"- p-value: {gee['p_value']:.2e}",
            f"- Notes: {gee['notes']}",
            "",
        ]

    if cluster:
        lines += [
            "### Cluster-Robust Logistic (Sandwich SE, Clustered by Participant)",
            "",
            f"- Coefficient (block): {cluster['coefficient']:.5f}",
            f"- SE: {cluster['se']:.5f}",
            f"- 95% CI: [{cluster['ci_lower']:.5f}, {cluster['ci_upper']:.5f}]",
            f"- OR: {cluster['odds_ratio']:.4f}",
            f"- p-value: {cluster['p_value']:.2e}",
            "",
        ]

    # Comparison table
    gee_coef = f"{gee['coefficient']:.5f}" if gee else "—"
    gee_se = f"{gee['se']:.5f}" if gee else "—"
    gee_p = f"{gee['p_value']:.2e}" if gee else "—"
    gee_or = f"{gee['odds_ratio']:.4f}" if gee else "—"
    cl_coef = f"{cluster['coefficient']:.5f}" if cluster else "—"
    cl_se = f"{cluster['se']:.5f}" if cluster else "—"
    cl_p = f"{cluster['p_value']:.2e}" if cluster else "—"
    cl_or = f"{cluster['odds_ratio']:.4f}" if cluster else "—"

    lines += [
        "### Comparison",
        "",
        "| Metric | Naive | GEE | Cluster-Robust |",
        "|--------|-------|-----|----------------|",
        f"| Coefficient | {naive['coefficient']:.5f} | {gee_coef} | {cl_coef} |",
        f"| SE | {naive['se']:.5f} | {gee_se} | {cl_se} |",
        f"| p-value | {naive['p_value']:.2e} | {gee_p} | {cl_p} |",
        f"| OR | {naive['odds_ratio']:.4f} | {gee_or} | {cl_or} |",
    ]
    if gee and cluster:
        lines.append(f"| SE inflation | 1.0x | {gee['se']/naive['se']:.1f}x | {cluster['se']/naive['se']:.1f}x |")

    lines += [
        "",
        "## Interpretation",
        "",
    ]

    if primary and primary["p_value"] < 0.05:
            p_str = "< .001" if primary["p_value"] < 0.001 else f"= {primary['p_value']:.3f}"
            lines += [
                f"The block-related decline in EV failure **remains statistically significant**",
                f"after accounting for within-participant clustering (p = {primary['p_value']:.2e}).",
                f"The SE inflates by {primary['se']/naive['se']:.1f}x relative to the naive estimate,",
                f"but the effect remains robust. Each additional block is associated with",
                f"{(1 - primary['odds_ratio'])*100:.1f}% lower odds of EV failure (OR = {primary['odds_ratio']:.4f}).",
                "",
                "## Manuscript Implication",
                "",
                "Add to Results (Changes Across Blocks):",
                f"> A GEE with exchangeable correlation clustered by participant confirmed that",
                f"> the block-related decline remained significant (OR = {primary['odds_ratio']:.3f},",
                f"> 95% CI [{primary['ci_lower']:.3f}, {primary['ci_upper']:.3f}], p {p_str}).",
            ]
    else:
        lines += [
            "The block-related decline in EV failure **does not reach significance**",
            "after accounting for within-participant clustering.",
            "",
            "## Manuscript Implication",
            "",
            "Revise block paragraph to purely descriptive language.",
        ]

    (OUT_REPORTS / "cpc18_clustered_trial_check.md").write_text("\n".join(lines))


def main():
    print("Loading trial-level data...")
    df = load_trial_data()
    print(f"  {len(df):,} trials, {df['SubjID'].nunique()} participants, {df['GameID'].nunique()} games")
    print(f"  Block 1 failure: {df[df['block']==1]['ev_failure'].mean():.4f}")
    print(f"  Block 5 failure: {df[df['block']==5]['ev_failure'].mean():.4f}")

    results = []

    print("\nNaive logistic...")
    results.append(run_naive_logistic(df))
    print(f"  coef={results[-1]['coefficient']:.5f}, SE={results[-1]['se']:.5f}, p={results[-1]['p_value']:.2e}")

    print("\nGEE (exchangeable, clustered by SubjID)...")
    try:
        results.append(run_gee(df))
        print(f"  coef={results[-1]['coefficient']:.5f}, SE={results[-1]['se']:.5f}, p={results[-1]['p_value']:.2e}")
    except Exception as e:
        print(f"  GEE failed: {e}")

    print("\nCluster-robust logistic...")
    try:
        results.append(run_cluster_robust(df))
        print(f"  coef={results[-1]['coefficient']:.5f}, SE={results[-1]['se']:.5f}, p={results[-1]['p_value']:.2e}")
    except Exception as e:
        print(f"  Cluster-robust failed: {e}")

    # Save table
    pd.DataFrame(results).to_csv(OUT_TABLES / "cpc18_clustered_trial_model.csv", index=False)
    print(f"\nSaved: {OUT_TABLES / 'cpc18_clustered_trial_model.csv'}")

    # Write report
    write_report(results, df)
    print(f"Saved: {OUT_REPORTS / 'cpc18_clustered_trial_check.md'}")


if __name__ == "__main__":
    main()
