# Community Health of Open-Source Software

Exploration of community health in open-source software communities developing
on GitHub.

## Data

Data for this project were obtained through the GitHub API. For reproducibility,
we provide access to the data as they existed at the time of our analysis. Data
can be found in a zipped folder in our [OSF project](https://osf.io/6ncwt/). The
files are organized in that folder as follows:

* `project_name`: Each project included in our experiment includes its own top-
  directory, named according to the repository.
  * `project_name/issues.tsv`: Includes tickets, issues, and pull requests made
    on the project. In addition to the columns provided automatically by GitHub,
    we have also created two additional columns:
      * `num_PR_created`: the number of PR created before that issue/PR by that
        user.
      * `num_issue_created`: the number of issues created before that issue/PR
        by the corresponding author.
  * `project_name/comments.tsv`: Includes all comments made on the issues for
    the project.
