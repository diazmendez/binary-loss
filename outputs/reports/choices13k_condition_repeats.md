# choices13k: Condition Repeats Analysis

Generated: 2026-05-05 12:12 UTC

## Summary Counts

- Total rows: 14,568
- Unique problem_id values: 13,006
- Repeated problem_id values: 1,562
- Total rows for repeated problems: 3,124

Rows per repeated problem:

| Rows | Count |
|------|-------|
| 2 | 1562 |

## Structural Identity Validation

- Structurally identical across rows: **1562** / 1562
- Structure differs: **0**
- ✓ All repeated problems have identical gamble structure across conditions.

## Condition Variable Differences

| Variable | N problems where it differs |
|----------|---------------------------|
| feedback | 1562 |
| block | 1562 |
| ambiguity | 0 |
| corr | 0 |
| n | 1033 |

Most common combinations of differing variables:

| Combination | Count |
|-------------|-------|
| feedback, block, n | 1033 |
| feedback, block | 529 |

## Feedback Effect (Within-Problem)

Pairs where feedback differs: **1562**

- Mean bRate difference (feedback − no feedback): **0.0149**
- Median bRate difference: **0.0125**
- Feedback increases bRate (more B): 825
- Feedback decreases bRate (less B): 722
- Unchanged: 15

### Stratified by Ambiguity

| Ambiguity | Mean Δ | Median Δ | N |
|-----------|--------|----------|---|
| False | 0.0163 | 0.0125 | 1266 |
| True | 0.0090 | 0.0000 | 296 |

### Stratified by EV/Max Conflict

| EV/Max Conflict | Mean Δ | Median Δ | N |
|-----------------|--------|----------|---|
| False | 0.0224 | 0.0164 | 952 |
| True | 0.0032 | 0.0000 | 610 |

### Stratified by EV-Predicted Option

| EV Predicts | Mean Δ | Median Δ | N |
|-------------|--------|----------|---|
| A | -0.0147 | -0.0231 | 734 |
| B | 0.0437 | 0.0379 | 776 |
| tie | 0.0039 | -0.0058 | 52 |

### Stratified by N Outcomes B

| Group | Mean Δ | Median Δ | N |
|-------|--------|----------|---|
| 1-2 | 0.0100 | 0.0095 | 859 |
| 3-4 | 0.0147 | 0.0125 | 215 |
| 5-6 | 0.0337 | 0.0375 | 202 |
| 7-9 | 0.0165 | -0.0070 | 286 |

## Block Effect (Within-Problem)

Pairs where block differs: **1562**

- Mean bRate difference (later block − earlier block): **0.0149**
- Median bRate difference: **0.0125**
- bRate increases with block: 825
- bRate decreases with block: 722
- Unchanged: 15

## Top 30 Largest Within-Problem bRate Changes

| # | problem_id | bRate_row1 | bRate_row2 | abs_diff | feedback_r1 | feedback_r2 | block_r1 | block_r2 |
|---|---|---|---|---|---|---|---|---|
| 1 | 2973 | 0.275 | 0.853 | 0.578 | False | True | 1 | 4 |
| 2 | 503 | 0.375 | 0.863 | 0.488 | False | True | 1 | 3 |
| 3 | 6032 | 0.907 | 0.475 | 0.432 | False | True | 1 | 4 |
| 4 | 767 | 0.550 | 0.126 | 0.424 | False | True | 1 | 2 |
| 5 | 2366 | 0.307 | 0.716 | 0.409 | False | True | 1 | 3 |
| 6 | 4000 | 0.358 | 0.760 | 0.402 | False | True | 1 | 4 |
| 7 | 1698 | 0.188 | 0.587 | 0.399 | False | True | 1 | 3 |
| 8 | 3741 | 0.275 | 0.667 | 0.392 | False | True | 1 | 3 |
| 9 | 236 | 0.338 | 0.725 | 0.387 | False | True | 1 | 2 |
| 10 | 5037 | 0.227 | 0.613 | 0.386 | False | True | 1 | 3 |
| 11 | 4581 | 0.475 | 0.093 | 0.382 | False | True | 1 | 3 |
| 12 | 2080 | 0.850 | 0.475 | 0.375 | False | True | 1 | 5 |
| 13 | 3982 | 0.450 | 0.825 | 0.375 | False | True | 1 | 5 |
| 14 | 3535 | 0.660 | 0.289 | 0.371 | False | True | 1 | 2 |
| 15 | 3648 | 0.325 | 0.693 | 0.368 | False | True | 1 | 5 |
| 16 | 6658 | 0.325 | 0.693 | 0.368 | False | True | 1 | 3 |
| 17 | 2880 | 0.320 | 0.688 | 0.367 | False | True | 1 | 2 |
| 18 | 4331 | 0.387 | 0.747 | 0.360 | False | True | 1 | 5 |
| 19 | 6067 | 0.575 | 0.933 | 0.358 | False | True | 1 | 3 |
| 20 | 784 | 0.263 | 0.613 | 0.351 | False | True | 1 | 4 |
| 21 | 97 | 0.225 | 0.573 | 0.348 | False | True | 1 | 3 |
| 22 | 5627 | 0.212 | 0.560 | 0.347 | False | True | 1 | 3 |
| 23 | 3915 | 0.627 | 0.973 | 0.347 | False | True | 1 | 5 |
| 24 | 3594 | 0.275 | 0.613 | 0.338 | False | True | 1 | 4 |
| 25 | 2942 | 0.533 | 0.200 | 0.333 | False | True | 1 | 4 |
| 26 | 2656 | 0.575 | 0.906 | 0.331 | False | True | 1 | 3 |
| 27 | 4662 | 0.558 | 0.888 | 0.330 | False | True | 1 | 5 |
| 28 | 3601 | 0.533 | 0.862 | 0.329 | False | True | 1 | 5 |
| 29 | 1246 | 0.447 | 0.773 | 0.326 | False | True | 1 | 3 |
| 30 | 940 | 0.325 | 0.000 | 0.325 | False | True | 1 | 4 |

## Interpretation Notes

- Within-problem comparisons control for gamble structure, isolating condition effects.
- Feedback effect direction indicates whether outcome information shifts choices toward or away from B.
- Block effects should NOT be interpreted as learning without confirming temporal ordering within participants.

## Limitations

- Block interpretation uncertainty: it is unclear whether block represents temporal ordering within the same participant group.
- Small n per problem (15–33 participants per row).
- Aggregate bRate may mask individual-level heterogeneity.
- No correction for multiple comparisons in stratified analyses.

## Next Steps

- Investigate whether feedback effect interacts with EV failure (do failures become consistent with feedback?).
- Consider mixed-effects models if individual-level data becomes available.
- Use condition repeats as validation for graph-based representations (same node, different edge weights by condition).
