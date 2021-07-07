import numpy as np
import pandas as pd
from utils_graphs import compute_contributions_per_project
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec


data = pd.read_csv("results/data/sentiment_frame_original.tsv", sep="\t")

###############################################################################
# First, draw a heatmap of the number of people that contribute to eac

all_authors_mapping = {
    a: i for i, a in enumerate(np.unique(data["author_name"]))}

contributions_per_projects = compute_contributions_per_project(data)

num_contributions = (contributions_per_projects != 0).sum(axis=1)

test = (contributions_per_projects > 0).astype(int)
test["N"] = num_contributions

test = test.groupby("N").sum()
test = test.apply(lambda x: x / x.sum()) * 100
test = test[test.columns[test.loc[1].argsort()]]


labels = test.columns
data = test.values.T
data_cum = data.cumsum(axis=1)
category_colors = plt.get_cmap('inferno')(
    np.linspace(0.15, 0.85, data.shape[1]))

fig = plt.figure(figsize=(7, 5))
gs = GridSpec(10, 10, figure=fig)
ax = fig.add_subplot(gs[:9, 1:])
ax.invert_yaxis()
ax.set_xlim(0, 100)
category_names = ["%d" % i for i in np.arange(1, 9)]

legend = []
for i, (colname, color) in enumerate(zip(category_names, category_colors)):
    widths = data[:, i]
    starts = data_cum[:, i] - widths
    rects = ax.barh(labels, widths, left=starts, height=0.5,
                    label=colname, color=color)
    legend.append(rects[0])
    r, g, b, _ = color
    text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
    bar_labels = ["%0.0f%%" % v if v > 3.5 else "" for v in widths]
    ax.bar_label(rects, bar_labels, label_type='center',
                 color=text_color, fmt="%0.0f",
                 fontsize="x-small", fontweight="bold")

ax.spines["top"].set_linewidth(0)
ax.spines["right"].set_linewidth(0)
ax.spines["bottom"].set_linewidth(0)
ax.set_xticks([])

ax.set_yticklabels(labels, fontweight="bold", fontsize="small")


###############################################################################
# Legend

ax_leg = fig.add_subplot(gs[9:, 1:])
ax_leg.spines["top"].set_linewidth(0)
ax_leg.spines["bottom"].set_linewidth(0)
ax_leg.spines["left"].set_linewidth(0)
ax_leg.spines["right"].set_linewidth(0)
ax_leg.set_xticks([])
ax_leg.set_yticks([])


leg = ax_leg.legend(
    legend, ["N=%s" % d for d in category_names],
    ncol=len(category_names),
    fontsize='x-small', frameon=False,
    loc="lower center",
    title="Contributors contributing to N projects",
    title_fontproperties={"weight": "bold", "size": "small"})
fig.savefig("figures/supp/contributors_contributing_to_different_project.pdf")
fig.savefig("figures/supp/contributors_contributing_to_different_project.png")
