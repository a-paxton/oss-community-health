import argparse
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from glob import glob
from utils import visualization


parser = argparse.ArgumentParser()
parser.add_argument("--outname", "-o")
args = parser.parse_args()

outname = args.outname

filenames = glob("data/*/issues.tsv")

fig, ax = plt.subplots()
for filename in filenames:
    label = filename.split("/")[1]
    all_issues = pd.read_csv(filename, sep="\t")
    pull_requests = all_issues[all_issues["type"] == "pull_request"]

    _, num_pull_request_per_authors = np.unique(
        pull_requests["author_id"],
        return_counts=True)

    survival_data = [
        ((num_pull_request_per_authors > i).sum() /
         len(num_pull_request_per_authors))
        for i in np.arange(0, num_pull_request_per_authors.max() + 1)]

    ax.plot(np.arange(len(survival_data)) + 1, survival_data, label=label)

visualization.format_ax(ax)
ax.set_xscale("log")
ax.legend()
ax.set_title("Survival analysis", fontweight="bold")
ax.set_xlabel("Number of pull requests opened (log scale)", fontsize="small",
              fontweight="bold")
ax.set_ylabel("Survival rate", fontsize="small",
              fontweight="bold")


if outname is not None:
    try:
        os.makedirs(os.path.dirname(outname))
    except OSError:
        pass

    fig.savefig(outname)
