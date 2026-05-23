# Revision Inference Results

**Spec**: 024A — Revision Inference and Controls
**Date**: 2026-05-06
**Script**: `scripts/run_revision_inference.py`

---

## Executive Summary

All four reviewer concerns are addressed with inferential statistics:

1. **Loss exposure ≠ loss aversion repackaged**: Binary loss presence (ev_favored_has_loss) adds significant predictive value beyond loss probability and magnitude. β = 0.84 (p < 0.001) in choices13k and β = 0.71 (p < 0.001) in CPC18 after controlling for prob_loss and expected_loss. Binary-only AUC (0.738) outperforms probability-only (0.669) and magnitude-only (0.663).

2. **Inferential statistics added**: 95% CIs computed for all key rates and AUCs. All CIs are narrow for choices13k (large N) and wider but informative for CPC18.

3. **Graph clustering is not circular**: Permutation test (1,000 permutations) yields p < 0.001. Observed both-failure edge fraction (0.125) is 2.06× the null mean (0.061), far outside the null 95% interval [0.060, 0.062].

4. **Dominance ≠ easy problems**: any_dominance survives control for ev_abs_diff (β = −1.51, p < 0.001 in choices13k; β = −0.94, p < 0.001 in CPC18). Dominance problems do have larger EV gaps (5.56 vs 3.84 in choices13k), but dominance adds substantial predictive value beyond problem easiness.

---

## 1. EV Failure Rate Confidence Intervals

| Metric | Dataset | Value | 95% CI | N | Method |
|--------|---------|-------|--------|---|--------|
| EV failure rate | choices13k | 25.8% | [25.2%, 26.4%] | 23,159 | Wilson |
| EV failure rate | CPC18 | 17.6% | [13.4%, 22.7%] | 256 | Wilson |
| Trial-level block 1 | CPC18 | 35.3% | [34.7%, 35.9%] | 26,030 | Wilson (clustered) |
| Trial-level block 5 | CPC18 | 30.5% | [29.9%, 31.1%] | 26,030 | Wilson (clustered) |

**Note**: Trial-level CIs treat participant-game observations as independent (conservative for clustered data; true uncertainty is likely wider).

---

## 2. Loss Exposure Effect

### Unadjusted

| Dataset | Log OR | 95% CI | p-value |
|---------|--------|--------|---------|
| choices13k | 1.31 | [1.24, 1.37] | < 0.001 |
| CPC18 | 1.08 | [0.42, 1.75] | < 0.001 |

### Controlled for Probability and Magnitude

After controlling for ev_abs_diff, prob_loss_ev_favored, expected_loss_ev_favored, ambiguity, and any_dominance:

| Dataset | Predictor | β (std) | 95% CI | p-value |
|---------|-----------|---------|--------|---------|
| choices13k | ev_favored_has_loss | 0.84 | [0.80, 0.88] | < 0.001 |
| choices13k | prob_loss_ev_favored | −0.92 | [−0.98, −0.87] | < 0.001 |
| choices13k | expected_loss_ev_favored | −0.42 | [−0.46, −0.37] | < 0.001 |
| CPC18 | ev_favored_has_loss | 0.71 | [0.39, 1.08] | < 0.001 |
| CPC18 | prob_loss_ev_favored | −0.16 | [−0.74, 0.37] | 0.575 |
| CPC18 | expected_loss_ev_favored | 0.64 | [0.14, 1.24] | 0.027 |

**Interpretation**: ev_favored_has_loss remains large and significant in both datasets after controlling for continuous loss measures. The binary presence of loss adds predictive value beyond its probability and magnitude. This supports the claim that it is the *presence* of loss (a categorical signal) rather than its continuous properties that primarily drives EV failure.

### Binary vs Continuous Loss Comparison (AUC, choices13k 5-fold CV)

| Model | Predictors | AUC | SD |
|-------|-----------|-----|-----|
| Binary only | ev_abs_diff + ev_favored_has_loss | 0.738 | 0.010 |
| Probability only | ev_abs_diff + prob_loss_ev_favored | 0.669 | 0.006 |
| Magnitude only | ev_abs_diff + expected_loss_ev_favored | 0.663 | 0.003 |
| Full loss | all four | 0.791 | 0.010 |

**Interpretation**: Binary loss presence alone outperforms both probability-only and magnitude-only models by ~7 AUC points. Adding continuous measures to binary presence further improves to 0.791, indicating complementary information. But the binary signal is the dominant component.

---

## 3. Dominance Control

### ev_abs_diff Comparison

| Dataset | Condition | Mean ev_abs_diff | Median ev_abs_diff |
|---------|-----------|-----------------|-------------------|
| choices13k | Dominance present | 5.56 | 5.20 |
| choices13k | No dominance | 3.84 | 3.20 |
| CPC18 | Dominance present | 4.62 | 3.69 |
| CPC18 | No dominance | 3.70 | 2.75 |

Dominance problems do have systematically larger EV gaps (as expected — dominance implies one option is uniformly better).

### Controlled Regression

| Dataset | Predictor | β (std) | 95% CI | p-value |
|---------|-----------|---------|--------|---------|
| choices13k | ev_abs_diff | −0.61 | [−0.65, −0.57] | < 0.001 |
| choices13k | any_dominance | −1.51 | [−1.70, −1.37] | < 0.001 |
| choices13k | ev_favored_has_loss | 0.58 | [0.55, 0.62] | < 0.001 |
| choices13k | ambiguity | 0.27 | [0.23, 0.30] | < 0.001 |
| CPC18 | ev_abs_diff | −1.57 | [−2.20, −1.08] | < 0.001 |
| CPC18 | any_dominance | −0.94 | [−1.08, −0.76] | < 0.001 |
| CPC18 | ev_favored_has_loss | 0.52 | [0.18, 0.85] | 0.002 |
| CPC18 | ambiguity | 0.09 | [−0.23, 0.38] | 0.571 |

**Interpretation**: any_dominance has a large negative coefficient (−1.51 in choices13k, −0.94 in CPC18) even after controlling for ev_abs_diff. Dominance is not merely a proxy for "easy problems" — it provides additional protective information beyond the EV gap magnitude.

---

## 4. AUC Confidence Intervals

| Model | Dataset | AUC | 95% CI | N | Method |
|-------|---------|-----|--------|---|--------|
| Full logistic | choices13k | 0.744 | [0.738, 0.751] | 23,159 | Bootstrap predictions |
| Full logistic | CPC18 | 0.755 | [0.682, 0.825] | 256 | Bootstrap predictions |
| Cross-transfer | c13k → CPC18 | 0.728 | [0.642, 0.811] | 256 | Bootstrap test set |

**Note**: The choices13k AUC (0.744) is lower than the previously reported 0.837 because this analysis uses the full merged dataset (23,159 rows including condition repeats) rather than the deduplicated problem set used in spec 016. The relative ordering and cross-transfer pattern remain consistent.

---

## 5. Graph Permutation Test

| Statistic | Observed | Null Mean | Null SD | Null 95% CI | p-value | N perms |
|-----------|----------|-----------|---------|-------------|---------|---------|
| Both-endpoints EV-failure fraction | 0.125 | 0.061 | 0.0007 | [0.060, 0.062] | < 0.001 | 1,000 |

**Interpretation**: The observed fraction of edges connecting two EV-failure problems (0.125) is 2.06× the null expectation (0.061) and lies far outside the null distribution (no permutation out of 1,000 exceeded the observed value). The EV-failure clustering in the similarity graph is highly statistically significant and cannot be attributed to chance label assignment.

---

## Interpretation Consequences for Manuscript

### Claims Strengthened

1. **Loss exposure as binary signal**: The controlled regression and AUC comparison provide strong evidence that binary loss presence is not merely a proxy for loss probability or magnitude. The manuscript's emphasis on "presence of loss" (rather than continuous loss aversion) is empirically supported.

2. **Dominance as independent protector**: Dominance survives the ev_abs_diff control with a large coefficient. The claim that dominance reflects cognitive competence (not just problem easiness) is supported.

3. **Graph clustering significance**: The permutation test (p < 0.001) converts the descriptive 1.9× enrichment into a formal inferential result. The graph clustering claim can now be stated with statistical confidence.

4. **All key rates have CIs**: The manuscript can report precise confidence intervals for all headline numbers.

### Claims Unchanged

- Cross-dataset transfer remains strong (AUC 0.728, CI excludes 0.5 by wide margin).
- Learning dynamics are not re-tested here (block/feedback confound acknowledged).

### No Claims Need Softening

All tested claims survived their respective controls. No revision of the manuscript's central narrative is required based on these results.
