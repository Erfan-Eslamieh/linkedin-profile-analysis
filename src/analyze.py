import json
from itertools import combinations
from pathlib import Path
import matplotlib.pyplot as plt
import networkx as nx
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score

# everyone works here now, so it says nothing about who is close to whom
COMMON_EMPLOYER = "parsa data systems"

with open("data/profiles.json", encoding="utf-8") as f:
    profiles = json.load(f)
Path("output").mkdir(exist_ok=True)


def norm(text):
    return text.strip().lower()


# ---- 1. build the graph ----------------------------------------------
G = nx.Graph()
G.add_nodes_from(p["name"] for p in profiles)


def add_link(a, b, weight):
    if G.has_edge(a, b):
        G[a][b]["weight"] += weight
    else:
        G.add_edge(a, b, weight=weight)


# link 1: one person commented on / replied to / mentioned another (weight 2)
# the graph is undirected, so who wrote to whom is not kept
for p in profiles:
    for act in p["activity"]:
        for other in act["mentioned"]:
            add_link(p["name"], other, 2)

# link 2: same earlier employer or same university (weight 1)
groups = {}
for p in profiles:
    for job in p["experiences"]:
        if norm(job["company"]) != COMMON_EMPLOYER:
            groups.setdefault(norm(job["company"]), set()).add(p["name"])
    for edu in p["education"]:
        groups.setdefault(norm(edu["institution"]), set()).add(p["name"])
for people in groups.values():
    for a, b in combinations(sorted(people), 2):
        add_link(a, b, 1)

# ---- 2. key people (centrality) --------------------------------------
degree = nx.degree_centrality(G)
# betweenness is unweighted on purpose, because networkx would read a weight
# as a distance, and here a bigger weight means a closer tie
betweenness = nx.betweenness_centrality(G)
pagerank = nx.pagerank(G, weight="weight")

# ---- 3. cluster people by skills -------------------------------------
skills = [[s.lower() for s in p["skills"]] for p in profiles]
X = TfidfVectorizer(analyzer=lambda x: x).fit_transform(skills)  # one skill = one word

# pick the number of clusters with the silhouette score instead of fixing it
scores = {}
for k in range(2, min(6, len(profiles))):
    tmp = KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(X)
    scores[k] = silhouette_score(X, tmp)
best_k = max(scores, key=scores.get)  # on a tie, the smaller k wins
print("silhouette by k:", {k: round(v, 2) for k, v in scores.items()}, "-> k =", best_k)

labels = KMeans(n_clusters=best_k, n_init=10, random_state=42).fit_predict(X)
cluster = {p["name"]: int(l) for p, l in zip(profiles, labels)}

# ---- 4. save the results ---------------------------------------------
pos = nx.spring_layout(G, seed=42, k=1.5)
plt.figure(figsize=(12, 8))
nx.draw_networkx_edges(G, pos, edge_color="lightgray",
                       width=[0.5 + min(G[a][b]["weight"], 8) * 0.6 for a, b in G.edges])
nx.draw_networkx_nodes(G, pos, node_color=[cluster[n] for n in G], cmap=plt.cm.Set2,
                       node_size=[600 + 5000 * betweenness[n] for n in G], edgecolors="black")
label_pos = {n: (x, y - 0.1) for n, (x, y) in pos.items()}  # names under the circles
nx.draw_networkx_labels(G, label_pos, font_size=9)
plt.title("Connection graph (size = betweenness, color = skill cluster)")
plt.axis("off")
plt.tight_layout()
plt.savefig("output/graph.png", dpi=150)

table = [{"name": n, "cluster": cluster[n], "degree": round(degree[n], 2),
          "betweenness": round(betweenness[n], 2), "pagerank": round(pagerank[n], 2)}
         for n in G]
table.sort(key=lambda r: r["betweenness"], reverse=True)

with open("output/graph.json", "w", encoding="utf-8") as f:
    json.dump({"nodes": table,
               "edges": [[a, b, d["weight"]] for a, b, d in G.edges(data=True)]},
              f, indent=2, ensure_ascii=False)

with open("output/report.md", "w", encoding="utf-8") as f:
    f.write("# Report\n\n")
    f.write(f"Graph: {G.number_of_nodes()} people, {G.number_of_edges()} links.\n\n")
    f.write("| Person | Cluster | Degree | Betweenness | PageRank |\n|---|---|---|---|---|\n")
    for r in table:
        f.write(f"| {r['name']} | {r['cluster']} | {r['degree']} | {r['betweenness']} | {r['pagerank']} |\n")

    f.write(f"\n## Clusters (k = {best_k}, chosen by silhouette score)\n")
    for c in range(best_k):
        members = [n for n in G if cluster[n] == c]
        note = " (single-person cluster, an outlier by skills)" if len(members) == 1 else ""
        f.write(f"- Cluster {c}: {', '.join(members)}{note}\n")

    f.write("\n## Interpretation\n")
    f.write(f"{table[0]['name']} has the highest betweenness ({table[0]['betweenness']}), "
            f"followed by {table[1]['name']} ({table[1]['betweenness']}). "
            "With only 10 people and a dense graph, the gaps between ranks are small, "
            "so the ranking shows how the method works and is not a strong finding.\n")

    f.write("\n## Notes\n")
    f.write("- Profile 1 is a real public profile. Profiles 2 to 10 are synthetic, so these "
            "results demonstrate the pipeline and say nothing about a real organization.\n")
    f.write("- Links are undirected. An interaction (mention, comment, reply) adds weight 2, "
            "a shared past employer or institution adds weight 1.\n")
    f.write("- Betweenness ignores weights. PageRank uses them.\n")
    f.write(f"- Clusters use skills only. Even the best silhouette score is low ({scores[best_k]:.2f}), "
            "so there is no clear natural grouping in this small sample.\n")
    f.write("- Ranks with equal rounded betweenness are ties, and their order in the table is arbitrary.\n")

print("Top 3 by betweenness:", [r["name"] for r in table[:3]])
print("Saved output/graph.png, output/graph.json, output/report.md")