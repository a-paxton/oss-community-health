import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from utils_graphs import compute_contributions_per_project
from matplotlib import ticker
from matplotlib.gridspec import GridSpec
from utils_vis import add_letter_and_title


fig = plt.figure(figsize=(7.007874, 3))

# Prepare the gridspeck

gs = GridSpec(110, 100,  figure=fig, top=0.9, left=0.1, right=0.96,
              bottom=0.05)


###############################################################################
# How many people contribute to more than one project?

ax = fig.add_subplot(gs[:75, :12])
data = pd.read_csv("results/data/sentiment_frame_original.tsv", sep="\t")

all_authors_mapping = {
    a: i for i, a in enumerate(np.unique(data["author_name"]))}

contributions_per_projects = compute_contributions_per_project(data)
number_of_projects_contributed_to = (
    contributions_per_projects != 0).sum(axis=1).values
num_proj, counts = np.unique(number_of_projects_contributed_to, return_counts=True)
ax.bar(num_proj, counts,
       color="0", width=0.8)
ax.set_xticks(np.arange(1, 9))
ax.set_xlabel("Number of projects", fontweight="bold", fontsize="x-small")
ax.set_ylabel("Number of contributors", fontweight="bold", fontsize="x-small")
ax.spines["right"].set_linewidth(0)
ax.spines["top"].set_linewidth(0)
ylim = ax.get_ylim()
ax.yaxis.set_major_locator(
    ticker.MultipleLocator(5000))
ax.tick_params(labelsize="x-small")
add_letter_and_title(ax, "A", "")



###############################################################################
# Co-contributors across projects

ax = fig.add_subplot(gs[:80, 25:52])

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
    bar_labels = ["%0.0f%%" % v if v > 9 else "" for v in widths]
    ax.bar_label(rects, bar_labels, label_type='center',
                 color=text_color, fmt="%0.0f",
                 fontsize=5)

ax.spines["top"].set_linewidth(0)
ax.spines["right"].set_linewidth(0)
#ax.spines["bottom"].set_linewidth(0)
#ax.set_xticks([])
ax.set_xticks([0, 50, 100])
ax.set_xticklabels(["0%", "50%", "100%"], fontsize="xx-small")
ax.tick_params(axis='y', which='major', pad=0)

ax.set_yticklabels(labels, fontsize="x-small", rotation=45,
                   verticalalignment="top")
add_letter_and_title(ax, "B", "")

ax_leg = fig.add_subplot(gs[78:, 25:52], facecolor="none")
ax_leg.spines["top"].set_linewidth(0)
ax_leg.spines["bottom"].set_linewidth(0)
ax_leg.spines["left"].set_linewidth(0)
ax_leg.spines["right"].set_linewidth(0)
ax_leg.set_xticks([])
ax_leg.set_yticks([])


leg = ax_leg.legend(
    legend, ["N=%s" % d for d in category_names],
    ncol=int(len(category_names)/2),
    fontsize='xx-small', frameon=False,
    loc="lower center",
    title="Contributors contributing to N projects",
    title_fontproperties={"weight": "bold", "size": "x-small"})


###############################################################################
# First, draw a heatmap of the number of people that contribute to eac
ax = fig.add_subplot(gs[:80, 68:])

contributions_per_projects = (contributions_per_projects > 0).astype(int)

# Reorder the projects such that they are the same as in the previous plot
contributions_per_projects = contributions_per_projects[test.columns]

# Remove anyone that has contributed only to one project
#contributions_per_projects = contributions_per_projects.loc[
#    contributions_per_projects.sum(axis=1) > 1]

cocontributors = np.dot(
    contributions_per_projects.values.T,
    contributions_per_projects.values)
dist_cocontributors = (cocontributors /
                       cocontributors[np.diag_indices_from(cocontributors)] * 100).T

#dist_cocontributors = cocontributors
dist_cocontributors[np.diag_indices_from(cocontributors)] = np.nan

projects = contributions_per_projects.columns

ax.imshow(dist_cocontributors, cmap="YlOrRd")

for i in range(len(projects)):
    for j in range(len(projects)):
        if i == j:
            continue

        val = dist_cocontributors[j, i]
        ax.text(i, j, "%0.0f%%" % val, color="black",
                fontsize=5, horizontalalignment="center",
                verticalalignment="center")

ax.set_xticks(np.arange(0, len(projects)))
ax.set_yticks(np.arange(0, len(projects)))

ax.set_xticklabels(projects, rotation=45,
                   fontsize="x-small", 
                   horizontalalignment="right")
ax.set_yticklabels(projects, fontsize="x-small",
                   rotation=45, verticalalignment="top")
ax.tick_params(axis='both', which='major', pad=0)
ax.set_ylabel("Percentage of authors of", fontweight="bold",
              fontsize="x-small", labelpad=0)
ax.set_xlabel("Also interact with", fontweight="bold", fontsize="x-small",
              labelpad=0)
add_letter_and_title(ax, "C", "")
fig.savefig("figures/understanding_communities.pdf")
fig.savefig("figures/understanding_communities.png")
