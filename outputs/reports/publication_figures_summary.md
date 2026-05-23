# Publication Figures Summary (Spec 020)

## Generated Figures

| Figure | PDF Size | PNG Size | Dimensions |
|--------|----------|----------|-----------|
| fig1_ev_failure_rates | 16K | 82K | 5.5×3.5 in |
| fig2_loss_dominance_effects | 18K | 81K | 7×3.5 in |
| fig3_feature_ablation | 16K | 78K | 5.5×3.5 in |
| fig4_learning_dynamics | 17K | 108K | 5×3.5 in |
| fig5_graph_clustering | 19K | 130K | 7×3.5 in |
| fig6_cross_dataset_bridge | 30K | 103K | 6×4 in |

## Style Settings

- Font: sans-serif, base size 10pt
- Axis labels: 11pt
- Tick labels: 9pt
- Resolution: 300 dpi (PNG)
- Format: PDF (vector) for LaTeX, PNG (raster) for preview
- Width: all ≤ 7 inches

## Color Palette (colorblind-friendly)

| Color | Hex | Usage |
|-------|-----|-------|
| Blue | #0072B2 | choices13k, non-ambiguous, safety features |
| Orange | #D55E00 | CPC18, EV-failure, loss features |
| Green | #009E73 | GB ceiling, ambiguity features |
| Gray | #666666 | Reference lines, dominance |
| Purple | #CC79A7 | Conflict features |

## Manuscript Integration

All `manuscript/figures/fig*.tex` files updated to use `\includegraphics` pointing to generated PDFs via relative path `../outputs/figures/publication/`.

## Issues

- None. All figures compile and render correctly.
- Figure 6 is a schematic (not data-driven plot); may benefit from manual refinement for final submission.
