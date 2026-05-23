# Decision-Focused Slim Revision Summary

**Spec**: 024C — Decision-Focused Slim Revision
**Date**: 2026-05-06
**Status**: Complete. Compiles successfully (24 pages, 222 KB).

---

## Changes from 024B → 024C

| Dimension | Before (024B) | After (024C) |
|-----------|---------------|--------------|
| Pages | 31 | 24 |
| Estimated words | ~8,500 | ~6,500 |
| Main-text figures | 6 | 4 |
| Tables | 4 | 4 |
| References | 19 | 19 |
| Graph emphasis | Full Results subsection + 2 figures | 1 paragraph + supplementary |
| Learning emphasis | Full subsection with anti-learning detail | 1 paragraph, descriptive |
| CPT framing | "More consistent with loss attention than CPT" | No refutation; explicit caveat about no formal model comparison |
| ML language | Some remaining | Replaced with "predictive validation" |
| Feature engineering | Detailed 78-feature description | Compressed to key features + supplementary reference |

---

## Key Structural Changes

1. **Abstract**: Opens with puzzle, centers on binary > probability > magnitude, ends with model comparison caveat.
2. **Introduction**: Trimmed from ~1,400 to ~1,100 words. Removed graph as contribution. Added explicit statement: "We did not perform formal model comparison against CPT, TAX, priority heuristic, or IBL."
3. **Method**: Compressed from ~1,900 to ~1,400 words. Features compressed to key list. Graph reduced to 2 sentences ("exploratory structural analysis"). Learning reduced to 2 sentences.
4. **Results**: Trimmed from ~2,400 to ~1,900 words. Loss exposure is longest subsection. Learning is 1 paragraph. Graph is 1 paragraph labeled "Exploratory Structural Clustering."
5. **Discussion**: Trimmed from ~1,700 to ~1,200 words. Removed graph subsection (merged into 1 sentence). Added "Relation to Formal Models" paragraph with explicit caveat. Trimmed experience section.
6. **Limitations**: Added "No formal model comparison" as first limitation. Added "Trial-level nesting" limitation. Kept all others.
7. **Conclusion**: Trimmed to ~200 words. Ends with: "formal model comparisons, causal experiments, and individual-differences analyses are needed."
8. **Figures**: Fig 5 (graph clustering) and Fig 6 (cross-dataset bridge) commented out → supplementary.

---

## Compilation

- **Tool**: pdflatex + bibtex
- **Result**: ✓ 24 pages, 222 KB, zero errors, zero undefined references

---

## Reviewer Concerns Addressed (Second Pass)

| Concern | Action |
|---------|--------|
| Too much ML/feature engineering | Compressed to key features + "predictive validation" framing |
| Graph distracts | 1 paragraph + figures to supplement |
| Learning confounded and overemphasized | 1 descriptive paragraph with confound caveat |
| CPT comparison too strong | Explicit caveat: no formal model comparison performed |
| Trial-level nesting | Added as limitation |
| Table 4 is strongest result | Made central in Results and Abstract |
| Paper too broad | Focused on binary loss exposure; everything else is supporting |
