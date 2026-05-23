# Graph Results Validation and Leakage Audit

## Executive Summary

**6/7 claims validated.** 5 suitable for main text.

Key finding: Track C (AUC 0.86) had label leakage. After correction:
- Fold-safe AUC: 0.8492 (was 0.8609)
- Topology-only AUC: 0.6121
- Leakage inflation: +0.0117

## Leakage Analysis

### Track C: Graph Position

**Problem**: `failure_density` and `neighborhood_entropy` use ev_failure labels of neighbors,
including test-fold neighbors. This is transductive label leakage.

**Leaked features**: failure_density, neighborhood_entropy, local_disagreement
**Clean features**: embedding_density, degree, boundary_score, dist_to_dom

| Method | AUC |
|--------|-----|
| Original (leaked) | 0.8609 |
| Method A (fold-safe labels) | 0.8492 |
| Method B (topology-only) | 0.6121 |

**Conclusion**: Leakage inflated AUC by +0.0117. 
Fold-safe result still strong (>= 0.75). Claim survives with correction.

### Track 1/B: Embeddings

- Adjacency uses behavioral labels: **False**
- Verified AUC: **0.7882**
- Status: **behavior-free**

The spectral embedding is genuinely behavior-free. The adjacency matrix is built from
problem-structure features (EV, variance, outcomes, loss presence) — none of which are
behavioral outcomes (bRate, choice, learning). The embedding encodes relational structure.

## Baseline Comparisons

### Track D: Retrieval vs Flat Features

| Method | r with actual bRate |
|--------|---------------------|
| Graph retrieval (k=20) | 0.7629 |
| EV-only | -0.6352 |
| Loss-only | -0.0213 |
| Flat features (CV) | 0.7558 |

Retrieval beats EV-only: **True**
Retrieval beats flat features: **True**

## Stability Checks

### Track E: Participant Clusters

- Clusters: 4
- Sizes: [188, 355, 173, 210]
- Mean ARI (5 seeds): **0.9779**
- Min ARI: 0.9633
- Stable (ARI > 0.7): **True**

## Matched Counterfactual Verification

### Track F: Pair Quality

- Loss-exposure matched pairs: 224
- Balance OK: **False**

Covariate balance (standardized differences):

- standardized_diff_ev_diff: 0.6725
- standardized_diff_variance_diff: 0.8350
- standardized_diff_n_outcomes_A: 4.3619
- standardized_diff_n_outcomes_B: 0.7364

## Validated Claims Table

See `outputs/tables/graph_results_validated_claims.csv`

## Risk Register

See `outputs/tables/graph_results_risk_register.csv`

## Recommendation for Paper 2

### Strong claims (low risk, validated):
- Topology-only graph features predict EV failure (AUC = 0.61)
- Behavior-free spectral embedding predicts EV failure (AUC = 0.79)
- The embedding signal is robust: 3 of 5 methods achieve AUC >= 0.75
- Graph retrieval predicts CPC18 behavior (r = 0.76)
- Participant clusters are stable (ARI = 0.98)

### Moderate claims (medium risk, validated with caveats):
- Graph-position features predict EV failure (AUC = 0.85, fold-safe)

### Weakened/dropped claims:
- Matched counterfactuals: loss effect attenuates after matching: Balance OK: False. N pairs: 224
