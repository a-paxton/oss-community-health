import argparse
import pandas as pd
import matplotlib.pyplot as plt
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

model_results = pd.read_csv("results/models/model-1.3b4.tsv", sep="\t")
fig, ax = plt.subplots(figsize=(7.007874 / 2, 4.2047 / 2))

mask = [True if project in s else False
        for s in model_results.index]

fig.subplots_adjust(bottom=0.25)
ax.text(
    -0, 1.07,
    project, fontweight="bold", fontsize="medium",
    horizontalalignment="left",
    transform=ax.transAxes)


plot_gratitude(ax, model_results[mask])
if outname is not None:
    try:
        os.makedirs(os.path.dirname(outname))
    except OSError:
        pass
    fig.savefig(outname)
