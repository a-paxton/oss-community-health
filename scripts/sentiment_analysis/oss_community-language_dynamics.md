---
title: "Communication dynamics in OSS communities"
output:
  html_document:
    keep_md: yes
    number_sections: yes
    toc: true
---

This R markdown provides the data preparation for our forthcoming manuscript
(Paxton, Varoquaux, Geiger, & Holdgraf, *in preparation*).

To run this from scratch, you will need the following files:

* `../../data/analysis_data/sentiment_frame_tickets-for_r.csv`: Contains cleaned
**tickets**-related data and derived variables from scraped GitHub data.
* `../../data/analysis_data/sentiment_frame_comments-for_r.csv`: Contains
cleaned **comments**-related data and derived variables from scraped GitHub
data.
* `./utils/ossc-libraries_and_functions.r`: Loads in necessary libraries and
creates new functions for our analyses.

**Code written by**: A. Paxton (University of Connecticut) & N. Varoquaux
(University of California, Berkeley)

**Date last modified**: 25 September 2019



***

# Preliminaries


```r
# clear everything
rm(list=ls())

# load libraries and add new functions
source('./utils/ossc-libraries_and_functions.r')

# load data
tickets_frame = read.csv('../../data/analysis_data/dataset_scip/sentiment_frame_tickets-for_r.tsv',
                          sep = '\t', stringsAsFactors=FALSE)

comments_frame = read.csv('../../data/analysis_data/dataset_scip/sentiment_frame_comments-for_r.tsv',
                          sep = '\t', stringsAsFactors=FALSE)

ticket_frame_preserve = tickets_frame
tickets_frame = ticket_frame_preserve
comment_frame_preserve = comments_frame
comments_frame = comment_frame_preserve
```


```r
# Sometimes, R fails to load the CSV file properly and truncates it. This cell
# does a basic check on the size of the data to make sure we have the correct
# number of rows and colums.
if(all(dim(tickets_frame) != c(90117, 36))){
    stop("Problem with the ticket frame. Not the right size!!")
}

if(all(dim(comments_frame) != c(524062, 29))){
    stop("Problem with the ticket frame. Not the right size!!")
}
```



```r
# We are now going to select the dataset we'll be working on.
which_dataset = "original"
tickets_frame = tickets_frame[tickets_frame$scip_dataset == which_dataset, ]
comments_frame = comments_frame[comments_frame$scip_dataset == which_dataset, ]
```

***

## Clean up dataframes

Here, we run a number of cleanup stages to ensure that we have the data we need
(and in the right format) for our models.


```r
# fix tickets dataframe
tickets_frame = tickets_frame %>% ungroup() %>%
  
  # filter out bots
  dplyr::filter(bot_flag == "False") %>%
  dplyr::select(-bot_flag) %>%
  
  # get time in seconds, read creation date properly, and specify contribution type
  dplyr::rename(open_time = open_duration) %>%
  mutate(date = as.numeric(as.Date(created_at))) %>%
  mutate(type_family = 'post') %>%

  # Mutate those columns. Seems to think it's dealing with strings…
  mutate(num_PR_created=as.integer(num_PR_created)) %>%
  mutate(num_issue_created=as.integer(num_issue_created)) %>%
  mutate(id=as.integer(id)) %>%
  mutate(ticket_id=as.integer(ticket_id)) %>%
  mutate(automatic_grateful_count=as.integer(automatic_grateful_count)) %>% 
  mutate(code_blocks=as.numeric(code_blocks)) %>% 
  mutate(negative_emotion=as.numeric(negative_emotion)) %>%
  mutate(positive_emotion=as.numeric(positive_emotion)) %>%
  mutate(compound_emotion=as.numeric(compound_emotion)) %>%
  mutate(neutral_emotion=as.numeric(neutral_emotion)) %>%
  mutate(grateful_count=as.integer(grateful_count)) %>%
  mutate(ticket_author_last_comment_ticket=as.integer(ticket_author_last_comment_ticket)) %>%

  # figure out author associations
  mutate(total_tickets = num_PR_created + num_issue_created) %>%
  mutate(author_group = dplyr::if_else(total_tickets < 5,
                                       'nonmember',
                                       'member')) %>%
  
  # rename variables associated with type of ticket and type of contribution
  dplyr::rename(ticket_family = type) %>%
  mutate(ticket_family = recode(ticket_family, pull_request = "pr")) %>%
  mutate(type = paste0(ticket_family,'_',type_family)) %>%
  
  # convert to factors (as needed) for proper modeling
  mutate_at(vars(first_ticket),
            as.logical) %>%
  mutate_at(vars(project,
                 author_name,
                 author_group,
                 author_association,
                 type,
                 type_family,
                 ticket_family),
            as.factor) %>%
  
  # drop old columns
  dplyr::select(-ends_with('_at'))
```


```r
# fix comments dataframe
comments_frame = comments_frame %>% ungroup() %>%
  
  # filter out bots and comments on tickets that have been filtered out (due to modification date)
  dplyr::filter(bot_flag == "False") %>%
  dplyr::select(-bot_flag) %>%
  dplyr::filter(!type == "") %>%
  
  # Mutate columns
  mutate(id=as.integer(id)) %>%
  mutate(ticket_id=as.integer(ticket_id)) %>%
  mutate(automatic_grateful_count=as.integer(automatic_grateful_count)) %>%
  mutate(code_blocks=as.numeric(code_blocks)) %>% 
  mutate(negative_emotion=as.numeric(negative_emotion)) %>%
  mutate(positive_emotion=as.numeric(positive_emotion)) %>%
  mutate(compound_emotion=as.numeric(compound_emotion)) %>%
  mutate(neutral_emotion=as.numeric(neutral_emotion)) %>%
  
  # read creation date properly and add contribution type
  mutate(date = as.numeric(as.Date(created_at))) %>%
  mutate(type_family = 'reply') %>%
  
  # figure out author associations
  mutate(total_tickets = num_PR_created + num_issue_created) %>%
  mutate(author_group = dplyr::if_else(total_tickets < 5,
                                       'nonmember',
                                       'member')) %>%
  
  # rename variables associated with type of ticket and type of contribution
  dplyr::rename(ticket_family = type) %>%
  mutate(ticket_family = recode(ticket_family, pull_request = "pr")) %>%
  mutate(type = paste0(ticket_family,'_',type_family)) %>%
  
  # convert to factors (as needed) for proper modeling
  mutate_at(vars(project,
                 author_name,
                 author_group,
                 author_association,
                 type,
                 type_family,
                 ticket_family),
            as.factor) %>%
  
  # drop old columns
  dplyr::select(-ends_with('_at')) 
```

***

## Basic summary stats

Now that our data have been largely cleaned, let's take a look at some basic
patterns.




|    project     | unique_tickets | unique_comments |
|:--------------:|:--------------:|:---------------:|
|   matplotlib   |     12204      |      65592      |
|     mayavi     |      730       |      2104       |
|     numpy      |     10021      |      60973      |
|     pandas     |     23239      |     133950      |
|  scikit-image  |      3277      |      22602      |
|  scikit-learn  |     11649      |     107930      |
|     scipy      |      7142      |      42967      |
| sphinx-gallery |      409       |      2906       |

Our dataset includes 8 unique projects with a
total of 68671 unique tickets, with a
mean of 8583.875 tickets per project.

On these tickets, the dataset includes
439024 unique comments, with
5.4878\times 10^{4} average comments per project.

In total, we have 15560 unique commenters,
14147 unique ticket-creators, and
19430 overall unique users.

***

# Data analysis

***

## Model Series 1: Sentiment analysis

### Data preparation

Before we can run Model Series 1, we need to combine `tickets_frame` and
`comments_frame` into a single dataframe.


```r
# merge tickets and comments into a single frame
sentiment_frame = tickets_frame %>%
  dplyr::bind_rows(., comments_frame) %>%
  
  # keep only select variables
  dplyr::select(project,
                date,
                contains('author'),
                first_ticket,
                contains('num_'),
                contains('ticket'),
                contains('type'),
                contains('grateful_count'),
                contains('emotion'),
                contains('open_'),
                -contains('ticket_author_')) %>%
  
  # convert to factors (as needed) for proper modeling
  mutate_at(vars(first_ticket),
            as.logical) %>%
  mutate_at(vars(project,
                 author_name,
                 author_group,
                 author_association,
                 type,
                 type_family,
                 ticket_family),
            as.factor)
```

```
## Warning in bind_rows_(x, .id): Unequal factor levels: coercing to character
```

```
## Warning in bind_rows_(x, .id): binding character and factor vector,
## coercing into character vector

## Warning in bind_rows_(x, .id): binding character and factor vector,
## coercing into character vector
```

```
## Warning in bind_rows_(x, .id): Unequal factor levels: coercing to character
```

```
## Warning in bind_rows_(x, .id): binding character and factor vector,
## coercing into character vector

## Warning in bind_rows_(x, .id): binding character and factor vector,
## coercing into character vector
```

```
## Warning in bind_rows_(x, .id): Unequal factor levels: coercing to character
```

```
## Warning in bind_rows_(x, .id): binding character and factor vector,
## coercing into character vector

## Warning in bind_rows_(x, .id): binding character and factor vector,
## coercing into character vector
```

```
## Warning in bind_rows_(x, .id): Unequal factor levels: coercing to character
```

```
## Warning in bind_rows_(x, .id): binding character and factor vector,
## coercing into character vector

## Warning in bind_rows_(x, .id): binding character and factor vector,
## coercing into character vector
```

### Model 1.1: Do different kinds of user contributions materially differ in emotion?

Now we begin the actual modeling. Our first general question is whether users'
patterns of sentiment differ materially by whether they are a member of the
community versus a nonmember of the community and by their different kinds of
possible contributions (i.e., a posted pull request, a reply to a pull request,
a posted issue, or a reply to an issue).

#### Model 1.1a: Overall effects with linear mixed-effects models

This model presents the analyses in a way that is typical of psychological
analyses. We predict the changes in emotion by community membership and 
contribution type, including random effects for project and for author. This
allows us to explore the general patterns of the main and interaction terms,
rather than focusing in on the project-specific variability.


```r
# do tickets and comments materially differ in emotion?
creators_v_commenters_emotion_by_project = lmer(compound_emotion ~ type * author_group  +
                                                  (1 | project) + (1 | author_name),
                                                data = sentiment_frame,
                                                REML = FALSE)
```


|                  &nbsp;                   | Estimate  | Std..Error |   df   | t.value |   p    | p_adj  | sig |
|:-----------------------------------------:|:---------:|:----------:|:------:|:-------:|:------:|:------:|:---:|
|              **(Intercept)**              |  0.07149  |  0.009517  | 11.46  |  7.513  | 0.0001 | 0.0001 | *** |
|            **typeissue_reply**            |  0.09652  |  0.003701  | 495665 |  26.08  | 0.0001 | 0.0001 | *** |
|              **typepr_post**              | -0.002956 |  0.004442  | 496774 | -0.6655 |  0.51  |  0.58  |     |
|             **typepr_reply**              |  0.1388   |  0.003687  | 497463 |  37.65  | 0.0001 | 0.0001 | *** |
|         **author_groupnonmember**         | 0.009269  |  0.005382  | 307538 |  1.722  | 0.085  | 0.113  |     |
| **typeissue_reply:author_groupnonmember** |  0.01909  |  0.005288  | 491934 |  3.61   | 0.0003 |   0    | *** |
|   **typepr_post:author_groupnonmember**   |  0.02457  |  0.006811  | 446590 |  3.607  | 0.0003 |   0    | *** |
|  **typepr_reply:author_groupnonmember**   | -0.003124 |  0.005593  | 349946 | -0.5586 |  0.58  |  0.58  |     |

While we see significant differences in the model, interpreting the results is
difficult because of the way that `lmer` handles factor comparisons. All 
factors are compared against a "reference level," the first level in the model.
This makes intepreting models with factors that include more than two levels
incredibly difficult, because the intercept is essentially an interaction term
among all reference levels of all factors.

As a result, we turn to the biostatistics approach of multiple *t*-tests 
(corrected for comparisons) of the model estimates to better understand the 
effects.

#### Model 1.1b: In-depth investigation through *t*-tests of model estimates

First, we build a series of linear mixed-effects models with one term included
in each model (either main term or interaction term). We then use the estimates
from those models to perform *t*-tests to investigate how different levels of
the effects differ from one another (and not just from the model-level 
intercept).

Projects here are random effects, but the rest of the model is the same as 
before. This allows us to do pairwise testing of main and interaction terms,
along with better exploring inter-project variability.

##### Model 1.1b.1: Does sentiment vary significantly by community membership?

First, look at whether there are differences in sentiment between author 
groups.


```r
# do members and nonmembers materially differ in emotion?
fixed_creators_v_commenters_emotion = lmer(
  compound_emotion ~ 0 + author_group + (1 | author_name) + (1 | project),
  data=sentiment_frame,
  REML=FALSE)
```

Run *t*-tests among levels and prepare for the Model 1.1b table later.


```r
# convert Model 1.1b1 output to dataframe
coefficients_and_se = data.frame(
  summary(fixed_creators_v_commenters_emotion)$coefficients)

# get comparison names as rownames
row_names = gsub("author_group", "", 
                 gsub("type", "", row.names(coefficients_and_se)))

# convert model estimates to a dataframe
means = coefficients_and_se$Estimate
names(means) = row_names

# convert standard error to dataframe
se = coefficients_and_se$Std..Error
names(se) = row_names

# compute t-statistics and p-values for desired contrasts
contrasts = c("member-nonmember")
author_groups_tests = compute_t_statistics(
  means, se,
  contrasts)
author_groups_tests[, "p_value"] = compute_p_value_from_t_stats(
  author_groups_tests$t_stats)
```

##### Model 1.1b.2: Does sentiment vary significantly across contribution types?

Now, look at whether there are differences in sentiment between contribution
types.


```r
# do tickets and comments materially differ in emotion?
fixed_types_emotion = lmer(
  compound_emotion ~ 0 + type + (1 | author_name) + (1 | project),
  data=sentiment_frame,
  REML=FALSE)
```

Run *t*-tests among levels and prepare for the Model 1.1b table later.


```r
# convert Model 1.1b2 output to dataframe
coefficients_and_se = data.frame(
  summary(fixed_types_emotion)$coefficients)

# get comparison names as rownames
row_names = gsub("author_group", "", 
                 gsub("type", "", row.names(coefficients_and_se)))

# convert model estimates to a dataframe
means = coefficients_and_se$Estimate
names(means) = row_names

# convert standard error to dataframe
se = coefficients_and_se$Std..Error
names(se) = row_names

# compute t-statistics and p-values for desired contrasts
contrasts = c("issue_post-issue_reply", # issues: posts vs. replies
              "pr_post-pr_reply",       # PRs: posts vs. replies
              "issue_post-pr_post",     # posts: issues vs. PRs
              "issue_reply-pr_reply")   # replies: issues vs. PRs
types_tests = compute_t_statistics(
  means, se,
  contrasts)
types_tests[, "p_value"] = compute_p_value_from_t_stats(types_tests$t_stats)
```

##### Model 1.1b.3: Does sentiment vary significantly across community memberships and contribution types?

Finally, let's look at the interaction between membership and contribution.


```r
# does emotion differ by the interaction between contribution and authorship group?
community_contribution_emotion = lmer(
  compound_emotion ~ 0 + type:author_group + (1 | author_name) + (1 | project),
  data=sentiment_frame,
  REML=FALSE)
```

Run *t*-tests among levels and prepare for the Model 1.1b table later.


```r
# convert Model 1.1b3 output to dataframe
coefficients_and_se = data.frame(
  summary(community_contribution_emotion)$coefficients)

# get comparison names as rownames
row_names = gsub("author_group", "", gsub("type", "", row.names(coefficients_and_se)))

# convert model estimates to a dataframe
means = coefficients_and_se$Estimate
names(means) = row_names

# convert standard error to dataframe
se = coefficients_and_se$Std..Error
names(se) = row_names

# compute t-statistics and p-values for desired contrasts
contrasts = c(
  "issue_post:member-issue_post:nonmember",     # contribution static (issue posts); membership varies (members v. nonmembers)
  "issue_reply:member-issue_reply:nonmember",   # contribution static (issue replies); membership varies (members v. nonmembers)
  "pr_post:member-pr_post:nonmember",           # contribution static (PR posts); membership varies (members v. nonmembers)
  "pr_reply:member-pr_reply:nonmember",         # contribution static (PR replies); membership varies (members v. nonmembers)
  "issue_post:member-issue_reply:member",       # contribution varies (issue posts vs. issue replies); membership static (members)
  "issue_post:nonmember-issue_reply:nonmember", # contribution varies (issue posts vs. issue replies); membership static (nonmembers)
  "pr_post:member-pr_reply:member",             # contribution varies (PR posts vs. PR replies); membership static (members)
  "pr_post:nonmember-pr_reply:nonmember",       # contribution varies (PR posts vs. PR replies); membership static (nonmembers)
  "issue_post:member-pr_post:member",           # contribution varies (issue posts vs. PR posts); membership static (members)
  "issue_post:nonmember-pr_post:nonmember",     # contribution varies (issue posts vs. PR posts); membership static (nonmembers)
  "issue_reply:member-pr_reply:member",         # contribution varies (issue replies vs. PR replies); membership static (members)
  "issue_reply:nonmember-pr_reply:nonmember")   # contribution varies (issue replies vs. PR replies); membership static (nonmembers)
types_author_groups_tests = compute_t_statistics(
  means, se,
  contrasts)
types_author_groups_tests[, "p_value"] = compute_p_value_from_t_stats(
  types_author_groups_tests$"t_stats")
```

##### Model 1.1b.4 : Do different kinds of user contributions differ in emotion by projects?

Now adding projects into the mix to understand how the previous analysis
varies across projects.


```r
# do tickets and comments materially differ in emotion by projects?
creators_v_commenters_emotion_by_project = lmer(
  compound_emotion ~ 0 + project:type:author_group + (1 | author_name),
  data = sentiment_frame,
  REML = FALSE)
```

Run *t*-tests among levels and prepare for the Model 1.1b table later.


```r
# convert Model 1.1c output to dataframe
coefficients_and_se = data.frame(
  summary(creators_v_commenters_emotion_by_project)$coefficients)

# get comparison names as rownames
row_names = gsub(
  "project", "", gsub(
    "author_group", "", gsub(
      "type", "", row.names(coefficients_and_se))))

# replace hyphens in project names with periods
row_names = gsub(
  "scikit-", "scikit.", gsub(
    "sphinx-", "sphinx.", row_names))

# convert model estimates to a dataframe
means = coefficients_and_se$Estimate
names(means) = row_names

# convert standard error to dataframe
se = coefficients_and_se$Std..Error
names(se) = row_names

# compute t-statistics and p-values for desired contrasts
# (note: ordering of contrasts within each project is identical to Model 1.1b.3)
contrasts = c(
  
  # scikit-learn
  "scikit.learn:issue_post:member-scikit.learn:issue_post:nonmember",   
  "scikit.learn:issue_reply:member-scikit.learn:issue_reply:nonmember",
  "scikit.learn:pr_post:member-scikit.learn:pr_post:nonmember",
  "scikit.learn:pr_reply:member-scikit.learn:pr_reply:nonmember",
  "scikit.learn:issue_post:member-scikit.learn:issue_reply:member",
  "scikit.learn:issue_post:nonmember-scikit.learn:issue_reply:nonmember",
  "scikit.learn:pr_post:member-scikit.learn:pr_reply:member",
  "scikit.learn:pr_post:nonmember-scikit.learn:pr_reply:nonmember",
  "scikit.learn:issue_post:member-scikit.learn:pr_post:member",
  "scikit.learn:issue_post:nonmember-scikit.learn:pr_post:nonmember",    
  "scikit.learn:issue_reply:member-scikit.learn:pr_reply:member",  
  "scikit.learn:issue_reply:nonmember-scikit.learn:pr_reply:nonmember",
  
  # scikit-image
  "scikit.image:issue_post:member-scikit.image:issue_post:nonmember", 
  "scikit.image:issue_reply:member-scikit.image:issue_reply:nonmember",
  "scikit.image:pr_post:member-scikit.image:pr_post:nonmember",       
  "scikit.image:pr_reply:member-scikit.image:pr_reply:nonmember",     
  "scikit.image:issue_post:member-scikit.image:issue_reply:member",
  "scikit.image:issue_post:nonmember-scikit.image:issue_reply:nonmember",
  "scikit.image:pr_post:member-scikit.image:pr_reply:member",     
  "scikit.image:pr_post:nonmember-scikit.image:pr_reply:nonmember",    
  "scikit.image:issue_post:member-scikit.image:pr_post:member",   
  "scikit.image:issue_post:nonmember-scikit.image:pr_post:nonmember",    
  "scikit.image:issue_reply:member-scikit.image:pr_reply:member",  
  "scikit.image:issue_reply:nonmember-scikit.image:pr_reply:nonmember",
  
  # matplotlib
  "matplotlib:issue_post:member-matplotlib:issue_post:nonmember", 
  "matplotlib:issue_reply:member-matplotlib:issue_reply:nonmember",
  "matplotlib:pr_post:member-matplotlib:pr_post:nonmember",       
  "matplotlib:pr_reply:member-matplotlib:pr_reply:nonmember",     
  "matplotlib:issue_post:member-matplotlib:issue_reply:member",
  "matplotlib:issue_post:nonmember-matplotlib:issue_reply:nonmember",
  "matplotlib:pr_post:member-matplotlib:pr_reply:member",     
  "matplotlib:pr_post:nonmember-matplotlib:pr_reply:nonmember",    
  "matplotlib:issue_post:member-matplotlib:pr_post:member",   
  "matplotlib:issue_post:nonmember-matplotlib:pr_post:nonmember",    
  "matplotlib:issue_reply:member-matplotlib:pr_reply:member",  
  "matplotlib:issue_reply:nonmember-matplotlib:pr_reply:nonmember",
  
  # mayavi
  "mayavi:issue_post:member-mayavi:issue_post:nonmember", 
  "mayavi:issue_reply:member-mayavi:issue_reply:nonmember",
  "mayavi:pr_post:member-mayavi:pr_post:nonmember",       
  "mayavi:pr_reply:member-mayavi:pr_reply:nonmember",     
  "mayavi:issue_post:member-mayavi:issue_reply:member",
  "mayavi:issue_post:nonmember-mayavi:issue_reply:nonmember",
  "mayavi:pr_post:member-mayavi:pr_reply:member",     
  "mayavi:pr_post:nonmember-mayavi:pr_reply:nonmember",    
  "mayavi:issue_post:member-mayavi:pr_post:member",   
  "mayavi:issue_post:nonmember-mayavi:pr_post:nonmember",    
  "mayavi:issue_reply:member-mayavi:pr_reply:member",  
  "mayavi:issue_reply:nonmember-mayavi:pr_reply:nonmember",
  
  # pandas
  "pandas:issue_post:member-pandas:issue_post:nonmember", 
  "pandas:issue_reply:member-pandas:issue_reply:nonmember",
  "pandas:pr_post:member-pandas:pr_post:nonmember",       
  "pandas:pr_reply:member-pandas:pr_reply:nonmember",     
  "pandas:issue_post:member-pandas:issue_reply:member",
  "pandas:issue_post:nonmember-pandas:issue_reply:nonmember",
  "pandas:pr_post:member-pandas:pr_reply:member",     
  "pandas:pr_post:nonmember-pandas:pr_reply:nonmember",    
  "pandas:issue_post:member-pandas:pr_post:member",   
  "pandas:issue_post:nonmember-pandas:pr_post:nonmember",    
  "pandas:issue_reply:member-pandas:pr_reply:member",  
  "pandas:issue_reply:nonmember-pandas:pr_reply:nonmember",
  
  # scipy
  "scipy:issue_post:member-scipy:issue_post:nonmember", 
  "scipy:issue_reply:member-scipy:issue_reply:nonmember",
  "scipy:pr_post:member-scipy:pr_post:nonmember",       
  "scipy:pr_reply:member-scipy:pr_reply:nonmember",     
  "scipy:issue_post:member-scipy:issue_reply:member",
  "scipy:issue_post:nonmember-scipy:issue_reply:nonmember",
  "scipy:pr_post:member-scipy:pr_reply:member",     
  "scipy:pr_post:nonmember-scipy:pr_reply:nonmember",    
  "scipy:issue_post:member-scipy:pr_post:member",   
  "scipy:issue_post:nonmember-scipy:pr_post:nonmember",    
  "scipy:issue_reply:member-scipy:pr_reply:member",  
  "scipy:issue_reply:nonmember-scipy:pr_reply:nonmember",
  
  # numpy
  "numpy:issue_post:member-numpy:issue_post:nonmember", 
  "numpy:issue_reply:member-numpy:issue_reply:nonmember",
  "numpy:pr_post:member-numpy:pr_post:nonmember",       
  "numpy:pr_reply:member-numpy:pr_reply:nonmember",     
  "numpy:issue_post:member-numpy:issue_reply:member",
  "numpy:issue_post:nonmember-numpy:issue_reply:nonmember",
  "numpy:pr_post:member-numpy:pr_reply:member",     
  "numpy:pr_post:nonmember-numpy:pr_reply:nonmember",    
  "numpy:issue_post:member-numpy:pr_post:member",   
  "numpy:issue_post:nonmember-numpy:pr_post:nonmember",    
  "numpy:issue_reply:member-numpy:pr_reply:member",  
  "numpy:issue_reply:nonmember-numpy:pr_reply:nonmember",
  
  # sphinx-gallery
  "sphinx.gallery:issue_post:member-sphinx.gallery:issue_post:nonmember", 
  "sphinx.gallery:issue_reply:member-sphinx.gallery:issue_reply:nonmember",
  "sphinx.gallery:pr_post:member-sphinx.gallery:pr_post:nonmember",       
  "sphinx.gallery:pr_reply:member-sphinx.gallery:pr_reply:nonmember",     
  "sphinx.gallery:issue_post:member-sphinx.gallery:issue_reply:member",
  "sphinx.gallery:issue_post:nonmember-sphinx.gallery:issue_reply:nonmember",
  "sphinx.gallery:pr_post:member-sphinx.gallery:pr_reply:member",     
  "sphinx.gallery:pr_post:nonmember-sphinx.gallery:pr_reply:nonmember",    
  "sphinx.gallery:issue_post:member-sphinx.gallery:pr_post:member",   
  "sphinx.gallery:issue_post:nonmember-sphinx.gallery:pr_post:nonmember",    
  "sphinx.gallery:issue_reply:member-sphinx.gallery:pr_reply:member",  
  "sphinx.gallery:issue_reply:nonmember-sphinx.gallery:pr_reply:nonmember"
)
project_types_author_group_tests = compute_t_statistics(
  means, se,
  contrasts)
project_types_author_group_tests[, "p_value"] = compute_p_value_from_t_stats(
  project_types_author_group_tests$t_stats) 
```

#### Model 1.1b: Overall results

Now we bring together all analyses from Model 1.1b.


```r
# specify main terms
author_groups_tests["contrast"] = row.names(author_groups_tests)
types_tests["contrast"] = row.names(types_tests)
all_tests = merge(author_groups_tests, types_tests, all=TRUE, sort=FALSE)
all_tests["model"] = "Main Terms"

# specify 2-way interactions
types_author_groups_tests["contrast"] = row.names(types_author_groups_tests)
types_author_groups_tests["model"] = "2W: Types x Author Groups"
all_tests = merge(all_tests, types_author_groups_tests, all=TRUE, sort=FALSE)

# specify 3-way interactions
project_types_author_group_tests["contrast"] = row.names(project_types_author_group_tests)
project_types_author_group_tests["model"] = "3W: Types x Author Groups x Project"
all_tests = merge(all_tests, project_types_author_group_tests, all=TRUE,
                  sort=FALSE)
```

Let's correct all tests at once for multiple comparisons.


```r
# specify all contrasts
row.names(all_tests) = all_tests$contrast
all_tests = subset(all_tests, select=-c(contrast))

# print the table (reordering columns for readibility)
all_tests = all_tests[c("model", "t_stats", "p_value")]
pander_clean_anova(all_tests, rename_columns=FALSE)
```



|                                    &nbsp;                                    |                model                | t_stats  | p_value | p_adj  | sig |
|:----------------------------------------------------------------------------:|:-----------------------------------:|:--------:|:-------:|:------:|:---:|
|                             **member-nonmember**                             |             Main Terms              | -0.09303 |  0.93   |  0.94  |     |
|                          **issue_post-issue_reply**                          |             Main Terms              |  -8.828  | 0.0001  | 0.0001 | *** |
|                             **pr_post-pr_reply**                             |             Main Terms              |  -11.45  | 0.0001  | 0.0001 | *** |
|                            **issue_post-pr_post**                            |             Main Terms              | -0.6207  |  0.54   |  0.64  |     |
|                           **issue_reply-pr_reply**                           |             Main Terms              |  -3.329  |  0.001  | 0.002  | **  |
|                  **issue_post:member-issue_post:nonmember**                  |      2W: Types x Author Groups      | -0.7101  |  0.48   |  0.59  |     |
|                 **issue_reply:member-issue_reply:nonmember**                 |      2W: Types x Author Groups      |  -2.284  |  0.022  |  0.04  |  *  |
|                     **pr_post:member-pr_post:nonmember**                     |      2W: Types x Author Groups      |  -2.579  |  0.01   | 0.018  |  *  |
|                    **pr_reply:member-pr_reply:nonmember**                    |      2W: Types x Author Groups      | -0.4897  |  0.62   |  0.7   |     |
|                   **issue_post:member-issue_reply:member**                   |      2W: Types x Author Groups      |  -7.388  | 0.0001  | 0.0001 | *** |
|                **issue_post:nonmember-issue_reply:nonmember**                |      2W: Types x Author Groups      |  -9.318  | 0.0001  | 0.0001 | *** |
|                      **pr_post:member-pr_reply:member**                      |      2W: Types x Author Groups      |  -11.03  | 0.0001  | 0.0001 | *** |
|                   **pr_post:nonmember-pr_reply:nonmember**                   |      2W: Types x Author Groups      |   -8.9   | 0.0001  | 0.0001 | *** |
|                     **issue_post:member-pr_post:member**                     |      2W: Types x Author Groups      |  0.2227  |  0.82   |  0.89  |     |
|                  **issue_post:nonmember-pr_post:nonmember**                  |      2W: Types x Author Groups      |  -1.676  |  0.094  | 0.141  |     |
|                    **issue_reply:member-pr_reply:member**                    |      2W: Types x Author Groups      |  -3.346  |  0.001  | 0.002  | **  |
|                 **issue_reply:nonmember-pr_reply:nonmember**                 |      2W: Types x Author Groups      |  -1.63   |  0.103  | 0.151  |     |
|     **scikit.learn:issue_post:member-scikit.learn:issue_post:nonmember**     | 3W: Types x Author Groups x Project |  -0.666  |   0.5   |  0.61  |     |
|    **scikit.learn:issue_reply:member-scikit.learn:issue_reply:nonmember**    | 3W: Types x Author Groups x Project |  -3.531  | 0.0004  | 0.001  | **  |
|        **scikit.learn:pr_post:member-scikit.learn:pr_post:nonmember**        | 3W: Types x Author Groups x Project |  0.0292  |  0.98   |  0.98  |     |
|       **scikit.learn:pr_reply:member-scikit.learn:pr_reply:nonmember**       | 3W: Types x Author Groups x Project | -0.7557  |  0.45   |  0.56  |     |
|      **scikit.learn:issue_post:member-scikit.learn:issue_reply:member**      | 3W: Types x Author Groups x Project |  -8.905  | 0.0001  | 0.0001 | *** |
|   **scikit.learn:issue_post:nonmember-scikit.learn:issue_reply:nonmember**   | 3W: Types x Author Groups x Project |  -12.53  | 0.0001  | 0.0001 | *** |
|         **scikit.learn:pr_post:member-scikit.learn:pr_reply:member**         | 3W: Types x Author Groups x Project |  -12.62  | 0.0001  | 0.0001 | *** |
|      **scikit.learn:pr_post:nonmember-scikit.learn:pr_reply:nonmember**      | 3W: Types x Author Groups x Project |  -13.32  | 0.0001  | 0.0001 | *** |
|        **scikit.learn:issue_post:member-scikit.learn:pr_post:member**        | 3W: Types x Author Groups x Project |  -1.875  |  0.061  | 0.094  |  .  |
|     **scikit.learn:issue_post:nonmember-scikit.learn:pr_post:nonmember**     | 3W: Types x Author Groups x Project |  -1.352  |  0.176  | 0.243  |     |
|       **scikit.learn:issue_reply:member-scikit.learn:pr_reply:member**       | 3W: Types x Author Groups x Project |  -6.373  | 0.0001  | 0.0001 | *** |
|    **scikit.learn:issue_reply:nonmember-scikit.learn:pr_reply:nonmember**    | 3W: Types x Author Groups x Project |  -3.788  | 0.0002  | 0.0004 | *** |
|     **scikit.image:issue_post:member-scikit.image:issue_post:nonmember**     | 3W: Types x Author Groups x Project |  -1.238  |  0.216  |  0.29  |     |
|    **scikit.image:issue_reply:member-scikit.image:issue_reply:nonmember**    | 3W: Types x Author Groups x Project |  -1.251  |  0.211  |  0.29  |     |
|        **scikit.image:pr_post:member-scikit.image:pr_post:nonmember**        | 3W: Types x Author Groups x Project |  -7.149  | 0.0001  | 0.0001 | *** |
|       **scikit.image:pr_reply:member-scikit.image:pr_reply:nonmember**       | 3W: Types x Author Groups x Project |  -1.972  |  0.049  | 0.077  |  .  |
|      **scikit.image:issue_post:member-scikit.image:issue_reply:member**      | 3W: Types x Author Groups x Project |  -7.62   | 0.0001  | 0.0001 | *** |
|   **scikit.image:issue_post:nonmember-scikit.image:issue_reply:nonmember**   | 3W: Types x Author Groups x Project |  -7.292  | 0.0001  | 0.0001 | *** |
|         **scikit.image:pr_post:member-scikit.image:pr_reply:member**         | 3W: Types x Author Groups x Project |  -8.905  | 0.0001  | 0.0001 | *** |
|      **scikit.image:pr_post:nonmember-scikit.image:pr_reply:nonmember**      | 3W: Types x Author Groups x Project | -0.5706  |  0.57   |  0.67  |     |
|        **scikit.image:issue_post:member-scikit.image:pr_post:member**        | 3W: Types x Author Groups x Project |  -3.253  |  0.001  | 0.002  | **  |
|     **scikit.image:issue_post:nonmember-scikit.image:pr_post:nonmember**     | 3W: Types x Author Groups x Project |  -8.13   | 0.0001  | 0.0001 | *** |
|       **scikit.image:issue_reply:member-scikit.image:pr_reply:member**       | 3W: Types x Author Groups x Project |  -4.009  | 0.0001  | 0.0002 | *** |
|    **scikit.image:issue_reply:nonmember-scikit.image:pr_reply:nonmember**    | 3W: Types x Author Groups x Project |  -3.981  | 0.0001  | 0.0002 | *** |
|       **matplotlib:issue_post:member-matplotlib:issue_post:nonmember**       | 3W: Types x Author Groups x Project | -0.8706  |  0.38   |  0.48  |     |
|      **matplotlib:issue_reply:member-matplotlib:issue_reply:nonmember**      | 3W: Types x Author Groups x Project |  -1.846  |  0.065  | 0.099  |  .  |
|          **matplotlib:pr_post:member-matplotlib:pr_post:nonmember**          | 3W: Types x Author Groups x Project | -0.8664  |  0.39   |  0.48  |     |
|         **matplotlib:pr_reply:member-matplotlib:pr_reply:nonmember**         | 3W: Types x Author Groups x Project |  -1.663  |  0.096  | 0.143  |     |
|        **matplotlib:issue_post:member-matplotlib:issue_reply:member**        | 3W: Types x Author Groups x Project |  -7.369  | 0.0001  | 0.0001 | *** |
|     **matplotlib:issue_post:nonmember-matplotlib:issue_reply:nonmember**     | 3W: Types x Author Groups x Project |  -9.981  | 0.0001  | 0.0001 | *** |
|           **matplotlib:pr_post:member-matplotlib:pr_reply:member**           | 3W: Types x Author Groups x Project |  -11.45  | 0.0001  | 0.0001 | *** |
|        **matplotlib:pr_post:nonmember-matplotlib:pr_reply:nonmember**        | 3W: Types x Author Groups x Project |  -8.938  | 0.0001  | 0.0001 | *** |
|          **matplotlib:issue_post:member-matplotlib:pr_post:member**          | 3W: Types x Author Groups x Project |  -0.564  |  0.57   |  0.67  |     |
|       **matplotlib:issue_post:nonmember-matplotlib:pr_post:nonmember**       | 3W: Types x Author Groups x Project | -0.5298  |   0.6   |  0.69  |     |
|         **matplotlib:issue_reply:member-matplotlib:pr_reply:member**         | 3W: Types x Author Groups x Project |  -2.933  |  0.003  | 0.007  | **  |
|      **matplotlib:issue_reply:nonmember-matplotlib:pr_reply:nonmember**      | 3W: Types x Author Groups x Project |  -2.734  |  0.006  | 0.012  |  *  |
|           **mayavi:issue_post:member-mayavi:issue_post:nonmember**           | 3W: Types x Author Groups x Project |  -1.564  |  0.118  | 0.166  |     |
|          **mayavi:issue_reply:member-mayavi:issue_reply:nonmember**          | 3W: Types x Author Groups x Project |  -1.404  |  0.16   | 0.224  |     |
|              **mayavi:pr_post:member-mayavi:pr_post:nonmember**              | 3W: Types x Author Groups x Project | -0.5194  |   0.6   |  0.69  |     |
|             **mayavi:pr_reply:member-mayavi:pr_reply:nonmember**             | 3W: Types x Author Groups x Project |  -2.07   |  0.038  | 0.063  |  .  |
|            **mayavi:issue_post:member-mayavi:issue_reply:member**            | 3W: Types x Author Groups x Project |  -1.881  |  0.06   | 0.094  |  .  |
|         **mayavi:issue_post:nonmember-mayavi:issue_reply:nonmember**         | 3W: Types x Author Groups x Project |  -2.89   |  0.004  | 0.008  | **  |
|               **mayavi:pr_post:member-mayavi:pr_reply:member**               | 3W: Types x Author Groups x Project |  -2.277  |  0.023  |  0.04  |  *  |
|            **mayavi:pr_post:nonmember-mayavi:pr_reply:nonmember**            | 3W: Types x Author Groups x Project |  -3.397  |  0.001  | 0.002  | **  |
|              **mayavi:issue_post:member-mayavi:pr_post:member**              | 3W: Types x Author Groups x Project | -0.06947 |  0.94   |  0.95  |     |
|           **mayavi:issue_post:nonmember-mayavi:pr_post:nonmember**           | 3W: Types x Author Groups x Project |  1.067   |  0.29   |  0.37  |     |
|             **mayavi:issue_reply:member-mayavi:pr_reply:member**             | 3W: Types x Author Groups x Project | -0.1931  |  0.85   |  0.89  |     |
|          **mayavi:issue_reply:nonmember-mayavi:pr_reply:nonmember**          | 3W: Types x Author Groups x Project |  -1.566  |  0.117  | 0.166  |     |
|           **pandas:issue_post:member-pandas:issue_post:nonmember**           | 3W: Types x Author Groups x Project |  -1.062  |  0.29   |  0.37  |     |
|          **pandas:issue_reply:member-pandas:issue_reply:nonmember**          | 3W: Types x Author Groups x Project |  -5.46   | 0.0001  | 0.0001 | *** |
|              **pandas:pr_post:member-pandas:pr_post:nonmember**              | 3W: Types x Author Groups x Project |  -4.601  | 0.0001  | 0.0001 | *** |
|             **pandas:pr_reply:member-pandas:pr_reply:nonmember**             | 3W: Types x Author Groups x Project |  2.577   |  0.01   | 0.018  |  *  |
|            **pandas:issue_post:member-pandas:issue_reply:member**            | 3W: Types x Author Groups x Project |  -9.877  | 0.0001  | 0.0001 | *** |
|         **pandas:issue_post:nonmember-pandas:issue_reply:nonmember**         | 3W: Types x Author Groups x Project |  -15.01  | 0.0001  | 0.0001 | *** |
|               **pandas:pr_post:member-pandas:pr_reply:member**               | 3W: Types x Author Groups x Project |  -18.34  | 0.0001  | 0.0001 | *** |
|            **pandas:pr_post:nonmember-pandas:pr_reply:nonmember**            | 3W: Types x Author Groups x Project |  -8.317  | 0.0001  | 0.0001 | *** |
|              **pandas:issue_post:member-pandas:pr_post:member**              | 3W: Types x Author Groups x Project |  4.595   | 0.0001  | 0.0001 | *** |
|           **pandas:issue_post:nonmember-pandas:pr_post:nonmember**           | 3W: Types x Author Groups x Project |  0.4341  |  0.66   |  0.74  |     |
|             **pandas:issue_reply:member-pandas:pr_reply:member**             | 3W: Types x Author Groups x Project |  -3.831  | 0.0001  | 0.0003 | *** |
|          **pandas:issue_reply:nonmember-pandas:pr_reply:nonmember**          | 3W: Types x Author Groups x Project |  3.939   | 0.0001  | 0.0002 | *** |
|            **scipy:issue_post:member-scipy:issue_post:nonmember**            | 3W: Types x Author Groups x Project |  -2.994  |  0.003  | 0.006  | **  |
|           **scipy:issue_reply:member-scipy:issue_reply:nonmember**           | 3W: Types x Author Groups x Project |  -5.599  | 0.0001  | 0.0001 | *** |
|               **scipy:pr_post:member-scipy:pr_post:nonmember**               | 3W: Types x Author Groups x Project |  -3.891  | 0.0001  | 0.0003 | *** |
|              **scipy:pr_reply:member-scipy:pr_reply:nonmember**              | 3W: Types x Author Groups x Project |  -2.103  |  0.035  | 0.059  |  .  |
|             **scipy:issue_post:member-scipy:issue_reply:member**             | 3W: Types x Author Groups x Project |  -8.777  | 0.0001  | 0.0001 | *** |
|          **scipy:issue_post:nonmember-scipy:issue_reply:nonmember**          | 3W: Types x Author Groups x Project |  -11.82  | 0.0001  | 0.0001 | *** |
|                **scipy:pr_post:member-scipy:pr_reply:member**                | 3W: Types x Author Groups x Project |  -16.57  | 0.0001  | 0.0001 | *** |
|             **scipy:pr_post:nonmember-scipy:pr_reply:nonmember**             | 3W: Types x Author Groups x Project |  -10.36  | 0.0001  | 0.0001 | *** |
|               **scipy:issue_post:member-scipy:pr_post:member**               | 3W: Types x Author Groups x Project |  -2.261  |  0.024  | 0.041  |  *  |
|            **scipy:issue_post:nonmember-scipy:pr_post:nonmember**            | 3W: Types x Author Groups x Project |  -2.864  |  0.004  | 0.008  | **  |
|              **scipy:issue_reply:member-scipy:pr_reply:member**              | 3W: Types x Author Groups x Project |  -9.007  | 0.0001  | 0.0001 | *** |
|           **scipy:issue_reply:nonmember-scipy:pr_reply:nonmember**           | 3W: Types x Author Groups x Project |  -4.303  | 0.0001  | 0.0001 | *** |
|            **numpy:issue_post:member-numpy:issue_post:nonmember**            | 3W: Types x Author Groups x Project |  0.1347  |  0.89   |  0.92  |     |
|           **numpy:issue_reply:member-numpy:issue_reply:nonmember**           | 3W: Types x Author Groups x Project |  -2.47   |  0.014  | 0.025  |  *  |
|               **numpy:pr_post:member-numpy:pr_post:nonmember**               | 3W: Types x Author Groups x Project | -0.2003  |  0.84   |  0.89  |     |
|              **numpy:pr_reply:member-numpy:pr_reply:nonmember**              | 3W: Types x Author Groups x Project |  0.4999  |  0.62   |  0.7   |     |
|             **numpy:issue_post:member-numpy:issue_reply:member**             | 3W: Types x Author Groups x Project |  -9.885  | 0.0001  | 0.0001 | *** |
|          **numpy:issue_post:nonmember-numpy:issue_reply:nonmember**          | 3W: Types x Author Groups x Project |  -13.27  | 0.0001  | 0.0001 | *** |
|                **numpy:pr_post:member-numpy:pr_reply:member**                | 3W: Types x Author Groups x Project |  -16.96  | 0.0001  | 0.0001 | *** |
|             **numpy:pr_post:nonmember-numpy:pr_reply:nonmember**             | 3W: Types x Author Groups x Project |  -11.68  | 0.0001  | 0.0001 | *** |
|               **numpy:issue_post:member-numpy:pr_post:member**               | 3W: Types x Author Groups x Project |  -1.991  |  0.046  | 0.075  |  .  |
|            **numpy:issue_post:nonmember-numpy:pr_post:nonmember**            | 3W: Types x Author Groups x Project |  -2.204  |  0.028  | 0.046  |  *  |
|              **numpy:issue_reply:member-numpy:pr_reply:member**              | 3W: Types x Author Groups x Project |  -9.482  | 0.0001  | 0.0001 | *** |
|           **numpy:issue_reply:nonmember-numpy:pr_reply:nonmember**           | 3W: Types x Author Groups x Project |  -5.036  | 0.0001  | 0.0001 | *** |
|   **sphinx.gallery:issue_post:member-sphinx.gallery:issue_post:nonmember**   | 3W: Types x Author Groups x Project |  0.5634  |  0.57   |  0.67  |     |
|  **sphinx.gallery:issue_reply:member-sphinx.gallery:issue_reply:nonmember**  | 3W: Types x Author Groups x Project | -0.3587  |  0.72   |  0.79  |     |
|      **sphinx.gallery:pr_post:member-sphinx.gallery:pr_post:nonmember**      | 3W: Types x Author Groups x Project |  -1.624  |  0.104  | 0.151  |     |
|     **sphinx.gallery:pr_reply:member-sphinx.gallery:pr_reply:nonmember**     | 3W: Types x Author Groups x Project |   0.13   |   0.9   |  0.92  |     |
|    **sphinx.gallery:issue_post:member-sphinx.gallery:issue_reply:member**    | 3W: Types x Author Groups x Project |  -3.571  | 0.0004  | 0.001  | **  |
| **sphinx.gallery:issue_post:nonmember-sphinx.gallery:issue_reply:nonmember** | 3W: Types x Author Groups x Project |  -4.126  | 0.0001  | 0.0001 | *** |
|       **sphinx.gallery:pr_post:member-sphinx.gallery:pr_reply:member**       | 3W: Types x Author Groups x Project |  -3.456  |    0    | 0.001  | **  |
|    **sphinx.gallery:pr_post:nonmember-sphinx.gallery:pr_reply:nonmember**    | 3W: Types x Author Groups x Project |  -0.181  |  0.86   |  0.9   |     |
|      **sphinx.gallery:issue_post:member-sphinx.gallery:pr_post:member**      | 3W: Types x Author Groups x Project | -0.2976  |  0.77   |  0.83  |     |
|   **sphinx.gallery:issue_post:nonmember-sphinx.gallery:pr_post:nonmember**   | 3W: Types x Author Groups x Project |  -2.209  |  0.027  | 0.046  |  *  |
|     **sphinx.gallery:issue_reply:member-sphinx.gallery:pr_reply:member**     | 3W: Types x Author Groups x Project |  1.223   |  0.221  |  0.29  |     |
|  **sphinx.gallery:issue_reply:nonmember-sphinx.gallery:pr_reply:nonmember**  | 3W: Types x Author Groups x Project |  1.033   |   0.3   |  0.39  |     |

Finally, let's plot these effects.



![**Figure**. Sentiment by contribution type (ticket vs. comment) and community membership at the time of posting (member vs. nonmember).](../../figures/sentiment_analysis/ossc-sentiment_membership_contribution-aggregated-knitr.jpg)



![**Figure**. Sentiment by contribution type (ticket vs. comment) and community membership at the time of posting (member vs. nonmember) for each project.](../../figures/sentiment_analysis/ossc-sentiment_membership_contribution-by_project-knitr.jpg)

### Model 1.2: Do tickets and comments materially differ in emotion over time?


```r
# specify number of splines basis to use
degrees_of_freedom = 4
```

In this model, we explore whether there are time-based splines in the
observations from Model 1.1. First, let's look at the splines basis functions,
and which time points they span by default.



![**Figure**. Basis functions for sentiment.](../../figures/sentiment_analysis/ossc-sentiment_basis_functions.jpg)

Now, let us use these splines model to model the time variation of the 3-way
interaction terms. We model the intercept for the three way interaction
separately from the splines: This allows us to only look at changes over time
and not changes in intercept.

Note that we cannot use too many degrees of freedom, as sphinx-gallery spans a
shorter time period than other projects. Any spline basis function that covers
only the 2012 to 2015 cannot be estimated on sphinx-gallery.




```r
# do tickets and comments materially differ in emotion over time?
degrees_of_freedom = NULL
knots = NULL

# do tickets and comments materially differ in emotion over time?
formula = (
  compound_emotion ~ 0 + project:type:author_group + 
    type:author_group:group_date_ns(
      date, project, "matplotlib",
      knots=knots, degrees_of_freedom=degrees_of_freedom) +
    type:author_group:group_date_ns(
      date, project, "mayavi",
      knots=knots, degrees_of_freedom=degrees_of_freedom) +
    type:author_group:group_date_ns(
      date, project, "numpy",
      knots=knots, degrees_of_freedom=degrees_of_freedom) +
    type:author_group:group_date_ns(
      date, project, "pandas",
      knots=knots, degrees_of_freedom=degrees_of_freedom) +
    type:author_group:group_date_ns(
      date, project, "scikit-image",
      knots=knots, degrees_of_freedom=degrees_of_freedom) +
    type:author_group:group_date_ns(
      date, project, "scikit-learn",
      knots=knots, degrees_of_freedom=degrees_of_freedom) +
    type:author_group:group_date_ns(
      date, project, "scipy",
      knots=knots, degrees_of_freedom=degrees_of_freedom) +
    type:author_group:group_date_ns(
      date, project, "sphinx-gallery",
      knots=knots, degrees_of_freedom=degrees_of_freedom) +
    (1 | author_name))

creators_v_commenters_emotion_by_project_time = lmer(
  formula,
  data = sentiment_frame,
  REML=FALSE)
```

```
## Warning: Some predictor variables are on very different scales: consider
## rescaling

## Warning: Some predictor variables are on very different scales: consider
## rescaling
```

We'll do another table to display all results.


```r
# convert Model 1.2 output to dataframe
coefficients_and_se = data.frame(
  summary(creators_v_commenters_emotion_by_project_time)$coefficients)

# get comparison names as rownames
row_names = gsub(
  "project", "", gsub(
    "author_group", "", gsub("type", "", row.names(coefficients_and_se))))

# Now deal with the very annoying splines coefficient row.names
row_names = gsub(
  "group_date_ns(date, , \"", "", row_names, fixed=TRUE)
row_names = gsub(
  "\", knots = knots, degrees_of_freedom = degrees_of_freedom)", ":coef", row_names, fixed=TRUE)


# replace hyphens in project names with periods
row_names = gsub(
  "scikit-", "scikit.", gsub(
    "sphinx-", "sphinx.", row_names))


# convert model estimates to a dataframe
means = coefficients_and_se$Estimate
names(means) = row_names

# convert standard error to dataframe
se = coefficients_and_se$Std..Error
names(se) = row_names

# we're interested in looking at the coefficients of the splines.
partial_time_contrasts = c(
  # scikit-learn
  "issue_post:member:scikit.learn-issue_post:nonmember:scikit.learn",   
  "issue_reply:member:scikit.learn-issue_reply:nonmember:scikit.learn",
  "pr_post:member:scikit.learn-pr_post:nonmember:scikit.learn",
  "pr_reply:member:scikit.learn-pr_reply:nonmember:scikit.learn",
  "issue_post:member:scikit.learn-issue_reply:member:scikit.learn",
  "issue_post:nonmember:scikit.learn-issue_reply:nonmember:scikit.learn",
  "pr_post:member:scikit.learn-pr_reply:member:scikit.learn",
  "pr_post:nonmember:scikit.learn-pr_reply:nonmember:scikit.learn",
  "issue_post:member:scikit.learn-pr_post:member:scikit.learn",
  "issue_post:nonmember:scikit.learn-pr_post:nonmember:scikit.learn",    
  "issue_reply:member:scikit.learn-pr_reply:member:scikit.learn",  
  "issue_reply:nonmember:scikit.learn-pr_reply:nonmember:scikit.learn",
  
  # scikit-image
  "issue_post:member:scikit.image-issue_post:nonmember:scikit.image",   
  "issue_reply:member:scikit.image-issue_reply:nonmember:scikit.image",
  "pr_post:member:scikit.image-pr_post:nonmember:scikit.image",
  "pr_reply:member:scikit.image-pr_reply:nonmember:scikit.image",
  "issue_post:member:scikit.image-issue_reply:member:scikit.image",
  "issue_post:nonmember:scikit.image-issue_reply:nonmember:scikit.image",
  "pr_post:member:scikit.image-pr_reply:member:scikit.image",
  "pr_post:nonmember:scikit.image-pr_reply:nonmember:scikit.image",
  "issue_post:member:scikit.image-pr_post:member:scikit.image",
  "issue_post:nonmember:scikit.image-pr_post:nonmember:scikit.image",    
  "issue_reply:member:scikit.image-pr_reply:member:scikit.image",  
  "issue_reply:nonmember:scikit.image-pr_reply:nonmember:scikit.image",
  
  # matplotlib
  "issue_post:member:matplotlib-issue_post:nonmember:matplotlib",   
  "issue_reply:member:matplotlib-issue_reply:nonmember:matplotlib",
  "pr_post:member:matplotlib-pr_post:nonmember:matplotlib",
  "pr_reply:member:matplotlib-pr_reply:nonmember:matplotlib",
  "issue_post:member:matplotlib-issue_reply:member:matplotlib",
  "issue_post:nonmember:matplotlib-issue_reply:nonmember:matplotlib",
  "pr_post:member:matplotlib-pr_reply:member:matplotlib",
  "pr_post:nonmember:matplotlib-pr_reply:nonmember:matplotlib",
  "issue_post:member:matplotlib-pr_post:member:matplotlib",
  "issue_post:nonmember:matplotlib-pr_post:nonmember:matplotlib",    
  "issue_reply:member:matplotlib-pr_reply:member:matplotlib",  
  "issue_reply:nonmember:matplotlib-pr_reply:nonmember:matplotlib",
  
  # mayavi
  "issue_post:member:mayavi-issue_post:nonmember:mayavi",   
  "issue_reply:member:mayavi-issue_reply:nonmember:mayavi",
  "pr_post:member:mayavi-pr_post:nonmember:mayavi",
  "pr_reply:member:mayavi-pr_reply:nonmember:mayavi",
  "issue_post:member:mayavi-issue_reply:member:mayavi",
  "issue_post:nonmember:mayavi-issue_reply:nonmember:mayavi",
  "pr_post:member:mayavi-pr_reply:member:mayavi",
  "pr_post:nonmember:mayavi-pr_reply:nonmember:mayavi",
  "issue_post:member:mayavi-pr_post:member:mayavi",
  "issue_post:nonmember:mayavi-pr_post:nonmember:mayavi",    
  "issue_reply:member:mayavi-pr_reply:member:mayavi",  
  "issue_reply:nonmember:mayavi-pr_reply:nonmember:mayavi",
  
  # pandas
  "issue_post:member:pandas-issue_post:nonmember:pandas",   
  "issue_reply:member:pandas-issue_reply:nonmember:pandas",
  "pr_post:member:pandas-pr_post:nonmember:pandas",
  "pr_reply:member:pandas-pr_reply:nonmember:pandas",
  "issue_post:member:pandas-issue_reply:member:pandas",
  "issue_post:nonmember:pandas-issue_reply:nonmember:pandas",
  "pr_post:member:pandas-pr_reply:member:pandas",
  "pr_post:nonmember:pandas-pr_reply:nonmember:pandas",
  "issue_post:member:pandas-pr_post:member:pandas",
  "issue_post:nonmember:pandas-pr_post:nonmember:pandas",    
  "issue_reply:member:pandas-pr_reply:member:pandas",  
  "issue_reply:nonmember:pandas-pr_reply:nonmember:pandas",
  
  # scipy
  "issue_post:member:scipy-issue_post:nonmember:scipy",   
  "issue_reply:member:scipy-issue_reply:nonmember:scipy",
  "pr_post:member:scipy-pr_post:nonmember:scipy",
  "pr_reply:member:scipy-pr_reply:nonmember:scipy",
  "issue_post:member:scipy-issue_reply:member:scipy",
  "issue_post:nonmember:scipy-issue_reply:nonmember:scipy",
  "pr_post:member:scipy-pr_reply:member:scipy",
  "pr_post:nonmember:scipy-pr_reply:nonmember:scipy",
  "issue_post:member:scipy-pr_post:member:scipy",
  "issue_post:nonmember:scipy-pr_post:nonmember:scipy",    
  "issue_reply:member:scipy-pr_reply:member:scipy",  
  "issue_reply:nonmember:scipy-pr_reply:nonmember:scipy",
  
  # numpy
  "issue_post:member:numpy-issue_post:nonmember:numpy",   
  "issue_reply:member:numpy-issue_reply:nonmember:numpy",
  "pr_post:member:numpy-pr_post:nonmember:numpy",
  "pr_reply:member:numpy-pr_reply:nonmember:numpy",
  "issue_post:member:numpy-issue_reply:member:numpy",
  "issue_post:nonmember:numpy-issue_reply:nonmember:numpy",
  "pr_post:member:numpy-pr_reply:member:numpy",
  "pr_post:nonmember:numpy-pr_reply:nonmember:numpy",
  "issue_post:member:numpy-pr_post:member:numpy",
  "issue_post:nonmember:numpy-pr_post:nonmember:numpy",    
  "issue_reply:member:numpy-pr_reply:member:numpy",  
  "issue_reply:nonmember:numpy-pr_reply:nonmember:numpy",
  
  # sphinx-gallery
  "issue_post:member:sphinx.gallery-issue_post:nonmember:sphinx.gallery",   
  "issue_reply:member:sphinx.gallery-issue_reply:nonmember:sphinx.gallery",
  "pr_post:member:sphinx.gallery-pr_post:nonmember:sphinx.gallery",
  "pr_reply:member:sphinx.gallery-pr_reply:nonmember:sphinx.gallery",
  "issue_post:member:sphinx.gallery-issue_reply:member:sphinx.gallery",
  "issue_post:nonmember:sphinx.gallery-issue_reply:nonmember:sphinx.gallery",
  "pr_post:member:sphinx.gallery-pr_reply:member:sphinx.gallery",
  "pr_post:nonmember:sphinx.gallery-pr_reply:nonmember:sphinx.gallery",
  "issue_post:member:sphinx.gallery-pr_post:member:sphinx.gallery",
  "issue_post:nonmember:sphinx.gallery-pr_post:nonmember:sphinx.gallery",    
  "issue_reply:member:sphinx.gallery-pr_reply:member:sphinx.gallery",  
  "issue_reply:nonmember:sphinx.gallery-pr_reply:nonmember:sphinx.gallery"
)


time_contrasts = c(
  unlist(
    lapply(gsub("-", ":coef1-", partial_time_contrasts),
           function(x) paste(x, ":coef1", sep=""))),
  unlist(
    lapply(gsub("-", ":coef2-", partial_time_contrasts),
           function(x) paste(x, ":coef2", sep=""))),
  unlist(
    lapply(gsub("-", ":coef3-", partial_time_contrasts),
           function(x) paste(x, ":coef3", sep=""))),
  unlist(
    lapply(gsub("-", ":coef4-", partial_time_contrasts),
           function(x) paste(x, ":coef4", sep=""))),
  unlist(
    lapply(gsub("-", ":coef5-", partial_time_contrasts),
           function(x) paste(x, ":coef5", sep=""))),
  unlist(
    lapply(gsub("-", ":coef6-", partial_time_contrasts),
           function(x) paste(x, ":coef6", sep=""))),
  unlist(
    lapply(gsub("-", ":coef7-", partial_time_contrasts),
           function(x) paste(x, ":coef7", sep=""))),
  unlist(
    lapply(gsub("-", ":coef8-", partial_time_contrasts),
           function(x) paste(x, ":coef8", sep="")))
)

# compute statistics over specified contrast areas
project_type_author_group_time_tests = compute_t_statistics(
  means, se, time_contrasts)
project_type_author_group_time_tests[, "p_value"] = compute_p_value_from_t_stats(
  project_type_author_group_time_tests$t_stats)
# Filter out all NAs, which correspond to contrasts that don't exist
project_type_author_group_time_tests = project_type_author_group_time_tests[
  !is.na(project_type_author_group_time_tests$p_value), ]
```

Because we have so many tests, we'll only display the ones that are significant
(after adjusting for multiple comparisons).


|                                      &nbsp;                                      | t_stats | p_value | p_adj  | sig |
|:--------------------------------------------------------------------------------:|:-------:|:-------:|:------:|:---:|
|     **issue_reply:member:matplotlib:coef1-pr_reply:member:matplotlib:coef1**     |  3.091  |  0.002  | 0.045  |  *  |
|         **issue_reply:member:pandas:coef1-pr_reply:member:pandas:coef1**         |  3.48   |    0    | 0.018  |  *  |
|     **pr_post:member:scikit.learn:coef2-pr_reply:member:scikit.learn:coef2**     | -3.231  |  0.001  | 0.033  |  *  |
|     **issue_reply:member:matplotlib:coef2-pr_reply:member:matplotlib:coef2**     |  3.814  | 0.0001  | 0.007  | **  |
|     **issue_reply:member:matplotlib:coef3-pr_reply:member:matplotlib:coef3**     |  4.425  | 0.0001  | 0.001  | **  |
|       **pr_post:member:matplotlib:coef4-pr_reply:member:matplotlib:coef4**       |  3.109  |  0.002  | 0.044  |  *  |
|     **issue_reply:member:matplotlib:coef4-pr_reply:member:matplotlib:coef4**     |  3.188  |  0.001  | 0.036  |  *  |
|        **issue_post:member:pandas:coef4-issue_reply:member:pandas:coef4**        |  3.411  |  0.001  |  0.02  |  *  |
|         **issue_reply:member:pandas:coef4-pr_reply:member:pandas:coef4**         |  3.946  | 0.0001  | 0.004  | **  |
|    **issue_post:member:scikit.learn:coef5-pr_post:member:scikit.learn:coef5**    |  4.149  | 0.0001  | 0.002  | **  |
|     **pr_post:member:scikit.image:coef5-pr_reply:member:scikit.image:coef5**     |  4.523  | 0.0001  | 0.001  | **  |
|  **issue_reply:member:matplotlib:coef5-issue_reply:nonmember:matplotlib:coef5**  |  3.721  | 0.0002  | 0.009  | **  |
|     **issue_reply:member:matplotlib:coef5-pr_reply:member:matplotlib:coef5**     |  3.257  |  0.001  | 0.033  |  *  |
|         **issue_reply:member:pandas:coef5-pr_reply:member:pandas:coef5**         |  3.47   |    0    | 0.018  |  *  |
|    **issue_post:member:matplotlib:coef6-issue_reply:member:matplotlib:coef6**    | -4.718  | 0.0001  | 0.0004 | *** |
|      **issue_post:member:matplotlib:coef6-pr_post:member:matplotlib:coef6**      | -4.126  | 0.0001  | 0.002  | **  |
|     **issue_reply:member:matplotlib:coef6-pr_reply:member:matplotlib:coef6**     |  3.691  | 0.0002  | 0.009  | **  |
|        **issue_post:member:pandas:coef6-issue_reply:member:pandas:coef6**        |  4.604  | 0.0001  | 0.001  | **  |
|     **pr_post:member:scikit.learn:coef7-pr_reply:member:scikit.learn:coef7**     | -3.238  |  0.001  | 0.033  |  *  |
|   **issue_reply:member:scikit.image:coef7-pr_reply:member:scikit.image:coef7**   |  3.216  |  0.001  | 0.034  |  *  |
|     **issue_reply:member:matplotlib:coef7-pr_reply:member:matplotlib:coef7**     |  4.399  | 0.0001  | 0.001  | **  |
|         **issue_reply:member:pandas:coef7-pr_reply:member:pandas:coef7**         |   3.5   |    0    | 0.017  |  *  |
| **issue_post:nonmember:scikit.learn:coef8-pr_post:nonmember:scikit.learn:coef8** |  3.613  | 0.0003  | 0.012  |  *  |
|   **issue_reply:member:scikit.learn:coef8-pr_reply:member:scikit.learn:coef8**   |  3.417  |  0.001  |  0.02  |  *  |
|          **pr_post:member:pandas:coef8-pr_post:nonmember:pandas:coef8**          |  3.699  | 0.0002  | 0.009  | **  |
|         **pr_reply:member:pandas:coef8-pr_reply:nonmember:pandas:coef8**         |  3.941  | 0.0001  | 0.004  | **  |
|        **issue_post:member:pandas:coef8-issue_reply:member:pandas:coef8**        | -3.141  |  0.002  |  0.04  |  *  |
|       **issue_post:nonmember:pandas:coef8-pr_post:nonmember:pandas:coef8**       |  5.051  | 0.0001  | 0.0001 | *** |
|         **issue_reply:member:pandas:coef8-pr_reply:member:pandas:coef8**         |  5.57   | 0.0001  | 0.0001 | *** |
|      **issue_reply:nonmember:pandas:coef8-pr_reply:nonmember:pandas:coef8**      |  4.752  | 0.0001  | 0.0004 | *** |



![**Figure**. Sentiment over time by contribution type (ticket vs. comment) and community membership at the time of posting (member vs. nonmember).](../../figures/sentiment_analysis/ossc-sentiment_membership_contribution_time-aggregated-knitr.jpg)


![**Figure**. Sentiment over time by contribution type (ticket vs. comment) and community membership  at the time of posting (member vs. nonmember) by project.](../../figures/sentiment_analysis/ossc-sentiment_membership_contribution_time-by_project-knitr.jpg)

### Model 1.3: Do tickets and comments materially differ in gratitude?

First, let's take a look at a summary table of expressions of gratitude by
membership status and contribution type.


```r
# create a summary table of gratitude by type and author association
gratitude_summary_stats = sentiment_frame %>% ungroup() %>%
  group_by(author_group, type, grateful_count) %>%
  summarise(n = n())
pander(gratitude_summary_stats, style = 'rmarkdown')
```



| author_group |    type     | grateful_count |   n    |
|:------------:|:-----------:|:--------------:|:------:|
|    member    | issue_post  |       0        | 14184  |
|    member    | issue_post  |       1        |  255   |
|    member    | issue_post  |       2        |   15   |
|    member    | issue_post  |       3        |   3    |
|    member    | issue_reply |       0        | 131533 |
|    member    | issue_reply |       1        |  8295  |
|    member    | issue_reply |       2        |  251   |
|    member    | issue_reply |       3        |   16   |
|    member    |   pr_post   |       0        | 24642  |
|    member    |   pr_post   |       1        |  335   |
|    member    |   pr_post   |       2        |   13   |
|    member    |  pr_reply   |       0        | 183118 |
|    member    |  pr_reply   |       1        | 29372  |
|    member    |  pr_reply   |       2        |  669   |
|    member    |  pr_reply   |       3        |   38   |
|    member    |  pr_reply   |       4        |   2    |
|  nonmember   | issue_post  |       0        | 15963  |
|  nonmember   | issue_post  |       1        |  1607  |
|  nonmember   | issue_post  |       2        |  103   |
|  nonmember   | issue_post  |       3        |   3    |
|  nonmember   | issue_reply |       0        | 37061  |
|  nonmember   | issue_reply |       1        |  7695  |
|  nonmember   | issue_reply |       2        |  637   |
|  nonmember   | issue_reply |       3        |   39   |
|  nonmember   | issue_reply |       4        |   2    |
|  nonmember   |   pr_post   |       0        | 11205  |
|  nonmember   |   pr_post   |       1        |  322   |
|  nonmember   |   pr_post   |       2        |   19   |
|  nonmember   |   pr_post   |       3        |   2    |
|  nonmember   |  pr_reply   |       0        | 32626  |
|  nonmember   |  pr_reply   |       1        |  7298  |
|  nonmember   |  pr_reply   |       2        |  338   |
|  nonmember   |  pr_reply   |       3        |   34   |

Now that we have a better idea of how the underlying data look, let's go ahead
and build our model.


```r
# do users tend to express appreciation and gratitude differently by group and content?
creators_v_commenters_gratitude_by_project = lmer(log(grateful_count + 1) ~ project * author_group * type +
                                                    (1 | author_name),
                                                  data=sentiment_frame)

# print results
pander_lme(creators_v_commenters_gratitude_by_project)
```



|                             &nbsp;                              | Estimate  | Std..Error |   df   | t.value |   p    | p_adj  | sig |
|:---------------------------------------------------------------:|:---------:|:----------:|:------:|:-------:|:------:|:------:|:---:|
|                         **(Intercept)**                         |  0.08939  |  0.005854  | 475280 |  15.27  | 0.0001 | 0.0001 | *** |
|                        **projectmayavi**                        | -0.00541  |  0.02909   | 485881 | -0.186  |  0.85  |  0.89  |     |
|                        **projectnumpy**                         | -0.01738  |  0.007603  | 497011 | -2.285  | 0.022  | 0.048  |  *  |
|                        **projectpandas**                        | -0.03162  |  0.006502  | 505910 | -4.863  | 0.0001 | 0.0001 | *** |
|                     **projectscikit-image**                     | -0.05825  |  0.01119   | 496520 | -5.203  | 0.0001 | 0.0001 | *** |
|                     **projectscikit-learn**                     | -0.03577  |  0.007506  | 503031 | -4.766  | 0.0001 | 0.0001 | *** |
|                        **projectscipy**                         | -0.01448  |  0.009381  | 494975 | -1.544  | 0.123  | 0.207  |     |
|                    **projectsphinx-gallery**                    | -0.01805  |  0.02272   | 490235 | -0.7944 |  0.43  |  0.58  |     |
|                    **author_groupnonmember**                    | -0.02049  |  0.00703   | 491106 | -2.915  | 0.004  | 0.009  | **  |
|                       **typeissue_reply**                       |  0.02565  |  0.005444  | 490881 |  4.711  | 0.0001 | 0.0001 | *** |
|                         **typepr_post**                         | 0.002612  |  0.005991  | 491145 | 0.4359  |  0.66  |  0.79  |     |
|                        **typepr_reply**                         |  0.05334  |  0.005385  | 491204 |  9.906  | 0.0001 | 0.0001 | *** |
|             **projectmayavi:author_groupnonmember**             |  0.08542  |  0.03133   | 481224 |  2.726  | 0.006  | 0.016  |  *  |
|             **projectnumpy:author_groupnonmember**              | 0.009888  |  0.009761  | 490459 |  1.013  |  0.31  |  0.45  |     |
|             **projectpandas:author_groupnonmember**             |  0.01496  |  0.008171  | 485244 |  1.83   | 0.067  | 0.123  |     |
|          **projectscikit-image:author_groupnonmember**          |  0.07383  |  0.01498   | 478671 |  4.928  | 0.0001 | 0.0001 | *** |
|          **projectscikit-learn:author_groupnonmember**          |  0.05506  |  0.009497  | 484148 |  5.798  | 0.0001 | 0.0001 | *** |
|             **projectscipy:author_groupnonmember**              |  0.02364  |  0.01143   | 497459 |  2.068  | 0.039  | 0.077  |  .  |
|         **projectsphinx-gallery:author_groupnonmember**         |  0.0572   |  0.03192   | 503101 |  1.792  | 0.073  |  0.13  |     |
|                **projectmayavi:typeissue_reply**                | 0.001107  |  0.02601   | 490156 | 0.04255 |  0.97  |  0.97  |     |
|                **projectnumpy:typeissue_reply**                 | -0.00765  |  0.007452  | 490088 | -1.026  |  0.3   |  0.45  |     |
|                **projectpandas:typeissue_reply**                |  0.01468  |  0.006121  | 490762 |  2.399  | 0.016  | 0.036  |  *  |
|             **projectscikit-image:typeissue_reply**             |  0.0345   |  0.01097   | 489209 |  3.146  | 0.002  | 0.004  | **  |
|             **projectscikit-learn:typeissue_reply**             |  0.0184   |  0.007169  | 490127 |  2.567  |  0.01  | 0.024  |  *  |
|                **projectscipy:typeissue_reply**                 | 0.001001  |  0.009351  | 489679 | 0.1071  |  0.92  |  0.93  |     |
|            **projectsphinx-gallery:typeissue_reply**            | -0.006232 |  0.02373   | 488985 | -0.2626 |  0.79  |  0.86  |     |
|                  **projectmayavi:typepr_post**                  | -0.03733  |  0.02868   | 489228 | -1.302  | 0.193  |  0.3   |     |
|                  **projectnumpy:typepr_post**                   | -0.01123  |  0.008484  | 490199 | -1.324  | 0.186  |  0.3   |     |
|                  **projectpandas:typepr_post**                  | 0.002889  |  0.007027  | 491063 | 0.4112  |  0.68  |  0.79  |     |
|               **projectscikit-image:typepr_post**               |  0.01147  |  0.01222   | 489351 | 0.9386  |  0.35  |  0.5   |     |
|               **projectscikit-learn:typepr_post**               | -0.004068 |  0.00831   | 490280 | -0.4895 |  0.62  |  0.77  |     |
|                  **projectscipy:typepr_post**                   | -0.006662 |  0.01029   | 489817 | -0.6473 |  0.52  |  0.68  |     |
|              **projectsphinx-gallery:typepr_post**              | -0.004425 |  0.02815   | 489005 | -0.1572 |  0.88  |  0.9   |     |
|                 **projectmayavi:typepr_reply**                  |  0.1147   |  0.02649   | 489611 |  4.33   | 0.0001 | 0.0001 | *** |
|                  **projectnumpy:typepr_reply**                  |  0.02764  |  0.007444  | 490377 |  3.713  | 0.0002 | 0.001  | **  |
|                 **projectpandas:typepr_reply**                  |  0.04779  |  0.00608   | 491191 |  7.861  | 0.0001 | 0.0001 | *** |
|              **projectscikit-image:typepr_reply**               |  0.06862  |  0.01072   | 489358 |  6.401  | 0.0001 | 0.0001 | *** |
|              **projectscikit-learn:typepr_reply**               |  0.03854  |  0.007073  | 490435 |  5.449  | 0.0001 | 0.0001 | *** |
|                  **projectscipy:typepr_reply**                  |  0.04695  |  0.009234  | 489869 |  5.084  | 0.0001 | 0.0001 | *** |
|             **projectsphinx-gallery:typepr_reply**              |  0.01067  |  0.02314   | 489110 |  0.461  |  0.64  |  0.78  |     |
|            **author_groupnonmember:typeissue_reply**            |  0.05941  |  0.007262  | 506722 |  8.181  | 0.0001 | 0.0001 | *** |
|              **author_groupnonmember:typepr_post**              | -0.02019  |  0.00909   | 488096 | -2.221  | 0.026  | 0.054  |  .  |
|             **author_groupnonmember:typepr_reply**              |  0.0379   |  0.007805  | 469726 |  4.856  | 0.0001 | 0.0001 | *** |
|     **projectmayavi:author_groupnonmember:typeissue_reply**     | -0.05677  |  0.03002   | 507310 | -1.891  | 0.059  | 0.114  |     |
|     **projectnumpy:author_groupnonmember:typeissue_reply**      |  0.01268  |  0.01031   | 505156 |  1.231  | 0.218  |  0.33  |     |
|     **projectpandas:author_groupnonmember:typeissue_reply**     | -0.00213  |  0.008504  | 505016 | -0.2504 |  0.8   |  0.86  |     |
|  **projectscikit-image:author_groupnonmember:typeissue_reply**  | -0.06068  |  0.01582   | 504794 | -3.836  | 0.0001 | 0.0004 | *** |
|  **projectscikit-learn:author_groupnonmember:typeissue_reply**  | -0.05756  |  0.009833  | 503820 | -5.854  | 0.0001 | 0.0001 | *** |
|     **projectscipy:author_groupnonmember:typeissue_reply**      | -0.008078 |  0.01207   | 507034 | -0.6691 |  0.5   |  0.67  |     |
| **projectsphinx-gallery:author_groupnonmember:typeissue_reply** | -0.01751  |  0.03532   | 500843 | -0.4958 |  0.62  |  0.77  |     |
|       **projectmayavi:author_groupnonmember:typepr_post**       | -0.01222  |  0.03992   | 502137 | -0.3061 |  0.76  |  0.85  |     |
|       **projectnumpy:author_groupnonmember:typepr_post**        |  0.01054  |  0.01307   | 491557 | 0.8063  |  0.42  |  0.58  |     |
|       **projectpandas:author_groupnonmember:typepr_post**       | 0.005876  |  0.01101   | 484100 | 0.5336  |  0.59  |  0.76  |     |
|    **projectscikit-image:author_groupnonmember:typepr_post**    | -0.02653  |  0.01881   | 492333 | -1.411  | 0.158  |  0.26  |     |
|    **projectscikit-learn:author_groupnonmember:typepr_post**    | -0.02014  |  0.01227   | 489436 | -1.642  |  0.1   | 0.174  |     |
|       **projectscipy:author_groupnonmember:typepr_post**        | 0.004067  |  0.01455   | 498159 | 0.2796  |  0.78  |  0.86  |     |
|   **projectsphinx-gallery:author_groupnonmember:typepr_post**   | -0.01693  |  0.04677   | 504994 | -0.362  |  0.72  |  0.82  |     |
|      **projectmayavi:author_groupnonmember:typepr_reply**       |  -0.115   |  0.03498   | 499600 | -3.286  | 0.001  | 0.003  | **  |
|       **projectnumpy:author_groupnonmember:typepr_reply**       | -0.02069  |  0.01104   | 478200 | -1.875  | 0.061  | 0.114  |     |
|      **projectpandas:author_groupnonmember:typepr_reply**       | -0.02918  |  0.009248  | 461702 | -3.155  | 0.002  | 0.004  | **  |
|   **projectscikit-image:author_groupnonmember:typepr_reply**    | -0.08685  |  0.01589   | 474921 | -5.465  | 0.0001 | 0.0001 | *** |
|   **projectscikit-learn:author_groupnonmember:typepr_reply**    | -0.06118  |   0.0103   | 469477 |  -5.94  | 0.0001 | 0.0001 | *** |
|       **projectscipy:author_groupnonmember:typepr_reply**       | -0.04245  |  0.01248   | 489470 | -3.401  | 0.001  | 0.002  | **  |
|  **projectsphinx-gallery:author_groupnonmember:typepr_reply**   | -0.08952  |   0.0354   | 503994 | -2.529  | 0.011  | 0.026  |  *  |



![**Figure**. Expressions of gratitude by contribution type (ticket vs. comment) and community membership (member vs. nonmember) at the time of posting.](../../figures/sentiment_analysis/ossc-grateful_membership_contribution-knitr.jpg)

### Testing Model 1.3 using Model 1.1 methods

#### Model 1.3a: Overall effects with linear mixed-effects models

This model presents the analyses in a way that is typical of psychological
analyses. We predict the changes in emotion by community membership and 
contribution type, including random effects for project and for author. This
allows us to explore the general patterns of the main and interaction terms,
rather than focusing in on the project-specific variability.


```r
# do users tend to express appreciation and gratitude differently by group and content?
retrying_model_1.3 = lmer(log(grateful_count + 1) ~ author_group * type +
                            (1 | project),
                          data=sentiment_frame)
```


|                  &nbsp;                   | Estimate  | Std..Error |   df   | t.value |   p    | p_adj  | sig |
|:-----------------------------------------:|:---------:|:----------:|:------:|:-------:|:------:|:------:|:---:|
|              **(Intercept)**              |  0.01942  |  0.008113  | 7.526  |  2.394  | 0.046  | 0.052  |  .  |
|         **author_groupnonmember**         |  0.05539  |   0.0025   | 507686 |  22.16  | 0.0001 | 0.0001 | *** |
|            **typeissue_reply**            |  0.02959  |  0.001947  | 507681 |  15.2   | 0.0001 | 0.0001 | *** |
|              **typepr_post**              | -0.003142 |  0.002332  | 507683 | -1.348  | 0.178  | 0.178  |     |
|             **typepr_reply**              |  0.08472  |  0.00192   | 507686 |  44.12  | 0.0001 | 0.0001 | *** |
| **author_groupnonmember:typeissue_reply** |  0.03474  |  0.002772  | 507680 |  12.53  | 0.0001 | 0.0001 | *** |
|   **author_groupnonmember:typepr_post**   | -0.04586  |  0.003541  | 507687 | -12.95  | 0.0001 | 0.0001 | *** |
|  **author_groupnonmember:typepr_reply**   | -0.01989  |  0.002779  | 507687 | -7.157  | 0.0001 | 0.0001 | *** |

While we see significant differences in the model, interpreting the results is
difficult because of the way that `lmer` handles factor comparisons. All 
factors are compared against a "reference level," the first level in the model.
This makes intepreting models with factors that include more than two levels
incredibly difficult, because the intercept is essentially an interaction term
among all reference levels of all factors.

As a result, we turn to the biostatistics approach of multiple *t*-tests 
(corrected for comparisons) of the model estimates to better understand the 
effects.

#### Model 1.3b: In-depth investigation through *t*-tests of model estimates

First, we build a series of linear mixed-effects models with one term included
in each model (either main term or interaction term). We then use the estimates
from those models to perform *t*-tests to investigate how different levels of
the effects differ from one another (and not just from the model-level
intercept).

Projects here are random effects, but the rest of the model is the same as
before. This allows us to do pairwise testing of main and interaction terms,
along with better exploring inter-project variability.

##### Model 1.3b.1: Does sentiment vary significantly by community membership?

First, look at whether there are differences in sentiment between author
groups.


```r
# do members and nonmembers materially differ in emotion?
fixed_authors_gratitude = lmer(
  log(grateful_count + 1) ~ 0 + author_group + (1 | project),
  data=sentiment_frame,
  REML=FALSE)
```

Run *t*-tests among levels and prepare for the Model 1.1b table later.


```r
# convert Model 1.1b1 output to dataframe
coefficients_and_se = data.frame(
  summary(fixed_authors_gratitude)$coefficients)

# get comparison names as rownames
row_names = gsub("author_group", "",
                 gsub("type", "", row.names(coefficients_and_se)))

# convert model estimates to a dataframe
means = coefficients_and_se$Estimate
names(means) = row_names

# convert standard error to dataframe
se = coefficients_and_se$Std..Error
names(se) = row_names

# compute t-statistics and p-values for desired contrasts
contrasts = c("member-nonmember")
author_groups_tests = compute_t_statistics(
  means, se,
  contrasts)
author_groups_tests[, "p_value"] = compute_p_value_from_t_stats(
  author_groups_tests$t_stats)
```

##### Model 1.3b.2: Does sentiment vary significantly across contribution types?

Now, look at whether there are differences in sentiment between contribution
types.


```r
# do tickets and comments materially differ in emotion?
fixed_types_gratitude = lmer(
  log(grateful_count + 1) ~ 0 + type + (1 | project),
  data=sentiment_frame,
  REML=FALSE)
```

Run *t*-tests among levels and prepare for the Model 1.1b table later.


```r
# convert Model 1.1b2 output to dataframe
coefficients_and_se = data.frame(
  summary(fixed_types_gratitude)$coefficients)

# get comparison names as rownames
row_names = gsub("author_group", "",
                 gsub("type", "", row.names(coefficients_and_se)))

# convert model estimates to a dataframe
means = coefficients_and_se$Estimate
names(means) = row_names

# convert standard error to dataframe
se = coefficients_and_se$Std..Error
names(se) = row_names

# compute t-statistics and p-values for desired contrasts
contrasts = c("issue_post-issue_reply", # issues: posts vs. replies
              "pr_post-pr_reply",       # PRs: posts vs. replies
              "issue_post-pr_post",     # posts: issues vs. PRs
              "issue_reply-pr_reply")   # replies: issues vs. PRs
types_tests = compute_t_statistics(
  means, se,
  contrasts)
types_tests[, "p_value"] = compute_p_value_from_t_stats(types_tests$t_stats)
```

##### Model 1.3b.3: Does sentiment vary significantly across community memberships and contribution types?

Finally, let's look at the interaction between membership and contribution.


```r
# does emotion differ by the interaction between contribution and authorship group?
community_contribution_gratitude = lmer(
  log(grateful_count + 1) ~ 0 + type:author_group + (1 | project),
  data=sentiment_frame,
  REML=FALSE)
```

Run *t*-tests among levels and prepare for the Model 1.1b table later.


```r
# convert Model 1.1b3 output to dataframe
coefficients_and_se = data.frame(
  summary(community_contribution_gratitude)$coefficients)

# get comparison names as rownames
row_names = gsub("author_group", "", gsub("type", "", row.names(coefficients_and_se)))

# convert model estimates to a dataframe
means = coefficients_and_se$Estimate
names(means) = row_names

# convert standard error to dataframe
se = coefficients_and_se$Std..Error
names(se) = row_names

# compute t-statistics and p-values for desired contrasts
contrasts = c(
  "issue_post:member-issue_post:nonmember",     # contribution static (issue posts); membership varies (members v. nonmembers)
  "issue_reply:member-issue_reply:nonmember",   # contribution static (issue replies); membership varies (members v. nonmembers)
  "pr_post:member-pr_post:nonmember",           # contribution static (PR posts); membership varies (members v. nonmembers)
  "pr_reply:member-pr_reply:nonmember",         # contribution static (PR replies); membership varies (members v. nonmembers)
  "issue_post:member-issue_reply:member",       # contribution varies (issue posts vs. issue replies); membership static (members)
  "issue_post:nonmember-issue_reply:nonmember", # contribution varies (issue posts vs. issue replies); membership static (nonmembers)
  "pr_post:member-pr_reply:member",             # contribution varies (PR posts vs. PR replies); membership static (members)
  "pr_post:nonmember-pr_reply:nonmember",       # contribution varies (PR posts vs. PR replies); membership static (nonmembers)
  "issue_post:member-pr_post:member",           # contribution varies (issue posts vs. PR posts); membership static (members)
  "issue_post:nonmember-pr_post:nonmember",     # contribution varies (issue posts vs. PR posts); membership static (nonmembers)
  "issue_reply:member-pr_reply:member",         # contribution varies (issue replies vs. PR replies); membership static (members)
  "issue_reply:nonmember-pr_reply:nonmember")   # contribution varies (issue replies vs. PR replies); membership static (nonmembers)
types_author_groups_tests = compute_t_statistics(
  means, se,
  contrasts)
types_author_groups_tests[, "p_value"] = compute_p_value_from_t_stats(
  types_author_groups_tests$"t_stats")
```

##### Model 1.3b.4 : Do different kinds of user contributions differ in emotion by projects?

Now adding projects into the mix to understand how the previous analysis
varies across projects.


```r
# do tickets and comments materially differ in gratitude by projects?
creators_v_commenters_gratitude_by_project = lm(
  log(grateful_count + 1) ~ 0 + project:type:author_group,
  data = sentiment_frame)
```

Run *t*-tests among levels and prepare for the Model 1.1b table later.


```r
# convert Model 1.1c output to dataframe
coefficients_and_se = data.frame(
  summary(creators_v_commenters_gratitude_by_project)$coefficients)

# get comparison names as rownames
row_names = gsub(
  "project", "", gsub(
    "author_group", "", gsub(
      "type", "", row.names(coefficients_and_se))))

# replace hyphens in project names with periods
row_names = gsub(
  "scikit-", "scikit.", gsub(
    "sphinx-", "sphinx.", row_names))

# convert model estimates to a dataframe
means = coefficients_and_se$Estimate
names(means) = row_names

# convert standard error to dataframe
se = coefficients_and_se$Std..Error
names(se) = row_names

# compute t-statistics and p-values for desired contrasts
# (note: ordering of contrasts within each project is identical to Model 1.3b.3)
contrasts = c(
  
  # scikit-learn
  "scikit.learn:issue_post:member-scikit.learn:issue_post:nonmember",
  "scikit.learn:issue_reply:member-scikit.learn:issue_reply:nonmember",
  "scikit.learn:pr_post:member-scikit.learn:pr_post:nonmember",
  "scikit.learn:pr_reply:member-scikit.learn:pr_reply:nonmember",
  "scikit.learn:issue_post:member-scikit.learn:issue_reply:member",
  "scikit.learn:issue_post:nonmember-scikit.learn:issue_reply:nonmember",
  "scikit.learn:pr_post:member-scikit.learn:pr_reply:member",
  "scikit.learn:pr_post:nonmember-scikit.learn:pr_reply:nonmember",
  "scikit.learn:issue_post:member-scikit.learn:pr_post:member",
  "scikit.learn:issue_post:nonmember-scikit.learn:pr_post:nonmember",
  "scikit.learn:issue_reply:member-scikit.learn:pr_reply:member",
  "scikit.learn:issue_reply:nonmember-scikit.learn:pr_reply:nonmember",
  
  # scikit-image
  "scikit.image:issue_post:member-scikit.image:issue_post:nonmember",
  "scikit.image:issue_reply:member-scikit.image:issue_reply:nonmember",
  "scikit.image:pr_post:member-scikit.image:pr_post:nonmember",
  "scikit.image:pr_reply:member-scikit.image:pr_reply:nonmember",
  "scikit.image:issue_post:member-scikit.image:issue_reply:member",
  "scikit.image:issue_post:nonmember-scikit.image:issue_reply:nonmember",
  "scikit.image:pr_post:member-scikit.image:pr_reply:member",
  "scikit.image:pr_post:nonmember-scikit.image:pr_reply:nonmember",
  "scikit.image:issue_post:member-scikit.image:pr_post:member",
  "scikit.image:issue_post:nonmember-scikit.image:pr_post:nonmember",
  "scikit.image:issue_reply:member-scikit.image:pr_reply:member",
  "scikit.image:issue_reply:nonmember-scikit.image:pr_reply:nonmember",
  
  # matplotlib
  "matplotlib:issue_post:member-matplotlib:issue_post:nonmember",
  "matplotlib:issue_reply:member-matplotlib:issue_reply:nonmember",
  "matplotlib:pr_post:member-matplotlib:pr_post:nonmember",
  "matplotlib:pr_reply:member-matplotlib:pr_reply:nonmember",
  "matplotlib:issue_post:member-matplotlib:issue_reply:member",
  "matplotlib:issue_post:nonmember-matplotlib:issue_reply:nonmember",
  "matplotlib:pr_post:member-matplotlib:pr_reply:member",
  "matplotlib:pr_post:nonmember-matplotlib:pr_reply:nonmember",
  "matplotlib:issue_post:member-matplotlib:pr_post:member",
  "matplotlib:issue_post:nonmember-matplotlib:pr_post:nonmember",
  "matplotlib:issue_reply:member-matplotlib:pr_reply:member",
  "matplotlib:issue_reply:nonmember-matplotlib:pr_reply:nonmember",
  
  # mayavi
  "mayavi:issue_post:member-mayavi:issue_post:nonmember",
  "mayavi:issue_reply:member-mayavi:issue_reply:nonmember",
  "mayavi:pr_post:member-mayavi:pr_post:nonmember",
  "mayavi:pr_reply:member-mayavi:pr_reply:nonmember",
  "mayavi:issue_post:member-mayavi:issue_reply:member",
  "mayavi:issue_post:nonmember-mayavi:issue_reply:nonmember",
  "mayavi:pr_post:member-mayavi:pr_reply:member",
  "mayavi:pr_post:nonmember-mayavi:pr_reply:nonmember",
  "mayavi:issue_post:member-mayavi:pr_post:member",
  "mayavi:issue_post:nonmember-mayavi:pr_post:nonmember",
  "mayavi:issue_reply:member-mayavi:pr_reply:member",
  "mayavi:issue_reply:nonmember-mayavi:pr_reply:nonmember",
  
  # pandas
  "pandas:issue_post:member-pandas:issue_post:nonmember",
  "pandas:issue_reply:member-pandas:issue_reply:nonmember",
  "pandas:pr_post:member-pandas:pr_post:nonmember",
  "pandas:pr_reply:member-pandas:pr_reply:nonmember",
  "pandas:issue_post:member-pandas:issue_reply:member",
  "pandas:issue_post:nonmember-pandas:issue_reply:nonmember",
  "pandas:pr_post:member-pandas:pr_reply:member",
  "pandas:pr_post:nonmember-pandas:pr_reply:nonmember",
  "pandas:issue_post:member-pandas:pr_post:member",
  "pandas:issue_post:nonmember-pandas:pr_post:nonmember",
  "pandas:issue_reply:member-pandas:pr_reply:member",
  "pandas:issue_reply:nonmember-pandas:pr_reply:nonmember",
  
  # scipy
  "scipy:issue_post:member-scipy:issue_post:nonmember",
  "scipy:issue_reply:member-scipy:issue_reply:nonmember",
  "scipy:pr_post:member-scipy:pr_post:nonmember",
  "scipy:pr_reply:member-scipy:pr_reply:nonmember",
  "scipy:issue_post:member-scipy:issue_reply:member",
  "scipy:issue_post:nonmember-scipy:issue_reply:nonmember",
  "scipy:pr_post:member-scipy:pr_reply:member",
  "scipy:pr_post:nonmember-scipy:pr_reply:nonmember",
  "scipy:issue_post:member-scipy:pr_post:member",
  "scipy:issue_post:nonmember-scipy:pr_post:nonmember",
  "scipy:issue_reply:member-scipy:pr_reply:member",
  "scipy:issue_reply:nonmember-scipy:pr_reply:nonmember",
  
  # numpy
  "numpy:issue_post:member-numpy:issue_post:nonmember",
  "numpy:issue_reply:member-numpy:issue_reply:nonmember",
  "numpy:pr_post:member-numpy:pr_post:nonmember",
  "numpy:pr_reply:member-numpy:pr_reply:nonmember",
  "numpy:issue_post:member-numpy:issue_reply:member",
  "numpy:issue_post:nonmember-numpy:issue_reply:nonmember",
  "numpy:pr_post:member-numpy:pr_reply:member",
  "numpy:pr_post:nonmember-numpy:pr_reply:nonmember",
  "numpy:issue_post:member-numpy:pr_post:member",
  "numpy:issue_post:nonmember-numpy:pr_post:nonmember",
  "numpy:issue_reply:member-numpy:pr_reply:member",
  "numpy:issue_reply:nonmember-numpy:pr_reply:nonmember",
  
  # sphinx-gallery
  "sphinx.gallery:issue_post:member-sphinx.gallery:issue_post:nonmember",
  "sphinx.gallery:issue_reply:member-sphinx.gallery:issue_reply:nonmember",
  "sphinx.gallery:pr_post:member-sphinx.gallery:pr_post:nonmember",
  "sphinx.gallery:pr_reply:member-sphinx.gallery:pr_reply:nonmember",
  "sphinx.gallery:issue_post:member-sphinx.gallery:issue_reply:member",
  "sphinx.gallery:issue_post:nonmember-sphinx.gallery:issue_reply:nonmember",
  "sphinx.gallery:pr_post:member-sphinx.gallery:pr_reply:member",
  "sphinx.gallery:pr_post:nonmember-sphinx.gallery:pr_reply:nonmember",
  "sphinx.gallery:issue_post:member-sphinx.gallery:pr_post:member",
  "sphinx.gallery:issue_post:nonmember-sphinx.gallery:pr_post:nonmember",
  "sphinx.gallery:issue_reply:member-sphinx.gallery:pr_reply:member",
  "sphinx.gallery:issue_reply:nonmember-sphinx.gallery:pr_reply:nonmember"
)
project_types_author_group_tests = compute_t_statistics(
  means, se,
  contrasts)
project_types_author_group_tests[, "p_value"] = compute_p_value_from_t_stats(
  project_types_author_group_tests$t_stats)
```

#### Model 1.3b: Overall results

Now we bring together all analyses from Model 1.3b.


```r
# specify main terms
author_groups_tests["contrast"] = row.names(author_groups_tests)
types_tests["contrast"] = row.names(types_tests)
all_tests = merge(author_groups_tests, types_tests, all=TRUE, sort=FALSE)
all_tests["model"] = "Main Terms"

# specify 2-way interactions
types_author_groups_tests["contrast"] = row.names(types_author_groups_tests)
types_author_groups_tests["model"] = "2W: Types x Author Groups"
all_tests = merge(all_tests, types_author_groups_tests, all=TRUE, sort=FALSE)

# specify 3-way interactions
project_types_author_group_tests["contrast"] = row.names(project_types_author_group_tests)
project_types_author_group_tests["model"] = "3W: Types x Author Groups x Project"
all_tests = merge(all_tests, project_types_author_group_tests, all=TRUE,
                  sort=FALSE)
```

Let's correct all tests at once for multiple comparisons.


```r
# specify all contrasts
row.names(all_tests) = all_tests$contrast
all_tests = subset(all_tests, select=-c(contrast))

# print the table (reordering columns for readibility)
all_tests = all_tests[c("model", "t_stats", "p_value")]
pander_clean_anova(all_tests, rename_columns=FALSE)
```



|                                    &nbsp;                                    |                model                | t_stats  | p_value | p_adj  | sig |
|:----------------------------------------------------------------------------:|:-----------------------------------:|:--------:|:-------:|:------:|:---:|
|                             **member-nonmember**                             |             Main Terms              |  -4.34   | 0.0001  | 0.0001 | *** |
|                          **issue_post-issue_reply**                          |             Main Terms              |  -1.621  |  0.105  | 0.132  |     |
|                             **pr_post-pr_reply**                             |             Main Terms              |  -6.921  | 0.0001  | 0.0001 | *** |
|                            **issue_post-pr_post**                            |             Main Terms              |  2.335   |  0.02   | 0.026  |  *  |
|                           **issue_reply-pr_reply**                           |             Main Terms              |  -2.964  |  0.003  | 0.004  | **  |
|                  **issue_post:member-issue_post:nonmember**                  |      2W: Types x Author Groups      |  -5.171  | 0.0001  | 0.0001 | *** |
|                 **issue_reply:member-issue_reply:nonmember**                 |      2W: Types x Author Groups      |  -8.597  | 0.0001  | 0.0001 | *** |
|                     **pr_post:member-pr_post:nonmember**                     |      2W: Types x Author Groups      | -0.8896  |  0.37   |  0.43  |     |
|                    **pr_reply:member-pr_reply:nonmember**                    |      2W: Types x Author Groups      |  -3.385  |  0.001  | 0.001  | **  |
|                   **issue_post:member-issue_reply:member**                   |      2W: Types x Author Groups      |  -2.791  |  0.005  | 0.008  | **  |
|                **issue_post:nonmember-issue_reply:nonmember**                |      2W: Types x Author Groups      |  -6.07   | 0.0001  | 0.0001 | *** |
|                      **pr_post:member-pr_reply:member**                      |      2W: Types x Author Groups      |  -8.35   | 0.0001  | 0.0001 | *** |
|                   **pr_post:nonmember-pr_reply:nonmember**                   |      2W: Types x Author Groups      |  -10.66  | 0.0001  | 0.0001 | *** |
|                     **issue_post:member-pr_post:member**                     |      2W: Types x Author Groups      |  0.2943  |  0.77   |  0.82  |     |
|                  **issue_post:nonmember-pr_post:nonmember**                  |      2W: Types x Author Groups      |  4.558   | 0.0001  | 0.0001 | *** |
|                    **issue_reply:member-pr_reply:member**                    |      2W: Types x Author Groups      |  -5.278  | 0.0001  | 0.0001 | *** |
|                 **issue_reply:nonmember-pr_reply:nonmember**                 |      2W: Types x Author Groups      | -0.04773 |  0.96   |  0.97  |     |
|     **scikit.learn:issue_post:member-scikit.learn:issue_post:nonmember**     | 3W: Types x Author Groups x Project |  -14.53  | 0.0001  | 0.0001 | *** |
|    **scikit.learn:issue_reply:member-scikit.learn:issue_reply:nonmember**    | 3W: Types x Author Groups x Project |  -28.26  | 0.0001  | 0.0001 | *** |
|        **scikit.learn:pr_post:member-scikit.learn:pr_post:nonmember**        | 3W: Types x Author Groups x Project |  -1.384  |  0.166  | 0.202  |     |
|       **scikit.learn:pr_reply:member-scikit.learn:pr_reply:nonmember**       | 3W: Types x Author Groups x Project |  -10.17  | 0.0001  | 0.0001 | *** |
|      **scikit.learn:issue_post:member-scikit.learn:issue_reply:member**      | 3W: Types x Author Groups x Project |  -9.094  | 0.0001  | 0.0001 | *** |
|   **scikit.learn:issue_post:nonmember-scikit.learn:issue_reply:nonmember**   | 3W: Types x Author Groups x Project |  -5.885  | 0.0001  | 0.0001 | *** |
|         **scikit.learn:pr_post:member-scikit.learn:pr_reply:member**         | 3W: Types x Author Groups x Project |  -22.48  | 0.0001  | 0.0001 | *** |
|      **scikit.learn:pr_post:nonmember-scikit.learn:pr_reply:nonmember**      | 3W: Types x Author Groups x Project |  -22.24  | 0.0001  | 0.0001 | *** |
|        **scikit.learn:issue_post:member-scikit.learn:pr_post:member**        | 3W: Types x Author Groups x Project |  -1.151  |  0.25   |  0.29  |     |
|     **scikit.learn:issue_post:nonmember-scikit.learn:pr_post:nonmember**     | 3W: Types x Author Groups x Project |  13.09   | 0.0001  | 0.0001 | *** |
|       **scikit.learn:issue_reply:member-scikit.learn:pr_reply:member**       | 3W: Types x Author Groups x Project |  -30.71  | 0.0001  | 0.0001 | *** |
|    **scikit.learn:issue_reply:nonmember-scikit.learn:pr_reply:nonmember**    | 3W: Types x Author Groups x Project | -0.06998 |  0.94   |  0.96  |     |
|     **scikit.image:issue_post:member-scikit.image:issue_post:nonmember**     | 3W: Types x Author Groups x Project |  -5.764  | 0.0001  | 0.0001 | *** |
|    **scikit.image:issue_reply:member-scikit.image:issue_reply:nonmember**    | 3W: Types x Author Groups x Project |  -10.21  | 0.0001  | 0.0001 | *** |
|        **scikit.image:pr_post:member-scikit.image:pr_post:nonmember**        | 3W: Types x Author Groups x Project |  -1.35   |  0.177  | 0.213  |     |
|       **scikit.image:pr_reply:member-scikit.image:pr_reply:nonmember**       | 3W: Types x Author Groups x Project |  -11.27  | 0.0001  | 0.0001 | *** |
|      **scikit.image:issue_post:member-scikit.image:issue_reply:member**      | 3W: Types x Author Groups x Project |  -5.824  | 0.0001  | 0.0001 | *** |
|   **scikit.image:issue_post:nonmember-scikit.image:issue_reply:nonmember**   | 3W: Types x Author Groups x Project |  -4.37   | 0.0001  | 0.0001 | *** |
|         **scikit.image:pr_post:member-scikit.image:pr_reply:member**         | 3W: Types x Author Groups x Project |  -18.71  | 0.0001  | 0.0001 | *** |
|      **scikit.image:pr_post:nonmember-scikit.image:pr_reply:nonmember**      | 3W: Types x Author Groups x Project |  -15.96  | 0.0001  | 0.0001 | *** |
|        **scikit.image:issue_post:member-scikit.image:pr_post:member**        | 3W: Types x Author Groups x Project |  -0.245  |  0.81   |  0.84  |     |
|     **scikit.image:issue_post:nonmember-scikit.image:pr_post:nonmember**     | 3W: Types x Author Groups x Project |   4.68   | 0.0001  | 0.0001 | *** |
|       **scikit.image:issue_reply:member-scikit.image:pr_reply:member**       | 3W: Types x Author Groups x Project |  -16.7   | 0.0001  | 0.0001 | *** |
|    **scikit.image:issue_reply:nonmember-scikit.image:pr_reply:nonmember**    | 3W: Types x Author Groups x Project |  -7.533  | 0.0001  | 0.0001 | *** |
|       **matplotlib:issue_post:member-matplotlib:issue_post:nonmember**       | 3W: Types x Author Groups x Project |  -5.063  | 0.0001  | 0.0001 | *** |
|      **matplotlib:issue_reply:member-matplotlib:issue_reply:nonmember**      | 3W: Types x Author Groups x Project |  -34.87  | 0.0001  | 0.0001 | *** |
|          **matplotlib:pr_post:member-matplotlib:pr_post:nonmember**          | 3W: Types x Author Groups x Project |  -1.511  |  0.131  | 0.162  |     |
|         **matplotlib:pr_reply:member-matplotlib:pr_reply:nonmember**         | 3W: Types x Author Groups x Project |  -17.14  | 0.0001  | 0.0001 | *** |
|        **matplotlib:issue_post:member-matplotlib:issue_reply:member**        | 3W: Types x Author Groups x Project | -0.2652  |  0.79   |  0.84  |     |
|     **matplotlib:issue_post:nonmember-matplotlib:issue_reply:nonmember**     | 3W: Types x Author Groups x Project |   -15    | 0.0001  | 0.0001 | *** |
|           **matplotlib:pr_post:member-matplotlib:pr_reply:member**           | 3W: Types x Author Groups x Project |  -16.78  | 0.0001  | 0.0001 | *** |
|        **matplotlib:pr_post:nonmember-matplotlib:pr_reply:nonmember**        | 3W: Types x Author Groups x Project |  -16.78  | 0.0001  | 0.0001 | *** |
|          **matplotlib:issue_post:member-matplotlib:pr_post:member**          | 3W: Types x Author Groups x Project |  3.494   |    0    | 0.001  | **  |
|       **matplotlib:issue_post:nonmember-matplotlib:pr_post:nonmember**       | 3W: Types x Author Groups x Project |  6.711   | 0.0001  | 0.0001 | *** |
|         **matplotlib:issue_reply:member-matplotlib:pr_reply:member**         | 3W: Types x Author Groups x Project |  -16.05  | 0.0001  | 0.0001 | *** |
|      **matplotlib:issue_reply:nonmember-matplotlib:pr_reply:nonmember**      | 3W: Types x Author Groups x Project |  2.634   |  0.008  | 0.012  |  *  |
|           **mayavi:issue_post:member-mayavi:issue_post:nonmember**           | 3W: Types x Author Groups x Project |  -5.676  | 0.0001  | 0.0001 | *** |
|          **mayavi:issue_reply:member-mayavi:issue_reply:nonmember**          | 3W: Types x Author Groups x Project |  -6.561  | 0.0001  | 0.0001 | *** |
|              **mayavi:pr_post:member-mayavi:pr_post:nonmember**              | 3W: Types x Author Groups x Project | 0.01372  |  0.99   |  0.99  |     |
|             **mayavi:pr_reply:member-mayavi:pr_reply:nonmember**             | 3W: Types x Author Groups x Project |  5.344   | 0.0001  | 0.0001 | *** |
|            **mayavi:issue_post:member-mayavi:issue_reply:member**            | 3W: Types x Author Groups x Project |  -3.327  |  0.001  | 0.001  | **  |
|         **mayavi:issue_post:nonmember-mayavi:issue_reply:nonmember**         | 3W: Types x Author Groups x Project | -0.6657  |  0.51   |  0.56  |     |
|               **mayavi:pr_post:member-mayavi:pr_reply:member**               | 3W: Types x Author Groups x Project |  -10.89  | 0.0001  | 0.0001 | *** |
|            **mayavi:pr_post:nonmember-mayavi:pr_reply:nonmember**            | 3W: Types x Author Groups x Project |  -3.758  | 0.0002  | 0.0003 | *** |
|              **mayavi:issue_post:member-mayavi:pr_post:member**              | 3W: Types x Author Groups x Project |  -0.828  |  0.41   |  0.46  |     |
|           **mayavi:issue_post:nonmember-mayavi:pr_post:nonmember**           | 3W: Types x Author Groups x Project |  4.919   | 0.0001  | 0.0001 | *** |
|             **mayavi:issue_reply:member-mayavi:pr_reply:member**             | 3W: Types x Author Groups x Project |  -10.43  | 0.0001  | 0.0001 | *** |
|          **mayavi:issue_reply:nonmember-mayavi:pr_reply:nonmember**          | 3W: Types x Author Groups x Project |  1.928   |  0.054  |  0.07  |  .  |
|           **pandas:issue_post:member-pandas:issue_post:nonmember**           | 3W: Types x Author Groups x Project |  -11.14  | 0.0001  | 0.0001 | *** |
|          **pandas:issue_reply:member-pandas:issue_reply:nonmember**          | 3W: Types x Author Groups x Project |  -44.34  | 0.0001  | 0.0001 | *** |
|              **pandas:pr_post:member-pandas:pr_post:nonmember**              | 3W: Types x Author Groups x Project |  -2.736  |  0.006  | 0.009  | **  |
|             **pandas:pr_reply:member-pandas:pr_reply:nonmember**             | 3W: Types x Author Groups x Project |  -21.1   | 0.0001  | 0.0001 | *** |
|            **pandas:issue_post:member-pandas:issue_reply:member**            | 3W: Types x Author Groups x Project |  -11.42  | 0.0001  | 0.0001 | *** |
|         **pandas:issue_post:nonmember-pandas:issue_reply:nonmember**         | 3W: Types x Author Groups x Project |  -24.59  | 0.0001  | 0.0001 | *** |
|               **pandas:pr_post:member-pandas:pr_reply:member**               | 3W: Types x Author Groups x Project |  -34.08  | 0.0001  | 0.0001 | *** |
|            **pandas:pr_post:nonmember-pandas:pr_reply:nonmember**            | 3W: Types x Author Groups x Project |  -28.34  | 0.0001  | 0.0001 | *** |
|              **pandas:issue_post:member-pandas:pr_post:member**              | 3W: Types x Author Groups x Project |  1.214   |  0.225  |  0.26  |     |
|           **pandas:issue_post:nonmember-pandas:pr_post:nonmember**           | 3W: Types x Author Groups x Project |   7.08   | 0.0001  | 0.0001 | *** |
|             **pandas:issue_reply:member-pandas:pr_reply:member**             | 3W: Types x Author Groups x Project |  -42.2   | 0.0001  | 0.0001 | *** |
|          **pandas:issue_reply:nonmember-pandas:pr_reply:nonmember**          | 3W: Types x Author Groups x Project |  -2.93   |  0.003  | 0.005  | **  |
|            **scipy:issue_post:member-scipy:issue_post:nonmember**            | 3W: Types x Author Groups x Project |  -7.369  | 0.0001  | 0.0001 | *** |
|           **scipy:issue_reply:member-scipy:issue_reply:nonmember**           | 3W: Types x Author Groups x Project |  -23.39  | 0.0001  | 0.0001 | *** |
|               **scipy:pr_post:member-scipy:pr_post:nonmember**               | 3W: Types x Author Groups x Project |  -2.303  |  0.021  | 0.028  |  *  |
|              **scipy:pr_reply:member-scipy:pr_reply:nonmember**              | 3W: Types x Author Groups x Project |  -3.462  |    0    | 0.001  | **  |
|             **scipy:issue_post:member-scipy:issue_reply:member**             | 3W: Types x Author Groups x Project |  -4.591  | 0.0001  | 0.0001 | *** |
|          **scipy:issue_post:nonmember-scipy:issue_reply:nonmember**          | 3W: Types x Author Groups x Project |  -9.837  | 0.0001  | 0.0001 | *** |
|                **scipy:pr_post:member-scipy:pr_reply:member**                | 3W: Types x Author Groups x Project |  -24.8   | 0.0001  | 0.0001 | *** |
|             **scipy:pr_post:nonmember-scipy:pr_reply:nonmember**             | 3W: Types x Author Groups x Project |  -16.08  | 0.0001  | 0.0001 | *** |
|               **scipy:issue_post:member-scipy:pr_post:member**               | 3W: Types x Author Groups x Project | -0.3404  |  0.73   |  0.79  |     |
|            **scipy:issue_post:nonmember-scipy:pr_post:nonmember**            | 3W: Types x Author Groups x Project |   6.3    | 0.0001  | 0.0001 | *** |
|              **scipy:issue_reply:member-scipy:pr_reply:member**              | 3W: Types x Author Groups x Project |  -30.52  | 0.0001  | 0.0001 | *** |
|           **scipy:issue_reply:nonmember-scipy:pr_reply:nonmember**           | 3W: Types x Author Groups x Project | -0.1306  |   0.9   |  0.92  |     |
|            **numpy:issue_post:member-numpy:issue_post:nonmember**            | 3W: Types x Author Groups x Project |  -5.816  | 0.0001  | 0.0001 | *** |
|           **numpy:issue_reply:member-numpy:issue_reply:nonmember**           | 3W: Types x Author Groups x Project |  -31.55  | 0.0001  | 0.0001 | *** |
|               **numpy:pr_post:member-numpy:pr_post:nonmember**               | 3W: Types x Author Groups x Project |  -1.043  |   0.3   |  0.34  |     |
|              **numpy:pr_reply:member-numpy:pr_reply:nonmember**              | 3W: Types x Author Groups x Project |  -4.952  | 0.0001  | 0.0001 | *** |
|             **numpy:issue_post:member-numpy:issue_reply:member**             | 3W: Types x Author Groups x Project |  -2.63   |  0.008  | 0.012  |  *  |
|          **numpy:issue_post:nonmember-numpy:issue_reply:nonmember**          | 3W: Types x Author Groups x Project |  -14.07  | 0.0001  | 0.0001 | *** |
|                **numpy:pr_post:member-numpy:pr_reply:member**                | 3W: Types x Author Groups x Project |  -23.84  | 0.0001  | 0.0001 | *** |
|             **numpy:pr_post:nonmember-numpy:pr_reply:nonmember**             | 3W: Types x Author Groups x Project |  -15.33  | 0.0001  | 0.0001 | *** |
|               **numpy:issue_post:member-numpy:pr_post:member**               | 3W: Types x Author Groups x Project |  1.746   |  0.081  | 0.103  |     |
|            **numpy:issue_post:nonmember-numpy:pr_post:nonmember**            | 3W: Types x Author Groups x Project |  5.941   | 0.0001  | 0.0001 | *** |
|              **numpy:issue_reply:member-numpy:pr_reply:member**              | 3W: Types x Author Groups x Project |  -32.27  | 0.0001  | 0.0001 | *** |
|           **numpy:issue_reply:nonmember-numpy:pr_reply:nonmember**           | 3W: Types x Author Groups x Project |  3.737   | 0.0002  | 0.0003 | *** |
|   **sphinx.gallery:issue_post:member-sphinx.gallery:issue_post:nonmember**   | 3W: Types x Author Groups x Project |  -1.779  |  0.075  | 0.096  |  .  |
|  **sphinx.gallery:issue_reply:member-sphinx.gallery:issue_reply:nonmember**  | 3W: Types x Author Groups x Project |  -6.106  | 0.0001  | 0.0001 | *** |
|      **sphinx.gallery:pr_post:member-sphinx.gallery:pr_post:nonmember**      | 3W: Types x Author Groups x Project | -0.7359  |  0.46   |  0.52  |     |
|     **sphinx.gallery:pr_reply:member-sphinx.gallery:pr_reply:nonmember**     | 3W: Types x Author Groups x Project | -0.1834  |  0.85   |  0.89  |     |
|    **sphinx.gallery:issue_post:member-sphinx.gallery:issue_reply:member**    | 3W: Types x Author Groups x Project | -0.5917  |  0.55   |  0.61  |     |
| **sphinx.gallery:issue_post:nonmember-sphinx.gallery:issue_reply:nonmember** | 3W: Types x Author Groups x Project |  -2.005  |  0.045  | 0.059  |  .  |
|       **sphinx.gallery:pr_post:member-sphinx.gallery:pr_reply:member**       | 3W: Types x Author Groups x Project |  -3.954  | 0.0001  | 0.0001 | *** |
|    **sphinx.gallery:pr_post:nonmember-sphinx.gallery:pr_reply:nonmember**    | 3W: Types x Author Groups x Project |  -1.466  |  0.143  | 0.175  |     |
|      **sphinx.gallery:issue_post:member-sphinx.gallery:pr_post:member**      | 3W: Types x Author Groups x Project |  0.5129  |  0.61   |  0.66  |     |
|   **sphinx.gallery:issue_post:nonmember-sphinx.gallery:pr_post:nonmember**   | 3W: Types x Author Groups x Project |  1.229   |  0.219  |  0.26  |     |
|     **sphinx.gallery:issue_reply:member-sphinx.gallery:pr_reply:member**     | 3W: Types x Author Groups x Project |  -4.463  | 0.0001  | 0.0001 | *** |
|  **sphinx.gallery:issue_reply:nonmember-sphinx.gallery:pr_reply:nonmember**  | 3W: Types x Author Groups x Project |  2.553   |  0.011  | 0.015  |  *  |

### Model 1.4: Do tickets and comments materially differ in gratitude over time?


```r
# do users tend to express appreciation and gratitude differently by group and content?
creators_v_commenters_gratitude_time = lmer(log(grateful_count + 1) ~ project + 
                                              (author_group + type) * ns(date, df=degrees_of_freedom) +
                                              (1 | author_name),
                                            data=sentiment_frame)
#family=poisson)

# print results
pander_lme(creators_v_commenters_gratitude_time)
```



|                           &nbsp;                            |  Estimate  | Std..Error |   df   | t.value |   p    | p_adj  | sig |
|:-----------------------------------------------------------:|:----------:|:----------:|:------:|:-------:|:------:|:------:|:---:|
|                       **(Intercept)**                       |  0.06311   |  0.004417  | 262967 |  14.29  | 0.0001 | 0.0001 | *** |
|                      **projectmayavi**                      |   0.0493   |  0.007211  | 113994 |  6.837  | 0.0001 | 0.0001 | *** |
|                      **projectnumpy**                       | -0.006947  |  0.002306  | 238782 | -3.013  | 0.003  | 0.004  | **  |
|                      **projectpandas**                      | -0.004654  |  0.00231   | 136210 | -2.014  | 0.044  | 0.058  |  .  |
|                   **projectscikit-image**                   | -0.007032  |  0.003318  | 251358 | -2.119  | 0.034  | 0.048  |  *  |
|                   **projectscikit-learn**                   | -0.009497  |  0.002443  | 133013 | -3.887  | 0.0001 | 0.0002 | *** |
|                      **projectscipy**                       |  0.008664  |  0.002434  | 238851 |  3.56   | 0.0004 | 0.001  | **  |
|                  **projectsphinx-gallery**                  |  -0.01512  |  0.004912  | 494933 | -3.078  | 0.002  | 0.004  | **  |
|                  **author_groupnonmember**                  |  0.03562   |  0.002859  | 284676 |  12.46  | 0.0001 | 0.0001 | *** |
|                     **typeissue_reply**                     |  0.04683   |  0.003655  | 507421 |  12.81  | 0.0001 | 0.0001 | *** |
|                       **typepr_post**                       | -0.0005321 |  0.004644  | 506461 | -0.1146 |  0.91  |  0.91  |     |
|                      **typepr_reply**                       |  0.07087   |  0.003709  | 505050 |  19.11  | 0.0001 | 0.0001 | *** |
|            **ns(date, df = degrees_of_freedom)**            |  -0.00268  |  0.006917  | 498412 | -0.3874 |  0.7   |  0.74  |     |
| **author_groupnonmember:ns(date, df = degrees_of_freedom)** |  -0.03261  |  0.005326  | 154656 | -6.123  | 0.0001 | 0.0001 | *** |
|    **typeissue_reply:ns(date, df = degrees_of_freedom)**    |  0.01302   |  0.006913  | 502013 |  1.883  |  0.06  | 0.072  |  .  |
|      **typepr_post:ns(date, df = degrees_of_freedom)**      |  0.008921  |  0.008709  | 501510 |  1.024  |  0.31  |  0.35  |     |
|     **typepr_reply:ns(date, df = degrees_of_freedom)**      |  0.06017   |  0.007013  | 496479 |  8.58   | 0.0001 | 0.0001 | *** |


```
## `geom_smooth()` using method = 'gam' and formula 'y ~ s(x, bs = "cs")'
## `geom_smooth()` using method = 'gam' and formula 'y ~ s(x, bs = "cs")'
## `geom_smooth()` using method = 'gam' and formula 'y ~ s(x, bs = "cs")'
## `geom_smooth()` using method = 'gam' and formula 'y ~ s(x, bs = "cs")'
## `geom_smooth()` using method = 'gam' and formula 'y ~ s(x, bs = "cs")'
```

![**Figure**. Expressions of gratitude over time by contribution type (ticket vs. comment) and community membership (member vs. nonmember) at the time of posting.](../../figures/sentiment_analysis/ossc-gratitude_membership_contribution_time-knitr.jpg)

## Model Series 2: Retention

Our second set of models investigates what aspects of the response to a 
newcomer's first contribution might predict their likelihood to come back
to contribute a second time.

### Data preparation

Because each ticket has multiple comments, we cannot use the standard long-form
format for the dataset, or we would lead to (uneven) duplication of tickets
based on the varying numbers of comments. As a result, we pull metrics of the
whole comment chain and use them as our measures of the community's response
to the newcomer's contribution.


```r
# aggregate ticket-level metrics for comments
aggregated_comments = comments_frame %>% ungroup() %>%
  
  # convert author group to numeric
  mutate(author_group_numeric = dplyr::if_else(author_group=='member',
                                               1,
                                               0)) %>%
  
  # create metrics for each unique ticket in each project
  dplyr::group_by(project, ticket_id) %>%
  dplyr::summarise(number_of_comments = n(),
                   comment_sentiment_mean = mean(compound_emotion, na.rm=TRUE),
                   comment_sentiment_variance = var(compound_emotion),
                   comment_sentiment_max_negative = max(negative_emotion),
                   comment_sentiment_max_positive = max(positive_emotion),
                   comment_grateful_cumulative = sum(grateful_count),
                   comment_first_response = min(date),
                   comment_member_ratio = sum(author_group_numeric)/n())
```

After we've summarized the comment threads, we next join those metrics with the
tickets dataframe in preparation for our models.


```r
# create joint dataframe
retention_frame = tickets_frame %>%
  dplyr::left_join(., aggregated_comments,
                   by=c('project', 'ticket_id')) %>%
  
  # keep only newcomers
  dplyr::filter(first_ticket == TRUE) %>%
  
  # keep only select variables
  dplyr::select(project,
                date,
                contains('author'),
                first_ticket,
                contains('num_'),
                contains('ticket'),
                contains('type'),
                contains('grateful_count'),
                contains('emotion'),
                open_time,
                contains('comment_'),
                number_of_comments,
                -contains('stamp'),
                -contains('last_comment')) %>%
  
  # read appropriate variables as logical
  mutate_at(vars(first_ticket,
                 ticket_author_last_ticket),
            as.logical) %>%
  
  # recode and rename retention variable so that it reflects continued engagement
  dplyr::rename(retained_newcomer = ticket_author_last_ticket) %>%
  mutate(retained_newcomer = dplyr::if_else(retained_newcomer==TRUE,
                                            FALSE,
                                            TRUE)) %>%
  
  # recode ticket group as two-level numeric factor
  mutate(ticket_family_numeric = dplyr::if_else(ticket_family=='issue',
                                                -.5,
                                                .5)) %>%
  
  #convert to factors (as needed) for proper modeling
  mutate_at(vars(project,
                 author_name,
                 author_group,
                 author_association,
                 type,
                 type_family,
                 ticket_family,
                 ticket_family_numeric,
                 retained_newcomer),
            as.factor)
```

### Model 2.1: How does a community's response to newcomers predict the newcomer's decision to return?


```r
# what predicts continuing retention?
retention_predictors = glm(retained_newcomer ~ 0 + ticket_family_numeric * (project +
                                                                              open_time +
                                                                              comment_sentiment_mean + 
                                                                              comment_sentiment_max_negative + 
                                                                              comment_grateful_cumulative +
                                                                              number_of_comments +
                                                                              comment_member_ratio),
                           data=retention_frame,
                           family=binomial)
```


------------------------------------------------------------------------------
                           &nbsp;                                 Estimate    
------------------------------------------------------------- ----------------
                **ticket_family_numeric-0.5**                     -0.6317     

                **ticket_family_numeric0.5**                       0.405      

                      **projectmayavi**                           -0.3241     

                      **projectnumpy**                             -0.43      

                      **projectpandas**                            0.2543     

                   **projectscikit-image**                        -0.06416    

                   **projectscikit-learn**                        -0.08375    

                      **projectscipy**                            -0.4465     

                  **projectsphinx-gallery**                        0.6894     

                        **open_time**                          0.000000001739 

                 **comment_sentiment_mean**                        0.3459     

             **comment_sentiment_max_negative**                   -0.3342     

               **comment_grateful_cumulative**                    -0.08027    

                   **number_of_comments**                         0.01935     

                  **comment_member_ratio**                        -0.3592     

         **ticket_family_numeric0.5:projectmayavi**               -0.06201    

          **ticket_family_numeric0.5:projectnumpy**                0.4436     

         **ticket_family_numeric0.5:projectpandas**               -0.2797     

      **ticket_family_numeric0.5:projectscikit-image**             0.2495     

      **ticket_family_numeric0.5:projectscikit-learn**             0.1798     

          **ticket_family_numeric0.5:projectscipy**                0.5958     

     **ticket_family_numeric0.5:projectsphinx-gallery**           -0.01765    

           **ticket_family_numeric0.5:open_time**              -0.00000001105 

     **ticket_family_numeric0.5:comment_sentiment_mean**          -0.02864    

 **ticket_family_numeric0.5:comment_sentiment_max_negative**       0.4052     

  **ticket_family_numeric0.5:comment_grateful_cumulative**        -0.0078     

       **ticket_family_numeric0.5:number_of_comments**            0.01044     

      **ticket_family_numeric0.5:comment_member_ratio**           -0.7747     
------------------------------------------------------------------------------

Table: Table continues below

 
-------------------------------------------------------------------------------
                           &nbsp;                                Std. Error    
------------------------------------------------------------- -----------------
                **ticket_family_numeric-0.5**                      0.08575     

                **ticket_family_numeric0.5**                       0.1339      

                      **projectmayavi**                            0.1639      

                      **projectnumpy**                             0.07531     

                      **projectpandas**                            0.06014     

                   **projectscikit-image**                         0.1162      

                   **projectscikit-learn**                         0.06944     

                      **projectscipy**                             0.07989     

                  **projectsphinx-gallery**                        0.3103      

                        **open_time**                          0.0000000005173 

                 **comment_sentiment_mean**                        0.08742     

             **comment_sentiment_max_negative**                     0.204      

               **comment_grateful_cumulative**                     0.02279     

                   **number_of_comments**                          0.00406     

                  **comment_member_ratio**                         0.08201     

         **ticket_family_numeric0.5:projectmayavi**                0.4253      

          **ticket_family_numeric0.5:projectnumpy**                0.1352      

         **ticket_family_numeric0.5:projectpandas**                0.1155      

      **ticket_family_numeric0.5:projectscikit-image**             0.1916      

      **ticket_family_numeric0.5:projectscikit-learn**             0.1198      

          **ticket_family_numeric0.5:projectscipy**                0.1399      

     **ticket_family_numeric0.5:projectsphinx-gallery**            0.6236      

           **ticket_family_numeric0.5:open_time**              0.000000001862  

     **ticket_family_numeric0.5:comment_sentiment_mean**           0.1824      

 **ticket_family_numeric0.5:comment_sentiment_max_negative**       0.3331      

  **ticket_family_numeric0.5:comment_grateful_cumulative**         0.03205     

       **ticket_family_numeric0.5:number_of_comments**            0.006219     

      **ticket_family_numeric0.5:comment_member_ratio**            0.1514      
-------------------------------------------------------------------------------

Table: Table continues below

 
-----------------------------------------------------------------------
                           &nbsp;                              z value 
------------------------------------------------------------- ---------
                **ticket_family_numeric-0.5**                  -7.366  

                **ticket_family_numeric0.5**                    3.024  

                      **projectmayavi**                        -1.977  

                      **projectnumpy**                          -5.71  

                      **projectpandas**                         4.228  

                   **projectscikit-image**                     -0.5521 

                   **projectscikit-learn**                     -1.206  

                      **projectscipy**                         -5.588  

                  **projectsphinx-gallery**                     2.222  

                        **open_time**                           3.361  

                 **comment_sentiment_mean**                     3.956  

             **comment_sentiment_max_negative**                -1.638  

               **comment_grateful_cumulative**                 -3.522  

                   **number_of_comments**                       4.766  

                  **comment_member_ratio**                      -4.38  

         **ticket_family_numeric0.5:projectmayavi**            -0.1458 

          **ticket_family_numeric0.5:projectnumpy**             3.281  

         **ticket_family_numeric0.5:projectpandas**            -2.422  

      **ticket_family_numeric0.5:projectscikit-image**          1.302  

      **ticket_family_numeric0.5:projectscikit-learn**          1.501  

          **ticket_family_numeric0.5:projectscipy**             4.259  

     **ticket_family_numeric0.5:projectsphinx-gallery**        -0.0283 

           **ticket_family_numeric0.5:open_time**              -5.936  

     **ticket_family_numeric0.5:comment_sentiment_mean**       -0.157  

 **ticket_family_numeric0.5:comment_sentiment_max_negative**    1.217  

  **ticket_family_numeric0.5:comment_grateful_cumulative**     -0.2433 

       **ticket_family_numeric0.5:number_of_comments**          1.679  

      **ticket_family_numeric0.5:comment_member_ratio**        -5.117  
-----------------------------------------------------------------------

Table: Table continues below

 
----------------------------------------------------------------------------------
                           &nbsp;                                   Pr(>|z|)      
------------------------------------------------------------- --------------------
                **ticket_family_numeric-0.5**                  0.0000000000001752 

                **ticket_family_numeric0.5**                        0.002498      

                      **projectmayavi**                             0.04806       

                      **projectnumpy**                           0.00000001132    

                      **projectpandas**                            0.0000236      

                   **projectscikit-image**                           0.5809       

                   **projectscikit-learn**                           0.2278       

                      **projectscipy**                           0.00000002294    

                  **projectsphinx-gallery**                         0.02631       

                        **open_time**                              0.0007753      

                 **comment_sentiment_mean**                        0.00007606     

             **comment_sentiment_max_negative**                      0.1014       

               **comment_grateful_cumulative**                     0.0004283      

                   **number_of_comments**                         0.000001877     

                  **comment_member_ratio**                         0.00001186     

         **ticket_family_numeric0.5:projectmayavi**                  0.8841       

          **ticket_family_numeric0.5:projectnumpy**                 0.001033      

         **ticket_family_numeric0.5:projectpandas**                 0.01544       

      **ticket_family_numeric0.5:projectscikit-image**               0.1928       

      **ticket_family_numeric0.5:projectscikit-learn**               0.1334       

          **ticket_family_numeric0.5:projectscipy**                0.0000205      

     **ticket_family_numeric0.5:projectsphinx-gallery**              0.9774       

           **ticket_family_numeric0.5:open_time**                0.00000000292    

     **ticket_family_numeric0.5:comment_sentiment_mean**             0.8752       

 **ticket_family_numeric0.5:comment_sentiment_max_negative**         0.2237       

  **ticket_family_numeric0.5:comment_grateful_cumulative**           0.8077       

       **ticket_family_numeric0.5:number_of_comments**              0.09322       

      **ticket_family_numeric0.5:comment_member_ratio**           0.0000003111    
----------------------------------------------------------------------------------


(Dispersion parameter for  binomial  family taken to be  1 )


-------------------- -----------------------------
   Null deviance:     22440  on 16187  degrees of 
                                freedom           

 Residual deviance:   20198  on 16159  degrees of 
                                freedom           
-------------------- -----------------------------






![**Figure**. Whether a first-time ticket creator will open a second ticket by commenters' expressions of gratitude and responsiveness.](../../figures/sentiment_analysis/ossc-retention_emotion-by_project-knitr.jpg)

***

# Future directions

Ideas:

* Do comments, generally, get more friendly or more hostile over time?
* Does the emotional valence of a contributor's first ticket predict whether
they'll come back to make a second one?
* Are requesters more or less polite?
* Does friendliness bring people back?
* Does the number and intensity of negative and positive comments on a
first-time contributor's ticket change whether they come back to make another
ticket?
