import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os

from utils_vis import plot_sentiment
from utils_vis import plot_gratitude
from utils_vis import plot_sentiment_all_projects

model_results = pd.read_csv("results/models/model-1.1b3.tsv", sep="\t")

fig = plt.figure(figsize=(7.007874, 4.2047))

gs = GridSpec(100, 150, figure=fig,
              top=0.9, left=0.06, right=0.96,
              bottom=0.04)

ax = fig.add_subplot(gs[:40, 5:45])

ax.text(
    -0.2, 1.07,
    "A", fontweight="bold", fontsize=10,
    horizontalalignment="left",
    transform=ax.transAxes)
ax.text(
    -0, 1.07,
    "Sentiment per context", fontweight="bold", fontsize=9,
    horizontalalignment="left",
    transform=ax.transAxes)


plot_sentiment(ax, model_results)

global_model = model_results

model_results = pd.read_csv("results/models/model-1.1c.tsv", sep="\t")
# Select skimage stuff
skimage = [True if "scikit-image" in s else False
           for s in model_results.index]

numpy = [True if "numpy" in s else False
         for s in model_results.index]

# Select post:PR for members
post_PR_members = [True if "typepr_post:author_groupmember" in s else False
                   for s in model_results.index]
comment_PR_members = [True if "typepr_post:author_groupnonmember" in s else False
                   for s in model_results.index]

ax_left = fig.add_subplot(gs[:40, 55:68])
ax_right = fig.add_subplot(gs[:40, 87:100], sharey=ax_left)

order = plot_sentiment_all_projects([ax_left, ax_right], model_results, fig)

ax_left.text(
    -0.4, 1.07,
    "B", fontweight="bold", fontsize=10,
    horizontalalignment="left",
    transform=ax_left.transAxes)

ax_left.text(
    -0, 1.07,
    "Sentiment post:PR", fontweight="bold", fontsize=9,
    horizontalalignment="left",
    transform=ax_left.transAxes)

ax_skimage = fig.add_subplot(gs[:15, 120:])
ax_numpy = fig.add_subplot(gs[28:40, 120:], sharey=ax_skimage)


plot_sentiment(ax_skimage, model_results[skimage]) #, display_xticks=False)
plot_sentiment(ax_numpy, model_results[numpy])

ax_skimage.text(
    -0.4, 1.14,
    "C", fontweight="bold", fontsize=10,
    horizontalalignment="left",
    transform=ax_skimage.transAxes)
ax_skimage.text(
     -0, 1.14,
     "scikit-image", fontweight="bold", fontsize=9,
     horizontalalignment="left",
     transform=ax_skimage.transAxes)

ax_numpy.text(
     -0.4, 1.14,
    "D", fontweight="bold", fontsize=10,
    horizontalalignment="left",
    transform=ax_numpy.transAxes)
ax_numpy.text(
    -0, 1.14,
    "numpy", fontweight="bold", fontsize=9,
    horizontalalignment="left",
    transform=ax_numpy.transAxes)


###############################################################################
# Plotting gratitude
model_results = pd.read_csv("results/models/model-1.3b3.tsv", sep="\t")

ax = fig.add_subplot(gs[55:95, 5:45])
plot_gratitude(ax, model_results, common_max_y=False)
ax.text(
    -0.2, 1.07,
    "E", fontweight="bold", fontsize=10,
    horizontalalignment="left",
    transform=ax.transAxes)
ax.text(
    -0, 1.07,
    "Gratitude per context", fontweight="bold", fontsize=9,
    horizontalalignment="left",
    transform=ax.transAxes)




model_results = pd.read_csv("results/models/model-1.3b4.tsv", sep="\t")

ax_left = fig.add_subplot(gs[55:95, 55:68])
ax_right = fig.add_subplot(gs[55:95, 87:100], sharey=ax_left)

plot_sentiment_all_projects([ax_left, ax_right], model_results, fig,
                            type="gratitude", order=order)

ax_left.text(
    -0.4, 1.07,
    "F", fontweight="bold", fontsize=10,
    horizontalalignment="left",
    transform=ax_left.transAxes)

ax_left.text(
    -0, 1.07,
    "Gratitude post:PR", fontweight="bold", fontsize=9,
    horizontalalignment="left",
    transform=ax_left.transAxes)


ax_skimage = fig.add_subplot(gs[55:67, 120:])
ax_numpy = fig.add_subplot(gs[80:95, 120:])

plot_gratitude(ax_skimage, model_results[skimage], common_max_y=False) 
plot_gratitude(ax_numpy, model_results[numpy], common_max_y=False)

ax_skimage.text(
    -0.4, 1.14,
    "G", fontweight="bold", fontsize=10,
    horizontalalignment="left",
    transform=ax_skimage.transAxes)
ax_skimage.text(
    -0, 1.14,
    "scikit-image", fontweight="bold", fontsize=9,
    horizontalalignment="left",
    transform=ax_skimage.transAxes)

ax_numpy.text(
    -0.4, 1.14,
    "H", fontweight="bold", fontsize=10,
    horizontalalignment="left",
    transform=ax_numpy.transAxes)
ax_numpy.text(
    -0, 1.14,
    "numpy", fontweight="bold", fontsize=9,
    horizontalalignment="left",
    transform=ax_numpy.transAxes)



try:
    os.makedirs("figures")
except OSError:
    pass
fig.savefig("figures/fig_sentiment.pdf")
