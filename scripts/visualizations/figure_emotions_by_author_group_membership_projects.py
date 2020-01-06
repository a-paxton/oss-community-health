import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os

from utils_vis import plot_sentiment
from utils_vis import plot_gratitude

model_results = pd.read_csv("results/models/model-1.1b3.tsv", sep="\t")

fig = plt.figure(figsize=(7.007874 / 3 * 2, 4.2047))

gs = GridSpec(100, 100, figure=fig,
              top=0.9, left=0.06, right=0.98,
              bottom=0.04)

ax = fig.add_subplot(gs[:40, 5:50])

ax.text(
    -0.2, 1.07,
    "A", fontweight="bold", fontsize="large",
    horizontalalignment="left",
    transform=ax.transAxes)
ax.text(
    -0, 1.07,
    "Aggregate", fontweight="bold", fontsize="medium",
    horizontalalignment="left",
    transform=ax.transAxes)


plot_sentiment(ax, model_results)

model_results = pd.read_csv("results/models/model-1.1c.tsv", sep="\t")
# Select skimage stuff
skimage = [True if "scikit-image" in s else False
           for s in model_results.index]

numpy = [True if "numpy" in s else False
         for s in model_results.index]


ax_skimage = fig.add_subplot(gs[:15, 65:])
ax_numpy = fig.add_subplot(gs[25:40, 65:])

plot_sentiment(ax_skimage, model_results[skimage]) #, display_xticks=False)
plot_sentiment(ax_numpy, model_results[numpy])

ax_skimage.text(
    -0.4, 1.14,
    "B", fontweight="bold", fontsize="large",
    horizontalalignment="left",
    transform=ax_skimage.transAxes)
ax_skimage.text(
    -0, 1.14,
    "scikit-image", fontweight="bold", fontsize="medium",
    horizontalalignment="left",
    transform=ax_skimage.transAxes)

ax_numpy.text(
    -0.4, 1.14,
    "C", fontweight="bold", fontsize="large",
    horizontalalignment="left",
    transform=ax_numpy.transAxes)
ax_numpy.text(
    -0, 1.14,
    "numpy", fontweight="bold", fontsize="medium",
    horizontalalignment="left",
    transform=ax_numpy.transAxes)


###############################################################################
# Plotting gratitude
model_results = pd.read_csv("results/models/model-1.3b3.tsv", sep="\t")

ax = fig.add_subplot(gs[55:95, 5:50])
plot_gratitude(ax, model_results)
ax.text(
    -0.2, 1.07,
    "D", fontweight="bold", fontsize="large",
    horizontalalignment="left",
    transform=ax.transAxes)
ax.text(
    -0, 1.07,
    "Aggregate", fontweight="bold", fontsize="medium",
    horizontalalignment="left",
    transform=ax.transAxes)


ax_skimage = fig.add_subplot(gs[55:67, 65:])
ax_numpy = fig.add_subplot(gs[80:95, 65:])

model_results = pd.read_csv("results/models/model-1.3b4.tsv", sep="\t")

plot_gratitude(ax_skimage, model_results[skimage]) #, display_xticks=False)
plot_gratitude(ax_numpy, model_results[numpy])

ax_skimage.text(
    -0.4, 1.14,
    "E", fontweight="bold", fontsize="large",
    horizontalalignment="left",
    transform=ax_skimage.transAxes)
ax_skimage.text(
    -0, 1.14,
    "scikit-image", fontweight="bold", fontsize="medium",
    horizontalalignment="left",
    transform=ax_skimage.transAxes)

ax_numpy.text(
    -0.4, 1.14,
    "F", fontweight="bold", fontsize="large",
    horizontalalignment="left",
    transform=ax_numpy.transAxes)
ax_numpy.text(
    -0, 1.14,
    "numpy", fontweight="bold", fontsize="medium",
    horizontalalignment="left",
    transform=ax_numpy.transAxes)



try:
    os.makedirs("figures")
except OSError:
    pass
fig.savefig("figures/fig_sentiment.pdf")
