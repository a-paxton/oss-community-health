"""
Sentiment analysis feature extractions
"""

import os
import argparse
import pandas as pd
from utils import annotate, project_features

parser = argparse.ArgumentParser()
parser.add_argument("folder",
                    help="Folder containing the data downloaded from GitHub")
parser.add_argument("--output-folder", "-o", default=None)
args = parser.parse_args()

folder = args.folder
output_folder = args.output_folder

project = folder.split("/")[-1]

# load in the lists needed
bot_list = pd.read_csv('../bot_names.txt')['bot_name']
gratitude_list = set(
    pd.read_csv('./utils/gratitude.txt')['expressions_of_gratitude'])

# Load all of the information we have on the projects
temp_comments = pd.read_csv(os.path.join(folder, 'comments.tsv'),
                            sep='\t', index_col=0).sort_index()
temp_issues = pd.read_csv(os.path.join(folder, 'issues.tsv'),
                          sep='\t', index_col=0).sort_index()
temp_commits = pd.read_csv(os.path.join(folder, 'commits.tsv'),
                           sep='\t', index_col=0).sort_index()

# append the current project to each
temp_comments['project'] = project
temp_issues['project'] = project
temp_commits['project'] = project

# annotate each file
temp_comments, temp_issues = annotate.annotate_logs(temp_comments,
                                                    temp_issues)

# drop columns we don't need
temp_comments = temp_comments.drop(
    columns=['node_id', 'updated_at', 'author_id'])
temp_issues = temp_issues.drop(
    columns=['node_id', 'organization', 'author_id', 'locked'])
# temp_commits = temp_commits.drop(columns=['author_id','sha'])

# clean up the text body
temp_comments = annotate.body_cleanup(temp_comments, bot_list)
temp_issues = annotate.body_cleanup(temp_issues, bot_list)
# temp_commits = annotate.body_cleanup(temp_commits, bot_list)

# run sentiment analysis
temp_comments = annotate.add_sentiment(temp_comments)
temp_issues = annotate.add_sentiment(temp_issues)
# temp_commits = annotate.add_sentiment(temp_commits)

# add gratitude info
temp_comments = annotate.add_gratitude(temp_comments, gratitude_list)
temp_issues = annotate.add_gratitude(temp_issues, gratitude_list)
# temp_commits = annotate.add_gratitude(temp_commits, gratitude_list)

# join the dataframes
temp_issues.set_index("ticket_id", inplace=True, drop=False)
temp_joined_frame = (temp_comments.join(
    temp_issues,
    lsuffix='_comment',
    rsuffix='_issue',
    on='ticket_id').reset_index(
        drop=True).drop(
            columns='project_comment').rename(
                columns={'project_issue': 'project'}))

# calculate bus factor
temp_bus_factor = project_features.compute_bus_factor(temp_commits)
temp_joined_frame['bus_factor'] = temp_bus_factor

# save cleaned data to intermediary folders
if output_folder is not None:
    try:
        os.makedirs(output_folder)
    except OSError:
        pass

    temp_comments.to_csv(
        os.path.join(output_folder, 'processed-comments.csv'),
        index=False, header=True)
    temp_issues.to_csv(
        os.path.join(output_folder, 'processed-issues.csv'),
        index=False, header=True)
    temp_commits.to_csv(
        os.path.join(output_folder, 'processed-commits.csv'),
        index=False, header=True)
    temp_joined_frame.to_csv(
        os.path.join(output_folder, 'processed-joined.csv'),
        index=False, header=True)