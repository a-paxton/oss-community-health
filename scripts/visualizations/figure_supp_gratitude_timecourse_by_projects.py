import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils import colors
from utils import labels
import os

from utils_vis import plot_gratitude

parser = argparse.ArgumentParser()
parser.add_argument("project")
parser.add_argument("--outname", "-o", default=None)
args = parser.parse_args()

project = args.project
outname = args.outname

mapping_names = {
    "scikit-image": "scikit.image",
    "matplotlib": "matplotlib",
    "scikit-learn": "scikit.learn",
    "sphinx-gallery": "sphinx.gallery",
    "mayavi": "mayavi",
    "numpy": "numpy",
    "scipy": "scipy"
    }


model_results = pd.read_csv("results/models/model-1.4.tsv", sep="\t")
fig, ax = plt.subplots(figsize=(7.007874 / 2, 4.2047 / 2))
mask = [True if project in s else False
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

fig, axes = plt.subplots(
    figsize=(7.007874, 3),
    ncols=2, sharey=True)
fig.subplots_adjust(right=0.75)

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
        1, 1.03,
        "member", fontweight="bold",
        fontsize="small",
        horizontalalignment="right",
        transform=ax.transAxes)


ax = axes[1]
membership_mask = ~membership_mask
for category in np.unique(categories):
    mask = (categories == category) & membership_mask
    ax.plot(years[mask], model_results["Estimate"][mask],
            linewidth=2, color=colors[category], label=labels[category])
    ax.fill_between(
        years[mask],
        model_results["Estimate"][mask] - model_results["Std..Error"][mask], 
        model_results["Estimate"][mask] + model_results["Std..Error"][mask], 
        color=colors[category],
        alpha=0.4)

    ax.text(
        1, 1.03,
        "nonmember", fontweight="bold",
        color="0.3",
        fontsize="small",
        horizontalalignment="right",
        transform=ax.transAxes)

ax.legend(frameon=False, bbox_to_anchor=(1, 0.5))
for ax in axes:
    ax.spines["top"].set_linewidth(0)
    ax.spines["right"].set_linewidth(0)
    ax.set_xlim(2009, 2019)
    ax.set_xticks([2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018])
    ax.set_xticklabels(
        ["2010", "", "", "",
         "2014", "", "", "",
         "2018"
        ])
    ax.set_ylim(-0.2, 0.45)


ax = axes[0]
ax.set_ylabel("Gratitude", fontweight="bold")
ax.text(
    -0, 1.07,
    project, fontweight="bold",
    horizontalalignment="left",
    transform=ax.transAxes)


if outname is not None:
    try:
        os.makedirs(os.path.dirname(outname))
    except OSError:
        pass
    fig.savefig(outname)
