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

<<<<<<< HEAD
**Date last compiled**:  2020-02-10 19:53:21
=======
**Date last compiled**:  2020-02-05 17:11:23
>>>>>>> 7ea8a4e28ec283d9f6e930c3ad1268db6826f1dc



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



<<<<<<< HEAD
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
=======
|    project     | unique_tickets | unique_comments |
|:--------------:|:--------------:|:---------------:|
|   matplotlib   |     12204      |      65592      |
|     mayavi     |      730       |      2104       |
|     numpy      |     10021      |      60973      |
|     pandas     |     23239      |     132489      |
|  scikit-image  |      3277      |      22360      |
|  scikit-learn  |     11649      |     107930      |
|     scipy      |      7142      |      42967      |
| sphinx-gallery |      409       |      2906       |
>>>>>>> 7ea8a4e28ec283d9f6e930c3ad1268db6826f1dc

Our dataset includes 8 unique projects. The dataset has
total of 32133 unique posted issues, with a mean of 
4016.625 posted issues per project. It also includes a total of 
36538 unique posted pull requests, with a mean of 
4567.25 posted pull requests per project.

<<<<<<< HEAD
On these contributions, the dataset includes
185529 unique comments on issues and 
253495 unique comments on pull requests. This includes an average of
23191.125 comments on issues per project and an average of 
31686.875 
comments on pull requests per project.

In total, we have 15560 unique commenters,
14147 unique post creators, and
19430 overall unique users.
=======
On these tickets, the dataset includes
437321 unique comments, with
54665.125 average comments per project.

In total, we have 15559 unique commenters,
14147 unique ticket-creators, and
19429 overall unique users.
>>>>>>> 7ea8a4e28ec283d9f6e930c3ad1268db6826f1dc

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

<<<<<<< HEAD
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
=======
```r
# do tickets and comments materially differ in emotion?
creators_v_commenters_emotion_by_project = lmer(compound_emotion ~ type * author_group  +
                                                  (1 | project) + (1 | author_name),
                                                data = sentiment_frame,
                                                REML = FALSE)
```


|                  &nbsp;                   | Estimate  | Std..Error |   df   | t.value |   p    | p_adj  | sig |
|:-----------------------------------------:|:---------:|:----------:|:------:|:-------:|:------:|:------:|:---:|
|              **(Intercept)**              |  0.07003  |  0.008879  | 11.87  |  7.887  | 0.0001 | 0.0001 | *** |
|            **typeissue_reply**            |  0.09656  |  0.003695  | 493838 |  26.14  | 0.0001 | 0.0001 | *** |
|              **typepr_post**              | -0.002869 |  0.004434  | 494937 | -0.6469 |  0.52  |  0.59  |     |
|             **typepr_reply**              |  0.1389   |  0.003681  | 495617 |  37.74  | 0.0001 | 0.0001 | *** |
|         **author_groupnonmember**         | 0.009317  |  0.005375  | 308636 |  1.733  | 0.083  | 0.111  |     |
| **typeissue_reply:author_groupnonmember** |  0.01915  |  0.00528   | 490454 |  3.628  | 0.0003 |   0    | *** |
|   **typepr_post:author_groupnonmember**   |  0.02472  |  0.006801  | 445432 |  3.635  | 0.0003 |   0    | *** |
|  **typepr_reply:author_groupnonmember**   | -0.002818 |  0.005585  | 350072 | -0.5046 |  0.61  |  0.61  |     |

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
>>>>>>> 7ea8a4e28ec283d9f6e930c3ad1268db6826f1dc

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

<<<<<<< HEAD
Run *t*-tests among levels and prepare for the Model 1.1 table later.
=======
```
## Warning in checkConv(attr(opt, "derivs"), opt$par, ctrl =
## control$checkConv, : Model failed to converge with max|grad| = 0.00294682
## (tol = 0.002, component 1)
```

Run *t*-tests among levels and prepare for the Model 1.1b table later.
>>>>>>> 7ea8a4e28ec283d9f6e930c3ad1268db6826f1dc


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

<<<<<<< HEAD
### Model 1.2: Time-course analysis for sentiment
=======

```r
pander_clean_anova(all_project_tests, rename_columns=FALSE)
```



|                                         &nbsp;                                         | t_stats  | p_value | p_adj  | sig |
|:--------------------------------------------------------------------------------------:|:--------:|:-------:|:------:|:---:|
|              **issue_post:member:numpyTRUE-issue_post:member:numpyFALSE**              |  -4.767  | 0.0001  | 0.0001 | *** |
|                 **pr_post:member:numpyTRUE-pr_post:member:numpyFALSE**                 |  -2.576  |  0.01   | 0.028  |  *  |
|             **issue_reply:member:numpyTRUE-issue_reply:member:numpyFALSE**             |  -5.296  | 0.0001  | 0.0001 | *** |
|                **pr_reply:member:numpyTRUE-pr_reply:member:numpyFALSE**                |  0.2195  |  0.83   |  0.88  |     |
|           **issue_post:nonmember:numpyTRUE-issue_post:nonmember:numpyFALSE**           |  -6.621  | 0.0001  | 0.0001 | *** |
|              **pr_post:nonmember:numpyTRUE-pr_post:nonmember:numpyFALSE**              |  -4.603  | 0.0001  | 0.0001 | *** |
|          **issue_reply:nonmember:numpyTRUE-issue_reply:nonmember:numpyFALSE**          |  -5.686  | 0.0001  | 0.0001 | *** |
|             **pr_reply:nonmember:numpyTRUE-pr_reply:nonmember:numpyFALSE**             |  -1.111  |  0.27   |  0.38  |     |
|       **issue_post:member:scikit-learnTRUE-issue_post:member:scikit-learnFALSE**       | -0.01578 |  0.99   |  0.99  |     |
|          **pr_post:member:scikit-learnTRUE-pr_post:member:scikit-learnFALSE**          |  3.401   |  0.001  | 0.003  | **  |
|      **issue_reply:member:scikit-learnTRUE-issue_reply:member:scikit-learnFALSE**      |  0.5669  |  0.57   |  0.7   |     |
|         **pr_reply:member:scikit-learnTRUE-pr_reply:member:scikit-learnFALSE**         |  1.545   |  0.122  | 0.201  |     |
|    **issue_post:nonmember:scikit-learnTRUE-issue_post:nonmember:scikit-learnFALSE**    |  0.7037  |  0.48   |  0.63  |     |
|       **pr_post:nonmember:scikit-learnTRUE-pr_post:nonmember:scikit-learnFALSE**       | -0.5547  |  0.58   |  0.7   |     |
|   **issue_reply:nonmember:scikit-learnTRUE-issue_reply:nonmember:scikit-learnFALSE**   |  1.378   |  0.168  |  0.26  |     |
|      **pr_reply:nonmember:scikit-learnTRUE-pr_reply:nonmember:scikit-learnFALSE**      |  2.229   |  0.026  | 0.057  |  .  |
|              **issue_post:member:scipyTRUE-issue_post:member:scipyFALSE**              |  -3.126  |  0.002  | 0.005  | **  |
|                 **pr_post:member:scipyTRUE-pr_post:member:scipyFALSE**                 | -0.5711  |  0.57   |  0.7   |     |
|             **issue_reply:member:scipyTRUE-issue_reply:member:scipyFALSE**             | -0.1885  |  0.85   |  0.89  |     |
|                **pr_reply:member:scipyTRUE-pr_reply:member:scipyFALSE**                |   5.35   | 0.0001  | 0.0001 | *** |
|           **issue_post:nonmember:scipyTRUE-issue_post:nonmember:scipyFALSE**           | -0.2518  |   0.8   |  0.87  |     |
|              **pr_post:nonmember:scipyTRUE-pr_post:nonmember:scipyFALSE**              |  1.556   |  0.12   | 0.201  |     |
|          **issue_reply:nonmember:scipyTRUE-issue_reply:nonmember:scipyFALSE**          |  3.288   |  0.001  | 0.003  | **  |
|             **pr_reply:nonmember:scipyTRUE-pr_reply:nonmember:scipyFALSE**             |  5.891   | 0.0001  | 0.0001 | *** |
|             **issue_post:member:mayaviTRUE-issue_post:member:mayaviFALSE**             |  -2.028  |  0.043  | 0.078  |  .  |
|                **pr_post:member:mayaviTRUE-pr_post:member:mayaviFALSE**                |  -2.456  |  0.014  | 0.035  |  *  |
|            **issue_reply:member:mayaviTRUE-issue_reply:member:mayaviFALSE**            |  -2.502  |  0.012  | 0.033  |  *  |
|               **pr_reply:member:mayaviTRUE-pr_reply:member:mayaviFALSE**               |  -3.299  |  0.001  | 0.003  | **  |
|          **issue_post:nonmember:mayaviTRUE-issue_post:nonmember:mayaviFALSE**          | -0.9843  |  0.32   |  0.45  |     |
|             **pr_post:nonmember:mayaviTRUE-pr_post:nonmember:mayaviFALSE**             |  -2.183  |  0.029  | 0.062  |  .  |
|         **issue_reply:nonmember:mayaviTRUE-issue_reply:nonmember:mayaviFALSE**         |  -3.541  | 0.0004  | 0.002  | **  |
|            **pr_reply:nonmember:mayaviTRUE-pr_reply:nonmember:mayaviFALSE**            | -0.5287  |   0.6   |  0.71  |     |
|     **issue_post:member:sphinx-galleryTRUE-issue_post:member:sphinx-galleryFALSE**     |  0.0217  |  0.98   |  0.99  |     |
|        **pr_post:member:sphinx-galleryTRUE-pr_post:member:sphinx-galleryFALSE**        |   0.56   |  0.58   |  0.7   |     |
|    **issue_reply:member:sphinx-galleryTRUE-issue_reply:member:sphinx-galleryFALSE**    |  4.149   | 0.0001  | 0.0002 | *** |
|       **pr_reply:member:sphinx-galleryTRUE-pr_reply:member:sphinx-galleryFALSE**       | -0.03689 |  0.97   |  0.99  |     |
|  **issue_post:nonmember:sphinx-galleryTRUE-issue_post:nonmember:sphinx-galleryFALSE**  |  -0.878  |  0.38   |  0.51  |     |
|     **pr_post:nonmember:sphinx-galleryTRUE-pr_post:nonmember:sphinx-galleryFALSE**     |  1.723   |  0.085  | 0.147  |     |
| **issue_reply:nonmember:sphinx-galleryTRUE-issue_reply:nonmember:sphinx-galleryFALSE** |  2.097   |  0.036  | 0.072  |  .  |
|    **pr_reply:nonmember:sphinx-galleryTRUE-pr_reply:nonmember:sphinx-galleryFALSE**    | -0.3273  |  0.74   |  0.82  |     |
|         **issue_post:member:matplotlibTRUE-issue_post:member:matplotlibFALSE**         | -0.3683  |  0.71   |  0.81  |     |
|            **pr_post:member:matplotlibTRUE-pr_post:member:matplotlibFALSE**            |  0.9646  |  0.34   |  0.46  |     |
|        **issue_reply:member:matplotlibTRUE-issue_reply:member:matplotlibFALSE**        |  -1.243  |  0.214  |  0.33  |     |
|           **pr_reply:member:matplotlibTRUE-pr_reply:member:matplotlibFALSE**           |  -4.55   | 0.0001  | 0.0001 | *** |
|      **issue_post:nonmember:matplotlibTRUE-issue_post:nonmember:matplotlibFALSE**      |  0.3523  |  0.72   |  0.81  |     |
|         **pr_post:nonmember:matplotlibTRUE-pr_post:nonmember:matplotlibFALSE**         |  -1.514  |  0.13   | 0.208  |     |
|     **issue_reply:nonmember:matplotlibTRUE-issue_reply:nonmember:matplotlibFALSE**     |  -3.287  |  0.001  | 0.003  | **  |
|        **pr_reply:nonmember:matplotlibTRUE-pr_reply:nonmember:matplotlibFALSE**        |  -2.078  |  0.038  | 0.073  |  .  |
|       **issue_post:member:scikit-imageTRUE-issue_post:member:scikit-imageFALSE**       |  -2.482  |  0.013  | 0.033  |  *  |
|          **pr_post:member:scikit-imageTRUE-pr_post:member:scikit-imageFALSE**          |  2.415   |  0.016  | 0.037  |  *  |
|      **issue_reply:member:scikit-imageTRUE-issue_reply:member:scikit-imageFALSE**      |   2.05   |  0.04   | 0.076  |  .  |
|         **pr_reply:member:scikit-imageTRUE-pr_reply:member:scikit-imageFALSE**         |  3.245   |  0.001  | 0.004  | **  |
|    **issue_post:nonmember:scikit-imageTRUE-issue_post:nonmember:scikit-imageFALSE**    |  -1.204  |  0.229  |  0.34  |     |
|       **pr_post:nonmember:scikit-imageTRUE-pr_post:nonmember:scikit-imageFALSE**       |   8.97   | 0.0001  | 0.0001 | *** |
|   **issue_reply:nonmember:scikit-imageTRUE-issue_reply:nonmember:scikit-imageFALSE**   |  1.139   |  0.26   |  0.37  |     |
|      **pr_reply:nonmember:scikit-imageTRUE-pr_reply:nonmember:scikit-imageFALSE**      |  2.161   |  0.031  | 0.063  |  .  |
|             **issue_post:member:pandasTRUE-issue_post:member:pandasFALSE**             |  4.903   | 0.0001  | 0.0001 | *** |
|                **pr_post:member:pandasTRUE-pr_post:member:pandasFALSE**                |  -2.956  |  0.003  | 0.009  | **  |
|            **issue_reply:member:pandasTRUE-issue_reply:member:pandasFALSE**            |  1.732   |  0.083  | 0.147  |     |
|               **pr_reply:member:pandasTRUE-pr_reply:member:pandasFALSE**               |  -2.388  |  0.017  | 0.039  |  *  |
|          **issue_post:nonmember:pandasTRUE-issue_post:nonmember:pandasFALSE**          |    5     | 0.0001  | 0.0001 | *** |
|             **pr_post:nonmember:pandasTRUE-pr_post:nonmember:pandasFALSE**             | -0.4006  |  0.69   |  0.8   |     |
|         **issue_reply:nonmember:pandasTRUE-issue_reply:nonmember:pandasFALSE**         |  3.657   | 0.0003  | 0.001  | **  |
|            **pr_reply:nonmember:pandasTRUE-pr_reply:nonmember:pandasFALSE**            |  -5.427  | 0.0001  | 0.0001 | *** |

### Model 1.2 time-course analysis
>>>>>>> 7ea8a4e28ec283d9f6e930c3ad1268db6826f1dc

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

<!-- ```{r model-gratitude-by-type-and-author-and-project-v1, eval = TRUE} -->

<<<<<<< HEAD
<!-- # do users tend to express appreciation and gratitude differently by group and content? -->
<!-- creators_v_commenters_gratitude_by_project = lmer(log(grateful_count + 1) ~ project * author_group * type + -->
<!--                                                     (1 | author_name), -->
<!--                                                   data=sentiment_frame) -->
=======
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
|                         **(Intercept)**                         |  0.08927  |  0.005863  | 473533 |  15.23  | 0.0001 | 0.0001 | *** |
|                        **projectmayavi**                        | -0.005475 |  0.02914   | 483375 | -0.1879 |  0.85  |  0.89  |     |
|                        **projectnumpy**                         | -0.01739  |  0.007616  | 495363 | -2.283  | 0.022  | 0.048  |  *  |
|                        **projectpandas**                        | -0.03167  |  0.006514  | 504365 | -4.862  | 0.0001 | 0.0001 | *** |
|                     **projectscikit-image**                     |  -0.0582  |  0.01122   | 494987 |  -5.19  | 0.0001 | 0.0001 | *** |
|                     **projectscikit-learn**                     | -0.03577  |  0.007518  | 501401 | -4.757  | 0.0001 | 0.0001 | *** |
|                        **projectscipy**                         | -0.01449  |  0.009397  | 493304 | -1.542  | 0.123  | 0.207  |     |
|                    **projectsphinx-gallery**                    | -0.01804  |  0.02276   | 488509 | -0.7927 |  0.43  |  0.58  |     |
|                    **author_groupnonmember**                    | -0.02037  |  0.007041  | 489322 | -2.893  | 0.004  |  0.01  |  *  |
|                       **typeissue_reply**                       |  0.02565  |  0.005453  | 489169 |  4.703  | 0.0001 | 0.0001 | *** |
|                         **typepr_post**                         |  0.00261  |  0.006001  | 489437 | 0.4348  |  0.66  |  0.79  |     |
|                        **typepr_reply**                         |  0.05334  |  0.005394  | 489497 |  9.889  | 0.0001 | 0.0001 | *** |
|             **projectmayavi:author_groupnonmember**             |  0.08557  |  0.03138   | 478905 |  2.727  | 0.006  | 0.016  |  *  |
|             **projectnumpy:author_groupnonmember**              | 0.009887  |  0.009776  | 488835 |  1.011  |  0.31  |  0.45  |     |
|             **projectpandas:author_groupnonmember**             |  0.01497  |  0.008184  | 483566 |  1.829  | 0.067  | 0.123  |     |
|          **projectscikit-image:author_groupnonmember**          |  0.07382  |   0.015    | 477106 |  4.92   | 0.0001 | 0.0001 | *** |
|          **projectscikit-learn:author_groupnonmember**          |  0.05511  |  0.009512  | 482515 |  5.794  | 0.0001 | 0.0001 | *** |
|             **projectscipy:author_groupnonmember**              |  0.02365  |  0.01145   | 495829 |  2.066  | 0.039  | 0.078  |  .  |
|         **projectsphinx-gallery:author_groupnonmember**         |  0.05711  |  0.03197   | 501402 |  1.786  | 0.074  | 0.132  |     |
|                **projectmayavi:typeissue_reply**                | 0.001116  |  0.02606   | 488433 | 0.04281 |  0.97  |  0.97  |     |
|                **projectnumpy:typeissue_reply**                 | -0.007651 |  0.007465  | 488365 | -1.025  |  0.31  |  0.45  |     |
|                **projectpandas:typeissue_reply**                |  0.01468  |  0.006132  | 489047 |  2.394  | 0.017  | 0.037  |  *  |
|             **projectscikit-image:typeissue_reply**             |  0.0345   |  0.01099   | 487474 |  3.141  | 0.002  | 0.004  | **  |
|             **projectscikit-learn:typeissue_reply**             |  0.0184   |  0.007181  | 488405 |  2.562  |  0.01  | 0.025  |  *  |
|                **projectscipy:typeissue_reply**                 | 0.001002  |  0.009368  | 487951 |  0.107  |  0.92  |  0.93  |     |
|            **projectsphinx-gallery:typeissue_reply**            | -0.006237 |  0.02377   | 487246 | -0.2624 |  0.79  |  0.85  |     |
|                  **projectmayavi:typepr_post**                  | -0.03732  |  0.02873   | 487493 | -1.299  | 0.194  |  0.3   |     |
|                  **projectnumpy:typepr_post**                   | -0.01123  |  0.008498  | 488478 | -1.322  | 0.186  |  0.3   |     |
|                  **projectpandas:typepr_post**                  | 0.002879  |  0.007039  | 489355 |  0.409  |  0.68  |  0.79  |     |
|               **projectscikit-image:typepr_post**               |  0.01147  |  0.01224   | 487617 | 0.9371  |  0.35  |  0.5   |     |
|               **projectscikit-learn:typepr_post**               | -0.004068 |  0.008324  | 488559 | -0.4887 |  0.62  |  0.77  |     |
|                  **projectscipy:typepr_post**                   | -0.006659 |  0.01031   | 488090 | -0.6459 |  0.52  |  0.68  |     |
|              **projectsphinx-gallery:typepr_post**              | -0.00443  |   0.0282   | 487266 | -0.1571 |  0.88  |  0.9   |     |
|                 **projectmayavi:typepr_reply**                  |  0.1147   |  0.02653   | 487881 |  4.323  | 0.0001 | 0.0001 | *** |
|                  **projectnumpy:typepr_reply**                  |  0.02763  |  0.007457  | 488659 |  3.706  | 0.0002 | 0.001  | **  |
|                 **projectpandas:typepr_reply**                  |  0.04779  |  0.006091  | 489483 |  7.846  | 0.0001 | 0.0001 | *** |
|              **projectscikit-image:typepr_reply**               |  0.06863  |  0.01074   | 487624 |  6.39   | 0.0001 | 0.0001 | *** |
|              **projectscikit-learn:typepr_reply**               |  0.03854  |  0.007085  | 488716 |  5.439  | 0.0001 | 0.0001 | *** |
|                  **projectscipy:typepr_reply**                  |  0.04695  |  0.00925   | 488144 |  5.076  | 0.0001 | 0.0001 | *** |
|             **projectsphinx-gallery:typepr_reply**              |  0.01066  |  0.02318   | 487373 |  0.46   |  0.65  |  0.78  |     |
|            **author_groupnonmember:typeissue_reply**            |  0.05936  |  0.007274  | 505026 |  8.161  | 0.0001 | 0.0001 | *** |
|              **author_groupnonmember:typepr_post**              | -0.02032  |  0.009104  | 486377 | -2.232  | 0.026  | 0.053  |  .  |
|             **author_groupnonmember:typepr_reply**              |  0.03778  |  0.007817  | 467812 |  4.834  | 0.0001 | 0.0001 | *** |
|     **projectmayavi:author_groupnonmember:typeissue_reply**     | -0.05686  |  0.03007   | 505599 | -1.891  | 0.059  | 0.114  |     |
|     **projectnumpy:author_groupnonmember:typeissue_reply**      |  0.01268  |  0.01032   | 503471 |  1.228  |  0.22  |  0.33  |     |
|     **projectpandas:author_groupnonmember:typeissue_reply**     | -0.002151 |  0.008518  | 503323 | -0.2525 |  0.8   |  0.85  |     |
|  **projectscikit-image:author_groupnonmember:typeissue_reply**  | -0.06066  |  0.01584   | 503107 | -3.829  | 0.0001 | 0.0004 | *** |
|  **projectscikit-learn:author_groupnonmember:typeissue_reply**  | -0.05761  |  0.009848  | 502140 |  -5.85  | 0.0001 | 0.0001 | *** |
|     **projectscipy:author_groupnonmember:typeissue_reply**      | -0.008104 |  0.01209   | 505343 | -0.6702 |  0.5   |  0.67  |     |
| **projectsphinx-gallery:author_groupnonmember:typeissue_reply** | -0.01748  |  0.03538   | 499147 | -0.4941 |  0.62  |  0.77  |     |
|       **projectmayavi:author_groupnonmember:typepr_post**       | -0.01243  |  0.03998   | 500430 | -0.3108 |  0.76  |  0.85  |     |
|       **projectnumpy:author_groupnonmember:typepr_post**        |  0.01056  |  0.01309   | 489874 | 0.8062  |  0.42  |  0.58  |     |
|       **projectpandas:author_groupnonmember:typepr_post**       | 0.005802  |  0.01103   | 482242 |  0.526  |  0.6   |  0.77  |     |
|    **projectscikit-image:author_groupnonmember:typepr_post**    | -0.02648  |  0.01884   | 490469 | -1.405  |  0.16  |  0.26  |     |
|    **projectscikit-learn:author_groupnonmember:typepr_post**    | -0.02019  |  0.01228   | 487754 | -1.643  |  0.1   | 0.174  |     |
|       **projectscipy:author_groupnonmember:typepr_post**        | 0.004069  |  0.01457   | 496482 | 0.2793  |  0.78  |  0.85  |     |
|   **projectsphinx-gallery:author_groupnonmember:typepr_post**   | -0.01683  |  0.04685   | 503288 | -0.3593 |  0.72  |  0.82  |     |
|      **projectmayavi:author_groupnonmember:typepr_reply**       |  -0.1152  |  0.03504   | 497802 | -3.288  | 0.001  | 0.003  | **  |
|       **projectnumpy:author_groupnonmember:typepr_reply**       | -0.02068  |  0.01105   | 476366 | -1.871  | 0.061  | 0.115  |     |
|      **projectpandas:author_groupnonmember:typepr_reply**       | -0.02962  |  0.009279  | 458552 | -3.192  | 0.001  | 0.004  | **  |
|   **projectscikit-image:author_groupnonmember:typepr_reply**    | -0.08649  |   0.016    | 471422 | -5.404  | 0.0001 | 0.0001 | *** |
|   **projectscikit-learn:author_groupnonmember:typepr_reply**    | -0.06125  |  0.01032   | 467640 | -5.937  | 0.0001 | 0.0001 | *** |
|       **projectscipy:author_groupnonmember:typepr_reply**       | -0.04245  |   0.0125   | 487725 | -3.396  | 0.001  | 0.002  | **  |
|  **projectsphinx-gallery:author_groupnonmember:typepr_reply**   | -0.08943  |  0.03546   | 502302 | -2.522  | 0.012  | 0.027  |  *  |



![**Figure**. Expressions of gratitude by contribution type (ticket vs. comment) and community membership (member vs. nonmember) at the time of posting.](../../figures/sentiment_analysis/ossc-grateful_membership_contribution-knitr.jpg)

### Testing Model 1.3 using Model 1.1 methods

#### Model 1.3a: Overall effects with linear mixed-effects models

This model presents the analyses in a way that is typical of psychological
analyses. We predict the changes in emotion by community membership and 
contribution type, including random effects for project and for author. This
allows us to explore the general patterns of the main and interaction terms,
rather than focusing in on the project-specific variability.
>>>>>>> 7ea8a4e28ec283d9f6e930c3ad1268db6826f1dc

<!-- # print results -->
<!-- pander_lme(creators_v_commenters_gratitude_by_project) -->

<!-- ``` -->


<<<<<<< HEAD
=======
|                  &nbsp;                   | Estimate  | Std..Error |   df   | t.value |   p    | p_adj  | sig |
|:-----------------------------------------:|:---------:|:----------:|:------:|:-------:|:------:|:------:|:---:|
|              **(Intercept)**              |  0.02085  |  0.008063  | 7.531  |  2.586  | 0.034  | 0.039  |  *  |
|         **author_groupnonmember**         |  0.05473  |  0.002477  | 505983 |  22.1   | 0.0001 | 0.0001 | *** |
|            **typeissue_reply**            |  0.02901  |  0.001929  | 505978 |  15.04  | 0.0001 | 0.0001 | *** |
|              **typepr_post**              | -0.003978 |  0.00231   | 505980 | -1.722  | 0.085  | 0.085  |  .  |
|             **typepr_reply**              |  0.08368  |  0.001903  | 505983 |  43.98  | 0.0001 | 0.0001 | *** |
| **author_groupnonmember:typeissue_reply** |  0.0351   |  0.002747  | 505978 |  12.78  | 0.0001 | 0.0001 | *** |
|   **author_groupnonmember:typepr_post**   | -0.04542  |  0.003508  | 505983 | -12.95  | 0.0001 | 0.0001 | *** |
|  **author_groupnonmember:typepr_reply**   | -0.04342  |  0.002762  | 505983 | -15.72  | 0.0001 | 0.0001 | *** |
>>>>>>> 7ea8a4e28ec283d9f6e930c3ad1268db6826f1dc

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


# Comment sentiment max positive
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

random_effects = ranef(retention_predictor)$project
colnames(random_effects) = "comment_sentiment_max_positive"
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

# Ticket family x comment sentiment max positive
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

random_effects = ranef(retention_predictor)$project
colnames(random_effects) = "ticket_family_comment_sentiment_max_positive"
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
|                     **open_time**                     |                     open_time                     | -1.296  |  0.195  | 0.234  |     |
|            **comment_grateful_cumulative**            |            comment_grateful_cumulative            |  6.701  | 0.0001  | 0.0001 | *** |
|          **comment_sentiment_max_negative**           |          comment_sentiment_max_negative           |   1.4   |  0.162  | 0.209  |     |
|          **comment_sentiment_max_positive**           |          comment_sentiment_max_positive           |  10.87  | 0.0001  | 0.0001 | *** |
|                **number_of_comments**                 |                number_of_comments                 |  9.35   | 0.0001  | 0.0001 | *** |
|               **comment_member_ratio**                |               comment_member_ratio                | -8.363  | 0.0001  | 0.0001 | *** |
|              **comment_sentiment_mean**               |              comment_sentiment_mean               |  6.341  | 0.0001  | 0.0001 | *** |
|           **ticket_familyissue:open_time**            |           ticket_familyissue:open_time            |  3.298  |  0.001  | 0.001  | **  |
|             **ticket_familypr:open_time**             |             ticket_familypr:open_time             | -2.956  |  0.003  | 0.004  | **  |
| **ticket_familyissue:comment_sentiment_max_negative** | ticket_familyissue:comment_sentiment_max_negative | -1.275  |  0.202  | 0.234  |     |
|  **ticket_familypr:comment_sentiment_max_negative**   |  ticket_familypr:comment_sentiment_max_negative   |  4.107  | 0.0001  | 0.0001 | *** |
| **ticket_familyissue:comment_sentiment_max_positive** | ticket_familyissue:comment_sentiment_max_positive |   5.3   | 0.0001  | 0.0001 | *** |
|  **ticket_familypr:comment_sentiment_max_positive**   |  ticket_familypr:comment_sentiment_max_positive   | 0.4519  |  0.65   |  0.68  |     |
|       **ticket_familyissue:number_of_comments**       |       ticket_familyissue:number_of_comments       |  4.011  | 0.0001  | 0.0001 | *** |
|        **ticket_familypr:number_of_comments**         |        ticket_familypr:number_of_comments         |  6.617  | 0.0001  | 0.0001 | *** |
|      **ticket_familyissue:comment_member_ratio**      |      ticket_familyissue:comment_member_ratio      | -4.288  | 0.0001  | 0.0001 | *** |
|       **ticket_familypr:comment_member_ratio**        |       ticket_familypr:comment_member_ratio        | -9.562  | 0.0001  | 0.0001 | *** |
|     **ticket_familyissue:comment_sentiment_mean**     |     ticket_familyissue:comment_sentiment_mean     |  4.387  | 0.0001  | 0.0001 | *** |
|      **ticket_familypr:comment_sentiment_mean**       |      ticket_familypr:comment_sentiment_mean       | -0.6878 |  0.49   |  0.54  |     |
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
<<<<<<< HEAD
|              **ticket_familyissue**               | -0.7759  |  0.07294  | -10.64  | 0.0001  | 0.0001 | *** |
|                **ticket_familypr**                | -0.2323  |  0.08432  | -2.755  |  0.006  | 0.012  |  *  |
| **ticket_familyissue:comment_sentiment_variance** | -0.1616  |   0.166   | -0.9735 |  0.33   |  0.33  |     |
|  **ticket_familypr:comment_sentiment_variance**   |  0.3532  |  0.2869   |  1.231  |  0.218  |  0.29  |     |
=======
|              **ticket_familyissue**               | -0.7779  |  0.07327  | -10.62  | 0.0001  | 0.0001 | *** |
|                **ticket_familypr**                | -0.2456  |  0.08486  | -2.894  |  0.004  | 0.008  | **  |
| **ticket_familyissue:comment_sentiment_variance** | -0.1611  |   0.166   | -0.9703 |  0.33   |  0.33  |     |
|  **ticket_familypr:comment_sentiment_variance**   |  0.4456  |  0.2917   |  1.527  |  0.127  | 0.169  |     |
>>>>>>> 7ea8a4e28ec283d9f6e930c3ad1268db6826f1dc


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
retention_tests$p_val_adjusted = p.adjust(retention_tests$p_value, method="BH")
write.table(retention_tests, file="results/models/model_2.tsv")

write.table(
    all_random_effects,
    "results/models/newcomer_retention_ticket_family_random_effects.tsv")
```


```r
pander_clean_anova(retention_tests_2.1[c("model", "stat", "p_value")],
                   rename_columns=FALSE)
```



|                        &nbsp;                         |                       model                       |  stat   | p_value | p_adj  | sig |
|:-----------------------------------------------------:|:-------------------------------------------------:|:-------:|:-------:|:------:|:---:|
<<<<<<< HEAD
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
=======
|                     **pr-issue**                      |                     pr-issue                      |  5.531  | 0.0001  | 0.0001 | *** |
|                     **open_time**                     |                     open_time                     | -1.296  |  0.195  | 0.243  |     |
|            **comment_grateful_cumulative**            |            comment_grateful_cumulative            |  6.701  | 0.0001  | 0.0001 | *** |
|          **comment_sentiment_max_negative**           |          comment_sentiment_max_negative           |   1.4   |  0.162  | 0.216  |     |
|          **comment_sentiment_max_positive**           |          comment_sentiment_max_positive           |  10.87  | 0.0001  | 0.0001 | *** |
|                **number_of_comments**                 |                number_of_comments                 |  9.35   | 0.0001  | 0.0001 | *** |
|               **comment_member_ratio**                |               comment_member_ratio                | -8.363  | 0.0001  | 0.0001 | *** |
|              **comment_sentiment_mean**               |              comment_sentiment_mean               |  6.341  | 0.0001  | 0.0001 | *** |
|           **ticket_familyissue:open_time**            |           ticket_familyissue:open_time            |  3.298  |  0.001  | 0.002  | **  |
|             **ticket_familypr:open_time**             |             ticket_familypr:open_time             | -2.956  |  0.003  | 0.005  | **  |
| **ticket_familyissue:comment_sentiment_max_negative** | ticket_familyissue:comment_sentiment_max_negative | -1.275  |  0.202  | 0.243  |     |
|  **ticket_familypr:comment_sentiment_max_negative**   |  ticket_familypr:comment_sentiment_max_negative   |  4.107  | 0.0001  | 0.0001 | *** |
| **ticket_familyissue:comment_sentiment_max_positive** | ticket_familyissue:comment_sentiment_max_positive |   5.3   | 0.0001  | 0.0001 | *** |
|  **ticket_familypr:comment_sentiment_max_positive**   |  ticket_familypr:comment_sentiment_max_positive   | 0.4519  |  0.65   |  0.68  |     |
|       **ticket_familyissue:number_of_comments**       |       ticket_familyissue:number_of_comments       |  4.011  | 0.0001  | 0.0001 | *** |
|        **ticket_familypr:number_of_comments**         |        ticket_familypr:number_of_comments         |  6.617  | 0.0001  | 0.0001 | *** |
|      **ticket_familyissue:comment_member_ratio**      |      ticket_familyissue:comment_member_ratio      | -4.288  | 0.0001  | 0.0001 | *** |
|       **ticket_familypr:comment_member_ratio**        |       ticket_familypr:comment_member_ratio        | -9.562  | 0.0001  | 0.0001 | *** |
|     **ticket_familyissue:comment_sentiment_mean**     |     ticket_familyissue:comment_sentiment_mean     |  4.387  | 0.0001  | 0.0001 | *** |
|      **ticket_familypr:comment_sentiment_mean**       |      ticket_familypr:comment_sentiment_mean       | -0.6878 |  0.49   |  0.54  |     |
|  **ticket_familyissue:comment_grateful_cumulative**   |  ticket_familyissue:comment_grateful_cumulative   | 0.06044 |  0.95   |  0.95  |     |
|    **ticket_familypr:comment_grateful_cumulative**    |    ticket_familypr:comment_grateful_cumulative    |   3.4   |  0.001  | 0.001  | **  |
|   **ticket_familyissue:comment_sentiment_variance**   |   ticket_familyissue:comment_sentiment_variance   | -0.9703 |  0.33   |  0.38  |     |
|    **ticket_familypr:comment_sentiment_variance**     |    ticket_familypr:comment_sentiment_variance     |  1.527  |  0.127  | 0.179  |     |
>>>>>>> 7ea8a4e28ec283d9f6e930c3ad1268db6826f1dc

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
