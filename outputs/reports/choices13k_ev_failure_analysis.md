# choices13k: EV Failure Analysis

Generated: 2026-05-05 12:05 UTC

## 1. Overall EV Consistency

| Metric | Count | Percentage |
|--------|-------|------------|
| EV-consistent | 10566 | 75.1% |
| EV-inconsistent | 3509 | 24.9% |
| EV ties (excluded) | 469 | — |
| Observed ties (excluded) | 25 | — |
| Total evaluated | 14075 | 100% |

## 2. EV Failure Breakdown by Variable

### Feedback

| Feedback | N | Inconsistent | Rate |
|---|---|---|---|
| False | 2301 | 652 | 28.3% |
| True | 11774 | 2857 | 24.3% |

### Ambiguity

| Ambiguity | N | Inconsistent | Rate |
|---|---|---|---|
| False | 11355 | 2584 | 22.8% |
| True | 2720 | 925 | 34.0% |

### Correlation

| Correlation | N | Inconsistent | Rate |
|---|---|---|---|
| -1.0 | 587 | 152 | 25.9% |
| 0.0 | 12902 | 3187 | 24.7% |
| 1.0 | 586 | 170 | 29.0% |

### Block

| Block | N | Inconsistent | Rate |
|---|---|---|---|
| 1.0 | 2301 | 652 | 28.3% |
| 2.0 | 2908 | 715 | 24.6% |
| 3.0 | 2933 | 739 | 25.2% |
| 4.0 | 2958 | 698 | 23.6% |
| 5.0 | 2975 | 705 | 23.7% |

### EV/Max Conflict

| EV/Max Conflict | N | Inconsistent | Rate |
|---|---|---|---|
| False | 8227 | 1638 | 19.9% |
| True | 5848 | 1871 | 32.0% |

### Safe Option A

| Safe Option A | N | Inconsistent | Rate |
|---|---|---|---|
| False | 6169 | 1751 | 28.4% |
| True | 7906 | 1758 | 22.2% |

### Safe Option B

| Safe Option B | N | Inconsistent | Rate |
|---|---|---|---|
| False | 13921 | 3454 | 24.8% |
| True | 154 | 55 | 35.7% |

### N Outcomes B (grouped)

| Group | N | Inconsistent | Rate |
|---|---|---|---|
| 1-2 | 7663 | 1793 | 23.4% |
| 3-4 | 1875 | 510 | 27.2% |
| 5-6 | 1893 | 479 | 25.3% |
| 7-9 | 2644 | 727 | 27.5% |

## 3. Top 30 Strongest EV Failures

| # | problem_id | ev_diff | bRate | failure_strength | n_outcomes_B | feedback | ambiguity | corr |
|---|---|---|---|---|---|---|---|---|
| 1 | 2487 | -0.83 | 0.062 | 0.938 | 2 | False | True | 0 |
| 2 | 1830 | 0.65 | 0.925 | 0.925 | 4 | False | True | 0 |
| 3 | 9841 | -0.09 | 0.075 | 0.925 | 2 | True | False | 0 |
| 4 | 3066 | 1.06 | 0.920 | 0.920 | 2 | False | True | 0 |
| 5 | 6255 | -2.90 | 0.093 | 0.907 | 2 | True | True | 0 |
| 6 | 4157 | 4.10 | 0.907 | 0.907 | 5 | False | True | 0 |
| 7 | 11899 | 4.50 | 0.894 | 0.894 | 9 | True | False | -1 |
| 8 | 11527 | 1.70 | 0.893 | 0.893 | 3 | True | True | 0 |
| 9 | 8221 | 0.20 | 0.889 | 0.889 | 8 | True | True | 0 |
| 10 | 1589 | 8.78 | 0.888 | 0.888 | 8 | False | True | 0 |
| 11 | 591 | 0.10 | 0.876 | 0.876 | 3 | True | False | 0 |
| 12 | 1381 | 2.72 | 0.875 | 0.875 | 9 | False | True | 0 |
| 13 | 1795 | 1.15 | 0.875 | 0.875 | 3 | False | True | 0 |
| 14 | 2170 | 2.40 | 0.875 | 0.875 | 2 | True | False | 0 |
| 15 | 4945 | 9.43 | 0.875 | 0.875 | 6 | True | True | 0 |
| 16 | 5444 | -4.75 | 0.126 | 0.874 | 7 | True | False | 0 |
| 17 | 7132 | -0.50 | 0.129 | 0.871 | 2 | True | True | 0 |
| 18 | 9105 | -1.25 | 0.129 | 0.871 | 2 | True | True | 0 |
| 19 | 219 | 0.05 | 0.867 | 0.867 | 2 | True | True | 0 |
| 20 | 5321 | 0.15 | 0.867 | 0.867 | 7 | False | False | 0 |
| 21 | 10099 | 5.80 | 0.867 | 0.867 | 9 | True | True | 0 |
| 22 | 5539 | -0.34 | 0.137 | 0.863 | 2 | False | True | 1 |
| 23 | 6682 | 1.30 | 0.863 | 0.863 | 7 | True | True | -1 |
| 24 | 1496 | 0.60 | 0.862 | 0.862 | 2 | False | True | 0 |
| 25 | 1890 | 1.30 | 0.862 | 0.862 | 3 | False | True | 0 |
| 26 | 1014 | 0.05 | 0.860 | 0.860 | 2 | True | False | 0 |
| 27 | 6716 | 8.00 | 0.859 | 0.859 | 5 | False | True | 0 |
| 28 | 9681 | -0.66 | 0.141 | 0.859 | 2 | True | True | 0 |
| 29 | 1573 | -2.00 | 0.147 | 0.853 | 2 | True | True | 0 |
| 30 | 2973 | 3.25 | 0.853 | 0.853 | 6 | True | False | 0 |

## 4. Mean bRate by EV/Max Conflict Category

| higher_ev \ higher_max | A | B | equal |
|---|---|---|---|
| A | 0.315 | 0.430 | 0.203 |
| B | 0.586 | 0.662 | 0.727 |
| equal | 0.518 | 0.525 | — |

## 5. Logistic Regression (Predicting Majority B)

*Descriptive model, not causal.*

| Feature | Coefficient | Std Error |
|---|---|---|
| intercept | -0.3159 | 0.0661 |
| ev_diff | -0.2868 | 0.0061 |
| max_value_diff | -0.0061 | 0.0006 |
| min_value_diff | -0.0366 | 0.0012 |
| n_outcomes_B | 0.1350 | 0.0096 |
| ambiguity | 0.6725 | 0.0550 |
| feedback | 0.0852 | 0.0573 |
| ev_max_conflict | 0.0790 | 0.0470 |

- **McFadden pseudo R²**: 0.3066
- **Classification accuracy**: 0.7805
- Note: All features standardized by sklearn default (no manual scaling).
