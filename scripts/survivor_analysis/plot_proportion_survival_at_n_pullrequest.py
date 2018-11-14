import argparse
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from glob import glob
from utils import visualization


parser = argparse.ArgumentParser()
parser.add_argument("--n-pull-request", "-n", default=2, type=int)
parser.add_argument("--outname", "-o")
args = parser.parse_args()

outname = args.outname
num_pull_request = args.n_pull_request

filenames = glob("data/raw_data/*/issues.tsv")

fig, ax = plt.subplots()
labels = []
survival_proportion = []
for i, filename in enumerate(filenames):
    labels.append(filename.split("/")[1])
    all_issues = pd.read_csv(filename, sep="\t")
    pull_requests = all_issues[all_issues["type"] == "pull_request"]

    _, num_pull_request_per_authors = np.unique(
        pull_requests["author_id"],
        return_counts=True)

    survival_proportion.append(
        (num_pull_request_per_authors >= num_pull_request).sum() /
        len(num_pull_request_per_authors))

survival_proportion = np.array(survival_proportion) * 100
labels = np.array(labels)
idx = np.argsort(survival_proportion)
ax.bar(np.arange(len(survival_proportion)), survival_proportion[idx],
       color="#000000")
ax.set_xticks(np.arange(len(survival_proportion)))
ax.set_xticklabels(labels[idx], fontsize="x-small", rotation=30,
                   horizontalalignment="right")
visualization.format_ax(ax)
ax.legend()
ax.set_title(
    "Proportion of contributors that opened more than %d pull requests" %
    num_pull_request,
    fontweight="bold", fontsize="small")
ax.set_ylabel("% of contributors", fontsize="small",
              fontweight="bold")


if outname is not None:
    try:
        os.makedirs(os.path.dirname(outname))
    except OSError:
        pass

    fig.savefig(outname)
