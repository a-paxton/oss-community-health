import numpy as np
import matplotlib.pyplot as plt


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
    ax.set_ylabel("Sentiment", fontweight="bold", fontsize="small")
    ax.set_yticks([0, 0.1, 0.2, 0.3])
    ax.set_yticklabels(["0", "0.1", "0.2",  "0.3"], fontsize="x-small")

    ax.spines["top"].set_linewidth(0)
    ax.set_ylabel("Sentiment", fontweight="bold")
    ax.spines["right"].set_linewidth(0)


def plot_gratitude(ax, model_results, display_xticks=True):
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
    ax.set_ylabel("Gratitude", fontweight="bold", fontsize="small")
    ax.set_yticks([0, 0.1])
    ax.set_ylim(0, 0.15)
    ax.set_yticklabels(["0", "0.1"], fontsize="x-small")

    ax.spines["top"].set_linewidth(0)
    ax.spines["right"].set_linewidth(0)
