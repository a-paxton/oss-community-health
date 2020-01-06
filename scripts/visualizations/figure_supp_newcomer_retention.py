import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

model_results = pd.read_csv("results/models/model_2.1.tsv", sep="\t")

fig, ax = plt.subplots(figsize=(7.007874 / 2, 4.2047 / 2))
fig.subplots_adjust(left=0.2)
means = model_results["Estimate"].loc[
    ["ticket_familyissue",
     "ticket_familypr"]]
yerr = model_results["Std..Error"].loc[
    ["ticket_familyissue",
     "ticket_familypr"]]

ax.bar([1, 2], means, color="#000000")
ax.spines["right"].set_linewidth(0)
ax.spines["top"].set_linewidth(0)
ax.spines["bottom"].set_position(('data', 0))
ax.xaxis.set_ticks_position('top')
ax.set_xticks([1, 2])
ax.set_xticklabels(["Issue", "PR"], fontweight="bold")
ax.set_ylabel("Retention Rate", fontweight="bold")

fig.savefig("figures/supp/retention_rates_ticket_vs_PR.pdf")
fig.savefig("figures/supp/retention_rates_ticket_vs_PR.png")


data = pd.read_csv("results/data/newcomer_retention.tsv", sep="\t")

###############################################################################
# comment sentiment max negative
intercept_issue = model_results["Estimate"].loc["ticket_familyissue2"]
intercept_pr = model_results["Estimate"].loc["ticket_familypr2"]

Ticket = model_results["Estimate"].loc[
    "ticket_familyissue:comment_sentiment_max_negative"]
PR = model_results["Estimate"].loc[
    "ticket_familypr:comment_sentiment_max_negative"]
x = np.linspace(0, 1, 100)
fig, ax = plt.subplots(figsize=(7.007874 / 2, 4.2047 / 2), tight_layout=True)
ax.plot(x, intercept_issue + Ticket * x, label="Issue")
ax.plot(x, intercept_pr + PR * x, label="PR")
ax.legend(frameon=False)

ax.spines["right"].set_linewidth(0)
ax.spines["top"].set_linewidth(0)
ax.set_ylabel("Newcomer retention", fontweight="bold")
ax.set_xlabel("Max negative emotion", fontweight="bold")
fig.savefig(
    "figures/supp/newcomer_retention_max_negative_emotion_cross_ticket.pdf")
fig.savefig(
    "figures/supp/newcomer_retention_max_negative_emotion_cross_ticket.png")
