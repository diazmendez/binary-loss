"""Spec 006: choices13k EV Failure Analysis.

Analyzes where expected value fails to predict majority human choice.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

ROOT = Path(__file__).resolve().parent.parent
COMMON = ROOT / "data/interim/choices13k_common.parquet"
FEATURES = ROOT / "data/interim/choices13k_features.parquet"
REPORT_OUT = ROOT / "outputs/reports/choices13k_ev_failure_analysis.md"
CSV_OUT = ROOT / "outputs/tables/choices13k_ev_failure_cases.csv"


def load_data():
    common = pd.read_parquet(COMMON)
    features = pd.read_parquet(FEATURES)
    # Same row order, join by index
    df = pd.concat([common, features.drop(columns=["problem_id"])], axis=1)
    return df


def classify_consistency(df):
    """Add ev_prediction, observed_majority, and consistency columns."""
    conditions = [df["ev_diff"] > 0, df["ev_diff"] < 0, df["ev_diff"] == 0]
    df["ev_prediction"] = np.select(conditions, ["A", "B", "tie"], default="tie")
    conditions_obs = [df["bRate"] < 0.5, df["bRate"] > 0.5, df["bRate"] == 0.5]
    df["observed_majority"] = np.select(conditions_obs, ["A", "B", "tie"], default="tie")
    # Exclude ties
    mask = (df["ev_prediction"] != "tie") & (df["observed_majority"] != "tie")
    df["ev_consistent"] = np.where(mask, df["ev_prediction"] == df["observed_majority"], np.nan)
    return df


def overall_consistency(df):
    mask = df["ev_consistent"].notna()
    subset = df[mask]
    n_consistent = int(subset["ev_consistent"].sum())
    n_inconsistent = int((~subset["ev_consistent"].astype(bool)).sum())
    n_ev_ties = int((df["ev_prediction"] == "tie").sum())
    n_obs_ties = int((df["observed_majority"] == "tie").sum())
    total = n_consistent + n_inconsistent
    return {
        "n_consistent": n_consistent,
        "pct_consistent": n_consistent / total * 100,
        "n_inconsistent": n_inconsistent,
        "pct_inconsistent": n_inconsistent / total * 100,
        "n_ev_ties": n_ev_ties,
        "n_obs_ties": n_obs_ties,
        "total_evaluated": total,
    }


def breakdown_by_variable(df, var):
    mask = df["ev_consistent"].notna()
    subset = df[mask]
    grouped = subset.groupby(var)["ev_consistent"].agg(["count", "sum"])
    grouped.columns = ["n", "n_consistent"]
    grouped["n_inconsistent"] = grouped["n"] - grouped["n_consistent"]
    grouped["inconsistency_rate"] = grouped["n_inconsistent"] / grouped["n"] * 100
    return grouped.reset_index()


def top_failures(df, n=30):
    inconsistent = df[df["ev_consistent"] == False].copy()  # noqa: E712
    # Failure strength
    inconsistent["failure_strength"] = np.where(
        inconsistent["ev_diff"] > 0,
        inconsistent["bRate"],  # EV predicts A but humans chose B
        1 - inconsistent["bRate"],  # EV predicts B but humans chose A
    )
    top = inconsistent.nlargest(n, "failure_strength")
    cols = ["problem_id", "ev_A", "ev_B", "ev_diff", "bRate", "n_outcomes_B",
            "feedback", "ambiguity", "corr", "options_A", "options_B", "failure_strength"]
    return top[cols].reset_index(drop=True)


def ev_max_crosstab(df):
    return df.groupby(["higher_ev_option", "higher_max_option"])["bRate"].mean().unstack(fill_value=np.nan)


def logistic_regression(df):
    mask = df["ev_consistent"].notna()
    subset = df[mask].copy()
    subset["min_value_diff"] = subset["min_value_A"] - subset["min_value_B"]
    subset["y"] = (subset["bRate"] > 0.5).astype(int)

    feature_cols = ["ev_diff", "max_value_diff", "min_value_diff", "n_outcomes_B",
                    "ambiguity", "feedback", "ev_max_conflict"]
    X = subset[feature_cols].copy()
    X["ambiguity"] = X["ambiguity"].astype(int)
    X["feedback"] = X["feedback"].astype(int)
    X["ev_max_conflict"] = X["ev_max_conflict"].astype(int)
    y = subset["y"]

    model = LogisticRegression(max_iter=1000, solver="lbfgs")
    model.fit(X, y)

    y_pred = model.predict(X)
    accuracy = accuracy_score(y, y_pred)

    # McFadden pseudo R²
    from sklearn.metrics import log_loss
    ll_model = -log_loss(y, model.predict_proba(X), normalize=False)
    ll_null = -log_loss(y, np.full((len(y), 2), [1 - y.mean(), y.mean()]), normalize=False)
    pseudo_r2 = 1 - (ll_model / ll_null)

    # Standard errors via Hessian approximation
    probs = model.predict_proba(X)[:, 1]
    W = probs * (1 - probs)
    X_with_intercept = np.column_stack([np.ones(len(X)), X.values])
    H = X_with_intercept.T @ np.diag(W) @ X_with_intercept
    try:
        cov = np.linalg.inv(H)
        se = np.sqrt(np.diag(cov))
        se_coefs = se[1:]  # skip intercept
        se_intercept = se[0]
    except np.linalg.LinAlgError:
        se_coefs = np.full(len(feature_cols), np.nan)
        se_intercept = np.nan

    coefs = pd.DataFrame({
        "feature": feature_cols,
        "coefficient": model.coef_[0],
        "std_error": se_coefs,
    })
    intercept_row = pd.DataFrame({
        "feature": ["intercept"],
        "coefficient": [model.intercept_[0]],
        "std_error": [se_intercept],
    })
    coefs = pd.concat([intercept_row, coefs], ignore_index=True)

    return coefs, pseudo_r2, accuracy


def generate_report(df):
    lines = []
    lines.append("# choices13k: EV Failure Analysis\n")
    lines.append(f"Generated: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M')} UTC\n")

    # 1. Overall consistency
    stats = overall_consistency(df)
    lines.append("## 1. Overall EV Consistency\n")
    lines.append(f"| Metric | Count | Percentage |")
    lines.append(f"|--------|-------|------------|")
    lines.append(f"| EV-consistent | {stats['n_consistent']} | {stats['pct_consistent']:.1f}% |")
    lines.append(f"| EV-inconsistent | {stats['n_inconsistent']} | {stats['pct_inconsistent']:.1f}% |")
    lines.append(f"| EV ties (excluded) | {stats['n_ev_ties']} | — |")
    lines.append(f"| Observed ties (excluded) | {stats['n_obs_ties']} | — |")
    lines.append(f"| Total evaluated | {stats['total_evaluated']} | 100% |")
    lines.append("")

    # 2. Breakdown
    lines.append("## 2. EV Failure Breakdown by Variable\n")
    breakdown_vars = [
        ("feedback", "Feedback"),
        ("ambiguity", "Ambiguity"),
        ("corr", "Correlation"),
        ("block", "Block"),
        ("ev_max_conflict", "EV/Max Conflict"),
        ("has_safe_option_A", "Safe Option A"),
        ("has_safe_option_B", "Safe Option B"),
    ]
    for var, label in breakdown_vars:
        bd = breakdown_by_variable(df, var)
        lines.append(f"### {label}\n")
        lines.append(f"| {label} | N | Inconsistent | Rate |")
        lines.append(f"|{'---'*1}|---|---|---|")
        for _, row in bd.iterrows():
            lines.append(f"| {row[var]} | {int(row['n'])} | {int(row['n_inconsistent'])} | {row['inconsistency_rate']:.1f}% |")
        lines.append("")

    # n_outcomes_B grouped
    df_eval = df[df["ev_consistent"].notna()].copy()
    df_eval["n_outcomes_B_group"] = pd.cut(df_eval["n_outcomes_B"], bins=[0, 2, 4, 6, 9], labels=["1-2", "3-4", "5-6", "7-9"])
    bd = df_eval.groupby("n_outcomes_B_group", observed=True)["ev_consistent"].agg(["count", "sum"]).reset_index()
    bd.columns = ["group", "n", "n_consistent"]
    bd["n_inconsistent"] = bd["n"] - bd["n_consistent"]
    bd["rate"] = bd["n_inconsistent"] / bd["n"] * 100
    lines.append("### N Outcomes B (grouped)\n")
    lines.append("| Group | N | Inconsistent | Rate |")
    lines.append("|---|---|---|---|")
    for _, row in bd.iterrows():
        lines.append(f"| {row['group']} | {int(row['n'])} | {int(row['n_inconsistent'])} | {row['rate']:.1f}% |")
    lines.append("")

    # 3. Top 30 failures
    lines.append("## 3. Top 30 Strongest EV Failures\n")
    top = top_failures(df)
    lines.append("| # | problem_id | ev_diff | bRate | failure_strength | n_outcomes_B | feedback | ambiguity | corr |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for i, row in top.iterrows():
        lines.append(f"| {i+1} | {row['problem_id']} | {row['ev_diff']:.2f} | {row['bRate']:.3f} | {row['failure_strength']:.3f} | {int(row['n_outcomes_B'])} | {row['feedback']} | {row['ambiguity']} | {int(row['corr'])} |")
    lines.append("")

    # 4. EV/Max cross-tab
    lines.append("## 4. Mean bRate by EV/Max Conflict Category\n")
    ct = ev_max_crosstab(df)
    lines.append(f"| higher_ev \\ higher_max | {' | '.join(str(c) for c in ct.columns)} |")
    lines.append(f"|---|{'---|' * len(ct.columns)}")
    for idx, row in ct.iterrows():
        vals = " | ".join(f"{v:.3f}" if not np.isnan(v) else "—" for v in row)
        lines.append(f"| {idx} | {vals} |")
    lines.append("")

    # 5. Logistic regression
    lines.append("## 5. Logistic Regression (Predicting Majority B)\n")
    lines.append("*Descriptive model, not causal.*\n")
    coefs, pseudo_r2, accuracy = logistic_regression(df)
    lines.append("| Feature | Coefficient | Std Error |")
    lines.append("|---|---|---|")
    for _, row in coefs.iterrows():
        lines.append(f"| {row['feature']} | {row['coefficient']:.4f} | {row['std_error']:.4f} |")
    lines.append("")
    lines.append(f"- **McFadden pseudo R²**: {pseudo_r2:.4f}")
    lines.append(f"- **Classification accuracy**: {accuracy:.4f}")
    lines.append(f"- Note: All features standardized by sklearn default (no manual scaling).")
    lines.append("")

    return "\n".join(lines)


def save_failure_csv(df):
    inconsistent = df[df["ev_consistent"] == False].copy()  # noqa: E712
    cols = ["problem_id", "ev_A", "ev_B", "ev_diff", "max_value_A", "max_value_B",
            "max_value_diff", "min_value_A", "min_value_B", "n_outcomes_B",
            "has_safe_option_A", "has_safe_option_B", "ev_max_conflict",
            "higher_ev_option", "higher_max_option",
            "feedback", "ambiguity", "corr", "block", "bRate", "bRate_std",
            "options_A", "options_B"]
    inconsistent[cols].to_csv(CSV_OUT, index=False)
    return len(inconsistent)


def main():
    print("Loading data...")
    df = load_data()
    print(f"  Loaded {len(df)} rows")

    print("Classifying EV consistency...")
    df = classify_consistency(df)

    stats = overall_consistency(df)
    print(f"  Consistent: {stats['n_consistent']} ({stats['pct_consistent']:.1f}%)")
    print(f"  Inconsistent: {stats['n_inconsistent']} ({stats['pct_inconsistent']:.1f}%)")

    print("Generating report...")
    report = generate_report(df)
    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.write_text(report)
    print(f"  Saved: {REPORT_OUT}")

    print("Saving failure cases CSV...")
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    n_saved = save_failure_csv(df)
    print(f"  Saved: {CSV_OUT} ({n_saved} rows)")

    print("Done.")


if __name__ == "__main__":
    main()
