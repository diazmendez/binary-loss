"""
Spec 024A: Revision Inference and Controls
Runs inferential analyses addressing internal review concerns for Decision manuscript.
"""

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from pathlib import Path

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

OUT_TABLES = Path("outputs/tables")
OUT_TABLES.mkdir(parents=True, exist_ok=True)


# ─── Data Loading ───────────────────────────────────────────────────────────

def load_data():
    """Load and merge all needed datasets."""
    c13k_common = pd.read_parquet("data/interim/choices13k_common.parquet")
    c13k_feat = pd.read_parquet("data/interim/choices13k_features.parquet")
    c13k_adv = pd.read_parquet("data/interim/choices13k_advanced_features.parquet")
    c13k = c13k_common.merge(c13k_feat, on="problem_id").merge(c13k_adv, on="problem_id")
    # EV failure: EV predicts higher_ev_option but majority chose otherwise
    c13k["ev_failure"] = ((c13k["ev_diff"] > 0) & (c13k["bRate"] > 0.5)) | \
                         ((c13k["ev_diff"] < 0) & (c13k["bRate"] < 0.5))
    c13k = c13k[c13k["ev_diff"] != 0].copy()

    cpc_common = pd.read_parquet("data/interim/cpc18_common.parquet")
    cpc_feat = pd.read_parquet("data/interim/cpc18_features.parquet")
    cpc_adv = pd.read_parquet("data/interim/cpc18_advanced_features.parquet")
    cpc = cpc_common.merge(cpc_feat, on="game_id").merge(cpc_adv, on="game_id")
    cpc["ev_failure"] = ((cpc["ev_diff"] > 0) & (cpc["mean_choice_B"] > 0.5)) | \
                        ((cpc["ev_diff"] < 0) & (cpc["mean_choice_B"] < 0.5))
    cpc = cpc[cpc["ev_diff"] != 0].copy()

    # Compute prob_loss_ev_favored and expected_loss_ev_favored
    for df in [c13k, cpc]:
        ev_favors_A = df["ev_diff"] < 0  # ev_diff = ev_B - ev_A, so negative means A is better
        df["prob_loss_ev_favored"] = np.where(ev_favors_A, df["prob_loss_A"], df["prob_loss_B"])
        df["expected_loss_ev_favored"] = np.where(ev_favors_A, df["expected_loss_A"], df["expected_loss_B"])

    return c13k, cpc


# ─── Analysis 1: Confidence Intervals for EV Failure Rates ──────────────────

def wilson_ci(k, n, alpha=0.05):
    """Wilson score interval for binomial proportion."""
    z = stats.norm.ppf(1 - alpha / 2)
    p_hat = k / n
    denom = 1 + z**2 / n
    center = (p_hat + z**2 / (2 * n)) / denom
    margin = z * np.sqrt(p_hat * (1 - p_hat) / n + z**2 / (4 * n**2)) / denom
    return center - margin, center + margin


def analysis_1(c13k, cpc):
    """CIs for key EV failure rates."""
    rows = []

    # choices13k problem-level
    n_c13k = len(c13k)
    k_c13k = c13k["ev_failure"].sum()
    rate_c13k = k_c13k / n_c13k
    lo, hi = wilson_ci(k_c13k, n_c13k)
    rows.append(("EV failure rate", "choices13k", "problem-level", rate_c13k, lo, hi, n_c13k, "Wilson"))

    # CPC18 problem-level
    n_cpc = len(cpc)
    k_cpc = cpc["ev_failure"].sum()
    rate_cpc = k_cpc / n_cpc
    lo, hi = wilson_ci(k_cpc, n_cpc)
    rows.append(("EV failure rate", "CPC18", "problem-level", rate_cpc, lo, hi, n_cpc, "Wilson"))

    # CPC18 trial-level from block-level data
    block_df = pd.read_csv("outputs/tables/cpc18_block_level_choice.csv")
    for block_num in [1, 5]:
        bdata = block_df[block_df["block"] == block_num]
        # ev_consistency is proportion choosing EV-optimal; failure = 1 - ev_consistency
        mean_fail = 1 - bdata["ev_consistency"].mean()
        # Use n_participants * n_games as effective N for binomial CI (note: clustered)
        n_eff = int(bdata["n_participants"].sum())  # total participant-game observations
        k_eff = int(round(mean_fail * n_eff))
        lo, hi = wilson_ci(k_eff, n_eff)
        rows.append((f"Trial-level EV failure block {block_num}", "CPC18", "trial-level",
                     mean_fail, lo, hi, n_eff, "Wilson (clustered, conservative)"))

    return pd.DataFrame(rows, columns=["metric", "dataset", "level", "value",
                                        "ci_lower", "ci_upper", "n", "method"])


# ─── Analysis 2: Loss Exposure Effect with Controls ─────────────────────────

def analysis_2(c13k, cpc):
    """Loss exposure unadjusted and controlled effects."""
    rows = []

    for name, df in [("choices13k", c13k), ("CPC18", cpc)]:
        y = df["ev_failure"].astype(int).values
        loss = df["ev_favored_has_loss"].astype(int).values

        # 2a: Unadjusted
        a = y[loss == 1].sum()  # failures with loss
        b = (loss == 1).sum() - a  # non-failures with loss
        c = y[loss == 0].sum()  # failures without loss
        d = (loss == 0).sum() - c  # non-failures without loss
        table = np.array([[a, b], [c, d]])
        odds_ratio_val = (a * d) / (b * c) if (b * c) > 0 else np.inf
        log_or_se = np.sqrt(1/a + 1/b + 1/c + 1/d) if min(a, b, c, d) > 0 else np.nan
        or_lo = np.exp(np.log(odds_ratio_val) - 1.96 * log_or_se)
        or_hi = np.exp(np.log(odds_ratio_val) + 1.96 * log_or_se)
        chi2, p_chi, _, _ = stats.chi2_contingency(table, correction=False)
        risk_diff = y[loss == 1].mean() - y[loss == 0].mean()

        rows.append((name, "ev_favored_has_loss", np.log(odds_ratio_val), log_or_se,
                     np.log(or_lo), np.log(or_hi), p_chi, "unadjusted"))

        # 2b: Controlled logistic regression
        predictors = ["ev_abs_diff", "ev_favored_has_loss", "prob_loss_ev_favored",
                      "expected_loss_ev_favored", "ambiguity", "any_dominance"]
        X = df[predictors].copy()
        for col in X.columns:
            X[col] = pd.to_numeric(X[col], errors="coerce")
        X = X.fillna(0)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = LogisticRegression(penalty="l2", C=1.0, max_iter=1000,
                                   random_state=RANDOM_STATE, solver="lbfgs")
        model.fit(X_scaled, y)
        coefs = model.coef_[0]

        # Bootstrap CIs for coefficients
        n_boot = 1000
        boot_coefs = np.zeros((n_boot, len(predictors)))
        rng = np.random.RandomState(RANDOM_STATE)
        for i in range(n_boot):
            idx = rng.choice(len(y), len(y), replace=True)
            try:
                m = LogisticRegression(penalty="l2", C=1.0, max_iter=1000,
                                       random_state=RANDOM_STATE, solver="lbfgs")
                m.fit(X_scaled[idx], y[idx])
                boot_coefs[i] = m.coef_[0]
            except Exception:
                boot_coefs[i] = np.nan

        for j, pred in enumerate(predictors):
            se = np.nanstd(boot_coefs[:, j])
            lo = np.nanpercentile(boot_coefs[:, j], 2.5)
            hi = np.nanpercentile(boot_coefs[:, j], 97.5)
            # p-value from z-test
            z = coefs[j] / se if se > 0 else 0
            p = 2 * (1 - stats.norm.cdf(abs(z)))
            rows.append((name, pred, coefs[j], se, lo, hi, p, "controlled"))

    return pd.DataFrame(rows, columns=["dataset", "predictor", "coefficient", "std_error",
                                        "ci_lower", "ci_upper", "p_value", "model"])


# ─── Analysis 3: Binary vs Continuous Loss Comparison ───────────────────────

def analysis_3(c13k):
    """Compare binary loss presence vs probability/magnitude using AUC."""
    y = c13k["ev_failure"].astype(int).values
    rows = []

    models_spec = {
        "Binary only": ["ev_abs_diff", "ev_favored_has_loss"],
        "Probability only": ["ev_abs_diff", "prob_loss_ev_favored"],
        "Magnitude only": ["ev_abs_diff", "expected_loss_ev_favored"],
        "Full loss": ["ev_abs_diff", "ev_favored_has_loss", "prob_loss_ev_favored", "expected_loss_ev_favored"],
    }

    for model_name, preds in models_spec.items():
        X = c13k[preds].fillna(0).values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
        aucs = []
        for train_idx, test_idx in cv.split(X_scaled, y):
            m = LogisticRegression(penalty="l2", C=1.0, max_iter=1000,
                                   random_state=RANDOM_STATE, solver="lbfgs")
            m.fit(X_scaled[train_idx], y[train_idx])
            proba = m.predict_proba(X_scaled[test_idx])[:, 1]
            aucs.append(roc_auc_score(y[test_idx], proba))
        rows.append((model_name, ", ".join(preds), np.mean(aucs), np.std(aucs)))

    return pd.DataFrame(rows, columns=["model", "predictors", "mean_auc", "std_auc"])


# ─── Analysis 4: Dominance Control ──────────────────────────────────────────

def analysis_4(c13k, cpc):
    """Dominance control: descriptive + controlled regression."""
    dom_rows = []

    for name, df in [("choices13k", c13k), ("CPC18", cpc)]:
        y = df["ev_failure"].astype(int).values
        dom = df["any_dominance"].astype(bool)

        # 4a: Descriptive
        mean_ev_dom = df.loc[dom, "ev_abs_diff"].mean()
        mean_ev_nodom = df.loc[~dom, "ev_abs_diff"].mean()
        med_ev_dom = df.loc[dom, "ev_abs_diff"].median()
        med_ev_nodom = df.loc[~dom, "ev_abs_diff"].median()

        dom_rows.append((name, "ev_abs_diff_mean_dominance", mean_ev_dom, np.nan,
                         np.nan, np.nan, np.nan))
        dom_rows.append((name, "ev_abs_diff_mean_no_dominance", mean_ev_nodom, np.nan,
                         np.nan, np.nan, np.nan))
        dom_rows.append((name, "ev_abs_diff_median_dominance", med_ev_dom, np.nan,
                         np.nan, np.nan, np.nan))
        dom_rows.append((name, "ev_abs_diff_median_no_dominance", med_ev_nodom, np.nan,
                         np.nan, np.nan, np.nan))

        # 4b: Controlled regression
        predictors = ["ev_abs_diff", "any_dominance", "ev_favored_has_loss", "ambiguity"]
        X = df[predictors].copy()
        for col in X.columns:
            X[col] = pd.to_numeric(X[col], errors="coerce")
        X = X.fillna(0).values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = LogisticRegression(penalty="l2", C=1.0, max_iter=1000,
                                   random_state=RANDOM_STATE, solver="lbfgs")
        model.fit(X_scaled, y)
        coefs = model.coef_[0]

        # Bootstrap
        n_boot = 1000
        boot_coefs = np.zeros((n_boot, len(predictors)))
        rng = np.random.RandomState(RANDOM_STATE + 1)
        for i in range(n_boot):
            idx = rng.choice(len(y), len(y), replace=True)
            try:
                m = LogisticRegression(penalty="l2", C=1.0, max_iter=1000,
                                       random_state=RANDOM_STATE, solver="lbfgs")
                m.fit(X_scaled[idx], y[idx])
                boot_coefs[i] = m.coef_[0]
            except Exception:
                boot_coefs[i] = np.nan

        for j, pred in enumerate(predictors):
            se = np.nanstd(boot_coefs[:, j])
            lo = np.nanpercentile(boot_coefs[:, j], 2.5)
            hi = np.nanpercentile(boot_coefs[:, j], 97.5)
            dom_rows.append((name, pred, coefs[j], se, lo, hi,
                             2 * (1 - stats.norm.cdf(abs(coefs[j] / se))) if se > 0 else np.nan))

    return pd.DataFrame(dom_rows, columns=["dataset", "predictor", "coefficient", "std_error",
                                            "ci_lower", "ci_upper", "p_value"])


# ─── Analysis 5: AUC Confidence Intervals ──────────────────────────────────

def get_full_features(df):
    """Get the full feature set used in spec 016."""
    exclude = ["problem_id", "game_id", "dataset", "bRate", "bRate_std", "mean_choice_B",
               "ev_failure", "feedback", "block", "ambiguity_x", "corr", "n", "options_A",
               "options_B", "set", "reconstruction_method", "reconstruction_notes",
               "n_participants", "n_trials_per_participant", "n_total_rows",
               "feedback_available", "higher_ev_option", "higher_max_option",
               "dominant_option", "ev_matches_dominance", "best_outcome_option",
               "worst_outcome_option", "rare_high_gain_option", "rare_loss_option",
               "riskier_option", "prob_loss_ev_favored", "expected_loss_ev_favored"]
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    feature_cols = [c for c in numeric_cols if c not in exclude]
    return feature_cols


def analysis_5(c13k, cpc):
    """Bootstrap AUC CIs for full model."""
    rows = []

    # Get feature columns
    feat_cols = get_full_features(c13k)
    X_c13k = c13k[feat_cols].fillna(0).values
    y_c13k = c13k["ev_failure"].astype(int).values
    scaler_c13k = StandardScaler()
    X_c13k_scaled = scaler_c13k.fit_transform(X_c13k)

    # choices13k 5-fold CV AUC with bootstrap
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    all_proba = np.zeros(len(y_c13k))
    for train_idx, test_idx in cv.split(X_c13k_scaled, y_c13k):
        m = LogisticRegression(penalty="l2", C=1.0, max_iter=1000,
                               random_state=RANDOM_STATE, solver="lbfgs")
        m.fit(X_c13k_scaled[train_idx], y_c13k[train_idx])
        all_proba[test_idx] = m.predict_proba(X_c13k_scaled[test_idx])[:, 1]

    auc_c13k = roc_auc_score(y_c13k, all_proba)
    # Bootstrap CI on predictions
    rng = np.random.RandomState(RANDOM_STATE)
    boot_aucs = []
    for _ in range(1000):
        idx = rng.choice(len(y_c13k), len(y_c13k), replace=True)
        if len(np.unique(y_c13k[idx])) < 2:
            continue
        boot_aucs.append(roc_auc_score(y_c13k[idx], all_proba[idx]))
    rows.append(("Full logistic AUC", "choices13k", "5-fold CV", auc_c13k,
                 np.percentile(boot_aucs, 2.5), np.percentile(boot_aucs, 97.5),
                 len(y_c13k), "bootstrap predictions"))

    # Cross-transfer: train all c13k, test CPC18
    cpc_feat_cols = [c for c in feat_cols if c in cpc.columns]
    X_cpc = cpc[cpc_feat_cols].fillna(0).values
    y_cpc = cpc["ev_failure"].astype(int).values

    # Align features: use only shared columns
    shared_cols = [c for c in feat_cols if c in cpc.columns]
    X_c13k_shared = c13k[shared_cols].fillna(0).values
    X_cpc_shared = cpc[shared_cols].fillna(0).values

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_c13k_shared)
    X_test = scaler.transform(X_cpc_shared)

    model = LogisticRegression(penalty="l2", C=1.0, max_iter=1000,
                               random_state=RANDOM_STATE, solver="lbfgs")
    model.fit(X_train, y_c13k)
    proba_cpc = model.predict_proba(X_test)[:, 1]
    auc_transfer = roc_auc_score(y_cpc, proba_cpc)

    # Bootstrap CPC18 test set
    boot_aucs_t = []
    for _ in range(1000):
        idx = rng.choice(len(y_cpc), len(y_cpc), replace=True)
        if len(np.unique(y_cpc[idx])) < 2:
            continue
        boot_aucs_t.append(roc_auc_score(y_cpc[idx], proba_cpc[idx]))
    rows.append(("Cross-transfer AUC", "choices13k→CPC18", "train c13k, test CPC18",
                 auc_transfer, np.percentile(boot_aucs_t, 2.5),
                 np.percentile(boot_aucs_t, 97.5), len(y_cpc), "bootstrap test set"))

    # CPC18 within-dataset (10-fold)
    X_cpc_full = cpc[shared_cols].fillna(0).values
    scaler2 = StandardScaler()
    X_cpc_scaled = scaler2.fit_transform(X_cpc_full)
    cv2 = StratifiedKFold(n_splits=10, shuffle=True, random_state=RANDOM_STATE)
    cpc_proba = np.zeros(len(y_cpc))
    for train_idx, test_idx in cv2.split(X_cpc_scaled, y_cpc):
        m = LogisticRegression(penalty="l2", C=1.0, max_iter=1000,
                               random_state=RANDOM_STATE, solver="lbfgs")
        m.fit(X_cpc_scaled[train_idx], y_cpc[train_idx])
        cpc_proba[test_idx] = m.predict_proba(X_cpc_scaled[test_idx])[:, 1]
    auc_cpc = roc_auc_score(y_cpc, cpc_proba)
    boot_aucs_cpc = []
    for _ in range(1000):
        idx = rng.choice(len(y_cpc), len(y_cpc), replace=True)
        if len(np.unique(y_cpc[idx])) < 2:
            continue
        boot_aucs_cpc.append(roc_auc_score(y_cpc[idx], cpc_proba[idx]))
    rows.append(("Full logistic AUC", "CPC18", "10-fold CV", auc_cpc,
                 np.percentile(boot_aucs_cpc, 2.5), np.percentile(boot_aucs_cpc, 97.5),
                 len(y_cpc), "bootstrap predictions"))

    return pd.DataFrame(rows, columns=["metric", "dataset", "evaluation", "value",
                                        "ci_lower", "ci_upper", "n", "method"])


# ─── Analysis 6: Graph Permutation Test ─────────────────────────────────────

def analysis_6():
    """Permutation test for EV-failure edge enrichment in similarity graph."""
    nodes = pd.read_csv("outputs/graph/nodes_problems.csv")
    edges = pd.read_csv("outputs/graph/edges_similar_problem.csv")

    # Build lookup: node_id -> ev_failure
    failure_map = dict(zip(nodes["node_id"], nodes["ev_failure"].astype(bool)))

    # Compute observed statistic: fraction of edges where both endpoints are EV-failure
    src_fail = edges["source_id"].map(failure_map).values.astype(bool)
    tgt_fail = edges["target_id"].map(failure_map).values.astype(bool)
    both_fail = src_fail & tgt_fail
    observed = both_fail.mean()

    # Get unique node IDs that appear in edges
    all_node_ids = nodes["node_id"].values
    labels = nodes["ev_failure"].astype(bool).values
    n_failures = labels.sum()

    # For permutation: shuffle labels, recompute
    # Build index mapping for fast lookup
    node_to_idx = {nid: i for i, nid in enumerate(all_node_ids)}
    src_idx = np.array([node_to_idx[s] for s in edges["source_id"].values])
    tgt_idx = np.array([node_to_idx[t] for t in edges["target_id"].values])

    n_perm = 1000
    rng = np.random.RandomState(RANDOM_STATE)
    null_stats = np.zeros(n_perm)

    for i in range(n_perm):
        perm_labels = rng.permutation(labels)
        both = perm_labels[src_idx] & perm_labels[tgt_idx]
        null_stats[i] = both.mean()

    p_value = (null_stats >= observed).mean()

    result = pd.DataFrame([{
        "statistic": "both_endpoints_ev_failure_fraction",
        "observed": observed,
        "null_mean": null_stats.mean(),
        "null_std": null_stats.std(),
        "null_p025": np.percentile(null_stats, 2.5),
        "null_p975": np.percentile(null_stats, 97.5),
        "p_value": p_value,
        "n_permutations": n_perm,
    }])
    return result


# ─── Main ───────────────────────────────────────────────────────────────────

def main():
    print("Loading data...")
    c13k, cpc = load_data()

    print("Analysis 1: EV failure rate CIs...")
    ci_df = analysis_1(c13k, cpc)
    print(ci_df.to_string(index=False))
    print()

    print("Analysis 2: Loss exposure controls...")
    loss_df = analysis_2(c13k, cpc)
    print(loss_df.to_string(index=False))
    print()

    print("Analysis 3: Binary vs continuous loss comparison...")
    compare_df = analysis_3(c13k)
    print(compare_df.to_string(index=False))
    print()

    print("Analysis 4: Dominance control...")
    dom_df = analysis_4(c13k, cpc)
    print(dom_df.to_string(index=False))
    print()

    print("Analysis 5: AUC confidence intervals...")
    auc_df = analysis_5(c13k, cpc)
    print(auc_df.to_string(index=False))
    print()

    print("Analysis 6: Graph permutation test...")
    perm_df = analysis_6()
    print(perm_df.to_string(index=False))
    print()

    # Save outputs
    # Combine CI results (analysis 1 + 5)
    key_stats = pd.concat([
        ci_df.rename(columns={"level": "evaluation"}),
        auc_df
    ], ignore_index=True)
    key_stats.to_csv(OUT_TABLES / "revision_inference_key_stats.csv", index=False)

    loss_df.to_csv(OUT_TABLES / "revision_loss_exposure_controls.csv", index=False)
    # Append analysis 3 comparison to loss file as separate section
    compare_df.to_csv(OUT_TABLES / "revision_loss_binary_vs_continuous.csv", index=False)

    dom_df.to_csv(OUT_TABLES / "revision_dominance_control_models.csv", index=False)
    perm_df.to_csv(OUT_TABLES / "revision_graph_permutation_results.csv", index=False)

    print("\nAll outputs saved to outputs/tables/revision_*.csv")


if __name__ == "__main__":
    main()
