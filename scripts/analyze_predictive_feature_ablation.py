"""Spec 016: Predictive Feature Ablation.

Evaluates whether advanced features improve EV failure prediction
through systematic ablation of feature groups.
"""

import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, balanced_accuracy_score,
                             f1_score, roc_auc_score)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent.parent
REPORT_OUT = ROOT / "outputs/reports/predictive_feature_ablation.md"
MODEL_CSV = ROOT / "outputs/tables/feature_ablation_model_comparison.csv"
GROUP_CSV = ROOT / "outputs/tables/feature_group_importance.csv"
TOP_CSV = ROOT / "outputs/tables/top_predictive_features.csv"
FIG_OUT = ROOT / "outputs/figures/feature_ablation_performance.png"

RANDOM_STATE = 42
NAN_THRESHOLD = 0.50  # Exclude features with >50% NaN

# Feature blocks
BLOCK_EV = ["ev_diff", "ev_abs_diff"]

BLOCK_BASIC = ["ev_diff", "max_value_diff", "min_value_diff", "n_outcomes_B",
               "ambiguity", "ev_max_conflict", "has_safe_option_A", "has_safe_option_B", "feedback"]

BLOCK_RISK = ["variance_A", "variance_B", "variance_diff", "std_A", "std_B", "std_diff",
              "range_A", "range_B", "range_diff", "ev_risk_conflict"]

BLOCK_LOSS = ["has_loss_A", "has_loss_B", "prob_loss_A", "prob_loss_B", "prob_loss_diff",
              "expected_loss_A", "expected_loss_B", "expected_loss_diff",
              "is_mixed_A", "is_mixed_B", "any_loss", "both_have_loss", "loss_asymmetry",
              "ev_favored_has_loss", "max_favored_has_loss"]

BLOCK_DOMINANCE = ["A_dominates_B", "B_dominates_A", "any_dominance"]

BLOCK_SALIENCE = ["prob_best_outcome_A", "prob_best_outcome_B",
                  "prob_worst_outcome_A", "prob_worst_outcome_B",
                  "has_rare_high_gain_A", "has_rare_high_gain_B",
                  "has_rare_loss_A", "has_rare_loss_B", "salience_conflict"]

BLOCK_SIMILARITY = ["ev_abs_diff", "range_overlap", "n_shared_values", "total_outcomes"]

BLOCK_SKEWNESS = ["skewness_A", "skewness_B", "skewness_diff",
                  "upside_distance_A", "upside_distance_B",
                  "downside_distance_A", "downside_distance_B",
                  "upside_ratio_A", "upside_ratio_B", "upside_ratio_diff"]

CONFIGS = [
    ("EV-only", BLOCK_EV),
    ("Basic", BLOCK_BASIC),
    ("Basic+Risk", BLOCK_BASIC + BLOCK_RISK),
    ("Basic+Loss", BLOCK_BASIC + BLOCK_LOSS),
    ("Basic+Dominance", BLOCK_BASIC + BLOCK_DOMINANCE),
    ("Basic+Salience", BLOCK_BASIC + BLOCK_SALIENCE),
    ("Basic+Similarity", BLOCK_BASIC + BLOCK_SIMILARITY),
    ("Basic+Skewness", BLOCK_BASIC + BLOCK_SKEWNESS),
    ("Full", BLOCK_BASIC + BLOCK_RISK + BLOCK_LOSS + BLOCK_DOMINANCE +
     BLOCK_SALIENCE + BLOCK_SIMILARITY + BLOCK_SKEWNESS),
]

# Feature group mapping for importance table
FEATURE_GROUPS = {}
for f in BLOCK_RISK:
    FEATURE_GROUPS[f] = "risk"
for f in BLOCK_LOSS:
    FEATURE_GROUPS[f] = "loss"
for f in BLOCK_DOMINANCE:
    FEATURE_GROUPS[f] = "dominance"
for f in BLOCK_SALIENCE:
    FEATURE_GROUPS[f] = "salience"
for f in BLOCK_SIMILARITY:
    FEATURE_GROUPS[f] = "similarity"
for f in BLOCK_SKEWNESS:
    FEATURE_GROUPS[f] = "skewness"
for f in BLOCK_BASIC:
    FEATURE_GROUPS[f] = "basic"
for f in BLOCK_EV:
    FEATURE_GROUPS[f] = "basic"


def load_dataset(dataset):
    """Load and merge common + basic features + advanced features."""
    if dataset == "choices13k":
        common = pd.read_parquet(ROOT / "data/interim/choices13k_common.parquet")
        feat = pd.read_parquet(ROOT / "data/interim/choices13k_features.parquet")
        adv = pd.read_parquet(ROOT / "data/interim/choices13k_advanced_features.parquet")
        df = pd.concat([common, feat.drop(columns=["problem_id"]),
                        adv.drop(columns=["problem_id"])], axis=1)
        df["min_value_diff"] = df["min_value_A"] - df["min_value_B"]
        df["feedback"] = df["feedback"].astype(int)
        b_rate_col = "bRate"
        id_col = "problem_id"
    else:
        common = pd.read_parquet(ROOT / "data/interim/cpc18_common.parquet")
        feat = pd.read_parquet(ROOT / "data/interim/cpc18_features.parquet")
        adv = pd.read_parquet(ROOT / "data/interim/cpc18_advanced_features.parquet")
        df = common.merge(feat, on="game_id").merge(adv, on="game_id")
        df["min_value_diff"] = df["min_value_A"] - df["min_value_B"]
        df["feedback"] = df["feedback_available"].astype(int)
        b_rate_col = "mean_choice_B"
        id_col = "game_id"

    # Exclude EV ties
    df = df[df["ev_diff"] != 0].copy()

    # Compute target: EV failure
    df["ev_failure"] = (((df["ev_diff"] > 0) & (df[b_rate_col] > 0.5)) |
                        ((df["ev_diff"] < 0) & (df[b_rate_col] < 0.5))).astype(int)

    # Convert booleans to int
    bool_cols = df.select_dtypes(include=[bool]).columns
    for col in bool_cols:
        df[col] = df[col].astype(int)

    return df, id_col


def prepare_features(df, feature_list, nan_threshold=NAN_THRESHOLD):
    """Prepare feature matrix, excluding high-NaN features and imputing rest."""
    # Deduplicate
    features = list(dict.fromkeys(feature_list))
    # Keep only available columns
    features = [f for f in features if f in df.columns]
    X = df[features].copy()

    # Exclude features with >threshold NaN
    nan_pct = X.isna().mean()
    dropped = nan_pct[nan_pct > nan_threshold].index.tolist()
    kept = [f for f in features if f not in dropped]
    X = X[kept]

    # Impute remaining NaN with 0 (neutral)
    X = X.fillna(0)
    return X, kept, dropped


def evaluate_model(X_train, y_train, X_test, y_test, model_type="logistic"):
    """Fit and evaluate a model."""
    scaler = StandardScaler()
    X_tr = scaler.fit_transform(X_train)
    X_te = scaler.transform(X_test)

    if model_type == "logistic":
        model = LogisticRegression(penalty="l2", max_iter=1000, random_state=RANDOM_STATE)
    else:
        model = GradientBoostingClassifier(n_estimators=100, max_depth=3, random_state=RANDOM_STATE)

    model.fit(X_tr, y_train)
    y_pred = model.predict(X_te)
    y_prob = model.predict_proba(X_te)[:, 1]

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "balanced_accuracy": balanced_accuracy_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_prob),
        "f1": f1_score(y_test, y_pred),
    }

    coefs = None
    if model_type == "logistic":
        coefs = pd.Series(model.coef_[0], index=X_train.columns)

    return metrics, coefs


def evaluate_cv(df, features, y, model_type="logistic", n_folds=5):
    """Stratified CV evaluation."""
    X, kept, dropped = prepare_features(df, features)
    y_arr = y.values

    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=RANDOM_STATE)
    metrics_list = []

    for train_idx, test_idx in skf.split(X, y_arr):
        X_tr, X_te = X.iloc[train_idx], X.iloc[test_idx]
        y_tr, y_te = y_arr[train_idx], y_arr[test_idx]
        m, _ = evaluate_model(X_tr, y_tr, X_te, y_te, model_type)
        metrics_list.append(m)

    mean_metrics = {k: np.mean([m[k] for m in metrics_list]) for k in metrics_list[0]}
    std_metrics = {k: np.std([m[k] for m in metrics_list]) for k in metrics_list[0]}
    return mean_metrics, std_metrics, kept, dropped


def evaluate_loocv(df, features, y, model_type="logistic"):
    """LOOCV for small datasets."""
    X, kept, dropped = prepare_features(df, features)
    y_arr = y.values

    scaler = StandardScaler()
    if model_type == "logistic":
        model = LogisticRegression(penalty="l2", max_iter=1000, random_state=RANDOM_STATE)
    else:
        model = GradientBoostingClassifier(n_estimators=100, max_depth=3, random_state=RANDOM_STATE)

    # Use cross_val_predict for efficiency
    skf = StratifiedKFold(n_splits=min(10, len(y_arr)), shuffle=True, random_state=RANDOM_STATE)
    y_pred = cross_val_predict(model, scaler.fit_transform(X), y_arr, cv=skf, method="predict")
    y_prob = cross_val_predict(model, scaler.fit_transform(X), y_arr, cv=skf, method="predict_proba")[:, 1]

    metrics = {
        "accuracy": accuracy_score(y_arr, y_pred),
        "balanced_accuracy": balanced_accuracy_score(y_arr, y_pred),
        "roc_auc": roc_auc_score(y_arr, y_prob),
        "f1": f1_score(y_arr, y_pred),
    }
    return metrics, kept, dropped


def run_ablation():
    """Run the full ablation study."""
    print("Loading datasets...")
    c13k, _ = load_dataset("choices13k")
    cpc, _ = load_dataset("cpc18")
    print(f"  choices13k: {len(c13k)} rows, {c13k['ev_failure'].mean()*100:.1f}% failure")
    print(f"  CPC18: {len(cpc)} rows, {cpc['ev_failure'].mean()*100:.1f}% failure")

    results = []
    c13k_coefs = {}
    cpc_coefs = {}

    # --- choices13k: 5-fold CV ---
    print("\nRunning choices13k ablation (5-fold CV)...")
    for config_name, feature_list in CONFIGS:
        # Logistic
        mean_m, std_m, kept, dropped = evaluate_cv(c13k, feature_list, c13k["ev_failure"], "logistic")
        results.append({
            "dataset": "choices13k", "config": config_name, "model": "logistic",
            "n_features": len(kept), "eval_method": "5fold_cv",
            **mean_m
        })
        # Get full-data coefficients for the Full model
        if config_name == "Full" or config_name == "Basic":
            X_full, kept_full, _ = prepare_features(c13k, feature_list)
            scaler = StandardScaler()
            X_sc = scaler.fit_transform(X_full)
            lr = LogisticRegression(penalty="l2", max_iter=1000, random_state=RANDOM_STATE)
            lr.fit(X_sc, c13k["ev_failure"])
            c13k_coefs[config_name] = pd.Series(lr.coef_[0], index=kept_full)

        # Gradient boosting (only for EV-only, Basic, Full)
        if config_name in ("EV-only", "Basic", "Full"):
            mean_m_gb, _, _, _ = evaluate_cv(c13k, feature_list, c13k["ev_failure"], "gradient_boosting")
            results.append({
                "dataset": "choices13k", "config": config_name, "model": "gradient_boosting",
                "n_features": len(kept), "eval_method": "5fold_cv",
                **mean_m_gb
            })

        print(f"  {config_name}: acc={mean_m['accuracy']:.4f}, AUC={mean_m['roc_auc']:.4f}")

    # --- CPC18: 10-fold CV ---
    print("\nRunning CPC18 ablation (10-fold CV)...")
    for config_name, feature_list in CONFIGS:
        metrics, kept, dropped = evaluate_loocv(cpc, feature_list, cpc["ev_failure"], "logistic")
        results.append({
            "dataset": "cpc18", "config": config_name, "model": "logistic",
            "n_features": len(kept), "eval_method": "10fold_cv",
            **metrics
        })
        if config_name == "Full":
            X_full, kept_full, _ = prepare_features(cpc, feature_list)
            scaler = StandardScaler()
            X_sc = scaler.fit_transform(X_full)
            lr = LogisticRegression(penalty="l2", max_iter=1000, random_state=RANDOM_STATE)
            lr.fit(X_sc, cpc["ev_failure"])
            cpc_coefs["Full"] = pd.Series(lr.coef_[0], index=kept_full)

        if config_name in ("EV-only", "Basic", "Full"):
            metrics_gb, _, _ = evaluate_loocv(cpc, feature_list, cpc["ev_failure"], "gradient_boosting")
            results.append({
                "dataset": "cpc18", "config": config_name, "model": "gradient_boosting",
                "n_features": len(kept), "eval_method": "10fold_cv",
                **metrics_gb
            })

        print(f"  {config_name}: acc={metrics['accuracy']:.4f}, AUC={metrics['roc_auc']:.4f}")

    # --- Cross-dataset transfer ---
    print("\nRunning cross-dataset transfer (train c13k → test CPC18)...")
    for config_name, feature_list in CONFIGS:
        # Get shared features
        X_train, kept_train, _ = prepare_features(c13k, feature_list)
        X_test, kept_test, _ = prepare_features(cpc, feature_list)
        shared = [f for f in kept_train if f in kept_test]
        if not shared:
            continue
        X_tr = X_train[shared]
        X_te = X_test[shared]
        m, _ = evaluate_model(X_tr, c13k["ev_failure"], X_te, cpc["ev_failure"], "logistic")
        results.append({
            "dataset": "cross_transfer", "config": config_name, "model": "logistic",
            "n_features": len(shared), "eval_method": "train_c13k_test_cpc18",
            **m
        })
        print(f"  {config_name}: acc={m['accuracy']:.4f}, AUC={m['roc_auc']:.4f}")

    results_df = pd.DataFrame(results)
    return results_df, c13k_coefs, cpc_coefs


def build_group_importance(results_df):
    """Compute marginal contribution of each feature group."""
    rows = []
    basic_results = results_df[
        (results_df["config"] == "Basic") & (results_df["model"] == "logistic")
    ]
    for dataset in ["choices13k", "cpc18"]:
        basic = basic_results[basic_results["dataset"] == dataset]
        if len(basic) == 0:
            continue
        basic_acc = basic.iloc[0]["accuracy"]
        basic_auc = basic.iloc[0]["roc_auc"]

        groups = [("risk", "Basic+Risk"), ("loss", "Basic+Loss"),
                  ("dominance", "Basic+Dominance"), ("salience", "Basic+Salience"),
                  ("similarity", "Basic+Similarity"), ("skewness", "Basic+Skewness")]
        for group_name, config_name in groups:
            row = results_df[(results_df["dataset"] == dataset) &
                             (results_df["config"] == config_name) &
                             (results_df["model"] == "logistic")]
            if len(row) == 0:
                continue
            rows.append({
                "dataset": dataset,
                "group": group_name,
                "accuracy_gain": row.iloc[0]["accuracy"] - basic_acc,
                "auc_gain": row.iloc[0]["roc_auc"] - basic_auc,
                "n_features_in_group": row.iloc[0]["n_features"] - basic.iloc[0]["n_features"],
            })
    return pd.DataFrame(rows)


def build_top_features(c13k_coefs, cpc_coefs):
    """Build top features table from Full model coefficients."""
    rows = []
    for dataset, coefs_dict in [("choices13k", c13k_coefs), ("cpc18", cpc_coefs)]:
        if "Full" not in coefs_dict:
            continue
        coefs = coefs_dict["Full"]
        ranked = coefs.abs().sort_values(ascending=False)
        for rank, (feat, abs_val) in enumerate(ranked.items(), 1):
            rows.append({
                "dataset": dataset,
                "feature": feat,
                "standardized_coef": coefs[feat],
                "abs_coef": abs_val,
                "rank": rank,
                "group": FEATURE_GROUPS.get(feat, "unknown"),
            })
    return pd.DataFrame(rows)


def make_figure(results_df):
    """Bar chart of ROC AUC by configuration and dataset."""
    FIG_OUT.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 5))

    logistic = results_df[results_df["model"] == "logistic"]
    config_order = [c[0] for c in CONFIGS]
    datasets = ["choices13k", "cpc18", "cross_transfer"]
    colors = {"choices13k": "#4C72B0", "cpc18": "#DD8452", "cross_transfer": "#55A868"}
    width = 0.25

    for i, ds in enumerate(datasets):
        sub = logistic[logistic["dataset"] == ds]
        aucs = []
        for cfg in config_order:
            row = sub[sub["config"] == cfg]
            aucs.append(row.iloc[0]["roc_auc"] if len(row) > 0 else 0)
        x = np.arange(len(config_order))
        ax.bar(x + i * width, aucs, width, label=ds, color=colors[ds])

    ax.set_xticks(np.arange(len(config_order)) + width)
    ax.set_xticklabels(config_order, rotation=30, ha="right")
    ax.set_ylabel("ROC AUC")
    ax.set_title("Feature Ablation: ROC AUC by Configuration")
    ax.legend()
    ax.set_ylim(0.5, 1.0)
    plt.tight_layout()
    plt.savefig(FIG_OUT, dpi=150)
    plt.close()


def generate_report(results_df, group_df, top_df, c13k_coefs):
    lines = []
    lines.append("# Predictive Feature Ablation\n")
    lines.append(f"Generated: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M')} UTC\n")

    lines.append("## Overview\n")
    lines.append("Systematic ablation evaluating whether advanced cognitive/risk features")
    lines.append("improve prediction of EV failure beyond EV-only and basic baselines.")
    lines.append("Target: binary EV failure (majority choice contradicts EV prediction).\n")

    lines.append("## Evaluation Protocol\n")
    lines.append("- choices13k: 5-fold stratified CV (N=14,075 after excluding EV ties)")
    lines.append("- CPC18: 10-fold stratified CV (N=256, **results unstable**)")
    lines.append("- Cross-transfer: train on choices13k, test on CPC18")
    lines.append("- NaN handling: features with >50% NaN excluded; remaining NaN imputed with 0")
    lines.append("- Models: L2-regularized logistic regression (primary), gradient boosting (ceiling)")
    lines.append("")

    # choices13k results
    lines.append("## Results: choices13k\n")
    c13k_log = results_df[(results_df["dataset"] == "choices13k") & (results_df["model"] == "logistic")]
    lines.append("| Config | N Features | Accuracy | Bal. Acc | ROC AUC | F1 |")
    lines.append("|--------|-----------|----------|---------|---------|-----|")
    for _, r in c13k_log.iterrows():
        lines.append(f"| {r['config']} | {int(r['n_features'])} | {r['accuracy']:.4f} | {r['balanced_accuracy']:.4f} | {r['roc_auc']:.4f} | {r['f1']:.4f} |")
    lines.append("")

    # GB comparison
    c13k_gb = results_df[(results_df["dataset"] == "choices13k") & (results_df["model"] == "gradient_boosting")]
    if len(c13k_gb) > 0:
        lines.append("### Gradient Boosting Ceiling\n")
        lines.append("| Config | Accuracy | ROC AUC |")
        lines.append("|--------|----------|---------|")
        for _, r in c13k_gb.iterrows():
            lines.append(f"| {r['config']} | {r['accuracy']:.4f} | {r['roc_auc']:.4f} |")
        lines.append("")

    # Top features
    c13k_top = top_df[top_df["dataset"] == "choices13k"].head(20)
    if len(c13k_top) > 0:
        lines.append("### Top 20 Features (Full Model, Standardized Coefficients)\n")
        lines.append("| Rank | Feature | Coef | Group |")
        lines.append("|------|---------|------|-------|")
        for _, r in c13k_top.iterrows():
            lines.append(f"| {int(r['rank'])} | {r['feature']} | {r['standardized_coef']:.4f} | {r['group']} |")
        lines.append("")

    # CPC18 results
    lines.append("## Results: CPC18 (⚠️ N=256, unstable)\n")
    cpc_log = results_df[(results_df["dataset"] == "cpc18") & (results_df["model"] == "logistic")]
    lines.append("| Config | N Features | Accuracy | Bal. Acc | ROC AUC | F1 |")
    lines.append("|--------|-----------|----------|---------|---------|-----|")
    for _, r in cpc_log.iterrows():
        lines.append(f"| {r['config']} | {int(r['n_features'])} | {r['accuracy']:.4f} | {r['balanced_accuracy']:.4f} | {r['roc_auc']:.4f} | {r['f1']:.4f} |")
    lines.append("")

    # Cross-transfer
    lines.append("## Results: Cross-Dataset Transfer\n")
    lines.append("*Train on choices13k → Test on CPC18*\n")
    xfer = results_df[results_df["dataset"] == "cross_transfer"]
    lines.append("| Config | N Features | Accuracy | Bal. Acc | ROC AUC | F1 |")
    lines.append("|--------|-----------|----------|---------|---------|-----|")
    for _, r in xfer.iterrows():
        lines.append(f"| {r['config']} | {int(r['n_features'])} | {r['accuracy']:.4f} | {r['balanced_accuracy']:.4f} | {r['roc_auc']:.4f} | {r['f1']:.4f} |")
    lines.append("")

    # Feature group importance
    lines.append("## Feature Group Importance\n")
    lines.append("Marginal gain over Basic configuration:\n")
    lines.append("| Dataset | Group | Accuracy Gain | AUC Gain | N Features |")
    lines.append("|---------|-------|--------------|----------|-----------|")
    for _, r in group_df.iterrows():
        lines.append(f"| {r['dataset']} | {r['group']} | {r['accuracy_gain']:+.4f} | {r['auc_gain']:+.4f} | {int(r['n_features_in_group'])} |")
    lines.append("")

    # Interpretation
    lines.append("## Interpretation\n")
    # Auto-generate key findings
    basic_auc = c13k_log[c13k_log["config"] == "Basic"]["roc_auc"].values[0]
    full_auc = c13k_log[c13k_log["config"] == "Full"]["roc_auc"].values[0]
    ev_auc = c13k_log[c13k_log["config"] == "EV-only"]["roc_auc"].values[0]
    lines.append(f"- EV-only AUC: {ev_auc:.4f} → Basic: {basic_auc:.4f} → Full: {full_auc:.4f}")
    lines.append(f"- Advanced features add {(full_auc - basic_auc)*100:.2f} AUC points over Basic in choices13k.")

    if "Full" in c13k_coefs:
        coefs = c13k_coefs["Full"]
        if "ev_favored_has_loss" in coefs.index:
            lines.append(f"- ev_favored_has_loss coefficient: {coefs['ev_favored_has_loss']:.4f} (confirms importance)")
        if "any_dominance" in coefs.index:
            lines.append(f"- any_dominance coefficient: {coefs['any_dominance']:.4f} (negative = protects against failure)")

    best_group = group_df[group_df["dataset"] == "choices13k"].sort_values("auc_gain", ascending=False)
    if len(best_group) > 0:
        lines.append(f"- Most valuable group (choices13k): {best_group.iloc[0]['group']} (+{best_group.iloc[0]['auc_gain']:.4f} AUC)")

    xfer_basic = xfer[xfer["config"] == "Basic"]["roc_auc"].values
    xfer_full = xfer[xfer["config"] == "Full"]["roc_auc"].values
    if len(xfer_basic) > 0 and len(xfer_full) > 0:
        lines.append(f"- Cross-transfer: Basic AUC={xfer_basic[0]:.4f}, Full AUC={xfer_full[0]:.4f}")
    lines.append("")

    # Limitations
    lines.append("## Limitations\n")
    lines.append("- CPC18 N=256 — all results unstable, wide confidence intervals.")
    lines.append("- NaN handling (impute with 0) affects skewness/cv features.")
    lines.append("- Cross-transfer assumes comparable problem spaces.")
    lines.append("- Logistic regression assumes linear feature effects.")
    lines.append("- No causal interpretation — correlational only.")
    lines.append("- Gradient boosting ceiling may overfit on small datasets.")
    lines.append("")

    lines.append("## Assumptions\n")
    lines.append("1. EV failure is a meaningful binary target.")
    lines.append("2. Standardized coefficients are comparable across features.")
    lines.append("3. L2 regularization prevents overfitting in logistic regression.")
    lines.append("4. Features with >50% NaN are uninformative and safely excluded.")
    lines.append("")

    return "\n".join(lines)


def main():
    results_df, c13k_coefs, cpc_coefs = run_ablation()

    print("\nBuilding output tables...")
    group_df = build_group_importance(results_df)
    top_df = build_top_features(c13k_coefs, cpc_coefs)

    print("Saving tables...")
    MODEL_CSV.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(MODEL_CSV, index=False)
    group_df.to_csv(GROUP_CSV, index=False)
    top_df.to_csv(TOP_CSV, index=False)

    print("Generating figure...")
    make_figure(results_df)

    print("Generating report...")
    report = generate_report(results_df, group_df, top_df, c13k_coefs)
    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.write_text(report)
    print(f"  {REPORT_OUT}")

    print("Done.")


if __name__ == "__main__":
    main()
