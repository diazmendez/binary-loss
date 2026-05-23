"""Spec 013: Build advanced features for choices13k and CPC18.

Computes beyond-EV features (risk, loss, skewness, dominance, salience, similarity)
and generates summary report with correlations to EV failure.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from cognitive_graph.common.advanced_features import compute_advanced_features

C13K_COMMON = ROOT / "data/interim/choices13k_common.parquet"
CPC_COMMON = ROOT / "data/interim/cpc18_common.parquet"
C13K_FEATURES = ROOT / "data/interim/choices13k_features.parquet"
CPC_FEATURES = ROOT / "data/interim/cpc18_features.parquet"
C13K_ADV_OUT = ROOT / "data/interim/choices13k_advanced_features.parquet"
CPC_ADV_OUT = ROOT / "data/interim/cpc18_advanced_features.parquet"
REPORT_OUT = ROOT / "outputs/reports/advanced_feature_summary.md"
DICT_CSV = ROOT / "outputs/tables/advanced_feature_dictionary.csv"

# Feature dictionary
FEATURE_DICT = [
    # Risk/Dispersion
    ("variance_A", "risk", "Σ pᵢ(vᵢ - EV_A)²", "numeric", "No"),
    ("variance_B", "risk", "Σ pᵢ(vᵢ - EV_B)²", "numeric", "No"),
    ("std_A", "risk", "√variance_A", "numeric", "No"),
    ("std_B", "risk", "√variance_B", "numeric", "No"),
    ("cv_A", "risk", "std_A / |EV_A|; NaN if EV≈0", "numeric", "Yes (EV≈0)"),
    ("cv_B", "risk", "std_B / |EV_B|; NaN if EV≈0", "numeric", "Yes (EV≈0)"),
    ("range_A", "risk", "max_A - min_A", "numeric", "No"),
    ("range_B", "risk", "max_B - min_B", "numeric", "No"),
    ("variance_diff", "risk", "variance_A - variance_B", "numeric", "No"),
    ("std_diff", "risk", "std_A - std_B", "numeric", "No"),
    ("range_diff", "risk", "range_A - range_B", "numeric", "No"),
    ("riskier_option", "risk", "A/B/equal by variance", "categorical", "No"),
    ("ev_risk_conflict", "risk", "higher_ev ≠ riskier_option", "boolean", "No"),
    # Loss
    ("has_loss_A", "loss", "any outcome < 0 in A", "boolean", "No"),
    ("has_loss_B", "loss", "any outcome < 0 in B", "boolean", "No"),
    ("prob_loss_A", "loss", "Σ pᵢ where vᵢ < 0 in A", "numeric", "No"),
    ("prob_loss_B", "loss", "Σ pᵢ where vᵢ < 0 in B", "numeric", "No"),
    ("expected_loss_A", "loss", "Σ pᵢvᵢ where vᵢ < 0 in A", "numeric", "No"),
    ("expected_loss_B", "loss", "Σ pᵢvᵢ where vᵢ < 0 in B", "numeric", "No"),
    ("min_negative_A", "loss", "min negative outcome in A (0 if none)", "numeric", "No"),
    ("min_negative_B", "loss", "min negative outcome in B (0 if none)", "numeric", "No"),
    ("is_mixed_A", "loss", "A has both positive and negative outcomes", "boolean", "No"),
    ("is_mixed_B", "loss", "B has both positive and negative outcomes", "boolean", "No"),
    ("any_loss", "loss", "either option has loss", "boolean", "No"),
    ("both_have_loss", "loss", "both options have loss", "boolean", "No"),
    ("loss_asymmetry", "loss", "one option has loss, other doesn't", "boolean", "No"),
    ("ev_favored_has_loss", "loss", "higher-EV option has negative outcome", "boolean", "No"),
    ("max_favored_has_loss", "loss", "higher-max option has negative outcome", "boolean", "No"),
    ("prob_loss_diff", "loss", "prob_loss_A - prob_loss_B", "numeric", "No"),
    ("expected_loss_diff", "loss", "expected_loss_A - expected_loss_B", "numeric", "No"),
    # Skewness
    ("skewness_A", "skewness", "probability-weighted 3rd moment of A", "numeric", "Yes (variance=0)"),
    ("skewness_B", "skewness", "probability-weighted 3rd moment of B", "numeric", "Yes (variance=0)"),
    ("upside_distance_A", "skewness", "max_A - EV_A", "numeric", "No"),
    ("upside_distance_B", "skewness", "max_B - EV_B", "numeric", "No"),
    ("downside_distance_A", "skewness", "EV_A - min_A", "numeric", "No"),
    ("downside_distance_B", "skewness", "EV_B - min_B", "numeric", "No"),
    ("upside_ratio_A", "skewness", "upside/(upside+downside) for A", "numeric", "No"),
    ("upside_ratio_B", "skewness", "upside/(upside+downside) for B", "numeric", "No"),
    ("skewness_diff", "skewness", "skewness_A - skewness_B", "numeric", "Yes"),
    ("upside_ratio_diff", "skewness", "upside_ratio_A - upside_ratio_B", "numeric", "No"),
    # Dominance
    ("A_dominates_B", "dominance", "A FOSD-dominates B", "boolean", "No"),
    ("B_dominates_A", "dominance", "B FOSD-dominates A", "boolean", "No"),
    ("any_dominance", "dominance", "either option dominates", "boolean", "No"),
    ("dominant_option", "dominance", "A/B/none", "categorical", "No"),
    ("ev_matches_dominance", "dominance", "EV agrees with dominance (or none)", "boolean", "No"),
    # Salience
    ("prob_best_outcome_A", "salience", "P(max outcome) in A", "numeric", "No"),
    ("prob_best_outcome_B", "salience", "P(max outcome) in B", "numeric", "No"),
    ("prob_worst_outcome_A", "salience", "P(min outcome) in A", "numeric", "No"),
    ("prob_worst_outcome_B", "salience", "P(min outcome) in B", "numeric", "No"),
    ("has_rare_high_gain_A", "salience", "max_A>0 and P(max_A)≤0.10", "boolean", "No"),
    ("has_rare_high_gain_B", "salience", "max_B>0 and P(max_B)≤0.10", "boolean", "No"),
    ("has_rare_loss_A", "salience", "min_A<0 and P(min_A)≤0.10", "boolean", "No"),
    ("has_rare_loss_B", "salience", "min_B<0 and P(min_B)≤0.10", "boolean", "No"),
    ("max_ratio", "salience", "max_B / max_A (NaN if max_A≤0)", "numeric", "Yes (max_A≤0)"),
    ("best_outcome_option", "salience", "who has higher max", "categorical", "No"),
    ("worst_outcome_option", "salience", "who has lower min", "categorical", "No"),
    ("rare_high_gain_option", "salience", "A/B/both/neither", "categorical", "No"),
    ("rare_loss_option", "salience", "A/B/both/neither", "categorical", "No"),
    ("salience_conflict", "salience", "best_outcome ≠ worst_outcome option", "boolean", "No"),
    # Similarity
    ("ev_abs_diff", "similarity", "|ev_A - ev_B|", "numeric", "No"),
    ("range_overlap", "similarity", "normalized range overlap [0,1]", "numeric", "No"),
    ("n_shared_values", "similarity", "count of shared outcome values", "numeric", "No"),
    ("total_outcomes", "similarity", "n_outcomes_A + n_outcomes_B", "numeric", "No"),
]


def build_features(common_df, id_col):
    """Compute advanced features for all rows."""
    results = []
    errors = 0
    for _, row in common_df.iterrows():
        try:
            feats = compute_advanced_features(row.to_dict())
            feats[id_col] = row[id_col]
            results.append(feats)
        except Exception:
            errors += 1
    return pd.DataFrame(results), errors


def compute_ev_failure(common_df, features_df, b_rate_col, id_col):
    """Compute EV failure indicator."""
    merged = common_df[[id_col, b_rate_col]].merge(features_df[[id_col, "ev_diff"]], on=id_col)
    merged = merged[merged["ev_diff"] != 0].copy()
    merged["ev_failure"] = ((merged["ev_diff"] > 0) & (merged[b_rate_col] > 0.5)) | \
                           ((merged["ev_diff"] < 0) & (merged[b_rate_col] < 0.5))
    return merged[[id_col, "ev_failure"]]


def correlations_with_failure(adv_df, failure_df, id_col):
    """Compute correlations between advanced features and EV failure."""
    merged = adv_df.merge(failure_df, on=id_col)
    numeric_cols = merged.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c not in [id_col, "ev_failure"]]
    bool_cols = [c for c in merged.columns if merged[c].dtype == bool and c != "ev_failure"]

    corrs = {}
    for col in numeric_cols + bool_cols:
        series = merged[col].astype(float) if merged[col].dtype == bool else merged[col]
        valid = series.notna() & merged["ev_failure"].notna()
        if valid.sum() > 10:
            corrs[col] = series[valid].corr(merged["ev_failure"].astype(float)[valid])
    return pd.Series(corrs).sort_values(key=abs, ascending=False)


def generate_report(c13k_adv, cpc_adv, c13k_corrs, cpc_corrs, c13k_errors, cpc_errors,
                    c13k_common, cpc_common):
    lines = []
    lines.append("# Advanced Feature Summary\n")
    lines.append(f"Generated: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M')} UTC\n")

    # Overview
    lines.append("## Overview\n")
    lines.append(f"- choices13k: {len(c13k_adv)} rows, {c13k_errors} computation errors")
    lines.append(f"- CPC18: {len(cpc_adv)} rows, {cpc_errors} computation errors")
    lines.append(f"- Total features: {len(FEATURE_DICT)}")
    lines.append(f"- Heuristic constants: RARE_THRESHOLD = {0.10}")
    lines.append("")

    # NaN counts
    lines.append("## NaN Counts\n")
    lines.append("| Feature | choices13k NaN | CPC18 NaN |")
    lines.append("|---------|---------------|-----------|")
    for col in c13k_adv.columns:
        if col == "problem_id":
            continue
        c_nan = int(c13k_adv[col].isna().sum()) if col in c13k_adv.columns else 0
        p_nan = int(cpc_adv[col].isna().sum()) if col in cpc_adv.columns else 0
        if c_nan > 0 or p_nan > 0:
            lines.append(f"| {col} | {c_nan} | {p_nan} |")
    lines.append("")

    # Numeric distributions
    lines.append("## Numeric Feature Distributions\n")
    num_cols = c13k_adv.select_dtypes(include=[np.number]).columns.tolist()
    num_cols = [c for c in num_cols if c != "problem_id"]
    lines.append("| Feature | c13k Mean | c13k Std | c13k Min | c13k Max | CPC18 Mean | CPC18 Std |")
    lines.append("|---------|-----------|---------|---------|---------|-----------|----------|")
    for col in num_cols[:30]:  # Top 30 for readability
        if col not in cpc_adv.columns:
            continue
        cs = c13k_adv[col]
        ps = cpc_adv[col]
        lines.append(f"| {col} | {cs.mean():.3f} | {cs.std():.3f} | {cs.min():.3f} | {cs.max():.3f} | {ps.mean():.3f} | {ps.std():.3f} |")
    lines.append("")

    # Boolean distributions
    lines.append("## Boolean Feature Distributions\n")
    bool_cols = [c for c in c13k_adv.columns if c13k_adv[c].dtype == bool]
    if bool_cols:
        lines.append("| Feature | c13k True% | CPC18 True% |")
        lines.append("|---------|-----------|------------|")
        for col in bool_cols:
            ct = c13k_adv[col].mean() * 100
            pt = cpc_adv[col].mean() * 100 if col in cpc_adv.columns else float("nan")
            lines.append(f"| {col} | {ct:.1f}% | {pt:.1f}% |")
        lines.append("")

    # Categorical distributions
    lines.append("## Categorical Feature Distributions\n")
    cat_cols = [c for c in c13k_adv.columns if c13k_adv[c].dtype == object and c != "problem_id"]
    for col in cat_cols:
        lines.append(f"**{col}**:")
        c_vc = c13k_adv[col].value_counts()
        p_vc = cpc_adv[col].value_counts() if col in cpc_adv.columns else pd.Series()
        lines.append(f"- choices13k: {c_vc.to_dict()}")
        lines.append(f"- CPC18: {p_vc.to_dict()}")
        lines.append("")

    # Correlations with EV failure
    lines.append("## Top 15 Correlations with EV Failure\n")
    lines.append("### choices13k\n")
    lines.append("| Feature | Correlation |")
    lines.append("|---------|------------|")
    for feat, corr in c13k_corrs.head(15).items():
        lines.append(f"| {feat} | {corr:.4f} |")
    lines.append("")

    lines.append("### CPC18\n")
    lines.append("| Feature | Correlation |")
    lines.append("|---------|------------|")
    for feat, corr in cpc_corrs.head(15).items():
        lines.append(f"| {feat} | {corr:.4f} |")
    lines.append("")

    # Cross-dataset comparison
    lines.append("## Cross-Dataset Feature Comparison\n")
    lines.append("Features with largest distribution differences (by mean):\n")
    diffs = []
    for col in num_cols:
        if col in cpc_adv.columns and col != "problem_id":
            cm = c13k_adv[col].mean()
            pm = cpc_adv[col].mean()
            cs = c13k_adv[col].std()
            if cs > 0:
                diffs.append((col, (pm - cm) / cs))
    diffs.sort(key=lambda x: abs(x[1]), reverse=True)
    lines.append("| Feature | Standardized Diff (CPC18 − c13k) |")
    lines.append("|---------|----------------------------------|")
    for feat, d in diffs[:15]:
        lines.append(f"| {feat} | {d:.3f} |")
    lines.append("")

    # Divergence explanation
    lines.append("## Do Advanced Features Explain Known Divergences?\n")
    lines.append("### ev_max_conflict divergence\n")
    lines.append("In choices13k, ev_max_conflict ↑ failure. In CPC18, it ↓ failure.\n")
    # Compare advanced features for conflict vs no-conflict in each dataset
    c13k_feat = pd.read_parquet(C13K_FEATURES)
    c13k_merged = c13k_adv.merge(c13k_feat[["problem_id", "ev_max_conflict"]], on="problem_id")
    cpc_feat = pd.read_parquet(CPC_FEATURES)
    cpc_merged = cpc_adv.merge(cpc_feat[["game_id", "ev_max_conflict"]], on="game_id")

    key_feats = ["variance_diff", "std_diff", "skewness_diff", "ev_risk_conflict",
                 "loss_asymmetry", "range_overlap", "ev_abs_diff"]
    lines.append("| Feature | c13k conflict | c13k no-conflict | CPC18 conflict | CPC18 no-conflict |")
    lines.append("|---------|--------------|-----------------|---------------|------------------|")
    for f in key_feats:
        if f in c13k_merged.columns and f in cpc_merged.columns:
            cc = c13k_merged[c13k_merged["ev_max_conflict"]][f]
            cn = c13k_merged[~c13k_merged["ev_max_conflict"]][f]
            pc = cpc_merged[cpc_merged["ev_max_conflict"]][f]
            pn = cpc_merged[~cpc_merged["ev_max_conflict"]][f]
            if cc.dtype == bool:
                lines.append(f"| {f} | {cc.mean()*100:.1f}% | {cn.mean()*100:.1f}% | {pc.mean()*100:.1f}% | {pn.mean()*100:.1f}% |")
            else:
                lines.append(f"| {f} | {cc.mean():.3f} | {cn.mean():.3f} | {pc.mean():.3f} | {pn.mean():.3f} |")
    lines.append("")

    # Anti-learning characterization
    lines.append("## CPC18 Anti-Learning Characterization\n")
    block_csv = ROOT / "outputs/tables/cpc18_block_level_choice.csv"
    if block_csv.exists():
        block_df = pd.read_csv(block_csv)
        b1 = block_df[block_df["block"] == 1][["game_id", "ev_consistency"]].rename(columns={"ev_consistency": "early"})
        b5 = block_df[block_df["block"] == 5][["game_id", "ev_consistency"]].rename(columns={"ev_consistency": "late"})
        shifts = b1.merge(b5, on="game_id")
        shifts["learning_shift"] = shifts["late"] - shifts["early"]
        anti = shifts[shifts["learning_shift"] < 0]["game_id"]
        learners = shifts[shifts["learning_shift"] > 0]["game_id"]

        anti_feats = cpc_adv[cpc_adv["game_id"].isin(anti)]
        learn_feats = cpc_adv[cpc_adv["game_id"].isin(learners)]

        lines.append(f"Anti-learning GameIDs: {len(anti)}, Learning GameIDs: {len(learners)}\n")
        lines.append("| Feature | Anti-learning Mean | Learning Mean | Diff |")
        lines.append("|---------|-------------------|--------------|------|")
        compare_feats = ["variance_diff", "std_diff", "ev_abs_diff", "range_overlap",
                         "skewness_diff", "prob_loss_diff", "upside_ratio_diff", "total_outcomes"]
        for f in compare_feats:
            if f in anti_feats.columns:
                am = anti_feats[f].mean()
                lm = learn_feats[f].mean()
                lines.append(f"| {f} | {am:.3f} | {lm:.3f} | {am-lm:.3f} |")

        # Boolean features
        bool_compare = ["ev_risk_conflict", "loss_asymmetry", "any_dominance", "salience_conflict"]
        for f in bool_compare:
            if f in anti_feats.columns:
                am = anti_feats[f].mean() * 100
                lm = learn_feats[f].mean() * 100
                lines.append(f"| {f} | {am:.1f}% | {lm:.1f}% | {am-lm:.1f}pp |")
        lines.append("")
    else:
        lines.append("Block-level CSV not found; skipping anti-learning analysis.\n")

    # Limitations
    lines.append("## Limitations\n")
    lines.append("- All analyses are exploratory.")
    lines.append("- Dominance is rare by design in these experiments.")
    lines.append("- CPC18 empirical reconstruction may affect variance/skewness estimates.")
    lines.append("- Correlations do not imply causation.")
    lines.append("")

    return "\n".join(lines)


def main():
    print("Loading data...")
    c13k_common = pd.read_parquet(C13K_COMMON)
    cpc_common = pd.read_parquet(CPC_COMMON)

    print("Computing advanced features for choices13k...")
    c13k_adv, c13k_errors = build_features(c13k_common, "problem_id")
    print(f"  {len(c13k_adv)} rows, {c13k_errors} errors")

    print("Computing advanced features for CPC18...")
    cpc_adv, cpc_errors = build_features(cpc_common, "game_id")
    print(f"  {len(cpc_adv)} rows, {cpc_errors} errors")

    print("Saving parquets...")
    C13K_ADV_OUT.parent.mkdir(parents=True, exist_ok=True)
    c13k_adv.to_parquet(C13K_ADV_OUT, index=False)
    cpc_adv.to_parquet(CPC_ADV_OUT, index=False)
    print(f"  {C13K_ADV_OUT}")
    print(f"  {CPC_ADV_OUT}")

    print("Computing EV failure correlations...")
    c13k_feat = pd.read_parquet(C13K_FEATURES)
    cpc_feat = pd.read_parquet(CPC_FEATURES)
    c13k_failure = compute_ev_failure(c13k_common, c13k_feat, "bRate", "problem_id")
    cpc_failure = compute_ev_failure(cpc_common, cpc_feat, "mean_choice_B", "game_id")
    c13k_corrs = correlations_with_failure(c13k_adv, c13k_failure, "problem_id")
    cpc_corrs = correlations_with_failure(cpc_adv, cpc_failure, "game_id")
    print(f"  choices13k top corr: {c13k_corrs.index[0]} = {c13k_corrs.iloc[0]:.4f}")
    print(f"  CPC18 top corr: {cpc_corrs.index[0]} = {cpc_corrs.iloc[0]:.4f}")

    print("Generating report...")
    report = generate_report(c13k_adv, cpc_adv, c13k_corrs, cpc_corrs,
                             c13k_errors, cpc_errors, c13k_common, cpc_common)
    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.write_text(report)
    print(f"  {REPORT_OUT}")

    print("Saving feature dictionary...")
    dict_df = pd.DataFrame(FEATURE_DICT, columns=["feature_name", "group", "definition", "type", "can_be_nan"])
    DICT_CSV.parent.mkdir(parents=True, exist_ok=True)
    dict_df.to_csv(DICT_CSV, index=False)
    print(f"  {DICT_CSV}")

    print("Done.")


if __name__ == "__main__":
    main()
