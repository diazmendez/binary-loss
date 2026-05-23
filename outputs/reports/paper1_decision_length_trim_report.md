# Paper 1 Decision Shorter Article Length Trim Report

Date: 2026-05-23

## Scope

Paper 1 only. No new analyses were run, no raw data were modified, no validated numerical results were changed, no Paper 1.5 material was added, and graph-first Paper 2 claims were not revived.

## Page Count Method

Page count was estimated from the compiled PDF using section starts extracted from `pdftotext` and the LaTeX log. I used a conservative submission-oriented count: title/author note/abstract plus manuscript text through the conclusion, excluding references, tables, and figures.

## Before Trimming

Before this trim pass:
- Total PDF pages: 27
- References began on page 18
- Tables began on page 20
- Figures began on page 24
- Conservative text count excluding references/tables/figures: pages 1--17 = **17 pages**
- Body text excluding title/author note/abstract: approximately pages 4--17 = **14 pages**

Conclusion: under a conservative interpretation that includes front matter, the manuscript exceeded the 15-page shorter-article limit by about 2 pages.

## After Trimming

After trimming:
- Total PDF pages: 25
- References begin on page 16
- Tables begin on page 18
- Figures begin on page 22
- Conservative text count excluding references/tables/figures: pages 1--15 = **15 pages**
- Body text excluding title/author note/abstract: approximately pages 4--15 = **12 pages**

Conclusion: the manuscript now fits the 15-page shorter-article limit under the conservative count.

## Sections Shortened

### Front Matter

- Condensed Author Note language while preserving article type positioning, affiliations, correspondence placeholder, data/materials/code availability, ethics statement, prior dissemination placeholder, COI/funding placeholders, and CRediT placeholder.
- Tightened the abstract slightly without changing numerical results or interpretation.

### Introduction

- Shortened the opening motivation.
- Compressed the literature review listing theories and citations.
- Condensed the Present Work paragraph.
- Preserved the theoretical positioning paragraph and the no-formal-model-comparison caveat.

### Method

- Shortened feature-construction prose.
- Tightened the Data and Code Availability statement.
- Preserved ethics/secondary-data language and all analysis descriptions.

### Discussion

- Reduced repeated theory lists.
- Shortened Cross-Dataset Generalization, Experience-Associated Changes, Relation to Prior Work and Future Directions, and Practical Implications.
- Preserved the central theoretical interpretation and causal caution.

### Limitations

- Tightened caveats while preserving required content:
  - no formal model comparison
  - no causal identification
  - structural confounding/matching caveat
  - block/feedback confound
  - trial-level nesting
  - reconstruction sensitivity
  - graph analysis as exploratory/feature-derived
  - constraints on generality

### Conclusion

- Reduced repetition of headline statistics already reported in Results and Abstract.
- Preserved the core claim and the need for formal model comparison, causal experiments, and individual-differences work.

## Required Decision Compliance Items

All required items remain present:

- Author Note: **present**
- Data/code availability in Author Note: **present**
- Data/code availability at end of Method: **present**
- Ethics/secondary data statement: **present**
- CRediT placeholders: **present**
- Constraints on Generality subsection: **present**
- Causality limitation: **present**
- Block/feedback confound: **present**
- No formal model comparison caveat: **present**
- Five keywords maximum: **still present from prior pass**

## Compilation

Command:
`make` in `manuscript/`

Result:
- `manuscript/main.pdf` compiled successfully.
- Total pages: 25.
- No fatal LaTeX errors.
- No unresolved rerun/reference warnings after the final `latexmk` pass.

## Remaining Warning

One existing table-layout warning remains:
- `Overfull \hbox (89.98938pt too wide) in main.ttt lines 6--15`

This is associated with the end-matter table layout and was not introduced by the length trim.

## Build Artifact Cleanup

Removed regenerated untracked LaTeX build artifacts:
- `manuscript/main.fdb_latexmk`
- `manuscript/main.fls`

## Remaining Human Inputs

The length is now compliant, but the Author Note still needs final human values for:
- corresponding author email
- prior dissemination
- conflict of interest
- funding
- final CRediT role assignment
- final public code repository/release status
