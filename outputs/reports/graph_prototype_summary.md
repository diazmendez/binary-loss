# Graph Prototype Summary (Spec 014)

## Node Counts by Label

| Label | Count |
|-------|-------|
| Dataset | 2 |
| Problem | 14838 |
| Option | 29676 |
| Outcome | 84272 |
| Feature | 9 |
| **Total** | **128797** |

## Edge Counts by Type

| Type | Count |
|------|-------|
| CONTAINS | 14838 |
| HAS_OPTION | 29676 |
| HAS_OUTCOME | 84272 |
| HAS_FEATURE | 43763 |
| SIMILAR_PROBLEM | 148380 |
| **Total** | **320929** |

## Feature Node Degree

| Feature | Degree (problems with feature=True) |
|---------|--------------------------------------|
| ev_favored_has_loss | 6341 |
| any_dominance | 2506 |
| ev_max_conflict | 6004 |
| has_safe_option_A | 8320 |
| has_safe_option_B | 245 |
| salience_conflict | 4906 |
| ambiguity | 2849 |
| ev_risk_conflict | 7150 |
| loss_asymmetry | 5442 |

## EV Failure Clustering in Similarity Graph

| Metric | Observed | Random Baseline |
|--------|----------|-----------------|
| Both EV-failure | 0.1254 | 0.0586 |
| Both EV-consistent | 0.6396 | 0.5745 |
| Cross-type | 0.2350 | 0.3669 |

EV-failure problems **do** cluster together in the similarity graph (observed 0.1254 vs random baseline 0.0586).

## Cross-Dataset Similarity Edges

- Cross-dataset edges (choices13k ↔ CPC18): **1538** / 148380 (1.0%)

## Connected Components (Similarity Graph)

- Number of components: **1**
- Largest component size: **14838** nodes
- Both datasets in largest component: **Yes**

## Basic Graph Statistics

- Nodes in similarity graph: **14838**
- Edges in similarity graph: **97529**
- Average degree: **13.15**
- Max degree: **29**
- Min degree: **10**

## Limitations and Next Steps

- Similarity is based on 15 features; richer representations may yield different topology.
- k=10 is arbitrary; sensitivity analysis on k could reveal structure changes.
- Outcome nodes are numerous (~84K); future work may aggregate or sample.
- No graph ML or GNN applied — this is a structural prototype only.
- Cypher script is untested against a live Neo4j instance.
