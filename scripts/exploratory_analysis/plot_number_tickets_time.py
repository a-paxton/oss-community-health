"""
Plotting the number of issues every two months.
"""

import argparse
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("filename")
parser.add_argument("--outname", "-o")
args = parser.parse_args()

filename = args.filename
outname = args.outname

##############################################################################
# Load stuff in memory.
project = filename.split("/")[-2]
issues = pd.read_csv(filename, sep="\t")

# Now load the bot names
bots = pd.read_csv("../bot_names.txt")

issues["total"] = np.ones(len(issues))
issues["bots"] = np.isin(issues["author_name"], bots.values).astype(int)
issues["created_at"] = pd.DatetimeIndex(issues["created_at"])
issues.set_index("created_at", inplace=True)
sampled_issues = issues.resample(
    '2M').sum().replace(np.nan, 0).astype(int)
if len(sampled_issues) < 12:
    sampled_issues = issues.resample(
        'W').sum().replace(np.nan, 0).astype(int)

fig, ax = plt.subplots(figsize=(6, 3), tight_layout=True)
ax.bar(np.arange(sampled_issues.shape[0]),
       sampled_issues["total"],
       color="#C1C1C1")
ax.bar(np.arange(sampled_issues.shape[0]),
       sampled_issues["total"] - sampled_issues["bots"],
       color="#000000")
ax.set_xticks(np.arange(0, len(sampled_issues), 2))
ax.set_xticklabels(
    sampled_issues.index.strftime("%b %Y")[::2], rotation=45,
    horizontalalignment="right",
    fontsize="small")
title = filename.split("/")[-2]
ax.set_title("%s (issues)" % title, fontweight="bold")
ax.set_ylabel("Number of issues", fontweight="bold")
ax.spines["right"].set_linewidth(0)
ax.spines["top"].set_linewidth(0)

if outname is not None:
    try:
        os.makedirs(os.path.dirname(outname))
    except OSError:
        pass
    fig.savefig(outname)
