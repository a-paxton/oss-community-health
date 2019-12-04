---
title: "Communication dynamics in OSS communities (2019 data)"
output:
  html_document:
    keep_md: yes
    number_sections: yes
    toc: true
---

This R markdown provides the data preparation for our forthcoming manuscript
(Paxton, Varoquaux, Geiger, & Holdgraf, *in preparation*).

This file relies on the same dependencies than the analysis on the whole
dataset. In fact, it is the same analysis, just on 2019 data.

**Date last compiled** 2019-12-04 21:53:58



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
tickets_frame = loading_tickets_data(dataset="2019")
comments_frame = loading_comments_data(dataset="2019")
```


## Basic summary stats

The data has been largely cleaned. Let's take a look at some basic
patterns.




|    project     | unique_tickets | unique_comments |
|:--------------:|:--------------:|:---------------:|
|   matplotlib   |      1351      |      4915       |
|     mayavi     |       43       |       96        |
|     numpy      |      1075      |      8062       |
|     pandas     |      2300      |      14704      |
|  scikit-image  |      283       |      2253       |
|  scikit-learn  |      1061      |      8496       |
|     scipy      |      596       |      3937       |
| sphinx-gallery |       71       |       430       |

Our dataset includes 8 unique projects with a
total of 6780 unique tickets, with a
mean of 847.5 tickets per project.

On these tickets, the dataset includes
42893 unique comments, with
5361.625 average comments per project.

In total, we have 3385 unique commenters,
2330 unique ticket-creators, and
4114 overall unique users.

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
## Warning in bind_rows_(x, .id): binding character and factor vector, coercing
## into character vector

## Warning in bind_rows_(x, .id): binding character and factor vector, coercing
## into character vector
```

```
## Warning in bind_rows_(x, .id): Unequal factor levels: coercing to character
```

```
## Warning in bind_rows_(x, .id): binding character and factor vector, coercing
## into character vector

## Warning in bind_rows_(x, .id): binding character and factor vector, coercing
## into character vector
```

```
## Warning in bind_rows_(x, .id): Unequal factor levels: coercing to character
```

```
## Warning in bind_rows_(x, .id): binding character and factor vector, coercing
## into character vector

## Warning in bind_rows_(x, .id): binding character and factor vector, coercing
## into character vector
```

```
## Warning in bind_rows_(x, .id): Unequal factor levels: coercing to character
```

```
## Warning in bind_rows_(x, .id): binding character and factor vector, coercing
## into character vector

## Warning in bind_rows_(x, .id): binding character and factor vector, coercing
## into character vector
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


|                  &nbsp;                   |  Estimate  | Std..Error |  df   | t.value  |   p    | p_adj  | sig |
|:-----------------------------------------:|:----------:|:----------:|:-----:|:--------:|:------:|:------:|:---:|
|              **(Intercept)**              |  0.07206   |  0.01838   |  107  |  3.921   | 0.0002 | 0.0004 | *** |
|            **typeissue_reply**            |   0.1281   |  0.01474   | 48374 |  8.693   | 0.0001 | 0.0001 | *** |
|              **typepr_post**              | -0.0003754 |  0.01641   | 48463 | -0.02288 |  0.98  |  0.98  |     |
|             **typepr_reply**              |   0.1372   |  0.01463   | 48706 |  9.373   | 0.0001 | 0.0001 | *** |
|         **author_groupnonmember**         |  0.01188   |  0.01876   | 20791 |  0.6333  |  0.53  |  0.78  |     |
| **typeissue_reply:author_groupnonmember** |  -0.02296  |   0.0185   | 49182 |  -1.241  | 0.215  |  0.43  |     |
|   **typepr_post:author_groupnonmember**   | -0.009835  |  0.02385   | 45634 | -0.4124  |  0.68  |  0.78  |     |
|  **typepr_reply:author_groupnonmember**   |  -0.00902  |  0.01987   | 38430 |  -0.454  |  0.65  |  0.78  |     |

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
|                             **member-nonmember**                             |             Main Terms              |  1.195   |  0.232  |  0.4   |     |
|                          **issue_post-issue_reply**                          |             Main Terms              |  -7.306  | 0.0001  | 0.0001 | *** |
|                             **pr_post-pr_reply**                             |             Main Terms              |  -8.605  | 0.0001  | 0.0001 | *** |
|                            **issue_post-pr_post**                            |             Main Terms              |  0.5748  |  0.56   |  0.72  |     |
|                           **issue_reply-pr_reply**                           |             Main Terms              | -0.8242  |  0.41   |  0.6   |     |
|                  **issue_post:member-issue_post:nonmember**                  |      2W: Types x Author Groups      | -0.5261  |   0.6   |  0.74  |     |
|                 **issue_reply:member-issue_reply:nonmember**                 |      2W: Types x Author Groups      |  0.6689  |   0.5   |  0.65  |     |
|                     **pr_post:member-pr_post:nonmember**                     |      2W: Types x Author Groups      | -0.09149 |  0.93   |  0.98  |     |
|                    **pr_reply:member-pr_reply:nonmember**                    |      2W: Types x Author Groups      |  -0.159  |  0.87   |  0.96  |     |
|                   **issue_post:member-issue_reply:member**                   |      2W: Types x Author Groups      |  -5.735  | 0.0001  | 0.0001 | *** |
|                **issue_post:nonmember-issue_reply:nonmember**                |      2W: Types x Author Groups      |  -6.226  | 0.0001  | 0.0001 | *** |
|                      **pr_post:member-pr_reply:member**                      |      2W: Types x Author Groups      |  -7.129  | 0.0001  | 0.0001 | *** |
|                   **pr_post:nonmember-pr_reply:nonmember**                   |      2W: Types x Author Groups      |  -6.523  | 0.0001  | 0.0001 | *** |
|                     **issue_post:member-pr_post:member**                     |      2W: Types x Author Groups      | 0.01599  |  0.99   |  0.99  |     |
|                  **issue_post:nonmember-pr_post:nonmember**                  |      2W: Types x Author Groups      |  0.4775  |  0.63   |  0.76  |     |
|                    **issue_reply:member-pr_reply:member**                    |      2W: Types x Author Groups      | -0.5081  |  0.61   |  0.74  |     |
|                 **issue_reply:nonmember-pr_reply:nonmember**                 |      2W: Types x Author Groups      |  -1.381  |  0.167  |  0.32  |     |
|     **scikit.learn:issue_post:member-scikit.learn:issue_post:nonmember**     | 3W: Types x Author Groups x Project | -0.1794  |  0.86   |  0.96  |     |
|    **scikit.learn:issue_reply:member-scikit.learn:issue_reply:nonmember**    | 3W: Types x Author Groups x Project |  -1.546  |  0.122  |  0.25  |     |
|        **scikit.learn:pr_post:member-scikit.learn:pr_post:nonmember**        | 3W: Types x Author Groups x Project |  -1.239  |  0.215  |  0.38  |     |
|       **scikit.learn:pr_reply:member-scikit.learn:pr_reply:nonmember**       | 3W: Types x Author Groups x Project |  -1.328  |  0.184  |  0.35  |     |
|      **scikit.learn:issue_post:member-scikit.learn:issue_reply:member**      | 3W: Types x Author Groups x Project |  -1.523  |  0.128  |  0.25  |     |
|   **scikit.learn:issue_post:nonmember-scikit.learn:issue_reply:nonmember**   | 3W: Types x Author Groups x Project |  -3.13   |  0.002  | 0.007  | **  |
|         **scikit.learn:pr_post:member-scikit.learn:pr_reply:member**         | 3W: Types x Author Groups x Project |  -6.131  | 0.0001  | 0.0001 | *** |
|      **scikit.learn:pr_post:nonmember-scikit.learn:pr_reply:nonmember**      | 3W: Types x Author Groups x Project |  -5.067  | 0.0001  | 0.0001 | *** |
|        **scikit.learn:issue_post:member-scikit.learn:pr_post:member**        | 3W: Types x Author Groups x Project |  2.393   |  0.017  | 0.058  |  .  |
|     **scikit.learn:issue_post:nonmember-scikit.learn:pr_post:nonmember**     | 3W: Types x Author Groups x Project |   1.71   |  0.087  | 0.205  |     |
|       **scikit.learn:issue_reply:member-scikit.learn:pr_reply:member**       | 3W: Types x Author Groups x Project | -0.9412  |  0.35   |  0.54  |     |
|    **scikit.learn:issue_reply:nonmember-scikit.learn:pr_reply:nonmember**    | 3W: Types x Author Groups x Project | -0.8663  |  0.39   |  0.59  |     |
|     **scikit.image:issue_post:member-scikit.image:issue_post:nonmember**     | 3W: Types x Author Groups x Project |  0.7137  |  0.48   |  0.64  |     |
|    **scikit.image:issue_reply:member-scikit.image:issue_reply:nonmember**    | 3W: Types x Author Groups x Project | -0.0712  |  0.94   |  0.98  |     |
|        **scikit.image:pr_post:member-scikit.image:pr_post:nonmember**        | 3W: Types x Author Groups x Project |  -1.53   |  0.126  |  0.25  |     |
|       **scikit.image:pr_reply:member-scikit.image:pr_reply:nonmember**       | 3W: Types x Author Groups x Project |  -2.26   |  0.024  | 0.077  |  .  |
|      **scikit.image:issue_post:member-scikit.image:issue_reply:member**      | 3W: Types x Author Groups x Project |  -1.603  |  0.109  | 0.228  |     |
|   **scikit.image:issue_post:nonmember-scikit.image:issue_reply:nonmember**   | 3W: Types x Author Groups x Project |  -3.27   |  0.001  | 0.006  | **  |
|         **scikit.image:pr_post:member-scikit.image:pr_reply:member**         | 3W: Types x Author Groups x Project |  2.626   |  0.009  | 0.034  |  *  |
|      **scikit.image:pr_post:nonmember-scikit.image:pr_reply:nonmember**      | 3W: Types x Author Groups x Project |   1.7    |  0.089  | 0.206  |     |
|        **scikit.image:issue_post:member-scikit.image:pr_post:member**        | 3W: Types x Author Groups x Project |  -3.145  |  0.002  | 0.007  | **  |
|     **scikit.image:issue_post:nonmember-scikit.image:pr_post:nonmember**     | 3W: Types x Author Groups x Project |  -5.111  | 0.0001  | 0.0001 | *** |
|       **scikit.image:issue_reply:member-scikit.image:pr_reply:member**       | 3W: Types x Author Groups x Project | -0.3686  |  0.71   |  0.84  |     |
|    **scikit.image:issue_reply:nonmember-scikit.image:pr_reply:nonmember**    | 3W: Types x Author Groups x Project |  -2.409  |  0.016  | 0.058  |  .  |
|       **matplotlib:issue_post:member-matplotlib:issue_post:nonmember**       | 3W: Types x Author Groups x Project |  -1.094  |  0.27   |  0.47  |     |
|      **matplotlib:issue_reply:member-matplotlib:issue_reply:nonmember**      | 3W: Types x Author Groups x Project |  0.8829  |  0.38   |  0.58  |     |
|          **matplotlib:pr_post:member-matplotlib:pr_post:nonmember**          | 3W: Types x Author Groups x Project |  -0.21   |  0.83   |  0.96  |     |
|         **matplotlib:pr_reply:member-matplotlib:pr_reply:nonmember**         | 3W: Types x Author Groups x Project | -0.6907  |  0.49   |  0.64  |     |
|        **matplotlib:issue_post:member-matplotlib:issue_reply:member**        | 3W: Types x Author Groups x Project |  -3.527  | 0.0004  | 0.002  | **  |
|     **matplotlib:issue_post:nonmember-matplotlib:issue_reply:nonmember**     | 3W: Types x Author Groups x Project |  -3.18   |  0.002  | 0.007  | **  |
|           **matplotlib:pr_post:member-matplotlib:pr_reply:member**           | 3W: Types x Author Groups x Project |  -3.215  |  0.001  | 0.006  | **  |
|        **matplotlib:pr_post:nonmember-matplotlib:pr_reply:nonmember**        | 3W: Types x Author Groups x Project |  -1.859  |  0.063  | 0.155  |     |
|          **matplotlib:issue_post:member-matplotlib:pr_post:member**          | 3W: Types x Author Groups x Project |  -2.038  |  0.042  | 0.112  |     |
|       **matplotlib:issue_post:nonmember-matplotlib:pr_post:nonmember**       | 3W: Types x Author Groups x Project |  -1.04   |   0.3   |  0.49  |     |
|         **matplotlib:issue_reply:member-matplotlib:pr_reply:member**         | 3W: Types x Author Groups x Project | -0.7684  |  0.44   |  0.61  |     |
|      **matplotlib:issue_reply:nonmember-matplotlib:pr_reply:nonmember**      | 3W: Types x Author Groups x Project |  -1.982  |  0.048  | 0.122  |     |
|           **mayavi:issue_post:member-mayavi:issue_post:nonmember**           | 3W: Types x Author Groups x Project |  -1.633  |  0.102  | 0.224  |     |
|          **mayavi:issue_reply:member-mayavi:issue_reply:nonmember**          | 3W: Types x Author Groups x Project |  0.1912  |  0.85   |  0.96  |     |
|              **mayavi:pr_post:member-mayavi:pr_post:nonmember**              | 3W: Types x Author Groups x Project | -0.8353  |   0.4   |  0.6   |     |
|             **mayavi:pr_reply:member-mayavi:pr_reply:nonmember**             | 3W: Types x Author Groups x Project |  2.391   |  0.017  | 0.058  |  .  |
|            **mayavi:issue_post:member-mayavi:issue_reply:member**            | 3W: Types x Author Groups x Project |  -1.631  |  0.103  | 0.224  |     |
|         **mayavi:issue_post:nonmember-mayavi:issue_reply:nonmember**         | 3W: Types x Author Groups x Project |  0.1066  |  0.92   |  0.98  |     |
|               **mayavi:pr_post:member-mayavi:pr_reply:member**               | 3W: Types x Author Groups x Project |  -1.382  |  0.167  |  0.32  |     |
|            **mayavi:pr_post:nonmember-mayavi:pr_reply:nonmember**            | 3W: Types x Author Groups x Project |  1.769   |  0.077  | 0.185  |     |
|              **mayavi:issue_post:member-mayavi:pr_post:member**              | 3W: Types x Author Groups x Project | -0.7916  |  0.43   |  0.61  |     |
|           **mayavi:issue_post:nonmember-mayavi:pr_post:nonmember**           | 3W: Types x Author Groups x Project | 0.06433  |  0.95   |  0.98  |     |
|             **mayavi:issue_reply:member-mayavi:pr_reply:member**             | 3W: Types x Author Groups x Project | -0.7471  |  0.46   |  0.62  |     |
|          **mayavi:issue_reply:nonmember-mayavi:pr_reply:nonmember**          | 3W: Types x Author Groups x Project |   2.19   |  0.028  | 0.085  |  .  |
|           **pandas:issue_post:member-pandas:issue_post:nonmember**           | 3W: Types x Author Groups x Project |  -3.161  |  0.002  | 0.007  | **  |
|          **pandas:issue_reply:member-pandas:issue_reply:nonmember**          | 3W: Types x Author Groups x Project | -0.01742 |  0.99   |  0.99  |     |
|              **pandas:pr_post:member-pandas:pr_post:nonmember**              | 3W: Types x Author Groups x Project |  0.1359  |  0.89   |  0.96  |     |
|             **pandas:pr_reply:member-pandas:pr_reply:nonmember**             | 3W: Types x Author Groups x Project | -0.5419  |  0.59   |  0.73  |     |
|            **pandas:issue_post:member-pandas:issue_reply:member**            | 3W: Types x Author Groups x Project |  -4.875  | 0.0001  | 0.0001 | *** |
|         **pandas:issue_post:nonmember-pandas:issue_reply:nonmember**         | 3W: Types x Author Groups x Project |  -2.21   |  0.027  | 0.083  |  .  |
|               **pandas:pr_post:member-pandas:pr_reply:member**               | 3W: Types x Author Groups x Project |  -5.387  | 0.0001  | 0.0001 | *** |
|            **pandas:pr_post:nonmember-pandas:pr_reply:nonmember**            | 3W: Types x Author Groups x Project |  -4.838  | 0.0001  | 0.0001 | *** |
|              **pandas:issue_post:member-pandas:pr_post:member**              | 3W: Types x Author Groups x Project |  0.8212  |  0.41   |  0.6   |     |
|           **pandas:issue_post:nonmember-pandas:pr_post:nonmember**           | 3W: Types x Author Groups x Project |  4.127   | 0.0001  | 0.0002 | *** |
|             **pandas:issue_reply:member-pandas:pr_reply:member**             | 3W: Types x Author Groups x Project |  1.621   |  0.105  | 0.224  |     |
|          **pandas:issue_reply:nonmember-pandas:pr_reply:nonmember**          | 3W: Types x Author Groups x Project |  1.031   |   0.3   |  0.49  |     |
|            **scipy:issue_post:member-scipy:issue_post:nonmember**            | 3W: Types x Author Groups x Project | -0.9651  |  0.33   |  0.53  |     |
|           **scipy:issue_reply:member-scipy:issue_reply:nonmember**           | 3W: Types x Author Groups x Project |   2.06   |  0.039  | 0.109  |     |
|               **scipy:pr_post:member-scipy:pr_post:nonmember**               | 3W: Types x Author Groups x Project | -0.1376  |  0.89   |  0.96  |     |
|              **scipy:pr_reply:member-scipy:pr_reply:nonmember**              | 3W: Types x Author Groups x Project |  1.077   |  0.28   |  0.47  |     |
|             **scipy:issue_post:member-scipy:issue_reply:member**             | 3W: Types x Author Groups x Project |  -5.284  | 0.0001  | 0.0001 | *** |
|          **scipy:issue_post:nonmember-scipy:issue_reply:nonmember**          | 3W: Types x Author Groups x Project |  -5.934  | 0.0001  | 0.0001 | *** |
|                **scipy:pr_post:member-scipy:pr_reply:member**                | 3W: Types x Author Groups x Project |  -5.801  | 0.0001  | 0.0001 | *** |
|             **scipy:pr_post:nonmember-scipy:pr_reply:nonmember**             | 3W: Types x Author Groups x Project |  -3.603  | 0.0003  | 0.002  | **  |
|               **scipy:issue_post:member-scipy:pr_post:member**               | 3W: Types x Author Groups x Project |  -1.62   |  0.105  | 0.224  |     |
|            **scipy:issue_post:nonmember-scipy:pr_post:nonmember**            | 3W: Types x Author Groups x Project |  -1.065  |  0.29   |  0.48  |     |
|              **scipy:issue_reply:member-scipy:pr_reply:member**              | 3W: Types x Author Groups x Project | -0.2513  |   0.8   |  0.93  |     |
|           **scipy:issue_reply:nonmember-scipy:pr_reply:nonmember**           | 3W: Types x Author Groups x Project | -0.7778  |  0.44   |  0.61  |     |
|            **numpy:issue_post:member-numpy:issue_post:nonmember**            | 3W: Types x Author Groups x Project |   2.48   |  0.013  | 0.049  |  *  |
|           **numpy:issue_reply:member-numpy:issue_reply:nonmember**           | 3W: Types x Author Groups x Project |  1.275   |  0.202  |  0.37  |     |
|               **numpy:pr_post:member-numpy:pr_post:nonmember**               | 3W: Types x Author Groups x Project | -0.6212  |  0.53   |  0.69  |     |
|              **numpy:pr_reply:member-numpy:pr_reply:nonmember**              | 3W: Types x Author Groups x Project |  0.7088  |  0.48   |  0.64  |     |
|             **numpy:issue_post:member-numpy:issue_reply:member**             | 3W: Types x Author Groups x Project |  -2.008  |  0.045  | 0.117  |     |
|          **numpy:issue_post:nonmember-numpy:issue_reply:nonmember**          | 3W: Types x Author Groups x Project |  -6.329  | 0.0001  | 0.0001 | *** |
|                **numpy:pr_post:member-numpy:pr_reply:member**                | 3W: Types x Author Groups x Project |  -6.582  | 0.0001  | 0.0001 | *** |
|             **numpy:pr_post:nonmember-numpy:pr_reply:nonmember**             | 3W: Types x Author Groups x Project |  -3.338  |  0.001  | 0.004  | **  |
|               **numpy:issue_post:member-numpy:pr_post:member**               | 3W: Types x Author Groups x Project |  1.266   |  0.206  |  0.37  |     |
|            **numpy:issue_post:nonmember-numpy:pr_post:nonmember**            | 3W: Types x Author Groups x Project |  -1.863  |  0.062  | 0.155  |     |
|              **numpy:issue_reply:member-numpy:pr_reply:member**              | 3W: Types x Author Groups x Project |  -2.336  |  0.02   | 0.065  |  .  |
|           **numpy:issue_reply:nonmember-numpy:pr_reply:nonmember**           | 3W: Types x Author Groups x Project |  -2.139  |  0.032  | 0.094  |  .  |
|   **sphinx.gallery:issue_post:member-sphinx.gallery:issue_post:nonmember**   | 3W: Types x Author Groups x Project | 0.03375  |  0.97   |  0.99  |     |
|  **sphinx.gallery:issue_reply:member-sphinx.gallery:issue_reply:nonmember**  | 3W: Types x Author Groups x Project |  2.219   |  0.026  | 0.083  |  .  |
|      **sphinx.gallery:pr_post:member-sphinx.gallery:pr_post:nonmember**      | 3W: Types x Author Groups x Project | -0.7875  |  0.43   |  0.61  |     |
|     **sphinx.gallery:pr_reply:member-sphinx.gallery:pr_reply:nonmember**     | 3W: Types x Author Groups x Project |  2.888   |  0.004  | 0.016  |  *  |
|    **sphinx.gallery:issue_post:member-sphinx.gallery:issue_reply:member**    | 3W: Types x Author Groups x Project |  -1.266  |  0.205  |  0.37  |     |
| **sphinx.gallery:issue_post:nonmember-sphinx.gallery:issue_reply:nonmember** | 3W: Types x Author Groups x Project | 0.06616  |  0.95   |  0.98  |     |
|       **sphinx.gallery:pr_post:member-sphinx.gallery:pr_reply:member**       | 3W: Types x Author Groups x Project |  -2.113  |  0.035  | 0.098  |  .  |
|    **sphinx.gallery:pr_post:nonmember-sphinx.gallery:pr_reply:nonmember**    | 3W: Types x Author Groups x Project |  0.8431  |   0.4   |  0.6   |     |
|      **sphinx.gallery:issue_post:member-sphinx.gallery:pr_post:member**      | 3W: Types x Author Groups x Project |  0.2011  |  0.84   |  0.96  |     |
|   **sphinx.gallery:issue_post:nonmember-sphinx.gallery:pr_post:nonmember**   | 3W: Types x Author Groups x Project | -0.5579  |  0.58   |  0.72  |     |
|     **sphinx.gallery:issue_reply:member-sphinx.gallery:pr_reply:member**     | 3W: Types x Author Groups x Project |  0.3673  |  0.71   |  0.84  |     |
|  **sphinx.gallery:issue_reply:nonmember-sphinx.gallery:pr_reply:nonmember**  | 3W: Types x Author Groups x Project |  0.1504  |  0.88   |  0.96  |     |

Finally, let's plot these effects.



![**Figure**. Sentiment by contribution type (ticket vs. comment) and community membership at the time of posting (member vs. nonmember).](../../figures/sentiment_analysis/ossc-sentiment_membership_contribution-aggregated-knitr_2019.jpg)


```
## Warning: Removed 1 rows containing missing values (geom_errorbar).

## Warning: Removed 1 rows containing missing values (geom_errorbar).
```

![**Figure**. Sentiment by contribution type (ticket vs. comment) and community membership at the time of posting (member vs. nonmember) for each project.](../../figures/sentiment_analysis/ossc-sentiment_membership_contribution-by_project-knitr_2019.jpg)

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

![](oss_community-language_dynamics-2019_files/figure-html/plot_pr_post_members-1.png)<!-- -->


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

![](oss_community-language_dynamics-2019_files/figure-html/plot_pr_post_nonmembers-1.png)<!-- -->



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

![](oss_community-language_dynamics-2019_files/figure-html/plot_issue_post_members-1.png)<!-- -->


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

![](oss_community-language_dynamics-2019_files/figure-html/plot_issue_post_nonmembers-1.png)<!-- -->



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

![](oss_community-language_dynamics-2019_files/figure-html/plot_pr_reply_members-1.png)<!-- -->


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

![](oss_community-language_dynamics-2019_files/figure-html/plot_pr_reply_nonmembers-1.png)<!-- -->



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

![](oss_community-language_dynamics-2019_files/figure-html/plot_issue_reply_members-1.png)<!-- -->


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

![](oss_community-language_dynamics-2019_files/figure-html/plot_issue_reply_nonmembers-1.png)<!-- -->

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



|                                         &nbsp;                                         | t_stats | p_value | p_adj  | sig |
|:--------------------------------------------------------------------------------------:|:-------:|:-------:|:------:|:---:|
|              **issue_post:member:numpyTRUE-issue_post:member:numpyFALSE**              | 0.02789 |  0.98   |  0.98  |     |
|                 **pr_post:member:numpyTRUE-pr_post:member:numpyFALSE**                 | -2.727  |  0.006  | 0.029  |  *  |
|             **issue_reply:member:numpyTRUE-issue_reply:member:numpyFALSE**             | -3.499  |    0    | 0.004  | **  |
|                **pr_reply:member:numpyTRUE-pr_reply:member:numpyFALSE**                | -0.5297 |   0.6   |  0.81  |     |
|           **issue_post:nonmember:numpyTRUE-issue_post:nonmember:numpyFALSE**           | -4.617  | 0.0001  | 0.0001 | *** |
|              **pr_post:nonmember:numpyTRUE-pr_post:nonmember:numpyFALSE**              | -0.2773 |  0.78   |  0.9   |     |
|          **issue_reply:nonmember:numpyTRUE-issue_reply:nonmember:numpyFALSE**          | -2.951  |  0.003  |  0.02  |  *  |
|             **pr_reply:nonmember:numpyTRUE-pr_reply:nonmember:numpyFALSE**             | -0.2772 |  0.78   |  0.9   |     |
|       **issue_post:member:scikit-learnTRUE-issue_post:member:scikit-learnFALSE**       |  1.755  |  0.079  | 0.211  |     |
|          **pr_post:member:scikit-learnTRUE-pr_post:member:scikit-learnFALSE**          | -1.977  |  0.048  |  0.14  |     |
|      **issue_reply:member:scikit-learnTRUE-issue_reply:member:scikit-learnFALSE**      | -0.6299 |  0.53   |  0.74  |     |
|         **pr_reply:member:scikit-learnTRUE-pr_reply:member:scikit-learnFALSE**         | 0.2209  |  0.82   |  0.9   |     |
|    **issue_post:nonmember:scikit-learnTRUE-issue_post:nonmember:scikit-learnFALSE**    |  2.406  |  0.016  |  0.06  |  .  |
|       **pr_post:nonmember:scikit-learnTRUE-pr_post:nonmember:scikit-learnFALSE**       | -0.169  |  0.87   |  0.92  |     |
|   **issue_reply:nonmember:scikit-learnTRUE-issue_reply:nonmember:scikit-learnFALSE**   |  2.866  |  0.004  | 0.022  |  *  |
|      **pr_reply:nonmember:scikit-learnTRUE-pr_reply:nonmember:scikit-learnFALSE**      |  1.892  |  0.058  | 0.163  |     |
|              **issue_post:member:scipyTRUE-issue_post:member:scipyFALSE**              | -2.109  |  0.035  | 0.112  |     |
|                 **pr_post:member:scipyTRUE-pr_post:member:scipyFALSE**                 | -0.4591 |  0.65   |  0.86  |     |
|             **issue_reply:member:scipyTRUE-issue_reply:member:scipyFALSE**             |  3.753  | 0.0002  | 0.002  | **  |
|                **pr_reply:member:scipyTRUE-pr_reply:member:scipyFALSE**                |  3.802  | 0.0001  | 0.002  | **  |
|           **issue_post:nonmember:scipyTRUE-issue_post:nonmember:scipyFALSE**           | -2.198  |  0.028  | 0.094  |  .  |
|              **pr_post:nonmember:scipyTRUE-pr_post:nonmember:scipyFALSE**              | -0.0376 |  0.97   |  0.98  |     |
|          **issue_reply:nonmember:scipyTRUE-issue_reply:nonmember:scipyFALSE**          |  2.078  |  0.038  | 0.115  |     |
|             **pr_reply:nonmember:scipyTRUE-pr_reply:nonmember:scipyFALSE**             |  1.297  |  0.194  |  0.39  |     |
|             **issue_post:member:mayaviTRUE-issue_post:member:mayaviFALSE**             | -1.584  |  0.113  |  0.26  |     |
|                **pr_post:member:mayaviTRUE-pr_post:member:mayaviFALSE**                | -1.048  |   0.3   |  0.54  |     |
|            **issue_reply:member:mayaviTRUE-issue_reply:member:mayaviFALSE**            | -0.7293 |  0.47   |  0.72  |     |
|               **pr_reply:member:mayaviTRUE-pr_reply:member:mayaviFALSE**               | 0.2414  |  0.81   |  0.9   |     |
|          **issue_post:nonmember:mayaviTRUE-issue_post:nonmember:mayaviFALSE**          | 0.2603  |   0.8   |  0.9   |     |
|             **pr_post:nonmember:mayaviTRUE-pr_post:nonmember:mayaviFALSE**             | 0.1064  |  0.92   |  0.94  |     |
|         **issue_reply:nonmember:mayaviTRUE-issue_reply:nonmember:mayaviFALSE**         | -1.621  |  0.105  |  0.25  |     |
|            **pr_reply:nonmember:mayaviTRUE-pr_reply:nonmember:mayaviFALSE**            | -2.755  |  0.006  | 0.029  |  *  |
|     **issue_post:member:sphinx-galleryTRUE-issue_post:member:sphinx-galleryFALSE**     | 0.2862  |  0.78   |  0.9   |     |
|        **pr_post:member:sphinx-galleryTRUE-pr_post:member:sphinx-galleryFALSE**        | -0.213  |  0.83   |  0.9   |     |
|    **issue_reply:member:sphinx-galleryTRUE-issue_reply:member:sphinx-galleryFALSE**    |  1.535  |  0.125  |  0.27  |     |
|       **pr_reply:member:sphinx-galleryTRUE-pr_reply:member:sphinx-galleryFALSE**       | 0.7253  |  0.47   |  0.72  |     |
|  **issue_post:nonmember:sphinx-galleryTRUE-issue_post:nonmember:sphinx-galleryFALSE**  |  0.394  |  0.69   |  0.9   |     |
|     **pr_post:nonmember:sphinx-galleryTRUE-pr_post:nonmember:sphinx-galleryFALSE**     |  1.128  |  0.26   |  0.5   |     |
| **issue_reply:nonmember:sphinx-galleryTRUE-issue_reply:nonmember:sphinx-galleryFALSE** | -1.055  |  0.29   |  0.54  |     |
|    **pr_reply:nonmember:sphinx-galleryTRUE-pr_reply:nonmember:sphinx-galleryFALSE**    | -2.387  |  0.017  |  0.06  |  .  |
|         **issue_post:member:matplotlibTRUE-issue_post:member:matplotlibFALSE**         | -1.619  |  0.106  |  0.25  |     |
|            **pr_post:member:matplotlibTRUE-pr_post:member:matplotlibFALSE**            |  1.526  |  0.127  |  0.27  |     |
|        **issue_reply:member:matplotlibTRUE-issue_reply:member:matplotlibFALSE**        | -0.7357 |  0.46   |  0.72  |     |
|           **pr_reply:member:matplotlibTRUE-pr_reply:member:matplotlibFALSE**           | -0.1425 |  0.89   |  0.93  |     |
|      **issue_post:nonmember:matplotlibTRUE-issue_post:nonmember:matplotlibFALSE**      | -0.8239 |  0.41   |  0.71  |     |
|         **pr_post:nonmember:matplotlibTRUE-pr_post:nonmember:matplotlibFALSE**         | 0.9449  |  0.34   |  0.61  |     |
|     **issue_reply:nonmember:matplotlibTRUE-issue_reply:nonmember:matplotlibFALSE**     | -1.461  |  0.144  |  0.3   |     |
|        **pr_reply:nonmember:matplotlibTRUE-pr_reply:nonmember:matplotlibFALSE**        | 0.7017  |  0.48   |  0.72  |     |
|       **issue_post:member:scikit-imageTRUE-issue_post:member:scikit-imageFALSE**       | -0.3351 |  0.74   |  0.9   |     |
|          **pr_post:member:scikit-imageTRUE-pr_post:member:scikit-imageFALSE**          |  6.291  | 0.0001  | 0.0001 | *** |
|      **issue_reply:member:scikit-imageTRUE-issue_reply:member:scikit-imageFALSE**      | -0.7925 |  0.43   |  0.72  |     |
|         **pr_reply:member:scikit-imageTRUE-pr_reply:member:scikit-imageFALSE**         | -0.6538 |  0.51   |  0.73  |     |
|    **issue_post:nonmember:scikit-imageTRUE-issue_post:nonmember:scikit-imageFALSE**    | -1.669  |  0.095  | 0.244  |     |
|       **pr_post:nonmember:scikit-imageTRUE-pr_post:nonmember:scikit-imageFALSE**       |  5.283  | 0.0001  | 0.0001 | *** |
|   **issue_reply:nonmember:scikit-imageTRUE-issue_reply:nonmember:scikit-imageFALSE**   |  0.259  |   0.8   |  0.9   |     |
|      **pr_reply:nonmember:scikit-imageTRUE-pr_reply:nonmember:scikit-imageFALSE**      |  2.458  |  0.014  | 0.056  |  .  |
|             **issue_post:member:pandasTRUE-issue_post:member:pandasFALSE**             | -0.7059 |  0.48   |  0.72  |     |
|                **pr_post:member:pandasTRUE-pr_post:member:pandasFALSE**                | -2.867  |  0.004  | 0.022  |  *  |
|            **issue_reply:member:pandasTRUE-issue_reply:member:pandasFALSE**            | -0.6665 |   0.5   |  0.73  |     |
|               **pr_reply:member:pandasTRUE-pr_reply:member:pandasFALSE**               | -4.108  | 0.0001  |   0    | *** |
|          **issue_post:nonmember:pandasTRUE-issue_post:nonmember:pandasFALSE**          |  4.474  | 0.0001  | 0.0001 | *** |
|             **pr_post:nonmember:pandasTRUE-pr_post:nonmember:pandasFALSE**             | -2.616  |  0.009  | 0.038  |  *  |
|         **issue_reply:nonmember:pandasTRUE-issue_reply:nonmember:pandasFALSE**         | 0.2181  |  0.83   |  0.9   |     |
|            **pr_reply:nonmember:pandasTRUE-pr_reply:nonmember:pandasFALSE**            | -3.131  |  0.002  | 0.012  |  *  |

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



| author_group |    type     | grateful_count |   n   |
|:------------:|:-----------:|:--------------:|:-----:|
|    member    | issue_post  |       0        |  845  |
|    member    | issue_post  |       1        |  10   |
|    member    | issue_reply |       0        | 11876 |
|    member    | issue_reply |       1        |  885  |
|    member    | issue_reply |       2        |  17   |
|    member    |   pr_post   |       0        | 3017  |
|    member    |   pr_post   |       1        |  23   |
|    member    |  pr_reply   |       0        | 16047 |
|    member    |  pr_reply   |       1        | 3000  |
|    member    |  pr_reply   |       2        |  63   |
|    member    |  pr_reply   |       3        |   4   |
|    member    |  pr_reply   |       4        |   1   |
|  nonmember   | issue_post  |       0        | 1797  |
|  nonmember   | issue_post  |       1        |  151  |
|  nonmember   | issue_post  |       2        |   7   |
|  nonmember   | issue_reply |       0        | 4845  |
|  nonmember   | issue_reply |       1        |  935  |
|  nonmember   | issue_reply |       2        |  79   |
|  nonmember   | issue_reply |       3        |   7   |
|  nonmember   |   pr_post   |       0        |  910  |
|  nonmember   |   pr_post   |       1        |  19   |
|  nonmember   |   pr_post   |       2        |   1   |
|  nonmember   |  pr_reply   |       0        | 4583  |
|  nonmember   |  pr_reply   |       1        |  508  |
|  nonmember   |  pr_reply   |       2        |  41   |
|  nonmember   |  pr_reply   |       3        |   2   |

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



|                             &nbsp;                              |  Estimate  | Std..Error |  df   | t.value  |   p   | p_adj | sig |
|:---------------------------------------------------------------:|:----------:|:----------:|:-----:|:--------:|:-----:|:-----:|:---:|
|                         **(Intercept)**                         |   0.0684   |  0.02618   | 46684 |  2.613   | 0.009 | 0.192 |     |
|                        **projectmayavi**                        |  -0.1176   |   0.2343   | 31967 |  -0.502  | 0.62  | 0.84  |     |
|                        **projectnumpy**                         |  -0.04548  |  0.03219   | 49606 |  -1.413  | 0.158 | 0.61  |     |
|                        **projectpandas**                        |  -0.03595  |  0.02891   | 47706 |  -1.243  | 0.214 | 0.61  |     |
|                     **projectscikit-image**                     |  -0.04452  |  0.04776   | 49336 | -0.9322  | 0.35  | 0.72  |     |
|                     **projectscikit-learn**                     |  -0.06468  |  0.03203   | 48874 |  -2.02   | 0.043 | 0.39  |     |
|                        **projectscipy**                         |  -0.0546   |  0.03966   | 49582 |  -1.377  | 0.169 | 0.61  |     |
|                    **projectsphinx-gallery**                    |  -0.04789  |  0.07376   | 48066 | -0.6493  | 0.52  | 0.81  |     |
|                    **author_groupnonmember**                    |  -0.03505  |  0.03011   | 42700 |  -1.164  | 0.244 | 0.65  |     |
|                       **typeissue_reply**                       |  0.03685   |  0.02513   | 47731 |  1.466   | 0.143 | 0.61  |     |
|                         **typepr_post**                         | -0.000381  |  0.02584   | 47884 | -0.01474 | 0.99  |   1   |     |
|                        **typepr_reply**                         |  0.06081   |  0.02499   | 47932 |  2.433   | 0.015 | 0.192 |     |
|             **projectmayavi:author_groupnonmember**             |   0.2406   |   0.2383   | 31552 |   1.01   | 0.31  | 0.69  |     |
|             **projectnumpy:author_groupnonmember**              |  0.05673   |   0.0375   | 46467 |  1.513   | 0.13  | 0.61  |     |
|             **projectpandas:author_groupnonmember**             |  0.03329   |  0.03376   | 42888 |  0.9861  | 0.32  | 0.69  |     |
|          **projectscikit-image:author_groupnonmember**          |  0.04165   |  0.05789   | 46920 |  0.7195  | 0.47  | 0.81  |     |
|          **projectscikit-learn:author_groupnonmember**          |   0.1046   |  0.03761   | 44973 |   2.78   | 0.005 | 0.174 |     |
|             **projectscipy:author_groupnonmember**              |  0.07214   |  0.04517   | 46797 |  1.597   | 0.11  | 0.61  |     |
|         **projectsphinx-gallery:author_groupnonmember**         |  0.02839   |  0.09204   | 49460 |  0.3085  | 0.76  | 0.86  |     |
|                **projectmayavi:typeissue_reply**                |   0.217    |   0.2375   | 41919 |  0.9139  | 0.36  | 0.72  |     |
|                **projectnumpy:typeissue_reply**                 | -0.009568  |  0.03168   | 47817 |  -0.302  | 0.76  | 0.86  |     |
|                **projectpandas:typeissue_reply**                | 0.0001293  |   0.0277   | 47717 | 0.004667 |   1   |   1   |     |
|             **projectscikit-image:typeissue_reply**             |  0.02754   |  0.04686   | 46793 |  0.5876  | 0.56  | 0.81  |     |
|             **projectscikit-learn:typeissue_reply**             |  0.01321   |  0.03088   | 47492 |  0.4277  | 0.67  | 0.86  |     |
|                **projectscipy:typeissue_reply**                 |  0.04044   |  0.03916   | 48347 |  1.033   |  0.3  | 0.69  |     |
|            **projectsphinx-gallery:typeissue_reply**            |  0.02787   |   0.0755   | 46834 |  0.3691  | 0.71  | 0.86  |     |
|                  **projectmayavi:typepr_post**                  |   0.1017   |   0.2787   | 44968 |  0.3647  | 0.72  | 0.86  |     |
|                  **projectnumpy:typepr_post**                   |  0.007889  |  0.03368   | 47693 |  0.2342  | 0.82  |  0.9  |     |
|                  **projectpandas:typepr_post**                  |  0.002089  |  0.02891   | 47886 | 0.07228  | 0.94  |   1   |     |
|               **projectscikit-image:typepr_post**               |  0.02084   |  0.04956   | 46957 |  0.4204  | 0.67  | 0.86  |     |
|               **projectscikit-learn:typepr_post**               |  0.02158   |   0.0331   | 47492 |  0.6518  | 0.51  | 0.81  |     |
|                  **projectscipy:typepr_post**                   |  0.02537   |  0.04219   | 48391 |  0.6012  | 0.55  | 0.81  |     |
|              **projectsphinx-gallery:typepr_post**              |  0.04264   |  0.08306   | 46519 |  0.5134  | 0.61  | 0.84  |     |
|                 **projectmayavi:typepr_reply**                  |   0.3203   |   0.2528   | 40500 |  1.267   | 0.205 | 0.61  |     |
|                  **projectnumpy:typepr_reply**                  |  0.03871   |  0.03155   | 47944 |  1.227   | 0.22  | 0.61  |     |
|                 **projectpandas:typepr_reply**                  |  0.03622   |  0.02754   | 47947 |  1.315   | 0.188 | 0.61  |     |
|              **projectscikit-image:typepr_reply**               |  0.03008   |  0.04647   | 46865 |  0.6472  | 0.52  | 0.81  |     |
|              **projectscikit-learn:typepr_reply**               |   0.047    |  0.03063   | 47686 |  1.535   | 0.125 | 0.61  |     |
|                  **projectscipy:typepr_reply**                  |   0.1148   |  0.03896   | 48541 |  2.947   | 0.003 | 0.174 |     |
|             **projectsphinx-gallery:typepr_reply**              |  0.09517   |  0.07511   | 47150 |  1.267   | 0.205 | 0.61  |     |
|            **author_groupnonmember:typeissue_reply**            |  0.07538   |  0.03016   | 49601 |  2.499   | 0.012 | 0.192 |     |
|              **author_groupnonmember:typepr_post**              | 0.00003202 |  0.04085   | 45578 | 0.000784 |   1   |   1   |     |
|             **author_groupnonmember:typepr_reply**              |  0.04933   |  0.03405   | 42636 |  1.449   | 0.147 | 0.61  |     |
|     **projectmayavi:author_groupnonmember:typeissue_reply**     |  -0.3053   |   0.2433   | 41075 |  -1.255  | 0.21  | 0.61  |     |
|     **projectnumpy:author_groupnonmember:typeissue_reply**      |  -0.01136  |  0.03823   | 49563 | -0.2972  | 0.77  | 0.86  |     |
|     **projectpandas:author_groupnonmember:typeissue_reply**     |  -0.02684  |  0.03401   | 49519 | -0.7893  | 0.43  | 0.77  |     |
|  **projectscikit-image:author_groupnonmember:typeissue_reply**  |  -0.01109  |  0.05893   | 49603 | -0.1882  | 0.85  | 0.92  |     |
|  **projectscikit-learn:author_groupnonmember:typeissue_reply**  |  -0.07482  |  0.03801   | 49583 |  -1.969  | 0.049 | 0.39  |     |
|     **projectscipy:author_groupnonmember:typeissue_reply**      |  -0.05068  |   0.0461   | 49566 |  -1.099  | 0.27  | 0.67  |     |
| **projectsphinx-gallery:author_groupnonmember:typeissue_reply** |  -0.05386  |  0.09946   | 48215 | -0.5416  | 0.59  | 0.84  |     |
|       **projectmayavi:author_groupnonmember:typepr_post**       |  -0.2336   |   0.2992   | 43862 | -0.7807  | 0.44  | 0.77  |     |
|       **projectnumpy:author_groupnonmember:typepr_post**        |  -0.01943  |  0.05138   | 46273 | -0.3782  |  0.7  | 0.86  |     |
|       **projectpandas:author_groupnonmember:typepr_post**       |  -0.01439  |   0.0456   | 45840 | -0.3156  | 0.75  | 0.86  |     |
|    **projectscikit-image:author_groupnonmember:typepr_post**    |  -0.04468  |  0.07628   | 47114 | -0.5858  | 0.56  | 0.81  |     |
|    **projectscikit-learn:author_groupnonmember:typepr_post**    |  -0.06228  |  0.05004   | 46879 |  -1.245  | 0.213 | 0.61  |     |
|       **projectscipy:author_groupnonmember:typepr_post**        |  -0.03849  |  0.05889   | 47596 | -0.6536  | 0.51  | 0.81  |     |
|   **projectsphinx-gallery:author_groupnonmember:typepr_post**   |  -0.04241  |   0.1197   | 49133 | -0.3544  | 0.72  | 0.86  |     |
|      **projectmayavi:author_groupnonmember:typepr_reply**       |  -0.5218   |   0.2824   | 41331 |  -1.848  | 0.065 | 0.46  |     |
|       **projectnumpy:author_groupnonmember:typepr_reply**       |  -0.03627  |  0.04279   | 44329 | -0.8476  |  0.4  | 0.75  |     |
|      **projectpandas:author_groupnonmember:typepr_reply**       |   -0.033   |   0.0383   | 41901 | -0.8616  | 0.39  | 0.75  |     |
|   **projectscikit-image:author_groupnonmember:typepr_reply**    | -0.003272  |  0.06322   | 45364 | -0.05176 | 0.96  |   1   |     |
|   **projectscikit-learn:author_groupnonmember:typepr_reply**    |  -0.04342  |  0.04159   | 43476 |  -1.044  |  0.3  | 0.69  |     |
|       **projectscipy:author_groupnonmember:typepr_reply**       |  -0.1063   |  0.05009   | 44693 |  -2.122  | 0.034 | 0.36  |     |
|  **projectsphinx-gallery:author_groupnonmember:typepr_reply**   |  -0.1059   |   0.0966   | 48791 |  -1.096  | 0.27  | 0.67  |     |



![**Figure**. Expressions of gratitude by contribution type (ticket vs. comment) and community membership (member vs. nonmember) at the time of posting.](../../figures/sentiment_analysis/ossc-grateful_membership_contribution-knitr_2019.jpg)

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


|                  &nbsp;                   | Estimate | Std..Error |  df   | t.value |   p    | p_adj  | sig |
|:-----------------------------------------:|:--------:|:----------:|:-----:|:-------:|:------:|:------:|:---:|
|              **(Intercept)**              | 0.01679  |  0.01159   | 14.57 |  1.449  | 0.168  | 0.193  |     |
|         **author_groupnonmember**         | 0.04716  |  0.009245  | 49653 |  5.101  | 0.0001 | 0.0001 | *** |
|            **typeissue_reply**            | 0.04093  |  0.007965  | 49657 |  5.138  | 0.0001 | 0.0001 | *** |
|              **typepr_post**              | 0.000133 |  0.00875   | 49664 | 0.0152  |  0.99  |  0.99  |     |
|             **typepr_reply**              |  0.1036  |  0.007882  | 49658 |  13.15  | 0.0001 | 0.0001 | *** |
| **author_groupnonmember:typeissue_reply** | 0.02933  |   0.0099   | 49661 |  2.963  | 0.003  | 0.004  | **  |
|   **author_groupnonmember:typepr_post**   | -0.04315 |  0.01255   | 49665 | -3.439  | 0.001  | 0.001  | **  |
|  **author_groupnonmember:typepr_reply**   | -0.08151 |  0.009938  | 49650 | -8.202  | 0.0001 | 0.0001 | *** |

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



|                                    &nbsp;                                    |                model                |  t_stats  | p_value | p_adj  | sig |
|:----------------------------------------------------------------------------:|:-----------------------------------:|:---------:|:-------:|:------:|:---:|
|                             **member-nonmember**                             |             Main Terms              |  -1.038   |   0.3   |  0.44  |     |
|                          **issue_post-issue_reply**                          |             Main Terms              |  -2.113   |  0.035  | 0.067  |  .  |
|                             **pr_post-pr_reply**                             |             Main Terms              |  -6.388   | 0.0001  | 0.0001 | *** |
|                            **issue_post-pr_post**                            |             Main Terms              |   2.055   |  0.04   | 0.076  |  .  |
|                           **issue_reply-pr_reply**                           |             Main Terms              |  -2.178   |  0.029  | 0.059  |  .  |
|                  **issue_post:member-issue_post:nonmember**                  |      2W: Types x Author Groups      |  -3.291   |  0.001  | 0.003  | **  |
|                 **issue_reply:member-issue_reply:nonmember**                 |      2W: Types x Author Groups      |  -6.628   | 0.0001  | 0.0001 | *** |
|                     **pr_post:member-pr_post:nonmember**                     |      2W: Types x Author Groups      |  -0.2926  |  0.77   |  0.89  |     |
|                    **pr_reply:member-pr_reply:nonmember**                    |      2W: Types x Author Groups      |   2.963   |  0.003  | 0.007  | **  |
|                   **issue_post:member-issue_reply:member**                   |      2W: Types x Author Groups      |  -3.012   |  0.003  | 0.006  | **  |
|                **issue_post:nonmember-issue_reply:nonmember**                |      2W: Types x Author Groups      |  -5.649   | 0.0001  | 0.0001 | *** |
|                      **pr_post:member-pr_reply:member**                      |      2W: Types x Author Groups      |  -8.724   | 0.0001  | 0.0001 | *** |
|                   **pr_post:nonmember-pr_reply:nonmember**                   |      2W: Types x Author Groups      |  -4.775   | 0.0001  | 0.0001 | *** |
|                     **issue_post:member-pr_post:member**                     |      2W: Types x Author Groups      | -0.008318 |  0.99   |   1    |     |
|                  **issue_post:nonmember-pr_post:nonmember**                  |      2W: Types x Author Groups      |   3.039   |  0.002  | 0.006  | **  |
|                    **issue_reply:member-pr_reply:member**                    |      2W: Types x Author Groups      |  -5.548   | 0.0001  | 0.0001 | *** |
|                 **issue_reply:nonmember-pr_reply:nonmember**                 |      2W: Types x Author Groups      |   4.072   | 0.0001  | 0.0001 | *** |
|     **scikit.learn:issue_post:member-scikit.learn:issue_post:nonmember**     | 3W: Types x Author Groups x Project |  -4.214   | 0.0001  | 0.0001 | *** |
|    **scikit.learn:issue_reply:member-scikit.learn:issue_reply:nonmember**    | 3W: Types x Author Groups x Project |  -8.667   | 0.0001  | 0.0001 | *** |
|        **scikit.learn:pr_post:member-scikit.learn:pr_post:nonmember**        | 3W: Types x Author Groups x Project |  -0.8706  |  0.38   |  0.52  |     |
|       **scikit.learn:pr_reply:member-scikit.learn:pr_reply:nonmember**       | 3W: Types x Author Groups x Project |  -8.443   | 0.0001  | 0.0001 | *** |
|      **scikit.learn:issue_post:member-scikit.learn:issue_reply:member**      | 3W: Types x Author Groups x Project |   -2.63   |  0.008  | 0.018  |  *  |
|   **scikit.learn:issue_post:nonmember-scikit.learn:issue_reply:nonmember**   | 3W: Types x Author Groups x Project |  -1.975   |  0.048  | 0.091  |  .  |
|         **scikit.learn:pr_post:member-scikit.learn:pr_reply:member**         | 3W: Types x Author Groups x Project |   -7.77   | 0.0001  | 0.0001 | *** |
|      **scikit.learn:pr_post:nonmember-scikit.learn:pr_reply:nonmember**      | 3W: Types x Author Groups x Project |  -8.758   | 0.0001  | 0.0001 | *** |
|        **scikit.learn:issue_post:member-scikit.learn:pr_post:member**        | 3W: Types x Author Groups x Project |  -0.2615  |  0.79   |  0.91  |     |
|     **scikit.learn:issue_post:nonmember-scikit.learn:pr_post:nonmember**     | 3W: Types x Author Groups x Project |   3.566   | 0.0004  | 0.001  | **  |
|       **scikit.learn:issue_reply:member-scikit.learn:pr_reply:member**       | 3W: Types x Author Groups x Project |  -8.774   | 0.0001  | 0.0001 | *** |
|    **scikit.learn:issue_reply:nonmember-scikit.learn:pr_reply:nonmember**    | 3W: Types x Author Groups x Project |  -4.899   | 0.0001  | 0.0001 | *** |
|     **scikit.image:issue_post:member-scikit.image:issue_post:nonmember**     | 3W: Types x Author Groups x Project |  -0.9994  |  0.32   |  0.45  |     |
|    **scikit.image:issue_reply:member-scikit.image:issue_reply:nonmember**    | 3W: Types x Author Groups x Project |  -6.349   | 0.0001  | 0.0001 | *** |
|        **scikit.image:pr_post:member-scikit.image:pr_post:nonmember**        | 3W: Types x Author Groups x Project |  0.2132   |  0.83   |  0.94  |     |
|       **scikit.image:pr_reply:member-scikit.image:pr_reply:nonmember**       | 3W: Types x Author Groups x Project |  -4.557   | 0.0001  | 0.0001 | *** |
|      **scikit.image:issue_post:member-scikit.image:issue_reply:member**      | 3W: Types x Author Groups x Project |  -1.464   |  0.143  | 0.219  |     |
|   **scikit.image:issue_post:nonmember-scikit.image:issue_reply:nonmember**   | 3W: Types x Author Groups x Project |   -3.78   | 0.0002  |   0    | *** |
|         **scikit.image:pr_post:member-scikit.image:pr_reply:member**         | 3W: Types x Author Groups x Project |  -4.295   | 0.0001  | 0.0001 | *** |
|      **scikit.image:pr_post:nonmember-scikit.image:pr_reply:nonmember**      | 3W: Types x Author Groups x Project |  -4.253   | 0.0001  | 0.0001 | *** |
|        **scikit.image:issue_post:member-scikit.image:pr_post:member**        | 3W: Types x Author Groups x Project |  -0.2053  |  0.84   |  0.94  |     |
|     **scikit.image:issue_post:nonmember-scikit.image:pr_post:nonmember**     | 3W: Types x Author Groups x Project |   1.031   |   0.3   |  0.44  |     |
|       **scikit.image:issue_reply:member-scikit.image:pr_reply:member**       | 3W: Types x Author Groups x Project |  -2.897   |  0.004  | 0.009  | **  |
|    **scikit.image:issue_reply:nonmember-scikit.image:pr_reply:nonmember**    | 3W: Types x Author Groups x Project |  -0.6113  |  0.54   |  0.68  |     |
|       **matplotlib:issue_post:member-matplotlib:issue_post:nonmember**       | 3W: Types x Author Groups x Project |  -0.7948  |  0.43   |  0.56  |     |
|      **matplotlib:issue_reply:member-matplotlib:issue_reply:nonmember**      | 3W: Types x Author Groups x Project |  -10.28   | 0.0001  | 0.0001 | *** |
|          **matplotlib:pr_post:member-matplotlib:pr_post:nonmember**          | 3W: Types x Author Groups x Project |  -1.001   |  0.32   |  0.45  |     |
|         **matplotlib:pr_reply:member-matplotlib:pr_reply:nonmember**         | 3W: Types x Author Groups x Project |  -3.125   |  0.002  | 0.005  | **  |
|        **matplotlib:issue_post:member-matplotlib:issue_reply:member**        | 3W: Types x Author Groups x Project |  -0.6133  |  0.54   |  0.68  |     |
|     **matplotlib:issue_post:nonmember-matplotlib:issue_reply:nonmember**     | 3W: Types x Author Groups x Project |  -5.714   | 0.0001  | 0.0001 | *** |
|           **matplotlib:pr_post:member-matplotlib:pr_reply:member**           | 3W: Types x Author Groups x Project |  -7.777   | 0.0001  | 0.0001 | *** |
|        **matplotlib:pr_post:nonmember-matplotlib:pr_reply:nonmember**        | 3W: Types x Author Groups x Project |  -2.839   |  0.004  |  0.01  |  *  |
|          **matplotlib:issue_post:member-matplotlib:pr_post:member**          | 3W: Types x Author Groups x Project |  0.9203   |  0.36   |  0.5   |     |
|       **matplotlib:issue_post:nonmember-matplotlib:pr_post:nonmember**       | 3W: Types x Author Groups x Project |  0.6295   |  0.53   |  0.68  |     |
|         **matplotlib:issue_reply:member-matplotlib:pr_reply:member**         | 3W: Types x Author Groups x Project |  -3.724   | 0.0002  | 0.001  | **  |
|      **matplotlib:issue_reply:nonmember-matplotlib:pr_reply:nonmember**      | 3W: Types x Author Groups x Project |   1.538   |  0.124  | 0.195  |     |
|           **mayavi:issue_post:member-mayavi:issue_post:nonmember**           | 3W: Types x Author Groups x Project |  -0.7172  |  0.47   |  0.62  |     |
|          **mayavi:issue_reply:member-mayavi:issue_reply:nonmember**          | 3W: Types x Author Groups x Project |  0.03385  |  0.97   |   1    |     |
|              **mayavi:pr_post:member-mayavi:pr_post:nonmember**              | 3W: Types x Author Groups x Project |     0     |    1    |   1    |     |
|             **mayavi:pr_reply:member-mayavi:pr_reply:nonmember**             | 3W: Types x Author Groups x Project |   1.844   |  0.065  | 0.121  |     |
|            **mayavi:issue_post:member-mayavi:issue_reply:member**            | 3W: Types x Author Groups x Project |  -0.7988  |  0.42   |  0.56  |     |
|         **mayavi:issue_post:nonmember-mayavi:issue_reply:nonmember**         | 3W: Types x Author Groups x Project |  -0.3697  |  0.71   |  0.83  |     |
|               **mayavi:pr_post:member-mayavi:pr_reply:member**               | 3W: Types x Author Groups x Project |  -1.479   |  0.139  | 0.216  |     |
|            **mayavi:pr_post:nonmember-mayavi:pr_reply:nonmember**            | 3W: Types x Author Groups x Project |     0     |    1    |   1    |     |
|              **mayavi:issue_post:member-mayavi:pr_post:member**              | 3W: Types x Author Groups x Project |     0     |    1    |   1    |     |
|           **mayavi:issue_post:nonmember-mayavi:pr_post:nonmember**           | 3W: Types x Author Groups x Project |   1.643   |   0.1   | 0.164  |     |
|             **mayavi:issue_reply:member-mayavi:pr_reply:member**             | 3W: Types x Author Groups x Project |  -0.8623  |  0.39   |  0.52  |     |
|          **mayavi:issue_reply:nonmember-mayavi:pr_reply:nonmember**          | 3W: Types x Author Groups x Project |   1.564   |  0.118  | 0.188  |     |
|           **pandas:issue_post:member-pandas:issue_post:nonmember**           | 3W: Types x Author Groups x Project |  -1.786   |  0.074  | 0.127  |     |
|          **pandas:issue_reply:member-pandas:issue_reply:nonmember**          | 3W: Types x Author Groups x Project |  -9.406   | 0.0001  | 0.0001 | *** |
|              **pandas:pr_post:member-pandas:pr_post:nonmember**              | 3W: Types x Author Groups x Project |  -0.4274  |  0.67   |  0.8   |     |
|             **pandas:pr_reply:member-pandas:pr_reply:nonmember**             | 3W: Types x Author Groups x Project |   19.72   | 0.0001  | 0.0001 | *** |
|            **pandas:issue_post:member-pandas:issue_reply:member**            | 3W: Types x Author Groups x Project |  -3.596   | 0.0003  | 0.001  | **  |
|         **pandas:issue_post:nonmember-pandas:issue_reply:nonmember**         | 3W: Types x Author Groups x Project |  -7.674   | 0.0001  | 0.0001 | *** |
|               **pandas:pr_post:member-pandas:pr_reply:member**               | 3W: Types x Author Groups x Project |  -15.77   | 0.0001  | 0.0001 | *** |
|            **pandas:pr_post:nonmember-pandas:pr_reply:nonmember**            | 3W: Types x Author Groups x Project |  -1.618   |  0.106  |  0.17  |     |
|              **pandas:issue_post:member-pandas:pr_post:member**              | 3W: Types x Author Groups x Project |  0.5894   |  0.56   |  0.68  |     |
|           **pandas:issue_post:nonmember-pandas:pr_post:nonmember**           | 3W: Types x Author Groups x Project |   1.804   |  0.071  | 0.126  |     |
|             **pandas:issue_reply:member-pandas:pr_reply:member**             | 3W: Types x Author Groups x Project |  -16.14   | 0.0001  | 0.0001 | *** |
|          **pandas:issue_reply:nonmember-pandas:pr_reply:nonmember**          | 3W: Types x Author Groups x Project |   12.51   | 0.0001  | 0.0001 | *** |
|            **scipy:issue_post:member-scipy:issue_post:nonmember**            | 3W: Types x Author Groups x Project |   -1.81   |  0.07   | 0.126  |     |
|           **scipy:issue_reply:member-scipy:issue_reply:nonmember**           | 3W: Types x Author Groups x Project |  -6.282   | 0.0001  | 0.0001 | *** |
|               **scipy:pr_post:member-scipy:pr_post:nonmember**               | 3W: Types x Author Groups x Project | -0.08723  |  0.93   |   1    |     |
|              **scipy:pr_reply:member-scipy:pr_reply:nonmember**              | 3W: Types x Author Groups x Project |   2.334   |  0.02   | 0.041  |  *  |
|             **scipy:issue_post:member-scipy:issue_reply:member**             | 3W: Types x Author Groups x Project |  -2.418   |  0.016  | 0.033  |  *  |
|          **scipy:issue_post:nonmember-scipy:issue_reply:nonmember**          | 3W: Types x Author Groups x Project |  -4.808   | 0.0001  | 0.0001 | *** |
|                **scipy:pr_post:member-scipy:pr_reply:member**                | 3W: Types x Author Groups x Project |  -9.918   | 0.0001  | 0.0001 | *** |
|             **scipy:pr_post:nonmember-scipy:pr_reply:nonmember**             | 3W: Types x Author Groups x Project |  -5.584   | 0.0001  | 0.0001 | *** |
|               **scipy:issue_post:member-scipy:pr_post:member**               | 3W: Types x Author Groups x Project |  -0.1073  |  0.92   |   1    |     |
|            **scipy:issue_post:nonmember-scipy:pr_post:nonmember**            | 3W: Types x Author Groups x Project |   2.127   |  0.033  | 0.066  |  .  |
|              **scipy:issue_reply:member-scipy:pr_reply:member**              | 3W: Types x Author Groups x Project |  -11.82   | 0.0001  | 0.0001 | *** |
|           **scipy:issue_reply:nonmember-scipy:pr_reply:nonmember**           | 3W: Types x Author Groups x Project |  0.1109   |  0.91   |   1    |     |
|            **numpy:issue_post:member-numpy:issue_post:nonmember**            | 3W: Types x Author Groups x Project |  -2.692   |  0.007  | 0.016  |  *  |
|           **numpy:issue_reply:member-numpy:issue_reply:nonmember**           | 3W: Types x Author Groups x Project |  -11.62   | 0.0001  | 0.0001 | *** |
|               **numpy:pr_post:member-numpy:pr_post:nonmember**               | 3W: Types x Author Groups x Project |  -0.3722  |  0.71   |  0.83  |     |
|              **numpy:pr_reply:member-numpy:pr_reply:nonmember**              | 3W: Types x Author Groups x Project |   -2.18   |  0.029  | 0.059  |  .  |
|             **numpy:issue_post:member-numpy:issue_reply:member**             | 3W: Types x Author Groups x Project |  -1.688   |  0.092  | 0.154  |     |
|          **numpy:issue_post:nonmember-numpy:issue_reply:nonmember**          | 3W: Types x Author Groups x Project |  -4.442   | 0.0001  | 0.0001 | *** |
|                **numpy:pr_post:member-numpy:pr_reply:member**                | 3W: Types x Author Groups x Project |  -7.781   | 0.0001  | 0.0001 | *** |
|             **numpy:pr_post:nonmember-numpy:pr_reply:nonmember**             | 3W: Types x Author Groups x Project |  -5.051   | 0.0001  | 0.0001 | *** |
|               **numpy:issue_post:member-numpy:pr_post:member**               | 3W: Types x Author Groups x Project |   -0.6    |  0.55   |  0.68  |     |
|            **numpy:issue_post:nonmember-numpy:pr_post:nonmember**            | 3W: Types x Author Groups x Project |   1.814   |  0.07   | 0.126  |     |
|              **numpy:issue_reply:member-numpy:pr_reply:member**              | 3W: Types x Author Groups x Project |  -12.48   | 0.0001  | 0.0001 | *** |
|           **numpy:issue_reply:nonmember-numpy:pr_reply:nonmember**           | 3W: Types x Author Groups x Project |  -0.8884  |  0.37   |  0.52  |     |
|   **sphinx.gallery:issue_post:member-sphinx.gallery:issue_post:nonmember**   | 3W: Types x Author Groups x Project |     0     |    1    |   1    |     |
|  **sphinx.gallery:issue_reply:member-sphinx.gallery:issue_reply:nonmember**  | 3W: Types x Author Groups x Project |  -1.785   |  0.074  | 0.127  |     |
|      **sphinx.gallery:pr_post:member-sphinx.gallery:pr_post:nonmember**      | 3W: Types x Author Groups x Project |     0     |    1    |   1    |     |
|     **sphinx.gallery:pr_reply:member-sphinx.gallery:pr_reply:nonmember**     | 3W: Types x Author Groups x Project |  0.9911   |  0.32   |  0.45  |     |
|    **sphinx.gallery:issue_post:member-sphinx.gallery:issue_reply:member**    | 3W: Types x Author Groups x Project |  -0.4517  |  0.65   |  0.79  |     |
| **sphinx.gallery:issue_post:nonmember-sphinx.gallery:issue_reply:nonmember** | 3W: Types x Author Groups x Project |   -1.67   |  0.095  | 0.158  |     |
|       **sphinx.gallery:pr_post:member-sphinx.gallery:pr_reply:member**       | 3W: Types x Author Groups x Project |  -2.665   |  0.008  | 0.017  |  *  |
|    **sphinx.gallery:pr_post:nonmember-sphinx.gallery:pr_reply:nonmember**    | 3W: Types x Author Groups x Project |  -1.329   |  0.184  |  0.28  |     |
|      **sphinx.gallery:issue_post:member-sphinx.gallery:pr_post:member**      | 3W: Types x Author Groups x Project |     0     |    1    |   1    |     |
|   **sphinx.gallery:issue_post:nonmember-sphinx.gallery:pr_post:nonmember**   | 3W: Types x Author Groups x Project |     0     |    1    |   1    |     |
|     **sphinx.gallery:issue_reply:member-sphinx.gallery:pr_reply:member**     | 3W: Types x Author Groups x Project |  -3.238   |  0.001  | 0.003  | **  |
|  **sphinx.gallery:issue_reply:nonmember-sphinx.gallery:pr_reply:nonmember**  | 3W: Types x Author Groups x Project |  0.4155   |  0.68   |  0.81  |     |

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
                **ticket_family_numeric-0.5**                      -1.495     

                **ticket_family_numeric0.5**                       -1.288     

                      **projectmayavi**                            0.3192     

                      **projectnumpy**                            -0.2234     

                      **projectpandas**                            0.1902     

                   **projectscikit-image**                         0.3803     

                   **projectscikit-learn**                         0.2436     

                      **projectscipy**                            -0.1474     

                  **projectsphinx-gallery**                        1.504      

                        **open_time**                          0.000000004008 

                 **comment_sentiment_mean**                        0.6177     

             **comment_sentiment_max_negative**                    0.168      

               **comment_grateful_cumulative**                    -0.02942    

                   **number_of_comments**                         0.03064     

                  **comment_member_ratio**                        -0.8794     

          **ticket_family_numeric0.5:projectnumpy**                0.5777     

         **ticket_family_numeric0.5:projectpandas**                0.2291     

      **ticket_family_numeric0.5:projectscikit-image**             0.2923     

      **ticket_family_numeric0.5:projectscikit-learn**             0.5647     

          **ticket_family_numeric0.5:projectscipy**                1.243      

     **ticket_family_numeric0.5:projectsphinx-gallery**            11.87      

           **ticket_family_numeric0.5:open_time**              -0.00000005829 

     **ticket_family_numeric0.5:comment_sentiment_mean**            1.21      

 **ticket_family_numeric0.5:comment_sentiment_max_negative**       0.5525     

  **ticket_family_numeric0.5:comment_grateful_cumulative**        -0.1212     

       **ticket_family_numeric0.5:number_of_comments**             0.051      

      **ticket_family_numeric0.5:comment_member_ratio**           0.03848     
------------------------------------------------------------------------------

Table: Table continues below

 
------------------------------------------------------------------------------
                           &nbsp;                                Std. Error   
------------------------------------------------------------- ----------------
                **ticket_family_numeric-0.5**                      0.3282     

                **ticket_family_numeric0.5**                       0.7203     

                      **projectmayavi**                            0.6944     

                      **projectnumpy**                             0.2917     

                      **projectpandas**                            0.2584     

                   **projectscikit-image**                         0.4238     

                   **projectscikit-learn**                         0.2896     

                      **projectscipy**                             0.3294     

                  **projectsphinx-gallery**                        0.7147     

                        **open_time**                          0.000000007731 

                 **comment_sentiment_mean**                        0.3194     

             **comment_sentiment_max_negative**                     0.79      

               **comment_grateful_cumulative**                    0.08212     

                   **number_of_comments**                         0.01679     

                  **comment_member_ratio**                         0.2903     

          **ticket_family_numeric0.5:projectnumpy**                0.6721     

         **ticket_family_numeric0.5:projectpandas**                0.6649     

      **ticket_family_numeric0.5:projectscikit-image**             0.904      

      **ticket_family_numeric0.5:projectscikit-learn**             0.6642     

          **ticket_family_numeric0.5:projectscipy**                0.7101     

     **ticket_family_numeric0.5:projectsphinx-gallery**             315       

           **ticket_family_numeric0.5:open_time**              0.00000003304  

     **ticket_family_numeric0.5:comment_sentiment_mean**           0.7732     

 **ticket_family_numeric0.5:comment_sentiment_max_negative**       1.231      

  **ticket_family_numeric0.5:comment_grateful_cumulative**         0.1568     

       **ticket_family_numeric0.5:number_of_comments**            0.03611     

      **ticket_family_numeric0.5:comment_member_ratio**            0.6035     
------------------------------------------------------------------------------

Table: Table continues below

 
-----------------------------------------------------------------------
                           &nbsp;                              z value 
------------------------------------------------------------- ---------
                **ticket_family_numeric-0.5**                  -4.556  

                **ticket_family_numeric0.5**                   -1.788  

                      **projectmayavi**                        0.4597  

                      **projectnumpy**                         -0.7657 

                      **projectpandas**                        0.7363  

                   **projectscikit-image**                     0.8973  

                   **projectscikit-learn**                     0.8412  

                      **projectscipy**                         -0.4474 

                  **projectsphinx-gallery**                     2.104  

                        **open_time**                          0.5184  

                 **comment_sentiment_mean**                     1.934  

             **comment_sentiment_max_negative**                0.2127  

               **comment_grateful_cumulative**                 -0.3582 

                   **number_of_comments**                       1.825  

                  **comment_member_ratio**                     -3.029  

          **ticket_family_numeric0.5:projectnumpy**            0.8595  

         **ticket_family_numeric0.5:projectpandas**            0.3445  

      **ticket_family_numeric0.5:projectscikit-image**         0.3233  

      **ticket_family_numeric0.5:projectscikit-learn**         0.8501  

          **ticket_family_numeric0.5:projectscipy**             1.751  

     **ticket_family_numeric0.5:projectsphinx-gallery**        0.0377  

           **ticket_family_numeric0.5:open_time**              -1.764  

     **ticket_family_numeric0.5:comment_sentiment_mean**        1.564  

 **ticket_family_numeric0.5:comment_sentiment_max_negative**   0.4488  

  **ticket_family_numeric0.5:comment_grateful_cumulative**     -0.7725 

       **ticket_family_numeric0.5:number_of_comments**          1.413  

      **ticket_family_numeric0.5:comment_member_ratio**        0.06377 
-----------------------------------------------------------------------

Table: Table continues below

 
---------------------------------------------------------------------------
                           &nbsp;                               Pr(>|z|)   
------------------------------------------------------------- -------------
                **ticket_family_numeric-0.5**                  0.000005224 

                **ticket_family_numeric0.5**                     0.0738    

                      **projectmayavi**                          0.6458    

                      **projectnumpy**                           0.4438    

                      **projectpandas**                          0.4615    

                   **projectscikit-image**                       0.3695    

                   **projectscikit-learn**                       0.4003    

                      **projectscipy**                           0.6546    

                  **projectsphinx-gallery**                      0.03538   

                        **open_time**                            0.6042    

                 **comment_sentiment_mean**                      0.05314   

             **comment_sentiment_max_negative**                  0.8316    

               **comment_grateful_cumulative**                   0.7202    

                   **number_of_comments**                        0.06806   

                  **comment_member_ratio**                      0.002451   

          **ticket_family_numeric0.5:projectnumpy**              0.3901    

         **ticket_family_numeric0.5:projectpandas**              0.7305    

      **ticket_family_numeric0.5:projectscikit-image**           0.7464    

      **ticket_family_numeric0.5:projectscikit-learn**           0.3953    

          **ticket_family_numeric0.5:projectscipy**              0.08001   

     **ticket_family_numeric0.5:projectsphinx-gallery**          0.9699    

           **ticket_family_numeric0.5:open_time**                0.07773   

     **ticket_family_numeric0.5:comment_sentiment_mean**         0.1177    

 **ticket_family_numeric0.5:comment_sentiment_max_negative**     0.6535    

  **ticket_family_numeric0.5:comment_grateful_cumulative**       0.4398    

       **ticket_family_numeric0.5:number_of_comments**           0.1578    

      **ticket_family_numeric0.5:comment_member_ratio**          0.9492    
---------------------------------------------------------------------------


(Dispersion parameter for  binomial  family taken to be  1 )


-------------------- ---------------------------
   Null deviance:     2290  on 1652  degrees of 
                               freedom          

 Residual deviance:   1537  on 1625  degrees of 
                               freedom          
-------------------- ---------------------------






![**Figure**. Whether a first-time ticket creator will open a second ticket by commenters' expressions of gratitude and responsiveness.](../../figures/sentiment_analysis/ossc-retention_emotion-by_project-knitr_2019.jpg)

***

