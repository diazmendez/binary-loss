# Figure Captions

## Figure 1: EV Failure Rates Across Datasets and Metrics

Expected value failure rates across datasets and metrics. Problem-level rates reflect whether EV predicts the majority choice; trial-level rates reflect individual choice deviations. Hatched bars indicate trial-level metrics. CPC18 problem-level rate (17.6%) is lower partly because it aggregates across learning trials.

## Figure 2: Loss and Dominance Effects on EV Failure

Effect of loss exposure and stochastic dominance on EV failure. (a) When the EV-favored option contains losses, failure rates increase dramatically in both datasets. (b) When stochastic dominance is present, EV failure is near zero, indicating reliable dominance detection.

## Figure 3: Feature Ablation Performance

Predictive performance by feature configuration. Loss features provide the largest single improvement (+0.14 AUC over Basic). Cross-dataset transfer (trained on choices13k, tested on CPC18) confirms generalization. Dashed line shows gradient boosting ceiling.

## Figure 4: CPC18 Learning Dynamics

Trial-level EV failure rate across learning blocks in CPC18. Block 1 has no feedback; blocks 2–5 include outcome feedback (dotted line marks onset). Ambiguous problems show the largest learning shift. Overall improvement is 4.7 percentage points.

## Figure 5: Graph EV-Failure Clustering

Structural clustering of EV-failure problems in the similarity graph. (a) EV-failure problems form a 1.9× denser subgraph than EV-consistent problems. (b) Feature nodes ranked by EV-failure enrichment; dashed line shows the base rate (24.2%). Loss-related features dominate.

## Figure 6: Cross-Dataset Structural Bridge

A choices13k problem and a CPC18 problem with near-identical feature structure (similarity = 0.997) are both EV-failure cases. Both share loss exposure in the EV-favored option, illustrating how the same structural pattern drives failure across independent datasets.
