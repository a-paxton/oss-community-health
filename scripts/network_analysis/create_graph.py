import pandas as pd
from joblib import Memory
import numpy as np
from utils import create_graph
from utils import compute_contributions_per_project

mem = Memory(".cache")


print("Loading data")
data = pd.read_csv("results/data/sentiment_frame_original.tsv", sep="\t")
# First, do some sanity check on this file. Ticket_id should be unique per
# project for posts.
assert np.all(data[data["type_family"] == "post"].groupby(
    ["project", "ticket_id"]).count().to_numpy() == 1)


print("Computing the number of contributiors per project per user")
contributions_per_project = mem.cache(compute_contributions_per_project)(data)

# Select users that have contributed to more than one project
#authors_of_interest = np.array(
#    contributions_per_project.loc[
#        np.sum(contributions_per_project != 0, axis=1) > 1].index)
# Select contributions from authors of interest
#data = data.loc[np.isin(data["author_name"], authors_of_interest)]
# data = data.loc[np.isin(data["project"],
#                ["sphinx-gallery", "mayavi",
#                 "scikit-image"])]


print("Estimating adjacency matrix")
all_authors_mapping = {
    a: i for i, a in enumerate(np.unique(data["author_name"]))}
adjacency_matrix = mem.cache(create_graph)(data, all_authors_mapping)
contributions_per_project = compute_contributions_per_project(data)


# Remove the diagonal
#adjacency_matrix[np.diag_indices_from(adjacency_matrix)] = 0


###############################################################################
# Ok… Let's try a simple visualization with Matplotlib & Grave
import matplotlib.pyplot as plt
import networkx
from networkx.algorithms.centrality import closeness_centrality
import grave

all_projects = contributions_per_project.columns
graph = networkx.convert_matrix.from_numpy_matrix(np.log(adjacency_matrix+1))
# Add some information

colors_projects = {"matplotlib": "C0",
                   "sphinx-gallery": "C1",
                   "mayavi": "C2",
                   "scikit-image": "C3",
                   "numpy": "C4",
                   "scipy": "C5",
                   "pandas": "C6",
                   "scikit-learn": "C7"}
            

for node, nodes_attr in graph.nodes(data=True):
    nodes_attr["author_name"] = contributions_per_project.iloc[node].name
    nodes_attr["main_project"] = all_projects[contributions_per_project.values.argmax(
        axis=1)[node]]
    nodes_attr["color"] = colors_projects[nodes_attr["main_project"]]
    # nodes_attr["size"] = 2+np.log(contributions_per_project.iloc[node].max() + 1)
    nodes_attr["linewidth"] = 0
   

# Let's attempt to put some alpha on the edge based on some closeness
# centrality
centrality = closeness_centrality(graph)
max_centrality = max(centrality.values())
for u, v, edge_attributes in graph.edges.data():
    c = (centrality[u] +
         centrality[v]) / 2
    color_idx = (c / max_centrality)
    cmap = plt.get_cmap("gray")
    edge_attributes['width'] = 1
    edge_attributes["alpha"] = 0.5

networkx.write_gexf(graph, "test.gexf")
networkx.write_gml(graph, "test.gml")
stop

fig, axes = plt.subplots()
grave.plot_network(graph, ax=axes, layout="kamada_kawai",
                   node_style=grave.use_attributes(),
                   edge_style=grave.use_attributes())

fig, axes = plt.subplots()
grave.plot_network(graph, ax=axes, layout="circular",
                   node_style=grave.use_attributes(),
                   edge_style=grave.use_attributes())



