import pandas as pd
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("filename")
parser.add_argument("--outname", "-o")
args = parser.parse_args()


filename = args.filename
outname = args.outname

is_emotion = "emotion" if "emotion" in filename else "gratitude"

pvalues = pd.read_csv(filename, delim_whitespace=True)
column_names = pd.read_csv("columns", header=None)

indices = pvalues.index
projects = [i.split(":")[2][:-4] for i in indices]
years = [int(i.split("year")[1].split("-")[0]) for i in indices]
contrasts = [
    ":".join(i.split(":")[:2])
    for i in indices]


contrast_names = {
    "issue_post:member": r"$\text{post:issue} \times \text{member}$",
    "issue_post:nonmember": r"$\text{post:issue} \times \text{nonmember}$",
    "pr_post:member": r"$\text{post:PR} \times \text{member}$",
    "pr_post:nonmember": r"$\text{post:PR} \times \text{nonmember}$",
    "issue_reply:member": r"$\text{comment:issue} \times \text{member}$",
    "issue_reply:nonmember": r"$\text{comment:issue} \times \text{nonmember}$",
    "pr_reply:member": r"$\text{comment:PR} \times \text{member}$",
    "pr_reply:nonmember": r"$\text{comment:PR} \times \text{nonmember}$",
    }

pvalues["Project"] = projects
pvalues["Year"] = years
pvalues["Contrast"] = [contrast_names[c] for c in contrasts]

pvalues = pvalues.sort_values(by=["Project", "Contrast", "Year"])
column_names = pvalues[["Project", "Contrast", "Year"]]
pvalues.index = pd.MultiIndex.from_frame(column_names)
pvalues = pvalues.drop(labels=["Project", "Contrast", "Year"], axis=1)

pvalues["Sig."] = ""
pvalues.loc[pvalues["p_val_adjusted"] < 0.1, "Sig."] = "."
pvalues.loc[pvalues["p_val_adjusted"] < 0.05, "Sig."] = "*"
pvalues.loc[pvalues["p_val_adjusted"] < 0.01, "Sig."] = "**"
pvalues.loc[pvalues["p_val_adjusted"] < 0.001, "Sig."] = "***"

pvalues.columns = ["t-stat", "p-val.", "p-val adj.", "sig."]

pivot_table = pvalues.pivot_table(
    columns="Year", index=["Project", "Contrast"])

order = pivot_table.columns.sortlevel("Year")
pivot_table = pivot_table[order[0]]
pivot_table.columns = pivot_table.columns.swaplevel()


try:
    os.makedirs(os.path.dirname(outname))
except OSError:
    pass

with open(outname, "w") as f:
    pvalues.to_latex(
        f, escape=False, longtable=True,
        multirow=True, float_format="%0.3f", na_rep="")
