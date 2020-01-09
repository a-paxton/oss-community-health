import pandas as pd
import os

pvalues = pd.read_csv("results/models/model_2.tsv", delim_whitespace=True)
outname = "results/latex/model_2.tex"

columns = [
    ("1W", r"$\mu_\text{PR} = \mu_\text{issue}$", ""),
    ("1W", "Time opened", ""),
    ("1W", "Cumulative grateful words on comments", ""),
    ("1W", "Maximum negative sentiment score", ""),
    ("1W", "Maximum positive sentiment score", ""),
    ("1W", "Number of comments", ""),
    ("1W", "Comment member ratio", ""),
    ("1W", "Mean sentiment score", ""),
    ("2W", "Time opened", "Issue"),
    ("2W", "Time opened", "PR"),
    ("2W", "Cumulative grateful words on comments", "Issue"),
    ("2W", "Cumulative grateful words on comments", "PR"),
    ("2W", "Maximum negative sentiment score", "Issue"),
    ("2W", "Maximum negative sentiment score", "PR"),
    ("2W", "Maximum positive sentiment score", "Issue"),
    ("2W", "Maximum positive sentiment score", "PR"),
    ("2W", "Number of comments", "Issue"),
    ("2W", "Number of comments", "PR"),
    ("2W", "Comment member ratio", "Issue"),
    ("2W", "Comment member ratio", "PR"),
    ("2W", "Mean sentiment score", "Issue"),
    ("2W", "Mean sentiment score", "PR"),
    ]

column_names = pd.DataFrame(columns)

pvalues["Sig."] = ""
pvalues.loc[pvalues["p_val_adjusted"] < 0.1, "Sig."] = "."
pvalues.loc[pvalues["p_val_adjusted"] < 0.05, "Sig."] = "*"
pvalues.loc[pvalues["p_val_adjusted"] < 0.01, "Sig."] = "**"
pvalues.loc[pvalues["p_val_adjusted"] < 0.001, "Sig."] = "***"

column_names.columns = ["", "", ""]
multi_index = pd.MultiIndex.from_frame(column_names)
pvalues.index = multi_index

pvalues = pvalues.drop("model", axis=1)

pvalues.columns = ["t-stat", "p-val.", "p-val adj.", "sig."]

try:
    os.makedirs(os.path.dirname(outname))
except OSError:
    pass

pvalues.to_latex(
    outname, escape=False, longtable=True,
    multirow=True, float_format="%0.3f")
