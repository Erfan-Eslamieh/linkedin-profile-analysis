# Report

Graph: 10 people, 21 links.

| Person | Cluster | Degree | Betweenness | PageRank |
|---|---|---|---|---|
| Zahra Mousavi | 0 | 0.67 | 0.15 | 0.15 |
| Sara Karimi | 1 | 0.56 | 0.12 | 0.12 |
| Erfan Eslamieh | 1 | 0.44 | 0.07 | 0.05 |
| Reza Mohammadi | 0 | 0.56 | 0.07 | 0.14 |
| Ali Rezaei | 2 | 0.56 | 0.07 | 0.08 |
| Amir Sadeghi | 3 | 0.44 | 0.06 | 0.1 |
| Maryam Nazari | 4 | 0.33 | 0.05 | 0.07 |
| Hossein Jafari | 1 | 0.33 | 0.04 | 0.08 |
| Mohammad Ahmadi | 2 | 0.44 | 0.02 | 0.12 |
| Fatemeh Hosseini | 3 | 0.33 | 0.02 | 0.1 |

## Clusters (k = 5, chosen by silhouette score)
- Cluster 0: Reza Mohammadi, Zahra Mousavi
- Cluster 1: Erfan Eslamieh, Sara Karimi, Hossein Jafari
- Cluster 2: Mohammad Ahmadi, Ali Rezaei
- Cluster 3: Fatemeh Hosseini, Amir Sadeghi
- Cluster 4: Maryam Nazari (single-person cluster, an outlier by skills)

## Interpretation
Zahra Mousavi has the highest betweenness (0.15), followed by Sara Karimi (0.12). With only 10 people and a dense graph, the gaps between ranks are small, so the ranking shows how the method works and is not a strong finding.

## Notes
- Profile 1 is a real public profile. Profiles 2 to 10 are synthetic, so these results demonstrate the pipeline and say nothing about a real organization.
- Links are undirected. An interaction (mention, comment, reply) adds weight 2, a shared past employer or institution adds weight 1.
- Betweenness ignores weights. PageRank uses them.
- Clusters use skills only. Even the best silhouette score is low (0.14), so there is no clear natural grouping in this small sample.
- Ranks with equal rounded betweenness are ties, and their order in the table is arbitrary.
