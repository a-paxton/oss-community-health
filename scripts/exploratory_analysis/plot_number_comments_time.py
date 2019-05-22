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
##############################################################################
# Load stuff in memory.

filename = os.path.join("data/raw_data", project, "comments.tsv")
comments = pd.read_csv(filename, sep="\t")
# Now load the bot names
bots = pd.read_csv("../bot_names.txt")


comments["total"] = np.ones(len(comments))
comments["bots"] = np.isin(comments["author_name"], bots.values).astype(int)
comments["created_at"] = pd.DatetimeIndex(comments["created_at"])
comments.set_index("created_at", inplace=True)
comments = comments.resample(
    '2M').sum().replace(np.nan, 0).astype(int)

fig, ax = plt.subplots(figsize=(6, 3), tight_layout=True)
ax.bar(np.arange(comments.shape[0]), comments["total"], color="black")
ax.bar(np.arange(comments.shape[0]), comments["bots"], color="#AB0000")

ax.set_xticks(np.arange(0, len(comments), 4))
ax.set_xticklabels(
    comments.index.strftime("%b %Y")[::4], rotation=45,
    horizontalalignment="right",
    fontsize="small")
title = filename.split("/")[-2]
ax.set_title("%s (Comments)" % title, fontweight="bold")
ax.set_ylabel("Number of comments", fontweight="bold")
ax.spines["right"].set_linewidth(0)
ax.spines["top"].set_linewidth(0)

if outname is not None:
    try:
        os.makedirs(os.path.dirname(outname))
    except OSError:
        pass
    fig.savefig(outname)
