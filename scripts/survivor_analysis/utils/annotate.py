

def annotate_comments_tickets(comments, tickets):
    """
    Annotates comments and tickets with additional information

    1. whether the body was updated (Boolean)
    2. the number of PRs and issues opened by the comment author at the time
         of the comment posting
    3. comment order (comment dataframe only)
    4. identify whether ticket is closed (Boolean; ticket dataframe only)

    Requires: pandas

    Parameters
    ----------
    comments : pd.DataFrame

    tickets : pd.DataFrame

    Returns
    -------
    The same dataframe, but with additional columns

    Examples
    --------
    >> import pandas as pd
    >> import utils
    >> tickets = pd.read_csv("data/numpy/issues.tsv", sep="\t")
    >> comments = pd.read_csv("data/numpy/comments.tsv", sep="\t")
    >> comments, tickets = utils.annotate_comments(comments, tickets)
    """

    # import pandas
    import pandas as pd

    # identify whether the body of comments or tickets were updated
    comments["was_updated"] = comments["created_at"] != comments["updated_at"]
    tickets["was_updated"] = tickets["created_at"] != tickets["updated_at"]

    # add number of PRs created by author to date
    num_PR_per_pers = [
        sum((tickets["created_at"] < created_at) &
            (tickets["type"] == "pull_request") &
            (tickets["author_id"] == author_id))
        for created_at, author_id
        in zip(comments["created_at"], comments["author_id"])]
    comments["num_PR_created"] = num_PR_per_pers

    # add number of issues created by author to date
    num_issue_per_pers = [
        sum((tickets["created_at"] < created_at) &
            (tickets["type"] == "issue") &
            (tickets["author_id"] == author_id))
        for created_at, author_id
        in zip(comments["created_at"], comments["author_id"])]
    comments["num_issue_created"] = num_issue_per_pers

    # track the comment order
    comments['comment_order'] = comments.sort_values(by=['created_at']) \
                                        .groupby(by=['ticket_id']) \
                                        .cumcount()

    # identify whether the PR is closed
    tickets['is_closed'] = pd.notnull(tickets['closed_at'])

    # return the dataframes
    return comments, tickets
