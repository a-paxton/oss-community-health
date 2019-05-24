from glob import glob
import os
import numpy as np
import pandas as pd
import argparse

"""
Getting numbers for the paper and putting them in a nicely formatted latex
table.
"""

parser = argparse.ArgumentParser()
parser.add_argument("--outname", "-o")
args = parser.parse_args()

outname = args.outname

filenames = glob("data/raw_data/*/issues.tsv")
filenames.sort()

columns = ["Project", "Issues", "Pull requests", "Comments", "Authors"]
summary_data = pd.DataFrame(
    columns=columns)

all_authors = None
for filename in filenames[1:]:
    project = filename.split("/")[-2]
    tickets = pd.read_csv(filename, sep="\t", keep_default_na=False)
    comments = pd.read_csv(
        filename.replace("issues.tsv", "comments.tsv"),
        sep="\t",
        keep_default_na=False)
    project_authors = np.unique(comments["author_name"])
    project_authors = np.unique(
        np.concatenate([project_authors,
                        np.unique(tickets["author_name"])]))
    row = pd.DataFrame(
        {"Project": [project],
         "Pull requests": [sum(tickets["type"] == "pull_request")],
         "Issues": [sum(tickets["type"] == "issue")],
         "Comments": [len(comments)],
         "Authors": [len(project_authors)]})
    if all_authors is None:
        all_authors = project_authors
    else:
        all_authors = np.unique(
            np.concatenate([all_authors, project_authors]))
    summary_data = summary_data.append(row)

summary_data = summary_data.sort_values(by="Authors", ascending=False)
row = pd.DataFrame(
        {"Project": ["all"],
         "Pull requests": [summary_data["Pull requests"].sum()],
         "Issues": [summary_data["Issues"].sum()],
         "Comments": [summary_data["Comments"].sum()],
         "Authors": [len(all_authors)]})

summary_data = summary_data.append(row)
summary_data.set_index("Project", inplace=True)

# Now sort the columns
summary_data = summary_data[columns[1:]]
outname = "latex/summary_data.tex"
try:
    os.makedirs(os.path.dirname(outname))
except OSError:
    pass

summary_data.to_latex(outname)
