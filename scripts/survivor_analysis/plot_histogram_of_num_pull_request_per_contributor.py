import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils import visualization


parser = argparse.ArgumentParser()
parser.add_argument("filename")
parser.add_argument("--outname", "-o")
args = parser.parse_args()


filename = args.filename

all_issues = pd.read_csv(filename, sep="\t")
pull_requests = all_issues[all_issues["type"] == "pull_request"]

_, num_pull_request_per_authors = np.unique(
    pull_requests["author_id"],
    return_counts=True)

fig, ax = plt.subplots()
ax.hist(num_pull_request_per_authors[num_pull_request_per_authors < 100],
        bins=100, color="#000000")
visualization.format_ax(ax)
