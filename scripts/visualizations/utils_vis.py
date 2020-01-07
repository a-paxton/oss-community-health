import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker

from utils import colors


def plot_sentiment(ax, model_results, display_xticks=True):
    colors = ["#e66101", "#fdb863",
              "#5e3c99",
              "#b2abd2"]

    labels = ["post:issue", "comment:issue", "post:PR", "comment:PR"]

    members = [False if "nonmember" not in s else True
               for s in model_results.index]
    members = np.array(members)
    index = np.arange(len(members), dtype=float)
    index[members] += 1

    ax.bar(index, model_results["Estimate"], color=colors*2,
           yerr=model_results["Std..Error"])

    ax.set_xticks([index[~members].mean(), index[members].mean()])
    if display_xticks:
        ax.set_xticklabels(["Member", "Nonmember"], fontweight="bold", # rotation=45,
                           fontsize="x-small")
    else:
        ax.set_xticklabels(["", ""])
    ax.set_ylabel("Sentiment", fontweight="bold", fontsize=8)
    ax.set_yticks([0, 0.1, 0.2, 0.3])
    ax.set_yticklabels(["0", "0.1", "0.2",  "0.3"], fontsize="x-small")

    ax.spines["top"].set_linewidth(0)
    ax.set_ylabel("Sentiment", fontweight="bold")
    ax.spines["right"].set_linewidth(0)


def plot_gratitude(ax, model_results, display_xticks=True, common_max_y=True):
    colors = ["#e66101", "#fdb863",
              "#5e3c99",
              "#b2abd2"]

    labels = ["post:issue", "comment:issue", "post:PR", "comment:PR"]

    members = [False if "nonmember" not in s else True
               for s in model_results.index]
    members = np.array(members)
    index = np.arange(len(members), dtype=float)
    index[members] += 1

    ax.bar(index, model_results["Estimate"], color=colors*2,
           yerr=model_results["Std..Error"])

    ax.set_xticks([index[~members].mean(), index[members].mean()])
    if display_xticks:
        ax.set_xticklabels(["Member", "Nonmember"], fontweight="bold", # rotation=45,
                           fontsize="x-small") #horizontalalignment="right")
    else:
        ax.set_xticklabels(["", ""])
    ax.set_ylabel("Gratitude", fontweight="bold", fontsize=8)
    if common_max_y:
        ax.set_yticks([0, 0.1, 0.2])
        ax.set_ylim(0, 0.25)
        ax.set_yticklabels(["0", "0.1", "0.2"], fontsize="x-small")
    else:
        ax.set_yticks([0, 0.1])
        ax.set_ylim(0, 0.15)
        ax.set_yticklabels(["0", "0.1"], fontsize="x-small")


    ax.spines["top"].set_linewidth(0)
    ax.spines["right"].set_linewidth(0)


def plot_sentiment_all_projects(axes, model_results, fig,
                                column_left="typepr_post:author_groupmember",
                                column_right="typepr_post:author_groupnonmember",
                                type="sentiment", order=None):
    # Select post:PR for members
    post_PR_members = [True if column_left in s else False
                    for s in model_results.index]
    comment_PR_members = [True if column_right in s else False
                    for s in model_results.index]

    ax_left = axes[0]
    ax_right = axes[1]

    estimates_left = (
        model_results[post_PR_members]["Estimate"])
    estimates_right = (
        model_results[comment_PR_members]["Estimate"])

    min_x = min(min(estimates_left), min(estimates_right))
    max_x = max(max(estimates_left), max(estimates_right))

    if order is None:
        order = (estimates_left.values + estimates_right.values).argsort()
    ax_left.barh(width=-estimates_left[order], y=np.arange(len(estimates_left)),
                color="black")

    ax_left.axvline(0, color="0", linewidth=0.5)

    ax_left.set_yticks([])
    ax_left.spines["right"].set_linewidth(0)
    ax_left.spines["top"].set_linewidth(0)
    ax_left.spines["left"].set_linewidth(0)
    ax_left.yaxis.set_ticks_position('right')
    ax_left.set_xlim(-max_x, -min_x)
    ax_right.set_xlim(min_x, max_x)
    if type == "sentiment":
        ax_left.set_xticks([0, -0.1, -0.2])
        ax_left.set_xticklabels(["0", "0.1", "0.2"], fontsize="x-small")
        ax_right.set_xticks([0, 0.1, 0.2])
        ax_right.set_xticklabels(["0", "0.1", "0.2"], fontsize="x-small")
    else:
        ax_left.set_xticks([0, -0.01, -0.02])
        ax_left.set_xticklabels(["0", "", "0.02"], fontsize="x-small")
        ax_right.set_xticks([0, 0.01, 0.02])
        ax_right.set_xticklabels(["0", "", "0.02"], fontsize="x-small")
        ax_left.set_xlim(-0.025, 0.001)
        ax_right.set_xlim(-0.001, 0.025)

    ax_right.set_yticks([])


    ax_right.barh(width=estimates_right[order], y=np.arange(len(estimates_right)),
                    color="black")
    ax_right.axvline(0, color="0", linewidth=0.5)

    ax_right.spines["left"].set_linewidth(0)
    ax_right.spines["top"].set_linewidth(0)
    ax_right.spines["right"].set_linewidth(0)
    ax_right.yaxis.set_ticks_position('left')



    projects = ["matplotlib", "mayavi", "numpy", "pandas", "scikit-image",
                "scikit-learn", "scipy", "sphinx-gallery"]

    ax_left.set_ylim(-0.5, len(projects)+0.5)

    for i in range(len(projects)):
        x1,y1 = ax_left.transData.transform_point( (0.05, i))
        x2,y2 = ax_right.transData.transform_point((-0.05, i))
        x,y = fig.transFigure.inverted().transform_point( ((x1+x2)/2,y1) )
        plt.text(x, y, projects[order[i]], transform=fig.transFigure, fontsize=8,
                horizontalalignment='center', verticalalignment='center')

    x1, y1 = ax_left.transData.transform_point((-min_x, len(projects)))
    x, y = fig.transFigure.inverted().transform_point((x1, y1))
    plt.text(x, y, "Member", fontweight="bold", fontsize="x-small",
            verticalalignment="bottom", horizontalalignment="right",
            transform=fig.transFigure,
            bbox=dict(boxstyle="round",
                    ec=(1., 1, 1),
                    fc=(1., 1, 1),
                    ))


    x1, y1 = ax_right.transData.transform_point((min_x, len(projects)))
    x, y = fig.transFigure.inverted().transform_point((x1, y1))
    plt.text(x, y, "Nonmember", fontweight="bold", fontsize="x-small",
            verticalalignment="bottom", horizontalalignment="left",
            transform=fig.transFigure,
            bbox=dict(boxstyle="round",
                    ec=(1., 1, 1),
                    fc=(1., 1, 1),
                    ))
    return order


def plot_sentiment_timecourse(axes, model_results, project_name):
    mask = [True if project_name in s else False
            for s in model_results.index]

    model_results = model_results[mask].sort_index()
    years = np.array(
        [int(i.split(":year")[-1]) for i in model_results.index.values])
    categories = np.array([
        i.split(":type")[-1].split(":year")[0].split(":author_group")[0]
        for i in model_results.index.values])
    membership = np.array([
        i.split(":author_group")[-1].split(":year")[0]
        for i in model_results.index.values])

    ax = axes[0]
    membership_mask = membership == "member"

    for category in np.unique(categories):
        mask = (categories == category) & membership_mask
        ax.plot(years[mask], model_results["Estimate"][mask],
                linewidth=2, color=colors[category])
        ax.fill_between(
            years[mask],
            model_results["Estimate"][mask] - model_results["Std..Error"][mask], 
            model_results["Estimate"][mask] + model_results["Std..Error"][mask], 
            color=colors[category],
            alpha=0.4)

        ax.text(
            1, 1.,
            "member", fontweight="bold",
            fontsize="x-small",
            horizontalalignment="right",
            transform=ax.transAxes)


    ax.spines["right"].set_linewidth(0)
    ax.spines["top"].set_linewidth(0)
    ax.set_xlim(2009, 2019)
    ax.set_xticks([2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018])
    ax.set_xticklabels(
        ["2010",
         "2014",
         "2018"
        ], fontsize="x-small")

    ax = axes[1]

    for category in np.unique(categories):
        mask = (categories == category) & ~membership_mask
        ax.plot(years[mask], model_results["Estimate"][mask],
                linewidth=2, color=colors[category])
        ax.fill_between(
            years[mask],
            model_results["Estimate"][mask] - model_results["Std..Error"][mask], 
            model_results["Estimate"][mask] + model_results["Std..Error"][mask], 
            color=colors[category],
            alpha=0.4)

        ax.text(
            1, 1,
            "nonmember", fontweight="bold",
            fontsize="x-small",
            horizontalalignment="right",
            transform=ax.transAxes)

    ax.spines["right"].set_linewidth(0)
    ax.spines["top"].set_linewidth(0)
    ax.set_xlim(2009, 2019)
    #ax.set_xticks([2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018])
    ax.tick_params(which='minor', width=0.75, length=2.5, labelsize=10)
    ax.xaxis.set_minor_formatter(ticker.NullFormatter())
    ax.xaxis.set_major_locator(ticker.FixedLocator([2010, 2014, 2018]))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    ax.set_xticklabels(
        ["2010",
         "2014",
         "2018"
        ], fontsize="x-small")

    axes[0].set_yticks([0, 0.5])
    axes[0].set_ylim(-0.25, 0.55)
    axes[0].set_yticklabels(["0", "0.5"], fontsize="x-small")

    axes[1].set_yticks([0, 0.5])
    axes[1].set_yticklabels([])
    axes[1].set_ylim(-0.25, 0.55)
    
    axes[0].set_ylabel("Sentiment", fontsize="small", fontweight="bold",
                        labelpad=-0.1)
