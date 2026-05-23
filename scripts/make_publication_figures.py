"""Spec 020: Generate publication-quality figures for Decision manuscript."""

import ast
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs" / "figures" / "publication"
OUT.mkdir(parents=True, exist_ok=True)

# Style
plt.rcParams.update({
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "font.family": "sans-serif",
})

# Colorblind-friendly palette
C_BLUE = "#0072B2"
C_ORANGE = "#D55E00"
C_GREEN = "#009E73"
C_GRAY = "#666666"
C_PURPLE = "#CC79A7"
C_YELLOW = "#F0E442"


def save(fig, name):
    fig.savefig(OUT / f"{name}.png")
    fig.savefig(OUT / f"{name}.pdf")
    plt.close(fig)
    print(f"  {name}")


def load_combined():
    """Load and merge choices13k and cpc18 data."""
    c_common = pd.read_parquet(ROOT / "data/interim/choices13k_common.parquet").reset_index(drop=True)
    c_feat = pd.read_parquet(ROOT / "data/interim/choices13k_features.parquet").reset_index(drop=True).drop(columns=["problem_id"])
    c_adv = pd.read_parquet(ROOT / "data/interim/choices13k_advanced_features.parquet").reset_index(drop=True).drop(columns=["problem_id"])
    c = pd.concat([c_common, c_feat, c_adv], axis=1)
    c["dataset"] = "choices13k"
    c["observed_B_rate"] = c["bRate"]
    c["ev_failure"] = ((c["higher_ev_option"] == "A") & (c["observed_B_rate"] > 0.5)) | \
                      ((c["higher_ev_option"] == "B") & (c["observed_B_rate"] < 0.5))

    p_common = pd.read_parquet(ROOT / "data/interim/cpc18_common.parquet").reset_index(drop=True)
    p_feat = pd.read_parquet(ROOT / "data/interim/cpc18_features.parquet").reset_index(drop=True).drop(columns=["game_id"])
    p_adv = pd.read_parquet(ROOT / "data/interim/cpc18_advanced_features.parquet").reset_index(drop=True).drop(columns=["game_id"])
    p = pd.concat([p_common, p_feat, p_adv], axis=1)
    p["dataset"] = "cpc18"
    p["observed_B_rate"] = p["mean_choice_B"]
    p["ev_failure"] = ((p["higher_ev_option"] == "A") & (p["observed_B_rate"] > 0.5)) | \
                      ((p["higher_ev_option"] == "B") & (p["observed_B_rate"] < 0.5))
    return c, p


def fig1_ev_failure_rates():
    """Bar chart of EV failure rates across datasets and metrics."""
    labels = ["choices13k\n(problem-level)", "CPC18\n(problem-level)",
              "CPC18 block 1\n(trial-level)", "CPC18 block 5\n(trial-level)"]
    values = [24.9, 17.6, 35.1, 30.4]
    colors = [C_BLUE, C_ORANGE, C_ORANGE, C_ORANGE]
    hatches = ["", "", "//", "//"]

    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    bars = ax.bar(range(len(values)), values, color=colors, edgecolor="black", linewidth=0.5)
    for bar, h in zip(bars, hatches):
        bar.set_hatch(h)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_ylabel("EV Failure Rate (%)")
    ax.set_ylim(0, 42)
    for i, v in enumerate(values):
        ax.text(i, v + 0.8, f"{v}%", ha="center", fontsize=9)
    ax.axhline(y=25, color=C_GRAY, linestyle="--", linewidth=0.7, alpha=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save(fig, "fig1_ev_failure_rates")


def fig2_loss_dominance(c, p):
    """Two-panel: loss and dominance effects on EV failure."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 3.5))

    # Panel (a): ev_favored_has_loss
    for i, (df, name, color) in enumerate([(c, "choices13k", C_BLUE), (p, "CPC18", C_ORANGE)]):
        rates = df.groupby("ev_favored_has_loss")["ev_failure"].mean() * 100
        x = np.array([0, 1]) + i * 0.3
        ax1.bar(x, [rates.get(False, 0), rates.get(True, 0)], width=0.28,
                color=color, edgecolor="black", linewidth=0.5, label=name)
    ax1.set_xticks([0.15, 1.15])
    ax1.set_xticklabels(["False", "True"])
    ax1.set_xlabel("EV-favored option has loss")
    ax1.set_ylabel("EV Failure Rate (%)")
    ax1.legend(frameon=False)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.text(-0.1, 1.05, "(a)", transform=ax1.transAxes, fontsize=12, fontweight="bold")

    # Panel (b): any_dominance
    for i, (df, name, color) in enumerate([(c, "choices13k", C_BLUE), (p, "CPC18", C_ORANGE)]):
        rates = df.groupby("any_dominance")["ev_failure"].mean() * 100
        x = np.array([0, 1]) + i * 0.3
        ax2.bar(x, [rates.get(False, 0), rates.get(True, 0)], width=0.28,
                color=color, edgecolor="black", linewidth=0.5, label=name)
    ax2.set_xticks([0.15, 1.15])
    ax2.set_xticklabels(["False", "True"])
    ax2.set_xlabel("Stochastic dominance present")
    ax2.set_ylabel("EV Failure Rate (%)")
    ax2.legend(frameon=False)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.text(-0.1, 1.05, "(b)", transform=ax2.transAxes, fontsize=12, fontweight="bold")

    fig.tight_layout()
    save(fig, "fig2_loss_dominance_effects")


def fig3_feature_ablation():
    """Grouped bar chart of feature ablation AUC."""
    df = pd.read_csv(ROOT / "outputs/tables/feature_ablation_model_comparison.csv")
    # Filter logistic only, 5fold_cv
    lg = df[(df["model"] == "logistic") & (df["eval_method"] == "5fold_cv")]

    configs = ["EV-only", "Basic", "Basic+Loss", "Full"]
    c13k_auc = [lg[(lg["dataset"] == "choices13k") & (lg["config"] == c)]["roc_auc"].values[0] for c in configs]

    # Cross-transfer
    ct = df[(df["model"] == "logistic") & (df["eval_method"] == "cross_transfer")]
    ct_auc = [ct[ct["config"] == c]["roc_auc"].values[0] if len(ct[ct["config"] == c]) > 0 else 0 for c in configs]

    # GB ceiling
    gb = df[(df["model"] == "gradient_boosting") & (df["dataset"] == "choices13k") &
            (df["eval_method"] == "5fold_cv") & (df["config"] == "Full")]
    gb_val = gb["roc_auc"].values[0] if len(gb) > 0 else 0.879

    x = np.arange(len(configs))
    w = 0.35
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    ax.bar(x - w/2, c13k_auc, w, color=C_BLUE, edgecolor="black", linewidth=0.5, label="choices13k (5-fold CV)")
    ax.bar(x + w/2, ct_auc, w, color=C_ORANGE, edgecolor="black", linewidth=0.5, label="Cross-transfer (c13k→CPC18)")
    ax.axhline(y=gb_val, color=C_GREEN, linestyle="--", linewidth=1.2, label=f"GB ceiling ({gb_val:.3f})")
    ax.set_xticks(x)
    ax.set_xticklabels(configs)
    ax.set_ylabel("AUC")
    ax.set_ylim(0.5, 0.95)
    ax.legend(frameon=False, loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    # Annotate loss jump
    ax.annotate("+0.14", xy=(1.5, (c13k_auc[1] + c13k_auc[2]) / 2),
                fontsize=9, ha="center", color=C_BLUE)
    fig.tight_layout()
    save(fig, "fig3_feature_ablation")


def fig4_learning_dynamics():
    """Line chart of EV failure by block, stratified by ambiguity."""
    df = pd.read_csv(ROOT / "outputs/tables/cpc18_block_level_choice.csv")
    # ev_failure = 1 - ev_consistency
    df["ev_failure_rate"] = 1 - df["ev_consistency"]

    overall = df.groupby("block")["ev_failure_rate"].mean()
    amb_true = df[df["ambiguity"] == True].groupby("block")["ev_failure_rate"].mean()
    amb_false = df[df["ambiguity"] == False].groupby("block")["ev_failure_rate"].mean()

    fig, ax = plt.subplots(figsize=(5, 3.5))
    blocks = [1, 2, 3, 4, 5]
    ax.plot(blocks, overall.values * 100, "o-", color="black", linewidth=2, markersize=6, label="Overall")
    ax.plot(blocks, amb_true.values * 100, "s--", color=C_ORANGE, linewidth=1.5, markersize=5, label="Ambiguous")
    ax.plot(blocks, amb_false.values * 100, "^--", color=C_BLUE, linewidth=1.5, markersize=5, label="Non-ambiguous")

    # Feedback onset annotation
    ax.axvline(x=1.5, color=C_GRAY, linestyle=":", linewidth=1)
    ax.text(1.55, ax.get_ylim()[1] * 0.95, "Feedback\nonset", fontsize=8, color=C_GRAY, va="top")

    ax.set_xlabel("Block")
    ax.set_ylabel("EV Failure Rate (%)")
    ax.set_xticks(blocks)
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    save(fig, "fig4_learning_dynamics")


def fig5_graph_clustering():
    """Two-panel: density comparison + feature hub enrichment."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 3.5))

    # Panel (a): density comparison
    densities = [0.00285, 0.00149]
    labels_d = ["EV-failure\nsubgraph", "EV-consistent\nsubgraph"]
    bars = ax1.bar(labels_d, densities, color=[C_ORANGE, C_BLUE], edgecolor="black", linewidth=0.5)
    ax1.set_ylabel("Edge Density")
    ax1.text(0.5, 0.0029, "1.9×", ha="center", fontsize=11, fontweight="bold")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.text(-0.1, 1.05, "(a)", transform=ax1.transAxes, fontsize=12, fontweight="bold")

    # Panel (b): feature hub enrichment
    hubs = pd.read_csv(ROOT / "outputs/tables/graph_feature_hubs.csv")
    hubs = hubs.sort_values("ev_failure_fraction")
    group_colors = {"loss": C_ORANGE, "conflict": C_PURPLE, "ambiguity": C_GREEN,
                    "safety": C_BLUE, "dominance": C_GRAY}
    colors = [group_colors.get(g, C_GRAY) for g in hubs["group"]]
    ax2.barh(range(len(hubs)), hubs["ev_failure_fraction"], color=colors, edgecolor="black", linewidth=0.5)
    ax2.set_yticks(range(len(hubs)))
    ax2.set_yticklabels(hubs["feature"].str.replace("_", " "), fontsize=8)
    ax2.set_xlabel("EV-Failure Fraction")
    ax2.axvline(x=0.242, color=C_GRAY, linestyle="--", linewidth=0.7, label="Base rate")
    ax2.legend(frameon=False, fontsize=8)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.text(-0.1, 1.05, "(b)", transform=ax2.transAxes, fontsize=12, fontweight="bold")

    fig.tight_layout()
    save(fig, "fig5_graph_clustering")


def fig6_cross_dataset_bridge(c, p):
    """Schematic showing cross-dataset similar problem pair."""
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_xlim(-1, 11)
    ax.set_ylim(-1, 7)
    ax.axis("off")

    # choices13k problem (left)
    c_row = c[c.index == 8961].iloc[0] if 8961 < len(c) else None
    # CPC18 problem (right) - game_id 58
    p_row = p[p["game_id"] == 58].iloc[0] if len(p[p["game_id"] == 58]) > 0 else None

    # Draw nodes
    def draw_node(ax, x, y, label, sublabel, color, is_failure):
        circle = plt.Circle((x, y), 0.8, color=color, alpha=0.3, ec="black", linewidth=1.5)
        ax.add_patch(circle)
        ax.text(x, y + 0.15, label, ha="center", va="center", fontsize=9, fontweight="bold")
        ax.text(x, y - 0.3, sublabel, ha="center", va="center", fontsize=7)
        if is_failure:
            ax.text(x, y + 1.1, "EV-failure", ha="center", fontsize=7, color=C_ORANGE, fontstyle="italic")

    # Left node: choices13k:8961
    draw_node(ax, 2.5, 4, "choices13k:8961", "ev_diff = 1.58", C_BLUE, True)
    # Right node: CPC18:58
    draw_node(ax, 7.5, 4, "CPC18:58", "ev_diff = 1.80", C_ORANGE, True)

    # Edge
    ax.annotate("", xy=(6.7, 4), xytext=(3.3, 4),
                arrowprops=dict(arrowstyle="-", lw=2, color="black"))
    ax.text(5, 4.4, "similarity = 0.997", ha="center", fontsize=9, fontweight="bold")

    # Feature labels
    ax.text(2.5, 2.2, "Features:", ha="center", fontsize=8, fontweight="bold")
    ax.text(2.5, 1.6, "• ev_favored_has_loss", ha="center", fontsize=7)
    ax.text(2.5, 1.1, "• loss_asymmetry", ha="center", fontsize=7)
    ax.text(2.5, 0.6, "• ambiguity", ha="center", fontsize=7)

    ax.text(7.5, 2.2, "Features:", ha="center", fontsize=8, fontweight="bold")
    ax.text(7.5, 1.6, "• ev_favored_has_loss", ha="center", fontsize=7)
    ax.text(7.5, 1.1, "• loss_asymmetry", ha="center", fontsize=7)

    # Title annotation
    ax.text(5, 6.2, "Cross-Dataset Structural Bridge", ha="center", fontsize=11, fontweight="bold")
    ax.text(5, 5.6, "Both problems: EV-favored option contains losses → people avoid it",
            ha="center", fontsize=8, color=C_GRAY)

    save(fig, "fig6_cross_dataset_bridge")


def main():
    print("Generating publication figures...")
    c, p = load_combined()

    fig1_ev_failure_rates()
    fig2_loss_dominance(c, p)
    fig3_feature_ablation()
    fig4_learning_dynamics()
    fig5_graph_clustering()
    fig6_cross_dataset_bridge(c, p)

    print(f"\nAll figures saved to {OUT}/")


if __name__ == "__main__":
    main()
