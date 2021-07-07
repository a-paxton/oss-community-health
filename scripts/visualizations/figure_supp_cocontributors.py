import numpy as np
import pandas as pd
from utils_graphs import compute_contributions_per_project
import matplotlib.pyplot as plt
from matplotlib import ticker
from matplotlib.gridspec import GridSpec


data = pd.read_csv("results/data/sentiment_frame_original.tsv", sep="\t")

###############################################################################
# First, draw a heatmap of the number of people that contribute to eac

all_authors_mapping = {
    a: i for i, a in enumerate(np.unique(data["author_name"]))}

contributions_per_projects = compute_contributions_per_project(data)
contributions_per_projects = (contributions_per_projects > 0).astype(int)

# Remove anyone that has contributed only to one project
#contributions_per_projects = contributions_per_projects.loc[
#    contributions_per_projects.sum(axis=1) > 1]

cocontributors = np.dot(
    contributions_per_projects.values.T,
    contributions_per_projects.values)
dist_cocontributors = (cocontributors /
                       cocontributors[np.diag_indices_from(cocontributors)] * 100).T

#dist_cocontributors = cocontributors
dist_cocontributors[np.diag_indices_from(cocontributors)] = 0

labels = contributions_per_projects.columns
data = dist_cocontributors
data_cum = data.cumsum(axis=1)
category_colors = plt.get_cmap('twilight_shifted')(
    np.linspace(0, 0.9, data.shape[1]))

fig = plt.figure(figsize=(7, 3))
gs = GridSpec(11, 10, figure=fig)
ax = fig.add_subplot(gs[:5, :])
#ax.set_xlim(0, 100)
category_names = ["%d" % i for i in np.arange(1, 9)]

legend = []
projects = category_names
for i, (colname, color) in enumerate(zip(category_names, category_colors)):
    widths = data[:, i]
    starts = data_cum[:, i] - widths
    rects = ax.bar(np.arange(len(labels))+i/(len(projects)*2), height=widths,
                   width=0.5/len(projects),
                   label=colname, color=color)
    legend.append(rects[0])
    r, g, b, _ = color
    text_color = 'white' if r * g * b < 0.2 else 'darkgrey'
    bar_labels = ["%0.0f%%" % v if v > 10 else "" for v in widths]
    #ax.bar_label(rects, bar_labels, label_type='center',
    #             color=text_color, fmt="%0.0f",
    #             fontsize="x-small", fontweight="bold")

ax.spines["top"].set_linewidth(0)
ax.spines["right"].set_linewidth(0)
ax.set_yticks([0, 50])
ax.set_yticks([0, 25, 50], minor=True)

ax.set_yticklabels(["0%", "50%"], fontsize="x-small")
ax.set_xticks(np.arange(len(labels)) + 7/16/2)
ax.set_xticklabels(labels, fontweight="bold", fontsize="x-small", rotation=90)
ax.set_ylabel("% of contributors", fontsize="small",
              fontweight="bold")

###############################################################################
# Legend
#
ax_leg = fig.add_subplot(gs[10:, :])
ax_leg.spines["top"].set_linewidth(0)
ax_leg.spines["bottom"].set_linewidth(0)
ax_leg.spines["left"].set_linewidth(0)
ax_leg.spines["right"].set_linewidth(0)
ax_leg.set_xticks([])
ax_leg.set_yticks([])


leg = ax_leg.legend(
    legend, labels,
    ncol=int(len(labels)),
    fontsize='xx-small', frameon=False,
    loc="lower center",
    title="Also contributes to",
    title_fontproperties={"weight": "bold", "size": "x-small"})
fig.savefig("figures/supp/contributors_also_contribute_to.pdf")
fig.savefig("figures/supp/contributors_also_contribute_to.png")
