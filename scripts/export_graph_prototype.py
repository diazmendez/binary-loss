"""Export graph representation prototype (spec 014).

Generates Neo4j-compatible CSVs for:
- View A: Problem-as-Subgraph (nodes + edges for datasets, problems, options, outcomes, features)
- View B: Problem-Similarity Graph (k-NN edges based on standardized feature vectors)
"""

import ast
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs" / "graph"
REPORT = ROOT / "outputs" / "reports" / "graph_prototype_summary.md"

BINARY_FEATURES = [
    "ev_favored_has_loss", "any_dominance", "ev_max_conflict",
    "has_safe_option_A", "has_safe_option_B", "salience_conflict",
    "ambiguity", "ev_risk_conflict", "loss_asymmetry",
]

SIMILARITY_FEATURES = [
    "ev_diff", "ev_abs_diff", "variance_diff", "std_diff",
    "prob_loss_A", "prob_loss_B", "prob_loss_diff",
    "ev_favored_has_loss", "any_dominance",
    "ev_max_conflict", "salience_conflict",
    "n_outcomes_A", "n_outcomes_B",
    "range_overlap", "range_diff",
]

K_NEIGHBORS = 10


def load_data():
    """Load and merge all parquets for both datasets."""
    # choices13k — files are row-aligned, use concat by column
    c_common = pd.read_parquet(ROOT / "data/interim/choices13k_common.parquet").reset_index(drop=True)
    c_feat = pd.read_parquet(ROOT / "data/interim/choices13k_features.parquet").reset_index(drop=True)
    c_adv = pd.read_parquet(ROOT / "data/interim/choices13k_advanced_features.parquet").reset_index(drop=True)
    # Drop duplicate problem_id columns before concat
    c_feat = c_feat.drop(columns=["problem_id"])
    c_adv = c_adv.drop(columns=["problem_id"])
    c = pd.concat([c_common, c_feat, c_adv], axis=1)
    c["dataset"] = "choices13k"
    c["observed_B_rate"] = c["bRate"]
    c["reconstruction_method"] = ""
    # Use row index as unique ID (problem_id is not unique due to condition repeats)
    c["uid"] = c.index

    # cpc18
    p_common = pd.read_parquet(ROOT / "data/interim/cpc18_common.parquet").reset_index(drop=True)
    p_feat = pd.read_parquet(ROOT / "data/interim/cpc18_features.parquet").reset_index(drop=True)
    p_adv = pd.read_parquet(ROOT / "data/interim/cpc18_advanced_features.parquet").reset_index(drop=True)
    p_feat = p_feat.drop(columns=["game_id"])
    p_adv = p_adv.drop(columns=["game_id"])
    p = pd.concat([p_common, p_feat, p_adv], axis=1)
    p["dataset"] = "cpc18"
    p["problem_id"] = p["game_id"]
    p["observed_B_rate"] = p["mean_choice_B"]
    p["uid"] = p["game_id"]  # game_id is unique in cpc18

    # Compute ev_failure
    c["ev_failure"] = ((c["higher_ev_option"] == "A") & (c["observed_B_rate"] > 0.5)) | \
                      ((c["higher_ev_option"] == "B") & (c["observed_B_rate"] < 0.5))
    p["ev_failure"] = ((p["higher_ev_option"] == "A") & (p["observed_B_rate"] > 0.5)) | \
                      ((p["higher_ev_option"] == "B") & (p["observed_B_rate"] < 0.5))

    return c, p


def build_nodes_datasets():
    return pd.DataFrame({"node_id": ["dataset:choices13k", "dataset:cpc18"], "name": ["choices13k", "cpc18"]})


def build_nodes_problems(c, p):
    rows = []
    for df in [c, p]:
        for _, r in df.iterrows():
            ds = r["dataset"]
            uid = r["uid"]
            rows.append({
                "node_id": f"problem:{ds}:{uid}",
                "dataset": ds,
                "problem_id": r["problem_id"],
                "ev_diff": r.get("ev_diff", ""),
                "observed_B_rate": r["observed_B_rate"],
                "ev_failure": r["ev_failure"],
                "ambiguity": r.get("ambiguity", False),
                "reconstruction_method": r.get("reconstruction_method", ""),
                "ev_favored_has_loss": r.get("ev_favored_has_loss", False),
                "any_dominance": r.get("any_dominance", False),
                "ev_max_conflict": r.get("ev_max_conflict", False),
                "ev_risk_conflict": r.get("ev_risk_conflict", False),
            })
    return pd.DataFrame(rows)


def build_nodes_options_outcomes(c, p):
    opt_rows = []
    out_rows = []
    for df in [c, p]:
        for _, r in df.iterrows():
            ds = r["dataset"]
            uid = r["uid"]
            prob_node = f"problem:{ds}:{uid}"
            for label in ["A", "B"]:
                opt_id = f"option:{ds}:{uid}:{label}"
                outcomes = ast.literal_eval(r[f"options_{label}"])
                ev = sum(prob * val for prob, val in outcomes)
                vals = [val for _, val in outcomes]
                var_key = f"variance_{label}"
                std_key = f"std_{label}"
                opt_rows.append({
                    "node_id": opt_id,
                    "problem_node_id": prob_node,
                    "label": label,
                    "expected_value": round(ev, 6),
                    "variance": round(r.get(var_key, 0), 6),
                    "std": round(r.get(std_key, 0), 6),
                    "has_loss": r.get(f"has_loss_{label}", False),
                    "prob_loss": round(r.get(f"prob_loss_{label}", 0), 6),
                    "is_safe": r.get(f"has_safe_option_{label}", False),
                    "n_outcomes": len(outcomes),
                })
                for idx, (prob, val) in enumerate(outcomes):
                    out_id = f"outcome:{ds}:{uid}:{label}:{idx}"
                    out_rows.append({
                        "node_id": out_id,
                        "option_node_id": opt_id,
                        "value": val,
                        "probability": prob,
                        "is_loss": val < 0,
                        "is_best": val == max(vals),
                        "is_worst": val == min(vals),
                        "is_rare": prob < 0.1,
                    })
    return pd.DataFrame(opt_rows), pd.DataFrame(out_rows)


def build_nodes_features():
    return pd.DataFrame({
        "node_id": [f"feature:{f}" for f in BINARY_FEATURES],
        "name": BINARY_FEATURES,
    })


def build_edges_contains(problems_df):
    rows = []
    for _, r in problems_df.iterrows():
        rows.append({"source_id": f"dataset:{r['dataset']}", "target_id": r["node_id"]})
    return pd.DataFrame(rows)


def build_edges_has_option(options_df):
    return options_df[["problem_node_id", "node_id"]].rename(
        columns={"problem_node_id": "source_id", "node_id": "target_id"})


def build_edges_has_outcome(outcomes_df):
    return outcomes_df[["option_node_id", "node_id"]].rename(
        columns={"option_node_id": "source_id", "node_id": "target_id"})


def build_edges_has_feature(c, p):
    rows = []
    for df in [c, p]:
        for _, r in df.iterrows():
            ds = r["dataset"]
            uid = r["uid"]
            prob_node = f"problem:{ds}:{uid}"
            for feat in BINARY_FEATURES:
                if r.get(feat, False):
                    rows.append({"source_id": prob_node, "target_id": f"feature:{feat}"})
    return pd.DataFrame(rows)


def build_similarity_edges(c, p):
    """Compute k-NN similarity graph over combined dataset."""
    combined = pd.concat([
        c[["dataset", "uid"] + SIMILARITY_FEATURES],
        p[["dataset", "uid"] + SIMILARITY_FEATURES],
    ], ignore_index=True)

    X = combined[SIMILARITY_FEATURES].copy()
    # Convert booleans to int
    for col in X.columns:
        if X[col].dtype == bool:
            X[col] = X[col].astype(int)
    # Impute NaN with 0
    nan_cols = X.columns[X.isna().any()].tolist()
    X = X.fillna(0)
    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # k-NN
    nn = NearestNeighbors(n_neighbors=K_NEIGHBORS + 1, metric="cosine", algorithm="brute")
    nn.fit(X_scaled)
    distances, indices = nn.kneighbors(X_scaled)

    # Build edges
    rows = []
    for i in range(len(combined)):
        ds_i = combined.iloc[i]["dataset"]
        uid_i = combined.iloc[i]["uid"]
        src = f"problem:{ds_i}:{uid_i}"
        for j_idx in range(1, K_NEIGHBORS + 1):  # skip self
            j = indices[i, j_idx]
            dist = distances[i, j_idx]
            sim = 1.0 - dist  # cosine similarity
            ds_j = combined.iloc[j]["dataset"]
            uid_j = combined.iloc[j]["uid"]
            tgt = f"problem:{ds_j}:{uid_j}"
            rows.append({"source_id": src, "target_id": tgt, "similarity_score": round(sim, 6)})

    return pd.DataFrame(rows), combined, nan_cols


def generate_report(nodes_ds, nodes_prob, nodes_opt, nodes_out, nodes_feat,
                    edges_contains, edges_opt, edges_out, edges_feat, edges_sim,
                    combined, c, p):
    """Generate summary report."""
    lines = ["# Graph Prototype Summary (Spec 014)\n"]

    # Node counts
    lines.append("## Node Counts by Label\n")
    lines.append(f"| Label | Count |")
    lines.append(f"|-------|-------|")
    lines.append(f"| Dataset | {len(nodes_ds)} |")
    lines.append(f"| Problem | {len(nodes_prob)} |")
    lines.append(f"| Option | {len(nodes_opt)} |")
    lines.append(f"| Outcome | {len(nodes_out)} |")
    lines.append(f"| Feature | {len(nodes_feat)} |")
    lines.append(f"| **Total** | **{len(nodes_ds)+len(nodes_prob)+len(nodes_opt)+len(nodes_out)+len(nodes_feat)}** |")
    lines.append("")

    # Edge counts
    lines.append("## Edge Counts by Type\n")
    lines.append(f"| Type | Count |")
    lines.append(f"|------|-------|")
    lines.append(f"| CONTAINS | {len(edges_contains)} |")
    lines.append(f"| HAS_OPTION | {len(edges_opt)} |")
    lines.append(f"| HAS_OUTCOME | {len(edges_out)} |")
    lines.append(f"| HAS_FEATURE | {len(edges_feat)} |")
    lines.append(f"| SIMILAR_PROBLEM | {len(edges_sim)} |")
    lines.append(f"| **Total** | **{len(edges_contains)+len(edges_opt)+len(edges_out)+len(edges_feat)+len(edges_sim)}** |")
    lines.append("")

    # Feature node degree
    lines.append("## Feature Node Degree\n")
    lines.append("| Feature | Degree (problems with feature=True) |")
    lines.append("|---------|--------------------------------------|")
    feat_counts = edges_feat["target_id"].value_counts()
    for feat in BINARY_FEATURES:
        fid = f"feature:{feat}"
        count = feat_counts.get(fid, 0)
        lines.append(f"| {feat} | {count} |")
    lines.append("")

    # EV failure clustering in similarity graph
    lines.append("## EV Failure Clustering in Similarity Graph\n")
    # Build lookup
    ev_fail_map = {}
    for df in [c, p]:
        for _, r in df.iterrows():
            nid = f"problem:{r['dataset']}:{r['uid']}"
            ev_fail_map[nid] = bool(r["ev_failure"])

    both_fail = 0
    both_consistent = 0
    cross = 0
    for _, e in edges_sim.iterrows():
        s_fail = ev_fail_map.get(e["source_id"], False)
        t_fail = ev_fail_map.get(e["target_id"], False)
        if s_fail and t_fail:
            both_fail += 1
        elif not s_fail and not t_fail:
            both_consistent += 1
        else:
            cross += 1

    total_edges = len(edges_sim)
    n_total = len(nodes_prob)
    n_fail = sum(ev_fail_map.values())
    p_fail = n_fail / n_total
    p_cons = 1 - p_fail
    expected_both_fail = p_fail ** 2
    expected_both_cons = p_cons ** 2
    expected_cross = 2 * p_fail * p_cons

    lines.append(f"| Metric | Observed | Random Baseline |")
    lines.append(f"|--------|----------|-----------------|")
    lines.append(f"| Both EV-failure | {both_fail/total_edges:.4f} | {expected_both_fail:.4f} |")
    lines.append(f"| Both EV-consistent | {both_consistent/total_edges:.4f} | {expected_both_cons:.4f} |")
    lines.append(f"| Cross-type | {cross/total_edges:.4f} | {expected_cross:.4f} |")
    lines.append("")
    clustering = (both_fail / total_edges) > expected_both_fail
    lines.append(f"EV-failure problems {'**do**' if clustering else 'do not'} cluster together "
                 f"in the similarity graph (observed {both_fail/total_edges:.4f} vs random baseline {expected_both_fail:.4f}).\n")

    # Cross-dataset edges
    lines.append("## Cross-Dataset Similarity Edges\n")
    cross_ds = edges_sim.apply(
        lambda e: ("choices13k" in e["source_id"] and "cpc18" in e["target_id"]) or
                  ("cpc18" in e["source_id"] and "choices13k" in e["target_id"]), axis=1).sum()
    lines.append(f"- Cross-dataset edges (choices13k ↔ CPC18): **{cross_ds}** / {total_edges} ({cross_ds/total_edges*100:.1f}%)\n")

    # Connected components
    lines.append("## Connected Components (Similarity Graph)\n")
    import networkx as nx
    G = nx.Graph()
    for _, e in edges_sim.iterrows():
        G.add_edge(e["source_id"], e["target_id"], weight=e["similarity_score"])
    components = list(nx.connected_components(G))
    largest = max(components, key=len)
    ds_in_largest = set()
    for n in largest:
        if "choices13k" in n:
            ds_in_largest.add("choices13k")
        elif "cpc18" in n:
            ds_in_largest.add("cpc18")

    lines.append(f"- Number of components: **{len(components)}**")
    lines.append(f"- Largest component size: **{len(largest)}** nodes")
    lines.append(f"- Both datasets in largest component: **{'Yes' if len(ds_in_largest) == 2 else 'No'}**")
    lines.append("")

    # Basic graph statistics
    lines.append("## Basic Graph Statistics\n")
    degrees = [d for _, d in G.degree()]
    lines.append(f"- Nodes in similarity graph: **{G.number_of_nodes()}**")
    lines.append(f"- Edges in similarity graph: **{G.number_of_edges()}**")
    lines.append(f"- Average degree: **{np.mean(degrees):.2f}**")
    lines.append(f"- Max degree: **{max(degrees)}**")
    lines.append(f"- Min degree: **{min(degrees)}**")
    lines.append("")

    # Limitations
    lines.append("## Limitations and Next Steps\n")
    lines.append("- Similarity is based on 15 features; richer representations may yield different topology.")
    lines.append("- k=10 is arbitrary; sensitivity analysis on k could reveal structure changes.")
    lines.append("- Outcome nodes are numerous (~84K); future work may aggregate or sample.")
    lines.append("- No graph ML or GNN applied — this is a structural prototype only.")
    lines.append("- Cypher script is untested against a live Neo4j instance.")
    lines.append("")

    return "\n".join(lines)


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(REPORT.parent, exist_ok=True)

    print("Loading data...")
    c, p = load_data()

    print("Building nodes...")
    nodes_ds = build_nodes_datasets()
    nodes_prob = build_nodes_problems(c, p)
    nodes_opt, nodes_out = build_nodes_options_outcomes(c, p)
    nodes_feat = build_nodes_features()

    print("Building edges (View A)...")
    edges_contains = build_edges_contains(nodes_prob)
    edges_opt = build_edges_has_option(nodes_opt)
    edges_out = build_edges_has_outcome(nodes_out)
    edges_feat = build_edges_has_feature(c, p)

    print("Computing similarity graph (View B)...")
    edges_sim, combined, nan_cols = build_similarity_edges(c, p)

    print("Writing CSVs...")
    nodes_ds.to_csv(OUT / "nodes_datasets.csv", index=False)
    nodes_prob.to_csv(OUT / "nodes_problems.csv", index=False)
    nodes_opt.to_csv(OUT / "nodes_options.csv", index=False)
    nodes_out.to_csv(OUT / "nodes_outcomes.csv", index=False)
    nodes_feat.to_csv(OUT / "nodes_features.csv", index=False)
    edges_contains.to_csv(OUT / "edges_contains.csv", index=False)
    edges_opt.to_csv(OUT / "edges_has_option.csv", index=False)
    edges_out.to_csv(OUT / "edges_has_outcome.csv", index=False)
    edges_feat.to_csv(OUT / "edges_has_feature.csv", index=False)
    edges_sim.to_csv(OUT / "edges_similar_problem.csv", index=False)

    # Also write edgelist for NetworkX
    edges_sim.to_csv(OUT / "similarity_edgelist.csv", index=False)

    print("Generating report...")
    report = generate_report(nodes_ds, nodes_prob, nodes_opt, nodes_out, nodes_feat,
                             edges_contains, edges_opt, edges_out, edges_feat, edges_sim,
                             combined, c, p)
    REPORT.write_text(report)

    print(f"\nDone. Outputs in {OUT}/")
    print(f"Report: {REPORT}")
    print(f"  Nodes: {len(nodes_ds) + len(nodes_prob) + len(nodes_opt) + len(nodes_out) + len(nodes_feat)}")
    print(f"  Edges: {len(edges_contains) + len(edges_opt) + len(edges_out) + len(edges_feat) + len(edges_sim)}")
    if nan_cols:
        print(f"  NaN imputed (→0) in: {nan_cols}")


if __name__ == "__main__":
    main()
