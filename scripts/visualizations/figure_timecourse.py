import pandas as pd
import os
import matplotlib.pyplot as plt

from matplotlib.gridspec import GridSpec
from matplotlib import patches
from matplotlib import lines
from utils_vis import plot_sentiment_timecourse
from utils_vis import add_letter_and_title
from utils import colors

model_results = pd.read_csv("results/models/model-1.2.tsv", sep="\t")

fig = plt.figure(figsize=(7.007874 / 2, 4))

gs = GridSpec(118, 100, figure=fig,
              top=0.9, left=0.15, right=0.96,
              bottom=0.05)

ax_members = fig.add_subplot(gs[:40, 5:50])
ax_nonmembers = fig.add_subplot(gs[:40, 55:], sharex=ax_members)

add_letter_and_title(ax_members, "A", "Sentiment over time on scikit-image")


plot_sentiment_timecourse(
    [ax_members, ax_nonmembers], model_results,
    "scikit-image")

ax_members = fig.add_subplot(gs[60:100, 5:50], sharex=ax_nonmembers)
ax_nonmembers = fig.add_subplot(gs[60:100, 55:], sharex=ax_members)
plot_sentiment_timecourse(
    [ax_members, ax_nonmembers], model_results,
    "numpy")
add_letter_and_title(ax_members, "B", "Sentiment over time on numpy")


###############################################################################
# Adding legend

legend_patches = (
    lines.Line2D([0, 1], [1, 1], color=colors["issue_post"]),
    lines.Line2D([0, 1], [1, 1], color=colors["issue_reply"]),
    lines.Line2D([0, 1], [1, 1], color=colors["pr_post"]),
    lines.Line2D([0, 1], [1, 1],  color=colors["pr_reply"]))

ax = fig.add_subplot(gs[115:, :])
ax.legend(legend_patches,
          ("post:issue",
           "comment:issue",
           "post:PR",
           "comment:PR"),
          fontsize=8,
          ncol=2, loc="center", frameon=False)
ax.spines["left"].set_linewidth(0)
ax.spines["right"].set_linewidth(0)
ax.spines["top"].set_linewidth(0)
ax.spines["bottom"].set_linewidth(0)
ax.set_xticks([])
ax.set_yticks([])



fig.savefig("figures/fig_sentiment_timecourse.pdf")
