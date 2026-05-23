# Cross-Dataset EV Failure Comparison

Generated: 2026-05-05 12:47 UTC

## Overview

Exploratory comparison of EV failure patterns between choices13k (14,568 condition-rows)
and CPC18 (270 problem-level GameIDs). Both datasets share the same common representation
with explicit `[[probability, value], ...]` outcome lists and identical feature set.

## Dataset-Level Summary

| Metric | choices13k | CPC18 |
|--------|-----------|-------|
| N problems | 14,568 | 270 |
| N EV-consistent | 10,566 | 211 |
| N EV-inconsistent | 3,509 | 45 |
| EV failure rate | 24.9% | 17.6% |
| N EV ties | 469 | 14 |
| N observed ties | 25 | 0 |
| Mean observed B-rate | 0.519 | 0.480 |
| Corr(ev_diff, B-rate) | -0.6280 | -0.7166 |

## EV Failure Breakdown by Feature

### ambiguity

| Category | choices13k N | choices13k Rate | CPC18 N | CPC18 Rate |
|----------|-------------|----------------|---------|-----------|
| False | 11,355 | 22.8% | 219 | 16.9% |
| True | 2,720 | 34.0% | 37 | 21.6% |

### corr

| Category | choices13k N | choices13k Rate | CPC18 N | CPC18 Rate |
|----------|-------------|----------------|---------|-----------|
| -1 | 587 | 25.9% | 10 | 10.0% |
| 0 | 12,902 | 24.7% | 239 | 18.0% |
| 1 | 586 | 29.0% | 7 | 14.3% |

### ev_max_conflict

| Category | choices13k N | choices13k Rate | CPC18 N | CPC18 Rate |
|----------|-------------|----------------|---------|-----------|
| False | 8,227 | 19.9% | 140 | 20.7% |
| True | 5,848 | 32.0% | 116 | 13.8% |

### has_safe_option_A

| Category | choices13k N | choices13k Rate | CPC18 N | CPC18 Rate |
|----------|-------------|----------------|---------|-----------|
| False | 6,169 | 28.4% | 110 | 22.7% |
| True | 7,906 | 22.2% | 146 | 13.7% |

### has_safe_option_B

| Category | choices13k N | choices13k Rate | CPC18 N | CPC18 Rate |
|----------|-------------|----------------|---------|-----------|
| False | 13,921 | 24.8% | 251 | 16.7% |
| True | 154 | 35.7% | 5 | 60.0% |

### n_outcomes_B_group

| Category | choices13k N | choices13k Rate | CPC18 N | CPC18 Rate |
|----------|-------------|----------------|---------|-----------|
| 1-2 | 7,663 | 23.4% | 148 | 18.9% |
| 3-4 | 1,875 | 27.2% | 37 | 16.2% |
| 5-6 | 1,893 | 25.3% | 26 | 11.5% |
| 7+ | 2,644 | 27.5% | 45 | 17.8% |

### feedback (choices13k) / feedback_available (CPC18)

| Category | Dataset | N | Rate |
|----------|---------|---|------|
| False | choices13k | 2301 | 28.3% |
| True | choices13k | 11774 | 24.3% |
| True | cpc18 | 256 | 17.6% |

### reconstruction_method (CPC18 only)

| Method | N | Rate |
|--------|---|------|
| empirical | 122 | 18.0% |
| exact | 134 | 17.2% |

## Effect Direction Comparison

| Predictor | choices13k | CPC18 | Consistent? |
|-----------|-----------|-------|-------------|
| ambiguity=True | ↑ | ↑ | ✓ |
| ev_max_conflict=True | ↑ | ↓ | ✗ |
| has_safe_option_A=True | ↓ | ↓ | ✓ |
| has_safe_option_B=True | ↑ | ↑ | ✓ |
| n_outcomes_B high | ↑ | ↓ | ✗ |

## Logistic Regression Comparison

*Exploratory. CPC18 has only 270 observations — estimates are less stable.*

| Feature | choices13k coef | CPC18 coef | Same sign? |
|---------|----------------|------------|-----------|
| intercept | -0.5143 | -0.6921 | ✓ |
| ev_diff | -0.2906 | -0.7259 | ✓ |
| max_value_diff | -0.0039 | 0.0166 | ✗ |
| min_value_diff | -0.0413 | -0.0449 | ✓ |
| n_outcomes_B | 0.1431 | 0.1982 | ✓ |
| ambiguity | 0.6706 | 0.0592 | ✓ |
| ev_max_conflict | 0.1039 | -0.2437 | ✗ |
| has_safe_option_A | 0.5582 | 0.6137 | ✓ |
| has_safe_option_B | -0.1205 | -0.4474 | ✓ |

| Metric | choices13k | CPC18 |
|--------|-----------|-------|
| McFadden pseudo R² | 0.3132 | 0.5617 |
| Classification accuracy | 0.7794 | 0.8477 |

## Top 20 EV Failures: choices13k

| # | id | B-rate | ev_diff | n_out_B | ambiguity | ev_max_conflict |
|---|---|--------|---------|---------|-----------|-----------------|
| 1 | 2487 | 0.062 | -0.83 | 2 | True | False |
| 2 | 1830 | 0.925 | 0.65 | 4 | True | True |
| 3 | 9841 | 0.075 | -0.09 | 2 | False | False |
| 4 | 3066 | 0.920 | 1.06 | 2 | True | True |
| 5 | 6255 | 0.093 | -2.90 | 2 | True | True |
| 6 | 4157 | 0.907 | 4.10 | 5 | True | True |
| 7 | 11899 | 0.894 | 4.50 | 9 | False | False |
| 8 | 11527 | 0.893 | 1.70 | 3 | True | True |
| 9 | 8221 | 0.889 | 0.20 | 8 | True | True |
| 10 | 1589 | 0.888 | 8.78 | 8 | True | True |
| 11 | 591 | 0.876 | 0.10 | 3 | False | False |
| 12 | 1381 | 0.875 | 2.72 | 9 | True | True |
| 13 | 1795 | 0.875 | 1.15 | 3 | True | True |
| 14 | 2170 | 0.875 | 2.40 | 2 | False | False |
| 15 | 4945 | 0.875 | 9.43 | 6 | True | True |
| 16 | 5444 | 0.126 | -4.75 | 7 | False | False |
| 17 | 7132 | 0.129 | -0.50 | 2 | True | True |
| 18 | 9105 | 0.129 | -1.25 | 2 | True | False |
| 19 | 219 | 0.867 | 0.05 | 2 | True | True |
| 20 | 5321 | 0.867 | 0.15 | 7 | False | True |

## Top 20 EV Failures: CPC18

| # | game_id | B-rate | ev_diff | n_out_B | ambiguity | ev_max_conflict | method |
|---|---------|--------|---------|---------|-----------|-----------------|--------|
| 1 | 86 | 0.246 | -3.50 | 2 | True | True | exact |
| 2 | 52 | 0.264 | -0.80 | 2 | False | False | exact |
| 3 | 208 | 0.326 | -1.19 | 10 | False | False | empirical |
| 4 | 221 | 0.669 | 2.91 | 8 | False | True | empirical |
| 5 | 31 | 0.331 | -2.40 | 2 | True | False | exact |
| 6 | 119 | 0.336 | -2.68 | 3 | False | False | empirical |
| 7 | 141 | 0.661 | 0.20 | 2 | False | False | exact |
| 8 | 269 | 0.340 | -5.60 | 2 | False | False | exact |
| 9 | 260 | 0.650 | 0.23 | 2 | False | False | exact |
| 10 | 39 | 0.646 | 1.50 | 6 | False | True | empirical |
| 11 | 263 | 0.366 | -0.81 | 2 | True | True | exact |
| 12 | 251 | 0.369 | -4.60 | 2 | False | False | exact |
| 13 | 69 | 0.378 | -0.68 | 4 | True | True | empirical |
| 14 | 226 | 0.384 | -3.00 | 2 | False | False | exact |
| 15 | 61 | 0.612 | 1.13 | 7 | False | True | empirical |
| 16 | 73 | 0.389 | -0.14 | 8 | False | False | empirical |
| 17 | 37 | 0.390 | -0.70 | 2 | False | False | exact |
| 18 | 195 | 0.606 | 0.09 | 7 | False | True | empirical |
| 19 | 241 | 0.402 | -1.65 | 8 | False | False | empirical |
| 20 | 114 | 0.403 | -4.51 | 2 | False | False | exact |

## Figures

- `outputs/figures/cross_dataset_ev_failure_rates.png` — Bar chart of failure rates by key predictors
- `outputs/figures/cross_dataset_ev_vs_choice.png` — Scatter plot of ev_diff vs observed B-rate

## Key Observations

- CPC18 EV failure rate (17.6%) vs choices13k (24.9%).
- 6/8 logistic regression coefficients share the same sign across datasets.
- Both datasets show negative correlation between ev_diff and observed B-rate.

## Limitations

- choices13k has 14,568 condition-rows (13,006 unique Problem IDs); some problems appear twice under different conditions.
- CPC18 has only 270 GameIDs — breakdowns have small cell sizes and regression estimates are less stable.
- CPC18 empirical reconstruction is the experienced marginal distribution of Apay/Bpay, not necessarily the original generative parametric decomposition.
- CPC18 mean_choice_B aggregates across all 25 trials (including early learning trials).
- The two datasets differ in experimental design (online vs lab participants).
- Logistic regression on 270 CPC18 observations has limited statistical power.

## Assumptions

1. EV failure definitions are identical across datasets.
2. The common representation makes features directly comparable.
3. Aggregate choice rates (bRate / mean_choice_B) are comparable measures of preference.
