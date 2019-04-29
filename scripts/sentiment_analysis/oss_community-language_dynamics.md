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

**Date last modified**: 28 April 2019

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


```r
unique_commenters = as.character(unique(joined_frame$author_name_comment))
unique_issuers = as.character(unique(joined_frame$author_name_issue))
unique_users = as.character(unique(append(unique_commenters, unique_issuers)))

print(paste0("Unique commenters included: ", length(unique_commenters)))
```

```
## [1] "Unique commenters included: 5944"
```

```r
print(paste0("Unique issue-creators included: ", length(unique_issuers)))
```

```
## [1] "Unique issue-creators included: 7019"
```

```r
print(paste0("Unique users included: ", length(unique_users)))
```

```
## [1] "Unique users included: 8659"
```


```r
activity_counts = joined_frame %>% ungroup() %>%
  dplyr::select(project, id_issue) %>%
  distinct() %>%
  group_by(project) %>%
  summarize(unique_issues = n())

print(paste0("Unique projects included: ", dim(activity_counts)[1]))
```

```
## [1] "Unique projects included: 8"
```

```r
print(paste0("Unique issues included: ", sum(activity_counts$unique_issues)))
```

```
## [1] "Unique issues included: 33822"
```

```r
print(paste0("Mean issues per project: ", mean(activity_counts$unique_issues)))
```

```
## [1] "Mean issues per project: 4227.75"
```

```r
comment_counts = joined_frame %>% ungroup() %>%
  dplyr::select(project, id_issue, id_comment) %>%
  distinct() %>%
  group_by(project, id_issue) %>%
  summarize(unique_comments = n())

print(paste0("Unique comments included: ", sum(comment_counts$unique_comments)))
```

```
## [1] "Unique comments included: 213904"
```

```r
print(paste0("Mean comments per issue: ", mean(comment_counts$unique_comments)))
```

```
## [1] "Mean comments per issue: 6.32440423393058"
```


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
|           **(Intercept)**           |   0.209   |  0.009478  |  22.05  | 0.0001 | *** |
|            **typeissue**            |  -0.1144  |  0.002959  | -38.66  | 0.0001 | *** |
|      **author_groupnonmember**      | -0.009759 |  0.005565  | -1.754  |  0.08  |  .  |
| **typeissue:author_groupnonmember** | -0.008198 |  0.006424  | -1.276  | 0.202  |     |

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



|                  &nbsp;                  | Estimate  | Std..Error | t.value |   p    | sig |
|:----------------------------------------:|:---------:|:----------:|:-------:|:------:|:---:|
|             **(Intercept)**              |   6.031   |   1.544    |  3.907  | 0.0001 | *** |
|              **typeissue**               |  -15.81   |   3.197    | -4.946  | 0.0001 | *** |
|        **author_groupnonmember**         |  -3.855   |   4.529    | -0.8512 |  0.4   |     |
|                 **date**                 | -0.00289  |  0.000766  | -3.773  | 0.0002 | *** |
|   **typeissue:author_groupnonmember**    |   2.697   |   6.989    | 0.3859  |  0.7   |     |
|            **typeissue:date**            | 0.007792  |  0.001587  |  4.91   | 0.0001 | *** |
|      **author_groupnonmember:date**      | 0.001909  |  0.002248  | 0.8493  |  0.4   |     |
| **typeissue:author_groupnonmember:date** | -0.001344 |  0.003469  | -0.3874 |  0.7   |     |

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
    member      comment         0          169740 

    member      comment         1          20471  

    member      comment         2           579   

    member      comment         3            52   

    member      comment         4            1    

    member       issue          0          24201  

    member       issue          1           654   

    member       issue          2            30   

    member       issue          3            3    

  nonmember     comment         0          19342  

  nonmember     comment         1           3438  

  nonmember     comment         2           263   

  nonmember     comment         3            18   

  nonmember      issue          0           8049  

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
## 164849.8 164901.9 -82419.9 164839.8   247721 
## 
## Scaled residuals: 
##     Min      1Q  Median      3Q     Max 
## -1.1026 -0.3827 -0.2623 -0.2147 21.6055 
## 
## Random effects:
##  Groups      Name        Variance  Std.Dev.
##  author_name (Intercept) 0.6756950 0.82201 
##  project     (Intercept) 0.0008876 0.02979 
## Number of obs: 247726, groups:  author_name, 8659; project, 8
## 
## Fixed effects:
##                       Estimate Std. Error z value            Pr(>|z|)    
## (Intercept)           -2.07941    0.02984  -69.69 <0.0000000000000002 ***
## author_groupnonmember  0.42951    0.03144   13.66 <0.0000000000000002 ***
## typeissue             -1.13937    0.02670  -42.67 <0.0000000000000002 ***
## ---
## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
## 
## Correlation of Fixed Effects:
##             (Intr) athr_g
## athr_grpnnm -0.633       
## typeissue   -0.121 -0.031
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
## control$checkConv, : Model failed to converge with max|grad| = 7.51619 (tol
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
## 173819.5 173892.4 -86902.7 173805.5   247719 
## 
## Scaled residuals: 
##     Min      1Q  Median      3Q     Max 
## -0.5644 -0.3491 -0.3125 -0.2967 15.3012 
## 
## Random effects:
##  Groups  Name        Variance Std.Dev.
##  project (Intercept) 0.06152  0.248   
## Number of obs: 247726, groups:  project, 8
## 
## Fixed effects:
##                               Estimate  Std. Error z value
## (Intercept)                  2.0959917   0.2807653   7.465
## author_groupnonmember      -28.1058157   0.3224714 -87.158
## typeissue                   10.6622147   0.2565953  41.553
## date                        -0.0021032   0.0001461 -14.400
## author_groupnonmember:date   0.0141934   0.0001603  88.545
## typeissue:date              -0.0057770   0.0001283 -45.038
##                                        Pr(>|z|)    
## (Intercept)                  0.0000000000000831 ***
## author_groupnonmember      < 0.0000000000000002 ***
## typeissue                  < 0.0000000000000002 ***
## date                       < 0.0000000000000002 ***
## author_groupnonmember:date < 0.0000000000000002 ***
## typeissue:date             < 0.0000000000000002 ***
## ---
## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
## 
## Correlation of Fixed Effects:
##             (Intr) athr_g typess date   athr_:
## athr_grpnnm -0.161                            
## typeissue    0.098 -0.013                     
## date        -0.954  0.154 -0.093              
## athr_grpnn:  0.161 -0.999  0.013 -0.155       
## typeissu:dt -0.098  0.013 -0.995  0.093 -0.014
## convergence code: 0
## Model failed to converge with max|grad| = 7.51619 (tol = 0.001, component 1)
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
##  37688.6  37747.6 -18837.3  37674.6    33815 
## 
## Scaled residuals: 
##     Min      1Q  Median      3Q     Max 
## -1.3660 -0.6014 -0.5420  1.1181  2.5233 
## 
## Random effects:
##  Groups  Name                   Variance Std.Dev. Corr 
##  project (Intercept)            0.15801  0.3975        
##          grateful_count_comment 0.02353  0.1534   -0.62
## Number of obs: 33822, groups:  project, 8
## 
## Fixed effects:
##                        Estimate Std. Error z value             Pr(>|z|)
## (Intercept)            -1.06137    0.14241  -7.453   0.0000000000000913
## compound_emotion       -0.00167    0.01260  -0.133              0.89458
## grateful_count_comment  0.18625    0.05748   3.240              0.00119
## open_time               0.15448    0.01199  12.889 < 0.0000000000000002
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
## grtfl_cnt_c -0.582 -0.001       
## open_time   -0.006 -0.069  0.041
```

**Note**. Need to fix this. Not really sure how best to demonstrate this given the limits of the linear fit...



![**Figure**. Whether a first-time issue creator will open a second issue by commenters' expressions of gratitude and responsiveness.](../../figures/sentiment_analysis/ossc-retention_emotion-knitr.jpg)
