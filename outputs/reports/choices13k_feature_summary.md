# choices13k: Common Representation & Feature Summary

Generated: 2026-05-05 11:47 UTC

## Validation Results

- **ID alignment**: JSON keys are row indices (0..14567), matching 14568 CSV rows. CSV has 13006 unique Problem IDs (some problems appear in multiple block/feedback conditions).
- **Problems normalized**: 14568
- **Probability sum issues (Option A)**: 0
- **Probability sum issues (Option B)**: 0
- **Missing/invalid bRate**: 0
- **Feature computation errors**: 0

## Common Representation

| Field | Description |
|-------|-------------|
| dataset | Always 'choices13k' |
| problem_id | 1-indexed problem identifier |
| feedback | Whether feedback was provided |
| block | Block number (1–5) |
| ambiguity | Whether Option B is ambiguous |
| corr | Correlation between options (-1/0/1) |
| n | Number of participants |
| options_A | JSON: [[prob, value], ...] from c13k_problems.json |
| options_B | JSON: [[prob, value], ...] from c13k_problems.json |
| bRate | Aggregate B-choice rate |
| bRate_std | Std dev of B-choice rate |

## Feature Distributions

### Numeric Features

| Feature | Mean | Std | Min | Median | Max |
|---------|------|-----|-----|--------|-----|
| n_outcomes_A | 2.000 | 0.000 | 2.000 | 2.000 | 2.000 |
| n_outcomes_B | 3.682 | 2.314 | 1.000 | 2.000 | 9.000 |
| ev_A | 10.529 | 11.728 | -10.450 | 11.000 | 30.470 |
| ev_B | 10.587 | 12.722 | -23.400 | 10.800 | 45.500 |
| ev_diff | -0.057 | 5.078 | -16.700 | 0.000 | 17.540 |
| max_value_A | 22.014 | 24.076 | -10.000 | 18.000 | 118.000 |
| max_value_B | 40.661 | 33.847 | -18.000 | 33.000 | 256.000 |
| max_value_diff | -18.647 | 39.329 | -259.000 | -13.000 | 120.000 |
| min_value_A | 3.813 | 16.407 | -50.000 | 5.000 | 30.000 |
| min_value_B | -4.744 | 18.388 | -50.000 | -4.000 | 41.000 |

### Categorical Features

- **has_safe_option_A**: True=8163, False=6405
- **has_safe_option_B**: True=240, False=14328
- **ev_max_conflict**: True=5888, False=8680
- **higher_ev_option**: B=7109, A=7063, equal=396
- **higher_max_option**: B=10658, A=3696, equal=214

### bRate vs Expected Value

- Problems where EV(A) > EV(B): 8490, mean bRate = 0.388
- Problems where EV(B) > EV(A): 8629, mean bRate = 0.648
- Problems where EV(A) = EV(B): 573, mean bRate = 0.524
- Correlation(ev_diff, bRate): -0.6209

## Assumptions

1. JSON keys are CSV row indices (0-based). Each JSON entry corresponds to one CSV row.
2. CSV Problem column is the problem ID; some problems appear in multiple rows (different block/feedback).
3. c13k_problems.json is authoritative for option/outcome/probability structure.
4. Each [prob, value] pair in JSON represents an explicit outcome.
5. A 'safe' option is one with a single outcome or any outcome with probability 1.0.
6. bRate aggregates across all participants for that problem-condition row.
