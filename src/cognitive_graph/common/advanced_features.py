"""Advanced feature extraction for choice problems.

Goes beyond EV/max/min to include risk, loss, skewness, dominance,
salience, and similarity features.
"""

import json
import math

import numpy as np

RARE_THRESHOLD = 0.10


def compute_advanced_features(row: dict) -> dict:
    """Compute advanced features from a common-format problem row.

    Expects row to have 'options_A' and 'options_B' as JSON strings
    of [[prob, value], ...] lists.

    Returns dict of feature_name -> value. Never raises exceptions.
    """
    try:
        options_a = json.loads(row["options_A"]) if isinstance(row["options_A"], str) else row["options_A"]
        options_b = json.loads(row["options_B"]) if isinstance(row["options_B"], str) else row["options_B"]
    except (json.JSONDecodeError, TypeError):
        return {}

    probs_a = [o[0] for o in options_a]
    vals_a = [o[1] for o in options_a]
    probs_b = [o[0] for o in options_b]
    vals_b = [o[1] for o in options_b]

    ev_a = sum(p * v for p, v in zip(probs_a, vals_a))
    ev_b = sum(p * v for p, v in zip(probs_b, vals_b))

    feats = {}

    # Group 1: Risk/Dispersion
    feats.update(_option_risk_features(probs_a, vals_a, ev_a, "A"))
    feats.update(_option_risk_features(probs_b, vals_b, ev_b, "B"))
    feats["variance_diff"] = feats["variance_A"] - feats["variance_B"]
    feats["std_diff"] = feats["std_A"] - feats["std_B"]
    feats["range_diff"] = feats["range_A"] - feats["range_B"]
    if feats["variance_A"] > feats["variance_B"]:
        feats["riskier_option"] = "A"
    elif feats["variance_B"] > feats["variance_A"]:
        feats["riskier_option"] = "B"
    else:
        feats["riskier_option"] = "equal"
    higher_ev = "A" if ev_a > ev_b else ("B" if ev_b > ev_a else "equal")
    feats["ev_risk_conflict"] = (higher_ev != feats["riskier_option"] and
                                  higher_ev != "equal" and feats["riskier_option"] != "equal")

    # Group 2: Loss
    feats.update(_option_loss_features(probs_a, vals_a, "A"))
    feats.update(_option_loss_features(probs_b, vals_b, "B"))
    feats["any_loss"] = feats["has_loss_A"] or feats["has_loss_B"]
    feats["both_have_loss"] = feats["has_loss_A"] and feats["has_loss_B"]
    feats["loss_asymmetry"] = feats["has_loss_A"] != feats["has_loss_B"]
    higher_max = "A" if max(vals_a) > max(vals_b) else ("B" if max(vals_b) > max(vals_a) else "equal")
    feats["ev_favored_has_loss"] = (higher_ev == "A" and feats["has_loss_A"]) or (higher_ev == "B" and feats["has_loss_B"])
    feats["max_favored_has_loss"] = (higher_max == "A" and feats["has_loss_A"]) or (higher_max == "B" and feats["has_loss_B"])
    feats["prob_loss_diff"] = feats["prob_loss_A"] - feats["prob_loss_B"]
    feats["expected_loss_diff"] = feats["expected_loss_A"] - feats["expected_loss_B"]

    # Group 3: Skewness
    feats.update(_option_skewness_features(probs_a, vals_a, ev_a, feats["std_A"], "A"))
    feats.update(_option_skewness_features(probs_b, vals_b, ev_b, feats["std_B"], "B"))
    feats["skewness_diff"] = _safe_sub(feats["skewness_A"], feats["skewness_B"])
    feats["upside_ratio_diff"] = feats["upside_ratio_A"] - feats["upside_ratio_B"]

    # Group 4: Dominance
    feats.update(_dominance_check(probs_a, vals_a, probs_b, vals_b, higher_ev))

    # Group 5: Salience
    feats.update(_option_salience_features(probs_a, vals_a, "A"))
    feats.update(_option_salience_features(probs_b, vals_b, "B"))
    max_a, max_b = max(vals_a), max(vals_b)
    feats["max_ratio"] = max_b / max_a if max_a > 0 else float("nan")
    feats["best_outcome_option"] = "A" if max_a > max_b else ("B" if max_b > max_a else "equal")
    min_a, min_b = min(vals_a), min(vals_b)
    feats["worst_outcome_option"] = "A" if min_a < min_b else ("B" if min_b < min_a else "equal")
    # Rare high gain option
    rh_a = feats["has_rare_high_gain_A"]
    rh_b = feats["has_rare_high_gain_B"]
    if rh_a and rh_b:
        feats["rare_high_gain_option"] = "both"
    elif rh_a:
        feats["rare_high_gain_option"] = "A"
    elif rh_b:
        feats["rare_high_gain_option"] = "B"
    else:
        feats["rare_high_gain_option"] = "neither"
    # Rare loss option
    rl_a = feats["has_rare_loss_A"]
    rl_b = feats["has_rare_loss_B"]
    if rl_a and rl_b:
        feats["rare_loss_option"] = "both"
    elif rl_a:
        feats["rare_loss_option"] = "A"
    elif rl_b:
        feats["rare_loss_option"] = "B"
    else:
        feats["rare_loss_option"] = "neither"
    feats["salience_conflict"] = feats["best_outcome_option"] != feats["worst_outcome_option"]

    # Group 6: Similarity
    feats.update(_similarity_features(probs_a, vals_a, probs_b, vals_b, ev_a, ev_b))

    return feats


def _option_risk_features(probs, values, ev, label):
    variance = sum(p * (v - ev) ** 2 for p, v in zip(probs, values))
    std = math.sqrt(variance)
    cv = std / abs(ev) if abs(ev) > 1e-10 else float("nan")
    rng = max(values) - min(values)
    return {
        f"variance_{label}": variance,
        f"std_{label}": std,
        f"cv_{label}": cv,
        f"range_{label}": rng,
    }


def _option_loss_features(probs, values, label):
    losses = [(p, v) for p, v in zip(probs, values) if v < 0]
    has_loss = len(losses) > 0
    prob_loss = sum(p for p, _ in losses)
    expected_loss = sum(p * v for p, v in losses)
    min_neg = min((v for _, v in losses), default=0.0)
    has_pos = any(v > 0 for v in values)
    return {
        f"has_loss_{label}": has_loss,
        f"prob_loss_{label}": prob_loss,
        f"expected_loss_{label}": expected_loss,
        f"min_negative_{label}": min_neg,
        f"is_mixed_{label}": has_loss and has_pos,
    }


def _option_skewness_features(probs, values, ev, std, label):
    if std > 1e-10:
        skew = sum(p * ((v - ev) / std) ** 3 for p, v in zip(probs, values))
    else:
        skew = float("nan")
    max_v, min_v = max(values), min(values)
    upside = max_v - ev
    downside = ev - min_v
    total = upside + downside
    upside_ratio = upside / total if total > 1e-10 else 0.5
    return {
        f"skewness_{label}": skew,
        f"upside_distance_{label}": upside,
        f"downside_distance_{label}": downside,
        f"upside_ratio_{label}": upside_ratio,
    }


def _dominance_check(probs_a, vals_a, probs_b, vals_b, higher_ev):
    """Conservative first-order stochastic dominance check."""
    # Collect all unique thresholds
    thresholds = sorted(set(vals_a + vals_b))

    # Compute P(X >= t) for each threshold
    def survival(probs, values, t):
        return sum(p for p, v in zip(probs, values) if v >= t)

    a_dom_b = True
    b_dom_a = True
    a_strict = False
    b_strict = False

    for t in thresholds:
        sa = survival(probs_a, vals_a, t)
        sb = survival(probs_b, vals_b, t)
        if sa < sb - 1e-9:
            a_dom_b = False
        if sa > sb + 1e-9:
            a_strict = True
        if sb < sa - 1e-9:
            b_dom_a = False
        if sb > sa + 1e-9:
            b_strict = True

    a_dominates = a_dom_b and a_strict
    b_dominates = b_dom_a and b_strict

    if a_dominates:
        dominant = "A"
    elif b_dominates:
        dominant = "B"
    else:
        dominant = "none"

    ev_matches = (dominant == "none") or (dominant == higher_ev)

    return {
        "A_dominates_B": a_dominates,
        "B_dominates_A": b_dominates,
        "any_dominance": a_dominates or b_dominates,
        "dominant_option": dominant,
        "ev_matches_dominance": ev_matches,
    }


def _option_salience_features(probs, values, label):
    max_v = max(values)
    min_v = min(values)
    # Find prob of best and worst
    prob_best = sum(p for p, v in zip(probs, values) if v == max_v)
    prob_worst = sum(p for p, v in zip(probs, values) if v == min_v)
    has_rare_high = max_v > 0 and prob_best <= RARE_THRESHOLD
    has_rare_loss = min_v < 0 and prob_worst <= RARE_THRESHOLD
    return {
        f"prob_best_outcome_{label}": prob_best,
        f"prob_worst_outcome_{label}": prob_worst,
        f"has_rare_high_gain_{label}": has_rare_high,
        f"has_rare_loss_{label}": has_rare_loss,
    }


def _similarity_features(probs_a, vals_a, probs_b, vals_b, ev_a, ev_b):
    ev_abs_diff = abs(ev_a - ev_b)
    max_a, min_a = max(vals_a), min(vals_a)
    max_b, min_b = max(vals_b), min(vals_b)
    range_a = max_a - min_a
    range_b = max_b - min_b
    overlap_num = max(0.0, min(max_a, max_b) - max(min_a, min_b))
    overlap_denom = max(range_a, range_b, 1.0)
    range_overlap = overlap_num / overlap_denom

    # Shared values (exact match)
    set_a = set(round(v, 4) for v in vals_a)
    set_b = set(round(v, 4) for v in vals_b)
    n_shared = len(set_a & set_b)

    return {
        "ev_abs_diff": ev_abs_diff,
        "range_overlap": range_overlap,
        "n_shared_values": n_shared,
        "total_outcomes": len(vals_a) + len(vals_b),
    }


def _safe_sub(a, b):
    if a != a or b != b:  # NaN check
        return float("nan")
    return a - b
