# Internal Review: Decision-Style Critique

## Summary Assessment

This is a well-executed secondary analysis with a clear empirical finding (loss exposure drives EV failure) that replicates across datasets. However, the paper currently reads more as a feature-engineering exercise with a graph appendage than as a contribution to decision theory. The theoretical interpretation is thin — the finding is consistent with prospect theory but doesn't clearly advance beyond it. The graph section adds length without proportional insight. With focused revision (sharpen the theoretical contribution, trim the graph, strengthen the loss-attention framing), this could be a solid *Decision* paper.

---

## Major Strengths

1. **Large-scale, cross-dataset validation.** Training on 13,006 problems and transferring to 270 independent problems (AUC 0.79) is genuinely impressive and rare in this literature. Most decision-making papers use one dataset.

2. **Clear, replicable main finding.** Loss exposure in the EV-favored option as the #1 predictor is simple, interpretable, and robust across methods (regression, ablation, graph hubs, cross-transfer).

3. **Honest limitations section.** The confound acknowledgment, the circularity of the graph, and the correlational nature are all stated clearly. This builds trust.

4. **Methodological transparency.** Feature definitions are explicit, the common representation is well-motivated, and the two-stage CPC18 reconstruction is properly documented.

5. **Learning dynamics add temporal depth.** The block-level analysis and anti-learning finding are genuinely interesting and connect to the decisions-from-experience literature.

---

## Major Weaknesses

1. **Theoretical contribution is underdeveloped.** The paper shows *that* loss exposure predicts EV failure but doesn't adequately explain *why* this is surprising or what it adds beyond prospect theory. A *Decision* reviewer will ask: "Isn't this just loss aversion? We've known this since 1979." The distinction between option-level loss avoidance and outcome-level loss aversion (the Yechiam/loss-attention connection) is mentioned but not developed enough to constitute a theoretical advance.

2. **The paper tries to do too much.** It covers: common representation, 78 features, ablation, cross-dataset transfer, learning dynamics, AND graph representation. Each could be a paper. The result is breadth without depth on any single contribution. A *Decision* reviewer may feel overwhelmed and unclear about what the *one* contribution is.

3. **Graph section is the weakest link.** It adds ~1,500 words and a figure but the main insight (EV-failure problems cluster) is already obvious from the feature analysis. The 1.9× density ratio lacks a formal significance test. The cross-dataset bridge (Figure 6) is illustrative but not quantitatively compelling. A skeptical reviewer will say: "You built a graph from the same features that predict failure, then showed that failure clusters in that graph. This is circular."

4. **Only 8 references.** For a journal paper in a mature field, this is far too few. Missing: Brandstätter et al. (priority heuristic), Loomes & Sugden (regret theory), Birnbaum (configural weight models), Hertwig et al. (description-experience gap), Gonzalez & Dutt (instance-based learning), Fehr-Duda & Epper (probability weighting). The paper positions itself against a strawman version of the literature.

5. **No formal statistical tests for key claims.** The 1.9× graph density has no p-value. The difference between 38% and 25% failure rate (loss exposure) has no confidence interval or test. The cross-dataset transfer AUC of 0.79 has no confidence interval. For an APA journal, inferential statistics are expected.

---

## Likely Reviewer Objections

1. **"This is just loss aversion repackaged."** The main finding (people avoid options with losses) is the central prediction of prospect theory. What does this paper add? The response needs to be sharper: it's not about the *magnitude* of loss aversion (λ ≈ 2) but about the *binary presence* of any loss being sufficient to trigger avoidance, regardless of probability or magnitude. This is a different claim that needs explicit testing (e.g., does the probability or magnitude of the loss matter, or is mere presence sufficient?).

2. **"The graph adds nothing."** A reviewer will note that the graph is built from the same features used in regression, so clustering is expected by construction. The paper needs to either (a) show the graph reveals something the regression doesn't, or (b) demote the graph to supplementary material.

3. **"N=270 for CPC18 is too small for the claims made."** The CPC18 AUC estimates are unstable (10-fold CV on 270 observations). The cross-transfer is more convincing (trained on 13K, tested on 270), but within-CPC18 results should be heavily caveated or removed.

4. **"The block/feedback confound invalidates the learning section."** A strict reviewer may argue that without separating block from feedback, the learning section is uninterpretable. The paper acknowledges this but still devotes significant space to learning interpretations.

5. **"Where is the comparison to prospect theory?"** The paper doesn't fit a prospect theory model and compare. If loss exposure is the key, does CPT with standard parameters predict the same failures? If yes, the contribution is incremental. If no, that's interesting and should be shown.

6. **"Feature engineering is not theory."** Computing 78 features and running logistic regression is methodology, not cognitive science. What is the *process model*? How do people actually make these decisions? The paper describes patterns but not mechanisms.

7. **"The dominance finding is trivial."** Of course people choose the dominant option — it's better in every state. This doesn't tell us about cognition; it tells us about problem design (most experiments avoid dominated options).

8. **"Why not use prospect theory features directly?"** The paper computes ad hoc features rather than deriving predictions from established models (CPT, priority heuristic, TAX). A model-comparison approach would be more theoretically informative.

---

## Dimension-by-Dimension Assessment

### 1. Fit to Decision
**Adequate but borderline.** The topic (risky choice, EV deviations) fits perfectly. The approach (feature engineering, ML, graphs) is more computational than typical *Decision* papers. Needs stronger theoretical framing to avoid being seen as a methods paper.

### 2. Clarity of Main Claim
**Good but diluted.** The loss-exposure claim is clear in the abstract and conclusion. But the paper also claims contributions about dominance, learning, and graphs, which dilute the central message. Recommend: one main claim (loss exposure), with others as supporting evidence.

### 3. Theoretical Contribution
**Weak.** The paper describes a pattern but doesn't explain it mechanistically. The connection to loss attention (Yechiam) is promising but underdeveloped. Needs 1–2 paragraphs distinguishing option-level loss avoidance from outcome-level loss aversion, with testable predictions.

### 4. Beyond Feature Engineering
**Borderline.** Currently reads as: "we computed features, ran regression, features predict." The cognitive interpretation (loss attention, dominance detection) elevates it, but needs more development. The Discussion should spend more time on *why* binary loss presence matters more than loss magnitude.

### 5. Loss Exposure Result
**Strong empirically, weak theoretically.** The convergence across methods is compelling. But the interpretation needs sharpening. Is this: (a) loss aversion applied at the option level? (b) a simpler heuristic ("avoid options with negatives")? (c) loss attention increasing deliberation time? These have different implications and the paper doesn't distinguish them.

### 6. Dominance Interpretation
**Overclaimed.** The "cognitive competence" framing is too strong. Dominance problems may simply have large EV differences that make the choice obvious. Need to check: is dominance still protective after controlling for ev_abs_diff? If dominance is confounded with easy problems, the finding is less interesting.

### 7. Learning/Feedback Claims
**Appropriately cautious but still too much space.** The confound is acknowledged, but the section still interprets results as "learning." Consider renaming to "Changes Across Blocks" and reducing interpretive language. The anti-learning finding is the most interesting part — consider leading with it.

### 8. Graph Results
**Overclaimed relative to evidence.** The graph confirms what regression already shows. Without a formal null model, the 1.9× ratio is descriptive. The cross-dataset bridge is a nice illustration but one example (sim=0.997) is anecdotal. Recommend: demote to brief section or supplementary, or add permutation test.

### 9. Reproducibility
**Good.** Data sources are public, methods are described in detail, feature definitions are explicit. Missing: code/data availability statement (required by many journals). Should add a statement about where code and processed data can be accessed.

### 10. Figures and Tables
**Mostly good.** Figures 1–5 are clear and support the narrative. Figure 6 (cross-dataset bridge) is the weakest — a single example pair is not compelling as a standalone figure. Table 2 (ablation) is the most informative table. Consider whether Table 3 (key results) is redundant with the text.

### 11. Limitations
**Strong.** Comprehensive and honest. Could promote the "no formal null model for graph" limitation to a more prominent position, given how much weight the graph section carries.

### 12. Length and Scope
**Too broad.** 7,800 words covering representation + features + ablation + transfer + learning + graph is a lot. The paper would be stronger at 6,000 words focused on: loss exposure finding + cross-dataset transfer + brief learning note. Graph could be supplementary.

### 13. Title and Abstract
**Title is good** — specific, accurate, not overclaimed. **Abstract is good** — hits the key numbers. Could be slightly more compelling by leading with the puzzle ("Why do people reject options that maximize expected value?") rather than the method.

---

## Required Revisions Before Submission

| # | Section | Issue | Suggested Fix | Priority |
|---|---------|-------|---------------|----------|
| 1 | Introduction | Theoretical contribution unclear | Add 2 paragraphs distinguishing option-level loss avoidance from prospect theory's outcome-level loss aversion. State testable predictions. | High |
| 2 | All | Only 8 references | Add 15–20 references: priority heuristic, regret theory, description-experience gap, instance-based learning, probability weighting, salience theory. | High |
| 3 | Results | No inferential statistics | Add confidence intervals for key AUC values (bootstrap). Add chi-square or proportion test for 38% vs 25% failure rate. | High |
| 4 | Graph section | Circularity not addressed | Either add permutation test for density ratio, or demote graph to supplementary/brief paragraph. | High |
| 5 | Discussion | "Cognitive competence" for dominance | Check if dominance is confounded with ev_abs_diff. If so, soften the claim. | High |
| 6 | Method | No code/data availability statement | Add statement about data sources (public) and code availability (GitHub or OSF). | Medium |
| 7 | Learning section | Interpretive language despite confound | Rename subsection to "Changes Across Blocks." Reduce causal language. | Medium |
| 8 | Abstract | Starts with method, not puzzle | Rewrite opening sentence to pose the question, then introduce the approach. | Medium |
| 9 | Discussion | No comparison to CPT predictions | Add paragraph discussing whether CPT with standard parameters would predict the same pattern. If unknown, state as future work. | Medium |
| 10 | Results/Discussion | Anti-learning underexplored | The anti-learning finding (33% of problems worsen) is novel and interesting. Give it more prominence. | Medium |

---

## Optional Revisions

| # | Section | Issue | Suggested Fix |
|---|---------|-------|---------------|
| 1 | Graph section | Adds length without proportional insight | Move to supplementary materials; keep 1 paragraph + 1 figure in main text |
| 2 | Figure 6 | Single example is anecdotal | Replace with aggregate: "X% of cross-dataset neighbors share EV-failure status" |
| 3 | Table 3 | Redundant with text | Remove or move to supplementary |
| 4 | Introduction | Could be more engaging | Open with a concrete example problem showing loss-driven EV failure |
| 5 | Method | 78 features may overwhelm reader | Add a "feature summary" figure or move full list to appendix |
| 6 | Discussion | Practical implications section | Expand slightly — decision support angle is appealing to applied readers |

---

## Risk Assessment

**Medium.** The paper has a clear finding and good data, but risks desk rejection if the editor perceives it as a methods/ML paper rather than a decision science contribution. The thin theoretical framing and heavy computational methodology may not match *Decision*'s typical content. With the required revisions (especially #1 and #2), the risk drops to low-medium.

---

## Recommendation

**Needs major revision before submission.**

The empirical work is solid and the main finding is compelling, but the paper needs:
1. Stronger theoretical positioning (not just "loss aversion repackaged")
2. More engagement with the existing literature (8 references is unacceptable)
3. Inferential statistics for key claims
4. Either a formal test for the graph or demotion to supplementary
5. Tighter scope (consider cutting or shortening the graph section)

After these revisions, the paper would be a reasonable submission to *Decision* with a moderate chance of acceptance after peer review.

---

## Specific Suggestions

1. **Lead with the puzzle, not the method.** The paper's hook should be: "People reject the option that maximizes expected value 25% of the time. When does this happen and why?" Currently the introduction leads with EV as a benchmark, which is less engaging.

2. **Sharpen the loss-attention distinction.** The key theoretical claim should be: "It's not that people overweight losses (prospect theory) — it's that the mere *presence* of any negative outcome in an option triggers avoidance, regardless of its probability or magnitude relative to gains. This is more consistent with loss attention than loss aversion." Then show evidence: does the probability of the loss matter? Does its magnitude? If not, that's the novel finding.

3. **Cut the graph to 1 paragraph + 1 figure.** Say: "To confirm that EV-failure problems share structural properties beyond what regression captures, we constructed a similarity graph. EV-failure problems were 1.9× more densely connected than EV-consistent problems, consistent with a coherent structural type." That's all you need. The cross-dataset bridge can be a supplementary figure.

4. **Add a CPT comparison paragraph.** Even if you don't fit CPT formally, discuss: "A CPT model with standard parameters (λ=2.25, α=0.88, γ=0.61) would predict increased avoidance of loss-containing options, but would also predict sensitivity to loss probability and magnitude. Our finding that binary loss presence dominates over probability-weighted loss magnitude suggests a simpler mechanism than CPT specifies."

5. **Expand the reference list aggressively.** This is a mature field. You need to cite: Brandstätter et al. 2006 (priority heuristic), Hertwig et al. 2004 (description-experience gap), Gonzalez & Dutt 2011 (IBL), Birnbaum 2008 (TAX), Loomes & Sugden 1982 (regret), Bordalo et al. 2012 (salience theory), Erev et al. 2010 (CPC2015 paper), Rieskamp 2008 (SSL model). At minimum 20 references for a journal paper.
