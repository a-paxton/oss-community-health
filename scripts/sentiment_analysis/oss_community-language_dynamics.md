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
**posts**-related data (sometimes also referred to as *tickets*) and 
derived variables from scraped GitHub data.
* `../../data/analysis_data/sentiment_frame_comments-for_r.csv`: Contains
cleaned **comments**-related data and derived variables from scraped GitHub
data.
* `./utils/ossc-libraries_and_functions.r`: Loads in necessary libraries and
creates new functions for our analyses.
* `./utils/data-loading.R`: loads functions related to data loading and
preprocessing.

**Code written by**: A. Paxton (University of Connecticut) & N. Varoquaux
(CNRS)

**Date last compiled**:  2020-02-21 20:50:34



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
# select the dataset we'll be working on
tickets_frame = loading_tickets_data(dataset="original")
comments_frame = loading_comments_data(dataset="original")
```

***

## Basic summary stats

The data have been largely cleaned by the time we load them. 
Let's take a look at some basic patterns in the aggregate and
broken down by specific projects.




| ticket_family | unique_tickets | unique_comments |
|:-------------:|:--------------:|:---------------:|
|     issue     |     32133      |     185529      |
|      pr       |     36538      |     251792      |



|    project     | ticket_family | unique_tickets | unique_comments |
|:--------------:|:-------------:|:--------------:|:---------------:|
|   matplotlib   |     issue     |      4819      |      28904      |
|   matplotlib   |      pr       |      7385      |      36688      |
|     mayavi     |     issue     |      440       |      1459       |
|     mayavi     |      pr       |      290       |       645       |
|     numpy      |     issue     |      4467      |      27720      |
|     numpy      |      pr       |      5554      |      33253      |
|     pandas     |     issue     |     12991      |      64587      |
|     pandas     |      pr       |     10248      |      67902      |
|  scikit-image  |     issue     |      1174      |      7240       |
|  scikit-image  |      pr       |      2103      |      15120      |
|  scikit-learn  |     issue     |      5205      |      37783      |
|  scikit-learn  |      pr       |      6444      |      70147      |
|     scipy      |     issue     |      2847      |      16762      |
|     scipy      |      pr       |      4295      |      26205      |
| sphinx-gallery |     issue     |      190       |      1074       |
| sphinx-gallery |      pr       |      219       |      1832       |

Our dataset includes 8 unique projects. The dataset has
total of 32133 unique posted issues, with a mean of 
4016.625 posted issues per project. It also includes a total of 
36538 unique posted pull requests, with a mean of 
4567.25 posted pull requests per project.

On these contributions, the dataset includes
185529 unique comments on issues and 
251792 unique comments on pull requests. This includes an average of
23191.125 comments on issues per project and an average of 
31474 
comments on pull requests per project.

In total, we have 15559 unique commenters,
14147 unique post creators, and
19429 overall unique users.

***

# Data analysis

***

## Model Series 1: Sentiment analysis

***

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



***

### Model 1.1: Do different kinds of activities materially differ in emotion?

First, we build a series of linear mixed-effects models with one term included
in each model (either main term or interaction term). We then use the estimates
from those models to perform *t*-tests to investigate how different levels of
the effects differ from one another (and not just from the model-level 
intercept).

Projects here are random effects, but the rest of the model is the same as 
before. This allows us to do pairwise testing of main and interaction terms,
along with better exploring inter-project variability.

#### Model 1.1a: Does sentiment vary significantly by community membership?

First, look at whether there are differences in sentiment between author 
groups.


```r
# do members and nonmembers materially differ in emotion?
fixed_creators_v_commenters_emotion = lmer(
  compound_emotion ~ 0 + author_group + (1 | author_name) + (1 | project),
  data=sentiment_frame,
  REML=FALSE)
```

Run *t*-tests among levels and prepare for the Model 1.1 table later.


```r
# convert Model 1.1a output to dataframe
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


```r
dir.create("results/models", showWarnings=FALSE)
write.table(coefficients_and_se,
            file="results/models/model-1.1b1.tsv",
            sep="\t")
```

#### Model 1.1b: Does sentiment vary significantly across activity types?

Now, look at whether there are differences in sentiment between activity
types.


```r
# do posts and comments materially differ in emotion?
fixed_types_emotion = lmer(
  compound_emotion ~ 0 + type + (1 | author_name) + (1 | project),
  data=sentiment_frame,
  REML=FALSE)
```

Run *t*-tests among levels and prepare for the Model 1.1 table later.


```r
# convert Model 1.1b output to dataframe
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


```r
write.table(coefficients_and_se,
            file="results/models/model-1.1b2.tsv",
            sep="\t")
```


#### Model 1.1c: Does sentiment vary significantly across community memberships and activity types?

Finally, let's look at the interaction between membership and activity.


```r
# does emotion differ by the interaction between activity and authorship group?
community_contribution_emotion = lmer(
  compound_emotion ~ 0 + type:author_group + (1 | author_name) + (1 | project),
  data=sentiment_frame,
  REML=FALSE)
```

Run *t*-tests among levels and prepare for the Model 1.1 table later.


```r
# convert Model 1.1c output to dataframe
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
  "issue_post:member-issue_post:nonmember",     # activity static (issue posts); membership varies (members v. nonmembers)
  "issue_reply:member-issue_reply:nonmember",   # activity static (issue replies); membership varies (members v. nonmembers)
  "pr_post:member-pr_post:nonmember",           # activity static (PR posts); membership varies (members v. nonmembers)
  "pr_reply:member-pr_reply:nonmember",         # activity static (PR replies); membership varies (members v. nonmembers)
  "issue_post:member-issue_reply:member",       # activity varies (issue posts vs. issue replies); membership static (members)
  "issue_post:nonmember-issue_reply:nonmember", # activity varies (issue posts vs. issue replies); membership static (nonmembers)
  "pr_post:member-pr_reply:member",             # activity varies (PR posts vs. PR replies); membership static (members)
  "pr_post:nonmember-pr_reply:nonmember",       # activity varies (PR posts vs. PR replies); membership static (nonmembers)
  "issue_post:member-pr_post:member",           # activity varies (issue posts vs. PR posts); membership static (members)
  "issue_post:nonmember-pr_post:nonmember",     # activity varies (issue posts vs. PR posts); membership static (nonmembers)
  "issue_reply:member-pr_reply:member",         # activity varies (issue replies vs. PR replies); membership static (members)
  "issue_reply:nonmember-pr_reply:nonmember")   # activity varies (issue replies vs. PR replies); membership static (nonmembers)
types_author_groups_tests = compute_t_statistics(
  means, se,
  contrasts)
types_author_groups_tests[, "p_value"] = compute_p_value_from_t_stats(
  types_author_groups_tests$"t_stats")
```


```r
write.table(coefficients_and_se,
            file="results/models/model-1.1b3.tsv",
            sep="\t")
```


#### Model 1.1d : Do different kinds of activities differ in emotion by projects?

Now adding projects into the mix to understand how the previous analysis
varies across projects.


```r
# do posts and comments materially differ in emotion by projects?
creators_v_commenters_emotion_by_project = lmer(
  compound_emotion ~ 0 + project:type:author_group + (1 | author_name),
  data = sentiment_frame,
  REML = FALSE)
```

```
## Warning in checkConv(attr(opt, "derivs"), opt$par, ctrl =
## control$checkConv, : Model failed to converge with max|grad| = 0.00294682
## (tol = 0.002, component 1)
```

Run *t*-tests among levels and prepare for the Model 1.1 table later.


```r
# convert Model 1.1d output to dataframe
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
# (note: ordering of contrasts within each project is identical to Model 1.1c)
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


```r
write.table(coefficients_and_se,
            file="results/models/model-1.1c.tsv",
            sep="\t")
```

#### Overall results

Now we bring together all analyses from Model 1.1.


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
|                             **member-nonmember**                             |             Main Terms              |  -0.1151  |  0.91   |  0.94  |     |
|                          **issue_post-issue_reply**                          |             Main Terms              |  -9.671   | 0.0001  | 0.0001 | *** |
|                             **pr_post-pr_reply**                             |             Main Terms              |  -12.53   | 0.0001  | 0.0001 | *** |
|                            **issue_post-pr_post**                            |             Main Terms              |  -0.692   |  0.49   |  0.59  |     |
|                           **issue_reply-pr_reply**                           |             Main Terms              |   -3.66   | 0.0003  | 0.001  | **  |
|                  **issue_post:member-issue_post:nonmember**                  |      2W: Types x Author Groups      |  -0.7685  |  0.44   |  0.55  |     |
|                 **issue_reply:member-issue_reply:nonmember**                 |      2W: Types x Author Groups      |  -2.489   |  0.013  | 0.024  |  *  |
|                     **pr_post:member-pr_post:nonmember**                     |      2W: Types x Author Groups      |  -2.791   |  0.005  |  0.01  |  *  |
|                    **pr_reply:member-pr_reply:nonmember**                    |      2W: Types x Author Groups      |  -0.5611  |  0.57   |  0.67  |     |
|                   **issue_post:member-issue_reply:member**                   |      2W: Types x Author Groups      |  -7.957   | 0.0001  | 0.0001 | *** |
|                **issue_post:nonmember-issue_reply:nonmember**                |      2W: Types x Author Groups      |  -10.13   | 0.0001  | 0.0001 | *** |
|                      **pr_post:member-pr_reply:member**                      |      2W: Types x Author Groups      |   -11.9   | 0.0001  | 0.0001 | *** |
|                   **pr_post:nonmember-pr_reply:nonmember**                   |      2W: Types x Author Groups      |  -9.623   | 0.0001  | 0.0001 | *** |
|                     **issue_post:member-pr_post:member**                     |      2W: Types x Author Groups      |  0.2321   |  0.82   |  0.88  |     |
|                  **issue_post:nonmember-pr_post:nonmember**                  |      2W: Types x Author Groups      |  -1.828   |  0.068  | 0.105  |     |
|                    **issue_reply:member-pr_reply:member**                    |      2W: Types x Author Groups      |  -3.625   | 0.0003  | 0.001  | **  |
|                 **issue_reply:nonmember-pr_reply:nonmember**                 |      2W: Types x Author Groups      |  -1.797   |  0.072  |  0.11  |     |
|     **scikit.learn:issue_post:member-scikit.learn:issue_post:nonmember**     | 3W: Types x Author Groups x Project |  -0.7117  |  0.48   |  0.58  |     |
|    **scikit.learn:issue_reply:member-scikit.learn:issue_reply:nonmember**    | 3W: Types x Author Groups x Project |  -3.612   | 0.0003  | 0.001  | **  |
|        **scikit.learn:pr_post:member-scikit.learn:pr_post:nonmember**        | 3W: Types x Author Groups x Project | -0.01136  |  0.99   |  0.99  |     |
|       **scikit.learn:pr_reply:member-scikit.learn:pr_reply:nonmember**       | 3W: Types x Author Groups x Project |  -0.8423  |   0.4   |  0.5   |     |
|      **scikit.learn:issue_post:member-scikit.learn:issue_reply:member**      | 3W: Types x Author Groups x Project |  -8.913   | 0.0001  | 0.0001 | *** |
|   **scikit.learn:issue_post:nonmember-scikit.learn:issue_reply:nonmember**   | 3W: Types x Author Groups x Project |  -12.54   | 0.0001  | 0.0001 | *** |
|         **scikit.learn:pr_post:member-scikit.learn:pr_reply:member**         | 3W: Types x Author Groups x Project |  -12.63   | 0.0001  | 0.0001 | *** |
|      **scikit.learn:pr_post:nonmember-scikit.learn:pr_reply:nonmember**      | 3W: Types x Author Groups x Project |  -13.35   | 0.0001  | 0.0001 | *** |
|        **scikit.learn:issue_post:member-scikit.learn:pr_post:member**        | 3W: Types x Author Groups x Project |  -1.877   |  0.06   | 0.095  |  .  |
|     **scikit.learn:issue_post:nonmember-scikit.learn:pr_post:nonmember**     | 3W: Types x Author Groups x Project |  -1.344   |  0.179  |  0.25  |     |
|       **scikit.learn:issue_reply:member-scikit.learn:pr_reply:member**       | 3W: Types x Author Groups x Project |  -6.375   | 0.0001  | 0.0001 | *** |
|    **scikit.learn:issue_reply:nonmember-scikit.learn:pr_reply:nonmember**    | 3W: Types x Author Groups x Project |  -3.797   | 0.0001  | 0.0004 | *** |
|     **scikit.image:issue_post:member-scikit.image:issue_post:nonmember**     | 3W: Types x Author Groups x Project |  -1.315   |  0.189  |  0.26  |     |
|    **scikit.image:issue_reply:member-scikit.image:issue_reply:nonmember**    | 3W: Types x Author Groups x Project |  -1.323   |  0.186  |  0.26  |     |
|        **scikit.image:pr_post:member-scikit.image:pr_post:nonmember**        | 3W: Types x Author Groups x Project |   -7.07   | 0.0001  | 0.0001 | *** |
|       **scikit.image:pr_reply:member-scikit.image:pr_reply:nonmember**       | 3W: Types x Author Groups x Project | -0.009377 |  0.99   |  0.99  |     |
|      **scikit.image:issue_post:member-scikit.image:issue_reply:member**      | 3W: Types x Author Groups x Project |  -7.624   | 0.0001  | 0.0001 | *** |
|   **scikit.image:issue_post:nonmember-scikit.image:issue_reply:nonmember**   | 3W: Types x Author Groups x Project |  -7.252   | 0.0001  | 0.0001 | *** |
|         **scikit.image:pr_post:member-scikit.image:pr_reply:member**         | 3W: Types x Author Groups x Project |  -8.901   | 0.0001  | 0.0001 | *** |
|      **scikit.image:pr_post:nonmember-scikit.image:pr_reply:nonmember**      | 3W: Types x Author Groups x Project |  0.6255   |  0.53   |  0.64  |     |
|        **scikit.image:issue_post:member-scikit.image:pr_post:member**        | 3W: Types x Author Groups x Project |  -3.255   |  0.001  | 0.002  | **  |
|     **scikit.image:issue_post:nonmember-scikit.image:pr_post:nonmember**     | 3W: Types x Author Groups x Project |  -7.981   | 0.0001  | 0.0001 | *** |
|       **scikit.image:issue_reply:member-scikit.image:pr_reply:member**       | 3W: Types x Author Groups x Project |  -4.003   | 0.0001  | 0.0002 | *** |
|    **scikit.image:issue_reply:nonmember-scikit.image:pr_reply:nonmember**    | 3W: Types x Author Groups x Project |  -2.137   |  0.033  | 0.056  |  .  |
|       **matplotlib:issue_post:member-matplotlib:issue_post:nonmember**       | 3W: Types x Author Groups x Project |  -0.9334  |  0.35   |  0.45  |     |
|      **matplotlib:issue_reply:member-matplotlib:issue_reply:nonmember**      | 3W: Types x Author Groups x Project |  -1.965   |  0.05   |  0.08  |  .  |
|          **matplotlib:pr_post:member-matplotlib:pr_post:nonmember**          | 3W: Types x Author Groups x Project |  -0.9281  |  0.35   |  0.45  |     |
|         **matplotlib:pr_reply:member-matplotlib:pr_reply:nonmember**         | 3W: Types x Author Groups x Project |  -1.746   |  0.081  | 0.122  |     |
|        **matplotlib:issue_post:member-matplotlib:issue_reply:member**        | 3W: Types x Author Groups x Project |  -7.369   | 0.0001  | 0.0001 | *** |
|     **matplotlib:issue_post:nonmember-matplotlib:issue_reply:nonmember**     | 3W: Types x Author Groups x Project |  -9.991   | 0.0001  | 0.0001 | *** |
|           **matplotlib:pr_post:member-matplotlib:pr_reply:member**           | 3W: Types x Author Groups x Project |  -11.45   | 0.0001  | 0.0001 | *** |
|        **matplotlib:pr_post:nonmember-matplotlib:pr_reply:nonmember**        | 3W: Types x Author Groups x Project |  -8.945   | 0.0001  | 0.0001 | *** |
|          **matplotlib:issue_post:member-matplotlib:pr_post:member**          | 3W: Types x Author Groups x Project |  -0.5556  |  0.58   |  0.67  |     |
|       **matplotlib:issue_post:nonmember-matplotlib:pr_post:nonmember**       | 3W: Types x Author Groups x Project |  -0.5169  |   0.6   |  0.69  |     |
|         **matplotlib:issue_reply:member-matplotlib:pr_reply:member**         | 3W: Types x Author Groups x Project |  -2.933   |  0.003  | 0.007  | **  |
|      **matplotlib:issue_reply:nonmember-matplotlib:pr_reply:nonmember**      | 3W: Types x Author Groups x Project |  -2.713   |  0.007  | 0.013  |  *  |
|           **mayavi:issue_post:member-mayavi:issue_post:nonmember**           | 3W: Types x Author Groups x Project |  -1.568   |  0.117  | 0.169  |     |
|          **mayavi:issue_reply:member-mayavi:issue_reply:nonmember**          | 3W: Types x Author Groups x Project |  -1.406   |  0.16   | 0.229  |     |
|              **mayavi:pr_post:member-mayavi:pr_post:nonmember**              | 3W: Types x Author Groups x Project |  -0.5197  |   0.6   |  0.69  |     |
|             **mayavi:pr_reply:member-mayavi:pr_reply:nonmember**             | 3W: Types x Author Groups x Project |  -2.075   |  0.038  | 0.063  |  .  |
|            **mayavi:issue_post:member-mayavi:issue_reply:member**            | 3W: Types x Author Groups x Project |  -1.882   |  0.06   | 0.095  |  .  |
|         **mayavi:issue_post:nonmember-mayavi:issue_reply:nonmember**         | 3W: Types x Author Groups x Project |   -2.89   |  0.004  | 0.008  | **  |
|               **mayavi:pr_post:member-mayavi:pr_reply:member**               | 3W: Types x Author Groups x Project |  -2.279   |  0.023  | 0.041  |  *  |
|            **mayavi:pr_post:nonmember-mayavi:pr_reply:nonmember**            | 3W: Types x Author Groups x Project |  -3.404   |  0.001  | 0.002  | **  |
|              **mayavi:issue_post:member-mayavi:pr_post:member**              | 3W: Types x Author Groups x Project | -0.06937  |  0.94   |  0.96  |     |
|           **mayavi:issue_post:nonmember-mayavi:pr_post:nonmember**           | 3W: Types x Author Groups x Project |   1.071   |  0.28   |  0.38  |     |
|             **mayavi:issue_reply:member-mayavi:pr_reply:member**             | 3W: Types x Author Groups x Project |  -0.1931  |  0.85   |  0.9   |     |
|          **mayavi:issue_reply:nonmember-mayavi:pr_reply:nonmember**          | 3W: Types x Author Groups x Project |   -1.57   |  0.116  | 0.169  |     |
|           **pandas:issue_post:member-pandas:issue_post:nonmember**           | 3W: Types x Author Groups x Project |  -1.052   |  0.29   |  0.38  |     |
|          **pandas:issue_reply:member-pandas:issue_reply:nonmember**          | 3W: Types x Author Groups x Project |  -5.483   | 0.0001  | 0.0001 | *** |
|              **pandas:pr_post:member-pandas:pr_post:nonmember**              | 3W: Types x Author Groups x Project |   -4.7    | 0.0001  | 0.0001 | *** |
|             **pandas:pr_reply:member-pandas:pr_reply:nonmember**             | 3W: Types x Author Groups x Project |   1.397   |  0.162  | 0.229  |     |
|            **pandas:issue_post:member-pandas:issue_reply:member**            | 3W: Types x Author Groups x Project |  -9.886   | 0.0001  | 0.0001 | *** |
|         **pandas:issue_post:nonmember-pandas:issue_reply:nonmember**         | 3W: Types x Author Groups x Project |  -15.06   | 0.0001  | 0.0001 | *** |
|               **pandas:pr_post:member-pandas:pr_reply:member**               | 3W: Types x Author Groups x Project |  -18.35   | 0.0001  | 0.0001 | *** |
|            **pandas:pr_post:nonmember-pandas:pr_reply:nonmember**            | 3W: Types x Author Groups x Project |   -9.05   | 0.0001  | 0.0001 | *** |
|              **pandas:issue_post:member-pandas:pr_post:member**              | 3W: Types x Author Groups x Project |   4.587   | 0.0001  | 0.0001 | *** |
|           **pandas:issue_post:nonmember-pandas:pr_post:nonmember**           | 3W: Types x Author Groups x Project |  0.3137   |  0.75   |  0.84  |     |
|             **pandas:issue_reply:member-pandas:pr_reply:member**             | 3W: Types x Author Groups x Project |  -3.839   | 0.0001  | 0.0003 | *** |
|          **pandas:issue_reply:nonmember-pandas:pr_reply:nonmember**          | 3W: Types x Author Groups x Project |   2.691   |  0.007  | 0.014  |  *  |
|            **scipy:issue_post:member-scipy:issue_post:nonmember**            | 3W: Types x Author Groups x Project |  -3.035   |  0.002  | 0.005  | **  |
|           **scipy:issue_reply:member-scipy:issue_reply:nonmember**           | 3W: Types x Author Groups x Project |  -5.669   | 0.0001  | 0.0001 | *** |
|               **scipy:pr_post:member-scipy:pr_post:nonmember**               | 3W: Types x Author Groups x Project |  -3.921   | 0.0001  | 0.0002 | *** |
|              **scipy:pr_reply:member-scipy:pr_reply:nonmember**              | 3W: Types x Author Groups x Project |  -2.119   |  0.034  | 0.058  |  .  |
|             **scipy:issue_post:member-scipy:issue_reply:member**             | 3W: Types x Author Groups x Project |   -8.79   | 0.0001  | 0.0001 | *** |
|          **scipy:issue_post:nonmember-scipy:issue_reply:nonmember**          | 3W: Types x Author Groups x Project |  -11.83   | 0.0001  | 0.0001 | *** |
|                **scipy:pr_post:member-scipy:pr_reply:member**                | 3W: Types x Author Groups x Project |   -16.6   | 0.0001  | 0.0001 | *** |
|             **scipy:pr_post:nonmember-scipy:pr_reply:nonmember**             | 3W: Types x Author Groups x Project |  -10.36   | 0.0001  | 0.0001 | *** |
|               **scipy:issue_post:member-scipy:pr_post:member**               | 3W: Types x Author Groups x Project |  -2.263   |  0.024  | 0.042  |  *  |
|            **scipy:issue_post:nonmember-scipy:pr_post:nonmember**            | 3W: Types x Author Groups x Project |  -2.847   |  0.004  | 0.009  | **  |
|              **scipy:issue_reply:member-scipy:pr_reply:member**              | 3W: Types x Author Groups x Project |  -9.017   | 0.0001  | 0.0001 | *** |
|           **scipy:issue_reply:nonmember-scipy:pr_reply:nonmember**           | 3W: Types x Author Groups x Project |  -4.262   | 0.0001  | 0.0001 | *** |
|            **numpy:issue_post:member-numpy:issue_post:nonmember**            | 3W: Types x Author Groups x Project |  0.0917   |  0.93   |  0.95  |     |
|           **numpy:issue_reply:member-numpy:issue_reply:nonmember**           | 3W: Types x Author Groups x Project |  -2.542   |  0.011  | 0.021  |  *  |
|               **numpy:pr_post:member-numpy:pr_post:nonmember**               | 3W: Types x Author Groups x Project |  -0.2255  |  0.82   |  0.88  |     |
|              **numpy:pr_reply:member-numpy:pr_reply:nonmember**              | 3W: Types x Author Groups x Project |  0.4803   |  0.63   |  0.71  |     |
|             **numpy:issue_post:member-numpy:issue_reply:member**             | 3W: Types x Author Groups x Project |  -9.899   | 0.0001  | 0.0001 | *** |
|          **numpy:issue_post:nonmember-numpy:issue_reply:nonmember**          | 3W: Types x Author Groups x Project |  -13.29   | 0.0001  | 0.0001 | *** |
|                **numpy:pr_post:member-numpy:pr_reply:member**                | 3W: Types x Author Groups x Project |  -16.98   | 0.0001  | 0.0001 | *** |
|             **numpy:pr_post:nonmember-numpy:pr_reply:nonmember**             | 3W: Types x Author Groups x Project |  -11.68   | 0.0001  | 0.0001 | *** |
|               **numpy:issue_post:member-numpy:pr_post:member**               | 3W: Types x Author Groups x Project |  -1.996   |  0.046  | 0.075  |  .  |
|            **numpy:issue_post:nonmember-numpy:pr_post:nonmember**            | 3W: Types x Author Groups x Project |  -2.191   |  0.028  |  0.05  |  .  |
|              **numpy:issue_reply:member-numpy:pr_reply:member**              | 3W: Types x Author Groups x Project |  -9.492   | 0.0001  | 0.0001 | *** |
|           **numpy:issue_reply:nonmember-numpy:pr_reply:nonmember**           | 3W: Types x Author Groups x Project |  -5.002   | 0.0001  | 0.0001 | *** |
|   **sphinx.gallery:issue_post:member-sphinx.gallery:issue_post:nonmember**   | 3W: Types x Author Groups x Project |  0.5705   |  0.57   |  0.67  |     |
|  **sphinx.gallery:issue_reply:member-sphinx.gallery:issue_reply:nonmember**  | 3W: Types x Author Groups x Project |  -0.3542  |  0.72   |  0.81  |     |
|      **sphinx.gallery:pr_post:member-sphinx.gallery:pr_post:nonmember**      | 3W: Types x Author Groups x Project |  -1.625   |  0.104  | 0.155  |     |
|     **sphinx.gallery:pr_reply:member-sphinx.gallery:pr_reply:nonmember**     | 3W: Types x Author Groups x Project |  0.1352   |  0.89   |  0.93  |     |
|    **sphinx.gallery:issue_post:member-sphinx.gallery:issue_reply:member**    | 3W: Types x Author Groups x Project |  -3.577   | 0.0003  | 0.001  | **  |
| **sphinx.gallery:issue_post:nonmember-sphinx.gallery:issue_reply:nonmember** | 3W: Types x Author Groups x Project |  -4.137   | 0.0001  | 0.0001 | *** |
|       **sphinx.gallery:pr_post:member-sphinx.gallery:pr_reply:member**       | 3W: Types x Author Groups x Project |  -3.462   |    0    | 0.001  | **  |
|    **sphinx.gallery:pr_post:nonmember-sphinx.gallery:pr_reply:nonmember**    | 3W: Types x Author Groups x Project |  -0.1818  |  0.86   |  0.9   |     |
|      **sphinx.gallery:issue_post:member-sphinx.gallery:pr_post:member**      | 3W: Types x Author Groups x Project |  -0.2975  |  0.77   |  0.84  |     |
|   **sphinx.gallery:issue_post:nonmember-sphinx.gallery:pr_post:nonmember**   | 3W: Types x Author Groups x Project |  -2.216   |  0.027  | 0.047  |  *  |
|     **sphinx.gallery:issue_reply:member-sphinx.gallery:pr_reply:member**     | 3W: Types x Author Groups x Project |   1.224   |  0.221  |  0.3   |     |
|  **sphinx.gallery:issue_reply:nonmember-sphinx.gallery:pr_reply:nonmember**  | 3W: Types x Author Groups x Project |   1.034   |   0.3   |  0.39  |     |


```r
all_tests$p_val_adjusted = p.adjust(all_tests$p_value, method="BH")
write.table(all_tests, file="results/models/model-1.1b_final_pvalues.tsv")
```

Finally, let's plot these effects.





![**Figure**. Sentiment by activity type and community membership at the time of posting (member vs. nonmember).](../../figures/sentiment_analysis/ossc-sentiment_membership_contribution-aggregated-knitr.jpg)



![**Figure**. Sentiment by activity type  and community membership at the time of posting (member vs. nonmember) for each project.](../../figures/sentiment_analysis/ossc-sentiment_membership_contribution-by_project-knitr.jpg)

***

### Model 1.2: Time-course analysis for sentiment

The time-course analysis has been moved in a separate file.

***

### Model 1.3: Do posts and comments materially differ in gratitude?

First, let's take a look at a summary table of expressions of gratitude by
membership status and activity type.


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
|  nonmember   |  pr_reply   |       0        | 32623  |
|  nonmember   |  pr_reply   |       1        |  5598  |
|  nonmember   |  pr_reply   |       2        |  338   |
|  nonmember   |  pr_reply   |       3        |   34   |

Now that we have a better idea of how the underlying data look, let's go ahead
and build our model.



![**Figure**. Expressions of gratitude by activity type (posted issue, comment on issue, posted pull request, or comment on pull request) and community membership (member vs. nonmember) at the time of posting.](../../figures/sentiment_analysis/ossc-grateful_membership_contribution-knitr.jpg)

First, we build a series of linear mixed-effects models with one term included
in each model (either main term or interaction term). We then use the estimates
from those models to perform *t*-tests to investigate how different levels of
the effects differ from one another (and not just from the model-level
intercept).

Projects here are random effects, but the rest of the model is the same as
before. This allows us to do pairwise testing of main and interaction terms,
along with better exploring inter-project variability.

#### Model 1.3b: Does sentiment vary significantly by community membership?

First, look at whether there are differences in sentiment between author
groups.


```r
# do members and nonmembers materially differ in emotion?
fixed_authors_gratitude = lmer(
  log(grateful_count + 1) ~ 0 + author_group + (1 | project),
  data=sentiment_frame,
  REML=FALSE)
```

Run *t*-tests among levels and prepare for the Model 1.3 table later.


```r
# convert Model 1.3b output to dataframe
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


```r
write.table(coefficients_and_se,
            file="results/models/model-1.3b1.tsv",
            sep="\t")
```

#### Model 1.3c: Does sentiment vary significantly across activity types?

Now, look at whether there are differences in sentiment between activity
types.


```r
# do posts and comments materially differ in emotion?
fixed_types_gratitude = lmer(
  log(grateful_count + 1) ~ 0 + type + (1 | project),
  data=sentiment_frame,
  REML=FALSE)
```

Run *t*-tests among levels and prepare for the Model 1.3 table later.


```r
# convert Model 1.1c output to dataframe
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


```r
write.table(coefficients_and_se,
            file="results/models/model-1.3b2.tsv",
            sep="\t")
```

#### Model 1.3d: Does sentiment vary significantly across community memberships and activity types?

Finally, let's look at the interaction between membership and activity.


```r
# does emotion differ by the interaction between activity and authorship group?
community_contribution_gratitude = lmer(
  log(grateful_count + 1) ~ 0 + type:author_group + (1 | project),
  data=sentiment_frame,
  REML=FALSE)
```

Run *t*-tests among levels and prepare for the Model 1.3 table later.


```r
# convert Model 1.3d output to dataframe
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
  "issue_post:member-issue_post:nonmember",     # activity static (issue posts); membership varies (members v. nonmembers)
  "issue_reply:member-issue_reply:nonmember",   # activity static (issue replies); membership varies (members v. nonmembers)
  "pr_post:member-pr_post:nonmember",           # activity static (PR posts); membership varies (members v. nonmembers)
  "pr_reply:member-pr_reply:nonmember",         # activity static (PR replies); membership varies (members v. nonmembers)
  "issue_post:member-issue_reply:member",       # activity varies (issue posts vs. issue replies); membership static (members)
  "issue_post:nonmember-issue_reply:nonmember", # activity varies (issue posts vs. issue replies); membership static (nonmembers)
  "pr_post:member-pr_reply:member",             # activity varies (PR posts vs. PR replies); membership static (members)
  "pr_post:nonmember-pr_reply:nonmember",       # activity varies (PR posts vs. PR replies); membership static (nonmembers)
  "issue_post:member-pr_post:member",           # activity varies (issue posts vs. PR posts); membership static (members)
  "issue_post:nonmember-pr_post:nonmember",     # activity varies (issue posts vs. PR posts); membership static (nonmembers)
  "issue_reply:member-pr_reply:member",         # activity varies (issue replies vs. PR replies); membership static (members)
  "issue_reply:nonmember-pr_reply:nonmember")   # activity varies (issue replies vs. PR replies); membership static (nonmembers)
types_author_groups_tests = compute_t_statistics(
  means, se,
  contrasts)
types_author_groups_tests[, "p_value"] = compute_p_value_from_t_stats(
  types_author_groups_tests$"t_stats")
```


```r
write.table(coefficients_and_se,
            file="results/models/model-1.3b3.tsv",
            sep="\t")
```

#### Model 1.3e : Do different kinds of activities differ in emotion by projects?

Now adding projects into the mix to understand how the previous analysis
varies across projects.


```r
# do posts and comments materially differ in gratitude by projects?
creators_v_commenters_gratitude_by_project = lm(
  log(grateful_count + 1) ~ 0 + project:type:author_group,
  data = sentiment_frame)
```

Run *t*-tests among levels and prepare for the Model 1.3 table later.


```r
# convert Model 1.3e output to dataframe
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
# (note: ordering of contrasts within each project is identical to Model 1.3c)
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


```r
write.table(coefficients_and_se,
            file="results/models/model-1.3e.tsv",
            sep="\t")
```

#### Overall results

Now we bring together all analyses from Model 1.3.


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
|                             **member-nonmember**                             |             Main Terms              |  -3.383  |  0.001  | 0.001  | **  |
|                          **issue_post-issue_reply**                          |             Main Terms              |  -1.619  |  0.105  | 0.135  |     |
|                             **pr_post-pr_reply**                             |             Main Terms              |  -6.71   | 0.0001  | 0.0001 | *** |
|                            **issue_post-pr_post**                            |             Main Terms              |  2.418   |  0.016  | 0.022  |  *  |
|                           **issue_reply-pr_reply**                           |             Main Terms              |  -2.671  |  0.008  | 0.011  |  *  |
|                  **issue_post:member-issue_post:nonmember**                  |      2W: Types x Author Groups      |  -5.139  | 0.0001  | 0.0001 | *** |
|                 **issue_reply:member-issue_reply:nonmember**                 |      2W: Types x Author Groups      |  -8.616  | 0.0001  | 0.0001 | *** |
|                     **pr_post:member-pr_post:nonmember**                     |      2W: Types x Author Groups      | -0.8737  |  0.38   |  0.44  |     |
|                    **pr_reply:member-pr_reply:nonmember**                    |      2W: Types x Author Groups      |  -1.084  |  0.28   |  0.33  |     |
|                   **issue_post:member-issue_reply:member**                   |      2W: Types x Author Groups      |  -2.752  |  0.006  | 0.009  | **  |
|                **issue_post:nonmember-issue_reply:nonmember**                |      2W: Types x Author Groups      |  -6.083  | 0.0001  | 0.0001 | *** |
|                      **pr_post:member-pr_reply:member**                      |      2W: Types x Author Groups      |  -8.378  | 0.0001  | 0.0001 | *** |
|                   **pr_post:nonmember-pr_reply:nonmember**                   |      2W: Types x Author Groups      |  -8.442  | 0.0001  | 0.0001 | *** |
|                     **issue_post:member-pr_post:member**                     |      2W: Types x Author Groups      |  0.3748  |  0.71   |  0.76  |     |
|                  **issue_post:nonmember-pr_post:nonmember**                  |      2W: Types x Author Groups      |  4.622   | 0.0001  | 0.0001 | *** |
|                    **issue_reply:member-pr_reply:member**                    |      2W: Types x Author Groups      |  -5.263  | 0.0001  | 0.0001 | *** |
|                 **issue_reply:nonmember-pr_reply:nonmember**                 |      2W: Types x Author Groups      |  2.278   |  0.023  | 0.031  |  *  |
|     **scikit.learn:issue_post:member-scikit.learn:issue_post:nonmember**     | 3W: Types x Author Groups x Project |  -14.67  | 0.0001  | 0.0001 | *** |
|    **scikit.learn:issue_reply:member-scikit.learn:issue_reply:nonmember**    | 3W: Types x Author Groups x Project |  -28.53  | 0.0001  | 0.0001 | *** |
|        **scikit.learn:pr_post:member-scikit.learn:pr_post:nonmember**        | 3W: Types x Author Groups x Project |  -1.397  |  0.162  | 0.202  |     |
|       **scikit.learn:pr_reply:member-scikit.learn:pr_reply:nonmember**       | 3W: Types x Author Groups x Project |  -10.27  | 0.0001  | 0.0001 | *** |
|      **scikit.learn:issue_post:member-scikit.learn:issue_reply:member**      | 3W: Types x Author Groups x Project |  -9.181  | 0.0001  | 0.0001 | *** |
|   **scikit.learn:issue_post:nonmember-scikit.learn:issue_reply:nonmember**   | 3W: Types x Author Groups x Project |  -5.942  | 0.0001  | 0.0001 | *** |
|         **scikit.learn:pr_post:member-scikit.learn:pr_reply:member**         | 3W: Types x Author Groups x Project |  -22.7   | 0.0001  | 0.0001 | *** |
|      **scikit.learn:pr_post:nonmember-scikit.learn:pr_reply:nonmember**      | 3W: Types x Author Groups x Project |  -22.46  | 0.0001  | 0.0001 | *** |
|        **scikit.learn:issue_post:member-scikit.learn:pr_post:member**        | 3W: Types x Author Groups x Project |  -1.162  |  0.245  |  0.29  |     |
|     **scikit.learn:issue_post:nonmember-scikit.learn:pr_post:nonmember**     | 3W: Types x Author Groups x Project |  13.22   | 0.0001  | 0.0001 | *** |
|       **scikit.learn:issue_reply:member-scikit.learn:pr_reply:member**       | 3W: Types x Author Groups x Project |  -31.01  | 0.0001  | 0.0001 | *** |
|    **scikit.learn:issue_reply:nonmember-scikit.learn:pr_reply:nonmember**    | 3W: Types x Author Groups x Project | -0.07065 |  0.94   |  0.95  |     |
|     **scikit.image:issue_post:member-scikit.image:issue_post:nonmember**     | 3W: Types x Author Groups x Project |  -5.82   | 0.0001  | 0.0001 | *** |
|    **scikit.image:issue_reply:member-scikit.image:issue_reply:nonmember**    | 3W: Types x Author Groups x Project |  -10.31  | 0.0001  | 0.0001 | *** |
|        **scikit.image:pr_post:member-scikit.image:pr_post:nonmember**        | 3W: Types x Author Groups x Project |  -1.363  |  0.173  | 0.212  |     |
|       **scikit.image:pr_reply:member-scikit.image:pr_reply:nonmember**       | 3W: Types x Author Groups x Project | -0.6262  |  0.53   |  0.59  |     |
|      **scikit.image:issue_post:member-scikit.image:issue_reply:member**      | 3W: Types x Author Groups x Project |  -5.881  | 0.0001  | 0.0001 | *** |
|   **scikit.image:issue_post:nonmember-scikit.image:issue_reply:nonmember**   | 3W: Types x Author Groups x Project |  -4.413  | 0.0001  | 0.0001 | *** |
|         **scikit.image:pr_post:member-scikit.image:pr_reply:member**         | 3W: Types x Author Groups x Project |  -18.89  | 0.0001  | 0.0001 | *** |
|      **scikit.image:pr_post:nonmember-scikit.image:pr_reply:nonmember**      | 3W: Types x Author Groups x Project |  -10.77  | 0.0001  | 0.0001 | *** |
|        **scikit.image:issue_post:member-scikit.image:pr_post:member**        | 3W: Types x Author Groups x Project | -0.2474  |   0.8   |  0.84  |     |
|     **scikit.image:issue_post:nonmember-scikit.image:pr_post:nonmember**     | 3W: Types x Author Groups x Project |  4.725   | 0.0001  | 0.0001 | *** |
|       **scikit.image:issue_reply:member-scikit.image:pr_reply:member**       | 3W: Types x Author Groups x Project |  -16.86  | 0.0001  | 0.0001 | *** |
|    **scikit.image:issue_reply:nonmember-scikit.image:pr_reply:nonmember**    | 3W: Types x Author Groups x Project | -0.1531  |  0.88   |  0.9   |     |
|       **matplotlib:issue_post:member-matplotlib:issue_post:nonmember**       | 3W: Types x Author Groups x Project |  -5.112  | 0.0001  | 0.0001 | *** |
|      **matplotlib:issue_reply:member-matplotlib:issue_reply:nonmember**      | 3W: Types x Author Groups x Project |  -35.21  | 0.0001  | 0.0001 | *** |
|          **matplotlib:pr_post:member-matplotlib:pr_post:nonmember**          | 3W: Types x Author Groups x Project |  -1.525  |  0.127  | 0.161  |     |
|         **matplotlib:pr_reply:member-matplotlib:pr_reply:nonmember**         | 3W: Types x Author Groups x Project |  -17.31  | 0.0001  | 0.0001 | *** |
|        **matplotlib:issue_post:member-matplotlib:issue_reply:member**        | 3W: Types x Author Groups x Project | -0.2677  |  0.79   |  0.83  |     |
|     **matplotlib:issue_post:nonmember-matplotlib:issue_reply:nonmember**     | 3W: Types x Author Groups x Project |  -15.15  | 0.0001  | 0.0001 | *** |
|           **matplotlib:pr_post:member-matplotlib:pr_reply:member**           | 3W: Types x Author Groups x Project |  -16.94  | 0.0001  | 0.0001 | *** |
|        **matplotlib:pr_post:nonmember-matplotlib:pr_reply:nonmember**        | 3W: Types x Author Groups x Project |  -16.94  | 0.0001  | 0.0001 | *** |
|          **matplotlib:issue_post:member-matplotlib:pr_post:member**          | 3W: Types x Author Groups x Project |  3.528   | 0.0004  | 0.001  | **  |
|       **matplotlib:issue_post:nonmember-matplotlib:pr_post:nonmember**       | 3W: Types x Author Groups x Project |  6.776   | 0.0001  | 0.0001 | *** |
|         **matplotlib:issue_reply:member-matplotlib:pr_reply:member**         | 3W: Types x Author Groups x Project |  -16.2   | 0.0001  | 0.0001 | *** |
|      **matplotlib:issue_reply:nonmember-matplotlib:pr_reply:nonmember**      | 3W: Types x Author Groups x Project |  2.659   |  0.008  | 0.011  |  *  |
|           **mayavi:issue_post:member-mayavi:issue_post:nonmember**           | 3W: Types x Author Groups x Project |  -5.731  | 0.0001  | 0.0001 | *** |
|          **mayavi:issue_reply:member-mayavi:issue_reply:nonmember**          | 3W: Types x Author Groups x Project |  -6.625  | 0.0001  | 0.0001 | *** |
|              **mayavi:pr_post:member-mayavi:pr_post:nonmember**              | 3W: Types x Author Groups x Project | 0.01385  |  0.99   |  0.99  |     |
|             **mayavi:pr_reply:member-mayavi:pr_reply:nonmember**             | 3W: Types x Author Groups x Project |  5.396   | 0.0001  | 0.0001 | *** |
|            **mayavi:issue_post:member-mayavi:issue_reply:member**            | 3W: Types x Author Groups x Project |  -3.359  |  0.001  | 0.001  | **  |
|         **mayavi:issue_post:nonmember-mayavi:issue_reply:nonmember**         | 3W: Types x Author Groups x Project | -0.6721  |   0.5   |  0.56  |     |
|               **mayavi:pr_post:member-mayavi:pr_reply:member**               | 3W: Types x Author Groups x Project |  -10.99  | 0.0001  | 0.0001 | *** |
|            **mayavi:pr_post:nonmember-mayavi:pr_reply:nonmember**            | 3W: Types x Author Groups x Project |  -3.794  | 0.0001  | 0.0002 | *** |
|              **mayavi:issue_post:member-mayavi:pr_post:member**              | 3W: Types x Author Groups x Project | -0.8359  |   0.4   |  0.46  |     |
|           **mayavi:issue_post:nonmember-mayavi:pr_post:nonmember**           | 3W: Types x Author Groups x Project |  4.967   | 0.0001  | 0.0001 | *** |
|             **mayavi:issue_reply:member-mayavi:pr_reply:member**             | 3W: Types x Author Groups x Project |  -10.53  | 0.0001  | 0.0001 | *** |
|          **mayavi:issue_reply:nonmember-mayavi:pr_reply:nonmember**          | 3W: Types x Author Groups x Project |  1.947   |  0.052  | 0.068  |  .  |
|           **pandas:issue_post:member-pandas:issue_post:nonmember**           | 3W: Types x Author Groups x Project |  -11.25  | 0.0001  | 0.0001 | *** |
|          **pandas:issue_reply:member-pandas:issue_reply:nonmember**          | 3W: Types x Author Groups x Project |  -44.77  | 0.0001  | 0.0001 | *** |
|              **pandas:pr_post:member-pandas:pr_post:nonmember**              | 3W: Types x Author Groups x Project |  -2.763  |  0.006  | 0.009  | **  |
|             **pandas:pr_reply:member-pandas:pr_reply:nonmember**             | 3W: Types x Author Groups x Project |  9.658   | 0.0001  | 0.0001 | *** |
|            **pandas:issue_post:member-pandas:issue_reply:member**            | 3W: Types x Author Groups x Project |  -11.53  | 0.0001  | 0.0001 | *** |
|         **pandas:issue_post:nonmember-pandas:issue_reply:nonmember**         | 3W: Types x Author Groups x Project |  -24.83  | 0.0001  | 0.0001 | *** |
|               **pandas:pr_post:member-pandas:pr_reply:member**               | 3W: Types x Author Groups x Project |  -34.41  | 0.0001  | 0.0001 | *** |
|            **pandas:pr_post:nonmember-pandas:pr_reply:nonmember**            | 3W: Types x Author Groups x Project |  -13.47  | 0.0001  | 0.0001 | *** |
|              **pandas:issue_post:member-pandas:pr_post:member**              | 3W: Types x Author Groups x Project |  1.225   |  0.22   |  0.26  |     |
|           **pandas:issue_post:nonmember-pandas:pr_post:nonmember**           | 3W: Types x Author Groups x Project |  7.148   | 0.0001  | 0.0001 | *** |
|             **pandas:issue_reply:member-pandas:pr_reply:member**             | 3W: Types x Author Groups x Project |  -42.61  | 0.0001  | 0.0001 | *** |
|          **pandas:issue_reply:nonmember-pandas:pr_reply:nonmember**          | 3W: Types x Author Groups x Project |  21.29   | 0.0001  | 0.0001 | *** |
|            **scipy:issue_post:member-scipy:issue_post:nonmember**            | 3W: Types x Author Groups x Project |  -7.441  | 0.0001  | 0.0001 | *** |
|           **scipy:issue_reply:member-scipy:issue_reply:nonmember**           | 3W: Types x Author Groups x Project |  -23.61  | 0.0001  | 0.0001 | *** |
|               **scipy:pr_post:member-scipy:pr_post:nonmember**               | 3W: Types x Author Groups x Project |  -2.325  |  0.02   | 0.028  |  *  |
|              **scipy:pr_reply:member-scipy:pr_reply:nonmember**              | 3W: Types x Author Groups x Project |  -3.495  |    0    | 0.001  | **  |
|             **scipy:issue_post:member-scipy:issue_reply:member**             | 3W: Types x Author Groups x Project |  -4.636  | 0.0001  | 0.0001 | *** |
|          **scipy:issue_post:nonmember-scipy:issue_reply:nonmember**          | 3W: Types x Author Groups x Project |  -9.932  | 0.0001  | 0.0001 | *** |
|                **scipy:pr_post:member-scipy:pr_reply:member**                | 3W: Types x Author Groups x Project |  -25.04  | 0.0001  | 0.0001 | *** |
|             **scipy:pr_post:nonmember-scipy:pr_reply:nonmember**             | 3W: Types x Author Groups x Project |  -16.24  | 0.0001  | 0.0001 | *** |
|               **scipy:issue_post:member-scipy:pr_post:member**               | 3W: Types x Author Groups x Project | -0.3437  |  0.73   |  0.78  |     |
|            **scipy:issue_post:nonmember-scipy:pr_post:nonmember**            | 3W: Types x Author Groups x Project |  6.361   | 0.0001  | 0.0001 | *** |
|              **scipy:issue_reply:member-scipy:pr_reply:member**              | 3W: Types x Author Groups x Project |  -30.82  | 0.0001  | 0.0001 | *** |
|           **scipy:issue_reply:nonmember-scipy:pr_reply:nonmember**           | 3W: Types x Author Groups x Project | -0.1318  |   0.9   |  0.91  |     |
|            **numpy:issue_post:member-numpy:issue_post:nonmember**            | 3W: Types x Author Groups x Project |  -5.873  | 0.0001  | 0.0001 | *** |
|           **numpy:issue_reply:member-numpy:issue_reply:nonmember**           | 3W: Types x Author Groups x Project |  -31.86  | 0.0001  | 0.0001 | *** |
|               **numpy:pr_post:member-numpy:pr_post:nonmember**               | 3W: Types x Author Groups x Project |  -1.053  |  0.29   |  0.34  |     |
|              **numpy:pr_reply:member-numpy:pr_reply:nonmember**              | 3W: Types x Author Groups x Project |    -5    | 0.0001  | 0.0001 | *** |
|             **numpy:issue_post:member-numpy:issue_reply:member**             | 3W: Types x Author Groups x Project |  -2.655  |  0.008  | 0.011  |  *  |
|          **numpy:issue_post:nonmember-numpy:issue_reply:nonmember**          | 3W: Types x Author Groups x Project |  -14.21  | 0.0001  | 0.0001 | *** |
|                **numpy:pr_post:member-numpy:pr_reply:member**                | 3W: Types x Author Groups x Project |  -24.07  | 0.0001  | 0.0001 | *** |
|             **numpy:pr_post:nonmember-numpy:pr_reply:nonmember**             | 3W: Types x Author Groups x Project |  -15.47  | 0.0001  | 0.0001 | *** |
|               **numpy:issue_post:member-numpy:pr_post:member**               | 3W: Types x Author Groups x Project |  1.763   |  0.078  | 0.101  |     |
|            **numpy:issue_post:nonmember-numpy:pr_post:nonmember**            | 3W: Types x Author Groups x Project |  5.998   | 0.0001  | 0.0001 | *** |
|              **numpy:issue_reply:member-numpy:pr_reply:member**              | 3W: Types x Author Groups x Project |  -32.58  | 0.0001  | 0.0001 | *** |
|           **numpy:issue_reply:nonmember-numpy:pr_reply:nonmember**           | 3W: Types x Author Groups x Project |  3.773   | 0.0002  | 0.0003 | *** |
|   **sphinx.gallery:issue_post:member-sphinx.gallery:issue_post:nonmember**   | 3W: Types x Author Groups x Project |  -1.797  |  0.072  | 0.095  |  .  |
|  **sphinx.gallery:issue_reply:member-sphinx.gallery:issue_reply:nonmember**  | 3W: Types x Author Groups x Project |  -6.165  | 0.0001  | 0.0001 | *** |
|      **sphinx.gallery:pr_post:member-sphinx.gallery:pr_post:nonmember**      | 3W: Types x Author Groups x Project |  -0.743  |  0.46   |  0.52  |     |
|     **sphinx.gallery:pr_reply:member-sphinx.gallery:pr_reply:nonmember**     | 3W: Types x Author Groups x Project | -0.1851  |  0.85   |  0.88  |     |
|    **sphinx.gallery:issue_post:member-sphinx.gallery:issue_reply:member**    | 3W: Types x Author Groups x Project | -0.5975  |  0.55   |  0.6   |     |
| **sphinx.gallery:issue_post:nonmember-sphinx.gallery:issue_reply:nonmember** | 3W: Types x Author Groups x Project |  -2.025  |  0.043  | 0.058  |  .  |
|       **sphinx.gallery:pr_post:member-sphinx.gallery:pr_reply:member**       | 3W: Types x Author Groups x Project |  -3.992  | 0.0001  | 0.0001 | *** |
|    **sphinx.gallery:pr_post:nonmember-sphinx.gallery:pr_reply:nonmember**    | 3W: Types x Author Groups x Project |  -1.48   |  0.139  | 0.174  |     |
|      **sphinx.gallery:issue_post:member-sphinx.gallery:pr_post:member**      | 3W: Types x Author Groups x Project |  0.5178  |   0.6   |  0.66  |     |
|   **sphinx.gallery:issue_post:nonmember-sphinx.gallery:pr_post:nonmember**   | 3W: Types x Author Groups x Project |  1.241   |  0.214  |  0.26  |     |
|     **sphinx.gallery:issue_reply:member-sphinx.gallery:pr_reply:member**     | 3W: Types x Author Groups x Project |  -4.506  | 0.0001  | 0.0001 | *** |
|  **sphinx.gallery:issue_reply:nonmember-sphinx.gallery:pr_reply:nonmember**  | 3W: Types x Author Groups x Project |  2.577   |  0.01   | 0.014  |  *  |


```r
all_tests$p_val_adjusted = p.adjust(all_tests$p_value, method="BH")
write.table(all_tests, file="results/models/model-1.3b_final_pvalues.tsv")
```

***

### Model 1.4: Time-course analysis for gratitude

The time-course analysis has been moved in a separate file.

***

## Model Series 2: Retention

Our second set of models investigates what aspects of the response to a 
newcomer's first activity (including aspects of the community's response
to their contribution) might predict their likelihood to come back to 
contribute a second time.

***

### Data preparation

Because each ticket has multiple comments, we cannot use the standard long-form
format for the dataset, or we would lead to (uneven) duplication of posts
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
posts dataframe in preparation for our models.


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


```r
write.table(retention_frame, "results/data/newcomer_retention.tsv", sep="\t")
```

***

### Summary statistics

What do these newcomers look like?



35.010285% of first-time contributors come back for a second
contribution.

70.4966206% of first-time contributors post issues (compared
with pull requests).

***

### Model 2.1: How does a community's response to newcomers predict the newcomer's decision to return?





![**Figure**. Whether a first-time ticket creator will open a second ticket by commenters' expressions of gratitude and responsiveness.](../../figures/sentiment_analysis/ossc-retention_emotion-by_project-knitr.jpg)


```r
retention_predictors = glmer(retained_newcomer ~ 0 + ticket_family + (1 | project),
                             data=retention_frame, family=binomial)
coefficients_and_se = data.frame(
  summary(retention_predictors)$coefficients)

# get comparison names as rownames
row_names = gsub("ticket_family", "", row.names(coefficients_and_se))
# convert model estimates to a dataframe
means = coefficients_and_se$Estimate
names(means) = row_names

# convert standard error to dataframe
se = coefficients_and_se$Std..Error
names(se) = row_names

# compute t-statistics and p-values for desired contrasts
contrasts = c("pr-issue")
retention_tests = compute_t_statistics(
  means, se,
  contrasts)
retention_tests[, "p_value"] = compute_p_value_from_t_stats(
  retention_tests$t_stats)


# Keep coefficient + sde for plotting purposes
all_coefs_and_se = coefficients_and_se[, c("Estimate", "Std..Error")]
all_random_effects = ranef(retention_predictors)$"project"
colnames(all_random_effects) = "ticket_family"
```



```r
# Open time
retention_predictor = glmer(retained_newcomer ~ open_time + (1 | project),
                            data=retention_frame, family=binomial, nAGQ=0)
```

```
## Warning: Some predictor variables are on very different scales: consider
## rescaling
```

```r
retention_tests_continuous = as.data.frame(summary(
  retention_predictor)$coefficients)
new_coefs = retention_tests_continuous[, c("Estimate", "Std. Error")]
colnames(new_coefs) = colnames(all_coefs_and_se)
all_coefs_and_se = rbind(
  all_coefs_and_se, new_coefs)
retention_tests_continuous[, "row_names"] = row.names(
  retention_tests_continuous)

random_effects = ranef(retention_predictor)$project
colnames(random_effects) = "open_time"
all_random_effects = cbind(all_random_effects, random_effects)

# Comment grateful cumulative
retention_predictor = glmer(retained_newcomer ~ comment_grateful_cumulative + (1 | project),
                            data=retention_frame, family=binomial, nAGQ=0)
retention_grateful =  as.data.frame(summary(retention_predictor)$coefficients)
new_coefs = retention_grateful[, c("Estimate", "Std. Error")]
colnames(new_coefs) = colnames(all_coefs_and_se)
all_coefs_and_se = rbind(
  all_coefs_and_se, new_coefs)
retention_grateful[, "row_names"] = row.names(
  retention_grateful)
retention_tests_continuous = merge(
  retention_tests_continuous,
  retention_grateful, all=TRUE, sort=FALSE)

random_effects = ranef(retention_predictor)$project
colnames(random_effects) = "comment_grateful_cumulative"
all_random_effects = cbind(all_random_effects, random_effects)

# Comment sentiment max negative
retention_predictor = glmer(retained_newcomer ~ comment_sentiment_max_negative + (1 | project),
                            data=retention_frame, family=binomial, nAGQ=0)
retention_comment_sentiment_max_negative = as.data.frame(
  summary(retention_predictor)$coefficients)
new_coefs = retention_comment_sentiment_max_negative[, c("Estimate", "Std. Error")]
colnames(new_coefs) = colnames(all_coefs_and_se)
all_coefs_and_se = rbind(
  all_coefs_and_se, new_coefs)
retention_comment_sentiment_max_negative[, "row_names"] = row.names(
  retention_comment_sentiment_max_negative)
retention_tests_continuous = merge(
  retention_tests_continuous,
  retention_comment_sentiment_max_negative,
  all=TRUE, sort=FALSE)

random_effects = ranef(retention_predictor)$project
colnames(random_effects) = "comment_sentiment_max_negative"
all_random_effects = cbind(all_random_effects, random_effects)

# Number of comments
retention_predictor = glmer(retained_newcomer ~ number_of_comments + (1 | project),
                            data=retention_frame, family=binomial, nAGQ=0)
retention_number_of_comment = as.data.frame(
  summary(retention_predictor)$coefficients)
new_coefs = retention_number_of_comment[, c("Estimate", "Std. Error")]
colnames(new_coefs) = colnames(all_coefs_and_se)
all_coefs_and_se = rbind(
  all_coefs_and_se,
  new_coefs)
retention_number_of_comment[, "row_names"] = row.names(
  retention_number_of_comment)
retention_tests_continuous = merge(
  retention_tests_continuous,
  retention_number_of_comment,
  all=TRUE, sort=FALSE)

random_effects = ranef(retention_predictor)$project
colnames(random_effects) = "number_of_comments"
all_random_effects = cbind(all_random_effects, random_effects)

# Comment member ratio
retention_predictor = glmer(retained_newcomer ~ comment_member_ratio + (1 | project),
                            data=retention_frame, family=binomial, nAGQ=0)

retention_comment_member_ratio = as.data.frame(
  summary(retention_predictor)$coefficients)
new_coefs = retention_comment_member_ratio[, c("Estimate", "Std. Error")]
colnames(new_coefs) = colnames(all_coefs_and_se)
all_coefs_and_se = rbind(
  all_coefs_and_se,
  new_coefs)

retention_comment_member_ratio[, "row_names"] = row.names(
  retention_comment_member_ratio)
retention_tests_continuous = merge(
  retention_tests_continuous,
  retention_comment_member_ratio,
  all=TRUE, sort=FALSE)

random_effects = ranef(retention_predictor)$project
colnames(random_effects) = "comment_member_ratio"
all_random_effects = cbind(all_random_effects, random_effects)

# Comment sentiment mean
retention_predictor = glmer(retained_newcomer ~ comment_sentiment_mean + (1 | project),
                            data=retention_frame, family=binomial, nAGQ=0)
retention_comment_sentiment_mean = as.data.frame(
  summary(retention_predictor)$coefficients)
new_coefs = retention_comment_sentiment_mean[, c("Estimate", "Std. Error")]
colnames(new_coefs) = colnames(all_coefs_and_se)
all_coefs_and_se = rbind(
  all_coefs_and_se,
  new_coefs)
retention_comment_sentiment_mean[, "row_names"] = row.names(
  retention_comment_sentiment_mean)
retention_tests_continuous = rbind(
  retention_tests_continuous,
  retention_comment_sentiment_mean)

random_effects = ranef(retention_predictor)$project
colnames(random_effects) = "comment_sentiment_mean"
all_random_effects = cbind(all_random_effects, random_effects)
```

Now let's do interaction terms between contribution types and everything else.


```r
# Ticket family x open time
retention_predictor = glmer(
  retained_newcomer ~ 0 + ticket_family + ticket_family:open_time + (1 | project),
  data=retention_frame, family=binomial, nAGQ=0)
```

```
## Warning: Some predictor variables are on very different scales: consider
## rescaling
```

```r
retention_open_time = as.data.frame(
  summary(retention_predictor)$coefficients)
new_coefs = retention_open_time[, c("Estimate", "Std. Error")]
colnames(new_coefs) = colnames(all_coefs_and_se)
all_coefs_and_se = rbind(
  all_coefs_and_se,
  new_coefs)
retention_open_time[, "row_names"] = row.names(
  retention_open_time)
retention_tests_continuous = rbind(
  retention_tests_continuous,
  retention_open_time)
random_effects = ranef(retention_predictor)$project
colnames(random_effects) = "ticket_family_open_time"
all_random_effects = cbind(all_random_effects, random_effects)

# Ticket family x comment sentiment max negative
retention_predictor = glmer(
  retained_newcomer ~ 0 + ticket_family + ticket_family:comment_sentiment_max_negative + (1 | project),
  data=retention_frame, family=binomial, nAGQ=0)
retention_comment_sentiment_max_negative = as.data.frame(
  summary(retention_predictor)$coefficients)
new_coefs = retention_comment_sentiment_max_negative[, c("Estimate", "Std. Error")]
colnames(new_coefs) = colnames(all_coefs_and_se)
all_coefs_and_se = rbind(
  all_coefs_and_se,
  new_coefs)
retention_comment_sentiment_max_negative[, "row_names"] = row.names(
  retention_comment_sentiment_max_negative)
retention_tests_continuous = merge(
  retention_tests_continuous,
  retention_comment_sentiment_max_negative,
  all=TRUE, sort=FALSE)

random_effects = ranef(retention_predictor)$project
colnames(random_effects) = "ticket_family_comment_sentiment_max_negative"
all_random_effects = cbind(all_random_effects, random_effects)

# Ticket family x number of comments
retention_predictor = glmer(
  retained_newcomer ~ 0 + ticket_family + ticket_family:number_of_comments + (1 | project),
  data=retention_frame, family=binomial, nAGQ=0)
retention_number_of_comments = as.data.frame(
  summary(retention_predictor)$coefficients)
new_coefs = retention_number_of_comments[, c("Estimate", "Std. Error")]
colnames(new_coefs) = colnames(all_coefs_and_se)
all_coefs_and_se = rbind(
  all_coefs_and_se,
  new_coefs)
retention_number_of_comments[, "row_names"] = row.names(
  retention_number_of_comments)
retention_tests_continuous = merge(
  retention_tests_continuous,
  retention_number_of_comments,
  all=TRUE, sort=FALSE)

random_effects = ranef(retention_predictor)$project
colnames(random_effects) = "ticket_family_number_of_comments"
all_random_effects = cbind(all_random_effects, random_effects)

# Ticket family x comment member ratio
retention_predictor = glmer(
  retained_newcomer ~ 0 + ticket_family + ticket_family:comment_member_ratio + (1 | project),
  data=retention_frame, family=binomial, nAGQ=0)
retention_comment_member_ratio = as.data.frame(
  summary(retention_predictor)$coefficients)
new_coefs = retention_comment_member_ratio[, c("Estimate", "Std. Error")]
colnames(new_coefs) = colnames(all_coefs_and_se)
all_coefs_and_se = rbind(
  all_coefs_and_se,
  new_coefs)
retention_comment_member_ratio[, "row_names"] = row.names(
  retention_comment_member_ratio)
retention_tests_continuous = rbind(
  retention_tests_continuous,
  retention_comment_member_ratio)

random_effects = ranef(retention_predictor)$project
colnames(random_effects) = "ticket_family_comment_member_ratio"
all_random_effects = cbind(all_random_effects, random_effects)

# Ticket family x comment sentiment mean
retention_predictor = glmer(
  retained_newcomer ~ 0 + ticket_family + ticket_family:comment_sentiment_mean + (1 | project),
  data=retention_frame, family=binomial, nAGQ=0)
retention_comment_sentiment_mean = as.data.frame(
  summary(retention_predictor)$coefficients)
new_coefs = retention_comment_sentiment_mean[, c("Estimate", "Std. Error")]
colnames(new_coefs) = colnames(all_coefs_and_se)
all_coefs_and_se = rbind(
  all_coefs_and_se,
  new_coefs)
retention_comment_sentiment_mean[, "row_names"] = row.names(
  retention_comment_sentiment_mean)
retention_tests_continuous = rbind(
  retention_tests_continuous,
  retention_comment_sentiment_mean)

random_effects = ranef(retention_predictor)$project
colnames(random_effects) = "ticket_family_comment_sentiment_mean"
all_random_effects = cbind(all_random_effects, random_effects)

# Ticket family x comment grateful cumulative
retention_predictor = glmer(
  retained_newcomer ~ 0 + ticket_family + ticket_family:comment_grateful_cumulative + (1 | project),
  data=retention_frame, family=binomial, nAGQ=0)
retention_comment_grateful_cumulative = as.data.frame(
  summary(retention_predictor)$coefficients)
new_coefs = retention_comment_grateful_cumulative[, c("Estimate", "Std. Error")]
colnames(new_coefs) = colnames(all_coefs_and_se)
all_coefs_and_se = rbind(
  all_coefs_and_se,
  new_coefs)
retention_comment_grateful_cumulative[, "row_names"] = row.names(
  retention_comment_grateful_cumulative)
retention_tests_continuous = rbind(
  retention_tests_continuous,
  retention_comment_grateful_cumulative)

random_effects = ranef(retention_predictor)$project
colnames(random_effects) = "ticket_family_comment_grateful_cumulative"
all_random_effects = cbind(all_random_effects, random_effects)
```


```r
mask = (
  retention_tests_continuous$row_names != "(Intercept)" &
    retention_tests_continuous$row_names != "ticket_familyissue" &
    retention_tests_continuous$row_names != "ticket_familypr")
retention_tests_continuous = retention_tests_continuous[mask, ]
row.names(retention_tests_continuous) = retention_tests_continuous[,
                                                                   "row_names"] 

columns_of_interest = c("z value", "Pr(>|z|)")
retention_tests_continuous = retention_tests_continuous[, columns_of_interest]
retention_tests_continuous["model"] = row.names(retention_tests_continuous)
colnames(retention_tests_continuous) = c("stat", "p_value", "model")
retention_tests["model"] = row.names(retention_tests)
colnames(retention_tests) = c("stat", "p_value", "model")

retention_tests = rbind(retention_tests, retention_tests_continuous)
```


```r
pander_clean_anova(retention_tests[c("model", "stat", "p_value")],
                   rename_columns=FALSE)
```



|                        &nbsp;                         |                       model                       |  stat   | p_value | p_adj  | sig |
|:-----------------------------------------------------:|:-------------------------------------------------:|:-------:|:-------:|:------:|:---:|
|                     **pr-issue**                      |                     pr-issue                      |  5.531  | 0.0001  | 0.0001 | *** |
|                     **open_time**                     |                     open_time                     | -1.296  |  0.195  | 0.226  |     |
|            **comment_grateful_cumulative**            |            comment_grateful_cumulative            |  6.701  | 0.0001  | 0.0001 | *** |
|          **comment_sentiment_max_negative**           |          comment_sentiment_max_negative           |   1.4   |  0.162  | 0.205  |     |
|                **number_of_comments**                 |                number_of_comments                 |  9.35   | 0.0001  | 0.0001 | *** |
|               **comment_member_ratio**                |               comment_member_ratio                | -8.363  | 0.0001  | 0.0001 | *** |
|              **comment_sentiment_mean**               |              comment_sentiment_mean               |  6.341  | 0.0001  | 0.0001 | *** |
|           **ticket_familyissue:open_time**            |           ticket_familyissue:open_time            |  3.298  |  0.001  | 0.001  | **  |
|             **ticket_familypr:open_time**             |             ticket_familypr:open_time             | -2.956  |  0.003  | 0.004  | **  |
| **ticket_familyissue:comment_sentiment_max_negative** | ticket_familyissue:comment_sentiment_max_negative | -1.275  |  0.202  | 0.226  |     |
|  **ticket_familypr:comment_sentiment_max_negative**   |  ticket_familypr:comment_sentiment_max_negative   |  4.107  | 0.0001  | 0.0001 | *** |
|       **ticket_familyissue:number_of_comments**       |       ticket_familyissue:number_of_comments       |  4.011  | 0.0001  | 0.0001 | *** |
|        **ticket_familypr:number_of_comments**         |        ticket_familypr:number_of_comments         |  6.617  | 0.0001  | 0.0001 | *** |
|      **ticket_familyissue:comment_member_ratio**      |      ticket_familyissue:comment_member_ratio      | -4.288  | 0.0001  | 0.0001 | *** |
|       **ticket_familypr:comment_member_ratio**        |       ticket_familypr:comment_member_ratio        | -9.562  | 0.0001  | 0.0001 | *** |
|     **ticket_familyissue:comment_sentiment_mean**     |     ticket_familyissue:comment_sentiment_mean     |  4.387  | 0.0001  | 0.0001 | *** |
|      **ticket_familypr:comment_sentiment_mean**       |      ticket_familypr:comment_sentiment_mean       | -0.6878 |  0.49   |  0.52  |     |
|  **ticket_familyissue:comment_grateful_cumulative**   |  ticket_familyissue:comment_grateful_cumulative   | 0.06044 |  0.95   |  0.95  |     |
|    **ticket_familypr:comment_grateful_cumulative**    |    ticket_familypr:comment_grateful_cumulative    |   3.4   |  0.001  | 0.001  | **  |


```r
write.table(retention_tests,
            file="results/models/model-2.1.tsv", sep="\t")
```


```r
retention_tests$p_val_adjusted = p.adjust(retention_tests$p_value, method="BH")
write.table(retention_tests, file="results/models/model-2.1.tsv")
```

***

### Model 2.2: Hints of different newcomer goals

Both mean sentiment and max negative sentiment are predictive of newcomer
retention. We hypothesize that this might be driven by feedback from the
community, consistent with previous findings that volunteers in software
developer communities are often looking for learning experiences.

We thus now look at whether comment sentiment variance and maximum
positive sentiment are predictive of newcomer retention.


```r
# max positive comment sentiment
retention_predictor = glmer(retained_newcomer ~ comment_sentiment_max_positive + (1 | project),
                            data=retention_frame, family=binomial, nAGQ=0)
retention_comment_sentiment_max_positive = as.data.frame(
  summary(retention_predictor)$coefficients)

# extract coefficients
new_coefs = retention_comment_sentiment_max_positive[, c("Estimate", "Std. Error")]
colnames(new_coefs) = colnames(all_coefs_and_se)
all_coefs_and_se = rbind(
  all_coefs_and_se, new_coefs)

# concatenate
retention_comment_sentiment_max_positive[, "row_names"] = row.names(
  retention_comment_sentiment_max_positive)
retention_comment_sentiment_followups = retention_comment_sentiment_max_positive

# ticket family x max positive comment sentiment
retention_predictor = glmer(
  retained_newcomer ~ 0 + ticket_family + ticket_family:comment_sentiment_max_positive + (1 | project),
  data=retention_frame, family=binomial, nAGQ=0)
retention_comment_sentiment_max_positive = as.data.frame(
  summary(retention_predictor)$coefficients)

# extract coefficients
new_coefs = retention_comment_sentiment_max_positive[, c("Estimate", "Std. Error")]
colnames(new_coefs) = colnames(all_coefs_and_se)
all_coefs_and_se = rbind(
  all_coefs_and_se,
  new_coefs)

# concatenate
retention_comment_sentiment_max_positive[, "row_names"] = row.names(
  retention_comment_sentiment_max_positive)
retention_comment_sentiment_followups = merge(
  retention_comment_sentiment_followups,
  retention_comment_sentiment_max_positive,
  all=TRUE, sort=FALSE)
```



```r
# sentiment variance
retention_predictor = glmer(
  retained_newcomer ~ 0 + comment_sentiment_variance + (1 | project),
  data=retention_frame, family=binomial, nAGQ=0)
retention_comment_sentiment_variance = as.data.frame(
  summary(retention_predictor)$coefficients)

# extract coefficients
new_coefs = retention_comment_sentiment_variance[, c("Estimate", "Std. Error")]
colnames(new_coefs) = colnames(all_coefs_and_se)
all_coefs_and_se_2.1 = rbind(
  all_coefs_and_se,
  new_coefs)

# concatenate
retention_comment_sentiment_variance[, "row_names"] = row.names(
  retention_comment_sentiment_variance)
retention_comment_sentiment_followups = merge(
  retention_comment_sentiment_followups,
  retention_comment_sentiment_variance,
  all=TRUE, sort=FALSE)

# ticket family x sentiment variance
retention_predictor = glmer(
  retained_newcomer ~ 0 + ticket_family + ticket_family:comment_sentiment_variance + (1 | project),
  data=retention_frame, family=binomial, nAGQ=0)
retention_comment_sentiment_variance = as.data.frame(
  summary(retention_predictor)$coefficients)

# extract coefficients
new_coefs = retention_comment_sentiment_variance[, c("Estimate", "Std. Error")]
colnames(new_coefs) = colnames(all_coefs_and_se)
all_coefs_and_se_2.1 = rbind(
  all_coefs_and_se,
  new_coefs)

# concatenate
retention_comment_sentiment_variance[, "row_names"] = row.names(
  retention_comment_sentiment_variance)
retention_comment_sentiment_followups = merge(
  retention_comment_sentiment_followups,
  retention_comment_sentiment_variance,
  all=TRUE, sort=FALSE)
```


```r
# set column names
colnames(retention_comment_sentiment_followups) = c("Estimate", "Std Error", "Z value", "p_value", "model")

# remove unneeded rows
mask = (
  retention_comment_sentiment_followups$model != "(Intercept)" &
    retention_comment_sentiment_followups$model != "ticket_familyissue" &
    retention_comment_sentiment_followups$model != "ticket_familypr")
retention_comment_sentiment_followups = retention_comment_sentiment_followups[mask, ]
rownames(retention_comment_sentiment_followups) = retention_comment_sentiment_followups$model

# extract necessary columns and rename
columns_of_interest = c("Z value", "p_value", "model")
retention_comment_sentiment_followups = select(retention_comment_sentiment_followups, 
                                               one_of(columns_of_interest))
colnames(retention_comment_sentiment_followups) = c("stat", "p_value", "model")

# concatenate with model 2
retention_tests_2.2 = rbind(select(retention_tests, -p_val_adjusted), 
                            retention_comment_sentiment_followups)
```


```r
write.table(retention_tests_2.2,
            file="results/models/model-2.2.tsv", sep="\t")
```


```r
retention_tests$p_val_adjusted = p.adjust(retention_tests$p_value, method="BH")
write.table(retention_tests, file="results/models/model_2.tsv")

retention_tests_2.2$p_val_adjusted = p.adjust(retention_tests_2.2$p_value, method="BH")
write.table(retention_tests_2.2, file="results/models/model_2.2_final_pvalues.tsv")


write.table(
  all_random_effects,
  "results/models/newcomer_retention_ticket_family_random_effects.tsv")
```


```r
pander_clean_anova(retention_tests_2.2[c("model", "stat", "p_value")],
                   rename_columns=FALSE)
```



|                        &nbsp;                         |                       model                       |  stat   | p_value | p_adj  | sig |
|:-----------------------------------------------------:|:-------------------------------------------------:|:-------:|:-------:|:------:|:---:|
|                     **pr-issue**                      |                     pr-issue                      |  5.531  | 0.0001  | 0.0001 | *** |
|                     **open_time**                     |                     open_time                     | -1.296  |  0.195  |  0.25  |     |
|            **comment_grateful_cumulative**            |            comment_grateful_cumulative            |  6.701  | 0.0001  | 0.0001 | *** |
|          **comment_sentiment_max_negative**           |          comment_sentiment_max_negative           |   1.4   |  0.162  | 0.224  |     |
|                **number_of_comments**                 |                number_of_comments                 |  9.35   | 0.0001  | 0.0001 | *** |
|               **comment_member_ratio**                |               comment_member_ratio                | -8.363  | 0.0001  | 0.0001 | *** |
|              **comment_sentiment_mean**               |              comment_sentiment_mean               |  6.341  | 0.0001  | 0.0001 | *** |
|           **ticket_familyissue:open_time**            |           ticket_familyissue:open_time            |  3.298  |  0.001  | 0.002  | **  |
|             **ticket_familypr:open_time**             |             ticket_familypr:open_time             | -2.956  |  0.003  | 0.005  | **  |
| **ticket_familyissue:comment_sentiment_max_negative** | ticket_familyissue:comment_sentiment_max_negative | -1.275  |  0.202  |  0.25  |     |
|  **ticket_familypr:comment_sentiment_max_negative**   |  ticket_familypr:comment_sentiment_max_negative   |  4.107  | 0.0001  | 0.0001 | *** |
|       **ticket_familyissue:number_of_comments**       |       ticket_familyissue:number_of_comments       |  4.011  | 0.0001  | 0.0001 | *** |
|        **ticket_familypr:number_of_comments**         |        ticket_familypr:number_of_comments         |  6.617  | 0.0001  | 0.0001 | *** |
|      **ticket_familyissue:comment_member_ratio**      |      ticket_familyissue:comment_member_ratio      | -4.288  | 0.0001  | 0.0001 | *** |
|       **ticket_familypr:comment_member_ratio**        |       ticket_familypr:comment_member_ratio        | -9.562  | 0.0001  | 0.0001 | *** |
|     **ticket_familyissue:comment_sentiment_mean**     |     ticket_familyissue:comment_sentiment_mean     |  4.387  | 0.0001  | 0.0001 | *** |
|      **ticket_familypr:comment_sentiment_mean**       |      ticket_familypr:comment_sentiment_mean       | -0.6878 |  0.49   |  0.53  |     |
|  **ticket_familyissue:comment_grateful_cumulative**   |  ticket_familyissue:comment_grateful_cumulative   | 0.06044 |  0.95   |  0.95  |     |
|    **ticket_familypr:comment_grateful_cumulative**    |    ticket_familypr:comment_grateful_cumulative    |   3.4   |  0.001  | 0.001  | **  |
|          **comment_sentiment_max_positive**           |          comment_sentiment_max_positive           |  10.87  | 0.0001  | 0.0001 | *** |
| **ticket_familyissue:comment_sentiment_max_positive** | ticket_familyissue:comment_sentiment_max_positive |   5.3   | 0.0001  | 0.0001 | *** |
|  **ticket_familypr:comment_sentiment_max_positive**   |  ticket_familypr:comment_sentiment_max_positive   | 0.4519  |  0.65   |  0.68  |     |
|            **comment_sentiment_variance**             |            comment_sentiment_variance             |  -1.12  |  0.26   |  0.31  |     |
|   **ticket_familyissue:comment_sentiment_variance**   |   ticket_familyissue:comment_sentiment_variance   | -0.9703 |  0.33   |  0.38  |     |
|    **ticket_familypr:comment_sentiment_variance**     |    ticket_familypr:comment_sentiment_variance     |  1.527  |  0.127  | 0.186  |     |

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
* Can we track the enculturation of sentiment and gratitude continuously?
