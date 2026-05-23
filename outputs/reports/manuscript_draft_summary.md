# Manuscript Draft Summary

**Spec**: 022 — Write Decision Manuscript Draft
**Date**: 2026-05-06
**Status**: First draft complete, compiles successfully.

---

## Word Count by Section

| Section | Estimated Words |
|---------|---------------:|
| Abstract | 190 |
| Introduction | 1,200 |
| Method | 1,800 |
| Results | 2,200 |
| Discussion | 1,500 |
| Limitations | 650 |
| Conclusion | 250 |
| **Total** | **~7,800** |

Target range: 6,000–8,000 words. ✓ Within target.

---

## Figures Referenced

| Figure | Label | Description |
|--------|-------|-------------|
| 1 | fig:ev_failure_rates | EV failure rates across datasets and metrics |
| 2 | fig:loss_dominance | Loss and dominance effects on EV failure |
| 3 | fig:feature_ablation | Feature ablation performance |
| 4 | fig:learning_dynamics | CPC18 learning dynamics |
| 5 | fig:graph_clustering | Graph EV-failure clustering |
| 6 | fig:example_problems | Cross-dataset structural bridge example |

Total: **6 figures** (all included and referenced).

---

## Tables Referenced

| Table | Label | Description |
|-------|-------|-------------|
| 1 | tab:dataset_summary | Dataset characteristics |
| 2 | tab:feature_ablation | Predictive performance by feature configuration |
| 3 | tab:key_results | Summary of key results |

Total: **3 tables** (all filled with data).

---

## References Cited

| Key | Authors | Year |
|-----|---------|------|
| kahneman1979prospect | Kahneman & Tversky | 1979 |
| tversky1992advances | Tversky & Kahneman | 1992 |
| yechiam2013loss | Yechiam & Hochman | 2013 |
| peterson2021science | Peterson et al. | 2021 |
| bourgin2019icml | Bourgin et al. | 2019 |
| erev2017psychreview | Erev et al. | 2017 |
| plonsky2019zenodo | Plonsky et al. | 2019 |
| plonsky2019jbdm | Plonsky et al. | 2019 |

Total: **8 references**.

---

## Compilation Status

- **Tool**: pdflatex + bibtex (latexmk not available)
- **Command**: `pdflatex → bibtex → pdflatex → pdflatex`
- **Result**: ✓ Successful. 28 pages, 286 KB PDF.
- **Errors**: None.
- **Undefined references**: None.
- **Warnings**: apa7 class deprecation notice about `\authorsaffiliations` (cosmetic only, does not affect output).

---

## Known Gaps and TODOs

1. **ORCID and correspondence**: Placeholder in main.tex (commented out).
2. **Author note**: Not yet written (standard for first draft).
3. **Supplementary materials**: Not prepared (could include full feature list, per-GameID learning data).
4. **Formal significance tests**: Graph density enrichment lacks permutation test (noted in Limitations).
5. **Figure quality check**: Figures are linked from `outputs/figures/publication/` — verify PDF quality before submission.
6. **Bibliography style**: Using `apalike` as fallback; `apacite` would be more APA-compliant but requires texlive-bibtex-extra.
7. **Page numbers in references**: Some entries may need page number verification (marked in .bib).
8. **Makefile**: Uses latexmk which is not installed; compilation works via manual pdflatex+bibtex cycle.

---

## Main Claim

EV failures are systematic, organized around loss exposure, protected by dominance, partially corrected by experience, and clustered in a cross-dataset graph.

---

## Files Modified

```
manuscript/main.tex                        (added abstract to preamble, included tables/figures)
manuscript/sections/00_title_abstract.tex   (abstract moved to preamble)
manuscript/sections/01_introduction.tex     (full prose)
manuscript/sections/02_method.tex           (full prose)
manuscript/sections/03_results.tex          (full prose)
manuscript/sections/04_discussion.tex       (full prose)
manuscript/sections/05_limitations.tex      (full prose)
manuscript/sections/06_conclusion.tex       (full prose)
manuscript/tables/tab1_dataset_summary.tex  (filled)
manuscript/tables/tab2_feature_ablation.tex (filled)
manuscript/tables/tab3_key_results.tex      (filled)
manuscript/references.bib                   (added 3 references)
```
