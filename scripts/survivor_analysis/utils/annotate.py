import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime
from nltk.tokenize import RegexpTokenizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def annotate_logs(comments, tickets):
    """
    Annotates comments and tickets with additional information:

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
    >> comments, tickets = utils.annotate_logs(comments, tickets)
    """

    # identify whether the body of comments or tickets were updated
    comments["was_updated"] = comments["created_at"] != comments["updated_at"]
    tickets["was_updated"] = tickets["created_at"] != tickets["updated_at"]

    # comments df: add number of PRs created by author to date
    num_PR_per_pers = [
        sum((tickets["created_at"] < created_at) &
            (tickets["type"] == "pull_request") &
            (tickets["author_id"] == author_id))
        for created_at, author_id
        in zip(comments["created_at"], comments["author_id"])]
    comments["num_PR_created"] = num_PR_per_pers

    # issues df: add number of PRs created by author to date
    num_PR_per_pers = [
        sum((tickets["created_at"] < created_at) &
            (tickets["type"] == "pull_request") &
            (tickets["author_id"] == author_id))
        for created_at, author_id
        in zip(tickets["created_at"], tickets["author_id"])]
    tickets["num_PR_created"] = num_PR_per_pers

    # comments df: add number of issues created by author to date
    num_issue_per_pers = [
        sum((tickets["created_at"] < created_at) &
            (tickets["type"] == "issue") &
            (tickets["author_id"] == author_id))
        for created_at, author_id
        in zip(comments["created_at"], comments["author_id"])]
    comments["num_issue_created"] = num_issue_per_pers

    # tickets df: add number of issues created by author to date
    num_issue_per_pers = [
        sum((tickets["created_at"] < created_at) &
            (tickets["type"] == "issue") &
            (tickets["author_id"] == author_id))
        for created_at, author_id
        in zip(tickets["created_at"], tickets["author_id"])]
    tickets["num_issue_created"] = num_issue_per_pers

    # track the comment order
    comments['comment_order'] = comments.sort_values(by=['created_at']) \
                                        .groupby(by=['ticket_id']) \
                                        .cumcount()

    # identify whether the PR is closed
    tickets['is_closed'] = pd.notnull(tickets['closed_at'])
    tmp = tickets["closed_at"]
    tmp[tmp.isnull()] = pd.to_datetime(datetime.now())
    tickets["open_duration"] = (
        pd.to_datetime(tmp) - pd.to_datetime(tickets["created_at"]))

    # Now we want to remove this estimate for anything created before 1970
    m = [True if c.startswith("1970") else False
         for c in tickets["created_at"]]
    tickets[m]["open_duration"] = np.nan

    # For each comment, get the information on when the corresponding ticket
    # has been opened when it is available (comments can also be added to
    # commits)
    tickets.set_index("ticket_id", inplace=True)
    comments["ticket_created_at"] = tickets.loc[
        comments["ticket_id"]]["created_at"].values
    # Reset the old index
    tickets.set_index("id", inplace=True)

    # return the dataframes
    return comments, tickets


def body_cleanup(comments, bot_list):
    """
    Prepare comment or issue dataframe for text analysis:

    1. Remove quoted text
    2. Strip newlines
    3. Count and remove code blocks
    4. Identify other users referenced in body
    5. Flag whether the author was a bot

    Requires: pandas

    Parameters
    ----------
    comments : pd.DataFrame, ideally annotated with `annotate_logs()`;
        can be run with either comments df or issues/tickets df

    bot_list : list or pd.Series of bot usernames to be ignored

    Returns
    -------
    The same dataframe, but with cleaned body text and new columns
    (code_blocks , referenced_users , bot_flag)

    Examples
    --------
    >> import pandas as pd
    >> import utils
    >> comments = pd.read_csv("data/numpy/comments.tsv", sep="\t")
    >> comments, tickets = utils.annotate.annotate_logs(comments, tickets)
    >> comments = utils.annotate.body_cleanup(comments, bot_list_df)
    """

    # remove text quotes
    comments['body'] = (comments['body'].replace(
        "(^|\n|\r)+\>.*(?=\n|$)", " ",
        regex=True))

    # remove newlines
    comments['body'] = (comments['body'].replace(
        "[\n\r]+", " ", regex=True))

    # count and then remove code blocks
    comments['code_blocks'] = comments['body'].str.count("\`{3}")/2
    comments['body'] = (comments['body'].replace(
        "\`{3}.*\`{3}", " ", regex=True))

    # identify other humans
    comments['referenced_users'] = comments['body'].str.findall('@\w{1,}')

    # identify bots
    comments['bot_flag'] = comments['author_name'].isin(bot_list)
    # return our dataframe
    return comments


def add_sentiment(comments):
    """
    Add sentiment analysis scores to comments dataframe:
    * negative emotion
    * positive emotion
    * neutral emotion
    * compound emotion

    Requires: pandas , vaderSentiment

    For more on vaderSentiment, see https://github.com/cjhutto/vaderSentiment

    Parameters
    ----------
    comments : pd.DataFrame
        ideally after `annotate_logs()` and `body_cleanup()`;
        can be run with either comments df or issues/tickets df

    Returns
    -------
    The same dataframe but with new sentiment columns

    Examples
    --------
    >> import pandas as pd
    >> import utils
    >> comments = pd.read_csv("data/numpy/comments.tsv", sep="\t")
    >> comments, tickets = utils.annotate.annotate_logs(comments, tickets)
    >> comments = utils.annotate.body_cleanup(comments, bot_list_df)
    >> comments = utils.annotate.add_sentiment(comments)
    """

    # initialize sentiment analyzer
    analyser = SentimentIntensityAnalyzer()

    # remove NaNs
    comments['body'] = comments['body'].replace(np.nan, ' ', regex=True)

    # run sentiment analyzer over each comment body
    sentiment_df = (
        comments['body']
        .apply(analyser.polarity_scores)
        .astype(str)
        .str.strip('{}')
        .str.split(', ', expand=True))

    # split the emotion output dictionary into new columns
    # (thanks to https://stackoverflow.com/a/13053267 for partial solution)
    comments['negative_emotion'] = sentiment_df[0].str.split(
        ': ').str[-1].astype(float)
    comments['neutral_emotion'] = sentiment_df[1].str.split(
        ': ').str[-1].astype(float)
    comments['positive_emotion'] = sentiment_df[2].str.split(
        ': ').str[-1].astype(float)
    comments['compound_emotion'] = sentiment_df[3].str.split(
        ': ').str[-1].astype(float)

    # return our dataframe
    return comments


def add_gratitude(comments, grateful_list):
    """
    Track expressions of gratitude:
    * overall counts
    * specific words

    Thanks to https://stackoverflow.com/a/47686394

    Requires: pandas , nltk , collections

    Parameters
    ----------
    comments : pd.DataFrame
        ideally after `annotate_logs()` and `body_cleanup()`;
        can be run with either comments df or issues/tickets df

    grateful_list : list or pd.Series of gratitude words to identify;
        currently works only with grateful unigrams

    Returns
    -------
    The same dataframe but with new gratitude columns

    Examples
    --------
    >> import pandas as pd
    >> import utils
    >> comments = pd.read_csv("data/numpy/comments.tsv", sep="\t")
    >> comments, tickets = utils.annotate.annotate_logs(comments, tickets)
    >> comments = utils.annotate.body_cleanup(comments, bot_list_df)
    >> comments = utils.annotate.add_gratitude(comments)
    """

    # tokenize and count words
    tokenizer = RegexpTokenizer(r'\w+')
    comments['tokenized'] = comments['body'].apply(
        str.lower).apply(tokenizer.tokenize)
    comments['word_count'] = comments['tokenized'].apply(lambda x: Counter(x))

    # count words if they're in our grateful list
    comments['grateful_count'] = (
        comments['word_count'].apply(
            lambda x: np.sum([v for k, v in x.items()
                              if k in grateful_list])))

    # let us know which ones were used
    comments['grateful_list'] = (
        comments['word_count'].apply(
            lambda x: [k for k in x if k in grateful_list]))

    # remove the columns we don't need anymore
    comments = comments.drop(columns=['tokenized', 'word_count'])

    # spit back our dataframe now
    return comments
