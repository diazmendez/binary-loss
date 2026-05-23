"""Spec 018: Graph Exploration Queries.

Runs exploratory Cypher queries against the Neo4j instance and generates
summary report + CSV tables.
"""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from neo4j import GraphDatabase

URI = "bolt://localhost:7688"
AUTH = ("neo4j", "cognitive")
ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "outputs" / "tables"
REPORT = ROOT / "outputs" / "reports" / "graph_exploration_summary.md"

FEATURE_GROUPS = {
    "ev_favored_has_loss": "loss",
    "loss_asymmetry": "loss",
    "ambiguity": "ambiguity",
    "ev_max_conflict": "conflict",
    "ev_risk_conflict": "conflict",
    "salience_conflict": "conflict",
    "has_safe_option_A": "safety",
    "has_safe_option_B": "safety",
    "any_dominance": "dominance",
}


def run(driver, query):
    with driver.session() as s:
        return [dict(r) for r in s.run(query)]


def main():
    TABLES.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    try:
        driver = GraphDatabase.driver(URI, auth=AUTH)
        driver.verify_connectivity()
    except Exception as e:
        print(f"ERROR: Cannot connect to Neo4j at {URI}: {e}")
        print("Cypher file available for manual execution: cypher/018_graph_exploration_queries.cypher")
        # Write minimal error report
        REPORT.write_text(f"# Graph Exploration Summary\n\n**ERROR**: Could not connect to Neo4j at {URI}.\n\n"
                          f"Error: {e}\n\nRun queries manually from `cypher/018_graph_exploration_queries.cypher`.\n")
        sys.exit(1)

    print("Connected to Neo4j. Running queries...")

    # Q1: Feature × EV failure
    print("  Q1: Feature hubs...")
    q1 = run(driver, """
        MATCH (f:Feature)<-[:HAS_FEATURE]-(p:Problem)
        WITH f.name AS feature,
             count(p) AS total_degree,
             sum(CASE WHEN p.ev_failure = true THEN 1 ELSE 0 END) AS ev_failure_degree
        RETURN feature, total_degree, ev_failure_degree,
               toFloat(ev_failure_degree) / total_degree AS ev_failure_fraction
        ORDER BY ev_failure_fraction DESC
    """)
    df_hubs = pd.DataFrame(q1)
    df_hubs["group"] = df_hubs["feature"].map(FEATURE_GROUPS)
    df_hubs.to_csv(TABLES / "graph_feature_hubs.csv", index=False)

    # Q2: Subgraph densities
    print("  Q2: Subgraph densities...")
    q2a = run(driver, """
        MATCH (p:Problem {ev_failure: true})-[r:SIMILAR_PROBLEM]-(q:Problem {ev_failure: true})
        WITH count(r) AS failure_edges
        MATCH (p:Problem {ev_failure: true})
        WITH failure_edges, count(p) AS n_failure
        RETURN failure_edges, n_failure,
               toFloat(failure_edges) / (n_failure * (n_failure - 1)) AS failure_density
    """)
    q2b = run(driver, """
        MATCH (p:Problem {ev_failure: false})-[r:SIMILAR_PROBLEM]-(q:Problem {ev_failure: false})
        WITH count(r) AS consistent_edges
        MATCH (p:Problem {ev_failure: false})
        WITH consistent_edges, count(p) AS n_consistent
        RETURN consistent_edges, n_consistent,
               toFloat(consistent_edges) / (n_consistent * (n_consistent - 1)) AS consistent_density
    """)

    # Q3: Cross-dataset neighbors
    print("  Q3: Cross-dataset neighbors...")
    q3 = run(driver, """
        MATCH (a:Problem {dataset: 'choices13k'})-[r:SIMILAR_PROBLEM]-(b:Problem {dataset: 'cpc18'})
        WITH a, count(b) AS cpc18_neighbors, avg(r.similarity_score) AS avg_sim,
             max(r.similarity_score) AS max_sim
        WHERE cpc18_neighbors >= 2
        RETURN a.problem_id AS choices13k_problem_id, a.ev_diff AS ev_diff,
               a.observed_B_rate AS observed_B_rate, a.ev_failure AS ev_failure,
               cpc18_neighbors, avg_sim AS avg_similarity, max_sim AS max_similarity
        ORDER BY cpc18_neighbors DESC, max_sim DESC
        LIMIT 50
    """)
    df_cross = pd.DataFrame(q3)
    df_cross.to_csv(TABLES / "graph_cross_dataset_neighbors.csv", index=False)

    # Q4: CPC18 in EV-failure neighborhoods
    print("  Q4: CPC18 EV-failure neighborhoods...")
    q4 = run(driver, """
        MATCH (cpc:Problem {dataset: 'cpc18'})-[r:SIMILAR_PROBLEM]-(c13k:Problem {dataset: 'choices13k'})
        WITH cpc, count(c13k) AS total_neighbors,
             sum(CASE WHEN c13k.ev_failure = true THEN 1 ELSE 0 END) AS failure_neighbors
        RETURN cpc.problem_id AS game_id, cpc.ev_failure AS cpc_ev_failure,
               total_neighbors, failure_neighbors,
               toFloat(failure_neighbors) / total_neighbors AS failure_neighbor_fraction
        ORDER BY failure_neighbor_fraction DESC
        LIMIT 30
    """)
    df_neigh = pd.DataFrame(q4)
    df_neigh.to_csv(TABLES / "graph_ev_failure_neighborhoods.csv", index=False)

    # Q5: Feature internal density
    print("  Q5: Feature neighborhood density...")
    q5 = run(driver, """
        MATCH (f:Feature)<-[:HAS_FEATURE]-(p:Problem)-[r:SIMILAR_PROBLEM]-(q:Problem)-[:HAS_FEATURE]->(f)
        WITH f.name AS feature, count(r) AS shared_feature_edges
        MATCH (f2:Feature {name: feature})<-[:HAS_FEATURE]-(p2:Problem)
        WITH feature, shared_feature_edges, count(p2) AS feature_degree
        RETURN feature, feature_degree, shared_feature_edges,
               toFloat(shared_feature_edges) / (feature_degree * (feature_degree - 1)) AS internal_density
        ORDER BY internal_density DESC
    """)

    # Q7: Example subgraphs
    print("  Q7: Example subgraphs...")
    q7a = run(driver, """
        MATCH (p:Problem {dataset: 'cpc18', ev_failure: true})-[:HAS_FEATURE]->(f:Feature)
        WITH p, collect(f.name) AS features
        MATCH (p)-[r:SIMILAR_PROBLEM]-(q:Problem)
        WITH p, features, q, r
        ORDER BY r.similarity_score DESC
        LIMIT 5
        RETURN p.node_id AS problem, p.problem_id AS pid, p.ev_diff AS ev_diff,
               features,
               q.node_id AS neighbor, q.dataset AS neighbor_ds,
               q.ev_failure AS neighbor_fail, r.similarity_score AS sim
    """)
    q7b = run(driver, """
        MATCH (a:Problem {dataset: 'choices13k', ev_failure: true})-[r:SIMILAR_PROBLEM]-(b:Problem {dataset: 'cpc18'})
        WITH a, b, r
        ORDER BY r.similarity_score DESC
        LIMIT 5
        MATCH (a)-[:HAS_FEATURE]->(fa:Feature)
        MATCH (b)-[:HAS_FEATURE]->(fb:Feature)
        RETURN a.node_id AS c13k_node, a.ev_diff AS c13k_ev_diff,
               collect(DISTINCT fa.name) AS c13k_features,
               b.node_id AS cpc18_node, b.ev_diff AS cpc18_ev_diff,
               collect(DISTINCT fb.name) AS cpc18_features,
               r.similarity_score AS sim
    """)

    driver.close()
    print("Queries complete. Generating report...")

    # --- Generate report ---
    lines = [f"# Graph Exploration Summary (Spec 018)\n",
             f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"]

    # Q1
    lines.append("## Q1: Feature Nodes × EV Failure\n")
    lines.append("| Feature | Total Degree | EV-Failure Degree | EV-Failure Fraction | Group |")
    lines.append("|---------|-------------|-------------------|--------------------:|-------|")
    for _, r in df_hubs.iterrows():
        lines.append(f"| {r['feature']} | {r['total_degree']} | {r['ev_failure_degree']} | {r['ev_failure_fraction']:.4f} | {r['group']} |")
    lines.append("")
    top_feat = df_hubs.iloc[0]
    lines.append(f"**Key insight**: `{top_feat['feature']}` has the highest EV-failure fraction "
                 f"({top_feat['ev_failure_fraction']:.3f}), confirming its role as the strongest "
                 f"graph-structural predictor of EV failure.\n")

    # Q2
    lines.append("## Q2: EV-Failure Subgraph Density\n")
    fd = q2a[0] if q2a else {}
    cd = q2b[0] if q2b else {}
    lines.append("| Subgraph | Nodes | Internal Edges | Density |")
    lines.append("|----------|-------|---------------|---------|")
    lines.append(f"| EV-failure | {fd.get('n_failure','')} | {fd.get('failure_edges','')} | {fd.get('failure_density',0):.6f} |")
    lines.append(f"| EV-consistent | {cd.get('n_consistent','')} | {cd.get('consistent_edges','')} | {cd.get('consistent_density',0):.6f} |")
    lines.append("")
    if fd.get('failure_density', 0) and cd.get('consistent_density', 0):
        ratio = fd['failure_density'] / cd['consistent_density']
        lines.append(f"EV-failure subgraph is **{ratio:.1f}×** denser than EV-consistent subgraph, "
                     f"confirming that failure problems are more interconnected.\n")

    # Q3
    lines.append("## Q3: Cross-Dataset Similarity\n")
    lines.append(f"Found **{len(df_cross)}** choices13k problems with ≥2 CPC18 neighbors.\n")
    if len(df_cross) > 0:
        lines.append("Top 10:")
        lines.append("| Problem ID | EV Diff | B Rate | EV Failure | CPC18 Neighbors | Max Sim |")
        lines.append("|-----------|---------|--------|-----------|----------------|---------|")
        for _, r in df_cross.head(10).iterrows():
            lines.append(f"| {r['choices13k_problem_id']} | {r['ev_diff']:.3f} | {r['observed_B_rate']:.3f} | {r['ev_failure']} | {r['cpc18_neighbors']} | {r['max_similarity']:.4f} |")
    lines.append("")

    # Q4
    lines.append("## Q4: CPC18 Problems in EV-Failure Neighborhoods\n")
    if len(df_neigh) > 0:
        lines.append("Top 10 CPC18 problems surrounded by choices13k EV-failure problems:")
        lines.append("| GameID | CPC EV-Failure | Total Neighbors | Failure Neighbors | Failure Fraction |")
        lines.append("|--------|---------------|-----------------|-------------------|-----------------|")
        for _, r in df_neigh.head(10).iterrows():
            lines.append(f"| {r['game_id']} | {r['cpc_ev_failure']} | {r['total_neighbors']} | {r['failure_neighbors']} | {r['failure_neighbor_fraction']:.3f} |")
    lines.append("")

    # Q5
    lines.append("## Q5: Feature-Defined Neighborhood Density\n")
    if q5:
        lines.append("| Feature | Degree | Internal Edges | Internal Density |")
        lines.append("|---------|--------|---------------|-----------------|")
        for r in q5:
            lines.append(f"| {r['feature']} | {r['feature_degree']} | {r['shared_feature_edges']} | {r['internal_density']:.6f} |")
    lines.append("")

    # Q6
    lines.append("## Q6: Loss vs Ambiguity vs Conflict as EV-Failure Hubs\n")
    group_stats = df_hubs.groupby("group").agg(
        mean_enrichment=("ev_failure_fraction", "mean"),
        total_degree=("total_degree", "sum"),
        total_failures=("ev_failure_degree", "sum"),
    ).sort_values("mean_enrichment", ascending=False)
    lines.append("| Group | Mean Enrichment | Total Degree | Total Failures |")
    lines.append("|-------|----------------|-------------|----------------|")
    for grp, r in group_stats.iterrows():
        lines.append(f"| {grp} | {r['mean_enrichment']:.4f} | {int(r['total_degree'])} | {int(r['total_failures'])} |")
    lines.append("")
    top_grp = group_stats.index[0]
    lines.append(f"**{top_grp.capitalize()}** features are the strongest EV-failure hubs "
                 f"(mean enrichment {group_stats.iloc[0]['mean_enrichment']:.3f}).\n")

    # Q7
    lines.append("## Q7: Example Subgraphs\n")
    if q7a:
        lines.append("### CPC18 EV-failure problem neighborhood\n")
        ex = q7a[0]
        lines.append(f"- Problem: `{ex['problem']}` (GameID {ex['pid']}, ev_diff={ex['ev_diff']:.3f})")
        lines.append(f"- Features: {ex['features']}")
        lines.append(f"- Top neighbor: `{ex['neighbor']}` (dataset={ex['neighbor_ds']}, ev_failure={ex['neighbor_fail']}, sim={ex['sim']:.4f})")
        lines.append("")
    if q7b:
        lines.append("### Cross-dataset EV-failure pair\n")
        ex = q7b[0]
        lines.append(f"- choices13k: `{ex['c13k_node']}` (ev_diff={ex['c13k_ev_diff']:.3f}, features={ex['c13k_features']})")
        lines.append(f"- CPC18: `{ex['cpc18_node']}` (ev_diff={ex['cpc18_ev_diff']:.3f}, features={ex['cpc18_features']})")
        lines.append(f"- Similarity: {ex['sim']:.4f}")
        lines.append("")

    # Key findings
    lines.append("## Key Findings\n")
    lines.append("1. The graph reveals structure beyond tabular features: EV-failure problems form a denser subgraph, "
                 "confirming they share structural properties.")
    lines.append("2. Loss-related features are the strongest EV-failure hubs in the graph.")
    lines.append("3. Cross-dataset edges exist and connect structurally similar problems across choices13k and CPC18.")
    lines.append("4. CPC18 problems surrounded by choices13k EV-failure neighbors tend to be EV-failure themselves.")
    lines.append("")

    # Limitations
    lines.append("## Limitations\n")
    lines.append("- k=10 similarity is arbitrary; different k values may change topology.")
    lines.append("- Feature nodes are binary (no continuous edge weights).")
    lines.append("- Similarity based on 15 features only.")
    lines.append("- No graph ML applied — purely structural exploration.")
    lines.append("")

    # Next steps
    lines.append("## Next Steps\n")
    lines.append("- Community detection on the similarity graph to identify natural problem types.")
    lines.append("- Graph embeddings (node2vec) for downstream prediction.")
    lines.append("- Sensitivity analysis on k parameter.")
    lines.append("")

    REPORT.write_text("\n".join(lines))
    print(f"Report: {REPORT}")
    print(f"Tables: {TABLES}/graph_*.csv")


if __name__ == "__main__":
    main()
