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
* `./utils/data-loading.R`: loads functions related to data loading and
  preprocessing.

**Code written by**: A. Paxton (University of Connecticut) & N. Varoquaux
(CNRS)

**Date last compiled**:  2019-10-15 16:17:10



***

# Preliminaries


```r
# clear everything
rm(list=ls())

# load libraries and add new functions
source('./utils/ossc-libraries_and_functions.r')
source("./utils/data-loading.R")
```


```r
# We are now going to select the dataset we'll be working on.
library(dplyr)
tickets_frame = loading_tickets_data(dataset="original")
comments_frame = loading_comments_data(dataset="original")
```


## Basic summary stats

The data has been largely cleaned. Let's take a look at some basic
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
54878 average comments per project.

In total, we have 15560 unique commenters,
14147 unique ticket-creators, and
19430 overall unique users.

***

# Data analysis

***

## Model Series 1: Sentiment analysis

### Data preparation

Before we can run Model Series 1, we need to combine `tickets_frame` and
`comments_frame` into a single dataframe. We do this using the
`combine_tickets_and_comments` function, `defined in utils/data-loading.R`


```r
sentiment_frame = combine_tickets_and_comments(tickets_frame, comments_frame)
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

#### Model 1.2b: More plots, this time using means and std estimated from model-fit

Here, we are going to test whether projects differ from the mean.


```r
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
```


```r
projects = c("Matplotlib", "Mayavi", "numpy", "pandas",
	     "scikit-image", "scikit-learn", "scipy", "sphinx-gallery")
```


```r
group_of_interest = "pr_post:member"
rows_to_plot = grep(group_of_interest, names(means))

bar_centers = barplot(means[rows_to_plot], names.arg=projects,
		      main=group_of_interest,    
		      cex.names=0.8)
arrows(bar_centers,
       means[rows_to_plot] - se[rows_to_plot] ** 2, 
       bar_centers,
       means[rows_to_plot] + se[rows_to_plot] ** 2,
       angle=90,
       code=3)
```

![](oss_community-language_dynamics_files/figure-html/plot_pr_post_members-1.png)<!-- -->


```r
group_of_interest = "pr_post:nonmember"
rows_to_plot = grep(group_of_interest, names(means))

bar_centers = barplot(means[rows_to_plot], names.arg=projects,
		      main=group_of_interest,
		      cex.names=0.8)

arrows(bar_centers,
       means[rows_to_plot] - se[rows_to_plot] ** 2, 
       bar_centers,
       means[rows_to_plot] + se[rows_to_plot] ** 2,
       angle=90,
       code=3)
```

![](oss_community-language_dynamics_files/figure-html/plot_pr_post_nonmembers-1.png)<!-- -->



```r
group_of_interest = "issue_post:member"
rows_to_plot = grep(group_of_interest, names(means))

bar_centers = barplot(means[rows_to_plot], names.arg=projects,
		      main=group_of_interest,
		      cex.names=0.8
		      )
arrows(bar_centers,
       means[rows_to_plot] - se[rows_to_plot] ** 2, 
       bar_centers,
       means[rows_to_plot] + se[rows_to_plot] ** 2,
       angle=90,
       code=3)
```

![](oss_community-language_dynamics_files/figure-html/plot_issue_post_members-1.png)<!-- -->


```r
group_of_interest = "issue_post:nonmember"
rows_to_plot = grep(group_of_interest, names(means))

bar_centers = barplot(means[rows_to_plot], names.arg=projects,
		      main=group_of_interest,
		      cex.names=0.8
		      )
arrows(bar_centers,
       means[rows_to_plot] - se[rows_to_plot] ** 2, 
       bar_centers,
       means[rows_to_plot] + se[rows_to_plot] ** 2,
       angle=90,
       code=3)
```

![](oss_community-language_dynamics_files/figure-html/plot_issue_post_nonmembers-1.png)<!-- -->



```r
group_of_interest = "pr_reply:member"
rows_to_plot = grep(group_of_interest, names(means))

bar_centers = barplot(means[rows_to_plot], names.arg=projects,
		      main=group_of_interest,
		      cex.names=0.8)
arrows(bar_centers,
       means[rows_to_plot] - se[rows_to_plot] ** 2, 
       bar_centers,
       means[rows_to_plot] + se[rows_to_plot] ** 2,
       angle=90,
       code=3)
```

```
## Warning in arrows(bar_centers, means[rows_to_plot] - se[rows_to_plot]^2, :
## zero-length arrow is of indeterminate angle and so skipped

## Warning in arrows(bar_centers, means[rows_to_plot] - se[rows_to_plot]^2, :
## zero-length arrow is of indeterminate angle and so skipped

## Warning in arrows(bar_centers, means[rows_to_plot] - se[rows_to_plot]^2, :
## zero-length arrow is of indeterminate angle and so skipped

## Warning in arrows(bar_centers, means[rows_to_plot] - se[rows_to_plot]^2, :
## zero-length arrow is of indeterminate angle and so skipped

## Warning in arrows(bar_centers, means[rows_to_plot] - se[rows_to_plot]^2, :
## zero-length arrow is of indeterminate angle and so skipped
```

![](oss_community-language_dynamics_files/figure-html/plot_pr_reply_members-1.png)<!-- -->


```r
group_of_interest = "pr_reply:nonmember"
rows_to_plot = grep(group_of_interest, names(means))

bar_centers = barplot(means[rows_to_plot], names.arg=projects,
		      main=group_of_interest,
		      cex.names=0.8)
arrows(bar_centers,
       means[rows_to_plot] - se[rows_to_plot] ** 2, 
       bar_centers,
       means[rows_to_plot] + se[rows_to_plot] ** 2,
       angle=90,
       code=3)
```

```
## Warning in arrows(bar_centers, means[rows_to_plot] - se[rows_to_plot]^2, :
## zero-length arrow is of indeterminate angle and so skipped

## Warning in arrows(bar_centers, means[rows_to_plot] - se[rows_to_plot]^2, :
## zero-length arrow is of indeterminate angle and so skipped
```

![](oss_community-language_dynamics_files/figure-html/plot_pr_reply_nonmembers-1.png)<!-- -->



```r
group_of_interest = "issue_reply:member"
rows_to_plot = grep(group_of_interest, names(means))

bar_centers = barplot(means[rows_to_plot], names.arg=projects,
		      main=group_of_interest,
		      cex.names=0.8)
arrows(bar_centers,
       means[rows_to_plot] - se[rows_to_plot] ** 2, 
       bar_centers,
       means[rows_to_plot] + se[rows_to_plot] ** 2,
       angle=90,
       code=3)
```

```
## Warning in arrows(bar_centers, means[rows_to_plot] - se[rows_to_plot]^2, :
## zero-length arrow is of indeterminate angle and so skipped

## Warning in arrows(bar_centers, means[rows_to_plot] - se[rows_to_plot]^2, :
## zero-length arrow is of indeterminate angle and so skipped

## Warning in arrows(bar_centers, means[rows_to_plot] - se[rows_to_plot]^2, :
## zero-length arrow is of indeterminate angle and so skipped

## Warning in arrows(bar_centers, means[rows_to_plot] - se[rows_to_plot]^2, :
## zero-length arrow is of indeterminate angle and so skipped

## Warning in arrows(bar_centers, means[rows_to_plot] - se[rows_to_plot]^2, :
## zero-length arrow is of indeterminate angle and so skipped
```

![](oss_community-language_dynamics_files/figure-html/plot_issue_reply_members-1.png)<!-- -->


```r
group_of_interest = "issue_reply:nonmember"
rows_to_plot = grep(group_of_interest, names(means))

bar_centers = barplot(means[rows_to_plot], names.arg=projects,
		      main=group_of_interest,
		      cex.names=0.8)
arrows(bar_centers,
       means[rows_to_plot] - se[rows_to_plot] ** 2, 
       bar_centers,
       means[rows_to_plot] + se[rows_to_plot] ** 2,
       angle=90,
       code=3)
```

```
## Warning in arrows(bar_centers, means[rows_to_plot] - se[rows_to_plot]^2, :
## zero-length arrow is of indeterminate angle and so skipped

## Warning in arrows(bar_centers, means[rows_to_plot] - se[rows_to_plot]^2, :
## zero-length arrow is of indeterminate angle and so skipped

## Warning in arrows(bar_centers, means[rows_to_plot] - se[rows_to_plot]^2, :
## zero-length arrow is of indeterminate angle and so skipped

## Warning in arrows(bar_centers, means[rows_to_plot] - se[rows_to_plot]^2, :
## zero-length arrow is of indeterminate angle and so skipped
```

![](oss_community-language_dynamics_files/figure-html/plot_issue_reply_nonmembers-1.png)<!-- -->

### Model 1.1c Do projects differ in emotion between one another?

One versus all minus one type of approach.


```r
all_project_tests = NA
all_projects = unique(sentiment_frame$project)

# We're going to fit the model for each projects, and concatenate the results
# in a dataframe. Then, we'll apply multiple correction and display the
# results
for(project in all_projects){
    sentiment_frame$test_group = sentiment_frame$project == project
    one_versus_all_emotion = lmer(
	compound_emotion ~ 0 + type:author_group:test_group + (1|author_name),
	data=sentiment_frame,
	REML=FALSE)

    # Clean up mode
    coefficients_and_se = data.frame(
	summary(one_versus_all_emotion)$coefficients)
    row_names = gsub(
	"author_group", "", 
	    gsub("type", "",
		gsub("project", "", row.names(coefficients_and_se))))

    means = coefficients_and_se$Estimate
    names(means) = row_names
    se = coefficients_and_se$Std..Error
    names(se) = row_names

    contrasts = c(
	"issue_post:member:test_groupTRUE-issue_post:member:test_groupFALSE",
	"pr_post:member:test_groupTRUE-pr_post:member:test_groupFALSE",
	"issue_reply:member:test_groupTRUE-issue_reply:member:test_groupFALSE",
	"pr_reply:member:test_groupTRUE-pr_reply:member:test_groupFALSE",
	"issue_post:nonmember:test_groupTRUE-issue_post:nonmember:test_groupFALSE",
	"pr_post:nonmember:test_groupTRUE-pr_post:nonmember:test_groupFALSE",
	"issue_reply:nonmember:test_groupTRUE-issue_reply:nonmember:test_groupFALSE",
	"pr_reply:nonmember:test_groupTRUE-pr_reply:nonmember:test_groupFALSE"
	)

    one_versus_all_emotion_tests = compute_t_statistics(
	means, se,
	contrasts)
    one_versus_all_emotion_tests[, "p_value"] = compute_p_value_from_t_stats(
	one_versus_all_emotion_tests$t_stats)

    # Add unique identifier based on the project of interest in the table.
    row.names(one_versus_all_emotion_tests) = gsub(
	"test_group", project,
	row.names(one_versus_all_emotion_tests))

    if(is.null(dim(all_project_tests))){
	all_project_tests = one_versus_all_emotion_tests
    }else{
	all_project_tests = rbind(
	    all_project_tests, one_versus_all_emotion_tests)
    }
}
```

Now apply multiple correction and display the results of the analysis.


```r
pander_clean_anova(all_project_tests, rename_columns=FALSE)
```



|                                         &nbsp;                                         | t_stats  | p_value | p_adj  | sig |
|:--------------------------------------------------------------------------------------:|:--------:|:-------:|:------:|:---:|
|              **issue_post:member:numpyTRUE-issue_post:member:numpyFALSE**              |  -4.762  | 0.0001  | 0.0001 | *** |
|                 **pr_post:member:numpyTRUE-pr_post:member:numpyFALSE**                 |  -2.573  |  0.01   | 0.025  |  *  |
|             **issue_reply:member:numpyTRUE-issue_reply:member:numpyFALSE**             |  -5.293  | 0.0001  | 0.0001 | *** |
|                **pr_reply:member:numpyTRUE-pr_reply:member:numpyFALSE**                |  0.219   |  0.83   |  0.88  |     |
|           **issue_post:nonmember:numpyTRUE-issue_post:nonmember:numpyFALSE**           |  -6.615  | 0.0001  | 0.0001 | *** |
|              **pr_post:nonmember:numpyTRUE-pr_post:nonmember:numpyFALSE**              |  -4.597  | 0.0001  | 0.0001 | *** |
|          **issue_reply:nonmember:numpyTRUE-issue_reply:nonmember:numpyFALSE**          |  -5.683  | 0.0001  | 0.0001 | *** |
|             **pr_reply:nonmember:numpyTRUE-pr_reply:nonmember:numpyFALSE**             |  -1.11   |  0.27   |  0.38  |     |
|       **issue_post:member:scikit-learnTRUE-issue_post:member:scikit-learnFALSE**       | -0.01398 |  0.99   |  0.99  |     |
|          **pr_post:member:scikit-learnTRUE-pr_post:member:scikit-learnFALSE**          |  3.399   |  0.001  | 0.002  | **  |
|      **issue_reply:member:scikit-learnTRUE-issue_reply:member:scikit-learnFALSE**      |  0.5696  |  0.57   |  0.69  |     |
|         **pr_reply:member:scikit-learnTRUE-pr_reply:member:scikit-learnFALSE**         |  1.548   |  0.122  | 0.205  |     |
|    **issue_post:nonmember:scikit-learnTRUE-issue_post:nonmember:scikit-learnFALSE**    |  0.7041  |  0.48   |  0.63  |     |
|       **pr_post:nonmember:scikit-learnTRUE-pr_post:nonmember:scikit-learnFALSE**       | -0.5552  |  0.58   |  0.69  |     |
|   **issue_reply:nonmember:scikit-learnTRUE-issue_reply:nonmember:scikit-learnFALSE**   |  1.382   |  0.167  |  0.26  |     |
|      **pr_reply:nonmember:scikit-learnTRUE-pr_reply:nonmember:scikit-learnFALSE**      |  2.235   |  0.025  | 0.052  |  .  |
|              **issue_post:member:scipyTRUE-issue_post:member:scipyFALSE**              |  -3.122  |  0.002  | 0.005  | **  |
|                 **pr_post:member:scipyTRUE-pr_post:member:scipyFALSE**                 | -0.5708  |  0.57   |  0.69  |     |
|             **issue_reply:member:scipyTRUE-issue_reply:member:scipyFALSE**             |  -0.189  |  0.85   |  0.89  |     |
|                **pr_reply:member:scipyTRUE-pr_reply:member:scipyFALSE**                |  5.345   | 0.0001  | 0.0001 | *** |
|           **issue_post:nonmember:scipyTRUE-issue_post:nonmember:scipyFALSE**           | -0.2549  |   0.8   |  0.87  |     |
|              **pr_post:nonmember:scipyTRUE-pr_post:nonmember:scipyFALSE**              |  1.554   |  0.12   | 0.205  |     |
|          **issue_reply:nonmember:scipyTRUE-issue_reply:nonmember:scipyFALSE**          |  3.279   |  0.001  | 0.003  | **  |
|             **pr_reply:nonmember:scipyTRUE-pr_reply:nonmember:scipyFALSE**             |   5.89   | 0.0001  | 0.0001 | *** |
|             **issue_post:member:mayaviTRUE-issue_post:member:mayaviFALSE**             |  -2.025  |  0.043  | 0.078  |  .  |
|                **pr_post:member:mayaviTRUE-pr_post:member:mayaviFALSE**                |  -2.453  |  0.014  | 0.032  |  *  |
|            **issue_reply:member:mayaviTRUE-issue_reply:member:mayaviFALSE**            |   -2.5   |  0.012  |  0.03  |  *  |
|               **pr_reply:member:mayaviTRUE-pr_reply:member:mayaviFALSE**               |  -3.296  |  0.001  | 0.003  | **  |
|          **issue_post:nonmember:mayaviTRUE-issue_post:nonmember:mayaviFALSE**          | -0.9832  |  0.33   |  0.45  |     |
|             **pr_post:nonmember:mayaviTRUE-pr_post:nonmember:mayaviFALSE**             |  -2.18   |  0.029  | 0.058  |  .  |
|         **issue_reply:nonmember:mayaviTRUE-issue_reply:nonmember:mayaviFALSE**         |  -3.533  | 0.0004  | 0.002  | **  |
|            **pr_reply:nonmember:mayaviTRUE-pr_reply:nonmember:mayaviFALSE**            | -0.5364  |  0.59   |  0.69  |     |
|     **issue_post:member:sphinx-galleryTRUE-issue_post:member:sphinx-galleryFALSE**     | 0.02178  |  0.98   |  0.99  |     |
|        **pr_post:member:sphinx-galleryTRUE-pr_post:member:sphinx-galleryFALSE**        |  0.5591  |  0.58   |  0.69  |     |
|    **issue_reply:member:sphinx-galleryTRUE-issue_reply:member:sphinx-galleryFALSE**    |  4.143   | 0.0001  | 0.0002 | *** |
|       **pr_reply:member:sphinx-galleryTRUE-pr_reply:member:sphinx-galleryFALSE**       | -0.03669 |  0.97   |  0.99  |     |
|  **issue_post:nonmember:sphinx-galleryTRUE-issue_post:nonmember:sphinx-galleryFALSE**  | -0.8765  |  0.38   |  0.51  |     |
|     **pr_post:nonmember:sphinx-galleryTRUE-pr_post:nonmember:sphinx-galleryFALSE**     |  1.721   |  0.085  | 0.152  |     |
| **issue_reply:nonmember:sphinx-galleryTRUE-issue_reply:nonmember:sphinx-galleryFALSE** |  2.095   |  0.036  |  0.07  |  .  |
|    **pr_reply:nonmember:sphinx-galleryTRUE-pr_reply:nonmember:sphinx-galleryFALSE**    | -0.3261  |  0.74   |  0.82  |     |
|         **issue_post:member:matplotlibTRUE-issue_post:member:matplotlibFALSE**         | -0.3677  |  0.71   |  0.81  |     |
|            **pr_post:member:matplotlibTRUE-pr_post:member:matplotlibFALSE**            |  0.963   |  0.34   |  0.46  |     |
|        **issue_reply:member:matplotlibTRUE-issue_reply:member:matplotlibFALSE**        |  -1.243  |  0.214  |  0.32  |     |
|           **pr_reply:member:matplotlibTRUE-pr_reply:member:matplotlibFALSE**           |  -4.548  | 0.0001  | 0.0001 | *** |
|      **issue_post:nonmember:matplotlibTRUE-issue_post:nonmember:matplotlibFALSE**      |  0.3518  |  0.72   |  0.81  |     |
|         **pr_post:nonmember:matplotlibTRUE-pr_post:nonmember:matplotlibFALSE**         |  -1.513  |  0.13   | 0.214  |     |
|     **issue_reply:nonmember:matplotlibTRUE-issue_reply:nonmember:matplotlibFALSE**     |  -3.286  |  0.001  | 0.003  | **  |
|        **pr_reply:nonmember:matplotlibTRUE-pr_reply:nonmember:matplotlibFALSE**        |  -2.074  |  0.038  | 0.072  |  .  |
|       **issue_post:member:scikit-imageTRUE-issue_post:member:scikit-imageFALSE**       |  -2.323  |  0.02   | 0.043  |  *  |
|          **pr_post:member:scikit-imageTRUE-pr_post:member:scikit-imageFALSE**          |  2.636   |  0.008  | 0.022  |  *  |
|      **issue_reply:member:scikit-imageTRUE-issue_reply:member:scikit-imageFALSE**      |  2.359   |  0.018  |  0.04  |  *  |
|         **pr_reply:member:scikit-imageTRUE-pr_reply:member:scikit-imageFALSE**         |  3.601   | 0.0003  | 0.001  | **  |
|    **issue_post:nonmember:scikit-imageTRUE-issue_post:nonmember:scikit-imageFALSE**    |  -1.11   |  0.27   |  0.38  |     |
|       **pr_post:nonmember:scikit-imageTRUE-pr_post:nonmember:scikit-imageFALSE**       |  9.303   | 0.0001  | 0.0001 | *** |
|   **issue_reply:nonmember:scikit-imageTRUE-issue_reply:nonmember:scikit-imageFALSE**   |   1.38   |  0.168  |  0.26  |     |
|      **pr_reply:nonmember:scikit-imageTRUE-pr_reply:nonmember:scikit-imageFALSE**      |  5.701   | 0.0001  | 0.0001 | *** |
|             **issue_post:member:pandasTRUE-issue_post:member:pandasFALSE**             |   4.74   | 0.0001  | 0.0001 | *** |
|                **pr_post:member:pandasTRUE-pr_post:member:pandasFALSE**                |  -3.146  |  0.002  | 0.005  | **  |
|            **issue_reply:member:pandasTRUE-issue_reply:member:pandasFALSE**            |  1.491   |  0.136  | 0.218  |     |
|               **pr_reply:member:pandasTRUE-pr_reply:member:pandasFALSE**               |  -2.64   |  0.008  | 0.022  |  *  |
|          **issue_post:nonmember:pandasTRUE-issue_post:nonmember:pandasFALSE**          |  4.907   | 0.0001  | 0.0001 | *** |
|             **pr_post:nonmember:pandasTRUE-pr_post:nonmember:pandasFALSE**             | -0.6625  |  0.51   |  0.65  |     |
|         **issue_reply:nonmember:pandasTRUE-issue_reply:nonmember:pandasFALSE**         |  3.448   |  0.001  | 0.002  | **  |
|            **pr_reply:nonmember:pandasTRUE-pr_reply:nonmember:pandasFALSE**            |  -7.581  | 0.0001  | 0.0001 | *** |

### Model 1.2 time-course analysis

The time-course analysis has been moved in a separate file.

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
