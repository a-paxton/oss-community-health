import pandas as pd
from utils import colors
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib import patches
import os

from utils_vis import plot_sentiment
from utils_vis import plot_gratitude
from utils_vis import plot_sentiment_all_projects
from utils_vis import add_letter_and_title

model_results = pd.read_csv("results/models/model-1.1b3.tsv", sep="\t")

fig = plt.figure(figsize=(7.007874, 4.2047))

gs = GridSpec(110, 150, figure=fig,
              top=0.9, left=0.06, right=0.96,
              bottom=0.04)

ax = fig.add_subplot(gs[:40, 5:45])

add_letter_and_title(ax, "A", title="Sentiment per context")

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
add_letter_and_title(ax_left, "B", title="Sentiment post:PR",
                     extra_x_shift=20)

ax_skimage = fig.add_subplot(gs[:15, 120:])
ax_numpy = fig.add_subplot(gs[28:40, 120:], sharey=ax_skimage)


plot_sentiment(ax_skimage, model_results[skimage]) #, display_xticks=False)
plot_sentiment(ax_numpy, model_results[numpy])

add_letter_and_title(ax_skimage, "C", title="scikit-image")
add_letter_and_title(ax_numpy, "D", title="numpy")


###############################################################################
# Plotting gratitude
model_results = pd.read_csv("results/models/model-1.3b3.tsv", sep="\t")

ax = fig.add_subplot(gs[55:95, 5:45])
plot_gratitude(ax, model_results, common_max_y=False)
add_letter_and_title(ax, "E", title="Gratitude per context")


model_results = pd.read_csv("results/models/model-1.3b4.tsv", sep="\t")

ax_left = fig.add_subplot(gs[55:95, 55:68])
ax_right = fig.add_subplot(gs[55:95, 87:100], sharey=ax_left)

plot_sentiment_all_projects([ax_left, ax_right], model_results, fig,
                            type="gratitude", order=order)
add_letter_and_title(ax_left, "F", title="Gratitude post:PR",
                     extra_x_shift=20)


ax_skimage = fig.add_subplot(gs[55:67, 120:])
ax_numpy = fig.add_subplot(gs[80:95, 120:])

plot_gratitude(ax_skimage, model_results[skimage], common_max_y=False) 
plot_gratitude(ax_numpy, model_results[numpy], common_max_y=False)

add_letter_and_title(ax_skimage, "G", title="scikit-image")
add_letter_and_title(ax_numpy, "H", title="numpy")

###############################################################################
# Adding legend

legend_patches = (
    patches.Patch(color=colors["issue_post"]),
    patches.Patch(color=colors["issue_reply"]),
    patches.Patch(color=colors["pr_post"]),
    patches.Patch(color=colors["pr_reply"]))

ax = fig.add_subplot(gs[106:, :])
ax.legend(legend_patches,
          ("post:issue",
           "comment:issue",
           "post:PR",
           "comment:PR"),
          fontsize=8,
          ncol=4, loc="center", frameon=False)
ax.spines["left"].set_linewidth(0)
ax.spines["right"].set_linewidth(0)
ax.spines["top"].set_linewidth(0)
ax.spines["bottom"].set_linewidth(0)
ax.set_xticks([])
ax.set_yticks([])


try:
    os.makedirs("figures")
except OSError:
    pass
fig.savefig("figures/fig_sentiment.pdf")
