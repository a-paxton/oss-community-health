---
title: "Communication dynamics in OSS communities"
output:
  html_document:
    keep_md: yes
    number_sections: yes
---

This R markdown provides the data preparation for our forthcoming manuscript
(Paxton, Varoquaux, Geiger, & Holdgraf, *in preparation*). 

To run this from scratch, you will need the following files:

* `../../data/analysis_data/all-sentiment_frame.csv`: Contains cleaned data and derived 
  variables from scraped GitHub data.
* `./utils/ossc-libraries_and_functions.r`: Loads in necessary libraries and creates 
  new functions for our analyses.

**Code written by**: A. Paxton (University of Connecticut)

**Date last modified**: 22 May 2019

***

# Preliminaries


```r
# clear everything
rm(list=ls())

# load libraries and add new functions
source('./utils/ossc-libraries_and_functions.r')
library(jtools)
library(magrittr)

# load data
joined_frame = read.table('../../data/analysis_data/all-sentiment_frame-for_r.csv', 
                          sep = ',', header=TRUE, fill=TRUE)
bot_names = read.table('../bot_names.txt') %>% .$V1 %>% as.character(.)
```

***

# Data preparation

## Identify potential remaining bots

**Note**: This is useful to run if more data are collected. The results
should be manually inspected, and any additional bots detected should
be added to the `../bot_names.txt` file. Otherwise, it does not need 
to be run.


```r
# # identify potential bots based on who uses "bot" in their names
# potential_bot_df = joined_frame %>% ungroup() %>%
#   filter(grepl("bot",author_name_issue)) %>% 
#   filter(grepl("bot",author_name_comment)) %>%
#   select(author_name_issue, author_name_comment)
# 
# # find all unique instances
# bot_issues = as.character(unique(potential_bot_df$author_name_issue))
# bot_comments = as.character(unique(potential_bot_df$author_name_comment))
# potential_bots = unique(c(bot_issues,bot_comments))
# potential_bots = potential_bots[grepl("bot",potential_bots)]
# 
# # save to file
# write.table(potential_bots, file="ossc-potential_bots.csv",
#           col.names=FALSE, row.names=FALSE)
```

## Convert time to dates


```r
# fix time
joined_frame = joined_frame %>% ungroup() %>%
  
  # filter out bots
  filter(!author_name_issue %in% bot_names) %>% 
  filter(!author_name_comment %in% bot_names) %>% 
  
  # get time in days
  mutate(open_time_comment = strsplit(as.character(open_duration), ' ') %>%
           sapply(magrittr::extract2, 1) %>%
           as.numeric()) %>%
  mutate(open_time_issue = open_time_comment) %>%
  
  # get the year and month it was created 
  mutate(year_comment = as.numeric(format(as.Date(created_at_comment), "%Y"))) %>%
  mutate(year_issue = as.numeric(format(as.Date(created_at_issue), "%Y"))) %>%
  mutate(month_comment = as.numeric(format(as.Date(created_at_comment), "%m"))) %>%
  mutate(month_issue = as.numeric(format(as.Date(created_at_issue), "%m"))) %>%
  mutate(date_comment = year_comment + (month_comment/12.1)) %>%
  mutate(date_issue = year_issue + (month_issue/12.1)) %>%
  
  # drop old columns
  select(-ends_with('_at'), -contains('_at_'),
         -contains('month'), -contains('year'),
         -open_duration)
```


***

# Basic summary stats





Our dataset includes 8 unique projects with a total of 33752 unique issues, with a mean of 4219 issues per project.

On these issues, the dataset includes 210014 unique comments, with `mean(comment_counts$unique_comments)` average comments per issue.

In total, we have 5942 unique commenters, 7016 unique issue-creators, and 8654 overall unique users.

***

# Data analysis

Ideas:
* Do comments, generally, get more friendly or more hostile over time?
* Does the emotional valence of a contributor's first ticket predict whether they'll come 
back to make a second one?
* Are requesters more or less polite?
* Does friendliness bring people back?
* Does the number and intensity of negative and positive comments on a first-time contributor's issue 
change whether they come back to make another ticket?

## Model Series 1: Survivor curves

**To do**: See whether this can be modeled against a Poisson distribution, then see whether the
communities tend to be more similar or different to one another.
* Need to figure out how to do this (cf. orthogonal polynomials)



## Model Series 2: Sentiment analysis


```r
# mutate wide-form into long-form data
body_sentiment_df = joined_frame %>% ungroup() %>%
  select(contains('author'), 
         contains('grateful_count'),
         contains('emotion'),
         contains('id_'),
         contains('date_'),
         contains('open_'),
         contains('num_PR_'),
         -contains('ticket_id'))

# separate out comments, issues, and last activity counters
comment_sentiment_df = body_sentiment_df %>% ungroup() %>%
  select(ends_with('_comment')) %>%
  rename_all(funs(gsub('_comment','',.)))
```

```
## Warning: funs() is soft deprecated as of dplyr 0.8.0
## please use list() instead
## 
## # Before:
## funs(name = f(.)
## 
## # After: 
## list(name = ~f(.))
## This warning is displayed once per session.
```

```r
issue_sentiment_df = body_sentiment_df %>% ungroup() %>%
  select(ends_with('_issue')) %>%
  rename_all(funs(gsub('_issue','',.)))
last_counters = joined_frame %>% ungroup() %>%
  select(id_issue, id_comment, project, bus_factor,
         issue_author_last_issue, issue_author_last_comment)

# merge counters
comment_sentiment_df = full_join(comment_sentiment_df,
                                 last_counters,
                                 by=c('id' = 'id_comment')) %>%
  select(-id_issue) %>%
  mutate(type = 'comment') %>%
  distinct()
issue_sentiment_df = full_join(issue_sentiment_df,
                               distinct(select(last_counters,
                                               -id_comment)),
                               by=c('id' = 'id_issue')) %>%
  mutate(type = 'issue') %>%
  distinct()

# append the dataframes
sentiment_frame = rbind.data.frame(comment_sentiment_df, issue_sentiment_df)

# concatenate association groups
sentiment_frame = sentiment_frame %>% ungroup() %>%
  mutate(author_group = ifelse(author_association=='MEMBER',
                               'member',
                               ifelse(author_association=='CONTRIBUTOR',
                                      'member',
                                      ifelse(author_association=='OWNER',
                                             'member',
                                             'nonmember')))) %>%
  
  # convert to factors
  mutate(author_group = as.factor(author_group)) %>%
  mutate(type = as.factor(type))
```

For Model 2, if we were going to keep original author associations,
we would have to remove first-time contributors and first-timers from 
the dataset when we're analyzing `type` as a covariate, since both types
of users only ever submitted issues.


```r
# first time contributors
first_time_contrib_df = sentiment_frame %>%
  filter(author_association=='FIRST_TIME_CONTRIBUTOR')
print(paste0("Unique contribution types for first-time contributors: ",
             unique(first_time_contrib_df$type)))
```

```
## [1] "Unique contribution types for first-time contributors: issue"
```

```r
# first time contributors
first_timers_df = sentiment_frame %>%
  filter(author_association=='FIRST_TIMER')
print(paste0("Unique contribution types for first-timers: ",
             unique(first_timers_df$type)))
```

```
## [1] "Unique contribution types for first-timers: issue"
```

However, because we are grouping simply by members and non-members,
we can retain them in the dataset.

### Model 2.1: Do issues and comments materially differ in emotion?


```r
# do issues and comments materially differ in emotion?
creators_v_commenters_emotion = lmer(compound_emotion ~ type * author_group +
                                       (1 | project) +
                                       (1 | author_name),
                                     data = sentiment_frame,
                                     REML=FALSE)

# print results
pander_lme(creators_v_commenters_emotion)
```



|               &nbsp;                | Estimate  | Std..Error | t.value |   p    | sig |
|:-----------------------------------:|:---------:|:----------:|:-------:|:------:|:---:|
|           **(Intercept)**           |   0.209   |  0.009345  |  22.37  | 0.0001 | *** |
|            **typeissue**            |  -0.1143  |  0.002984  |  -38.3  | 0.0001 | *** |
|      **author_groupnonmember**      | -0.009831 |  0.005574  | -1.764  | 0.078  |  .  |
| **typeissue:author_groupnonmember** | -0.00866  |  0.006467  | -1.339  |  0.18  |     |

These results are quite different from our results conducted
over a smaller dataset last year. One potential reason is
that these effects may be time-dependent. Our next model
explores this possibility by adding a time term.



![**Figure**. Sentiment by contribution type (issue vs. comment) and community membership (member vs. nonmember) at the time of posting.](../../figures/sentiment_analysis/ossc-sentiment_membership_contribution-knitr.jpg)

### Model 2.2: Do issues and comments materially differ in emotion over time?


```r
# do issues and comments materially differ in emotion over time?
creators_v_commenters_emotion_time = lmer(compound_emotion ~ type * author_group * date +
                                            (1 | project) +
                                            (1 | author_name),
                                          data = sentiment_frame,
                                          REML=FALSE)

# print results
pander_lme(creators_v_commenters_emotion_time)
```



|                  &nbsp;                  |  Estimate  | Std..Error | t.value |   p    | sig |
|:----------------------------------------:|:----------:|:----------:|:-------:|:------:|:---:|
|             **(Intercept)**              |   6.115    |   1.555    |  3.931  | 0.0001 | *** |
|              **typeissue**               |   -15.65   |   3.219    | -4.863  | 0.0001 | *** |
|        **author_groupnonmember**         |   1.088    |   4.572    |  0.238  |  0.81  |     |
|                 **date**                 | -0.002931  | 0.0007719  | -3.798  | 0.0001 | *** |
|   **typeissue:author_groupnonmember**    |   -1.112   |   7.042    | -0.158  |  0.87  |     |
|            **typeissue:date**            |  0.007713  |  0.001598  |  4.827  | 0.0001 | *** |
|      **author_groupnonmember:date**      | -0.0005443 |  0.002269  | -0.2399 |  0.81  |     |
| **typeissue:author_groupnonmember:date** | 0.0005466  |  0.003495  | 0.1564  |  0.88  |     |

Interestingly, we see much more volatility here in the emotion dynamics
of community members relative to the community nonmembers over time, even
when we collapse across all projects.

Perhaps more interestingly, we see a difference in the affect dynamics
only in the last year: Members' issues are becoming more positive, while
nonmembers' issues are becoming more negative.

We'll need to do an analysis to follow up on this.


![**Figure**. Sentiment over time by contribution type (issue vs. comment) and community membership (member vs. nonmember) at the time of posting.](../../figures/sentiment_analysis/ossc-sentiment_membership_contribution_time-knitr.jpg)

### Model 2.3: Do issues and comments materially differ in gratitude?


```r
# create a summary table of gratitude by type and author association
gratitude_summary_stats = sentiment_frame %>% ungroup() %>%
  group_by(author_group, type, grateful_count) %>%
  summarise(n = n())

pander(gratitude_summary_stats)
```


--------------------------------------------------
 author_group    type     grateful_count     n    
-------------- --------- ---------------- --------
    member      comment         0          169737 

    member      comment         1          20471  

    member      comment         2           579   

    member      comment         3            52   

    member      comment         4            1    

    member       issue          0          24133  

    member       issue          1           654   

    member       issue          2            30   

    member       issue          3            3    

  nonmember     comment         0          15457  

  nonmember     comment         1           3436  

  nonmember     comment         2           263   

  nonmember     comment         3            18   

  nonmember      issue          0           8047  

  nonmember      issue          1           834   

  nonmember      issue          2            49   

  nonmember      issue          3            2    
--------------------------------------------------

This model fails to converge if we include the interaction term.


```r
# do users tend to express appreciation and gratitude differently by group and content?
creators_v_commenters_gratitude = glmer(grateful_count ~ author_group + type +
                                          (1 | project) +
                                          (1 | author_name),
                                        data=sentiment_frame,
                                        family=poisson)

# print results
summary(creators_v_commenters_gratitude)
```

```
## Generalized linear mixed model fit by maximum likelihood (Laplace
##   Approximation) [glmerMod]
##  Family: poisson  ( log )
## Formula: 
## grateful_count ~ author_group + type + (1 | project) + (1 | author_name)
##    Data: sentiment_frame
## 
##      AIC      BIC   logLik deviance df.resid 
## 164768.8 164820.8 -82379.4 164758.8   243761 
## 
## Scaled residuals: 
##     Min      1Q  Median      3Q     Max 
## -1.0991 -0.3827 -0.2663 -0.2148 16.6547 
## 
## Random effects:
##  Groups      Name        Variance  Std.Dev.
##  author_name (Intercept) 0.6503609 0.80645 
##  project     (Intercept) 0.0009403 0.03066 
## Number of obs: 243766, groups:  author_name, 8654; project, 8
## 
## Fixed effects:
##                       Estimate Std. Error z value            Pr(>|z|)    
## (Intercept)           -2.07462    0.02978  -69.66 <0.0000000000000002 ***
## author_groupnonmember  0.43539    0.03130   13.91 <0.0000000000000002 ***
## typeissue             -1.13669    0.02670  -42.57 <0.0000000000000002 ***
## ---
## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
## 
## Correlation of Fixed Effects:
##             (Intr) athr_g
## athr_grpnnm -0.631       
## typeissue   -0.127 -0.027
```



![**Figure**. Expressions of gratitude by contribution type (issue vs. comment) and community membership (member vs. nonmember) at the time of posting.](../../figures/sentiment_analysis/ossc-grateful_membership_contribution-knitr.jpg)

### Model 2.4: Do issues and comments materially differ in gratitude over time?

**Note**: Having difficulty getting this to converge.


```r
# do users tend to express appreciation and gratitude differently by group and content?
creators_v_commenters_gratitude_time = glmer(grateful_count ~ (author_group + type) * date +
                                               (1 | project),
                                             data=sentiment_frame,
                                             family=poisson)
```

```
## Warning in checkConv(attr(opt, "derivs"), opt$par, ctrl =
## control$checkConv, : Model failed to converge with max|grad| = 4.72115 (tol
## = 0.001, component 1)
```

```
## Warning in checkConv(attr(opt, "derivs"), opt$par, ctrl = control$checkConv, : Model is nearly unidentifiable: very large eigenvalue
##  - Rescale variables?;Model is nearly unidentifiable: large eigenvalue ratio
##  - Rescale variables?
```

```r
# print results
summary(creators_v_commenters_gratitude_time)
```

```
## Generalized linear mixed model fit by maximum likelihood (Laplace
##   Approximation) [glmerMod]
##  Family: poisson  ( log )
## Formula: grateful_count ~ (author_group + type) * date + (1 | project)
##    Data: sentiment_frame
## 
##      AIC      BIC   logLik deviance df.resid 
## 171913.5 171986.3 -85949.7 171899.5   243759 
## 
## Scaled residuals: 
##     Min      1Q  Median      3Q     Max 
## -0.6255 -0.3566 -0.3072 -0.2881 16.4522 
## 
## Random effects:
##  Groups  Name        Variance Std.Dev.
##  project (Intercept) 0.06638  0.2576  
## Number of obs: 243766, groups:  project, 8
## 
## Fixed effects:
##                               Estimate  Std. Error z value
## (Intercept)                  4.1752430   0.2471912   16.89
## author_groupnonmember       57.8282774   0.2157337  268.05
## typeissue                  -10.9232492   0.3072801  -35.55
## date                        -0.0031389   0.0001308  -24.00
## author_groupnonmember:date  -0.0283526   0.0001074 -263.97
## typeissue:date               0.0048998   0.0001534   31.94
##                                       Pr(>|z|)    
## (Intercept)                <0.0000000000000002 ***
## author_groupnonmember      <0.0000000000000002 ***
## typeissue                  <0.0000000000000002 ***
## date                       <0.0000000000000002 ***
## author_groupnonmember:date <0.0000000000000002 ***
## typeissue:date             <0.0000000000000002 ***
## ---
## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
## 
## Correlation of Fixed Effects:
##             (Intr) athr_g typess date   athr_:
## athr_grpnnm  0.023                            
## typeissue    0.200 -0.075                     
## date        -0.938 -0.021 -0.187              
## athr_grpnn: -0.023 -0.997  0.076  0.020       
## typeissu:dt -0.200  0.075 -0.997  0.187 -0.077
## convergence code: 0
## Model failed to converge with max|grad| = 4.72115 (tol = 0.001, component 1)
## Model is nearly unidentifiable: very large eigenvalue
##  - Rescale variables?
## Model is nearly unidentifiable: large eigenvalue ratio
##  - Rescale variables?
```



![**Figure**. Expressions of gratitude over time by contribution type (issue vs. comment) and community membership (member vs. nonmember) at the time of posting.](../../figures/sentiment_analysis/ossc-gratitude_membership_contribution_time-knitr.jpg)

## Model Series 3: Retention


```r
# combine information by issue
retention_frame = joined_frame %>% ungroup() %>%
  group_by(project, id_issue) %>%
  summarize_if(is.numeric, mean, na.rm=TRUE) %>%
  ungroup() %>%
  left_join(., issue_sentiment_df,
            by=c('project', 'bus_factor',
                 'id_issue' = 'id'))

# normalize
retention_frame_st = retention_frame %>%
  mutate_all(funs(as.numeric(scale(as.numeric(.))))) %>%
  mutate(issue_author_last_issue = as.factor(issue_author_last_issue)) %>%
  mutate(project = as.factor(project))
```

```
## Warning in scale(as.numeric(type)): NAs introduced by coercion
```


```r
# what predicts continuing retention?
dropout_predictors = glmer(issue_author_last_issue ~ compound_emotion + grateful_count_comment + open_time +
                             (1 + grateful_count_comment | project),
                           data=retention_frame_st,
                           family=binomial)

# print it
summary(dropout_predictors)
```

```
## Generalized linear mixed model fit by maximum likelihood (Laplace
##   Approximation) [glmerMod]
##  Family: binomial  ( logit )
## Formula: 
## issue_author_last_issue ~ compound_emotion + grateful_count_comment +  
##     open_time + (1 + grateful_count_comment | project)
##    Data: retention_frame_st
## 
##      AIC      BIC   logLik deviance df.resid 
##  37622.3  37681.3 -18804.1  37608.3    33745 
## 
## Scaled residuals: 
##     Min      1Q  Median      3Q     Max 
## -1.3626 -0.6016 -0.5466  1.1200  2.5238 
## 
## Random effects:
##  Groups  Name                   Variance Std.Dev. Corr 
##  project (Intercept)            0.15874  0.3984        
##          grateful_count_comment 0.02572  0.1604   -0.62
## Number of obs: 33752, groups:  project, 8
## 
## Fixed effects:
##                         Estimate Std. Error z value             Pr(>|z|)
## (Intercept)            -1.058779   0.142562  -7.427    0.000000000000111
## compound_emotion       -0.001483   0.012613  -0.118               0.9064
## grateful_count_comment  0.181746   0.059876   3.035               0.0024
## open_time               0.153680   0.012010  12.796 < 0.0000000000000002
##                           
## (Intercept)            ***
## compound_emotion          
## grateful_count_comment ** 
## open_time              ***
## ---
## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
## 
## Correlation of Fixed Effects:
##             (Intr) cmpnd_ grtf__
## compond_mtn -0.002              
## grtfl_cnt_c -0.588 -0.001       
## open_time   -0.006 -0.069  0.040
```

**Note**. Need to fix this. Not really sure how best to demonstrate this given the limits of the linear fit...



![**Figure**. Whether a first-time issue creator will open a second issue by commenters' expressions of gratitude and responsiveness.](../../figures/sentiment_analysis/ossc-retention_emotion-knitr.jpg)
