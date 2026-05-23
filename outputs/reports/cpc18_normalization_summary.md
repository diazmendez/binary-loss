# CPC18 Normalization Summary

Generated: 2026-05-05 12:37 UTC

## Overview

- Total raw rows: 694,500
- Unique GameIDs normalized: 270
- Unique participants: 926
- Exact reconstruction: 148 GameIDs
- Empirical reconstruction: 122 GameIDs

## Stage 1: Exact Normalization

- GameIDs: 148
- Raw rows covered: 377,850
- Max EV error A: 0.000000
- Max EV error B: 0.000000

## Stage 2: Empirical Normalization

*Reconstructed outcome distributions represent the experienced marginal distribution
of Apay/Bpay, not necessarily the generative parametric lottery decomposition.*

- GameIDs: 122
- Raw rows covered: 316,650
- Mean EV error A: 0.1155
- Mean EV error B: 0.3276
- Max EV error A: 1.5450
- Max EV error B: 2.7310

## Feature Summary

| Feature | Mean | Std | Min | Max |
|---------|------|-----|-----|-----|
| n_outcomes_A | 1.904 | 1.685 | 1.000 | 10.000 |
| n_outcomes_B | 3.630 | 2.433 | 1.000 | 10.000 |
| ev_A | 10.818 | 11.855 | -10.000 | 30.435 |
| ev_B | 10.532 | 11.846 | -15.774 | 36.540 |
| ev_diff | 0.287 | 4.899 | -18.500 | 13.266 |
| max_value_A | 23.281 | 29.593 | -10.000 | 221.000 |
| max_value_B | 42.604 | 41.668 | -11.000 | 256.000 |
| max_value_diff | -19.322 | 50.356 | -247.000 | 221.000 |
| min_value_A | 3.744 | 15.991 | -47.000 | 30.000 |
| min_value_B | -5.100 | 18.445 | -50.000 | 36.000 |

- **has_safe_option_A**: {True: 157, False: 113}
- **has_safe_option_B**: {False: 265, True: 5}
- **ev_max_conflict**: {False: 154, True: 116}
- **higher_ev_option**: {'A': 141, 'B': 115, 'equal': 14}
- **higher_max_option**: {'B': 199, 'A': 66, 'equal': 5}

## Set Distribution

| Set | Rows | Participants | Games |
|-----|------|--------------|-------|
| 1 | 93,750 | 125 | 30 |
| 2 | 60,750 | 81 | 30 |
| 3 | 60,000 | 80 | 30 |
| 4 | 60,000 | 80 | 30 |
| 5 | 60,000 | 80 | 30 |
| 6 | 90,000 | 120 | 30 |
| 7 | 90,000 | 120 | 30 |
| 8 | 90,000 | 120 | 30 |
| 9 | 90,000 | 120 | 30 |

## Missing RT

| Set | Total | Missing RT | % Missing |
|-----|-------|-----------|-----------|
| 1 | 93,750 | 93,750 | 100.0% |
| 2 | 60,750 | 60,750 | 100.0% |
| 3 | 60,000 | 60,000 | 100.0% |
| 4 | 60,000 | 60,000 | 100.0% |
| 5 | 60,000 | 60,000 | 100.0% |
| 6 | 90,000 | 0 | 0.0% |
| 7 | 90,000 | 0 | 0.0% |
| 8 | 90,000 | 0 | 0.0% |
| 9 | 90,000 | 0 | 0.0% |

## Validation Results

- choice_B binary (all 0/1): ✓
- Probability sum issues (A): 0
- Probability sum issues (B): 0

## Assumptions

1. Apay/Bpay represent realized payoffs from the full option (including La/lottery split).
2. Empirical marginals approximate the true outcome distribution with ~2500+ draws per GameID.
3. For simple games, the parametric formula exactly describes the outcome distribution.
4. pHa/pHb in the CSV are already 0–1 probabilities (not percentages).
5. CPC18 Sets 1–5 subsume CPC15; CPC15 is not normalized separately.

## Open Questions

1. Whether RT is available for Sets 8–9 (appears to be available based on data).
2. Whether empirical distributions for correlated games (Corr≠0) properly reflect the marginal.
3. Whether the 25-trial structure is consistent across all participants and games.
