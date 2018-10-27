# Community health of open-source software: Variable metadata

This file contains a description of each variable in the original data files and
the new variables we create throughout the process.

## Original data

* `comments.tsv`: Dataframe of information on comments, derived from GitHub API
  * `author_association`: Comment author's role in the project
    * `NONE`: No association with the project
    * `FIRST_TIMER`: Has not previously committed to GitHub
    * `FIRST_TIME_CONTRIBUTOR`: First time contributing to this repository
    * `COLLABORATOR`: Has previously contributed to repository
    * `MEMBER`: Member of the organization that owns the repository
    * `CONTRIBUTOR`: Invited to collaborate on repository
    * `OWNER`: Owner of repository
  * `body`: Comment content
  * `created_at`: Time of comment creation
  * `id`: Unique identifier of comment
  * `node_id`: Unique identifier of entry for graphQL
  * `updated_at`: Time of comment update
  * `ticket_id`: Sequential identifier of ticket (issue or PR) in repository
  * `author_name`: Commenter's GitHub username
  * `author_id`: Commenter's unique identifier
* `issues.tsv`:  Dataframe of information on tickets, derived from GitHub API
  * `assignees`: Assigned users to ticket
  * `author_association`: Ticket author's role in the project
    * `NONE`: No association with the project
    * `FIRST_TIMER`: Has not previously committed to GitHub
    * `FIRST_TIME_CONTRIBUTOR`: First time contributing to this repository
    * `COLLABORATOR`: Has previously contributed to repository
    * `MEMBER`: Member of the organization that owns the repository
    * `CONTRIBUTOR`: Invited to collaborate on repository
    * `OWNER`: Owner of repository
  * `body`: Content of ticket
  * `closed_at`: Date and time when ticket was closed
  * `comments`: Number of comments made on ticket
  * `created_at`: Date and time of ticket creation
  * `id`: Unique identifier for ticket
  * `labels`
  * `locked`
  * `node_id`: Unique identifier for ticket for graphQL
  * `project`: Name of repository
  * `organization`: Name of organization that owns the repository
  * `author_name`: Ticket creator's GitHub username
  * `author_id`: Ticket creator's unique identifier
  * `ticket_id`: Sequential identifier of ticket (issue or PR) in repository
  * `type`: Type of ticket
    * `issue`
    * `pull_request`

## Calculated variables

* Created with `annotate_comments_tickets.py`
  * `comments_df`
    * `num_PR_created`: Number of pull requests created by the commenter before
      this comment
    * `num_issue_created`: Number of issues created by the commenter before
      this comment
    * `was_updated`: Whether the comment body was updated after posting
    * `comment_order`: The index of the comment within the ticket
  * `issues_df`
    * `num_PR_created`: Number of pull requests created by the ticket creator
      before this ticket
    * `num_issue_created`: Number of issues created by the ticket creator
      before this ticket
    * `was_updated`: Whether the ticket body was updated after posting
    * `is_closed`: Whether the ticket has been closed
