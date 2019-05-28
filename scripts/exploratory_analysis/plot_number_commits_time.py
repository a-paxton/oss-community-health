"""
Plotting the number of commits for each project every three months
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
commits = pd.read_csv(filename, sep="\t")
# Now load the bot names
bots = pd.read_csv("../bot_names.txt")

commits["total"] = np.ones(len(commits))
commits["bots"] = np.isin(commits["author_name"], bots.values).astype(int)
commits["date"] = pd.DatetimeIndex(commits["date"])
commits.set_index("date", inplace=True)
sampled_commits = commits.resample(
    '3M').sum().replace(np.nan, 0).astype(int)
if len(sampled_commits) < 12:
    sampled_commits = commits.resample(
        'W').sum().replace(np.nan, 0).astype(int)

fig, ax = plt.subplots(figsize=(6, 3), tight_layout=True)

ax.bar(np.arange(sampled_commits.shape[0]),
       sampled_commits["total"],
       color="#C1C1C1")
ax.bar(np.arange(sampled_commits.shape[0]),
       sampled_commits["total"] - sampled_commits["bots"],
       color="#000000")

ax.set_xticks(np.arange(0, len(sampled_commits), 4))
ax.set_xticklabels(
    sampled_commits.index.strftime("%b %Y")[::4], rotation=45,
    horizontalalignment="right",
    fontsize="small")
ax.set_title("%s (Commits)" % (project, ), fontweight="bold")
ax.set_ylabel("Number of Commits", fontweight="bold")
ax.spines["right"].set_linewidth(0)
ax.spines["top"].set_linewidth(0)

if outname is not None:
    try:
        os.makedirs(os.path.dirname(outname))
    except OSError:
        pass
    fig.savefig(outname)
