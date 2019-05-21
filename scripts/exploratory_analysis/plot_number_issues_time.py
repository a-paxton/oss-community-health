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

filename = os.path.join("data/raw_data", project, "issues.tsv")
issues = pd.read_csv(filename, sep="\t")

issues["total"] = np.ones(len(issues))
issues["created_at"] = pd.DatetimeIndex(issues["created_at"])
issues.set_index("created_at", inplace=True)
issues = issues.resample(
    'M').sum().replace(np.nan, 0).astype(int)

fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(np.arange(issues.shape[0]), issues["total"], color="black")
ax.set_xticks(np.arange(0, len(issues), 2))
ax.set_xticklabels(
    issues.index.strftime("%b %Y")[::2], rotation=45,
    horizontalalignment="right",
    fontsize="small")
title = filename.split("/")[-2]
ax.set_title(title, fontweight="bold")
ax.set_ylabel("Number of issues")

if outname is not None:
    try:
        os.makedirs(os.path.dirname(outname))
    except OSError:
        pass
    fig.savefig(outname)
