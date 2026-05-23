"""Feature extraction for choice problems in common representation."""

import json


def compute_features(row: dict) -> dict:
    """Compute basic features from a common-format problem row.

    Expects row to have 'options_A' and 'options_B' as JSON strings
    of [[prob, value], ...] lists.
    """
    options_a = json.loads(row["options_A"])
    options_b = json.loads(row["options_B"])

    values_a = [o[1] for o in options_a]
    values_b = [o[1] for o in options_b]
    probs_a = [o[0] for o in options_a]
    probs_b = [o[0] for o in options_b]

    ev_a = sum(p * v for p, v in zip(probs_a, values_a))
    ev_b = sum(p * v for p, v in zip(probs_b, values_b))

    max_a = max(values_a)
    max_b = max(values_b)
    min_a = min(values_a)
    min_b = min(values_b)

    # Safe option: single outcome (all probability on one value, i.e. one outcome with p=1)
    has_safe_a = len(options_a) == 1 or any(p == 1.0 for p in probs_a)
    has_safe_b = len(options_b) == 1 or any(p == 1.0 for p in probs_b)

    higher_ev = "A" if ev_a > ev_b else ("B" if ev_b > ev_a else "equal")
    higher_max = "A" if max_a > max_b else ("B" if max_b > max_a else "equal")
    ev_max_conflict = higher_ev != higher_max and higher_ev != "equal" and higher_max != "equal"

    return {
        "n_outcomes_A": len(options_a),
        "n_outcomes_B": len(options_b),
        "ev_A": round(ev_a, 6),
        "ev_B": round(ev_b, 6),
        "ev_diff": round(ev_a - ev_b, 6),
        "max_value_A": max_a,
        "max_value_B": max_b,
        "max_value_diff": max_a - max_b,
        "min_value_A": min_a,
        "min_value_B": min_b,
        "has_safe_option_A": has_safe_a,
        "has_safe_option_B": has_safe_b,
        "higher_ev_option": higher_ev,
        "higher_max_option": higher_max,
        "ev_max_conflict": ev_max_conflict,
    }
