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
library(splines)
library(lmerTest)
# clear everything
rm(list=ls())

# load libraries and add new functions
source('./utils/ossc-libraries_and_functions.r')
library(jtools)
library(magrittr)

library(splines)

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

## Convert time to numbers


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
  mutate(date_comment = as.numeric(as.Date(created_at_comment))) %>%
  mutate(date_issue = as.numeric(as.Date(created_at_issue))) %>%
  
  # drop old columns
  select(-ends_with('_at'), -contains('_at_'),
         -contains('month'), -contains('year'),
         -open_duration)
```


***

# Basic summary stats





Our dataset includes 8 unique projects with a total 
of 62304 unique issues, with a mean of `
r mean(activity_counts$unique_issues)` issues per project.

On these issues, the dataset includes 408963 
unique comments, with 6.5639927 average comments 
per issue.

In total, we have 14259 unique commenters, 
14133 unique issue-creators, and 18012 
overall unique users.

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
|           **(Intercept)**           |  0.2098   |  0.01092   |  19.22  | 0.0001 | *** |
|            **typeissue**            | -0.07926  |  0.00218   | -36.36  | 0.0001 | *** |
|      **author_groupnonmember**      | -0.006838 |  0.003744  | -1.826  | 0.068  |  .  |
| **typeissue:author_groupnonmember** |  0.01139  |  0.004455  |  2.557  | 0.011  |  *  |

<<<<<<< HEAD
These results are quite different from our results conducted
over a smaller dataset last year. One potential reason is
that these effects may be time-dependent. Our next model
explores this possibility by adding a time term.

=======
```r
# do tickets and comments materially differ in emotion?
creators_v_commenters_emotion_by_project = lmer(compound_emotion ~ project * type * author_group  +
                                               (1 | author_name),
                                                data = sentiment_frame,
                                                REML = TRUE)


# print results
pander_lme(creators_v_commenters_emotion_by_project)
```
>>>>>>> d5ab35a... Got the damn p-value at last


![**Figure**. Sentiment by contribution type (issue vs. comment) and community membership (member vs. nonmember) at the time of posting.](../../figures/sentiment_analysis/ossc-sentiment_membership_contribution-knitr.jpg)

<<<<<<< HEAD
### Model 2.2: Do issues and comments materially differ in emotion over time?
=======
|                             &nbsp;                              | Estimate  | Std..Error |   df   | t.value |              Pr...t..              |   p    | p_adj  | sig |
|:---------------------------------------------------------------:|:---------:|:----------:|:------:|:-------:|:----------------------------------:|:------:|:------:|:---:|
|                         **(Intercept)**                         |  0.1259   |  0.01123   | 394336 |  11.22  | 0.00000000000000000000000000003371 | 0.0001 | 0.0002 | *** |
|                        **projectmayavi**                        |  -0.1515  |  0.05561   | 261975 | -2.725  |              0.006438              | 0.006  | 0.011  |  *  |
|                        **projectnumpy**                         | -0.09428  |  0.01475   | 481341 | -6.393  |          0.0000000001632           | 0.0001 | 0.0002 | *** |
|                        **projectpandas**                        | -0.02049  |   0.0126   | 462322 | -1.627  |               0.1038               | 0.104  | 0.145  |     |
|                     **projectscikit-image**                     | -0.07675  |  0.02176   | 480993 | -3.527  |              0.00042               | 0.0004 | 0.001  | **  |
|                     **projectscikit-learn**                     | -0.02622  |  0.01452   | 477480 | -1.806  |              0.07094               | 0.071  | 0.108  |     |
|                        **projectscipy**                         | -0.08206  |  0.01782   | 479667 | -4.606  |            0.000004113             | 0.0001 | 0.0002 | *** |
|                    **projectsphinx-gallery**                    | -0.01646  |  0.04382   | 468944 | -0.3756 |               0.7072               |  0.71  |  0.73  |     |
|                       **typeissue_reply**                       |  0.03811  |   0.0106   | 471532 |  3.595  |              0.000324              | 0.0003 | 0.001  | **  |
|                         **typepr_post**                         |  0.1113   |  0.01163   | 472290 |  9.573  |     0.000000000000000000001046     | 0.0001 | 0.0002 | *** |
|                        **typepr_reply**                         |  0.06672  |  0.01046   | 472341 |  6.379  |          0.0000000001787           | 0.0001 | 0.0002 | *** |
|                    **author_groupnonmember**                    |  0.06546  |  0.01345   | 429809 |  4.867  |            0.000001134             | 0.0001 | 0.0002 | *** |
|                **projectmayavi:typeissue_reply**                |  0.08577  |  0.05092   | 469500 |  1.684  |              0.09212               | 0.092  | 0.131  |     |
|                **projectnumpy:typeissue_reply**                 |  0.07758  |  0.01448   | 469361 |  5.36   |           0.00000008345            | 0.0001 | 0.0002 | *** |
|                **projectpandas:typeissue_reply**                |  0.03759  |  0.01191   | 471047 |  3.156  |              0.001598              | 0.002  | 0.004  | **  |
|             **projectscikit-image:typeissue_reply**             |  0.1165   |  0.02141   | 466838 |  5.441  |           0.00000005291            | 0.0001 | 0.0002 | *** |
|             **projectscikit-learn:typeissue_reply**             |  0.04822  |  0.01392   | 469436 |  3.464  |             0.0005316              |   0    | 0.0001 | *** |
|                **projectscipy:typeissue_reply**                 |  0.08936  |   0.0178   | 468394 |  5.021  |            0.0000005153            | 0.0001 | 0.0002 | *** |
|            **projectsphinx-gallery:typeissue_reply**            |  0.1018   |  0.04602   | 465861 |  2.212  |              0.02699               | 0.027  | 0.048  |  *  |
|                  **projectmayavi:typepr_post**                  |  -0.1071  |  0.05611   | 467053 | -1.909  |              0.05625               | 0.056  | 0.089  |  .  |
|                  **projectnumpy:typepr_post**                   |  -0.0539  |  0.01645   | 469683 | -3.276  |              0.001052              | 0.001  | 0.002  | **  |
|                  **projectpandas:typepr_post**                  |  -0.1546  |  0.01364   | 471894 | -11.33  | 0.00000000000000000000000000000951 | 0.0001 | 0.0002 | *** |
|               **projectscikit-image:typepr_post**               | -0.03681  |  0.02377   | 467243 | -1.549  |               0.1214               | 0.121  | 0.165  |     |
|               **projectscikit-learn:typepr_post**               | -0.02088  |  0.01606   | 469907 |  -1.3   |               0.1936               | 0.194  | 0.244  |     |
|                  **projectscipy:typepr_post**                   | -0.08184  |  0.01963   | 468754 |  -4.17  |             0.0000305              | 0.0001 | 0.0002 | *** |
|              **projectsphinx-gallery:typepr_post**              |  -0.108   |  0.05448   | 465995 | -1.982  |              0.04752               | 0.048  | 0.079  |  .  |
|                 **projectmayavi:typepr_reply**                  |  0.06237  |  0.05182   | 468110 |  1.204  |               0.2287               | 0.229  |  0.28  |     |
|                  **projectnumpy:typepr_reply**                  |  0.1283   |  0.01444   | 470135 |  8.889  |      0.0000000000000000006208      | 0.0001 | 0.0002 | *** |
|                 **projectpandas:typepr_reply**                  |  0.03945  |   0.0118   | 472115 |  3.343  |             0.0008291              | 0.001  | 0.002  | **  |
|              **projectscikit-image:typepr_reply**               |  0.1455   |  0.02085   | 467337 |  6.978  |         0.000000000003005          | 0.0001 | 0.0002 | *** |
|              **projectscikit-learn:typepr_reply**               |  0.07015  |   0.0137   | 470268 |  5.122  |            0.0000003023            | 0.0001 | 0.0002 | *** |
|                  **projectscipy:typepr_reply**                  |  0.1361   |  0.01754   | 468981 |  7.761  |        0.000000000000008442        | 0.0001 | 0.0002 | *** |
|             **projectsphinx-gallery:typepr_reply**              |  0.05909  |   0.0447   | 466211 |  1.322  |               0.1862               | 0.186  | 0.243  |     |
|             **projectmayavi:author_groupnonmember**             |  0.02512  |   0.0599   | 300127 | 0.4193  |               0.675                |  0.68  |  0.71  |     |
|             **projectnumpy:author_groupnonmember**              | -0.06446  |   0.0186   | 454852 | -3.465  |             0.0005303              |   0    | 0.0001 | *** |
|             **projectpandas:author_groupnonmember**             | -0.06421  |  0.01562   | 429966 | -4.112  |             0.00003931             | 0.0001 | 0.0002 | *** |
|          **projectscikit-image:author_groupnonmember**          | -0.04912  |  0.02866   | 440834 | -1.714  |              0.08656               | 0.087  | 0.126  |     |
|          **projectscikit-learn:author_groupnonmember**          | -0.007876 |  0.01809   | 439713 | -0.4353 |               0.6633               |  0.66  |  0.7   |     |
|             **projectscipy:author_groupnonmember**              | -0.02225  |  0.02146   | 464890 | -1.037  |               0.2999               |  0.3   |  0.35  |     |
|         **projectsphinx-gallery:author_groupnonmember**         |  -0.1301  |  0.06142   | 480335 | -2.119  |              0.03413               | 0.034  | 0.057  |  .  |
|            **typeissue_reply:author_groupnonmember**            | -0.04762  |  0.01406   | 479242 | -3.386  |              0.00071               | 0.001  | 0.002  | **  |
|              **typepr_post:author_groupnonmember**              |  -0.1148  |  0.01737   | 444196 | -6.609  |          0.0000000000387           | 0.0001 | 0.0002 | *** |
|             **typepr_reply:author_groupnonmember**              | -0.04862  |  0.01498   | 391432 | -3.246  |              0.001171              | 0.001  | 0.002  | **  |
|     **projectmayavi:typeissue_reply:author_groupnonmember**     | 0.008681  |  0.05846   | 481641 | 0.1485  |               0.8819               |  0.88  |  0.89  |     |
|     **projectnumpy:typeissue_reply:author_groupnonmember**      |  0.06923  |  0.01989   | 477536 |  3.48   |             0.0005011              |   0    | 0.0001 | *** |
|     **projectpandas:typeissue_reply:author_groupnonmember**     |  0.07683  |  0.01644   | 476687 |  4.672  |            0.000002983             | 0.0001 | 0.0002 | *** |
|  **projectscikit-image:typeissue_reply:author_groupnonmember**  |  0.03506  |  0.03071   | 476891 |  1.142  |               0.2536               |  0.25  |  0.3   |     |
|  **projectscikit-learn:typeissue_reply:author_groupnonmember**  |  0.00145  |  0.01896   | 475984 | 0.0765  |               0.939                |  0.94  |  0.94  |     |
|     **projectscipy:typeissue_reply:author_groupnonmember**      |  0.04997  |  0.02295   | 480656 |  2.177  |              0.02945               |  0.03  | 0.052  |  .  |
| **projectsphinx-gallery:typeissue_reply:author_groupnonmember** |  0.1311   |  0.06896   | 477767 |  1.901  |              0.05729               | 0.057  | 0.089  |  .  |
|       **projectmayavi:typepr_post:author_groupnonmember**       |  0.05076  |  0.07717   | 466016 | 0.6578  |               0.5107               |  0.51  |  0.55  |     |
|       **projectnumpy:typepr_post:author_groupnonmember**        |   0.104   |  0.02493   | 454120 |  4.17   |             0.00003047             | 0.0001 | 0.0002 | *** |
|       **projectpandas:typepr_post:author_groupnonmember**       |  0.1548   |  0.02104   | 439167 |  7.358  |         0.0000000000001873         | 0.0001 | 0.0002 | *** |
|    **projectscikit-image:typepr_post:author_groupnonmember**    |  0.2347   |  0.03607   | 455072 |  6.505  |          0.00000000007796          | 0.0001 | 0.0002 | *** |
|    **projectscikit-learn:typepr_post:author_groupnonmember**    |  0.1988   |  0.02328   | 450979 |  8.541  |       0.00000000000000001336       | 0.0001 | 0.0002 | *** |
|       **projectscipy:typepr_post:author_groupnonmember**        |  0.1208   |   0.0275   | 463818 |  4.392  |             0.00001122             | 0.0001 | 0.0002 | *** |
|   **projectsphinx-gallery:typepr_post:author_groupnonmember**   |  0.2689   |  0.08988   | 481223 |  2.992  |              0.00277               | 0.003  | 0.006  | **  |
|      **projectmayavi:typepr_reply:author_groupnonmember**       |  0.06305  |  0.06747   | 437480 | 0.9344  |               0.3501               |  0.35  |  0.4   |     |
|       **projectnumpy:typepr_reply:author_groupnonmember**       |  0.03613  |  0.02112   | 411395 |  1.711  |              0.08712               | 0.087  | 0.126  |     |
|      **projectpandas:typepr_reply:author_groupnonmember**       |  0.02014  |  0.01769   | 374526 |  1.139  |               0.2548               |  0.26  |  0.31  |     |
|   **projectscikit-image:typepr_reply:author_groupnonmember**    |  0.03983  |  0.03062   | 422874 |  1.301  |               0.1933               | 0.193  | 0.244  |     |
|   **projectscikit-learn:typepr_reply:author_groupnonmember**    | -0.01317  |   0.0197   | 399785 | -0.6685 |               0.5038               |  0.5   |  0.55  |     |
|       **projectscipy:typepr_reply:author_groupnonmember**       |  0.01785  |  0.02357   | 437080 | 0.7573  |               0.4489               |  0.45  |  0.5   |     |
|  **projectsphinx-gallery:typepr_reply:author_groupnonmember**   |  0.09414  |  0.06826   | 481223 |  1.379  |               0.1678               | 0.168  | 0.224  |     |


```r
anova_results = anova(creators_v_commenters_emotion_by_project)
pander(anova_results)
```


-----------------------------------------------------------------------------
            &nbsp;               Sum Sq   Mean Sq   NumDF   DenDF    F value 
------------------------------- -------- --------- ------- -------- ---------
          **project**            65.64     9.377      7     118969    54.67  

           **type**              92.59     30.86      3     438325    179.9  

       **author_group**          3.859     3.859      1     168225    22.5   

       **project:type**          206.6     9.836     21     393743    57.35  

   **project:author_group**      9.588     1.37       7     239876    7.986  

     **type:author_group**        1.95    0.6499      3     439926    3.789  

 **project:type:author_group**    43.1     2.052     21     397412    11.97  
-----------------------------------------------------------------------------

Table: Type III Analysis of Variance Table with Satterthwaite's method (continued below)

 
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            &nbsp;                                                                                                                                       Pr(>F)                                                                                                                         
------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
          **project**                                                                                             0.000000000000000000000000000000000000000000000000000000000000000000000000000001634                                                                                   

           **type**                                                                            0.00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001303                                                                

       **author_group**                                                                                                                               0.000002105                                                                                                                       

       **project:type**          0.0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001708 

   **project:author_group**                                                                                                                          0.00000000099                                                                                                                      

     **type:author_group**                                                                                                                               0.0099                                                                                                                         

 **project:type:author_group**                                                                                                       0.00000000000000000000000000000000000000002341                                                                                                     
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


These results are quite different from our results conducted over a smaller
dataset last year. One potential reason is that these effects may be
time-dependent. Our next model explores this possibility by adding a time term.



![**Figure**. Sentiment by contribution type (ticket vs. comment) and community membership at the time of posting (member vs. nonmember).](../../figures/sentiment_analysis/ossc-sentiment_membership_contribution-aggregated-knitr.jpg)



![**Figure**. Sentiment by contribution type (ticket vs. comment) and community membership at the time of posting (member vs. nonmember) for each project.](../../figures/sentiment_analysis/ossc-sentiment_membership_contribution-by_project-knitr.jpg)

### Model 1.2: Do tickets and comments materially differ in emotion over time?
>>>>>>> d5ab35a... Got the damn p-value at last



```r
<<<<<<< HEAD
# do issues and comments materially differ in emotion over time?
creators_v_commenters_emotion_time = lmer(compound_emotion ~ type * author_group * ns(date) +
                                            (1 | project) +
                                            (1 | author_name),
                                          data = sentiment_frame,
                                          REML=FALSE)

=======
# do tickets and comments materially differ in emotion over time?
creators_v_commenters_emotion_by_project_time = lmer(compound_emotion ~ project * type * author_group * ns(date) +
                                                       (1 | author_name),
                                                     data = sentiment_frame,
                                                     REML=FALSE)
>>>>>>> d5ab35a... Got the damn p-value at last
# print results
pander_lme(creators_v_commenters_emotion_time)
```



<<<<<<< HEAD
|                    &nbsp;                    | Estimate | Std..Error | t.value |   p    | sig |
|:--------------------------------------------:|:--------:|:----------:|:-------:|:------:|:---:|
|               **(Intercept)**                |  0.2249  |  0.01132   |  19.86  | 0.0001 | *** |
|                **typeissue**                 | -0.1865  |  0.005778  | -32.29  | 0.0001 | *** |
|          **author_groupnonmember**           | 0.02776  |  0.008433  |  3.292  | 0.001  | **  |
|                 **ns(date)**                 | -0.03248 |  0.004935  | -6.581  | 0.0001 | *** |
|     **typeissue:author_groupnonmember**      | -0.0586  |  0.01305   | -4.489  | 0.0001 | *** |
|            **typeissue:ns(date)**            |  0.2179  |  0.01088   |  20.02  | 0.0001 | *** |
|      **author_groupnonmember:ns(date)**      | -0.0623  |  0.01423   | -4.379  | 0.0001 | *** |
| **typeissue:author_groupnonmember:ns(date)** |  0.1206  |  0.02372   |  5.085  | 0.0001 | *** |
=======
|                                  &nbsp;                                  | Estimate | Std..Error |   df   | t.value  |           Pr...t..           |   p    | p_adj  | sig |
|:------------------------------------------------------------------------:|:--------:|:----------:|:------:|:--------:|:----------------------------:|:------:|:------:|:---:|
|                             **(Intercept)**                              | -0.07142 |  0.02893   | 464782 |  -2.469  |           0.01356            | 0.014  | 0.028  |  *  |
|                            **projectmayavi**                             |  0.2935  |   0.2932   | 481190 |  1.001   |            0.3168            |  0.32  |  0.4   |     |
|                             **projectnumpy**                             |  0.0598  |  0.03732   | 481718 |  1.602   |            0.1091            | 0.109  | 0.171  |     |
|                            **projectpandas**                             |  0.1039  |  0.03149   | 476060 |  3.299   |          0.0009705           | 0.001  | 0.004  | **  |
|                         **projectscikit-image**                          | -0.05047 |  0.06241   | 475776 | -0.8086  |            0.4187            |  0.42  |  0.51  |     |
|                         **projectscikit-learn**                          |  0.1268  |  0.03608   | 481074 |  3.513   |          0.0004425           | 0.0004 | 0.002  | **  |
|                             **projectscipy**                             | 0.09733  |  0.05494   | 477088 |  1.771   |           0.07649            | 0.076  |  0.13  |     |
|                        **projectsphinx-gallery**                         | -0.4451  |   0.2608   | 469225 |  -1.707  |           0.08785            | 0.088  | 0.146  |     |
|                           **typeissue_reply**                            |  0.1989  |  0.02957   | 481702 |  6.726   |       0.00000000001741       | 0.0001 |   0    | *** |
|                             **typepr_post**                              |  -0.115  |  0.03219   | 481545 |  -3.572  |           0.000354           | 0.0004 | 0.002  | **  |
|                             **typepr_reply**                             |  0.2842  |  0.02887   | 481600 |  9.842   | 0.00000000000000000000007437 | 0.0001 |   0    | *** |
|                        **author_groupnonmember**                         | -0.04141 |  0.03631   | 436956 |  -1.14   |            0.2541            |  0.25  |  0.33  |     |
|                               **ns(date)**                               |  0.3904  |  0.05373   | 481276 |  7.266   |      0.0000000000003704      | 0.0001 |   0    | *** |
|                    **projectmayavi:typeissue_reply**                     |  -0.235  |    0.3     | 471048 | -0.7831  |            0.4336            |  0.43  |  0.51  |     |
|                     **projectnumpy:typeissue_reply**                     |  -0.06   |  0.03748   | 479706 |  -1.601  |            0.1094            | 0.109  | 0.171  |     |
|                    **projectpandas:typeissue_reply**                     |  -0.086  |  0.03212   | 481560 |  -2.678  |           0.007414           | 0.007  | 0.017  |  *  |
|                 **projectscikit-image:typeissue_reply**                  | 0.03649  |   0.0652   | 471325 |  0.5596  |            0.5757            |  0.58  |  0.65  |     |
|                 **projectscikit-learn:typeissue_reply**                  | -0.06171 |  0.03697   | 479914 |  -1.669  |           0.09507            | 0.095  | 0.156  |     |
|                     **projectscipy:typeissue_reply**                     | -0.07226 |  0.05672   | 473417 |  -1.274  |            0.2026            | 0.203  |  0.28  |     |
|                **projectsphinx-gallery:typeissue_reply**                 |  0.2889  |   0.2814   | 467369 |  1.027   |            0.3045            |  0.3   |  0.38  |     |
|                      **projectmayavi:typepr_post**                       | -0.0789  |   0.3148   | 469453 | -0.2507  |            0.8021            |  0.8   |  0.81  |     |
|                       **projectnumpy:typepr_post**                       | 0.08245  |  0.04393   | 477873 |  1.877   |            0.0605            |  0.06  | 0.108  |     |
|                      **projectpandas:typepr_post**                       |  0.1363  |  0.03717   | 480310 |  3.665   |          0.0002469           | 0.0002 | 0.001  | **  |
|                   **projectscikit-image:typepr_post**                    |  0.1867  |  0.06902   | 471425 |  2.705   |           0.006829           | 0.007  | 0.017  |  *  |
|                   **projectscikit-learn:typepr_post**                    |  0.1977  |   0.0422   | 478077 |  4.685   |         0.000002796          | 0.0001 |   0    | *** |
|                       **projectscipy:typepr_post**                       |  0.181   |  0.06106   | 472770 |  2.965   |           0.00303            | 0.003  | 0.008  | **  |
|                  **projectsphinx-gallery:typepr_post**                   |  1.052   |   0.3377   | 467016 |  3.114   |           0.001846           | 0.002  | 0.006  | **  |
|                      **projectmayavi:typepr_reply**                      | -0.5316  |   0.304    | 471081 |  -1.749  |           0.08036            |  0.08  | 0.135  |     |
|                      **projectnumpy:typepr_reply**                       | -0.06105 |  0.03783   | 479951 |  -1.614  |            0.1066            | 0.107  | 0.171  |     |
|                      **projectpandas:typepr_reply**                      | -0.1143  |  0.03164   | 481677 |  -3.614  |          0.0003015           | 0.0003 | 0.001  | **  |
|                   **projectscikit-image:typepr_reply**                   |  0.117   |  0.06285   | 471881 |  1.862   |           0.06257            | 0.063  |  0.11  |     |
|                   **projectscikit-learn:typepr_reply**                   | -0.03613 |  0.03605   | 480323 |  -1.002  |            0.3163            |  0.32  |  0.4   |     |
|                      **projectscipy:typepr_reply**                       | -0.0399  |  0.05536   | 473912 | -0.7206  |            0.4711            |  0.47  |  0.55  |     |
|                  **projectsphinx-gallery:typepr_reply**                  |  0.509   |   0.2723   | 468137 |  1.869   |           0.06165            | 0.062  |  0.11  |     |
|                 **projectmayavi:author_groupnonmember**                  | -0.09589 |   0.3004   | 481617 | -0.3191  |            0.7496            |  0.75  |  0.78  |     |
|                  **projectnumpy:author_groupnonmember**                  | 0.05904  |  0.05117   | 446072 |  1.154   |            0.2486            | 0.249  |  0.33  |     |
|                 **projectpandas:author_groupnonmember**                  | 0.06581  |  0.04133   | 429095 |  1.592   |            0.1114            | 0.111  | 0.171  |     |
|              **projectscikit-image:author_groupnonmember**               |  0.2038  |  0.08576   | 461477 |  2.376   |            0.0175            | 0.018  | 0.035  |  *  |
|              **projectscikit-learn:author_groupnonmember**               | -0.0613  |  0.04836   | 432852 |  -1.268  |            0.2049            | 0.205  |  0.28  |     |
|                  **projectscipy:author_groupnonmember**                  | 0.04914  |  0.06875   | 463350 |  0.7148  |            0.4747            |  0.48  |  0.55  |     |
|             **projectsphinx-gallery:author_groupnonmember**              |  0.9374  |   0.3574   | 480772 |  2.623   |           0.008713           | 0.009  |  0.02  |  *  |
|                **typeissue_reply:author_groupnonmember**                 | 0.09961  |  0.04013   | 473240 |  2.482   |           0.01305            | 0.013  | 0.027  |  *  |
|                  **typepr_post:author_groupnonmember**                   |  0.1564  |  0.04637   | 455766 |  3.372   |          0.0007473           | 0.001  | 0.004  | **  |
|                  **typepr_reply:author_groupnonmember**                  |  0.1099  |  0.04111   | 413352 |  2.674   |           0.007492           | 0.008  | 0.018  |  *  |
|                        **projectmayavi:ns(date)**                        | -0.8649  |   0.5407   | 473893 |   -1.6   |            0.1097            |  0.11  | 0.171  |     |
|                        **projectnumpy:ns(date)**                         | -0.3054  |  0.07094   | 480511 |  -4.306  |          0.00001665          | 0.0001 |   0    | *** |
|                        **projectpandas:ns(date)**                        | -0.2339  |  0.05924   | 481700 |  -3.948  |          0.00007891          | 0.0001 |   0    | *** |
|                     **projectscikit-image:ns(date)**                     | -0.0758  |   0.1158   | 472797 | -0.6547  |            0.5126            |  0.51  |  0.58  |     |
|                     **projectscikit-learn:ns(date)**                     | -0.3053  |  0.06788   | 480782 |  -4.497  |          0.00000689          | 0.0001 |   0    | *** |
|                        **projectscipy:ns(date)**                         | -0.3621  |   0.1034   | 474742 |  -3.503  |          0.0004607           |   0    | 0.0001 | *** |
|                    **projectsphinx-gallery:ns(date)**                    |  0.6064  |   0.4144   | 468471 |  1.463   |            0.1434            | 0.143  | 0.203  |     |
|                       **typeissue_reply:ns(date)**                       |  -0.33   |  0.05546   | 481535 |  -5.951  |        0.000000002673        | 0.0001 |   0    | *** |
|                         **typepr_post:ns(date)**                         |  0.4114  |  0.05975   | 481053 |  6.885   |      0.000000000005783       | 0.0001 |   0    | *** |
|                        **typepr_reply:ns(date)**                         | -0.4407  |  0.05432   | 481640 |  -8.113  |     0.000000000000000493     | 0.0001 |   0    | *** |
|                    **author_groupnonmember:ns(date)**                    |  0.2077  |  0.06767   | 435275 |   3.07   |           0.00214            | 0.002  | 0.006  | **  |
|         **projectmayavi:typeissue_reply:author_groupnonmember**          | -0.09092 |   0.3106   | 474906 | -0.2927  |            0.7697            |  0.77  |  0.79  |     |
|          **projectnumpy:typeissue_reply:author_groupnonmember**          | -0.08426 |  0.05681   | 473339 |  -1.483  |            0.138             | 0.138  | 0.202  |     |
|         **projectpandas:typeissue_reply:author_groupnonmember**          | 0.009619 |  0.04607   | 471814 |  0.2088  |            0.8346            |  0.84  |  0.85  |     |
|      **projectscikit-image:typeissue_reply:author_groupnonmember**       | -0.2292  |  0.09649   | 479094 |  -2.375  |           0.01753            | 0.018  | 0.035  |  *  |
|      **projectscikit-learn:typeissue_reply:author_groupnonmember**       | -0.01954 |  0.05351   | 472072 | -0.3652  |            0.715             |  0.72  |  0.76  |     |
|          **projectscipy:typeissue_reply:author_groupnonmember**          | -0.05975 |  0.07571   | 479188 | -0.7892  |             0.43             |  0.43  |  0.51  |     |
|     **projectsphinx-gallery:typeissue_reply:author_groupnonmember**      | -0.9054  |   0.402    | 477149 |  -2.252  |           0.02433            | 0.024  | 0.046  |  *  |
|           **projectmayavi:typepr_post:author_groupnonmember**            | -0.1139  |   0.3413   | 479485 | -0.3337  |            0.7386            |  0.74  |  0.78  |     |
|            **projectnumpy:typepr_post:author_groupnonmember**            | -0.07429 |  0.06668   | 463688 |  -1.114  |            0.2652            |  0.26  |  0.34  |     |
|           **projectpandas:typepr_post:author_groupnonmember**            | -0.1936  |   0.058    | 451587 |  -3.339  |          0.0008418           | 0.001  | 0.004  | **  |
|        **projectscikit-image:typepr_post:author_groupnonmember**         | -0.2546  |   0.1022   | 471426 |  -2.491  |           0.01272            | 0.013  | 0.027  |  *  |
|        **projectscikit-learn:typepr_post:author_groupnonmember**         | -0.2544  |  0.06247   | 456335 |  -4.073  |          0.0000465           | 0.0001 |   0    | *** |
|            **projectscipy:typepr_post:author_groupnonmember**            | -0.1223  |  0.08257   | 469774 |  -1.481  |            0.1386            | 0.139  | 0.202  |     |
|       **projectsphinx-gallery:typepr_post:author_groupnonmember**        |  -1.277  |   0.5314   | 481635 |  -2.403  |           0.01627            | 0.016  | 0.032  |  *  |
|           **projectmayavi:typepr_reply:author_groupnonmember**           |  0.2975  |   0.3228   | 480411 |  0.9217  |            0.3567            |  0.36  |  0.44  |     |
|           **projectnumpy:typepr_reply:author_groupnonmember**            | -0.1063  |  0.05766   | 431224 |  -1.843  |           0.06532            | 0.065  | 0.112  |     |
|           **projectpandas:typepr_reply:author_groupnonmember**           | -0.01919 |  0.04909   | 389000 |  -0.391  |            0.6958            |  0.7   |  0.75  |     |
|        **projectscikit-image:typepr_reply:author_groupnonmember**        | -0.3466  |   0.0917   | 454154 |  -3.78   |          0.0001568           | 0.0002 | 0.001  | **  |
|        **projectscikit-learn:typepr_reply:author_groupnonmember**        | -0.03091 |  0.05366   | 414439 |  -0.576  |            0.5646            |  0.56  |  0.63  |     |
|           **projectscipy:typepr_reply:author_groupnonmember**            | -0.1128  |  0.07374   | 452969 |  -1.53   |            0.1261            | 0.126  |  0.19  |     |
|       **projectsphinx-gallery:typepr_reply:author_groupnonmember**       |  -1.025  |   0.3971   | 481662 |  -2.58   |           0.009875           |  0.01  | 0.022  |  *  |
|                **projectmayavi:typeissue_reply:ns(date)**                |  0.6449  |   0.5554   | 470798 |  1.161   |            0.2456            | 0.246  |  0.33  |     |
|                **projectnumpy:typeissue_reply:ns(date)**                 |  0.2767  |  0.07223   | 478345 |  3.831   |          0.0001274           | 0.0001 |   0    | *** |
|                **projectpandas:typeissue_reply:ns(date)**                |  0.2436  |  0.06112   | 480754 |  3.986   |          0.00006713          | 0.0001 |   0    | *** |
|             **projectscikit-image:typeissue_reply:ns(date)**             |  0.1693  |   0.1214   | 470558 |  1.394   |            0.1633            | 0.163  | 0.229  |     |
|             **projectscikit-learn:typeissue_reply:ns(date)**             |  0.2207  |  0.07029   | 478556 |   3.14   |           0.001689           | 0.002  | 0.006  | **  |
|                **projectscipy:typeissue_reply:ns(date)**                 |   0.33   |   0.1069   | 472488 |  3.087   |           0.00202            | 0.002  | 0.006  | **  |
|            **projectsphinx-gallery:typeissue_reply:ns(date)**            | -0.2473  |   0.4456   | 467092 | -0.5548  |            0.579             |  0.58  |  0.65  |     |
|                  **projectmayavi:typepr_post:ns(date)**                  | -0.03535 |   0.5792   | 469329 | -0.06104 |            0.9513            |  0.95  |  0.95  |     |
|                  **projectnumpy:typepr_post:ns(date)**                   | -0.2415  |  0.08278   | 476849 |  -2.917  |           0.003532           | 0.004  |  0.01  |  *  |
|                  **projectpandas:typepr_post:ns(date)**                  | -0.5522  |  0.06939   | 479535 |  -7.957  |     0.000000000000001764     | 0.0001 |   0    | *** |
|               **projectscikit-image:typepr_post:ns(date)**               | -0.3635  |   0.1301   | 470553 |  -2.794  |           0.005209           | 0.005  | 0.012  |  *  |
|               **projectscikit-learn:typepr_post:ns(date)**               | -0.3994  |  0.07991   | 476969 |  -4.999  |         0.0000005779         | 0.0001 |   0    | *** |
|                  **projectscipy:typepr_post:ns(date)**                   | -0.4851  |   0.1152   | 471925 |  -4.212  |          0.00002537          | 0.0001 |   0    | *** |
|              **projectsphinx-gallery:typepr_post:ns(date)**              |  -1.91   |   0.5346   | 466749 |  -3.573  |          0.0003531           | 0.0004 | 0.002  | **  |
|                 **projectmayavi:typepr_reply:ns(date)**                  |  1.141   |   0.5658   | 470623 |  2.017   |           0.04371            | 0.044  | 0.082  |  .  |
|                  **projectnumpy:typepr_reply:ns(date)**                  |  0.3805  |  0.07241   | 478670 |  5.256   |         0.0000001476         | 0.0001 |   0    | *** |
|                 **projectpandas:typepr_reply:ns(date)**                  |  0.2991  |  0.06018   | 481059 |   4.97   |         0.0000006685         | 0.0001 |   0    | *** |
|              **projectscikit-image:typepr_reply:ns(date)**               | 0.06096  |   0.1176   | 471036 |  0.5185  |            0.6041            |  0.6   |  0.66  |     |
|              **projectscikit-learn:typepr_reply:ns(date)**               |  0.201   |  0.06874   | 478989 |  2.924   |           0.003457           | 0.004  |  0.01  |  *  |
|                  **projectscipy:typepr_reply:ns(date)**                  |  0.3562  |   0.1047   | 472958 |  3.402   |          0.0006691           | 0.001  | 0.004  | **  |
|             **projectsphinx-gallery:typepr_reply:ns(date)**              | -0.6324  |   0.4319   | 467757 |  -1.464  |            0.1431            | 0.143  | 0.203  |     |
|             **projectmayavi:author_groupnonmember:ns(date)**             |  0.2295  |   0.5537   | 478095 |  0.4146  |            0.6785            |  0.68  |  0.74  |     |
|             **projectnumpy:author_groupnonmember:ns(date)**              | -0.2451  |   0.095    | 444095 |  -2.58   |           0.00988            |  0.01  | 0.022  |  *  |
|             **projectpandas:author_groupnonmember:ns(date)**             | -0.2661  |  0.07748   | 425726 |  -3.435  |          0.0005932           | 0.001  | 0.004  | **  |
|          **projectscikit-image:author_groupnonmember:ns(date)**          | -0.4767  |   0.1579   | 451630 |  -3.019  |           0.002536           | 0.002  | 0.006  | **  |
|          **projectscikit-learn:author_groupnonmember:ns(date)**          | 0.09039  |  0.08976   | 432127 |  1.007   |            0.3139            |  0.31  |  0.39  |     |
|             **projectscipy:author_groupnonmember:ns(date)**              |  -0.141  |   0.1269   | 465013 |  -1.111  |            0.2664            |  0.27  |  0.35  |     |
|         **projectsphinx-gallery:author_groupnonmember:ns(date)**         |  -1.773  |   0.5782   | 481518 |  -3.066  |           0.002166           | 0.002  | 0.006  | **  |
|            **typeissue_reply:author_groupnonmember:ns(date)**            | -0.2748  |  0.07441   | 472588 |  -3.693  |          0.0002213           | 0.0002 | 0.001  | **  |
|              **typepr_post:author_groupnonmember:ns(date)**              | -0.4415  |   0.0882   | 443673 |  -5.005  |         0.0000005579         | 0.0001 |   0    | *** |
|             **typepr_reply:author_groupnonmember:ns(date)**              | -0.3221  |  0.07842   | 385299 |  -4.107  |          0.00004007          | 0.0001 |   0    | *** |
|     **projectmayavi:typeissue_reply:author_groupnonmember:ns(date)**     |  0.1778  |   0.5737   | 475099 |  0.3099  |            0.7566            |  0.76  |  0.78  |     |
|     **projectnumpy:typeissue_reply:author_groupnonmember:ns(date)**      |  0.2955  |   0.105    | 472013 |  2.813   |           0.004905           | 0.005  | 0.012  |  *  |
|     **projectpandas:typeissue_reply:author_groupnonmember:ns(date)**     |  0.1321  |  0.08599   | 470159 |  1.536   |            0.1245            | 0.124  | 0.189  |     |
|  **projectscikit-image:typeissue_reply:author_groupnonmember:ns(date)**  |  0.5036  |   0.1771   | 474578 |  2.843   |           0.004466           | 0.004  |  0.01  |  *  |
|  **projectscikit-learn:typeissue_reply:author_groupnonmember:ns(date)**  | 0.04915  |  0.09886   | 471366 |  0.4972  |            0.6191            |  0.62  |  0.68  |     |
|     **projectscipy:typeissue_reply:author_groupnonmember:ns(date)**      |  0.2069  |   0.1391   | 479179 |  1.487   |            0.1369            | 0.137  | 0.202  |     |
| **projectsphinx-gallery:typeissue_reply:author_groupnonmember:ns(date)** |  1.756   |   0.6482   | 477271 |  2.709   |           0.006742           | 0.007  | 0.017  |  *  |
|       **projectmayavi:typepr_post:author_groupnonmember:ns(date)**       |  0.2554  |   0.6346   | 481142 |  0.4024  |            0.6874            |  0.69  |  0.74  |     |
|       **projectnumpy:typepr_post:author_groupnonmember:ns(date)**        |  0.2683  |   0.1262   | 452489 |  2.126   |           0.03348            | 0.034  | 0.064  |  .  |
|       **projectpandas:typepr_post:author_groupnonmember:ns(date)**       |  0.5937  |   0.1079   | 439459 |   5.5    |        0.00000003804         | 0.0001 |   0    | *** |
|    **projectscikit-image:typepr_post:author_groupnonmember:ns(date)**    |  0.8771  |   0.1929   | 461977 |  4.546   |         0.000005462          | 0.0001 |   0    | *** |
|    **projectscikit-learn:typepr_post:author_groupnonmember:ns(date)**    |  0.8122  |   0.1177   | 449642 |  6.901   |      0.000000000005156       | 0.0001 |   0    | *** |
|       **projectscipy:typepr_post:author_groupnonmember:ns(date)**        |  0.3898  |   0.1554   | 466471 |  2.509   |            0.0121            | 0.012  | 0.026  |  *  |
|   **projectsphinx-gallery:typepr_post:author_groupnonmember:ns(date)**   |  2.514   |   0.8568   | 481422 |  2.934   |           0.003347           | 0.003  | 0.008  | **  |
|      **projectmayavi:typepr_reply:author_groupnonmember:ns(date)**       | -0.4406  |   0.6119   | 481672 |  -0.72   |            0.4715            |  0.47  |  0.55  |     |
|       **projectnumpy:typepr_reply:author_groupnonmember:ns(date)**       |  0.2888  |   0.1094   | 403957 |   2.64   |           0.008287           | 0.008  | 0.018  |  *  |
|      **projectpandas:typepr_reply:author_groupnonmember:ns(date)**       |  0.128   |  0.09238   | 369476 |  1.386   |            0.1658            | 0.166  | 0.231  |     |
|   **projectscikit-image:typepr_reply:author_groupnonmember:ns(date)**    |  0.7782  |   0.1716   | 437770 |  4.535   |         0.000005748          | 0.0001 |   0    | *** |
|   **projectscikit-learn:typepr_reply:author_groupnonmember:ns(date)**    | 0.07319  |   0.1014   | 396882 |  0.722   |            0.4703            |  0.47  |  0.55  |     |
|       **projectscipy:typepr_reply:author_groupnonmember:ns(date)**       |  0.2691  |   0.1383   | 444425 |  1.946   |           0.05163            | 0.052  | 0.095  |  .  |
|  **projectsphinx-gallery:typepr_reply:author_groupnonmember:ns(date)**   |  1.888   |   0.6469   | 481270 |  2.919   |           0.003514           | 0.004  |  0.01  |  *  |


```r
anova_results = anova(creators_v_commenters_emotion_by_project_time)
pander(anova_results)
```


-------------------------------------------------------------------------------
                 &nbsp;                    Sum Sq    Mean Sq    NumDF   DenDF  
---------------------------------------- ---------- ---------- ------- --------
              **project**                  19.21      2.745       7     211475 

                **type**                   13.74       4.58       3     477310 

            **author_group**               0.4516     0.4516      1     435163 

              **ns(date)**                 3.296      3.296       1     391315 

            **project:type**                21.8      1.038      21     425497 

        **project:author_group**           15.74      2.248       7     316100 

         **type:author_group**             0.4742     0.1581      3     477381 

          **project:ns(date)**              46.1      6.586       7     231820 

           **type:ns(date)**               5.027      1.676       3     472099 

       **author_group:ns(date)**          0.003135   0.003135     1     430176 

     **project:type:author_group**         16.16      0.7698     21     428447 

       **project:type:ns(date)**            80.8      3.848      21     408274 

   **project:author_group:ns(date)**       29.55      4.221       7     271775 

     **type:author_group:ns(date)**        0.982      0.3273      3     472397 

 **project:type:author_group:ns(date)**    29.57      1.408      21     411162 
-------------------------------------------------------------------------------

Table: Type III Analysis of Variance Table with Satterthwaite's method (continued below)

 
--------------------------------------------------
                 &nbsp;                   F value 
---------------------------------------- ---------
              **project**                  16.08  

                **type**                   26.83  

            **author_group**               2.645  

              **ns(date)**                 19.31  

            **project:type**               6.082  

        **project:author_group**           13.17  

         **type:author_group**            0.9258  

          **project:ns(date)**             38.58  

           **type:ns(date)**               9.816  

       **author_group:ns(date)**          0.01836 

     **project:type:author_group**         4.509  

       **project:type:ns(date)**           22.54  

   **project:author_group:ns(date)**       24.72  

     **type:author_group:ns(date)**        1.917  

 **project:type:author_group:ns(date)**    8.248  
--------------------------------------------------

Table: Table continues below

 
-------------------------------------------------------------------------------------------------------------------------------------
                 &nbsp;                                                             Pr(>F)                                           
---------------------------------------- --------------------------------------------------------------------------------------------
              **project**                                                 0.000000000000000000002752                                 

                **type**                                                    0.00000000000000002428                                   

            **author_group**                                                        0.1039                                           

              **ns(date)**                                                        0.00001113                                         

            **project:type**                                                0.00000000000000002707                                   

        **project:author_group**                                            0.00000000000000004429                                   

         **type:author_group**                                                      0.4272                                           

          **project:ns(date)**                           0.000000000000000000000000000000000000000000000000000001605                 

           **type:ns(date)**                                                     0.000001803                                         

       **author_group:ns(date)**                                                    0.8922                                           

     **project:type:author_group**                                             0.00000000002487                                      

       **project:type:ns(date)**          0.0000000000000000000000000000000000000000000000000000000000000000000000000000000000000063 

   **project:author_group:ns(date)**                               0.0000000000000000000000000000000005813                           

     **type:author_group:ns(date)**                                                 0.1243                                           

 **project:type:author_group:ns(date)**                                0.00000000000000000000000006239                               
-------------------------------------------------------------------------------------------------------------------------------------
>>>>>>> d5ab35a... Got the damn p-value at last

Interestingly, we see much more volatility here in the emotion dynamics
of community members relative to the community nonmembers over time, even
when we collapse across all projects.

Perhaps more interestingly, we see a difference in the affect dynamics
only in the last year: Members' issues are becoming more positive, while
nonmembers' issues are becoming more negative.

We'll need to do an analysis to follow up on this.


```
## `geom_smooth()` using method = 'gam' and formula 'y ~ s(x, bs = "cs")'
## `geom_smooth()` using method = 'gam' and formula 'y ~ s(x, bs = "cs")'
## `geom_smooth()` using method = 'gam' and formula 'y ~ s(x, bs = "cs")'
## `geom_smooth()` using method = 'gam' and formula 'y ~ s(x, bs = "cs")'
## `geom_smooth()` using method = 'gam' and formula 'y ~ s(x, bs = "cs")'
```
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
    member      comment         0          318300 

    member      comment         1          40406  

    member      comment         2           1082  

    member      comment         3            75   

    member      comment         4            2    

    member       issue          0          41934  

    member       issue          1           1907  

    member       issue          2           746   

    member       issue          3            25   

  nonmember     comment         0          39330  

  nonmember     comment         1           9103  

  nonmember     comment         2           622   

  nonmember     comment         3            42   

  nonmember     comment         4            1    

  nonmember      issue          0          15480  

  nonmember      issue          1           1886  

  nonmember      issue          2           320   

  nonmember      issue          3            6    
--------------------------------------------------

```r
# do users tend to express appreciation and gratitude differently by group and content?
<<<<<<< HEAD
creators_v_commenters_gratitude = glmer(grateful_count ~ author_group * type +
                                          (1 | project) +
=======
creators_v_commenters_gratitude_by_project = lmer(log(grateful_count + 1) ~ project * author_group * type +
>>>>>>> d5ab35a... Got the damn p-value at last
                                          (1 | author_name),
                                        data=sentiment_frame)

# print results
summary(creators_v_commenters_gratitude)
```

```
## Generalized linear mixed model fit by maximum likelihood (Laplace
##   Approximation) [glmerMod]
##  Family: poisson  ( log )
## Formula: 
## grateful_count ~ author_group * type + (1 | project) + (1 | author_name)
##    Data: sentiment_frame
## 
##       AIC       BIC    logLik  deviance  df.resid 
##  345477.9  345544.3 -172733.0  345465.9    471261 
## 
## Scaled residuals: 
##     Min      1Q  Median      3Q     Max 
## -1.0216 -0.3623 -0.3124 -0.2255 19.2207 
## 
## Random effects:
##  Groups      Name        Variance Std.Dev.
##  author_name (Intercept) 0.590401 0.76838 
##  project     (Intercept) 0.001576 0.03969 
## Number of obs: 471267, groups:  author_name, 18012; project, 8
## 
## Fixed effects:
##                                 Estimate Std. Error z value
## (Intercept)                     -1.92452    0.02362 -81.474
## author_groupnonmember            0.23918    0.02103  11.373
## typeissue                       -0.51398    0.01809 -28.406
## author_groupnonmember:typeissue  0.03485    0.02927   1.191
##                                            Pr(>|z|)    
## (Intercept)                     <0.0000000000000002 ***
## author_groupnonmember           <0.0000000000000002 ***
## typeissue                       <0.0000000000000002 ***
## author_groupnonmember:typeissue               0.234    
## ---
## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
## 
## Correlation of Fixed Effects:
##             (Intr) athr_g typess
## athr_grpnnm -0.522              
## typeissue   -0.140  0.160       
## athr_grpnn:  0.072 -0.291 -0.609
```

```
## Linear mixed model fit by REML. t-tests use Satterthwaite's method [
## lmerModLmerTest]
## Formula: log(grateful_count + 1) ~ project * author_group * type + (1 |  
##     author_name)
##    Data: sentiment_frame
## 
## REML criterion at convergence: -79905.8
## 
## Scaled residuals: 
##     Min      1Q  Median      3Q     Max 
## -3.1726 -0.4812 -0.2706 -0.0640  6.6806 
## 
## Random effects:
##  Groups      Name        Variance Std.Dev.
##  author_name (Intercept) 0.01858  0.1363  
##  Residual                0.04782  0.2187  
## Number of obs: 481728, groups:  author_name, 18471
## 
## Fixed effects:
##                                                                   Estimate
## (Intercept)                                                      0.0923942
## projectmayavi                                                    0.0007727
## projectnumpy                                                    -0.0131129
## projectpandas                                                   -0.0246138
## projectscikit-image                                             -0.0442431
## projectscikit-learn                                             -0.0130242
## projectscipy                                                    -0.0063950
## projectsphinx-gallery                                           -0.0050508
## author_groupnonmember                                           -0.0215417
## typeissue_reply                                                  0.0304109
## typepr_post                                                      0.1373269
## typepr_reply                                                     0.0603030
## projectmayavi:author_groupnonmember                              0.0798275
## projectnumpy:author_groupnonmember                               0.0081659
## projectpandas:author_groupnonmember                              0.0096590
## projectscikit-image:author_groupnonmember                        0.0614578
## projectscikit-learn:author_groupnonmember                        0.1130811
## projectscipy:author_groupnonmember                               0.0246554
## projectsphinx-gallery:author_groupnonmember                      0.0573715
## projectmayavi:typeissue_reply                                   -0.0016627
## projectnumpy:typeissue_reply                                    -0.0105986
## projectpandas:typeissue_reply                                    0.0094743
## projectscikit-image:typeissue_reply                              0.0299111
## projectscikit-learn:typeissue_reply                              0.0067991
## projectscipy:typeissue_reply                                    -0.0032737
## projectsphinx-gallery:typeissue_reply                           -0.0070209
## projectmayavi:typepr_post                                       -0.1725511
## projectnumpy:typepr_post                                        -0.1207498
## projectpandas:typepr_post                                       -0.1317540
## projectscikit-image:typepr_post                                 -0.1214606
## projectscikit-learn:typepr_post                                 -0.0622864
## projectscipy:typepr_post                                        -0.1404428
## projectsphinx-gallery:typepr_post                               -0.1395683
## projectmayavi:typepr_reply                                       0.1065989
## projectnumpy:typepr_reply                                        0.0246531
## projectpandas:typepr_reply                                       0.0414495
## projectscikit-image:typepr_reply                                 0.0652463
## projectscikit-learn:typepr_reply                                 0.0259939
## projectscipy:typepr_reply                                        0.0408183
## projectsphinx-gallery:typepr_reply                               0.0061408
## author_groupnonmember:typeissue_reply                            0.0573556
## author_groupnonmember:typepr_post                               -0.0758783
## author_groupnonmember:typepr_reply                               0.0345167
## projectmayavi:author_groupnonmember:typeissue_reply             -0.0487836
## projectnumpy:author_groupnonmember:typeissue_reply               0.0188311
## projectpandas:author_groupnonmember:typeissue_reply              0.0059654
## projectscikit-image:author_groupnonmember:typeissue_reply       -0.0544768
## projectscikit-learn:author_groupnonmember:typeissue_reply       -0.1279161
## projectscipy:author_groupnonmember:typeissue_reply              -0.0091381
## projectsphinx-gallery:author_groupnonmember:typeissue_reply     -0.0199251
## projectmayavi:author_groupnonmember:typepr_post                  0.0481813
## projectnumpy:author_groupnonmember:typepr_post                   0.0568049
## projectpandas:author_groupnonmember:typepr_post                  0.0641229
## projectscikit-image:author_groupnonmember:typepr_post            0.0327511
## projectscikit-learn:author_groupnonmember:typepr_post            0.1389776
## projectscipy:author_groupnonmember:typepr_post                   0.0554810
## projectsphinx-gallery:author_groupnonmember:typepr_post          0.0335338
## projectmayavi:author_groupnonmember:typepr_reply                -0.1028665
## projectnumpy:author_groupnonmember:typepr_reply                 -0.0182982
## projectpandas:author_groupnonmember:typepr_reply                -0.0232265
## projectscikit-image:author_groupnonmember:typepr_reply          -0.0803810
## projectscikit-learn:author_groupnonmember:typepr_reply          -0.1304609
## projectscipy:author_groupnonmember:typepr_reply                 -0.0423487
## projectsphinx-gallery:author_groupnonmember:typepr_reply        -0.0910718
##                                                                 Std. Error
## (Intercept)                                                      0.0060628
## projectmayavi                                                    0.0301689
## projectnumpy                                                     0.0078178
## projectpandas                                                    0.0067172
## projectscikit-image                                              0.0115308
## projectscikit-learn                                              0.0077201
## projectscipy                                                     0.0094364
## projectsphinx-gallery                                            0.0231538
## author_groupnonmember                                            0.0072357
## typeissue_reply                                                  0.0056028
## typepr_post                                                      0.0061470
## typepr_reply                                                     0.0055293
## projectmayavi:author_groupnonmember                              0.0324510
## projectnumpy:author_groupnonmember                               0.0099925
## projectpandas:author_groupnonmember                              0.0084083
## projectscikit-image:author_groupnonmember                        0.0154389
## projectscikit-learn:author_groupnonmember                        0.0097370
## projectscipy:author_groupnonmember                               0.0115079
## projectsphinx-gallery:author_groupnonmember                      0.0325951
## projectmayavi:typeissue_reply                                    0.0269063
## projectnumpy:typeissue_reply                                     0.0076485
## projectpandas:typeissue_reply                                    0.0062949
## projectscikit-image:typeissue_reply                              0.0113093
## projectscikit-learn:typeissue_reply                              0.0073543
## projectscipy:typeissue_reply                                     0.0094031
## projectsphinx-gallery:typeissue_reply                            0.0243057
## projectmayavi:typepr_post                                        0.0296380
## projectnumpy:typepr_post                                         0.0086927
## projectpandas:typepr_post                                        0.0072111
## projectscikit-image:typepr_post                                  0.0125536
## projectscikit-learn:typepr_post                                  0.0084883
## projectscipy:typepr_post                                         0.0103698
## projectsphinx-gallery:typepr_post                                0.0287713
## projectmayavi:typepr_reply                                       0.0273751
## projectnumpy:typepr_reply                                        0.0076296
## projectpandas:typepr_reply                                       0.0062385
## projectscikit-image:typepr_reply                                 0.0110135
## projectscikit-learn:typepr_reply                                 0.0072373
## projectscipy:typepr_reply                                        0.0092650
## projectsphinx-gallery:typepr_reply                               0.0236107
## author_groupnonmember:typeissue_reply                            0.0075019
## author_groupnonmember:typepr_post                                0.0093436
## author_groupnonmember:typepr_reply                               0.0081010
## projectmayavi:author_groupnonmember:typeissue_reply              0.0310941
## projectnumpy:author_groupnonmember:typeissue_reply               0.0106230
## projectpandas:author_groupnonmember:typeissue_reply              0.0087822
## projectscikit-image:author_groupnonmember:typeissue_reply        0.0164076
## projectscikit-learn:author_groupnonmember:typeissue_reply        0.0101293
## projectscipy:author_groupnonmember:typeissue_reply               0.0122334
## projectsphinx-gallery:author_groupnonmember:typeissue_reply      0.0365387
## projectmayavi:author_groupnonmember:typepr_post                  0.0413309
## projectnumpy:author_groupnonmember:typepr_post                   0.0133929
## projectpandas:author_groupnonmember:typepr_post                  0.0113262
## projectscikit-image:author_groupnonmember:typepr_post            0.0193812
## projectscikit-learn:author_groupnonmember:typepr_post            0.0125123
## projectscipy:author_groupnonmember:typepr_post                   0.0147448
## projectsphinx-gallery:author_groupnonmember:typepr_post          0.0477430
## projectmayavi:author_groupnonmember:typepr_reply                 0.0362196
## projectnumpy:author_groupnonmember:typepr_reply                  0.0113944
## projectpandas:author_groupnonmember:typepr_reply                 0.0095824
## projectscikit-image:author_groupnonmember:typepr_reply           0.0165178
## projectscikit-learn:author_groupnonmember:typepr_reply           0.0106480
## projectscipy:author_groupnonmember:typepr_reply                  0.0126837
## projectsphinx-gallery:author_groupnonmember:typepr_reply         0.0362447
##                                                                         df
## (Intercept)                                                 445466.5363468
## projectmayavi                                               469645.5894608
## projectnumpy                                                470511.1208296
## projectpandas                                               479317.1648414
## projectscikit-image                                         469884.6217240
## projectscikit-learn                                         476407.4923795
## projectscipy                                                468854.0738921
## projectsphinx-gallery                                       464111.3388707
## author_groupnonmember                                       466450.3534502
## typeissue_reply                                             464477.2968593
## typepr_post                                                 464744.2545782
## typepr_reply                                                464760.7153834
## projectmayavi:author_groupnonmember                         464169.7386571
## projectnumpy:author_groupnonmember                          465200.6140438
## projectpandas:author_groupnonmember                         460362.4844441
## projectscikit-image:author_groupnonmember                   452012.5569430
## projectscikit-learn:author_groupnonmember                   458959.6036367
## projectscipy:author_groupnonmember                          471009.9220101
## projectsphinx-gallery:author_groupnonmember                 476584.8876613
## projectmayavi:typeissue_reply                               463928.0764238
## projectnumpy:typeissue_reply                                463876.2872197
## projectpandas:typeissue_reply                               464389.8223491
## projectscikit-image:typeissue_reply                         463134.6544097
## projectscikit-learn:typeissue_reply                         463890.5737856
## projectscipy:typeissue_reply                                463572.4769569
## projectsphinx-gallery:typeissue_reply                       462953.9188329
## projectmayavi:typepr_post                                   463169.9861278
## projectnumpy:typepr_post                                    463981.2341268
## projectpandas:typepr_post                                   464701.0240969
## projectscikit-image:typepr_post                             463292.0819937
## projectscikit-learn:typepr_post                             464066.0497559
## projectscipy:typepr_post                                    463698.4107699
## projectsphinx-gallery:typepr_post                           462972.0944672
## projectmayavi:typepr_reply                                  463490.1883122
## projectnumpy:typepr_reply                                   464123.9300373
## projectpandas:typepr_reply                                  464763.5023393
## projectscikit-image:typepr_reply                            463281.8940733
## projectscikit-learn:typepr_reply                            464163.3519960
## projectscipy:typepr_reply                                   463754.8084597
## projectsphinx-gallery:typepr_reply                          463074.6570223
## author_groupnonmember:typeissue_reply                       481486.8708674
## author_groupnonmember:typepr_post                           462792.7745480
## author_groupnonmember:typepr_reply                          446934.6250575
## projectmayavi:author_groupnonmember:typeissue_reply         480921.4829037
## projectnumpy:author_groupnonmember:typeissue_reply          480559.6298135
## projectpandas:author_groupnonmember:typeissue_reply         480575.7932435
## projectscikit-image:author_groupnonmember:typeissue_reply   480061.4496371
## projectscikit-learn:author_groupnonmember:typeissue_reply   479657.0210856
## projectscipy:author_groupnonmember:typeissue_reply          481574.3959230
## projectsphinx-gallery:author_groupnonmember:typeissue_reply 472668.0848183
## projectmayavi:author_groupnonmember:typepr_post             476540.3770279
## projectnumpy:author_groupnonmember:typepr_post              466367.6994520
## projectpandas:author_groupnonmember:typepr_post             459045.0497757
## projectscikit-image:author_groupnonmember:typepr_post       465728.9032066
## projectscikit-learn:author_groupnonmember:typepr_post       464038.3949171
## projectscipy:author_groupnonmember:typepr_post              472281.7302413
## projectsphinx-gallery:author_groupnonmember:typepr_post     478671.9251972
## projectmayavi:author_groupnonmember:typepr_reply            475510.4549916
## projectnumpy:author_groupnonmember:typepr_reply             455293.6505828
## projectpandas:author_groupnonmember:typepr_reply            439944.9983299
## projectscikit-image:author_groupnonmember:typepr_reply      451531.6465581
## projectscikit-learn:author_groupnonmember:typepr_reply      446457.1820478
## projectscipy:author_groupnonmember:typepr_reply             464221.3389827
## projectsphinx-gallery:author_groupnonmember:typepr_reply    477420.6830401
##                                                             t value
## (Intercept)                                                  15.240
## projectmayavi                                                 0.026
## projectnumpy                                                 -1.677
## projectpandas                                                -3.664
## projectscikit-image                                          -3.837
## projectscikit-learn                                          -1.687
## projectscipy                                                 -0.678
## projectsphinx-gallery                                        -0.218
## author_groupnonmember                                        -2.977
## typeissue_reply                                               5.428
## typepr_post                                                  22.341
## typepr_reply                                                 10.906
## projectmayavi:author_groupnonmember                           2.460
## projectnumpy:author_groupnonmember                            0.817
## projectpandas:author_groupnonmember                           1.149
## projectscikit-image:author_groupnonmember                     3.981
## projectscikit-learn:author_groupnonmember                    11.614
## projectscipy:author_groupnonmember                            2.142
## projectsphinx-gallery:author_groupnonmember                   1.760
## projectmayavi:typeissue_reply                                -0.062
## projectnumpy:typeissue_reply                                 -1.386
## projectpandas:typeissue_reply                                 1.505
## projectscikit-image:typeissue_reply                           2.645
## projectscikit-learn:typeissue_reply                           0.925
## projectscipy:typeissue_reply                                 -0.348
## projectsphinx-gallery:typeissue_reply                        -0.289
## projectmayavi:typepr_post                                    -5.822
## projectnumpy:typepr_post                                    -13.891
## projectpandas:typepr_post                                   -18.271
## projectscikit-image:typepr_post                              -9.675
## projectscikit-learn:typepr_post                              -7.338
## projectscipy:typepr_post                                    -13.543
## projectsphinx-gallery:typepr_post                            -4.851
## projectmayavi:typepr_reply                                    3.894
## projectnumpy:typepr_reply                                     3.231
## projectpandas:typepr_reply                                    6.644
## projectscikit-image:typepr_reply                              5.924
## projectscikit-learn:typepr_reply                              3.592
## projectscipy:typepr_reply                                     4.406
## projectsphinx-gallery:typepr_reply                            0.260
## author_groupnonmember:typeissue_reply                         7.645
## author_groupnonmember:typepr_post                            -8.121
## author_groupnonmember:typepr_reply                            4.261
## projectmayavi:author_groupnonmember:typeissue_reply          -1.569
## projectnumpy:author_groupnonmember:typeissue_reply            1.773
## projectpandas:author_groupnonmember:typeissue_reply           0.679
## projectscikit-image:author_groupnonmember:typeissue_reply    -3.320
## projectscikit-learn:author_groupnonmember:typeissue_reply   -12.628
## projectscipy:author_groupnonmember:typeissue_reply           -0.747
## projectsphinx-gallery:author_groupnonmember:typeissue_reply  -0.545
## projectmayavi:author_groupnonmember:typepr_post               1.166
## projectnumpy:author_groupnonmember:typepr_post                4.241
## projectpandas:author_groupnonmember:typepr_post               5.661
## projectscikit-image:author_groupnonmember:typepr_post         1.690
## projectscikit-learn:author_groupnonmember:typepr_post        11.107
## projectscipy:author_groupnonmember:typepr_post                3.763
## projectsphinx-gallery:author_groupnonmember:typepr_post       0.702
## projectmayavi:author_groupnonmember:typepr_reply             -2.840
## projectnumpy:author_groupnonmember:typepr_reply              -1.606
## projectpandas:author_groupnonmember:typepr_reply             -2.424
## projectscikit-image:author_groupnonmember:typepr_reply       -4.866
## projectscikit-learn:author_groupnonmember:typepr_reply      -12.252
## projectscipy:author_groupnonmember:typepr_reply              -3.339
## projectsphinx-gallery:author_groupnonmember:typepr_reply     -2.513
##                                                                         Pr(>|t|)
## (Intercept)                                                 < 0.0000000000000002
## projectmayavi                                                           0.979567
## projectnumpy                                                            0.093483
## projectpandas                                                           0.000248
## projectscikit-image                                                     0.000125
## projectscikit-learn                                                     0.091594
## projectscipy                                                            0.497966
## projectsphinx-gallery                                                   0.827318
## author_groupnonmember                                                   0.002910
## typeissue_reply                                             0.000000057081451145
## typepr_post                                                 < 0.0000000000000002
## typepr_reply                                                < 0.0000000000000002
## projectmayavi:author_groupnonmember                                     0.013896
## projectnumpy:author_groupnonmember                                      0.413810
## projectpandas:author_groupnonmember                                     0.250661
## projectscikit-image:author_groupnonmember                   0.000068716270898033
## projectscikit-learn:author_groupnonmember                   < 0.0000000000000002
## projectscipy:author_groupnonmember                                      0.032155
## projectsphinx-gallery:author_groupnonmember                             0.078387
## projectmayavi:typeissue_reply                                           0.950727
## projectnumpy:typeissue_reply                                            0.165833
## projectpandas:typeissue_reply                                           0.132302
## projectscikit-image:typeissue_reply                                     0.008174
## projectscikit-learn:typeissue_reply                                     0.355223
## projectscipy:typeissue_reply                                            0.727729
## projectsphinx-gallery:typeissue_reply                                   0.772690
## projectmayavi:typepr_post                                   0.000000005820199724
## projectnumpy:typepr_post                                    < 0.0000000000000002
## projectpandas:typepr_post                                   < 0.0000000000000002
## projectscikit-image:typepr_post                             < 0.0000000000000002
## projectscikit-learn:typepr_post                             0.000000000000217273
## projectscipy:typepr_post                                    < 0.0000000000000002
## projectsphinx-gallery:typepr_post                           0.000001229109856729
## projectmayavi:typepr_reply                                  0.000098614487364109
## projectnumpy:typepr_reply                                               0.001233
## projectpandas:typepr_reply                                  0.000000000030530068
## projectscikit-image:typepr_reply                            0.000000003140439673
## projectscikit-learn:typepr_reply                                        0.000329
## projectscipy:typepr_reply                                   0.000010549210184880
## projectsphinx-gallery:typepr_reply                                      0.794799
## author_groupnonmember:typeissue_reply                       0.000000000000020853
## author_groupnonmember:typepr_post                           0.000000000000000464
## author_groupnonmember:typepr_reply                          0.000020372681938620
## projectmayavi:author_groupnonmember:typeissue_reply                     0.116671
## projectnumpy:author_groupnonmember:typeissue_reply                      0.076284
## projectpandas:author_groupnonmember:typeissue_reply                     0.496969
## projectscikit-image:author_groupnonmember:typeissue_reply               0.000900
## projectscikit-learn:author_groupnonmember:typeissue_reply   < 0.0000000000000002
## projectscipy:author_groupnonmember:typeissue_reply                      0.455077
## projectsphinx-gallery:author_groupnonmember:typeissue_reply             0.585538
## projectmayavi:author_groupnonmember:typepr_post                         0.243718
## projectnumpy:author_groupnonmember:typepr_post              0.000022215720805029
## projectpandas:author_groupnonmember:typepr_post             0.000000015017263736
## projectscikit-image:author_groupnonmember:typepr_post                   0.091061
## projectscikit-learn:author_groupnonmember:typepr_post       < 0.0000000000000002
## projectscipy:author_groupnonmember:typepr_post                          0.000168
## projectsphinx-gallery:author_groupnonmember:typepr_post                 0.482441
## projectmayavi:author_groupnonmember:typepr_reply                        0.004510
## projectnumpy:author_groupnonmember:typepr_reply                         0.108297
## projectpandas:author_groupnonmember:typepr_reply                        0.015357
## projectscikit-image:author_groupnonmember:typepr_reply      0.000001137287428452
## projectscikit-learn:author_groupnonmember:typepr_reply      < 0.0000000000000002
## projectscipy:author_groupnonmember:typepr_reply                         0.000841
## projectsphinx-gallery:author_groupnonmember:typepr_reply                0.011982
##                                                                
## (Intercept)                                                 ***
## projectmayavi                                                  
## projectnumpy                                                .  
## projectpandas                                               ***
## projectscikit-image                                         ***
## projectscikit-learn                                         .  
## projectscipy                                                   
## projectsphinx-gallery                                          
## author_groupnonmember                                       ** 
## typeissue_reply                                             ***
## typepr_post                                                 ***
## typepr_reply                                                ***
## projectmayavi:author_groupnonmember                         *  
## projectnumpy:author_groupnonmember                             
## projectpandas:author_groupnonmember                            
## projectscikit-image:author_groupnonmember                   ***
## projectscikit-learn:author_groupnonmember                   ***
## projectscipy:author_groupnonmember                          *  
## projectsphinx-gallery:author_groupnonmember                 .  
## projectmayavi:typeissue_reply                                  
## projectnumpy:typeissue_reply                                   
## projectpandas:typeissue_reply                                  
## projectscikit-image:typeissue_reply                         ** 
## projectscikit-learn:typeissue_reply                            
## projectscipy:typeissue_reply                                   
## projectsphinx-gallery:typeissue_reply                          
## projectmayavi:typepr_post                                   ***
## projectnumpy:typepr_post                                    ***
## projectpandas:typepr_post                                   ***
## projectscikit-image:typepr_post                             ***
## projectscikit-learn:typepr_post                             ***
## projectscipy:typepr_post                                    ***
## projectsphinx-gallery:typepr_post                           ***
## projectmayavi:typepr_reply                                  ***
## projectnumpy:typepr_reply                                   ** 
## projectpandas:typepr_reply                                  ***
## projectscikit-image:typepr_reply                            ***
## projectscikit-learn:typepr_reply                            ***
## projectscipy:typepr_reply                                   ***
## projectsphinx-gallery:typepr_reply                             
## author_groupnonmember:typeissue_reply                       ***
## author_groupnonmember:typepr_post                           ***
## author_groupnonmember:typepr_reply                          ***
## projectmayavi:author_groupnonmember:typeissue_reply            
## projectnumpy:author_groupnonmember:typeissue_reply          .  
## projectpandas:author_groupnonmember:typeissue_reply            
## projectscikit-image:author_groupnonmember:typeissue_reply   ***
## projectscikit-learn:author_groupnonmember:typeissue_reply   ***
## projectscipy:author_groupnonmember:typeissue_reply             
## projectsphinx-gallery:author_groupnonmember:typeissue_reply    
## projectmayavi:author_groupnonmember:typepr_post                
## projectnumpy:author_groupnonmember:typepr_post              ***
## projectpandas:author_groupnonmember:typepr_post             ***
## projectscikit-image:author_groupnonmember:typepr_post       .  
## projectscikit-learn:author_groupnonmember:typepr_post       ***
## projectscipy:author_groupnonmember:typepr_post              ***
## projectsphinx-gallery:author_groupnonmember:typepr_post        
## projectmayavi:author_groupnonmember:typepr_reply            ** 
## projectnumpy:author_groupnonmember:typepr_reply                
## projectpandas:author_groupnonmember:typepr_reply            *  
## projectscikit-image:author_groupnonmember:typepr_reply      ***
## projectscikit-learn:author_groupnonmember:typepr_reply      ***
## projectscipy:author_groupnonmember:typepr_reply             ***
## projectsphinx-gallery:author_groupnonmember:typepr_reply    *  
## ---
## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
```

```
## 
## Correlation matrix not shown by default, as p = 64 > 12.
## Use print(x, correlation=TRUE)  or
##     vcov(x)        if you need it
```


```r
anova_results = anova(creators_v_commenters_gratitude_by_project)
pander(anova_results)
```


-----------------------------------------------------------------------------
            &nbsp;               Sum Sq   Mean Sq   NumDF   DenDF    F value 
------------------------------- -------- --------- ------- -------- ---------
          **project**            31.03     4.432      7     281719    92.68  

       **author_group**          1.338     1.338      1     439600    27.98  

           **type**              39.71     13.24      3     474872    276.8  

   **project:author_group**      17.92     2.56       7     409126    53.53  

       **project:type**          152.9     7.282     21     453316    152.3  

     **author_group:type**       7.252     2.417      3     475062    50.55  

 **project:author_group:type**   66.03     3.144     21     453993    65.75  
-----------------------------------------------------------------------------

Table: Type III Analysis of Variance Table with Satterthwaite's method (continued below)

 
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            &nbsp;                                                                                                                                                          Pr(>F)                                                                                                                                            
------------------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
          **project**                                                                                    0.000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001103                                                                         

       **author_group**                                                                                                                                                  0.0000001228                                                                                                                                         

           **type**                                                                0.00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001627                                                   

   **project:author_group**                                                                                                           0.0000000000000000000000000000000000000000000000000000000000000000000000000000683                                                                                                       

       **project:type**                                                                                                                                                       0                                                                                                                                               

     **author_group:type**                                                                                                                                  0.00000000000000000000000000000001178                                                                                                                             

 **project:author_group:type**   0.000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003567 
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



![**Figure**. Expressions of gratitude by contribution type (issue vs. comment) and community membership (member vs. nonmember) at the time of posting.](../../figures/sentiment_analysis/ossc-grateful_membership_contribution-knitr.jpg)

### Model 2.4: Do issues and comments materially differ in gratitude over time?

**Note**: Having difficulty getting this to converge.


```r
library(splines)
# do users tend to express appreciation and gratitude differently by group and content?
<<<<<<< HEAD
creators_v_commenters_gratitude_time = glmer(grateful_count ~ (author_group + type) * ns(date) +
                                               (1 | project),
                                             data=sentiment_frame,
                                             family=poisson)
=======
creators_v_commenters_gratitude_time = lmer(log(grateful_count + 1) ~ project + (author_group + type) * ns(date, df=8) +
                                               (1 | author_name),
                                             data=sentiment_frame)
                                             #family=poisson)
>>>>>>> d5ab35a... Got the damn p-value at last

# print results
summary(creators_v_commenters_gratitude_time)
```

```
## Generalized linear mixed model fit by maximum likelihood (Laplace
##   Approximation) [glmerMod]
##  Family: poisson  ( log )
## Formula: grateful_count ~ (author_group + type) * ns(date) + (1 | project)
##    Data: sentiment_frame
## 
##       AIC       BIC    logLik  deviance  df.resid 
##  362043.9  362121.4 -181015.0  362029.9    471260 
## 
## Scaled residuals: 
##     Min      1Q  Median      3Q     Max 
## -0.5983 -0.3740 -0.3327 -0.3052 22.7266 
## 
## Random effects:
##  Groups  Name        Variance Std.Dev.
##  project (Intercept) 0.05404  0.2325  
## Number of obs: 471267, groups:  project, 8
## 
## Fixed effects:
##                                Estimate Std. Error z value
## (Intercept)                    -2.35710    0.08183 -28.805
## author_groupnonmember           0.85114    0.03180  26.764
## typeissue                      -1.74778    0.04963 -35.218
## ns(date)                        0.47092    0.02562  18.378
## author_groupnonmember:ns(date) -0.48119    0.05494  -8.758
## typeissue:ns(date)              2.42027    0.08130  29.769
##                                           Pr(>|z|)    
## (Intercept)                    <0.0000000000000002 ***
## author_groupnonmember          <0.0000000000000002 ***
## typeissue                      <0.0000000000000002 ***
## ns(date)                       <0.0000000000000002 ***
## author_groupnonmember:ns(date) <0.0000000000000002 ***
## typeissue:ns(date)             <0.0000000000000002 ***
## ---
## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
## 
## Correlation of Fixed Effects:
##             (Intr) athr_g typess ns(dt) at_:()
## athr_grpnnm -0.059                            
## typeissue   -0.040 -0.136                     
## ns(date)    -0.158  0.365  0.172              
## athr_grp:()  0.058 -0.948  0.125 -0.408       
## typss:ns(d)  0.042  0.134 -0.960 -0.204 -0.137
```


```r
anova_results = anova(creators_v_commenters_gratitude_time)
pander(anova_results)
```



```
## `geom_smooth()` using method = 'gam' and formula 'y ~ s(x, bs = "cs")'
## `geom_smooth()` using method = 'gam' and formula 'y ~ s(x, bs = "cs")'
## `geom_smooth()` using method = 'gam' and formula 'y ~ s(x, bs = "cs")'
## `geom_smooth()` using method = 'gam' and formula 'y ~ s(x, bs = "cs")'
## `geom_smooth()` using method = 'gam' and formula 'y ~ s(x, bs = "cs")'
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
##  72926.3  72989.6 -36456.2  72912.3    62297 
## 
## Scaled residuals: 
##     Min      1Q  Median      3Q     Max 
## -1.5076 -0.6369 -0.5652  1.3507  2.6214 
## 
## Random effects:
##  Groups  Name                   Variance Std.Dev. Corr 
##  project (Intercept)            0.12799  0.3578        
##          grateful_count_comment 0.01585  0.1259   -0.68
## Number of obs: 62304, groups:  project, 8
## 
## Fixed effects:
##                         Estimate Std. Error z value             Pr(>|z|)
## (Intercept)            -0.927967   0.128094  -7.244 0.000000000000434370
## compound_emotion        0.073806   0.009065   8.142 0.000000000000000389
## grateful_count_comment  0.146308   0.047493   3.081              0.00207
## open_time               0.101775   0.008719  11.673 < 0.0000000000000002
##                           
## (Intercept)            ***
## compound_emotion       ***
## grateful_count_comment ** 
## open_time              ***
## ---
## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
## 
## Correlation of Fixed Effects:
##             (Intr) cmpnd_ grtf__
## compond_mtn -0.001              
## grtfl_cnt_c -0.642 -0.003       
## open_time   -0.005 -0.053  0.035
```

**Note**. Need to fix this. Not really sure how best to demonstrate this given the limits of the linear fit...



![**Figure**. Whether a first-time issue creator will open a second issue by commenters' expressions of gratitude and responsiveness.](../../figures/sentiment_analysis/ossc-retention_emotion-knitr.jpg)
