"""
Plotting the number of comments for each project every two months.
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
comments = pd.read_csv(filename, sep="\t")
# Now load the bot names
bots = pd.read_csv("../bot_names.txt")


comments["total"] = np.ones(len(comments))
comments["bots"] = np.isin(comments["author_name"], bots.values).astype(int)
comments["created_at"] = pd.DatetimeIndex(comments["created_at"])
comments.set_index("created_at", inplace=True)
sampled_comments = comments.resample(
    '2M').sum().replace(np.nan, 0).astype(int)
if len(sampled_comments) < 12:
    sampled_comments = comments.resample(
        'W').sum().replace(np.nan, 0).astype(int)


fig, ax = plt.subplots(figsize=(6, 3), tight_layout=True)
ax.bar(np.arange(sampled_comments.shape[0]),
       sampled_comments["total"],
       color="#C1C1C1")
ax.bar(np.arange(sampled_comments.shape[0]),
       sampled_comments["total"] - sampled_comments["bots"],
       color="#000000")

ax.set_xticks(np.arange(0, len(sampled_comments), 4))
ax.set_xticklabels(
    sampled_comments.index.strftime("%b %Y")[::4], rotation=45,
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
