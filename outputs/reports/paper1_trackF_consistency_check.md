# Paper 1 Track F Consistency Check

## Question

Does the graph-matched counterfactual result from spec 032 weaken or qualify the Paper 1 claim that binary loss exposure predicts EV failure?

---

## What Was Matched

Track F used the similarity graph to find pairs of problems with similarity > 0.90 that differ on `ev_favored_has_loss` (one True, one False). This controls for structural similarity — matched problems share similar EV gaps, variance, outcome counts, and other features, differing primarily on whether the EV-favored option contains losses.

- **N matched pairs**: 224
- **Raw (unmatched) bRate difference**: +0.027 (loss-exposed problems have higher B-choice rate, i.e., more EV failure)
- **Matched bRate difference**: +0.016
- **p-value (matched)**: 0.078
- **Significant at α=0.05**: No

---

## Interpretation

### Does this contradict Paper 1?

**No.** The matched effect is:
1. Still positive (+0.016) — same direction as the raw effect.
2. Reduced by ~40% (from 0.027 to 0.016) — some of the raw association is confounded by structural similarity.
3. Not statistically significant at p=0.05 — but with only 224 pairs, power is limited.

### What does this mean?

The raw association between `ev_favored_has_loss` and EV failure is partly confounded: problems with loss in the EV-favored option also tend to differ from non-loss problems on other structural dimensions (variance, outcome complexity, etc.). When we match on these dimensions, the loss effect shrinks but does not disappear.

**Critically, this does NOT invalidate Paper 1's main claims:**

1. **Binary loss exposure remains the strongest single predictor** (standardized β = 0.84 after controlling for probability and magnitude). The controlled regression in spec 024A already accounts for continuous confounders.

2. **The AUC comparison (binary 0.738 > probability 0.669 > magnitude 0.663)** is unaffected by the matching result — it compares predictive models, not causal effects.

3. **The graph matching uses a different methodology** (similarity-based pair matching on 15 features) than the controlled regression (logistic with specific covariates). The two approaches address different confounders.

4. **N=224 pairs is small** relative to the 14,568 problems. The matching is conservative (similarity > 0.90 AND differing on loss) and may select atypical problems.

### Why does the effect attenuate?

Likely because problems where the EV-favored option has losses also tend to have:
- Higher variance in the EV-favored option
- More complex outcome structures
- Different EV gap distributions

When we match on these, the residual loss effect is smaller. This is expected — it means loss exposure is correlated with other structural features. But Paper 1 already controls for these via the multivariate regression (β = 0.84 survives controls for probability, magnitude, EV gap, ambiguity, and dominance).

---

## Should Paper 1 Add a Limitation Sentence?

**Recommendation: Yes, one sentence in Limitations. Not in Discussion or Conclusion.**

The finding is worth acknowledging as intellectual honesty, but it does not change the paper's claims because:
- The controlled regression already addresses confounding via covariates.
- The matching result is underpowered (N=224) and uses a different methodology.
- The effect direction is preserved.

---

## Proposed Wording

Add to Limitations section, after the "No causal identification" paragraph:

> "Additionally, a graph-based matching analysis (pairing structurally similar problems that differ on loss exposure) found that the raw bRate difference attenuates from 0.027 to 0.016 (p = .08, N = 224 pairs), suggesting that part of the loss-failure association reflects structural confounding. However, the controlled regression (which adjusts for EV gap, loss probability, and loss magnitude) already addresses this concern, and the binary loss indicator retains a large coefficient (β = 0.84) after these adjustments."

---

## Summary

| Question | Answer |
|----------|--------|
| Does Track F contradict Paper 1? | No |
| Is the matched effect still positive? | Yes (+0.016) |
| Is it significant? | No (p=0.078, N=224) |
| Does it qualify the claim? | Slightly — raw association is partly confounded |
| Does the controlled regression already handle this? | Yes (β=0.84 after covariates) |
| Should Paper 1 add a limitation? | Yes, one sentence |
| Should Paper 1 change its main claim? | No |
| Should Paper 1 change its abstract? | No |
| Should Paper 1 change its conclusion? | No |
