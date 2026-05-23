# Paper 1 Pre-Submission Theory Refinement Report

Date: 2026-05-23

## Scope

Targeted pre-submission refinement of Paper 1 only. No raw data were modified, no new analyses were run, no Paper 1.5 material was added, and graph-first Paper 2 claims were not revived.

Edited files:
- `manuscript/main.tex`
- `manuscript/sections/01_introduction.tex`
- `manuscript/sections/03_results.tex`
- `manuscript/sections/04_discussion.tex`
- `manuscript/sections/05_limitations.tex`
- `manuscript/sections/06_conclusion.tex`

## Title Options

1. **Binary Loss Presence Predicts Expected-Value Failures Across Description- and Experience-Based Risky Choice**  
   Recommended. Directly names the key predictor, outcome, and cross-format replication.

2. **Binary Loss Presence Predicts Expected-Value Failures Across Large-Scale Risky Choice Datasets**  
   Strong general alternative; slightly less specific about description vs experience.

3. **When Expected Value Fails: Binary Loss Presence Predicts Risky-Choice Deviations Across Datasets**  
   More narrative, still clear.

4. **The Mere Presence of Loss Predicts Expected-Value Failure in Risky Choice**  
   Shorter and punchier, but less explicit about cross-dataset evidence.

5. **Categorical Loss Presence Predicts Expected-Value Failure Across Risky-Choice Paradigms**  
   Theoretically oriented; "categorical" may be slightly more abstract for Decision.

Implemented title:
**Binary Loss Presence Predicts Expected-Value Failures Across Description- and Experience-Based Risky Choice**

## Abstract Changes

The abstract was revised to make the central contribution more direct:

- It now states that the finding is not merely that losses matter.
- It foregrounds the key result: binary loss presence in the EV-favored option predicts EV failure better than loss probability or loss magnitude.
- It explicitly reports replication in CPC18 and cross-dataset generalization from description-based to experience-based choice.
- It frames interpretation as consistent with loss-attention and categorical-cue accounts.
- It explicitly states that the analyses are correlational and do not establish a causal mechanism or formal model comparison against prospect theory or alternatives.

No graph-first language was added.

## Theoretical Positioning Changes

Added a paragraph in the Introduction framing the contribution as a structural constraint on descriptive models of risky choice:

- Models may differ in mechanism: value transformation, sequential comparison, salience weighting, attentional allocation, or experience-based retrieval.
- Models that predict EV failure well should capture the categorical transition associated with the mere presence of a possible loss in the EV-favored option.
- The paragraph relates this constraint to CPT/prospect theory, the priority heuristic, salience theory, and loss-attention accounts.
- It explicitly avoids claiming formal model comparison.

The Discussion was also revised to repeat the same claim more cautiously: the result is a predictive structural constraint, not evidence that any named formal model is refuted.

## Limitations Strengthened

The causal limitation was strengthened substantially:

- All findings are described as correlational and predictive.
- Binary loss presence is acknowledged as potentially entangled with variance, EV gap, outcome count, payoff range, and broader structural properties.
- Controlled regressions and robustness checks are described as supporting incremental diagnostic value, not causal isolation.
- Causal tests are said to require controlled stimulus construction or experiments that manipulate loss presence while holding probability, magnitude, EV gap, and other structural properties fixed.

Matching/graph handling was clarified:

- Graph analysis remains supplementary and feature-derived.
- Matching is described as an exploratory robustness check, not a central result.
- The limitation notes that matched pairs attenuated the raw bRate difference from 0.027 to 0.016 (p = .08, N = 224), reducing but not eliminating concerns about structural confounding.

## Sensitivity Results Already Available

### CPC18 Reconstruction Sensitivity

Available existing evidence:

- `outputs/reports/cpc18_normalization_summary.md` documents 148 exactly normalized CPC18 GameIDs and 122 empirically reconstructed GameIDs.
- The existing manuscript already stated that the 148 exactly normalized problems replicated the same patterns.

Manuscript treatment:

- Kept this as robustness evidence in limitations.
- Softened wording to avoid overclaiming a separate confirmatory analysis from the smaller exact-only subset.

### CPC18 Block Sensitivity

Available existing evidence:

- `outputs/reports/cpc18_clustered_trial_check.md` reports block-level descriptive rates and a GEE clustered by participant.
- The GEE confirms the block-related decline (OR = 0.9504, p < .001), while block and feedback remain perfectly confounded.

Manuscript treatment:

- The block analysis remains descriptive.
- The limitations now explicitly state that block-1 results are sensitivity evidence, not a causal estimate of feedback effects.

## Repetition Reduction

Light repetition was reduced without restructuring:

- The Results section no longer repeats the loss-attention interpretation after the AUC comparison.
- The Discussion cross-dataset paragraph no longer re-emphasizes binary loss exposure unnecessarily.
- The Conclusion was tightened to avoid restating every headline statistic while preserving the main claim.

## Compilation

`manuscript/main.pdf` was compiled successfully with `make` after `apa7.cls` became available.

Build result:
- PDF: `manuscript/main.pdf`
- Pages: 25
- LaTeX errors: none
- Remaining warning: one overfull hbox in the table output (`main.ttt`), already present in the table layout style and not introduced by the theory edits.

Note: installing `texlive-publishers` made `apa7.cls` available, but the system package manager reported a `tex-common` post-install `fmtutil` failure. The manuscript still compiled successfully.

## Remaining Risks

- Title is now direct and Decision-suitable, but authors may prefer the slightly shorter "large-scale datasets" version if the description/experience contrast feels too prominent for the title.
- The exact-only CPC18 reconstruction sensitivity is documented as available, but the current repository evidence appears to be summarized rather than presented as a standalone table in the manuscript.
- Graph matching is now handled as a limitation; reviewers sensitive to graph language may prefer moving the supplementary structural check entirely out of Results.
- The abstract is denser than before because it now includes binary-vs-continuous, replication, transfer, dominance, and causal caveat in one paragraph.
