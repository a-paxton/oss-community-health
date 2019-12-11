import pandas as pd
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("filename")
parser.add_argument("--outname", "-o")
args = parser.parse_args()

filename = args.filename
outname = args.outname

pvalues = pd.read_csv(filename,
                      delim_whitespace=True)
column_names = pd.read_csv("columns", header=None)


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
