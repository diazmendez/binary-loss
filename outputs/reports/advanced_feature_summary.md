# Advanced Feature Summary

Generated: 2026-05-05 13:19 UTC

## Overview

- choices13k: 14568 rows, 0 computation errors
- CPC18: 270 rows, 0 computation errors
- Total features: 63
- Heuristic constants: RARE_THRESHOLD = 0.1

## NaN Counts

| Feature | choices13k NaN | CPC18 NaN |
|---------|---------------|-----------|
| cv_A | 243 | 5 |
| cv_B | 80 | 4 |
| skewness_A | 8243 | 158 |
| skewness_B | 291 | 5 |
| skewness_diff | 8508 | 162 |
| max_ratio | 2421 | 46 |

## Numeric Feature Distributions

| Feature | c13k Mean | c13k Std | c13k Min | c13k Max | CPC18 Mean | CPC18 Std |
|---------|-----------|---------|---------|---------|-----------|----------|
| variance_A | 199.613 | 543.894 | 0.000 | 5991.360 | 217.666 | 610.703 |
| std_A | 6.885 | 12.338 | 0.000 | 77.404 | 6.958 | 13.034 |
| cv_A | 1.505 | 7.844 | 0.000 | 286.590 | 1.460 | 6.094 |
| range_A | 18.201 | 29.400 | 0.000 | 158.000 | 19.537 | 35.748 |
| variance_B | 446.712 | 753.067 | 0.000 | 6455.040 | 556.403 | 1186.827 |
| std_B | 15.409 | 14.466 | 0.000 | 80.343 | 16.086 | 17.284 |
| cv_B | 3.602 | 12.731 | 0.000 | 391.087 | 10.291 | 105.473 |
| range_B | 45.404 | 37.940 | 0.000 | 283.000 | 47.704 | 45.962 |
| variance_diff | -247.099 | 924.825 | -6231.240 | 5946.916 | -338.738 | 1324.488 |
| std_diff | -8.524 | 19.116 | -78.384 | 72.092 | -9.128 | 21.192 |
| range_diff | -27.204 | 48.427 | -269.000 | 150.000 | -28.167 | 59.180 |
| prob_loss_A | 0.269 | 0.398 | 0.000 | 1.000 | 0.235 | 0.385 |
| expected_loss_A | -2.668 | 4.894 | -33.750 | 0.000 | -2.407 | 4.735 |
| min_negative_A | -4.913 | 9.423 | -50.000 | 0.000 | -4.507 | 9.462 |
| prob_loss_B | 0.327 | 0.368 | 0.000 | 1.000 | 0.308 | 0.369 |
| expected_loss_B | -4.636 | 6.489 | -36.000 | 0.000 | -4.534 | 6.964 |
| min_negative_B | -9.972 | 12.863 | -50.000 | 0.000 | -9.922 | 13.591 |
| prob_loss_diff | -0.058 | 0.367 | -1.000 | 1.000 | -0.074 | 0.372 |
| expected_loss_diff | 1.969 | 6.805 | -33.000 | 33.000 | 2.126 | 7.359 |
| skewness_A | 0.735 | 3.779 | -9.849 | 9.849 | 1.144 | 3.248 |
| upside_distance_A | 11.485 | 21.480 | -0.000 | 124.000 | 12.463 | 27.465 |
| downside_distance_A | 6.716 | 12.569 | -0.000 | 78.000 | 7.074 | 13.873 |
| upside_ratio_A | 0.533 | 0.208 | 0.010 | 0.990 | 0.534 | 0.189 |
| skewness_B | 1.078 | 3.867 | -25.537 | 54.464 | 1.115 | 4.427 |
| upside_distance_B | 30.074 | 32.575 | -0.000 | 268.600 | 32.072 | 40.103 |
| downside_distance_B | 15.331 | 15.810 | -0.000 | 86.400 | 15.632 | 16.464 |
| upside_ratio_B | 0.604 | 0.291 | 0.010 | 0.999 | 0.594 | 0.304 |
| skewness_diff | -0.221 | 5.360 | -54.056 | 25.537 | 0.291 | 5.136 |
| upside_ratio_diff | -0.071 | 0.356 | -0.984 | 0.980 | -0.061 | 0.363 |
| prob_best_outcome_A | 0.750 | 0.351 | 0.010 | 1.000 | 0.722 | 0.383 |

## Boolean Feature Distributions

| Feature | c13k True% | CPC18 True% |
|---------|-----------|------------|
| ev_risk_conflict | 48.2% | 47.8% |
| has_loss_A | 37.7% | 33.0% |
| is_mixed_A | 22.4% | 17.8% |
| has_loss_B | 57.0% | 53.0% |
| is_mixed_B | 51.5% | 44.4% |
| any_loss | 65.7% | 60.7% |
| both_have_loss | 29.0% | 25.2% |
| loss_asymmetry | 36.7% | 35.6% |
| ev_favored_has_loss | 42.9% | 36.3% |
| max_favored_has_loss | 55.9% | 50.7% |
| A_dominates_B | 7.0% | 5.2% |
| B_dominates_A | 10.0% | 8.1% |
| any_dominance | 17.0% | 13.3% |
| ev_matches_dominance | 100.0% | 100.0% |
| has_rare_high_gain_A | 10.4% | 14.4% |
| has_rare_loss_A | 4.0% | 2.2% |
| has_rare_high_gain_B | 44.6% | 40.7% |
| has_rare_loss_B | 10.2% | 10.0% |
| salience_conflict | 33.1% | 28.5% |

## Categorical Feature Distributions

## Top 15 Correlations with EV Failure

### choices13k

| Feature | Correlation |
|---------|------------|
| ev_favored_has_loss | 0.2767 |
| any_dominance | -0.2630 |
| ev_abs_diff | -0.2324 |
| B_dominates_A | -0.1986 |
| std_B | 0.1842 |
| salience_conflict | -0.1833 |
| range_B | 0.1814 |
| variance_B | 0.1598 |
| A_dominates_B | -0.1534 |
| max_favored_has_loss | 0.1494 |
| upside_distance_B | 0.1431 |
| downside_distance_B | 0.1407 |
| expected_loss_B | -0.1339 |
| is_mixed_B | 0.1233 |
| any_loss | 0.1207 |

### CPC18

| Feature | Correlation |
|---------|------------|
| ev_abs_diff | -0.3196 |
| ev_risk_conflict | -0.2191 |
| ev_favored_has_loss | 0.2063 |
| any_dominance | -0.1868 |
| variance_B | 0.1821 |
| std_B | 0.1763 |
| range_B | 0.1668 |
| std_A | 0.1548 |
| upside_distance_B | 0.1512 |
| range_A | 0.1500 |
| variance_A | 0.1468 |
| is_mixed_A | 0.1463 |
| B_dominates_A | -0.1416 |
| downside_distance_A | 0.1381 |
| upside_distance_A | 0.1252 |

## Cross-Dataset Feature Comparison

Features with largest distribution differences (by mean):

| Feature | Standardized Diff (CPC18 − c13k) |
|---------|----------------------------------|
| cv_B | 0.525 |
| n_shared_values | 0.464 |
| max_ratio | 0.150 |
| variance_B | 0.146 |
| ev_abs_diff | -0.122 |
| skewness_A | 0.108 |
| variance_diff | -0.099 |
| skewness_diff | 0.096 |
| prob_loss_A | -0.087 |
| prob_best_outcome_B | 0.086 |
| prob_best_outcome_A | -0.077 |
| total_outcomes | -0.064 |
| upside_distance_B | 0.061 |
| range_B | 0.061 |
| expected_loss_A | 0.053 |

## Do Advanced Features Explain Known Divergences?

### ev_max_conflict divergence

In choices13k, ev_max_conflict ↑ failure. In CPC18, it ↓ failure.

| Feature | c13k conflict | c13k no-conflict | CPC18 conflict | CPC18 no-conflict |
|---------|--------------|-----------------|---------------|------------------|
| variance_diff | -283.077 | -228.826 | -402.763 | -290.511 |
| std_diff | -9.854 | -7.707 | -10.827 | -7.849 |
| skewness_diff | -0.319 | -0.210 | -0.390 | 0.816 |
| ev_risk_conflict | 90.6% | 19.4% | 88.8% | 16.9% |
| loss_asymmetry | 39.8% | 34.5% | 40.5% | 31.8% |
| range_overlap | 0.150 | 0.131 | 0.124 | 0.156 |
| ev_abs_diff | 3.779 | 4.156 | 3.520 | 3.712 |

## CPC18 Anti-Learning Characterization

Anti-learning GameIDs: 84, Learning GameIDs: 172

| Feature | Anti-learning Mean | Learning Mean | Diff |
|---------|-------------------|--------------|------|
| variance_diff | -405.682 | -303.145 | -102.537 |
| std_diff | -10.518 | -8.415 | -2.103 |
| ev_abs_diff | 3.634 | 3.923 | -0.289 |
| range_overlap | 0.152 | 0.132 | 0.020 |
| skewness_diff | 1.500 | -0.501 | 2.000 |
| prob_loss_diff | -0.095 | -0.069 | -0.026 |
| upside_ratio_diff | -0.003 | -0.088 | 0.085 |
| total_outcomes | 5.571 | 5.703 | -0.132 |
| ev_risk_conflict | 58.3% | 46.5% | 11.8pp |
| loss_asymmetry | 40.5% | 34.3% | 6.2pp |
| any_dominance | 2.4% | 19.8% | -17.4pp |
| salience_conflict | 23.8% | 33.1% | -9.3pp |

## Limitations

- All analyses are exploratory.
- Dominance is rare by design in these experiments.
- CPC18 empirical reconstruction may affect variance/skewness estimates.
- Correlations do not imply causation.
