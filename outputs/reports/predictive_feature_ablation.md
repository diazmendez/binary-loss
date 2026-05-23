# Predictive Feature Ablation

Generated: 2026-05-05 13:39 UTC

## Overview

Systematic ablation evaluating whether advanced cognitive/risk features
improve prediction of EV failure beyond EV-only and basic baselines.
Target: binary EV failure (majority choice contradicts EV prediction).

## Evaluation Protocol

- choices13k: 5-fold stratified CV (N=14,075 after excluding EV ties)
- CPC18: 10-fold stratified CV (N=256, **results unstable**)
- Cross-transfer: train on choices13k, test on CPC18
- NaN handling: features with >50% NaN excluded; remaining NaN imputed with 0
- Models: L2-regularized logistic regression (primary), gradient boosting (ceiling)

## Results: choices13k

| Config | N Features | Accuracy | Bal. Acc | ROC AUC | F1 |
|--------|-----------|----------|---------|---------|-----|
| EV-only | 2 | 0.7511 | 0.5000 | 0.6712 | 0.0000 |
| Basic | 9 | 0.7537 | 0.5188 | 0.6461 | 0.0935 |
| Basic+Risk | 19 | 0.7544 | 0.5409 | 0.7057 | 0.1902 |
| Basic+Loss | 24 | 0.7979 | 0.6594 | 0.7891 | 0.4857 |
| Basic+Dominance | 12 | 0.7542 | 0.5154 | 0.6879 | 0.0745 |
| Basic+Salience | 18 | 0.7448 | 0.5161 | 0.6781 | 0.1059 |
| Basic+Similarity | 13 | 0.7534 | 0.5471 | 0.7248 | 0.2159 |
| Basic+Skewness | 17 | 0.7477 | 0.5227 | 0.6771 | 0.1284 |
| Full | 58 | 0.8090 | 0.6873 | 0.8373 | 0.5368 |

### Gradient Boosting Ceiling

| Config | Accuracy | ROC AUC |
|--------|----------|---------|
| EV-only | 0.7505 | 0.6742 |
| Basic | 0.7904 | 0.8258 |
| Full | 0.8306 | 0.8791 |

### Top 20 Features (Full Model, Standardized Coefficients)

| Rank | Feature | Coef | Group |
|------|---------|------|-------|
| 1 | ev_favored_has_loss | 1.6219 | loss |
| 2 | ev_abs_diff | -0.7293 | basic |
| 3 | B_dominates_A | -0.6696 | dominance |
| 4 | any_dominance | -0.6441 | dominance |
| 5 | std_A | 0.5508 | risk |
| 6 | std_B | 0.5417 | risk |
| 7 | has_loss_B | -0.5266 | loss |
| 8 | both_have_loss | -0.5231 | loss |
| 9 | ev_max_conflict | 0.5144 | basic |
| 10 | any_loss | -0.4678 | loss |
| 11 | has_loss_A | -0.4115 | loss |
| 12 | ambiguity | 0.3189 | basic |
| 13 | variance_A | -0.3153 | risk |
| 14 | variance_B | -0.3091 | risk |
| 15 | ev_diff | 0.2903 | basic |
| 16 | prob_worst_outcome_B | 0.2374 | salience |
| 17 | prob_best_outcome_B | 0.2332 | salience |
| 18 | prob_loss_A | 0.1770 | loss |
| 19 | downside_distance_A | 0.1756 | skewness |
| 20 | range_overlap | -0.1736 | similarity |

## Results: CPC18 (⚠️ N=256, unstable)

| Config | N Features | Accuracy | Bal. Acc | ROC AUC | F1 |
|--------|-----------|----------|---------|---------|-----|
| EV-only | 2 | 0.8242 | 0.5000 | 0.7870 | 0.0000 |
| Basic | 9 | 0.8242 | 0.5175 | 0.5838 | 0.0816 |
| Basic+Risk | 19 | 0.8164 | 0.5390 | 0.6496 | 0.1754 |
| Basic+Loss | 24 | 0.8164 | 0.5390 | 0.6796 | 0.1754 |
| Basic+Dominance | 12 | 0.8320 | 0.5310 | 0.6804 | 0.1224 |
| Basic+Salience | 18 | 0.8086 | 0.5167 | 0.6370 | 0.1091 |
| Basic+Similarity | 13 | 0.7891 | 0.4962 | 0.7462 | 0.0690 |
| Basic+Skewness | 17 | 0.8086 | 0.5167 | 0.6101 | 0.1091 |
| Full | 58 | 0.8125 | 0.6590 | 0.8039 | 0.4419 |

## Results: Cross-Dataset Transfer

*Train on choices13k → Test on CPC18*

| Config | N Features | Accuracy | Bal. Acc | ROC AUC | F1 |
|--------|-----------|----------|---------|---------|-----|
| EV-only | 2 | 0.8242 | 0.5000 | 0.7685 | 0.0000 |
| Basic | 9 | 0.8047 | 0.4969 | 0.5784 | 0.0385 |
| Basic+Risk | 19 | 0.8008 | 0.5295 | 0.6478 | 0.1639 |
| Basic+Loss | 24 | 0.8086 | 0.6042 | 0.6934 | 0.3467 |
| Basic+Dominance | 12 | 0.8164 | 0.4953 | 0.6602 | 0.0000 |
| Basic+Salience | 18 | 0.7812 | 0.4827 | 0.6234 | 0.0345 |
| Basic+Similarity | 13 | 0.7852 | 0.5288 | 0.7239 | 0.1791 |
| Basic+Skewness | 17 | 0.8125 | 0.5279 | 0.6097 | 0.1429 |
| Full | 58 | 0.8047 | 0.6630 | 0.7860 | 0.4444 |

## Feature Group Importance

Marginal gain over Basic configuration:

| Dataset | Group | Accuracy Gain | AUC Gain | N Features |
|---------|-------|--------------|----------|-----------|
| choices13k | risk | +0.0006 | +0.0596 | 10 |
| choices13k | loss | +0.0441 | +0.1430 | 15 |
| choices13k | dominance | +0.0004 | +0.0418 | 3 |
| choices13k | salience | -0.0089 | +0.0320 | 9 |
| choices13k | similarity | -0.0004 | +0.0787 | 4 |
| choices13k | skewness | -0.0060 | +0.0310 | 8 |
| cpc18 | risk | -0.0078 | +0.0658 | 10 |
| cpc18 | loss | -0.0078 | +0.0958 | 15 |
| cpc18 | dominance | +0.0078 | +0.0966 | 3 |
| cpc18 | salience | -0.0156 | +0.0532 | 9 |
| cpc18 | similarity | -0.0352 | +0.1624 | 4 |
| cpc18 | skewness | -0.0156 | +0.0263 | 8 |

## Interpretation

- EV-only AUC: 0.6712 → Basic: 0.6461 → Full: 0.8373
- Advanced features add 19.12 AUC points over Basic in choices13k.
- ev_favored_has_loss coefficient: 1.6219 (confirms importance)
- any_dominance coefficient: -0.6441 (negative = protects against failure)
- Most valuable group (choices13k): loss (+0.1430 AUC)
- Cross-transfer: Basic AUC=0.5784, Full AUC=0.7860

## Limitations

- CPC18 N=256 — all results unstable, wide confidence intervals.
- NaN handling (impute with 0) affects skewness/cv features.
- Cross-transfer assumes comparable problem spaces.
- Logistic regression assumes linear feature effects.
- No causal interpretation — correlational only.
- Gradient boosting ceiling may overfit on small datasets.

## Assumptions

1. EV failure is a meaningful binary target.
2. Standardized coefficients are comparable across features.
3. L2 regularization prevents overfitting in logistic regression.
4. Features with >50% NaN are uninformative and safely excluded.
