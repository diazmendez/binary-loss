# Manuscript Major Revision Summary

**Spec**: 024B — Theory and Manuscript Major Revision
**Date**: 2026-05-06
**Status**: Complete. Compiles successfully (31 pages, 298 KB).

---

## Changes Made

### Theoretical Reframing
- Distinguished three levels of loss sensitivity: outcome-level loss aversion (prospect theory), option-level loss attention (Yechiam & Hochman 2013), and binary loss presence (this paper's finding)
- Added testable prediction: if classical loss aversion drives EV failure, continuous measures should outperform binary; data show the opposite
- Framed contribution as evidence for loss attention over classical loss aversion

### Literature Expansion
- References expanded from 8 to 19
- Added: Brandstätter et al. 2006 (priority heuristic), Hertwig et al. 2004 (description-experience gap), Bordalo et al. 2012 (salience theory), Loomes & Sugden 1982 (regret theory), Birnbaum 2008 (configural weight/TAX), Gonzalez & Dutt 2011 (instance-based learning), Erev et al. 2010 (CPC2015), Wulff et al. 2018 (D-E gap meta-analysis), Fehr-Duda & Epper 2012 (probability weighting), Gigerenzer & Gaissmaier 2011 (heuristic decision making), Rieskamp 2008 (SSL model)

### Inferential Statistics Incorporated
- EV failure rates now reported with 95% Wilson CIs
- Controlled regression results: ev_favored_has_loss β=0.84 [0.80, 0.88] after controlling for probability and magnitude
- Dominance control: β=−1.51 [−1.70, −1.37] after controlling for ev_abs_diff
- Graph permutation test: p < .001, observed 0.125 vs null 0.061
- Cross-transfer AUC with CI: 0.79 [0.64, 0.81]
- Binary vs continuous AUC comparison in new Table 4

### Dominance Reframing
- Removed "cognitive competence" language
- Replaced with: "Dominance defines a structurally clear regime where EV failure is rare"
- Added ev_abs_diff control result showing dominance is not merely problem easiness

### Graph Reframing
- Now framed as "convergent structural evidence" not central claim
- Permutation test result leads the subsection
- Circularity explicitly acknowledged
- Subsection shortened

### Learning/Feedback Language
- Subsection renamed "Changes Across Blocks"
- Confound caveat placed at start of subsection
- "Anti-learning" replaced with "experience-associated worsening"
- No causal claims about feedback

### Scope
- Introduction clearly states loss exposure is primary finding
- Dominance, experience, graph are supporting analyses
- Conclusion centered on loss exposure

### Abstract
- Opens with puzzle: "Why do people reject options that maximize expected value?"
- Includes binary vs continuous AUC comparison
- Includes permutation test result
- Includes controlled regression β with CI

### Data/Code Availability
- Added to Method section with URLs for choices13k and CPC18
- Placeholder for analysis code repository

---

## Compilation

- **Tool**: pdflatex + bibtex
- **Result**: ✓ 31 pages, 298 KB, zero errors, zero undefined references
- **Note**: Fixed apa7 multiple-affiliation issue by combining into single \affiliation command

---

## Word Count Estimates

| Section | ~Words |
|---------|-------:|
| Abstract | 200 |
| Introduction | 1,400 |
| Method | 1,900 |
| Results | 2,400 |
| Discussion | 1,700 |
| Limitations | 600 |
| Conclusion | 280 |
| **Total** | **~8,500** |

Target: 7,000–9,000. ✓ Within range.

---

## Tables and Figures

- 4 tables (added Table 4: binary vs continuous loss comparison)
- 6 figures (unchanged)
- 19 references (up from 8)

---

## Reviewer Concerns Addressed

All 10 required revisions from the internal review (spec 023) have been addressed. See `outputs/tables/manuscript_revision_response_matrix.csv` for the full mapping.
