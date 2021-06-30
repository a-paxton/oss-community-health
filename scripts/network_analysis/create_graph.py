import pandas as pd
import itertools
import numpy as np


data = pd.read_csv("results/data/sentiment_frame_original.tsv", sep="\t")

# First, do some sanity check on this file. Ticket_id should be unique per
# project for posts.
assert np.all(data[data["type_family"] == "post"].groupby(
    ["project", "ticket_id"]).count().to_numpy() == 1)

all_authors_mapping = {a: i for i, a in enumerate(np.unique(data["author_name"]))}

all_projects = np.unique(data["project"])
adjacency_matrix = np.zeros((len(all_authors_mapping), len(all_authors_mapping)))
for project in all_projects:
    print(project)
    project_data = data[data["project"] == project]
    project_data.replace(all_authors_mapping, inplace=True)

    print("Finished replacing authors")
    for ticket_id in np.unique(project_data["ticket_id"]):
        authors = np.unique(
            project_data[project_data["ticket_id"] ==
            ticket_id]["author_name"])
        for idx in itertools.product(authors, authors):
            adjacency_matrix[idx] += 1

# Remove the diagonal
adjacency_matrix[np.diag_indices_from(adjacency_matrix)] = 0
