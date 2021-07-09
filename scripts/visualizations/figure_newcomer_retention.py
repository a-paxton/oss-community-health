import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from utils_vis import add_letter_and_title
from utils_vis import plot_newcomer_retention_2W
from utils import colors
from matplotlib import lines

fig = plt.figure(figsize=(7.007874, 3))


gs = GridSpec(100, 90,  figure=fig,
              top=0.9, left=0.1, right=0.96, bottom=0.05)


model_results = pd.read_csv("results/models/model_2.1.tsv", sep="\t")
data = pd.read_csv("results/data/newcomer_retention.tsv", sep="\t")


###############################################################################
# Bar plot of log pvalues
ax_A = fig.add_subplot(gs[:40, :15])
means = model_results["Estimate"].loc[
    ["ticket_familyissue",
     "ticket_familypr"]]
yerr = model_results["Std..Error"].loc[
    ["ticket_familyissue",
     "ticket_familypr"]]

ax_A.bar([1, 2], means, color="#000000")
ax_A.spines["right"].set_linewidth(0)
ax_A.spines["top"].set_linewidth(0)
ax_A.spines["bottom"].set_position(('data', 0))
ax_A.xaxis.set_ticks_position('top')
ax_A.set_xticks([1, 2])
ax_A.set_xticklabels(["Issue", "PR"], fontweight="bold", fontsize=8)
ax_A.set_yticks([0, -.5])
ax_A.set_yticklabels(["0", "-0.5"], fontsize="x-small")
ax_A.set_ylabel("log(p)", fontweight="bold", fontsize="x-small", labelpad=0)

add_letter_and_title(ax_A, "A", "")

###############################################################################
# Open time
ax_B = fig.add_subplot(gs[:30, 25:40])

plot_newcomer_retention_2W(
    ax_B, model_results, "ticket_familyissue1",
    "ticket_familypr1", "ticket_familyissue:open_time",
    "ticket_familypr:open_time",
    ylabel="Open time", yrange=[0, 2*10**8])

add_letter_and_title(ax_B, "B", "")


###############################################################################
# Max positive emotion
ax_D = fig.add_subplot(gs[:30, 50:65])

plot_newcomer_retention_2W(
    ax_D, model_results, "ticket_familyissue3",
    "ticket_familypr3", "ticket_familyissue:comment_sentiment_max_positive",
    "ticket_familypr:comment_sentiment_max_positive",
    ylabel="Max positive emotion")

add_letter_and_title(ax_D, "D", "")

###############################################################################
# Ratio of members
ax_F = fig.add_subplot(gs[:30, 75:90])
plot_newcomer_retention_2W(
    ax_F, model_results, "ticket_familyissue5",
    "ticket_familypr5", "ticket_familyissue:comment_member_ratio",
    "ticket_familypr:comment_member_ratio",
    ylabel="Ratio of members")

add_letter_and_title(ax_F, "F", "")


###############################################################################
# Max negative emotion
ax_C = fig.add_subplot(gs[55:85, 25:40])
plot_newcomer_retention_2W(
    ax_C, model_results, "ticket_familyissue2",
    "ticket_familypr2", "ticket_familyissue:comment_sentiment_max_negative",
    "ticket_familypr:comment_sentiment_max_negative",
    ylabel="Max negative emotion")

add_letter_and_title(ax_C, "C", "")

###############################################################################
# Number of comments
ax_E = fig.add_subplot(gs[55:85, 50:65])
plot_newcomer_retention_2W(
    ax_E, model_results, "ticket_familyissue4",
    "ticket_familypr4", "ticket_familyissue:number_of_comments",
    "ticket_familypr:number_of_comments",
    ylabel="Num. of comments", yrange=[0, 266])

add_letter_and_title(ax_E, "E", "")

###############################################################################
# Cumulative grateful counts
ax_G = fig.add_subplot(gs[55:85, 75:90])
plot_newcomer_retention_2W(
    ax_G, model_results, "ticket_familyissue7",
    "ticket_familypr7", "ticket_familyissue:comment_grateful_cumulative",
    "ticket_familypr:comment_grateful_cumulative",
    ylabel="Cum. grateful counts", yrange=[0, 34])


add_letter_and_title(ax_G, "G", "")

###############################################################################
# Legend
legend_patches = (
    lines.Line2D([0, 1], [1, 1], color=colors["issue_post"]),
    lines.Line2D([0, 1], [1, 1], color=colors["pr_post"]))

ax = fig.add_subplot(gs[60:85, :15])
ax.legend(legend_patches,
          ("issue",
           "PR"),
          fontsize=8,
          ncol=1, loc="center", frameon=False)
ax.spines["left"].set_linewidth(0)
ax.spines["right"].set_linewidth(0)
ax.spines["top"].set_linewidth(0)
ax.spines["bottom"].set_linewidth(0)
ax.set_xticks([])
ax.set_yticks([])


fig.savefig("figures/figure_newcomers.pdf")

