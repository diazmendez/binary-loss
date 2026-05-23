"""Spec 010: Cross-Dataset EV Failure Comparison (choices13k vs CPC18)."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss

ROOT = Path(__file__).resolve().parent.parent
REPORT_OUT = ROOT / "outputs/reports/cross_dataset_ev_failure_comparison.md"
SUMMARY_CSV = ROOT / "outputs/tables/cross_dataset_summary.csv"
BREAKDOWN_CSV = ROOT / "outputs/tables/cross_dataset_ev_failure_breakdown.csv"
FIG_DIR = ROOT / "outputs/figures"


def load_datasets():
    c13k_common = pd.read_parquet(ROOT / "data/interim/choices13k_common.parquet")
    c13k_feat = pd.read_parquet(ROOT / "data/interim/choices13k_features.parquet")
    c13k = pd.concat([c13k_common, c13k_feat.drop(columns=["problem_id"])], axis=1)
    c13k["observed_B_rate"] = c13k["bRate"]
    c13k["dataset"] = "choices13k"

    cpc_common = pd.read_parquet(ROOT / "data/interim/cpc18_common.parquet")
    cpc_feat = pd.read_parquet(ROOT / "data/interim/cpc18_features.parquet")
    cpc = cpc_common.merge(cpc_feat, on="game_id")
    cpc["observed_B_rate"] = cpc["mean_choice_B"]
    cpc["dataset"] = "cpc18"

    return c13k, cpc


def classify_ev(df):
    df["ev_prediction"] = np.select(
        [df["ev_diff"] > 0, df["ev_diff"] < 0], ["A", "B"], default="tie")
    df["observed_majority"] = np.select(
        [df["observed_B_rate"] < 0.5, df["observed_B_rate"] > 0.5], ["A", "B"], default="tie")
    mask = (df["ev_prediction"] != "tie") & (df["observed_majority"] != "tie")
    df["ev_consistent"] = np.where(mask, df["ev_prediction"] == df["observed_majority"], np.nan)
    return df


def dataset_summary(df, name):
    mask = df["ev_consistent"].notna()
    subset = df[mask]
    n_con = int(subset["ev_consistent"].sum())
    n_incon = int((~subset["ev_consistent"].astype(bool)).sum())
    total = n_con + n_incon
    return {
        "dataset": name,
        "n_problems": len(df),
        "n_consistent": n_con,
        "n_inconsistent": n_incon,
        "ev_failure_rate": n_incon / total * 100 if total > 0 else 0,
        "n_ev_ties": int((df["ev_prediction"] == "tie").sum()),
        "n_observed_ties": int((df["observed_majority"] == "tie").sum()),
        "mean_observed_B_rate": df["observed_B_rate"].mean(),
        "corr_ev_diff_choice": df["ev_diff"].corr(df["observed_B_rate"]),
    }


def breakdown_by_var(df, var, dataset_name):
    mask = df["ev_consistent"].notna()
    subset = df[mask]
    if var not in subset.columns:
        return pd.DataFrame()
    grouped = subset.groupby(var)["ev_consistent"].agg(["count", "sum"]).reset_index()
    grouped.columns = [var, "n_problems", "n_consistent"]
    grouped["n_inconsistent"] = grouped["n_problems"] - grouped["n_consistent"]
    grouped["failure_rate"] = grouped["n_inconsistent"] / grouped["n_problems"] * 100
    grouped["dataset"] = dataset_name
    grouped["variable"] = var
    grouped = grouped.rename(columns={var: "category"})
    return grouped[["dataset", "variable", "category", "n_problems", "n_inconsistent", "failure_rate"]]


def compute_breakdowns(c13k, cpc):
    rows = []
    # Shared variables
    for var in ["ambiguity", "corr", "ev_max_conflict", "has_safe_option_A", "has_safe_option_B"]:
        rows.append(breakdown_by_var(c13k, var, "choices13k"))
        rows.append(breakdown_by_var(cpc, var, "cpc18"))

    # n_outcomes_B grouped
    for df, name in [(c13k, "choices13k"), (cpc, "cpc18")]:
        mask = df["ev_consistent"].notna()
        sub = df[mask].copy()
        sub["n_outcomes_B_group"] = pd.cut(sub["n_outcomes_B"], bins=[0, 2, 4, 6, 100], labels=["1-2", "3-4", "5-6", "7+"])
        bd = sub.groupby("n_outcomes_B_group", observed=True)["ev_consistent"].agg(["count", "sum"]).reset_index()
        bd.columns = ["category", "n_problems", "n_consistent"]
        bd["n_inconsistent"] = bd["n_problems"] - bd["n_consistent"]
        bd["failure_rate"] = bd["n_inconsistent"] / bd["n_problems"] * 100
        bd["dataset"] = name
        bd["variable"] = "n_outcomes_B_group"
        rows.append(bd[["dataset", "variable", "category", "n_problems", "n_inconsistent", "failure_rate"]])

    # Dataset-specific
    rows.append(breakdown_by_var(c13k, "feedback", "choices13k"))
    rows.append(breakdown_by_var(cpc, "feedback_available", "cpc18"))
    rows.append(breakdown_by_var(cpc, "reconstruction_method", "cpc18"))

    return pd.concat([r for r in rows if len(r) > 0], ignore_index=True)


def fit_logistic(df, name):
    mask = df["ev_consistent"].notna()
    sub = df[mask].copy()
    sub["min_value_diff"] = sub["min_value_A"] - sub["min_value_B"]
    sub["y"] = (sub["observed_B_rate"] > 0.5).astype(int)

    feat_cols = ["ev_diff", "max_value_diff", "min_value_diff", "n_outcomes_B",
                 "ambiguity", "ev_max_conflict", "has_safe_option_A", "has_safe_option_B"]
    X = sub[feat_cols].copy()
    for col in ["ambiguity", "ev_max_conflict", "has_safe_option_A", "has_safe_option_B"]:
        X[col] = X[col].astype(int)
    y = sub["y"]

    model = LogisticRegression(max_iter=2000, solver="lbfgs")
    model.fit(X, y)

    y_pred = model.predict(X)
    accuracy = accuracy_score(y, y_pred)

    # McFadden pseudo R²
    ll_model = -log_loss(y, model.predict_proba(X), normalize=False)
    ll_null = -log_loss(y, np.full((len(y), 2), [1 - y.mean(), y.mean()]), normalize=False)
    pseudo_r2 = 1 - (ll_model / ll_null)

    coefs = pd.DataFrame({
        "feature": ["intercept"] + feat_cols,
        f"coef_{name}": np.concatenate([model.intercept_, model.coef_[0]]),
    })
    return coefs, pseudo_r2, accuracy


def top_failures(df, name, n=20):
    incon = df[df["ev_consistent"] == False].copy()  # noqa: E712
    incon["failure_strength"] = np.where(
        incon["ev_diff"] > 0, incon["observed_B_rate"], 1 - incon["observed_B_rate"])
    top = incon.nlargest(n, "failure_strength")
    cols = ["observed_B_rate", "ev_A", "ev_B", "ev_diff", "max_value_A", "max_value_B",
            "n_outcomes_A", "n_outcomes_B", "ambiguity", "ev_max_conflict"]
    result = top[cols].copy()
    result["dataset"] = name
    if name == "choices13k":
        result["id"] = top["problem_id"].values
        result["reconstruction_method"] = ""
    else:
        result["id"] = top["game_id"].values
        result["reconstruction_method"] = top["reconstruction_method"].values
    return result.reset_index(drop=True)


def make_figures(c13k, cpc):
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    # Figure 1: Bar chart of failure rates by key predictors
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    predictors = [("ambiguity", "Ambiguity"), ("ev_max_conflict", "EV/Max Conflict"),
                  ("has_safe_option_A", "Safe Option A")]

    for ax, (var, label) in zip(axes, predictors):
        rates = {}
        for df, name in [(c13k, "choices13k"), (cpc, "cpc18")]:
            mask = df["ev_consistent"].notna()
            sub = df[mask]
            for val in [False, True]:
                g = sub[sub[var] == val]
                if len(g) > 0:
                    rate = (g["ev_consistent"] == False).sum() / len(g) * 100
                    rates[(name, val)] = rate

        x = np.arange(2)
        w = 0.35
        c13k_vals = [rates.get(("choices13k", False), 0), rates.get(("choices13k", True), 0)]
        cpc_vals = [rates.get(("cpc18", False), 0), rates.get(("cpc18", True), 0)]
        ax.bar(x - w/2, c13k_vals, w, label="choices13k", color="#4C72B0")
        ax.bar(x + w/2, cpc_vals, w, label="CPC18", color="#DD8452")
        ax.set_xticks(x)
        ax.set_xticklabels(["False", "True"])
        ax.set_xlabel(label)
        ax.set_ylabel("EV Failure Rate (%)")
        ax.legend()

    plt.tight_layout()
    plt.savefig(FIG_DIR / "cross_dataset_ev_failure_rates.png", dpi=150)
    plt.close()

    # Figure 2: Scatter ev_diff vs observed_B_rate
    fig, ax = plt.subplots(figsize=(8, 6))
    # choices13k: subsample for readability
    c13k_sample = c13k.sample(n=min(3000, len(c13k)), random_state=42)
    ax.scatter(c13k_sample["ev_diff"], c13k_sample["observed_B_rate"],
               alpha=0.15, s=8, c="#4C72B0", label=f"choices13k (n={len(c13k):,})")
    ax.scatter(cpc["ev_diff"], cpc["observed_B_rate"],
               alpha=0.7, s=30, c="#DD8452", marker="D", label=f"CPC18 (n={len(cpc)})")
    ax.axhline(0.5, color="gray", linestyle="--", linewidth=0.8)
    ax.axvline(0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_xlabel("ev_diff (EV_A − EV_B)")
    ax.set_ylabel("Observed B-rate")
    ax.legend()
    ax.set_title("EV Difference vs Observed Choice")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "cross_dataset_ev_vs_choice.png", dpi=150)
    plt.close()


def direction_comparison(breakdown_df):
    """Determine effect direction for each predictor in each dataset."""
    rows = []
    comparisons = [
        ("ambiguity", True, False),
        ("ev_max_conflict", True, False),
        ("has_safe_option_A", True, False),
        ("has_safe_option_B", True, False),
    ]
    for var, high_val, low_val in comparisons:
        for ds in ["choices13k", "cpc18"]:
            sub = breakdown_df[(breakdown_df["dataset"] == ds) & (breakdown_df["variable"] == var)]
            high = sub[sub["category"].astype(str) == str(high_val)]
            low = sub[sub["category"].astype(str) == str(low_val)]
            if len(high) > 0 and len(low) > 0:
                diff = high["failure_rate"].values[0] - low["failure_rate"].values[0]
                direction = "↑" if diff > 1 else ("↓" if diff < -1 else "—")
            else:
                direction = "?"
            rows.append({"predictor": f"{var}=True", "dataset": ds, "direction": direction})

    # n_outcomes_B: compare 7+ vs 1-2
    for ds in ["choices13k", "cpc18"]:
        sub = breakdown_df[(breakdown_df["dataset"] == ds) & (breakdown_df["variable"] == "n_outcomes_B_group")]
        high = sub[sub["category"] == "7+"]
        low = sub[sub["category"] == "1-2"]
        if len(high) > 0 and len(low) > 0:
            diff = high["failure_rate"].values[0] - low["failure_rate"].values[0]
            direction = "↑" if diff > 1 else ("↓" if diff < -1 else "—")
        else:
            direction = "?"
        rows.append({"predictor": "n_outcomes_B high", "dataset": ds, "direction": direction})

    return pd.DataFrame(rows)


def generate_report(summary_df, breakdown_df, dir_df, c13k_coefs, cpc_coefs,
                    c13k_r2, cpc_r2, c13k_acc, cpc_acc, top_c13k, top_cpc):
    lines = []
    lines.append("# Cross-Dataset EV Failure Comparison\n")
    lines.append(f"Generated: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M')} UTC\n")

    lines.append("## Overview\n")
    lines.append("Exploratory comparison of EV failure patterns between choices13k (14,568 condition-rows)")
    lines.append("and CPC18 (270 problem-level GameIDs). Both datasets share the same common representation")
    lines.append("with explicit `[[probability, value], ...]` outcome lists and identical feature set.\n")

    # Summary table
    lines.append("## Dataset-Level Summary\n")
    lines.append("| Metric | choices13k | CPC18 |")
    lines.append("|--------|-----------|-------|")
    c = summary_df[summary_df["dataset"] == "choices13k"].iloc[0]
    p = summary_df[summary_df["dataset"] == "cpc18"].iloc[0]
    lines.append(f"| N problems | {int(c['n_problems']):,} | {int(p['n_problems'])} |")
    lines.append(f"| N EV-consistent | {int(c['n_consistent']):,} | {int(p['n_consistent'])} |")
    lines.append(f"| N EV-inconsistent | {int(c['n_inconsistent']):,} | {int(p['n_inconsistent'])} |")
    lines.append(f"| EV failure rate | {c['ev_failure_rate']:.1f}% | {p['ev_failure_rate']:.1f}% |")
    lines.append(f"| N EV ties | {int(c['n_ev_ties'])} | {int(p['n_ev_ties'])} |")
    lines.append(f"| N observed ties | {int(c['n_observed_ties'])} | {int(p['n_observed_ties'])} |")
    lines.append(f"| Mean observed B-rate | {c['mean_observed_B_rate']:.3f} | {p['mean_observed_B_rate']:.3f} |")
    lines.append(f"| Corr(ev_diff, B-rate) | {c['corr_ev_diff_choice']:.4f} | {p['corr_ev_diff_choice']:.4f} |")
    lines.append("")

    # Breakdown
    lines.append("## EV Failure Breakdown by Feature\n")
    shared_vars = ["ambiguity", "corr", "ev_max_conflict", "has_safe_option_A",
                   "has_safe_option_B", "n_outcomes_B_group"]
    for var in shared_vars:
        sub = breakdown_df[breakdown_df["variable"] == var]
        if len(sub) == 0:
            continue
        lines.append(f"### {var}\n")
        lines.append("| Category | choices13k N | choices13k Rate | CPC18 N | CPC18 Rate |")
        lines.append("|----------|-------------|----------------|---------|-----------|")
        cats = sub["category"].unique()
        for cat in sorted(cats, key=str):
            c_row = sub[(sub["dataset"] == "choices13k") & (sub["category"] == cat)]
            p_row = sub[(sub["dataset"] == "cpc18") & (sub["category"] == cat)]
            cn = f"{int(c_row['n_problems'].values[0]):,}" if len(c_row) > 0 else "—"
            cr = f"{c_row['failure_rate'].values[0]:.1f}%" if len(c_row) > 0 else "—"
            pn = f"{int(p_row['n_problems'].values[0])}" if len(p_row) > 0 else "—"
            pr = f"{p_row['failure_rate'].values[0]:.1f}%" if len(p_row) > 0 else "—"
            lines.append(f"| {cat} | {cn} | {cr} | {pn} | {pr} |")
        lines.append("")

    # Dataset-specific breakdowns
    lines.append("### feedback (choices13k) / feedback_available (CPC18)\n")
    lines.append("| Category | Dataset | N | Rate |")
    lines.append("|----------|---------|---|------|")
    for var in ["feedback", "feedback_available"]:
        sub = breakdown_df[breakdown_df["variable"] == var]
        for _, row in sub.iterrows():
            lines.append(f"| {row['category']} | {row['dataset']} | {int(row['n_problems'])} | {row['failure_rate']:.1f}% |")
    lines.append("")

    sub = breakdown_df[breakdown_df["variable"] == "reconstruction_method"]
    if len(sub) > 0:
        lines.append("### reconstruction_method (CPC18 only)\n")
        lines.append("| Method | N | Rate |")
        lines.append("|--------|---|------|")
        for _, row in sub.iterrows():
            lines.append(f"| {row['category']} | {int(row['n_problems'])} | {row['failure_rate']:.1f}% |")
        lines.append("")

    # Direction comparison
    lines.append("## Effect Direction Comparison\n")
    lines.append("| Predictor | choices13k | CPC18 | Consistent? |")
    lines.append("|-----------|-----------|-------|-------------|")
    predictors = dir_df["predictor"].unique()
    for pred in predictors:
        c_dir = dir_df[(dir_df["predictor"] == pred) & (dir_df["dataset"] == "choices13k")]["direction"].values
        p_dir = dir_df[(dir_df["predictor"] == pred) & (dir_df["dataset"] == "cpc18")]["direction"].values
        cd = c_dir[0] if len(c_dir) > 0 else "?"
        pd_ = p_dir[0] if len(p_dir) > 0 else "?"
        consistent = "✓" if cd == pd_ and cd != "?" else ("—" if cd == "—" or pd_ == "—" else "✗")
        lines.append(f"| {pred} | {cd} | {pd_} | {consistent} |")
    lines.append("")

    # Logistic regression
    lines.append("## Logistic Regression Comparison\n")
    lines.append("*Exploratory. CPC18 has only 270 observations — estimates are less stable.*\n")
    merged = c13k_coefs.merge(cpc_coefs, on="feature")
    merged["same_sign"] = np.sign(merged["coef_choices13k"]) == np.sign(merged["coef_cpc18"])
    lines.append("| Feature | choices13k coef | CPC18 coef | Same sign? |")
    lines.append("|---------|----------------|------------|-----------|")
    for _, row in merged.iterrows():
        ss = "✓" if row["same_sign"] else "✗"
        lines.append(f"| {row['feature']} | {row['coef_choices13k']:.4f} | {row['coef_cpc18']:.4f} | {ss} |")
    lines.append("")
    lines.append(f"| Metric | choices13k | CPC18 |")
    lines.append(f"|--------|-----------|-------|")
    lines.append(f"| McFadden pseudo R² | {c13k_r2:.4f} | {cpc_r2:.4f} |")
    lines.append(f"| Classification accuracy | {c13k_acc:.4f} | {cpc_acc:.4f} |")
    lines.append("")

    # Top failures
    lines.append("## Top 20 EV Failures: choices13k\n")
    lines.append("| # | id | B-rate | ev_diff | n_out_B | ambiguity | ev_max_conflict |")
    lines.append("|---|---|--------|---------|---------|-----------|-----------------|")
    for i, (_, row) in enumerate(top_c13k.iterrows(), 1):
        lines.append(f"| {i} | {int(row['id'])} | {row['observed_B_rate']:.3f} | {row['ev_diff']:.2f} | {int(row['n_outcomes_B'])} | {row['ambiguity']} | {row['ev_max_conflict']} |")
    lines.append("")

    lines.append("## Top 20 EV Failures: CPC18\n")
    lines.append("| # | game_id | B-rate | ev_diff | n_out_B | ambiguity | ev_max_conflict | method |")
    lines.append("|---|---------|--------|---------|---------|-----------|-----------------|--------|")
    for i, (_, row) in enumerate(top_cpc.iterrows(), 1):
        lines.append(f"| {i} | {int(row['id'])} | {row['observed_B_rate']:.3f} | {row['ev_diff']:.2f} | {int(row['n_outcomes_B'])} | {row['ambiguity']} | {row['ev_max_conflict']} | {row['reconstruction_method']} |")
    lines.append("")

    # Figures
    lines.append("## Figures\n")
    lines.append("- `outputs/figures/cross_dataset_ev_failure_rates.png` — Bar chart of failure rates by key predictors")
    lines.append("- `outputs/figures/cross_dataset_ev_vs_choice.png` — Scatter plot of ev_diff vs observed B-rate")
    lines.append("")

    # Key observations
    lines.append("## Key Observations\n")
    # Auto-generate based on data
    c_rate = summary_df[summary_df["dataset"] == "choices13k"]["ev_failure_rate"].values[0]
    p_rate = summary_df[summary_df["dataset"] == "cpc18"]["ev_failure_rate"].values[0]
    lines.append(f"- CPC18 EV failure rate ({p_rate:.1f}%) vs choices13k ({c_rate:.1f}%).")
    n_same_sign = merged[merged["feature"] != "intercept"]["same_sign"].sum()
    n_total_feat = len(merged) - 1
    lines.append(f"- {n_same_sign}/{n_total_feat} logistic regression coefficients share the same sign across datasets.")
    lines.append("- Both datasets show negative correlation between ev_diff and observed B-rate.")
    lines.append("")

    # Limitations
    lines.append("## Limitations\n")
    lines.append("- choices13k has 14,568 condition-rows (13,006 unique Problem IDs); some problems appear twice under different conditions.")
    lines.append("- CPC18 has only 270 GameIDs — breakdowns have small cell sizes and regression estimates are less stable.")
    lines.append("- CPC18 empirical reconstruction is the experienced marginal distribution of Apay/Bpay, not necessarily the original generative parametric decomposition.")
    lines.append("- CPC18 mean_choice_B aggregates across all 25 trials (including early learning trials).")
    lines.append("- The two datasets differ in experimental design (online vs lab participants).")
    lines.append("- Logistic regression on 270 CPC18 observations has limited statistical power.")
    lines.append("")

    # Assumptions
    lines.append("## Assumptions\n")
    lines.append("1. EV failure definitions are identical across datasets.")
    lines.append("2. The common representation makes features directly comparable.")
    lines.append("3. Aggregate choice rates (bRate / mean_choice_B) are comparable measures of preference.")
    lines.append("")

    return "\n".join(lines)


def main():
    print("Loading datasets...")
    c13k, cpc = load_datasets()
    print(f"  choices13k: {len(c13k):,} rows")
    print(f"  CPC18: {len(cpc)} rows")

    print("Classifying EV consistency...")
    c13k = classify_ev(c13k)
    cpc = classify_ev(cpc)

    print("Computing dataset summaries...")
    s_c13k = dataset_summary(c13k, "choices13k")
    s_cpc = dataset_summary(cpc, "cpc18")
    summary_df = pd.DataFrame([s_c13k, s_cpc])
    print(f"  choices13k failure rate: {s_c13k['ev_failure_rate']:.1f}%")
    print(f"  CPC18 failure rate: {s_cpc['ev_failure_rate']:.1f}%")

    print("Computing breakdowns...")
    breakdown_df = compute_breakdowns(c13k, cpc)

    print("Computing direction comparison...")
    dir_df = direction_comparison(breakdown_df)

    print("Fitting logistic regressions...")
    c13k_coefs, c13k_r2, c13k_acc = fit_logistic(c13k, "choices13k")
    cpc_coefs, cpc_r2, cpc_acc = fit_logistic(cpc, "cpc18")
    print(f"  choices13k: R²={c13k_r2:.4f}, acc={c13k_acc:.4f}")
    print(f"  CPC18: R²={cpc_r2:.4f}, acc={cpc_acc:.4f}")

    print("Finding top failures...")
    top_c13k = top_failures(c13k, "choices13k")
    top_cpc = top_failures(cpc, "cpc18")

    print("Generating figures...")
    make_figures(c13k, cpc)
    print(f"  Saved: {FIG_DIR}/cross_dataset_ev_failure_rates.png")
    print(f"  Saved: {FIG_DIR}/cross_dataset_ev_vs_choice.png")

    print("Saving tables...")
    SUMMARY_CSV.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(SUMMARY_CSV, index=False)
    breakdown_df.to_csv(BREAKDOWN_CSV, index=False)
    print(f"  Saved: {SUMMARY_CSV}")
    print(f"  Saved: {BREAKDOWN_CSV}")

    print("Generating report...")
    report = generate_report(summary_df, breakdown_df, dir_df,
                             c13k_coefs, cpc_coefs, c13k_r2, cpc_r2, c13k_acc, cpc_acc,
                             top_c13k, top_cpc)
    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.write_text(report)
    print(f"  Saved: {REPORT_OUT}")

    print("Done.")


if __name__ == "__main__":
    main()
