from glob import glob
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse

"""
This is a reproduction of Fernando's 2011 normalized commit rate plot. This
shows roughly the bus factor
"""

parser = argparse.ArgumentParser()
parser.add_argument("--outname", "-o")
args = parser.parse_args()

outname = args.outname

filenames = glob("data/raw_data/*/commits.tsv")
filenames.sort()

fig, ax = plt.subplots()
for i, filename in enumerate(filenames):

    # Parse project name
    project = filename.split("/")[2].split("_")[0]

    commits = pd.read_csv(filename, sep="\t", keep_default_na=False)
    commits[commits["author_name"].isnull()]["author_name"] = ""
    _, ticket_counts = np.unique(commits["author_name"], return_counts=True)
    ticket_counts.sort()
    ticket_counts = ticket_counts[::-1] / ticket_counts.max()
    ax.plot(ticket_counts[:15] * 100,
            label=project,
            marker=".", color="C%d" % i,
            linewidth=2)

ax.set_xlim(0, 20)
ax.legend()
ax.set_title("Normalized commit rates", fontweight="bold",
             fontsize="large")

ax.set_xticks(np.arange(0, 21, 5))
ax.set_yticks([0, 50, 100])
[ax.axhline(i, color="0", alpha=0.3, linewidth=1, zorder=-1)
 for i in (0, 50, 100)]
ax.set_ylim(-1, 105)
ax.spines['right'].set_color('none')
ax.spines['left'].set_color('none')
ax.spines['top'].set_color('none')
ax.spines['bottom'].set_color('none')
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')
ax.grid(which='major', axis='y', linewidth=0.75, linestyle='-',
        color='0.5')
ax.set_xticklabels(["%d" % i for i in np.arange(0, 20, 5)], fontsize="medium",
                   fontweight="bold", color="0.5")
ax.set_yticklabels(["%d%%" % i for i in (0, 50, 100)], fontsize="medium",
                   fontweight="bold", color="0.5")
ax.set_xlabel("Contributors", fontsize="medium", fontweight="bold",
              color="0.5")

if outname is not None:
    try:
        os.makedirs(os.path.dirname(outname))
    except OSError:
        pass

    fig.savefig(outname)
