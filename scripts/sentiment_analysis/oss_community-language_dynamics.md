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

**Date last compiled**:  2020-02-10 19:53:21



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
|      pr       |     36538      |     253495      |



|    project     | ticket_family | unique_tickets | unique_comments |
|:--------------:|:-------------:|:--------------:|:---------------:|
|   matplotlib   |     issue     |      4819      |      28904      |
|   matplotlib   |      pr       |      7385      |      36688      |
|     mayavi     |     issue     |      440       |      1459       |
|     mayavi     |      pr       |      290       |       645       |
|     numpy      |     issue     |      4467      |      27720      |
|     numpy      |      pr       |      5554      |      33253      |
|     pandas     |     issue     |     12991      |      64587      |
|     pandas     |      pr       |     10248      |      69363      |
|  scikit-image  |     issue     |      1174      |      7240       |
|  scikit-image  |      pr       |      2103      |      15362      |
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
253495 unique comments on pull requests. This includes an average of
23191.125 comments on issues per project and an average of 
31686.875 
comments on pull requests per project.

In total, we have 15560 unique commenters,
14147 unique post creators, and
19430 overall unique users.

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

<!-- Now we begin the actual modeling. Our first general question is whether users' -->
<!-- patterns of sentiment differ materially by whether they are a member of the -->
<!-- community versus a nonmember of the community and by their different kinds of -->
<!-- possible contributions (i.e., a posted pull request, a reply to a pull request, -->
<!-- a posted issue, or a reply to an issue). -->

<!-- #### Model 1.1a: Overall effects with linear mixed-effects models -->

<!-- This model presents the analyses in a way that is typical of psychological -->
<!-- analyses. We predict the changes in emotion by community membership and  -->
<!-- activity type, including random effects for project and for author. This -->
<!-- allows us to explore the general patterns of the main and interaction terms, -->
<!-- rather than focusing in on the project-specific variability. -->

<!-- ```{r model-emotion-by-type-and-author} -->

<!-- # do posts and comments materially differ in emotion? -->
<!-- creators_v_commenters_emotion_by_project = lmer(compound_emotion ~ type * author_group  + -->
<!--                                                   (1 | project) + (1 | author_name), -->
<!--                                                 data = sentiment_frame, -->
<!--                                                 REML = FALSE) -->

<!-- ``` -->

<!-- ```{r print-model-emotion-by-type-and-author, eval=TRUE, echo=FALSE} -->

<!-- # print results -->
<!-- pander_lme(creators_v_commenters_emotion_by_project) -->

<!-- ``` -->

<!-- While we see significant differences in the model, interpreting the results is -->
<!-- difficult because of the way that `lmer` handles factor comparisons. All  -->
<!-- factors are compared against a "reference level," the first level in the model. -->
<!-- This makes intepreting models with factors that include more than two levels -->
<!-- incredibly difficult, because the intercept is essentially an interaction term -->
<!-- among all reference levels of all factors. -->

<!-- As a result, we turn to the biostatistics approach of multiple *t*-tests  -->
<!-- (corrected for comparisons) of the model estimates to better understand the  -->
<!-- effects. -->

<!-- #### Model 1.1b: In-depth investigation through *t*-tests of model estimates -->

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



|                                    &nbsp;                                    |                model                | t_stats  | p_value | p_adj  | sig |
|:----------------------------------------------------------------------------:|:-----------------------------------:|:--------:|:-------:|:------:|:---:|
|                             **member-nonmember**                             |             Main Terms              | -0.09303 |  0.93   |  0.94  |     |
|                          **issue_post-issue_reply**                          |             Main Terms              |  -8.829  | 0.0001  | 0.0001 | *** |
|                             **pr_post-pr_reply**                             |             Main Terms              |  -11.45  | 0.0001  | 0.0001 | *** |
|                            **issue_post-pr_post**                            |             Main Terms              | -0.6208  |  0.54   |  0.64  |     |
|                           **issue_reply-pr_reply**                           |             Main Terms              |  -3.33   |  0.001  | 0.002  | **  |
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


```r
all_tests$p_val_adjusted = p.adjust(all_tests$p_value, method="BH")
write.table(all_tests, file="results/models/model-1.1b_final_pvalues.tsv")
```

Finally, let's plot these effects.





![**Figure**. Sentiment by activity type and community membership at the time of posting (member vs. nonmember).](../../figures/sentiment_analysis/ossc-sentiment_membership_contribution-aggregated-knitr.jpg)



![**Figure**. Sentiment by activity type  and community membership at the time of posting (member vs. nonmember) for each project.](../../figures/sentiment_analysis/ossc-sentiment_membership_contribution-by_project-knitr.jpg)

<!-- ### Model 1.2: More plots, this time using means and std estimated from model-fit -->

<!-- Here, we are going to test whether projects differ from the mean. -->

<!-- ```{r eval=TRUE, echo=TRUE} -->
<!-- coefficients_and_se = data.frame( -->
<!--   summary(creators_v_commenters_emotion_by_project)$coefficients) -->

<!-- # get comparison names as rownames -->
<!-- row_names = gsub( -->
<!--   "project", "", gsub( -->
<!--     "author_group", "", gsub( -->
<!--       "type", "", row.names(coefficients_and_se)))) -->

<!-- # replace hyphens in project names with periods -->
<!-- row_names = gsub( -->
<!--   "scikit-", "scikit.", gsub( -->
<!--     "sphinx-", "sphinx.", row_names)) -->

<!-- # convert model estimates to a dataframe -->
<!-- means = coefficients_and_se$Estimate -->
<!-- names(means) = row_names -->

<!-- # convert standard error to dataframe -->
<!-- se = coefficients_and_se$Std..Error -->
<!-- names(se) = row_names -->
<!-- ``` -->

<!-- ```{r} -->
<!-- projects = c("Matplotlib", "Mayavi", "numpy", "pandas", -->
<!--              "scikit-image", "scikit-learn", "scipy", "sphinx-gallery") -->
<!-- ``` -->

<!-- ```{r plot_pr_post_members, fig.width=8} -->
<!-- group_of_interest = "pr_post:member" -->
<!-- rows_to_plot = grep(group_of_interest, names(means)) -->

<!-- bar_centers = barplot(means[rows_to_plot], names.arg=projects, -->
<!--                       main=group_of_interest,     -->
<!--                       cex.names=0.8) -->
<!-- arrows(bar_centers, -->
<!--        means[rows_to_plot] - se[rows_to_plot] ** 2,  -->
<!--        bar_centers, -->
<!--        means[rows_to_plot] + se[rows_to_plot] ** 2, -->
<!--        angle=90, -->
<!--        code=3) -->
<!-- ``` -->

<!-- ```{r plot_pr_post_nonmembers, fig.width=8} -->
<!-- group_of_interest = "pr_post:nonmember" -->
<!-- rows_to_plot = grep(group_of_interest, names(means)) -->

<!-- bar_centers = barplot(means[rows_to_plot], names.arg=projects, -->
<!--                       main=group_of_interest, -->
<!--                       cex.names=0.8) -->

<!-- arrows(bar_centers, -->
<!--        means[rows_to_plot] - se[rows_to_plot] ** 2,  -->
<!--        bar_centers, -->
<!--        means[rows_to_plot] + se[rows_to_plot] ** 2, -->
<!--        angle=90, -->
<!--        code=3) -->
<!-- ``` -->


<!-- ```{r plot_issue_post_members, fig.width=8} -->
<!-- group_of_interest = "issue_post:member" -->
<!-- rows_to_plot = grep(group_of_interest, names(means)) -->

<!-- bar_centers = barplot(means[rows_to_plot], names.arg=projects, -->
<!--                       main=group_of_interest, -->
<!--                       cex.names=0.8 -->
<!-- ) -->
<!-- arrows(bar_centers, -->
<!--        means[rows_to_plot] - se[rows_to_plot] ** 2,  -->
<!--        bar_centers, -->
<!--        means[rows_to_plot] + se[rows_to_plot] ** 2, -->
<!--        angle=90, -->
<!--        code=3) -->
<!-- ``` -->

<!-- ```{r plot_issue_post_nonmembers, fig.width=8} -->
<!-- group_of_interest = "issue_post:nonmember" -->
<!-- rows_to_plot = grep(group_of_interest, names(means)) -->

<!-- bar_centers = barplot(means[rows_to_plot], names.arg=projects, -->
<!--                       main=group_of_interest, -->
<!--                       cex.names=0.8 -->
<!-- ) -->
<!-- arrows(bar_centers, -->
<!--        means[rows_to_plot] - se[rows_to_plot] ** 2,  -->
<!--        bar_centers, -->
<!--        means[rows_to_plot] + se[rows_to_plot] ** 2, -->
<!--        angle=90, -->
<!--        code=3) -->
<!-- ``` -->


<!-- ```{r plot_pr_reply_members, fig.width=8} -->
<!-- group_of_interest = "pr_reply:member" -->
<!-- rows_to_plot = grep(group_of_interest, names(means)) -->

<!-- bar_centers = barplot(means[rows_to_plot], names.arg=projects, -->
<!--                       main=group_of_interest, -->
<!--                       cex.names=0.8) -->
<!-- arrows(bar_centers, -->
<!--        means[rows_to_plot] - se[rows_to_plot] ** 2,  -->
<!--        bar_centers, -->
<!--        means[rows_to_plot] + se[rows_to_plot] ** 2, -->
<!--        angle=90, -->
<!--        code=3) -->
<!-- ``` -->

<!-- ```{r plot_pr_reply_nonmembers, fig.width=8} -->
<!-- group_of_interest = "pr_reply:nonmember" -->
<!-- rows_to_plot = grep(group_of_interest, names(means)) -->

<!-- bar_centers = barplot(means[rows_to_plot], names.arg=projects, -->
<!--                       main=group_of_interest, -->
<!--                       cex.names=0.8) -->
<!-- arrows(bar_centers, -->
<!--        means[rows_to_plot] - se[rows_to_plot] ** 2,  -->
<!--        bar_centers, -->
<!--        means[rows_to_plot] + se[rows_to_plot] ** 2, -->
<!--        angle=90, -->
<!--        code=3) -->
<!-- ``` -->


<!-- ```{r plot_issue_reply_members, fig.width=8} -->
<!-- group_of_interest = "issue_reply:member" -->
<!-- rows_to_plot = grep(group_of_interest, names(means)) -->

<!-- bar_centers = barplot(means[rows_to_plot], names.arg=projects, -->
<!--                       main=group_of_interest, -->
<!--                       cex.names=0.8) -->
<!-- arrows(bar_centers, -->
<!--        means[rows_to_plot] - se[rows_to_plot] ** 2,  -->
<!--        bar_centers, -->
<!--        means[rows_to_plot] + se[rows_to_plot] ** 2, -->
<!--        angle=90, -->
<!--        code=3) -->
<!-- ``` -->

<!-- ```{r plot_issue_reply_nonmembers, fig.width=8} -->
<!-- group_of_interest = "issue_reply:nonmember" -->
<!-- rows_to_plot = grep(group_of_interest, names(means)) -->

<!-- bar_centers = barplot(means[rows_to_plot], names.arg=projects, -->
<!--                       main=group_of_interest, -->
<!--                       cex.names=0.8) -->
<!-- arrows(bar_centers, -->
<!--        means[rows_to_plot] - se[rows_to_plot] ** 2,  -->
<!--        bar_centers, -->
<!--        means[rows_to_plot] + se[rows_to_plot] ** 2, -->
<!--        angle=90, -->
<!--        code=3) -->
<!-- ``` -->

<!-- ### Model 1.1c Do projects differ in emotion between one another? -->

<!-- One versus all minus one type of approach. -->

<!-- ```{r compound_emotion_all_vs_one} -->
<!-- all_project_tests = NA -->
<!-- all_projects = unique(sentiment_frame$project) -->

<!-- # We're going to fit the model for each projects, and concatenate the results -->
<!-- # in a dataframe. Then, we'll apply multiple correction and display the -->
<!-- # results -->
<!-- for(project in all_projects){ -->
<!--   sentiment_frame$test_group = sentiment_frame$project == project -->
<!--   one_versus_all_emotion = lmer( -->
<!--     compound_emotion ~ 0 + type:author_group:test_group + (1|author_name), -->
<!--     data=sentiment_frame, -->
<!--     REML=FALSE) -->

<!--   # Clean up mode -->
<!--   coefficients_and_se = data.frame( -->
<!--     summary(one_versus_all_emotion)$coefficients) -->
<!--   row_names = gsub( -->
<!--     "author_group", "",  -->
<!--     gsub("type", "", -->
<!--          gsub("project", "", row.names(coefficients_and_se)))) -->

<!--   means = coefficients_and_se$Estimate -->
<!--   names(means) = row_names -->
<!--   se = coefficients_and_se$Std..Error -->
<!--   names(se) = row_names -->

<!--   contrasts = c( -->
<!--     "issue_post:member:test_groupTRUE-issue_post:member:test_groupFALSE", -->
<!--     "pr_post:member:test_groupTRUE-pr_post:member:test_groupFALSE", -->
<!--     "issue_reply:member:test_groupTRUE-issue_reply:member:test_groupFALSE", -->
<!--     "pr_reply:member:test_groupTRUE-pr_reply:member:test_groupFALSE", -->
<!--     "issue_post:nonmember:test_groupTRUE-issue_post:nonmember:test_groupFALSE", -->
<!--     "pr_post:nonmember:test_groupTRUE-pr_post:nonmember:test_groupFALSE", -->
<!--     "issue_reply:nonmember:test_groupTRUE-issue_reply:nonmember:test_groupFALSE", -->
<!--     "pr_reply:nonmember:test_groupTRUE-pr_reply:nonmember:test_groupFALSE" -->
<!--   ) -->

<!--   one_versus_all_emotion_tests = compute_t_statistics( -->
<!--     means, se, -->
<!--     contrasts) -->
<!--   one_versus_all_emotion_tests[, "p_value"] = compute_p_value_from_t_stats( -->
<!--     one_versus_all_emotion_tests$t_stats) -->

<!--   # Add unique identifier based on the project of interest in the table. -->
<!--   row.names(one_versus_all_emotion_tests) = gsub( -->
<!--     "test_group", project, -->
<!--     row.names(one_versus_all_emotion_tests)) -->

<!--   if(is.null(dim(all_project_tests))){ -->
<!--     all_project_tests = one_versus_all_emotion_tests -->
<!--   }else{ -->
<!--     all_project_tests = rbind( -->
<!--       all_project_tests, one_versus_all_emotion_tests) -->
<!--   } -->
<!-- } -->
<!-- ``` -->

<!-- Now apply multiple correction and display the results of the analysis. -->

<!-- ```{r one_versus_all_display_results} -->
<!-- pander_clean_anova(all_project_tests, rename_columns=FALSE) -->
<!-- ``` -->

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
|  nonmember   |  pr_reply   |       0        | 32626  |
|  nonmember   |  pr_reply   |       1        |  7298  |
|  nonmember   |  pr_reply   |       2        |  338   |
|  nonmember   |  pr_reply   |       3        |   34   |

Now that we have a better idea of how the underlying data look, let's go ahead
and build our model.

<!-- ```{r model-gratitude-by-type-and-author-and-project-v1, eval = TRUE} -->

<!-- # do users tend to express appreciation and gratitude differently by group and content? -->
<!-- creators_v_commenters_gratitude_by_project = lmer(log(grateful_count + 1) ~ project * author_group * type + -->
<!--                                                     (1 | author_name), -->
<!--                                                   data=sentiment_frame) -->

<!-- # print results -->
<!-- pander_lme(creators_v_commenters_gratitude_by_project) -->

<!-- ``` -->



![**Figure**. Expressions of gratitude by activity type (posted issue, comment on issue, posted pull request, or comment on pull request) and community membership (member vs. nonmember) at the time of posting.](../../figures/sentiment_analysis/ossc-grateful_membership_contribution-knitr.jpg)

<!-- ### Testing Model 1.3 using Model 1.1 methods -->

<!-- #### Model 1.3a: Overall effects with linear mixed-effects models -->

<!-- This model presents the analyses in a way that is typical of psychological -->
<!-- analyses. We predict the changes in emotion by community membership and  -->
<!-- activity type, including random effects for project and for author. This -->
<!-- allows us to explore the general patterns of the main and interaction terms, -->
<!-- rather than focusing in on the project-specific variability. -->

<!-- ```{r retrying-model-1.3} -->

<!-- # do users tend to express appreciation and gratitude differently by group and content? -->
<!-- retrying_model_1.3 = lmer(log(grateful_count + 1) ~ author_group * type + -->
<!--                             (1 | project), -->
<!--                           data=sentiment_frame) -->

<!-- ``` -->

<!-- ```{r print-retrying-model-1.3, eval=TRUE, echo=FALSE} -->

<!-- # print results -->
<!-- pander_lme(retrying_model_1.3) -->

<!-- ``` -->

<!-- While we see significant differences in the model, interpreting the results is -->
<!-- difficult because of the way that `lmer` handles factor comparisons. All  -->
<!-- factors are compared against a "reference level," the first level in the model. -->
<!-- This makes intepreting models with factors that include more than two levels -->
<!-- incredibly difficult, because the intercept is essentially an interaction term -->
<!-- among all reference levels of all factors. -->

<!-- As a result, we turn to the biostatistics approach of multiple *t*-tests  -->
<!-- (corrected for comparisons) of the model estimates to better understand the  -->
<!-- effects. -->

<!-- #### Model 1.3b: In-depth investigation through *t*-tests of model estimates -->

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
|                             **member-nonmember**                             |             Main Terms              |  -4.341  | 0.0001  | 0.0001 | *** |
|                          **issue_post-issue_reply**                          |             Main Terms              |  -1.622  |  0.105  | 0.132  |     |
|                             **pr_post-pr_reply**                             |             Main Terms              |  -6.924  | 0.0001  | 0.0001 | *** |
|                            **issue_post-pr_post**                            |             Main Terms              |  2.336   |  0.02   | 0.026  |  *  |
|                           **issue_reply-pr_reply**                           |             Main Terms              |  -2.965  |  0.003  | 0.004  | **  |
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
```


```r
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


retention_predictor = glmer(retained_newcomer ~ comment_sentiment_max_positive + (1 | project),
                            data=retention_frame, family=binomial, nAGQ=0)
retention_comment_sentiment_max_positive = as.data.frame(
  summary(retention_predictor)$coefficients)
new_coefs = retention_comment_sentiment_max_positive[, c("Estimate", "Std. Error")]
colnames(new_coefs) = colnames(all_coefs_and_se)
all_coefs_and_se = rbind(
  all_coefs_and_se, new_coefs)
retention_comment_sentiment_max_positive[, "row_names"] = row.names(
  retention_comment_sentiment_max_positive)
retention_tests_continuous = merge(
  retention_tests_continuous,
  retention_comment_sentiment_max_positive,
  all=TRUE, sort=FALSE)


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
```

Now let's do interaction terms between contribution types and everything else.


```r
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

retention_predictor = glmer(
  retained_newcomer ~ 0 + ticket_family + ticket_family:comment_sentiment_max_positive + (1 | project),
  data=retention_frame, family=binomial, nAGQ=0)
retention_comment_sentiment_max_positive = as.data.frame(
  summary(retention_predictor)$coefficients)
new_coefs = retention_comment_sentiment_max_positive[, c("Estimate", "Std. Error")]
colnames(new_coefs) = colnames(all_coefs_and_se)
all_coefs_and_se = rbind(
  all_coefs_and_se,
  new_coefs)
retention_comment_sentiment_max_positive[, "row_names"] = row.names(
  retention_comment_sentiment_max_positive)
retention_tests_continuous = merge(
  retention_tests_continuous,
  retention_comment_sentiment_max_positive,
  all=TRUE, sort=FALSE)


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
|                     **pr-issue**                      |                     pr-issue                      |  5.542  | 0.0001  | 0.0001 | *** |
|                     **open_time**                     |                     open_time                     | -0.9746 |  0.33   |  0.38  |     |
|            **comment_grateful_cumulative**            |            comment_grateful_cumulative            |  6.722  | 0.0001  | 0.0001 | *** |
|          **comment_sentiment_max_negative**           |          comment_sentiment_max_negative           |  1.367  |  0.172  | 0.222  |     |
|          **comment_sentiment_max_positive**           |          comment_sentiment_max_positive           |  10.86  | 0.0001  | 0.0001 | *** |
|                **number_of_comments**                 |                number_of_comments                 |  9.338  | 0.0001  | 0.0001 | *** |
|               **comment_member_ratio**                |               comment_member_ratio                | -8.344  | 0.0001  | 0.0001 | *** |
|              **comment_sentiment_mean**               |              comment_sentiment_mean               |  6.342  | 0.0001  | 0.0001 | *** |
|           **ticket_familyissue:open_time**            |           ticket_familyissue:open_time            |  3.596  | 0.0003  |   0    | *** |
|             **ticket_familypr:open_time**             |             ticket_familypr:open_time             | -2.903  |  0.004  | 0.005  | **  |
| **ticket_familyissue:comment_sentiment_max_negative** | ticket_familyissue:comment_sentiment_max_negative | -1.276  |  0.202  | 0.247  |     |
|  **ticket_familypr:comment_sentiment_max_negative**   |  ticket_familypr:comment_sentiment_max_negative   |  3.872  | 0.0001  | 0.0002 | *** |
| **ticket_familyissue:comment_sentiment_max_positive** | ticket_familyissue:comment_sentiment_max_positive |  5.301  | 0.0001  | 0.0001 | *** |
|  **ticket_familypr:comment_sentiment_max_positive**   |  ticket_familypr:comment_sentiment_max_positive   |  0.395  |  0.69   |  0.73  |     |
|       **ticket_familyissue:number_of_comments**       |       ticket_familyissue:number_of_comments       |  4.012  | 0.0001  | 0.0001 | *** |
|        **ticket_familypr:number_of_comments**         |        ticket_familypr:number_of_comments         |  6.535  | 0.0001  | 0.0001 | *** |
|      **ticket_familyissue:comment_member_ratio**      |      ticket_familyissue:comment_member_ratio      | -4.281  | 0.0001  | 0.0001 | *** |
|       **ticket_familypr:comment_member_ratio**        |       ticket_familypr:comment_member_ratio        | -8.937  | 0.0001  | 0.0001 | *** |
|     **ticket_familyissue:comment_sentiment_mean**     |     ticket_familyissue:comment_sentiment_mean     |  4.387  | 0.0001  | 0.0001 | *** |
|      **ticket_familypr:comment_sentiment_mean**       |      ticket_familypr:comment_sentiment_mean       | -0.8239 |  0.41   |  0.45  |     |
|  **ticket_familyissue:comment_grateful_cumulative**   |  ticket_familyissue:comment_grateful_cumulative   | 0.05856 |  0.95   |  0.95  |     |
|    **ticket_familypr:comment_grateful_cumulative**    |    ticket_familypr:comment_grateful_cumulative    |  3.011  |  0.003  | 0.004  | **  |


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

We thus now look at whether comment sentiment variance is predictive of
newcomer retention.


```r
retention_predictor = glmer(
  retained_newcomer ~ 0 + ticket_family + ticket_family:comment_sentiment_variance + (1 | project),
  data=retention_frame, family=binomial, nAGQ=0)
retention_comment_sentiment_variance = as.data.frame(
  summary(retention_predictor)$coefficients)

new_coefs = retention_comment_sentiment_variance[, c("Estimate", "Std. Error")]
colnames(new_coefs) = colnames(all_coefs_and_se)
all_coefs_and_se_2.1 = rbind(
  all_coefs_and_se,
  new_coefs)

colnames(retention_comment_sentiment_variance) = c("Estimate", "Std Error", "Z value", "p_value")
pander_clean_anova(retention_comment_sentiment_variance, rename_columns=FALSE)
```



|                      &nbsp;                       | Estimate | Std Error | Z value | p_value | p_adj  | sig |
|:-------------------------------------------------:|:--------:|:---------:|:-------:|:-------:|:------:|:---:|
|              **ticket_familyissue**               | -0.7759  |  0.07294  | -10.64  | 0.0001  | 0.0001 | *** |
|                **ticket_familypr**                | -0.2323  |  0.08432  | -2.755  |  0.006  | 0.012  |  *  |
| **ticket_familyissue:comment_sentiment_variance** | -0.1616  |   0.166   | -0.9735 |  0.33   |  0.33  |     |
|  **ticket_familypr:comment_sentiment_variance**   |  0.3532  |  0.2869   |  1.231  |  0.218  |  0.29  |     |


```r
retention_comment_sentiment_variance[, "row_names"] = row.names(
  retention_comment_sentiment_variance)

mask = (
  retention_comment_sentiment_variance$row_names != "(Intercept)" &
    retention_comment_sentiment_variance$row_names != "ticket_familyissue" &
    retention_comment_sentiment_variance$row_names != "ticket_familypr")
retention_comment_sentiment_variance = retention_comment_sentiment_variance[mask, ]
row.names(retention_comment_sentiment_variance) = retention_comment_sentiment_variance[,
                                                                                       "row_names"] 

columns_of_interest = c("Z value", "p_value")
retention_comment_sentiment_variance = select(retention_comment_sentiment_variance, 
                                              one_of(columns_of_interest))
retention_comment_sentiment_variance["model"] = row.names(retention_comment_sentiment_variance)
colnames(retention_comment_sentiment_variance) = c("stat", "p_value", "model")
retention_tests_2.1 = rbind(select(retention_tests, -p_val_adjusted), 
                            retention_comment_sentiment_variance)
```


```r
write.table(retention_tests_2.1,
            file="results/models/model-2.2.tsv", sep="\t")
```


```r
retention_tests_2.1$p_val_adjusted = p.adjust(retention_tests_2.1$p_value, method="BH")
write.table(retention_tests, file="results/models/model-2.2.tsv")
```


```r
pander_clean_anova(retention_tests_2.1[c("model", "stat", "p_value")],
                   rename_columns=FALSE)
```



|                        &nbsp;                         |                       model                       |  stat   | p_value | p_adj  | sig |
|:-----------------------------------------------------:|:-------------------------------------------------:|:-------:|:-------:|:------:|:---:|
|                     **pr-issue**                      |                     pr-issue                      |  5.542  | 0.0001  | 0.0001 | *** |
|                     **open_time**                     |                     open_time                     | -0.9746 |  0.33   |  0.38  |     |
|            **comment_grateful_cumulative**            |            comment_grateful_cumulative            |  6.722  | 0.0001  | 0.0001 | *** |
|          **comment_sentiment_max_negative**           |          comment_sentiment_max_negative           |  1.367  |  0.172  | 0.242  |     |
|          **comment_sentiment_max_positive**           |          comment_sentiment_max_positive           |  10.86  | 0.0001  | 0.0001 | *** |
|                **number_of_comments**                 |                number_of_comments                 |  9.338  | 0.0001  | 0.0001 | *** |
|               **comment_member_ratio**                |               comment_member_ratio                | -8.344  | 0.0001  | 0.0001 | *** |
|              **comment_sentiment_mean**               |              comment_sentiment_mean               |  6.342  | 0.0001  | 0.0001 | *** |
|           **ticket_familyissue:open_time**            |           ticket_familyissue:open_time            |  3.596  | 0.0003  | 0.001  | **  |
|             **ticket_familypr:open_time**             |             ticket_familypr:open_time             | -2.903  |  0.004  | 0.006  | **  |
| **ticket_familyissue:comment_sentiment_max_negative** | ticket_familyissue:comment_sentiment_max_negative | -1.276  |  0.202  |  0.27  |     |
|  **ticket_familypr:comment_sentiment_max_negative**   |  ticket_familypr:comment_sentiment_max_negative   |  3.872  | 0.0001  | 0.0002 | *** |
| **ticket_familyissue:comment_sentiment_max_positive** | ticket_familyissue:comment_sentiment_max_positive |  5.301  | 0.0001  | 0.0001 | *** |
|  **ticket_familypr:comment_sentiment_max_positive**   |  ticket_familypr:comment_sentiment_max_positive   |  0.395  |  0.69   |  0.72  |     |
|       **ticket_familyissue:number_of_comments**       |       ticket_familyissue:number_of_comments       |  4.012  | 0.0001  | 0.0001 | *** |
|        **ticket_familypr:number_of_comments**         |        ticket_familypr:number_of_comments         |  6.535  | 0.0001  | 0.0001 | *** |
|      **ticket_familyissue:comment_member_ratio**      |      ticket_familyissue:comment_member_ratio      | -4.281  | 0.0001  | 0.0001 | *** |
|       **ticket_familypr:comment_member_ratio**        |       ticket_familypr:comment_member_ratio        | -8.937  | 0.0001  | 0.0001 | *** |
|     **ticket_familyissue:comment_sentiment_mean**     |     ticket_familyissue:comment_sentiment_mean     |  4.387  | 0.0001  | 0.0001 | *** |
|      **ticket_familypr:comment_sentiment_mean**       |      ticket_familypr:comment_sentiment_mean       | -0.8239 |  0.41   |  0.45  |     |
|  **ticket_familyissue:comment_grateful_cumulative**   |  ticket_familyissue:comment_grateful_cumulative   | 0.05856 |  0.95   |  0.95  |     |
|    **ticket_familypr:comment_grateful_cumulative**    |    ticket_familypr:comment_grateful_cumulative    |  3.011  |  0.003  | 0.004  | **  |
|   **ticket_familyissue:comment_sentiment_variance**   |   ticket_familyissue:comment_sentiment_variance   | -0.9735 |  0.33   |  0.38  |     |
|    **ticket_familypr:comment_sentiment_variance**     |    ticket_familypr:comment_sentiment_variance     |  1.231  |  0.218  |  0.28  |     |

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
