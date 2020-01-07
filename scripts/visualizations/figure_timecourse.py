import pandas as pd
import os
import matplotlib.pyplot as plt

from matplotlib.gridspec import GridSpec
from utils_vis import plot_sentiment_timecourse

model_results = pd.read_csv("results/models/model-1.2.tsv", sep="\t")

fig = plt.figure(figsize=(7.007874 / 2, 4))

gs = GridSpec(100, 100, figure=fig,
              top=0.9, left=0.15, right=0.96,
              bottom=0.1)

ax_members = fig.add_subplot(gs[:40, 5:50])
ax_nonmembers = fig.add_subplot(gs[:40, 55:], sharex=ax_members)

ax_members.text(-0.40, 1.14, "A", fontsize=10, horizontalalignment="left",
                transform=ax_members.transAxes, fontweight="bold")
ax_members.text(0, 1.14, "Sentiment over time on scikit-image", fontweight="bold", fontsize=9,
                horizontalalignment="left", transform=ax_members.transAxes)

plot_sentiment_timecourse(
    [ax_members, ax_nonmembers], model_results,
    "scikit-image")

ax_members = fig.add_subplot(gs[60:, 5:50], sharex=ax_nonmembers)
ax_nonmembers = fig.add_subplot(gs[60:, 55:], sharex=ax_members)
plot_sentiment_timecourse(
    [ax_members, ax_nonmembers], model_results,
    "numpy")

ax_members.text(-0.40, 1.14, "B", fontsize=10, horizontalalignment="left",
                transform=ax_members.transAxes, fontweight="bold")
ax_members.text(0, 1.14, "Sentiment over time on numpy", fontweight="bold", fontsize=9,
                horizontalalignment="left", transform=ax_members.transAxes)
fig.savefig("figures/fig_sentiment_timecourse.pdf")
