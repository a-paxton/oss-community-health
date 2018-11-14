import argparse
import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt

from utils import annotate
from utils import visualization

parser = argparse.ArgumentParser()
parser.add_argument("project")
parser.add_argument("--type", "-t", default="pull_request")
parser.add_argument("--outname", "-o")
args = parser.parse_args()

project = args.project
ticket_type = args.type
outname = args.outname


tickets = pd.read_csv("data/%s/issues.tsv" % project, sep="\t")
comments = pd.read_csv("data/%s/comments.tsv" % project, sep="\t")

comments, tickets = annotate.annotate_comments_tickets(comments, tickets)
tickets = tickets[tickets["type"] == ticket_type]
open_duration = np.array(
    [t.days for t in tickets["open_duration"]
     if not type(t) == float])
open_duration[open_duration > 200] = 200

fig, ax = plt.subplots()
ax.hist(open_duration, color="#000000", bins=100)
visualization.format_ax(ax)
ax.set_xlabel("Number of days before a ticket is closed (capped at 200)",
              fontweight="bold", fontsize="small")
ax.set_ylabel("Number of tickets", fontweight="bold", fontsize="small")
ax.set_title(project, fontweight="bold")

if outname is not None:
    try:
        os.makedirs(os.path.dirname(outname))
    except OSError:
        pass

    fig.savefig(outname)
