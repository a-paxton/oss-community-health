import argparse
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("project")
parser.add_argument("--outname", "-o")
args = parser.parse_args()

project = args.project
outname = args.outname

filename = os.path.join("data/raw_data", project, "commits.tsv")
commits = pd.read_csv(filename, sep="\t")

commits["total"] = np.ones(len(commits))
commits["date"] = pd.DatetimeIndex(commits["date"])
commits.set_index("date", inplace=True)
commits = commits.resample(
    '3M').sum().replace(np.nan, 0).astype(int)

fig, ax = plt.subplots(figsize=(6, 3), tight_layout=True)
ax.bar(np.arange(commits.shape[0]), commits["total"], color="black")
ax.set_xticks(np.arange(0, len(commits), 4))
ax.set_xticklabels(
    commits.index.strftime("%Y")[::4], rotation=45,
    horizontalalignment="right",
    fontsize="small")
ax.set_title("%s (Commits)" % (project, ), fontweight="bold")
ax.set_ylabel("Number of commits", fontweight="bold")
ax.spines["right"].set_linewidth(0)
ax.spines["top"].set_linewidth(0)

if outname is not None:
    try:
        os.makedirs(os.path.dirname(outname))
    except OSError:
        pass
    fig.savefig(outname)