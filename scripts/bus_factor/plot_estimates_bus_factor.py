from glob import glob
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
from utils import project_features

"""
"""

parser = argparse.ArgumentParser()
parser.add_argument("--outname", "-o")
args = parser.parse_args()

outname = args.outname

filenames = glob("data/raw_data/*/commits.tsv")
filenames.sort()

labels = []
fig, ax = plt.subplots()
for i, filename in enumerate(filenames):

    # Parse project name
    project = filename.split("/")[2].split("_")[0]

    commits = pd.read_csv(filename, sep="\t", keep_default_na=False)
    bus_factor = project_features.compute_bus_factor(commits)
    labels.append(project)
    ax.bar([i],
           [bus_factor],
           label=project,
           color="C%d" % i,
           zorder=10)

ax.set_title("Bus factor estimation", fontweight="bold",
             fontsize="large")

ax.spines['right'].set_color('none')
ax.spines['left'].set_color('none')
ax.spines['top'].set_color('none')
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')
ax.set_xticks(np.arange(len(filenames)))
ax.set_xticklabels(labels, rotation=25, fontsize="small", fontweight="bold",
                   color="0.5", horizontalalignment="right")
ax.set_ylabel("Bus factor estimation", color="0.5", fontweight="bold",
              fontsize="medium")
ax.grid(which='major', axis='y', linewidth=0.75, linestyle='-',
        color='0.5')

if outname is not None:
    try:
        os.makedirs(os.path.dirname(outname))
    except OSError:
        pass

    fig.savefig(outname)
