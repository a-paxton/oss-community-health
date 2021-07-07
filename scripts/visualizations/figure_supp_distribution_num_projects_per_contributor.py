import numpy as np
import pandas as pd
from utils_graphs import compute_contributions_per_project
import matplotlib.pyplot as plt
from matplotlib import ticker


data = pd.read_csv("results/data/sentiment_frame_original.tsv", sep="\t")

###############################################################################
# First, draw a heatmap of the number of people that contribute to eac

all_authors_mapping = {
    a: i for i, a in enumerate(np.unique(data["author_name"]))}

contributions_per_projects = compute_contributions_per_project(data)
number_of_projects_contributed_to = (
    contributions_per_projects != 0).sum(axis=1).values

fig, ax = plt.subplots()
ax.hist(number_of_projects_contributed_to, bins=np.arange(1, 10), align="left",
        color="0")
ax.set_xlabel("Number of projects", fontweight="bold")
ax.set_ylabel("Number of contributors", fontweight="bold")
ax.spines["right"].set_linewidth(0)
ax.spines["top"].set_linewidth(0)
ax.set_ylim(0, 20000)
ylim = ax.get_ylim()
ax.yaxis.set_major_locator(
    ticker.MultipleLocator(5000))
ax.tick_params(labelsize=8)

fig.savefig("figures/supp/distribution_num_projects_per_contributor.pdf")
