# Data Analysis for Paper 1

Paper: **Binary Loss Presence Predicts Expected-Value Failures Across Description- and Experience-Based Risky Choice**

This folder contains the reproducible analysis package for Paper 1. It is a curated copy of the validated code and derived outputs used for the Decision manuscript. Raw data are intentionally not included here.

## What This Folder Is

`data-analysis/` is the paper-specific analysis record:

- `scripts/` contains the code used to normalize data, build features, run Paper 1 analyses, generate figures, and produce robustness checks.
- `data/interim/` contains derived parquet files generated from the raw datasets.
- `outputs/` contains validated reports, tables, and figures used by the manuscript or its supplement/limitations.
- `src/` contains the small shared Python package copied with the paper for reproducibility.
- `pyproject.toml` records the Python package dependencies used by the project.

The current manuscript source is in:

```text
../paper/
```

## Raw Data

Raw data are **not copied** into this paper package.

The original local raw data remain at repository root:

```text
data/raw/
```

Expected raw sources:

- `data/raw/choices13k/c13k_problems.json`
- `data/raw/choices13k/c13k_selections.csv`
- `data/raw/cpc18/all_CPC18_raw_data.csv`
- `data/raw/cpc18/CPC18_dictionary.pdf`

Public source links:

- choices13k: https://github.com/jcpeterson/choices13k
- CPC18: https://zenodo.org/records/2571510

Do not modify raw data.

## Derived Data

`data/interim/` contains six derived parquet files:

- `choices13k_common.parquet`  
  Normalized choices13k rows in the common representation. Includes dataset metadata, problem IDs, conditions, JSON-encoded option/outcome distributions, and aggregate B-choice rates.

- `choices13k_features.parquet`  
  Basic EV/max/min/risk-relevant features computed from the common representation.

- `choices13k_advanced_features.parquet`  
  Additional loss, risk, skewness, dominance, salience, and similarity features.

- `cpc18_common.parquet`  
  CPC18 GameID-level common representation. Includes exact reconstructions for simple games and empirical payoff-frequency reconstructions for complex games.

- `cpc18_features.parquet`  
  Basic features for CPC18.

- `cpc18_advanced_features.parquet`  
  Advanced features for CPC18.

These files are derived artifacts, not raw data. Recreate them only through the normalization/feature scripts if a deliberate reproduction pass is needed.

## Script Map

### Dataset Inspection and Normalization

- `inspect_datasets.py`  
  Produces dataset inventory summaries.

- `check_choices13k.py`  
  Performs initial checks on choices13k data.

- `normalize_choices13k.py`  
  Converts choices13k into the common representation and computes basic features.

- `normalize_cpc18.py`  
  Converts CPC18 into the common representation, including exact and empirical reconstruction paths.

- `build_advanced_features.py`  
  Computes the advanced feature set for choices13k and CPC18.

### Main Paper 1 Analyses

- `analyze_choices13k_ev_failures.py`  
  Characterizes EV failure in choices13k.

- `compare_choices13k_cpc18_ev_failures.py`  
  Compares EV failure across choices13k and CPC18.

- `analyze_predictive_feature_ablation.py`  
  Runs the feature-ablation predictive models used for the Paper 1 model-performance claims.

- `run_revision_inference.py`  
  Produces inferential statistics added during revision: CIs, controlled loss regressions, binary-vs-continuous loss comparisons, dominance controls, and graph permutation checks.

### CPC18 Experience / Block Checks

- `analyze_cpc18_learning_dynamics.py`  
  Produces block/trial-level CPC18 descriptive analyses.

- `run_cpc18_clustered_trial_check.py`  
  Runs the clustered/GEE robustness check for the CPC18 block-related decline.

### Figures

- `make_publication_figures.py`  
  Generates publication-ready figure assets used by the Decision manuscript.

### Supplementary / Robustness Graph Checks

These scripts are not central graph-first claims. They are retained because Paper 1 references graph/matching only as supplementary robustness or limitation material.

- `export_graph_prototype.py`
- `run_graph_exploration.py`
- `run_graph_validation_audit.py`

Do not use these to revive graph-first Paper 2 claims inside Paper 1.

## Outputs

### `outputs/reports/`

Important reports:

- `dataset_inventory.md`  
  Dataset inventory.

- `choices13k_feature_summary.md`, `cpc18_normalization_summary.md`, `advanced_feature_summary.md`  
  Normalization and feature summaries.

- `choices13k_ev_failure_analysis.md`, `cross_dataset_ev_failure_comparison.md`  
  EV-failure result summaries.

- `predictive_feature_ablation.md`  
  Main predictive model/feature-ablation results.

- `revision_inference_results.md`  
  Controlled regression and inferential statistics supporting the binary-loss claim.

- `cpc18_learning_dynamics.md`, `cpc18_clustered_trial_check.md`  
  CPC18 block and clustered robustness checks.

- `paper1_trackF_consistency_check.md`  
  Matching/graph caveat used in limitations.

- `paper1_pre_submission_theory_refinement_report.md`, `paper1_decision_submission_compliance_report.md`, `paper1_decision_length_trim_report.md`  
  Manuscript-preparation reports.

### `outputs/tables/`

Important tables:

- `revision_loss_binary_vs_continuous.csv`  
  Binary-vs-continuous loss comparison.

- `revision_loss_exposure_controls.csv`  
  Controlled loss regression results.

- `revision_dominance_control_models.csv`  
  Dominance control models.

- `revision_inference_key_stats.csv`  
  Key rates, CIs, and AUC summaries.

- `feature_ablation_model_comparison.csv`, `feature_group_importance.csv`, `top_predictive_features.csv`  
  Predictive feature-ablation results.

- `cpc18_block_level_choice.csv`, `cpc18_trial_level_ev_consistency.csv`, `cpc18_clustered_trial_model.csv`  
  CPC18 block/trial summaries and clustered model output.

- `graph_matched_counterfactuals.csv`, `graph_results_validated_claims.csv`, `graph_results_risk_register.csv`  
  Supplementary matching/graph audit outputs used only for caveats.

### `outputs/figures/`

Main manuscript figure assets:

- `fig1_ev_failure_rates.pdf/.png`
- `fig2_loss_dominance_effects.pdf/.png`
- `fig3_feature_ablation.pdf/.png`
- `fig4_learning_dynamics.pdf/.png`

Supplementary or legacy Paper 1 figure assets:

- `fig5_graph_clustering.pdf/.png`
- `fig6_cross_dataset_bridge.pdf/.png`
- exploratory PNGs such as `cross_dataset_ev_failure_rates.png`, `feature_ablation_performance.png`, and CPC18 block plots.

## Suggested Reproduction Order

Only run this if intentionally reproducing the paper package.

```bash
python scripts/inspect_datasets.py
python scripts/normalize_choices13k.py
python scripts/normalize_cpc18.py
python scripts/build_advanced_features.py
python scripts/analyze_choices13k_ev_failures.py
python scripts/compare_choices13k_cpc18_ev_failures.py
python scripts/analyze_cpc18_learning_dynamics.py
python scripts/analyze_predictive_feature_ablation.py
python scripts/run_revision_inference.py
python scripts/run_cpc18_clustered_trial_check.py
python scripts/make_publication_figures.py
```

Graph/matching checks are supplementary and should be run only if specifically auditing those limitations.

## What Not To Change Casually

- Do not modify raw data.
- Do not overwrite validated outputs unless performing a deliberate reproduction pass.
- Do not add Paper 1.5 transfer outputs here.
- Do not reframe graph outputs as central Paper 1 claims.
- Do not change numerical results without updating the manuscript and reports together.

## Current Relationship to the Manuscript

The manuscript uses the results in this folder to support:

- binary loss presence versus continuous loss probability/magnitude
- cross-dataset replication between choices13k and CPC18
- dominance as a protective structural regime
- CPC18 block/feedback descriptive results
- limitations on causality, reconstruction, nesting, and matching

