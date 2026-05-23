# Paper-Ready Result Summary (Spec 019)

## 1. Core Results

### EV Failure Rates

| Dataset | Level | Metric | Value | Source |
|---------|-------|--------|-------|--------|
| choices13k | Problem-level | EV failure rate | 24.9% | choices13k_ev_failure_analysis.md |
| CPC18 | Problem-level | EV failure rate | 17.6% | cross_dataset_ev_failure_comparison.md |
| CPC18 | Trial-level, block 1 | EV failure rate | 35.1% | cpc18_learning_dynamics.md |
| CPC18 | Trial-level, block 5 | EV failure rate | 30.4% | cpc18_learning_dynamics.md |

### Predictive Performance

| Model | choices13k AUC | CPC18 AUC | Cross-transfer AUC |
|-------|---------------|-----------|-------------------|
| EV-only (2 features) | 0.671 | 0.787 | 0.769 |
| Basic (9 features) | 0.646 | 0.584 | 0.578 |
| Basic + Loss (24 features) | 0.789 | 0.680 | 0.693 |
| Full (58 features) | 0.837 | 0.804 | 0.786 |
| GB ceiling (Full) | 0.879 | — | — |

### Top Predictive Features

| Rank | Feature | Standardized Coef | Direction |
|------|---------|-------------------|-----------|
| 1 | ev_favored_has_loss | 1.62 | ↑ failure |
| 2 | any_dominance | −1.45 (approx) | ↓ failure |
| 3 | ev_abs_diff | −1.2 (approx) | ↓ failure |

### Graph Structure

| Metric | Value |
|--------|-------|
| Total nodes | 128,797 |
| Total edges | 320,929 |
| EV-failure subgraph density | 0.00285 |
| EV-consistent subgraph density | 0.00149 |
| Density enrichment ratio | 1.9× |
| Cross-dataset similarity edges | 1,538 |
| Max cross-dataset similarity | 0.997 |

---

## 2. Result Strength Assessment

### Strong (paper-ready)

These results are robust, replicated, and clearly interpretable:

1. **EV failure rates** — Large N (13,006 + 270 problems), clear operational definition, consistent across analyses.
2. **Loss features as dominant predictor** — Converging evidence: highest AUC gain (+0.14), top logistic coefficient (1.62), strongest graph hub (38% failure fraction).
3. **Dominance as protector** — 0.4% failure rate when dominance present; 100% EV-agreement with dominance.
4. **Cross-dataset transfer** — AUC 0.79 training on choices13k, testing on CPC18. Same feature directions for 6/8 coefficients.
5. **Graph density enrichment** — 1.9× with clear baseline comparison.
6. **Learning dynamics** — Block 1→5 shift (−4.7pp), stratified by condition, consistent with feedback mechanism.

### Exploratory but Promising

These results are suggestive but need additional validation:

7. **Anti-learning characterization** — 84/256 GameIDs worsen; concentrated in ev_max_conflict. Mechanism hypothesized but not tested.
8. **Cross-dataset graph bridges** — Similarity 0.997, shared features. Illustrative but not formally tested.
9. **GB ceiling** — 0.88 vs 0.84 suggests nonlinear structure. Not explored further.
10. **Feature group ablation ordering** — Loss > Risk > Similarity > Dominance > Salience > Skewness.

### Needs More Validation

11. **ev_max_conflict divergence explanation** — Experience hypothesis untested.
12. **Graph community structure** — No community detection run.
13. **Individual differences** — Not yet analyzed (spec 015 proposed).
14. **Causal interpretation** — All findings correlational.
15. **Statistical significance of graph density** — No formal null model test.

---

## 3. Observed Facts

These are empirical measurements, not interpretations:

- Corr(ev_diff, bRate) = −0.63 in choices13k
- Corr(ev_diff, mean_choice_B) = −0.72 in CPC18
- 1,562 choices13k problems appear under two conditions (feedback × block confounded)
- 148/270 CPC18 problems are exactly normalizable; 122 use empirical reconstruction
- All choices13k probabilities sum to 1.0 (zero violations)
- CPC18 empirical reconstruction mean EV error: A=0.12, B=0.33
- Block 1 = no feedback, blocks 2–5 = feedback (universal in CPC18)
- 6/8 logistic coefficients share sign across datasets
- ev_max_conflict coefficient: positive in choices13k, negative in CPC18
- Feature hub ranking: ev_favored_has_loss (0.379) > ambiguity (0.329) > ev_max_conflict (0.316) > loss_asymmetry (0.284) > ... > any_dominance (0.004)

---

## 4. Interpretations (supported but not proven)

- "Loss in the EV-favored option drives EV failure" — supported by coefficient, AUC gain, graph hub, cross-dataset replication. But correlation ≠ causation.
- "Dominance detection is a cognitive competence" — supported by 0.4% failure rate and 100% EV-agreement. But could reflect problem simplicity rather than active detection.
- "Feedback resolves informational uncertainty" — supported by −9.5pp ambiguity shift and −9.8pp complexity shift. But confounded with experience/time.
- "Anti-learning reflects max-value reinforcement" — supported by ev_max_conflict concentration. But mechanism not directly observed.
- "EV-failure problems form a structural type" — supported by 1.9× density. But graph is built from engineered features.

---

## 5. Hypotheses (untested)

- A hierarchy of heuristics governs choice (EV-tracking > loss-avoidance > max-attraction > ambiguity response)
- Graph community structure corresponds to distinct cognitive failure modes
- Individual differences in loss sensitivity explain anti-learning
- Graph embeddings would improve prediction beyond flat features
- The ev_max_conflict divergence reflects experience resolving initial max attraction

---

## 6. Limitations

| Limitation | Impact | Mitigation |
|-----------|--------|-----------|
| Block/feedback confound | Cannot separate experience from information | Acknowledge; note that main jump is at feedback onset |
| Scale imbalance (13K vs 270) | CPC18 breakdowns have small cells | Report confidence intervals; focus on convergent patterns |
| Empirical reconstruction (122 problems) | Outcome distributions are approximate | Report EV error bounds; note 148 exact problems replicate patterns |
| No causal identification | All findings correlational | Frame as predictive, not causal; propose experiments |
| Graph from engineered features | Circularity risk | Acknowledge; graph confirms but doesn't independently discover |
| No individual-level data (choices13k) | Cannot study strategies | Defer to CPC18 individual analysis (spec 015) |
| No formal null model for graph | Density ratio is descriptive | Propose permutation test as future work |
| Multiple comparisons | Inflated false positives | Focus on convergent cross-dataset patterns |
| Arbitrary k=10 | Topology may change | Mention as limitation; sensitivity analysis as future work |

---

## 7. What Remains Before Manuscript

| Task | Status | Blocking? |
|------|--------|-----------|
| Decide target venue | Not done | Yes |
| Decide main claim (A, B, or C) | Not done | Yes |
| Choose 6–8 final figures | Not done | Yes |
| Generate publication-quality figures | Not done | Yes |
| Write methods (normalization details) | Not done | Yes |
| Write limitations section | Not done | Yes |
| Write abstract | Not done | Yes |
| Formal significance test for graph clustering | Not done | No |
| Sensitivity analysis on k | Not done | No |
| Individual differences analysis (spec 015) | Not done | No |
| Decide on supplementary materials | Not done | No |

---

## 8. Venue Considerations

| Venue Type | Pros | Cons |
|-----------|------|------|
| Cognitive Science (CogSci, Cognition) | Natural audience, values cross-dataset | May want individual-level modeling |
| Decision Research (JDM, JBDM) | Core topic, values large-N | May want prospect theory framing |
| Computational (CogSci proceedings, NeurIPS workshop) | Values methodology, graph approach | Shorter format, less room for nuance |
| Interdisciplinary (PNAS, Nature Human Behaviour) | High impact, broad audience | Very competitive, needs strong causal story |

Recommendation: Target a decision research journal (JDM or Cognition) with the loss-centered claim (Claim A). The multi-mechanism story (Claim B) works as a longer paper. The methodological angle (Claim C) fits a computational venue.
