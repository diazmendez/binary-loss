# Graph Exploration Summary (Spec 018)

Generated: 2026-05-06 06:48

## Q1: Feature Nodes × EV Failure

| Feature | Total Degree | EV-Failure Degree | EV-Failure Fraction | Group |
|---------|-------------|-------------------|--------------------:|-------|
| ev_favored_has_loss | 6341 | 2405 | 0.3793 | loss |
| ambiguity | 2849 | 936 | 0.3285 | ambiguity |
| ev_max_conflict | 6004 | 1899 | 0.3163 | conflict |
| loss_asymmetry | 5442 | 1547 | 0.2843 | loss |
| has_safe_option_B | 245 | 66 | 0.2694 | safety |
| ev_risk_conflict | 7150 | 1687 | 0.2359 | conflict |
| has_safe_option_A | 8320 | 1784 | 0.2144 | safety |
| salience_conflict | 4906 | 688 | 0.1402 | conflict |
| any_dominance | 2506 | 11 | 0.0044 | dominance |

**Key insight**: `ev_favored_has_loss` has the highest EV-failure fraction (0.379), confirming its role as the strongest graph-structural predictor of EV failure.

## Q2: EV-Failure Subgraph Density

| Subgraph | Nodes | Internal Edges | Density |
|----------|-------|---------------|---------|
| EV-failure | 3591 | 36740 | 0.002850 |
| EV-consistent | 11247 | 188410 | 0.001490 |

EV-failure subgraph is **1.9×** denser than EV-consistent subgraph, confirming that failure problems are more interconnected.

## Q3: Cross-Dataset Similarity

Found **50** choices13k problems with ≥2 CPC18 neighbors.

Top 10:
| Problem ID | EV Diff | B Rate | EV Failure | CPC18 Neighbors | Max Sim |
|-----------|---------|--------|-----------|----------------|---------|
| 11978 | 0.150 | 0.675 | True | 10 | 0.9870 |
| 7340 | 0.800 | 0.480 | False | 8 | 0.9864 |
| 176 | 0.000 | 0.250 | False | 7 | 0.9619 |
| 12031 | 0.160 | 0.388 | False | 6 | 0.9893 |
| 2027 | -2.500 | 0.421 | True | 6 | 0.9710 |
| 2027 | -2.500 | 0.588 | False | 6 | 0.9710 |
| 3845 | 2.500 | 0.295 | False | 6 | 0.9690 |
| 11635 | 3.350 | 0.062 | False | 5 | 0.9485 |
| 4528 | 1.350 | 0.600 | True | 4 | 0.9968 |
| 8518 | 1.450 | 0.189 | False | 4 | 0.9933 |

## Q4: CPC18 Problems in EV-Failure Neighborhoods

Top 10 CPC18 problems surrounded by choices13k EV-failure problems:
| GameID | CPC EV-Failure | Total Neighbors | Failure Neighbors | Failure Fraction |
|--------|---------------|-----------------|-------------------|-----------------|
| 37 | True | 22 | 22 | 1.000 |
| 19 | False | 5 | 5 | 1.000 |
| 221 | True | 23 | 22 | 0.957 |
| 120 | False | 23 | 21 | 0.913 |
| 263 | True | 11 | 10 | 0.909 |
| 231 | True | 18 | 16 | 0.889 |
| 58 | True | 24 | 20 | 0.833 |
| 20 | False | 5 | 4 | 0.800 |
| 119 | True | 19 | 15 | 0.789 |
| 207 | False | 19 | 15 | 0.789 |

## Q5: Feature-Defined Neighborhood Density

| Feature | Degree | Internal Edges | Internal Density |
|---------|--------|---------------|-----------------|
| has_safe_option_B | 245 | 3642 | 0.060923 |
| any_dominance | 2506 | 49346 | 0.007861 |
| salience_conflict | 4906 | 96364 | 0.004004 |
| loss_asymmetry | 5442 | 98190 | 0.003316 |
| ev_max_conflict | 6004 | 118342 | 0.003283 |
| ev_favored_has_loss | 6341 | 124652 | 0.003101 |
| ev_risk_conflict | 7150 | 130824 | 0.002559 |
| has_safe_option_A | 8320 | 155092 | 0.002241 |
| ambiguity | 2849 | 11494 | 0.001417 |

## Q6: Loss vs Ambiguity vs Conflict as EV-Failure Hubs

| Group | Mean Enrichment | Total Degree | Total Failures |
|-------|----------------|-------------|----------------|
| loss | 0.3318 | 11783 | 3952 |
| ambiguity | 0.3285 | 2849 | 936 |
| safety | 0.2419 | 8565 | 1850 |
| conflict | 0.2308 | 18060 | 4274 |
| dominance | 0.0044 | 2506 | 11 |

**Loss** features are the strongest EV-failure hubs (mean enrichment 0.332).

## Q7: Example Subgraphs

### CPC18 EV-failure problem neighborhood

- Problem: `problem:cpc18:201` (GameID 201, ev_diff=-0.003)
- Features: ['has_safe_option_A']
- Top neighbor: `problem:cpc18:25` (dataset=cpc18, ev_failure=False, sim=1.0000)

### Cross-dataset EV-failure pair

- choices13k: `problem:choices13k:8961` (ev_diff=1.580, features=['ev_favored_has_loss', 'loss_asymmetry', 'ambiguity'])
- CPC18: `problem:cpc18:58` (ev_diff=1.800, features=['ev_favored_has_loss', 'loss_asymmetry'])
- Similarity: 0.9969

## Key Findings

1. The graph reveals structure beyond tabular features: EV-failure problems form a denser subgraph, confirming they share structural properties.
2. Loss-related features are the strongest EV-failure hubs in the graph.
3. Cross-dataset edges exist and connect structurally similar problems across choices13k and CPC18.
4. CPC18 problems surrounded by choices13k EV-failure neighbors tend to be EV-failure themselves.

## Limitations

- k=10 similarity is arbitrary; different k values may change topology.
- Feature nodes are binary (no continuous edge weights).
- Similarity based on 15 features only.
- No graph ML applied — purely structural exploration.

## Next Steps

- Community detection on the similarity graph to identify natural problem types.
- Graph embeddings (node2vec) for downstream prediction.
- Sensitivity analysis on k parameter.
