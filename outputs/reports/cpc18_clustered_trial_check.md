# CPC18 Clustered Trial-Level Robustness Check

## Purpose

Address the concern that trial-level CIs assume independence. Observations are
nested within participants (926 participants × ~750 trials each). This check
tests whether the block-related decline in EV failure survives clustering.

## Descriptive Rates by Block

| Block | EV Failure Rate | N trials |
|-------|----------------|----------|
| 1 | 0.3514 (35.1%) | 130,150 |
| 2 | 0.3232 (32.3%) | 130,150 |
| 3 | 0.3146 (31.5%) | 130,150 |
| 4 | 0.3073 (30.7%) | 130,150 |
| 5 | 0.3041 (30.4%) | 130,150 |

Total observations: 650,750 (after excluding 14 GameIDs with ev_diff = 0)
Participants: 926
Games: 256

## Method

Primary method: GEE with binomial family and exchangeable correlation
structure, clustered by participant (SubjID). This accounts for
within-participant correlation in the standard errors.

Fallback: Cluster-robust logistic regression (sandwich estimator).
Comparison: Naive logistic regression (independent observations).

## Results

### Naive (Independent Observations)

- Coefficient (block): -0.05078
- SE: 0.00188
- 95% CI: [-0.05447, -0.04710]
- OR: 0.9505
- p-value: 1.62e-160

### GEE (Exchangeable Correlation, Clustered by Participant)

- Coefficient (block): -0.05087
- SE: 0.00318
- 95% CI: [-0.05710, -0.04463]
- OR: 0.9504
- p-value: 1.44e-57
- Notes: exchangeable corr=The correlation between two observations in the same cluster is 0.029

### Cluster-Robust Logistic (Sandwich SE, Clustered by Participant)

- Coefficient (block): -0.05078
- SE: 0.00317
- 95% CI: [-0.05700, -0.04457]
- OR: 0.9505
- p-value: 1.02e-57

### Comparison

| Metric | Naive | GEE | Cluster-Robust |
|--------|-------|-----|----------------|
| Coefficient | -0.05078 | -0.05087 | -0.05078 |
| SE | 0.00188 | 0.00318 | 0.00317 |
| p-value | 1.62e-160 | 1.44e-57 | 1.02e-57 |
| OR | 0.9505 | 0.9504 | 0.9505 |
| SE inflation | 1.0x | 1.7x | 1.7x |

## Interpretation

The block-related decline in EV failure **remains statistically significant**
after accounting for within-participant clustering (p = 1.44e-57).
The SE inflates by 1.7x relative to the naive estimate,
but the effect remains robust. Each additional block is associated with
5.0% lower odds of EV failure (OR = 0.9504).

## Manuscript Implication

Add to Results (Changes Across Blocks):
> A GEE with exchangeable correlation clustered by participant confirmed that
> the block-related decline remained significant (OR = 0.950,
> 95% CI [-0.057, -0.045], p < .001).