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

* `../../data/analysis_data/sentiment_frame_tickets-for_r.csv`: Contains cleaned
  **tickets**-related data and derived variables from scraped GitHub data.
* `../../data/analysis_data/sentiment_frame_comments-for_r.csv`: Contains
  cleaned **comments**-related data and derived variables from scraped GitHub
  data.
* `./utils/ossc-libraries_and_functions.r`: Loads in necessary libraries and
  creates new functions for our analyses.

**Code written by**: A. Paxton (University of Connecticut) & N. Varoquaux
(University of California, Berkeley)

**Date last modified**: 30 May 2019



***

# Preliminaries


```r
library(splines)
library(lmerTest)
# clear everything
rm(list=ls())

# load libraries and add new functions
source('./utils/ossc-libraries_and_functions.r')

# load data
tickets_frame = read.table('../../data/analysis_data/dataset_upto2019/sentiment_frame_tickets-for_r.csv',
                          sep = ',', header=TRUE, fill=TRUE, stringsAsFactors = FALSE)
comments_frame = read.table('../../data/analysis_data/dataset_upto2019/sentiment_frame_comments-for_r.csv',
                            sep = ',', header=TRUE, fill=TRUE, stringsAsFactors = FALSE)

ticket_frame_preserve = tickets_frame
tickets_frame = ticket_frame_preserve
comment_frame_preserve = comments_frame
comments_frame = comment_frame_preserve
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





Our dataset includes 8 unique projects with a
total of 69674 unique tickets, with a
mean of 8709.25 tickets per project.

On these tickets, the dataset includes
411180 unique comments, with
5.13975\times 10^{4} average comments per project.

In total, we have 14338 unique commenters,
14232 unique ticket-creators, and
18346 overall unique users.

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
a posted ticket, or a reply to an ticket).


```r
pander_clean_anova = function(model){
    # First, rename the functions into something sane.
    colnames(model) = c("sum_sq", "mean_sq", "num_df", "den_df",
			"f_value", "p_value")
    
    # Adjust p-values
    model$p_adj = stats::p.adjust(model$p_value, method="BH")

    # Now, apply the same rounding on the p_value than on the rest
    model$p_value[model$p_value < .0001] = .0001
    model$p_value[model$p_value >= .0001] = round(model$p_value[model$p_value >= .0001],4)
    model$p_value[model$p_value >= .0005] = round(model$p_value[model$p_value >= .0005],3)
    model$p_value[model$p_value >= .25] = round(model$p_value[model$p_value >= .25],2)

    model$p_adj[model$p_adj < .0001] = .0001
    model$p_adj[model$p_adj >= .0001] = round(model$p_adj[model$p_adj >= .0001],4)
    model$p_adj[model$p_adj >= .0005] = round(model$p_adj[model$p_adj >= .0005],3)
    model$p_adj[model$p_adj >= .25] = round(model$p_adj[model$p_adj >= .25],2)

    model$sig = ' '
    model$sig[model$p_adj < .1] = '.'
    model$sig[model$p_adj < .05] = '*'
    model$sig[model$p_adj < .01] = '**'
    model$sig[model$p_adj < .001] = '***'
    return(pander(model, , split.table = Inf, style = 'rmarkdown'))
}
```


```r
# do tickets and comments materially differ in emotion?
creators_v_commenters_emotion_by_project = lmer(compound_emotion ~ project * type * author_group  +
                                               (1 | author_name),
                                                data = sentiment_frame,
                                                REML = TRUE)

# print results
pander_lme(creators_v_commenters_emotion_by_project)
```



|                             &nbsp;                              | Estimate  | Std..Error |   df   | t.value  |             Pr...t..              |   p    | p_adj | sig |
|:---------------------------------------------------------------:|:---------:|:----------:|:------:|:--------:|:---------------------------------:|:------:|:-----:|:---:|
|                         **(Intercept)**                         |  0.07089  |  0.01113   | 386052 |  6.367   |          0.0000000001931          | 0.0001 | 0.001 | **  |
|                        **projectmayavi**                        |  -0.1005  |  0.05509   | 242947 |  -1.824  |              0.06815              | 0.068  | 0.242 |     |
|                        **projectnumpy**                         | -0.04567  |  0.01464   | 480759 |  -3.118  |             0.001818              | 0.002  | 0.013 |  *  |
|                        **projectpandas**                        |  0.02742  |   0.0125   | 455331 |  2.193   |              0.02829              | 0.028  | 0.149 |     |
|                     **projectscikit-image**                     |  -0.0364  |  0.02161   | 480596 |  -1.685  |              0.09204              | 0.092  | 0.28  |     |
|                     **projectscikit-learn**                     | 0.007051  |  0.01447   | 474488 |  0.4874  |               0.626               |  0.63  |  0.8  |     |
|                        **projectscipy**                         | -0.03442  |  0.01769   | 479607 |  -1.945  |              0.05172              | 0.052  | 0.208 |     |
|                    **projectsphinx-gallery**                    |  0.0279   |  0.04352   | 469126 |  0.641   |              0.5215               |  0.52  | 0.74  |     |
|                       **typeissue_reply**                       |  0.08873  |  0.01053   | 471897 |  8.428   |      0.00000000000000003523       | 0.0001 | 0.001 | **  |
|                         **typepr_post**                         | 0.005664  |  0.01155   | 472665 |  0.4904  |              0.6238               |  0.62  |  0.8  |     |
|                        **typepr_reply**                         |  0.1151   |  0.01039   | 472716 |  11.08   | 0.0000000000000000000000000001518 | 0.0001 | 0.001 | **  |
|                    **author_groupnonmember**                    | 0.009596  |  0.01334   | 425119 |  0.7192  |               0.472               |  0.47  | 0.73  |     |
|                **projectmayavi:typeissue_reply**                |  0.03514  |  0.05058   | 469782 |  0.6949  |              0.4871               |  0.49  | 0.74  |     |
|                **projectnumpy:typeissue_reply**                 |  0.02631  |  0.01438   | 469638 |   1.83   |              0.0672               | 0.067  | 0.242 |     |
|                **projectpandas:typeissue_reply**                |  -0.013   |  0.01183   | 471380 |  -1.099  |              0.2719               |  0.27  |  0.6  |     |
|             **projectscikit-image:typeissue_reply**             |  0.06535  |  0.02127   | 467002 |  3.073   |              0.00212              | 0.002  | 0.013 |  *  |
|             **projectscikit-learn:typeissue_reply**             | 0.003979  |  0.01387   | 469643 |  0.2869  |              0.7742               |  0.77  |  0.9  |     |
|                **projectscipy:typeissue_reply**                 |  0.0372   |  0.01768   | 468633 |  2.104   |              0.03536              | 0.035  | 0.166 |     |
|            **projectsphinx-gallery:typeissue_reply**            |  0.0479   |  0.04571   | 465939 |  1.048   |              0.2947               |  0.3   |  0.6  |     |
|                  **projectmayavi:typepr_post**                  | -0.001205 |  0.05573   | 467238 | -0.02163 |              0.9827               |  0.98  | 0.98  |     |
|                  **projectnumpy:typepr_post**                   |  0.02168  |  0.01634   | 469968 |  1.327   |              0.1845               | 0.184  | 0.45  |     |
|                  **projectpandas:typepr_post**                  | -0.04891  |  0.01355   | 472236 |  -3.61   |             0.0003066             | 0.0003 | 0.003 | **  |
|               **projectscikit-image:typepr_post**               |  0.06565  |   0.0236   | 467414 |  2.781   |             0.005413              | 0.005  | 0.029 |  *  |
|               **projectscikit-learn:typepr_post**               |  0.02251  |  0.01605   | 470103 |  1.402   |               0.161               | 0.161  | 0.42  |     |
|                  **projectscipy:typepr_post**                   |  0.02186  |  0.01949   | 469002 |  1.121   |              0.2622               |  0.26  | 0.59  |     |
|              **projectsphinx-gallery:typepr_post**              | -0.001664 |  0.05411   | 466088 | -0.03075 |              0.9755               |  0.98  | 0.98  |     |
|                 **projectmayavi:typepr_reply**                  |  0.01376  |  0.05147   | 468340 |  0.2674  |              0.7892               |  0.79  |  0.9  |     |
|                  **projectnumpy:typepr_reply**                  |  0.07953  |  0.01434   | 470436 |  5.546   |           0.0000000292            | 0.0001 | 0.001 | **  |
|                 **projectpandas:typepr_reply**                  | -0.00892  |  0.01172   | 472464 |  -0.761  |              0.4467               |  0.45  | 0.72  |     |
|              **projectscikit-image:typepr_reply**               |  0.09626  |  0.02071   | 467522 |  4.648   |            0.000003347            | 0.0001 | 0.001 | **  |
|              **projectscikit-learn:typepr_reply**               |  0.02819  |  0.01365   | 470463 |  2.065   |              0.03893              | 0.039  | 0.166 |     |
|                  **projectscipy:typepr_reply**                  |  0.08589  |  0.01742   | 469241 |  4.932   |           0.0000008159            | 0.0001 | 0.001 | **  |
|             **projectsphinx-gallery:typepr_reply**              | 0.007502  |   0.0444   | 466301 |  0.169   |              0.8658               |  0.87  | 0.92  |     |
|             **projectmayavi:author_groupnonmember**             |  0.0824   |  0.05935   | 283576 |  1.388   |              0.1651               | 0.165  | 0.42  |     |
|             **projectnumpy:author_groupnonmember**              | -0.007749 |  0.01846   | 453311 | -0.4198  |              0.6746               |  0.68  | 0.84  |     |
|             **projectpandas:author_groupnonmember**             | -0.003987 |  0.01549   | 426160 | -0.2574  |              0.7969               |  0.8   |  0.9  |     |
|          **projectscikit-image:author_groupnonmember**          |  0.01797  |  0.02843   | 439870 |  0.6319  |              0.5274               |  0.53  | 0.74  |     |
|          **projectscikit-learn:author_groupnonmember**          |  0.01242  |  0.01821   | 436132 |  0.6822  |              0.4951               |  0.5   | 0.74  |     |
|             **projectscipy:author_groupnonmember**              |  0.03609  |   0.0213   | 463550 |  1.694   |              0.09022              |  0.09  | 0.28  |     |
|         **projectsphinx-gallery:author_groupnonmember**         | -0.07006  |  0.06099   | 479730 |  -1.149  |              0.2507               |  0.25  | 0.59  |     |
|            **typeissue_reply:author_groupnonmember**            |  0.01216  |  0.01396   | 478077 |  0.8709  |              0.3838               |  0.38  | 0.66  |     |
|              **typepr_post:author_groupnonmember**              | 0.003154  |  0.01723   | 442991 |  0.183   |              0.8548               |  0.86  | 0.92  |     |
|             **typepr_reply:author_groupnonmember**              | 0.006907  |  0.01486   | 388230 |  0.465   |               0.642               |  0.64  |  0.8  |     |
|     **projectmayavi:typeissue_reply:author_groupnonmember**     | -0.05219  |  0.05804   | 480786 | -0.8991  |              0.3686               |  0.37  | 0.66  |     |
|     **projectnumpy:typeissue_reply:author_groupnonmember**      |  0.01195  |  0.01975   | 476408 |  0.6052  |              0.5451               |  0.55  | 0.75  |     |
|     **projectpandas:typeissue_reply:author_groupnonmember**     |  0.01674  |  0.01632   | 475469 |  1.025   |              0.3052               |  0.3   |  0.6  |     |
|  **projectscikit-image:typeissue_reply:author_groupnonmember**  | -0.02423  |  0.03049   | 475821 | -0.7948  |              0.4267               |  0.43  | 0.71  |     |
|  **projectscikit-learn:typeissue_reply:author_groupnonmember**  | -0.007259 |  0.01906   | 473482 | -0.3809  |              0.7033               |  0.7   | 0.84  |     |
|     **projectscipy:typeissue_reply:author_groupnonmember**      | -0.007065 |  0.02278   | 479661 | -0.3101  |              0.7565               |  0.76  |  0.9  |     |
| **projectsphinx-gallery:typeissue_reply:author_groupnonmember** |  0.0743   |  0.06848   | 477400 |  1.085   |              0.2779               |  0.28  |  0.6  |     |
|       **projectmayavi:typepr_post:author_groupnonmember**       | -0.06741  |  0.07658   | 464644 | -0.8803  |              0.3787               |  0.38  | 0.66  |     |
|       **projectnumpy:typepr_post:author_groupnonmember**        | 0.003659  |  0.02474   | 453173 |  0.1479  |              0.8824               |  0.88  | 0.92  |     |
|       **projectpandas:typepr_post:author_groupnonmember**       |  0.03598  |  0.02087   | 438135 |  1.724   |              0.08467              | 0.085  | 0.28  |     |
|    **projectscikit-image:typepr_post:author_groupnonmember**    |  0.1158   |   0.0358   | 454296 |  3.235   |             0.001218              | 0.001  | 0.008 | **  |
|    **projectscikit-learn:typepr_post:author_groupnonmember**    | -0.01997  |  0.02347   | 449115 |  -0.851  |              0.3948               |  0.4   | 0.67  |     |
|       **projectscipy:typepr_post:author_groupnonmember**        |  0.00405  |  0.02729   | 462796 |  0.1484  |               0.882               |  0.88  | 0.92  |     |
|   **projectsphinx-gallery:typepr_post:author_groupnonmember**   |  0.1462   |  0.08924   | 480476 |  1.638   |              0.1014               | 0.101  | 0.29  |     |
|      **projectmayavi:typepr_reply:author_groupnonmember**       | 0.002329  |  0.06693   | 432207 | 0.03479  |              0.9722               |  0.97  | 0.98  |     |
|       **projectnumpy:typepr_reply:author_groupnonmember**       | -0.01844  |  0.02094   | 408317 | -0.8806  |              0.3785               |  0.38  | 0.66  |     |
|      **projectpandas:typepr_reply:author_groupnonmember**       | -0.03658  |  0.01754   | 370918 |  -2.085  |              0.03705              | 0.037  | 0.166 |     |
|   **projectscikit-image:typepr_reply:author_groupnonmember**    | -0.01904  |  0.03037   | 421270 | -0.6267  |              0.5308               |  0.53  | 0.74  |     |
|   **projectscikit-learn:typepr_reply:author_groupnonmember**    | -0.01984  |  0.01977   | 396180 |  -1.003  |              0.3157               |  0.32  | 0.62  |     |
|       **projectscipy:typepr_reply:author_groupnonmember**       | -0.03658  |  0.02339   | 434878 |  -1.564  |              0.1178               | 0.118  | 0.33  |     |
|  **projectsphinx-gallery:typepr_reply:author_groupnonmember**   |  0.03611  |  0.06777   | 480513 |  0.5329  |              0.5941               |  0.59  | 0.79  |     |


```r
anova_results = anova(creators_v_commenters_emotion_by_project)
pander_clean_anova(anova_results)
```



|            &nbsp;             | sum_sq | mean_sq | num_df | den_df | f_value | p_value | p_adj | sig |
|:-----------------------------:|:------:|:-------:|:------:|:------:|:-------:|:-------:|:-----:|:---:|
|          **project**          | 22.68  |  3.24   |   7    | 111756 |  19.15  |  1e-04  | 1e-04 | *** |
|           **type**            | 131.1  |  43.68  |   3    | 433922 |  258.2  |  1e-04  | 1e-04 | *** |
|       **author_group**        | 3.668  |  3.668  |   1    | 152171 |  21.68  |  1e-04  | 1e-04 | *** |
|       **project:type**        | 54.81  |  2.61   |   21   | 388447 |  15.43  |  1e-04  | 1e-04 | *** |
|   **project:author_group**    |  4.75  | 0.6785  |   7    | 226240 |  4.01   |  2e-04  | 2e-04 | *** |
|     **type:author_group**     | 1.594  | 0.5314  |   3    | 435688 |  3.14   |  0.024  | 0.024 |  *  |
| **project:type:author_group** | 13.69  | 0.6519  |   21   | 392239 |  3.853  |  1e-04  | 1e-04 | *** |

Table: Type III Analysis of Variance Table with Satterthwaite's method


These results are quite different from our results conducted over a smaller
dataset last year. One potential reason is that these effects may be
time-dependent. Our next model explores this possibility by adding a time term.



![**Figure**. Sentiment by contribution type (ticket vs. comment) and community membership at the time of posting (member vs. nonmember).](../../figures/sentiment_analysis/ossc-sentiment_membership_contribution-aggregated-knitr.jpg)



![**Figure**. Sentiment by contribution type (ticket vs. comment) and community membership at the time of posting (member vs. nonmember) for each project.](../../figures/sentiment_analysis/ossc-sentiment_membership_contribution-by_project-knitr.jpg)

### Model 1.2: Do tickets and comments materially differ in emotion over time?



```r
# do tickets and comments materially differ in emotion over time?
creators_v_commenters_emotion_by_project_time = lmer(compound_emotion ~ project * type * author_group * ns(date) +
                                                       (1 | author_name),
                                                     data = sentiment_frame,
                                                     REML=FALSE)
# print results
pander_lme(creators_v_commenters_emotion_by_project_time)
```



|                                  &nbsp;                                  | Estimate  | Std..Error |   df   | t.value  |   Pr...t..    |   p    | p_adj | sig |
|:------------------------------------------------------------------------:|:---------:|:----------:|:------:|:--------:|:-------------:|:------:|:-----:|:---:|
|                             **(Intercept)**                              |  0.04315  |  0.02876   | 459512 |   1.5    |    0.1335     | 0.134  | 0.42  |     |
|                            **projectmayavi**                             |  0.1724   |   0.2916   | 480627 |  0.5912  |    0.5544     |  0.55  |  0.8  |     |
|                             **projectnumpy**                             | -0.04867  |  0.03712   | 480633 |  -1.311  |    0.1897     |  0.19  | 0.47  |     |
|                            **projectpandas**                             | -0.01265  |  0.03131   | 472572 | -0.4041  |    0.6861     |  0.69  | 0.88  |     |
|                         **projectscikit-image**                          |  -0.1693  |  0.06208   | 475812 |  -2.727  |   0.006393    | 0.006  | 0.115 |     |
|                         **projectscikit-learn**                          |  0.01441  |  0.03592   | 479425 |  0.4011  |    0.6883     |  0.69  | 0.88  |     |
|                             **projectscipy**                             | -0.01242  |  0.05465   | 477094 | -0.2273  |    0.8202     |  0.82  | 0.96  |     |
|                        **projectsphinx-gallery**                         |  -0.5694  |   0.2594   | 469092 |  -2.195  |    0.02817    | 0.028  | 0.143 |     |
|                           **typeissue_reply**                            |  0.07708  |  0.02941   | 480545 |  2.621   |   0.008771    | 0.009  | 0.115 |     |
|                             **typepr_post**                              |  0.02581  |  0.03201   | 480848 |  0.8063  |     0.42      |  0.42  | 0.74  |     |
|                             **typepr_reply**                             |  0.1678   |  0.02872   | 480269 |  5.844   | 0.00000000511 | 0.0001 | 0.013 |  *  |
|                        **author_groupnonmember**                         |  0.0658   |  0.03609   | 433096 |  1.823   |    0.06829    | 0.068  | 0.26  |     |
|                               **ns(date)**                               |  0.06329  |  0.05344   | 479660 |  1.184   |    0.2363     | 0.236  | 0.53  |     |
|                    **projectmayavi:typeissue_reply**                     |  -0.1089  |   0.2985   | 471005 | -0.3648  |    0.7152     |  0.72  | 0.89  |     |
|                     **projectnumpy:typeissue_reply**                     |  0.0593   |  0.03728   | 479544 |  1.591   |    0.1116     | 0.112  | 0.38  |     |
|                    **projectpandas:typeissue_reply**                     |  0.03555  |  0.03194   | 480850 |  1.113   |    0.2657     |  0.27  | 0.59  |     |
|                 **projectscikit-image:typeissue_reply**                  |  0.1581   |  0.06486   | 471361 |  2.437   |    0.01482    | 0.015  | 0.128 |     |
|                 **projectscikit-learn:typeissue_reply**                  |  0.04959  |  0.03682   | 479703 |  1.347   |     0.178     | 0.178  | 0.46  |     |
|                     **projectscipy:typeissue_reply**                     |  0.04297  |  0.05642   | 473488 |  0.7617  |    0.4462     |  0.45  | 0.74  |     |
|                **projectsphinx-gallery:typeissue_reply**                 |  0.4097   |   0.2799   | 467197 |  1.464   |    0.1433     | 0.143  | 0.44  |     |
|                      **projectmayavi:typepr_post**                       |  -0.2157  |   0.3131   | 469377 | -0.6889  |    0.4909     |  0.49  | 0.74  |     |
|                       **projectnumpy:typepr_post**                       |  0.02013  |  0.04369   | 477873 |  0.4606  |    0.6451     |  0.64  | 0.85  |     |
|                      **projectpandas:typepr_post**                       | -0.004812 |  0.03697   | 480047 | -0.1301  |    0.8965     |  0.9   | 0.97  |     |
|                   **projectscikit-image:typepr_post**                    |  0.05893  |  0.06866   | 471444 |  0.8583  |    0.3907     |  0.39  | 0.72  |     |
|                   **projectscikit-learn:typepr_post**                    |  0.1429   |  0.04204   | 478042 |   3.4    |   0.0006735   | 0.001  | 0.032 |  *  |
|                       **projectscipy:typepr_post**                       |  0.03371  |  0.06074   | 472830 |  0.555   |    0.5789     |  0.58  | 0.81  |     |
|                  **projectsphinx-gallery:typepr_post**                   |  0.8985   |   0.336    | 466841 |  2.674   |   0.007491    | 0.008  | 0.115 |     |
|                      **projectmayavi:typepr_reply**                      |  -0.4095  |   0.3024   | 471029 |  -1.354  |    0.1757     | 0.176  | 0.46  |     |
|                      **projectnumpy:typepr_reply**                       |  0.05326  |  0.03763   | 479754 |  1.415   |     0.157     | 0.157  | 0.44  |     |
|                      **projectpandas:typepr_reply**                      | 0.001545  |  0.03147   | 480835 |  0.0491  |    0.9608     |  0.96  | 0.98  |     |
|                   **projectscikit-image:typepr_reply**                   |  0.2346   |  0.06252   | 471930 |  3.752   |   0.0001755   | 0.0002 | 0.013 |  *  |
|                   **projectscikit-learn:typepr_reply**                   |  0.06917  |   0.0359   | 480038 |  1.927   |    0.05403    | 0.054  | 0.21  |     |
|                      **projectscipy:typepr_reply**                       |  0.0698   |  0.05507   | 473986 |  1.267   |     0.205     | 0.205  | 0.49  |     |
|                  **projectsphinx-gallery:typepr_reply**                  |  0.6199   |   0.2709   | 467978 |  2.288   |    0.02213    | 0.022  | 0.139 |     |
|                 **projectmayavi:author_groupnonmember**                  |  -0.1961  |   0.2988   | 480842 | -0.6562  |    0.5117     |  0.51  | 0.75  |     |
|                  **projectnumpy:author_groupnonmember**                  |  -0.049   |  0.05087   | 444034 | -0.9633  |    0.3354     |  0.34  | 0.68  |     |
|                 **projectpandas:author_groupnonmember**                  | -0.04076  |  0.04108   | 425945 | -0.9922  |    0.3211     |  0.32  | 0.66  |     |
|              **projectscikit-image:author_groupnonmember**               |  0.09772  |  0.08526   | 460450 |  1.146   |    0.2517     |  0.25  | 0.55  |     |
|              **projectscikit-learn:author_groupnonmember**               |  -0.1075  |  0.04832   | 430315 |  -2.225  |    0.02611    | 0.026  | 0.139 |     |
|                  **projectscipy:author_groupnonmember**                  | -0.05314  |  0.06835   | 462156 | -0.7774  |    0.4369     |  0.44  | 0.74  |     |
|             **projectsphinx-gallery:author_groupnonmember**              |  0.8204   |   0.3554   | 480040 |  2.308   |    0.02099    | 0.021  | 0.139 |     |
|                **typeissue_reply:author_groupnonmember**                 | -0.007276 |   0.0399   | 471111 | -0.1824  |    0.8553     |  0.86  | 0.96  |     |
|                  **typepr_post:author_groupnonmember**                   | -0.03325  |   0.0461   | 453248 | -0.7212  |    0.4708     |  0.47  | 0.74  |     |
|                  **typepr_reply:author_groupnonmember**                  | 0.003994  |  0.04086   | 408948 | 0.09775  |    0.9221     |  0.92  | 0.97  |     |
|                        **projectmayavi:ns(date)**                        |  -0.5276  |   0.5378   | 473860 | -0.9811  |    0.3266     |  0.33  | 0.67  |     |
|                        **projectnumpy:ns(date)**                         | 0.006793  |  0.07056   | 480199 | 0.09627  |    0.9233     |  0.92  | 0.97  |     |
|                        **projectpandas:ns(date)**                        |  0.09059  |  0.05892   | 480553 |  1.538   |    0.1241     | 0.124  | 0.41  |     |
|                     **projectscikit-image:ns(date)**                     |  0.2476   |   0.1152   | 472853 |   2.15   |    0.03159    | 0.032  | 0.152 |     |
|                     **projectscikit-learn:ns(date)**                     | -0.009025 |  0.06779   | 480340 | -0.1331  |    0.8941     |  0.89  | 0.97  |     |
|                        **projectscipy:ns(date)**                         | -0.04754  |   0.1028   | 474803 | -0.4623  |    0.6438     |  0.64  | 0.85  |     |
|                    **projectsphinx-gallery:ns(date)**                    |  0.9402   |   0.4123   | 468330 |  2.281   |    0.02258    | 0.023  | 0.139 |     |
|                       **typeissue_reply:ns(date)**                       |  0.01874  |  0.05516   | 480846 |  0.3398  |     0.734     |  0.73  | 0.89  |     |
|                         **typepr_post:ns(date)**                         | -0.04194  |  0.05943   | 480604 | -0.7057  |    0.4804     |  0.48  | 0.74  |     |
|                        **typepr_reply:ns(date)**                         |  -0.1058  |  0.05402   | 480850 |  -1.958  |    0.05023    |  0.05  |  0.2  |     |
|                    **author_groupnonmember:ns(date)**                    |  -0.1182  |  0.06726   | 432559 |  -1.758  |    0.07878    | 0.079  | 0.28  |     |
|         **projectmayavi:typeissue_reply:author_groupnonmember**          | 0.008279  |   0.3089   | 474639 |  0.0268  |    0.9786     |  0.98  | 0.98  |     |
|          **projectnumpy:typeissue_reply:author_groupnonmember**          |  0.01709  |  0.05648   | 471737 |  0.3026  |    0.7622     |  0.76  | 0.91  |     |
|         **projectpandas:typeissue_reply:author_groupnonmember**          |  0.1162   |   0.0458   | 469817 |  2.536   |    0.0112     | 0.011  | 0.128 |     |
|      **projectscikit-image:typeissue_reply:author_groupnonmember**       |  -0.1229  |  0.09595   | 477949 |  -1.281  |    0.2003     |  0.2   | 0.48  |     |
|      **projectscikit-learn:typeissue_reply:author_groupnonmember**       |  0.0279   |  0.05343   | 469902 |  0.5222  |    0.6015     |  0.6   | 0.82  |     |
|          **projectscipy:typeissue_reply:author_groupnonmember**          |  0.0418   |  0.07528   | 478051 |  0.5553  |    0.5787     |  0.58  | 0.81  |     |
|     **projectsphinx-gallery:typeissue_reply:author_groupnonmember**      |  -0.7986  |   0.3999   | 476646 |  -1.997  |    0.04583    | 0.046  | 0.196 |     |
|           **projectmayavi:typepr_post:author_groupnonmember**            |  0.06773  |   0.3395   | 478916 |  0.1995  |    0.8419     |  0.84  | 0.96  |     |
|            **projectnumpy:typepr_post:author_groupnonmember**            |  0.06177  |  0.06629   | 462130 |  0.9319  |    0.3514     |  0.35  | 0.69  |     |
|           **projectpandas:typepr_post:author_groupnonmember**            | -0.003816 |  0.05765   | 449433 | -0.06619 |    0.9472     |  0.95  | 0.97  |     |
|        **projectscikit-image:typepr_post:author_groupnonmember**         | -0.06936  |   0.1016   | 470282 | -0.6826  |    0.4949     |  0.5   | 0.74  |     |
|        **projectscikit-learn:typepr_post:author_groupnonmember**         |  0.02235  |  0.06233   | 454230 |  0.3585  |     0.72      |  0.72  | 0.89  |     |
|            **projectscipy:typepr_post:author_groupnonmember**            |  0.06189  |   0.0821   | 468551 |  0.7539  |    0.4509     |  0.45  | 0.74  |     |
|       **projectsphinx-gallery:typepr_post:author_groupnonmember**        |   -1.08   |   0.5285   | 480795 |  -2.044  |    0.04097    | 0.041  | 0.187 |     |
|           **projectmayavi:typepr_reply:author_groupnonmember**           |  0.3885   |   0.3211   | 479831 |   1.21   |    0.2263     | 0.226  | 0.53  |     |
|           **projectnumpy:typepr_reply:author_groupnonmember**            | -0.004095 |  0.05731   | 428340 | -0.07146 |     0.943     |  0.94  | 0.97  |     |
|           **projectpandas:typepr_reply:author_groupnonmember**           |  0.08634  |  0.04877   | 384161 |   1.77   |    0.07668    | 0.077  | 0.28  |     |
|        **projectscikit-image:typepr_reply:author_groupnonmember**        |  -0.2395  |  0.09116   | 452514 |  -2.628  |   0.008599    | 0.009  | 0.115 |     |
|        **projectscikit-learn:typepr_reply:author_groupnonmember**        |  0.01482  |  0.05356   | 410963 |  0.2767  |     0.782     |  0.78  | 0.92  |     |
|           **projectscipy:typepr_reply:author_groupnonmember**            | -0.01268  |   0.0733   | 451249 |  -0.173  |    0.8627     |  0.86  | 0.96  |     |
|       **projectsphinx-gallery:typepr_reply:author_groupnonmember**       |  -0.909   |   0.395    | 480830 |  -2.301  |    0.02136    | 0.021  | 0.139 |     |
|                **projectmayavi:typeissue_reply:ns(date)**                |  0.2876   |   0.5525   | 470735 |  0.5205  |    0.6027     |  0.6   | 0.82  |     |
|                **projectnumpy:typeissue_reply:ns(date)**                 | -0.06634  |  0.07184   | 478310 | -0.9234  |    0.3558     |  0.36  | 0.69  |     |
|                **projectpandas:typeissue_reply:ns(date)**                |  -0.1045  |  0.06079   | 480392 |  -1.719  |    0.0856     | 0.086  |  0.3  |     |
|             **projectscikit-image:typeissue_reply:ns(date)**             |  -0.1799  |   0.1208   | 470572 |  -1.49   |    0.1363     | 0.136  | 0.42  |     |
|             **projectscikit-learn:typeissue_reply:ns(date)**             | -0.09343  |  0.07019   | 478434 |  -1.331  |    0.1831     | 0.183  | 0.46  |     |
|                **projectscipy:typeissue_reply:ns(date)**                 | -0.007258 |   0.1063   | 472543 | -0.06826 |    0.9456     |  0.95  | 0.97  |     |
|            **projectsphinx-gallery:typeissue_reply:ns(date)**            |  -0.5985  |   0.4433   | 466918 |  -1.35   |     0.177     | 0.177  | 0.46  |     |
|                  **projectmayavi:typepr_post:ns(date)**                  |  0.4103   |   0.5762   | 469243 |  0.7122  |    0.4764     |  0.48  | 0.74  |     |
|                  **projectnumpy:typepr_post:ns(date)**                   | 0.001638  |  0.08234   | 476887 | 0.01989  |    0.9841     |  0.98  | 0.98  |     |
|                  **projectpandas:typepr_post:ns(date)**                  | -0.09842  |  0.06902   | 479388 |  -1.426  |    0.1539     | 0.154  | 0.44  |     |
|               **projectscikit-image:typepr_post:ns(date)**               |  0.05089  |   0.1294   | 470548 |  0.3931  |    0.6942     |  0.69  | 0.88  |     |
|               **projectscikit-learn:typepr_post:ns(date)**               |  -0.2627  |  0.07993   | 476915 |  -3.287  |   0.001014    | 0.001  | 0.032 |  *  |
|                  **projectscipy:typepr_post:ns(date)**                   | -0.02116  |   0.1146   | 471967 | -0.1846  |    0.8535     |  0.85  | 0.96  |     |
|              **projectsphinx-gallery:typepr_post:ns(date)**              |  -1.436   |   0.5318   | 466570 |   -2.7   |   0.006929    | 0.007  | 0.115 |     |
|                 **projectmayavi:typepr_reply:ns(date)**                  |  0.7948   |   0.5629   | 470549 |  1.412   |    0.1579     | 0.158  | 0.44  |     |
|                  **projectnumpy:typepr_reply:ns(date)**                  |  0.05038  |  0.07202   | 478610 |  0.6995  |    0.4842     |  0.48  | 0.74  |     |
|                 **projectpandas:typepr_reply:ns(date)**                  | -0.03477  |  0.05986   | 480605 | -0.5809  |    0.5613     |  0.56  |  0.8  |     |
|              **projectscikit-image:typepr_reply:ns(date)**               |  -0.2782  |   0.1169   | 471061 |  -2.379  |    0.01734    | 0.017  | 0.136 |     |
|              **projectscikit-learn:typepr_reply:ns(date)**               | -0.09735  |  0.06865   | 478814 |  -1.418  |    0.1562     | 0.156  | 0.44  |     |
|                  **projectscipy:typepr_reply:ns(date)**                  |  0.03256  |   0.1042   | 473018 |  0.3126  |    0.7546     |  0.76  | 0.91  |     |
|             **projectsphinx-gallery:typepr_reply:ns(date)**              |  -0.9627  |   0.4297   | 467596 |  -2.241  |    0.02506    | 0.025  | 0.139 |     |
|             **projectmayavi:author_groupnonmember:ns(date)**             |  0.5428   |   0.5508   | 477696 |  0.9856  |    0.3243     |  0.32  | 0.66  |     |
|             **projectnumpy:author_groupnonmember:ns(date)**              |  0.0787   |  0.09443   | 442680 |  0.8334  |    0.4046     |  0.4   | 0.73  |     |
|             **projectpandas:author_groupnonmember:ns(date)**             |  0.06196  |  0.07701   | 423609 |  0.8047  |     0.421     |  0.42  | 0.74  |     |
|          **projectscikit-image:author_groupnonmember:ns(date)**          |  -0.1437  |   0.157    | 451158 | -0.9152  |    0.3601     |  0.36  | 0.69  |     |
|          **projectscikit-learn:author_groupnonmember:ns(date)**          |  0.2275   |  0.09044   | 429386 |  2.516   |    0.01188    | 0.012  | 0.128 |     |
|             **projectscipy:author_groupnonmember:ns(date)**              |  0.1732   |   0.1262   | 464023 |  1.373   |    0.1698     |  0.17  | 0.46  |     |
|         **projectsphinx-gallery:author_groupnonmember:ns(date)**         |  -1.424   |   0.5751   | 480699 |  -2.475  |    0.01331    | 0.013  | 0.128 |     |
|            **typeissue_reply:author_groupnonmember:ns(date)**            |  0.04182  |  0.07398   | 470589 |  0.5654  |    0.5718     |  0.57  | 0.81  |     |
|              **typepr_post:author_groupnonmember:ns(date)**              |  0.0692   |  0.08767   | 441364 |  0.7893  |    0.4299     |  0.43  | 0.74  |     |
|             **typepr_reply:author_groupnonmember:ns(date)**              | -0.01132  |  0.07792   | 381151 | -0.1452  |    0.8845     |  0.88  | 0.97  |     |
|     **projectmayavi:typeissue_reply:author_groupnonmember:ns(date)**     |  -0.1248  |   0.5706   | 474800 | -0.2187  |    0.8269     |  0.83  | 0.96  |     |
|     **projectnumpy:typeissue_reply:author_groupnonmember:ns(date)**      | -0.007668 |   0.1044   | 470483 | -0.07342 |    0.9415     |  0.94  | 0.97  |     |
|     **projectpandas:typeissue_reply:author_groupnonmember:ns(date)**     |  -0.184   |   0.0855   | 468291 |  -2.152  |    0.03143    | 0.031  | 0.152 |     |
|  **projectscikit-image:typeissue_reply:author_groupnonmember:ns(date)**  |  0.1891   |   0.1761   | 473403 |  1.074   |    0.2829     |  0.28  |  0.6  |     |
|  **projectscikit-learn:typeissue_reply:author_groupnonmember:ns(date)**  | -0.06928  |   0.0994   | 468411 |  -0.697  |    0.4858     |  0.49  | 0.74  |     |
|     **projectscipy:typeissue_reply:author_groupnonmember:ns(date)**      | -0.09579  |   0.1383   | 478074 | -0.6926  |    0.4886     |  0.49  | 0.74  |     |
| **projectsphinx-gallery:typeissue_reply:author_groupnonmember:ns(date)** |   1.442   |   0.6447   | 476754 |  2.236   |    0.02536    | 0.025  | 0.139 |     |
|       **projectmayavi:typepr_post:author_groupnonmember:ns(date)**       |  -0.2354  |   0.6312   | 480428 | -0.3729  |    0.7092     |  0.71  | 0.89  |     |
|       **projectnumpy:typepr_post:author_groupnonmember:ns(date)**        |  -0.1107  |   0.1254   | 451037 | -0.8827  |    0.3774     |  0.38  | 0.72  |     |
|       **projectpandas:typepr_post:author_groupnonmember:ns(date)**       |  0.08091  |   0.1073   | 437536 |  0.7541  |    0.4508     |  0.45  | 0.74  |     |
|    **projectscikit-image:typepr_post:author_groupnonmember:ns(date)**    |  0.3796   |   0.1918   | 461050 |  1.979   |    0.04778    | 0.048  | 0.198 |     |
|    **projectscikit-learn:typepr_post:author_groupnonmember:ns(date)**    | -0.05411  |   0.1183   | 447007 | -0.4575  |    0.6473     |  0.65  | 0.86  |     |
|       **projectscipy:typepr_post:author_groupnonmember:ns(date)**        |  -0.1074  |   0.1545   | 465321 | -0.6952  |    0.4869     |  0.49  | 0.74  |     |
|   **projectsphinx-gallery:typepr_post:author_groupnonmember:ns(date)**   |   1.985   |   0.8521   | 480489 |  2.329   |    0.01985    |  0.02  | 0.139 |     |
|      **projectmayavi:typepr_reply:author_groupnonmember:ns(date)**       |  -0.7217  |   0.6086   | 480839 |  -1.186  |    0.2357     | 0.236  | 0.53  |     |
|       **projectnumpy:typepr_reply:author_groupnonmember:ns(date)**       | -0.01057  |   0.1087   | 400809 | -0.09721 |    0.9226     |  0.92  | 0.97  |     |
|      **projectpandas:typepr_reply:author_groupnonmember:ns(date)**       |  -0.1834  |  0.09178   | 365222 |  -1.998  |    0.04573    | 0.046  | 0.196 |     |
|   **projectscikit-image:typepr_reply:author_groupnonmember:ns(date)**    |  0.4647   |   0.1705   | 436313 |  2.725   |   0.006431    | 0.006  | 0.115 |     |
|   **projectscikit-learn:typepr_reply:author_groupnonmember:ns(date)**    |  -0.036   |   0.1018   | 393198 | -0.3535  |    0.7237     |  0.72  | 0.89  |     |
|       **projectscipy:typepr_reply:author_groupnonmember:ns(date)**       | -0.02605  |   0.1374   | 442645 | -0.1895  |    0.8497     |  0.85  | 0.96  |     |
|  **projectsphinx-gallery:typepr_reply:author_groupnonmember:ns(date)**   |   1.559   |   0.6433   | 480249 |  2.424   |    0.01537    | 0.015  | 0.128 |     |


```r
anova_results = anova(creators_v_commenters_emotion_by_project_time)
pander_clean_anova(anova_results)
```



|                 &nbsp;                 | sum_sq | mean_sq | num_df | den_df | f_value | p_value | p_adj | sig |
|:--------------------------------------:|:------:|:-------:|:------:|:------:|:-------:|:-------:|:-----:|:---:|
|              **project**               | 9.731  |  1.39   |   7    | 206076 |  8.227  |  1e-04  | 1e-04 | *** |
|                **type**                | 9.788  |  3.263  |   3    | 476066 |  19.31  |  1e-04  | 1e-04 | *** |
|            **author_group**            | 0.5728 | 0.5728  |   1    | 430759 |  3.39   |  0.066  | 0.089 |  .  |
|              **ns(date)**              | 0.2589 | 0.2589  |   1    | 387166 |  1.532  |  0.216  | 0.249 |     |
|            **project:type**            |  18.3  | 0.8712  |   21   | 422452 |  5.156  |  1e-04  | 1e-04 | *** |
|        **project:author_group**        | 6.638  | 0.9483  |   7    | 312861 |  5.612  |  1e-04  | 1e-04 | *** |
|         **type:author_group**          | 0.6321 | 0.2107  |   3    | 476218 |  1.247  |  0.29   | 0.31  |     |
|          **project:ns(date)**          | 11.29  |  1.613  |   7    | 230089 |  9.544  |  1e-04  | 1e-04 | *** |
|           **type:ns(date)**            | 2.403  |  0.801  |   3    | 470673 |  4.74   |  0.003  | 0.004 | **  |
|       **author_group:ns(date)**        | 0.066  |  0.066  |   1    | 427534 | 0.3906  |  0.53   | 0.53  |     |
|     **project:type:author_group**      |  9.51  | 0.4529  |   21   | 425566 |  2.68   |  1e-04  | 1e-04 | *** |
|       **project:type:ns(date)**        | 23.16  |  1.103  |   21   | 404726 |  6.527  |  1e-04  | 1e-04 | *** |
|   **project:author_group:ns(date)**    | 8.629  |  1.233  |   7    | 270842 |  7.295  |  1e-04  | 1e-04 | *** |
|     **type:author_group:ns(date)**     | 1.076  | 0.3586  |   3    | 471022 |  2.122  |  0.095  | 0.119 |     |
| **project:type:author_group:ns(date)** | 10.06  | 0.4789  |   21   | 407739 |  2.835  |  1e-04  | 1e-04 | *** |

Table: Type III Analysis of Variance Table with Satterthwaite's method

Interestingly, we see much more volatility here in the emotion dynamics
of community members relative to the community nonmembers over time, even
when we collapse across all projects.

Perhaps more interestingly, we see a difference in the affect dynamics
only in the last year: Members' tickets are becoming more positive, while
nonmembers' tickets are becoming more negative.

We'll need to do an analysis to follow up on this.



![**Figure**. Sentiment over time by contribution type (ticket vs. comment) and community membership at the time of posting (member vs. nonmember).](../../figures/sentiment_analysis/ossc-sentiment_membership_contribution_time-aggregated-knitr.jpg)


![**Figure**. Sentiment over time by contribution type (ticket vs. comment) and community membership  at the time of posting (member vs. nonmember) by project.](../../figures/sentiment_analysis/ossc-sentiment_membership_contribution_time-by_project-knitr.jpg)

### Model 1.3: Do tickets and comments materially differ in gratitude?

First, let's take a look at a summary table of expressions of gratitude by
membership status and contribution type.



Now that we have a better idea of how the underlying data look, let's go ahead
and build our model.


```r
# do users tend to express appreciation and gratitude differently by group and content?
creators_v_commenters_gratitude_by_project = lmer(log(grateful_count + 1) ~ project * author_group * type +
                                          (1 | author_name),
                                        data=sentiment_frame)

# print results
summary(creators_v_commenters_gratitude_by_project)
```

```
## Linear mixed model fit by REML. t-tests use Satterthwaite's method [
## lmerModLmerTest]
## Formula: log(grateful_count + 1) ~ project * author_group * type + (1 |  
##     author_name)
##    Data: sentiment_frame
## 
## REML criterion at convergence: -110177.8
## 
## Scaled residuals: 
##     Min      1Q  Median      3Q     Max 
## -3.2344 -0.4753 -0.2702 -0.0621  6.8493 
## 
## Random effects:
##  Groups      Name        Variance Std.Dev.
##  author_name (Intercept) 0.01489  0.1220  
##  Residual                0.04503  0.2122  
## Number of obs: 480854, groups:  author_name, 18346
## 
## Fixed effects:
##                                                                   Estimate
## (Intercept)                                                      0.0886265
## projectmayavi                                                   -0.0039174
## projectnumpy                                                    -0.0173448
## projectpandas                                                   -0.0305130
## projectscikit-image                                             -0.0568000
## projectscikit-learn                                             -0.0369905
## projectscipy                                                    -0.0142559
## projectsphinx-gallery                                           -0.0160015
## author_groupnonmember                                           -0.0202879
## typeissue_reply                                                  0.0263509
## typepr_post                                                      0.0021558
## typepr_reply                                                     0.0542937
## projectmayavi:author_groupnonmember                              0.0849245
## projectnumpy:author_groupnonmember                               0.0107245
## projectpandas:author_groupnonmember                              0.0144297
## projectscikit-image:author_groupnonmember                        0.0712853
## projectscikit-learn:author_groupnonmember                        0.0659685
## projectscipy:author_groupnonmember                               0.0249989
## projectsphinx-gallery:author_groupnonmember                      0.0612219
## projectmayavi:typeissue_reply                                    0.0023502
## projectnumpy:typeissue_reply                                    -0.0081041
## projectpandas:typeissue_reply                                    0.0134577
## projectscikit-image:typeissue_reply                              0.0336284
## projectscikit-learn:typeissue_reply                              0.0194103
## projectscipy:typeissue_reply                                     0.0007676
## projectsphinx-gallery:typeissue_reply                           -0.0060581
## projectmayavi:typepr_post                                       -0.0373449
## projectnumpy:typepr_post                                        -0.0115245
## projectpandas:typepr_post                                        0.0032008
## projectscikit-image:typepr_post                                  0.0110049
## projectscikit-learn:typepr_post                                 -0.0006066
## projectscipy:typepr_post                                        -0.0057920
## projectsphinx-gallery:typepr_post                               -0.0040268
## projectmayavi:typepr_reply                                       0.1123571
## projectnumpy:typepr_reply                                        0.0292590
## projectpandas:typepr_reply                                       0.0473419
## projectscikit-image:typepr_reply                                 0.0706388
## projectscikit-learn:typepr_reply                                 0.0406009
## projectscipy:typepr_reply                                        0.0464649
## projectsphinx-gallery:typepr_reply                               0.0092669
## author_groupnonmember:typeissue_reply                            0.0612709
## author_groupnonmember:typepr_post                               -0.0197690
## author_groupnonmember:typepr_reply                               0.0361101
## projectmayavi:author_groupnonmember:typeissue_reply             -0.0563746
## projectnumpy:author_groupnonmember:typeissue_reply               0.0153204
## projectpandas:author_groupnonmember:typeissue_reply              0.0010600
## projectscikit-image:author_groupnonmember:typeissue_reply       -0.0582422
## projectscikit-learn:author_groupnonmember:typeissue_reply       -0.0645542
## projectscipy:author_groupnonmember:typeissue_reply              -0.0083797
## projectsphinx-gallery:author_groupnonmember:typeissue_reply     -0.0222245
## projectmayavi:author_groupnonmember:typepr_post                 -0.0135124
## projectnumpy:author_groupnonmember:typepr_post                   0.0106607
## projectpandas:author_groupnonmember:typepr_post                  0.0055226
## projectscikit-image:author_groupnonmember:typepr_post           -0.0262642
## projectscikit-learn:author_groupnonmember:typepr_post           -0.0284425
## projectscipy:author_groupnonmember:typepr_post                   0.0016058
## projectsphinx-gallery:author_groupnonmember:typepr_post         -0.0276545
## projectmayavi:author_groupnonmember:typepr_reply                -0.1128144
## projectnumpy:author_groupnonmember:typepr_reply                 -0.0218859
## projectpandas:author_groupnonmember:typepr_reply                -0.0280799
## projectscikit-image:author_groupnonmember:typepr_reply          -0.0869489
## projectscikit-learn:author_groupnonmember:typepr_reply          -0.0701249
## projectscipy:author_groupnonmember:typepr_reply                 -0.0423929
## projectsphinx-gallery:author_groupnonmember:typepr_reply        -0.0962306
##                                                                 Std. Error
## (Intercept)                                                      0.0058624
## projectmayavi                                                    0.0291890
## projectnumpy                                                     0.0075835
## projectpandas                                                    0.0065116
## projectscikit-image                                              0.0111856
## projectscikit-learn                                              0.0075142
## projectscipy                                                     0.0091545
## projectsphinx-gallery                                            0.0224675
## author_groupnonmember                                            0.0070012
## typeissue_reply                                                  0.0054366
## typepr_post                                                      0.0059645
## typepr_reply                                                     0.0053652
## projectmayavi:author_groupnonmember                              0.0313908
## projectnumpy:author_groupnonmember                               0.0096682
## projectpandas:author_groupnonmember                              0.0081337
## projectscikit-image:author_groupnonmember                        0.0149300
## projectscikit-learn:author_groupnonmember                        0.0095571
## projectscipy:author_groupnonmember                               0.0111377
## projectsphinx-gallery:author_groupnonmember                      0.0316064
## projectmayavi:typeissue_reply                                    0.0261088
## projectnumpy:typeissue_reply                                     0.0074218
## projectpandas:typeissue_reply                                    0.0061081
## projectscikit-image:typeissue_reply                              0.0109745
## projectscikit-learn:typeissue_reply                              0.0071608
## projectscipy:typeissue_reply                                     0.0091245
## projectsphinx-gallery:typeissue_reply                            0.0235863
## projectmayavi:typepr_post                                        0.0287605
## projectnumpy:typepr_post                                         0.0084350
## projectpandas:typepr_post                                        0.0069971
## projectscikit-image:typepr_post                                  0.0121819
## projectscikit-learn:typepr_post                                  0.0082879
## projectscipy:typepr_post                                         0.0100626
## projectsphinx-gallery:typepr_post                                0.0279197
## projectmayavi:typepr_reply                                       0.0265642
## projectnumpy:typepr_reply                                        0.0074034
## projectpandas:typepr_reply                                       0.0060533
## projectscikit-image:typepr_reply                                 0.0106874
## projectscikit-learn:typepr_reply                                 0.0070476
## projectscipy:typepr_reply                                        0.0089904
## projectsphinx-gallery:typepr_reply                               0.0229117
## author_groupnonmember:typeissue_reply                            0.0072677
## author_groupnonmember:typepr_post                                0.0090391
## author_groupnonmember:typepr_reply                               0.0078322
## projectmayavi:author_groupnonmember:typeissue_reply              0.0301366
## projectnumpy:author_groupnonmember:typeissue_reply               0.0102891
## projectpandas:author_groupnonmember:typeissue_reply              0.0085062
## projectscikit-image:author_groupnonmember:typeissue_reply        0.0158907
## projectscikit-learn:author_groupnonmember:typeissue_reply        0.0099417
## projectscipy:author_groupnonmember:typeissue_reply               0.0118520
## projectsphinx-gallery:author_groupnonmember:typeissue_reply      0.0354398
## projectmayavi:author_groupnonmember:typepr_post                  0.0400138
## projectnumpy:author_groupnonmember:typepr_post                   0.0129588
## projectpandas:author_groupnonmember:typepr_post                  0.0109555
## projectscikit-image:author_groupnonmember:typepr_post            0.0187524
## projectscikit-learn:author_groupnonmember:typepr_post            0.0123030
## projectscipy:author_groupnonmember:typepr_post                   0.0142713
## projectsphinx-gallery:author_groupnonmember:typepr_post          0.0462862
## projectmayavi:author_groupnonmember:typepr_reply                 0.0350616
## projectnumpy:author_groupnonmember:typepr_reply                  0.0110198
## projectpandas:author_groupnonmember:typepr_reply                 0.0092623
## projectscikit-image:author_groupnonmember:typepr_reply           0.0159727
## projectscikit-learn:author_groupnonmember:typepr_reply           0.0104209
## projectscipy:author_groupnonmember:typepr_reply                  0.0122711
## projectsphinx-gallery:author_groupnonmember:typepr_reply         0.0351427
##                                                                         df
## (Intercept)                                                 444290.7409341
## projectmayavi                                               457351.8416845
## projectnumpy                                                471684.7197716
## projectpandas                                               479881.7567204
## projectscikit-image                                         471032.6571401
## projectscikit-learn                                         477279.4202904
## projectscipy                                                469892.0752636
## projectsphinx-gallery                                       464613.5448605
## author_groupnonmember                                       462933.3610481
## typeissue_reply                                             465114.9030773
## typepr_post                                                 465419.8063197
## typepr_reply                                                465439.0700498
## projectmayavi:author_groupnonmember                         453685.8381913
## projectnumpy:author_groupnonmember                          463527.2174493
## projectpandas:author_groupnonmember                         457385.1025589
## projectscikit-image:author_groupnonmember                   450242.2531613
## projectscikit-learn:author_groupnonmember                   455969.0845524
## projectscipy:author_groupnonmember                          469656.3590755
## projectsphinx-gallery:author_groupnonmember                 476692.7903939
## projectmayavi:typeissue_reply                               464465.3267601
## projectnumpy:typeissue_reply                                464409.3306440
## projectpandas:typeissue_reply                               465004.3169467
## projectscikit-image:typeissue_reply                         463548.7904974
## projectscikit-learn:typeissue_reply                         464401.4433601
## projectscipy:typeissue_reply                                464059.6116677
## projectsphinx-gallery:typeissue_reply                       463325.7818133
## projectmayavi:typepr_post                                   463592.7251614
## projectnumpy:typepr_post                                    464529.6337476
## projectpandas:typepr_post                                   465358.3514394
## projectscikit-image:typepr_post                             463725.3345856
## projectscikit-learn:typepr_post                             464595.1303343
## projectscipy:typepr_post                                    464203.3420793
## projectsphinx-gallery:typepr_post                           463349.1671776
## projectmayavi:typepr_reply                                  463962.1266386
## projectnumpy:typepr_reply                                   464694.3835222
## projectpandas:typepr_reply                                  465431.7370657
## projectscikit-image:typepr_reply                            463719.5251353
## projectscikit-learn:typepr_reply                            464699.6702371
## projectscipy:typepr_reply                                   464270.0475308
## projectsphinx-gallery:typepr_reply                          463463.2570631
## author_groupnonmember:typeissue_reply                       480420.0287378
## author_groupnonmember:typepr_post                           459564.0093101
## author_groupnonmember:typepr_reply                          440123.1785767
## projectmayavi:author_groupnonmember:typeissue_reply         480265.4475609
## projectnumpy:author_groupnonmember:typeissue_reply          479321.1052051
## projectpandas:author_groupnonmember:typeissue_reply         479259.9939152
## projectscikit-image:author_groupnonmember:typeissue_reply   478757.7359195
## projectscikit-learn:author_groupnonmember:typeissue_reply   477328.1301056
## projectscipy:author_groupnonmember:typeissue_reply          480600.4542249
## projectsphinx-gallery:author_groupnonmember:typeissue_reply 473080.5093630
## projectmayavi:author_groupnonmember:typepr_post             474469.7280886
## projectnumpy:author_groupnonmember:typepr_post              463837.1897580
## projectpandas:author_groupnonmember:typepr_post             455597.4788000
## projectscikit-image:author_groupnonmember:typepr_post       463392.9124450
## projectscikit-learn:author_groupnonmember:typepr_post       460823.9104542
## projectscipy:author_groupnonmember:typepr_post              470242.8544376
## projectsphinx-gallery:author_groupnonmember:typepr_post     478519.1522360
## projectmayavi:author_groupnonmember:typepr_reply            472212.7568101
## projectnumpy:author_groupnonmember:typepr_reply             449974.6503269
## projectpandas:author_groupnonmember:typepr_reply            432116.9830418
## projectscikit-image:author_groupnonmember:typepr_reply      447616.1451112
## projectscikit-learn:author_groupnonmember:typepr_reply      439630.9524429
## projectscipy:author_groupnonmember:typepr_reply             460598.5048736
## projectsphinx-gallery:author_groupnonmember:typepr_reply    477556.2510190
##                                                             t value
## (Intercept)                                                  15.118
## projectmayavi                                                -0.134
## projectnumpy                                                 -2.287
## projectpandas                                                -4.686
## projectscikit-image                                          -5.078
## projectscikit-learn                                          -4.923
## projectscipy                                                 -1.557
## projectsphinx-gallery                                        -0.712
## author_groupnonmember                                        -2.898
## typeissue_reply                                               4.847
## typepr_post                                                   0.361
## typepr_reply                                                 10.120
## projectmayavi:author_groupnonmember                           2.705
## projectnumpy:author_groupnonmember                            1.109
## projectpandas:author_groupnonmember                           1.774
## projectscikit-image:author_groupnonmember                     4.775
## projectscikit-learn:author_groupnonmember                     6.903
## projectscipy:author_groupnonmember                            2.245
## projectsphinx-gallery:author_groupnonmember                   1.937
## projectmayavi:typeissue_reply                                 0.090
## projectnumpy:typeissue_reply                                 -1.092
## projectpandas:typeissue_reply                                 2.203
## projectscikit-image:typeissue_reply                           3.064
## projectscikit-learn:typeissue_reply                           2.711
## projectscipy:typeissue_reply                                  0.084
## projectsphinx-gallery:typeissue_reply                        -0.257
## projectmayavi:typepr_post                                    -1.298
## projectnumpy:typepr_post                                     -1.366
## projectpandas:typepr_post                                     0.457
## projectscikit-image:typepr_post                               0.903
## projectscikit-learn:typepr_post                              -0.073
## projectscipy:typepr_post                                     -0.576
## projectsphinx-gallery:typepr_post                            -0.144
## projectmayavi:typepr_reply                                    4.230
## projectnumpy:typepr_reply                                     3.952
## projectpandas:typepr_reply                                    7.821
## projectscikit-image:typepr_reply                              6.610
## projectscikit-learn:typepr_reply                              5.761
## projectscipy:typepr_reply                                     5.168
## projectsphinx-gallery:typepr_reply                            0.404
## author_groupnonmember:typeissue_reply                         8.431
## author_groupnonmember:typepr_post                            -2.187
## author_groupnonmember:typepr_reply                            4.610
## projectmayavi:author_groupnonmember:typeissue_reply          -1.871
## projectnumpy:author_groupnonmember:typeissue_reply            1.489
## projectpandas:author_groupnonmember:typeissue_reply           0.125
## projectscikit-image:author_groupnonmember:typeissue_reply    -3.665
## projectscikit-learn:author_groupnonmember:typeissue_reply    -6.493
## projectscipy:author_groupnonmember:typeissue_reply           -0.707
## projectsphinx-gallery:author_groupnonmember:typeissue_reply  -0.627
## projectmayavi:author_groupnonmember:typepr_post              -0.338
## projectnumpy:author_groupnonmember:typepr_post                0.823
## projectpandas:author_groupnonmember:typepr_post               0.504
## projectscikit-image:author_groupnonmember:typepr_post        -1.401
## projectscikit-learn:author_groupnonmember:typepr_post        -2.312
## projectscipy:author_groupnonmember:typepr_post                0.113
## projectsphinx-gallery:author_groupnonmember:typepr_post      -0.597
## projectmayavi:author_groupnonmember:typepr_reply             -3.218
## projectnumpy:author_groupnonmember:typepr_reply              -1.986
## projectpandas:author_groupnonmember:typepr_reply             -3.032
## projectscikit-image:author_groupnonmember:typepr_reply       -5.444
## projectscikit-learn:author_groupnonmember:typepr_reply       -6.729
## projectscipy:author_groupnonmember:typepr_reply              -3.455
## projectsphinx-gallery:author_groupnonmember:typepr_reply     -2.738
##                                                                         Pr(>|t|)
## (Intercept)                                                 < 0.0000000000000002
## projectmayavi                                                           0.893237
## projectnumpy                                                            0.022187
## projectpandas                                                0.00000278755152494
## projectscikit-image                                          0.00000038168701138
## projectscikit-learn                                          0.00000085360180579
## projectscipy                                                            0.119410
## projectsphinx-gallery                                                   0.476337
## author_groupnonmember                                                   0.003758
## typeissue_reply                                              0.00000125409476286
## typepr_post                                                             0.717769
## typepr_reply                                                < 0.0000000000000002
## projectmayavi:author_groupnonmember                                     0.006823
## projectnumpy:author_groupnonmember                                      0.267320
## projectpandas:author_groupnonmember                                     0.076053
## projectscikit-image:author_groupnonmember                    0.00000180102042094
## projectscikit-learn:author_groupnonmember                    0.00000000000511319
## projectscipy:author_groupnonmember                                      0.024799
## projectsphinx-gallery:author_groupnonmember                             0.052745
## projectmayavi:typeissue_reply                                           0.928273
## projectnumpy:typeissue_reply                                            0.274858
## projectpandas:typeissue_reply                                           0.027579
## projectscikit-image:typeissue_reply                                     0.002182
## projectscikit-learn:typeissue_reply                                     0.006716
## projectscipy:typeissue_reply                                            0.932955
## projectsphinx-gallery:typeissue_reply                                   0.797297
## projectmayavi:typepr_post                                               0.194123
## projectnumpy:typepr_post                                                0.171855
## projectpandas:typepr_post                                               0.647349
## projectscikit-image:typepr_post                                         0.366325
## projectscikit-learn:typepr_post                                         0.941652
## projectscipy:typepr_post                                                0.564889
## projectsphinx-gallery:typepr_post                                       0.885321
## projectmayavi:typepr_reply                                   0.00002341016756652
## projectnumpy:typepr_reply                                    0.00007747878709564
## projectpandas:typepr_reply                                   0.00000000000000526
## projectscikit-image:typepr_reply                             0.00000000003858791
## projectscikit-learn:typepr_reply                             0.00000000837084790
## projectscipy:typepr_reply                                    0.00000023637238275
## projectsphinx-gallery:typepr_reply                                      0.685875
## author_groupnonmember:typeissue_reply                       < 0.0000000000000002
## author_groupnonmember:typepr_post                                       0.028740
## author_groupnonmember:typepr_reply                           0.00000401854253701
## projectmayavi:author_groupnonmember:typeissue_reply                     0.061396
## projectnumpy:author_groupnonmember:typeissue_reply                      0.136489
## projectpandas:author_groupnonmember:typeissue_reply                     0.900828
## projectscikit-image:author_groupnonmember:typeissue_reply               0.000247
## projectscikit-learn:author_groupnonmember:typeissue_reply    0.00000000008408168
## projectscipy:author_groupnonmember:typeissue_reply                      0.479547
## projectsphinx-gallery:author_groupnonmember:typeissue_reply             0.530589
## projectmayavi:author_groupnonmember:typepr_post                         0.735595
## projectnumpy:author_groupnonmember:typepr_post                          0.410701
## projectpandas:author_groupnonmember:typepr_post                         0.614198
## projectscikit-image:author_groupnonmember:typepr_post                   0.161342
## projectscikit-learn:author_groupnonmember:typepr_post                   0.020787
## projectscipy:author_groupnonmember:typepr_post                          0.910413
## projectsphinx-gallery:author_groupnonmember:typepr_post                 0.550196
## projectmayavi:author_groupnonmember:typepr_reply                        0.001293
## projectnumpy:author_groupnonmember:typepr_reply                         0.047029
## projectpandas:author_groupnonmember:typepr_reply                        0.002433
## projectscikit-image:author_groupnonmember:typepr_reply       0.00000005224668521
## projectscikit-learn:author_groupnonmember:typepr_reply       0.00000000001707599
## projectscipy:author_groupnonmember:typepr_reply                         0.000551
## projectsphinx-gallery:author_groupnonmember:typepr_reply                0.006176
##                                                                
## (Intercept)                                                 ***
## projectmayavi                                                  
## projectnumpy                                                *  
## projectpandas                                               ***
## projectscikit-image                                         ***
## projectscikit-learn                                         ***
## projectscipy                                                   
## projectsphinx-gallery                                          
## author_groupnonmember                                       ** 
## typeissue_reply                                             ***
## typepr_post                                                    
## typepr_reply                                                ***
## projectmayavi:author_groupnonmember                         ** 
## projectnumpy:author_groupnonmember                             
## projectpandas:author_groupnonmember                         .  
## projectscikit-image:author_groupnonmember                   ***
## projectscikit-learn:author_groupnonmember                   ***
## projectscipy:author_groupnonmember                          *  
## projectsphinx-gallery:author_groupnonmember                 .  
## projectmayavi:typeissue_reply                                  
## projectnumpy:typeissue_reply                                   
## projectpandas:typeissue_reply                               *  
## projectscikit-image:typeissue_reply                         ** 
## projectscikit-learn:typeissue_reply                         ** 
## projectscipy:typeissue_reply                                   
## projectsphinx-gallery:typeissue_reply                          
## projectmayavi:typepr_post                                      
## projectnumpy:typepr_post                                       
## projectpandas:typepr_post                                      
## projectscikit-image:typepr_post                                
## projectscikit-learn:typepr_post                                
## projectscipy:typepr_post                                       
## projectsphinx-gallery:typepr_post                              
## projectmayavi:typepr_reply                                  ***
## projectnumpy:typepr_reply                                   ***
## projectpandas:typepr_reply                                  ***
## projectscikit-image:typepr_reply                            ***
## projectscikit-learn:typepr_reply                            ***
## projectscipy:typepr_reply                                   ***
## projectsphinx-gallery:typepr_reply                             
## author_groupnonmember:typeissue_reply                       ***
## author_groupnonmember:typepr_post                           *  
## author_groupnonmember:typepr_reply                          ***
## projectmayavi:author_groupnonmember:typeissue_reply         .  
## projectnumpy:author_groupnonmember:typeissue_reply             
## projectpandas:author_groupnonmember:typeissue_reply            
## projectscikit-image:author_groupnonmember:typeissue_reply   ***
## projectscikit-learn:author_groupnonmember:typeissue_reply   ***
## projectscipy:author_groupnonmember:typeissue_reply             
## projectsphinx-gallery:author_groupnonmember:typeissue_reply    
## projectmayavi:author_groupnonmember:typepr_post                
## projectnumpy:author_groupnonmember:typepr_post                 
## projectpandas:author_groupnonmember:typepr_post                
## projectscikit-image:author_groupnonmember:typepr_post          
## projectscikit-learn:author_groupnonmember:typepr_post       *  
## projectscipy:author_groupnonmember:typepr_post                 
## projectsphinx-gallery:author_groupnonmember:typepr_post        
## projectmayavi:author_groupnonmember:typepr_reply            ** 
## projectnumpy:author_groupnonmember:typepr_reply             *  
## projectpandas:author_groupnonmember:typepr_reply            ** 
## projectscikit-image:author_groupnonmember:typepr_reply      ***
## projectscikit-learn:author_groupnonmember:typepr_reply      ***
## projectscipy:author_groupnonmember:typepr_reply             ***
## projectsphinx-gallery:author_groupnonmember:typepr_reply    ** 
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
pander_clean_anova(anova_results)
```



|            &nbsp;             | sum_sq | mean_sq | num_df | den_df | f_value | p_value | p_adj | sig |
|:-----------------------------:|:------:|:-------:|:------:|:------:|:-------:|:-------:|:-----:|:---:|
|          **project**          | 2.843  | 0.4061  |   7    | 261810 |  9.017  |  1e-04  | 1e-04 | *** |
|       **author_group**        |  1.42  |  1.42   |   1    | 415018 |  31.53  |  1e-04  | 1e-04 | *** |
|           **type**            | 61.23  |  20.41  |   3    | 471397 |  453.2  |  1e-04  | 1e-04 | *** |
|   **project:author_group**    | 1.884  | 0.2692  |   7    | 395490 |  5.977  |  1e-04  | 1e-04 | *** |
|       **project:type**        | 8.633  | 0.4111  |   21   | 446377 |  9.128  |  1e-04  | 1e-04 | *** |
|     **author_group:type**     | 9.502  |  3.167  |   3    | 471687 |  70.33  |  1e-04  | 1e-04 | *** |
| **project:author_group:type** | 7.556  | 0.3598  |   21   | 447370 |  7.99   |  1e-04  | 1e-04 | *** |

Table: Type III Analysis of Variance Table with Satterthwaite's method



![**Figure**. Expressions of gratitude by contribution type (ticket vs. comment) and community membership (member vs. nonmember) at the time of posting.](../../figures/sentiment_analysis/ossc-grateful_membership_contribution-knitr.jpg)

### Model 1.4: Do tickets and comments materially differ in gratitude over time?

**Note**: Having difficulty getting this to converge.


```r
# do users tend to express appreciation and gratitude differently by group and content?
creators_v_commenters_gratitude_time = lmer(log(grateful_count + 1) ~ project + (author_group + type) * ns(date, df=8) +
                                               (1 | author_name),
                                             data=sentiment_frame)
                                             #family=poisson)

# print results
pander_lme(creators_v_commenters_gratitude_time)
```



|                   &nbsp;                    | Estimate  | Std..Error |   df   | t.value |     Pr...t..     |   p    | p_adj | sig |
|:-------------------------------------------:|:---------:|:----------:|:------:|:-------:|:----------------:|:------:|:-----:|:---:|
|               **(Intercept)**               |  0.07424  |  0.01589   | 478081 |  4.671  |   0.000002998    | 0.0001 | 0.001 | **  |
|              **projectmayavi**              |  0.05131  |  0.007361  | 106539 |  6.971  | 0.00000000000316 | 0.0001 | 0.001 | **  |
|              **projectnumpy**               | -0.005685 |  0.002393  | 221015 | -2.375  |     0.01753      | 0.018  | 0.058 |  .  |
|              **projectpandas**              | -0.003797 |  0.00238   | 125897 | -1.595  |      0.1107      | 0.111  | 0.206 |     |
|           **projectscikit-image**           | -0.005136 |  0.003454  | 236075 | -1.487  |      0.1371      | 0.137  | 0.238 |     |
|           **projectscikit-learn**           | -0.007008 |  0.002532  | 124531 | -2.768  |     0.00565      | 0.006  | 0.022 |  *  |
|              **projectscipy**               | 0.009305  |  0.002506  | 219340 |  3.713  |     0.000205     | 0.0002 | 0.002 | **  |
|          **projectsphinx-gallery**          | -0.01429  |  0.005048  | 467546 | -2.832  |     0.004631     | 0.005  | 0.02  |  *  |
|          **author_groupnonmember**          |  0.03728  |  0.009995  | 458552 |  3.73   |    0.0001918     | 0.0002 | 0.002 | **  |
|             **typeissue_reply**             |  0.02765  |  0.01728   | 478631 |   1.6   |      0.1097      |  0.11  | 0.206 |     |
|               **typepr_post**               | -0.02606  |  0.01964   | 480599 | -1.327  |      0.1844      | 0.184  | 0.27  |     |
|              **typepr_reply**               |   0.055   |  0.01609   | 480419 |  3.419  |     0.000629     | 0.001  | 0.006 | **  |
|            **ns(date, df = 8)1**            | -0.01832  |  0.01451   | 480801 | -1.262  |      0.2068      | 0.207  | 0.29  |     |
|            **ns(date, df = 8)2**            | -0.01401  |  0.01907   | 480637 | -0.7346 |      0.4626      |  0.46  | 0.54  |     |
|            **ns(date, df = 8)3**            | -0.004744 |  0.01685   | 480604 | -0.2815 |      0.7783      |  0.78  | 0.84  |     |
|            **ns(date, df = 8)4**            | -0.03053  |  0.01825   | 480148 | -1.673  |     0.09434      | 0.094  | 0.196 |     |
|            **ns(date, df = 8)5**            | -0.00315  |  0.01754   | 480043 | -0.1796 |      0.8574      |  0.86  | 0.89  |     |
|            **ns(date, df = 8)6**            | -0.01818  |  0.01258   | 475593 | -1.446  |      0.1482      | 0.148  | 0.248 |     |
|            **ns(date, df = 8)7**            | -0.02116  |  0.03548   | 480800 | -0.5965 |      0.5508      |  0.55  | 0.64  |     |
|            **ns(date, df = 8)8**            | 0.001346  |  0.009384  | 463233 | 0.1434  |      0.886       |  0.89  | 0.91  |     |
| **author_groupnonmember:ns(date, df = 8)1** | -0.01294  |  0.009589  | 431440 | -1.349  |      0.1772      | 0.177  | 0.26  |     |
| **author_groupnonmember:ns(date, df = 8)2** | -0.01751  |   0.0123   | 416824 | -1.424  |      0.1545      | 0.154  | 0.25  |     |
| **author_groupnonmember:ns(date, df = 8)3** | -0.02349  |  0.01101   | 410675 | -2.135  |     0.03279      | 0.033  | 0.09  |  .  |
| **author_groupnonmember:ns(date, df = 8)4** | -0.006389 |   0.0118   | 397789 | -0.5413 |      0.5883      |  0.59  | 0.65  |     |
| **author_groupnonmember:ns(date, df = 8)5** | -0.02683  |  0.01136   | 398856 | -2.363  |     0.01812      | 0.018  | 0.058 |  .  |
| **author_groupnonmember:ns(date, df = 8)6** | -0.02502  |  0.008089  | 333398 | -3.093  |     0.001982     | 0.002  | 0.012 |  *  |
| **author_groupnonmember:ns(date, df = 8)7** | -0.03246  |  0.02312   | 438111 | -1.404  |      0.1603      |  0.16  | 0.25  |     |
| **author_groupnonmember:ns(date, df = 8)8** | -0.01897  |  0.006326  | 220662 | -2.999  |     0.002709     | 0.003  | 0.014 |  *  |
|    **typeissue_reply:ns(date, df = 8)1**    |  0.0174   |  0.01586   | 478514 |  1.097  |      0.2727      |  0.27  | 0.33  |     |
|      **typepr_post:ns(date, df = 8)1**      |  0.02186  |  0.01814   | 480663 |  1.205  |      0.2281      | 0.228  | 0.29  |     |
|     **typepr_reply:ns(date, df = 8)1**      |  0.02782  |  0.01484   | 480503 |  1.875  |     0.06083      | 0.061  | 0.144 |     |
|    **typeissue_reply:ns(date, df = 8)2**    |  0.02515  |  0.02068   | 480072 |  1.216  |      0.2241      | 0.224  | 0.29  |     |
|      **typepr_post:ns(date, df = 8)2**      |  0.02896  |  0.02409   | 480245 |  1.202  |      0.2293      | 0.229  | 0.29  |     |
|     **typepr_reply:ns(date, df = 8)2**      |  0.04528  |  0.01956   | 479813 |  2.315  |      0.0206      | 0.021  | 0.064 |  .  |
|    **typeissue_reply:ns(date, df = 8)3**    |  0.0105   |  0.01832   | 479942 |  0.573  |      0.5667      |  0.57  | 0.64  |     |
|      **typepr_post:ns(date, df = 8)3**      |  0.01945  |   0.0212   | 480169 | 0.9176  |      0.3588      |  0.36  | 0.44  |     |
|     **typepr_reply:ns(date, df = 8)3**      |  0.03703  |  0.01728   | 479770 |  2.143  |      0.0321      | 0.032  | 0.09  |  .  |
|    **typeissue_reply:ns(date, df = 8)4**    |  0.03987  |  0.01978   | 480570 |  2.016  |     0.04376      | 0.044  | 0.109 |     |
|      **typepr_post:ns(date, df = 8)4**      |  0.03102  |  0.02304   | 479669 |  1.346  |      0.1782      | 0.178  | 0.26  |     |
|     **typepr_reply:ns(date, df = 8)4**      |  0.06183  |  0.01871   | 478873 |  3.304  |    0.0009537     | 0.001  | 0.006 | **  |
|    **typeissue_reply:ns(date, df = 8)5**    |  0.02313  |  0.01903   | 480580 |  1.215  |      0.2242      | 0.224  | 0.29  |     |
|      **typepr_post:ns(date, df = 8)5**      |  0.03656  |  0.02208   | 479597 |  1.655  |     0.09783      | 0.098  | 0.196 |     |
|     **typepr_reply:ns(date, df = 8)5**      |  0.05303  |  0.01798   | 478663 |  2.95   |     0.003178     | 0.003  | 0.014 |  *  |
|    **typeissue_reply:ns(date, df = 8)6**    |  0.02738  |  0.01347   | 479925 |  2.032  |     0.04213      | 0.042  | 0.109 |     |
|      **typepr_post:ns(date, df = 8)6**      |  0.02764  |  0.01569   | 475149 |  1.761  |     0.07825      | 0.078  | 0.176 |     |
|     **typepr_reply:ns(date, df = 8)6**      |  0.06425  |  0.01287   | 472283 |  4.993  |   0.0000005938   | 0.0001 | 0.001 | **  |
|    **typeissue_reply:ns(date, df = 8)7**    |  0.06568  |  0.03884   | 479183 |  1.691  |     0.09079      | 0.091  | 0.196 |     |
|      **typepr_post:ns(date, df = 8)7**      |  0.06909  |  0.04472   | 480614 |  1.545  |      0.1224      | 0.122  | 0.219 |     |
|     **typepr_reply:ns(date, df = 8)7**      |  0.1023   |  0.03641   | 480368 |  2.81   |     0.004953     | 0.005  | 0.02  |  *  |
|    **typeissue_reply:ns(date, df = 8)8**    | 0.0001938 |  0.009747  | 470307 | 0.01988 |      0.9841      |  0.98  | 0.98  |     |
|      **typepr_post:ns(date, df = 8)8**      | -0.002133 |  0.01178   | 467571 | -0.1811 |      0.8563      |  0.86  | 0.89  |     |
|     **typepr_reply:ns(date, df = 8)8**      |  0.03815  |  0.009566  | 457346 |  3.987  |    0.0000668     | 0.0001 | 0.001 | **  |


```r
anova_results = anova(creators_v_commenters_gratitude_time)
pander_clean_anova(anova_results)
```



|              &nbsp;               | sum_sq | mean_sq | num_df | den_df | f_value | p_value | p_adj | sig |
|:---------------------------------:|:------:|:-------:|:------:|:------:|:-------:|:-------:|:-----:|:---:|
|            **project**            | 6.325  | 0.9036  |   7    | 187379 |  20.05  |  1e-04  | 1e-04 | *** |
|         **author_group**          | 0.627  |  0.627  |   1    | 458552 |  13.91  |  2e-04  | 2e-04 | *** |
|             **type**              | 1.888  | 0.6292  |   3    | 479205 |  13.96  |  1e-04  | 1e-04 | *** |
|       **ns(date, df = 8)**        | 2.209  | 0.2761  |   8    | 232378 |  6.126  |  1e-04  | 1e-04 | *** |
| **author_group:ns(date, df = 8)** | 1.714  | 0.2142  |   8    | 212741 |  4.753  |  1e-04  | 1e-04 | *** |
|     **type:ns(date, df = 8)**     | 14.66  | 0.6106  |   24   | 475633 |  13.55  |  1e-04  | 1e-04 | *** |

Table: Type III Analysis of Variance Table with Satterthwaite's method



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
  
  #convert to factors (as needed) for proper modeling
  mutate_at(vars(project,
                 author_name,
                 author_group,
                 author_association,
                 type,
                 type_family,
                 ticket_family,
                 retained_newcomer),
            as.factor)
```

### Model 2.1: How does a community's response to newcomers predict the newcomer's decision to return?


```r
# what predicts continuing retention?
retention_predictors = glm(retained_newcomer ~ (project +
                                                open_time +
                                                comment_sentiment_mean + 
                                                comment_sentiment_max_negative + 
                                                comment_grateful_cumulative +
                                                number_of_comments +
                                                comment_member_ratio) * ticket_family,
                         data=retention_frame,
                         family=binomial)

# print it
summary(retention_predictors)
```

```
## 
## Call:
## glm(formula = retained_newcomer ~ (project + open_time + comment_sentiment_mean + 
##     comment_sentiment_max_negative + comment_grateful_cumulative + 
##     number_of_comments + comment_member_ratio) * ticket_family, 
##     family = binomial, data = retention_frame)
## 
## Deviance Residuals: 
##     Min       1Q   Median       3Q      Max  
## -2.3637  -0.9011  -0.7574   1.3116   2.3158  
## 
## Coefficients:
##                                                        Estimate
## (Intercept)                                    -0.7191918866661
## projectmayavi                                  -0.2789615884085
## projectnumpy                                   -0.5212856450314
## projectpandas                                   0.2277843261619
## projectscikit-image                            -0.0765388841066
## projectscikit-learn                            -0.0363185933883
## projectscipy                                   -0.4855619841680
## projectsphinx-gallery                           0.8382561475691
## open_time                                       0.0000000021193
## comment_sentiment_mean                          0.2884527309606
## comment_sentiment_max_negative                 -0.3462157230967
## comment_grateful_cumulative                    -0.0933062319696
## number_of_comments                              0.0200283207430
## comment_member_ratio                           -0.3526524132535
## ticket_familypr                                 0.9441526507007
## projectmayavi:ticket_familypr                   0.0608166518018
## projectnumpy:ticket_familypr                    0.5178765704788
## projectpandas:ticket_familypr                  -0.2709596299084
## projectscikit-image:ticket_familypr             0.0908637343644
## projectscikit-learn:ticket_familypr             0.1654917511694
## projectscipy:ticket_familypr                    0.5860824449299
## projectsphinx-gallery:ticket_familypr          -0.3791908395416
## open_time:ticket_familypr                      -0.0000000121430
## comment_sentiment_mean:ticket_familypr         -0.0126335960518
## comment_sentiment_max_negative:ticket_familypr  0.3343143990187
## comment_grateful_cumulative:ticket_familypr     0.0002422511395
## number_of_comments:ticket_familypr              0.0111889172724
## comment_member_ratio:ticket_familypr           -0.6141830134169
##                                                      Std. Error z value
## (Intercept)                                     0.0856242912187  -8.399
## projectmayavi                                   0.1640651655562  -1.700
## projectnumpy                                    0.0759970527896  -6.859
## projectpandas                                   0.0598445232691   3.806
## projectscikit-image                             0.1171309191055  -0.653
## projectscikit-learn                             0.0710311017009  -0.511
## projectscipy                                    0.0793833715227  -6.117
## projectsphinx-gallery                           0.3067255534598   2.733
## open_time                                       0.0000000005242   4.043
## comment_sentiment_mean                          0.0883630587347   3.264
## comment_sentiment_max_negative                  0.2067515409052  -1.675
## comment_grateful_cumulative                     0.0231419218488  -4.032
## number_of_comments                              0.0039908931738   5.019
## comment_member_ratio                            0.0822968041456  -4.285
## ticket_familypr                                 0.1574296284551   5.997
## projectmayavi:ticket_familypr                   0.4111119033740   0.148
## projectnumpy:ticket_familypr                    0.1344497304914   3.852
## projectpandas:ticket_familypr                   0.1148387871984  -2.359
## projectscikit-image:ticket_familypr             0.1922823359237   0.473
## projectscikit-learn:ticket_familypr             0.1210759994444   1.367
## projectscipy:ticket_familypr                    0.1387424967809   4.224
## projectsphinx-gallery:ticket_familypr           0.5846416212544  -0.649
## open_time:ticket_familypr                       0.0000000016131  -7.528
## comment_sentiment_mean:ticket_familypr          0.1816947765165  -0.070
## comment_sentiment_max_negative:ticket_familypr  0.3329336618170   1.004
## comment_grateful_cumulative:ticket_familypr     0.0321769952186   0.008
## number_of_comments:ticket_familypr              0.0061136408064   1.830
## comment_member_ratio:ticket_familypr            0.1496992404170  -4.103
##                                                            Pr(>|z|)    
## (Intercept)                                    < 0.0000000000000002 ***
## projectmayavi                                              0.089073 .  
## projectnumpy                                     0.0000000000069205 ***
## projectpandas                                              0.000141 ***
## projectscikit-image                                        0.513468    
## projectscikit-learn                                        0.609137    
## projectscipy                                     0.0000000009555021 ***
## projectsphinx-gallery                                      0.006278 ** 
## open_time                                        0.0000527773040476 ***
## comment_sentiment_mean                                     0.001097 ** 
## comment_sentiment_max_negative                             0.094023 .  
## comment_grateful_cumulative                      0.0000553245018347 ***
## number_of_comments                               0.0000005207490773 ***
## comment_member_ratio                             0.0000182633272465 ***
## ticket_familypr                                  0.0000000020062569 ***
## projectmayavi:ticket_familypr                              0.882396    
## projectnumpy:ticket_familypr                               0.000117 ***
## projectpandas:ticket_familypr                              0.018301 *  
## projectscikit-image:ticket_familypr                        0.636532    
## projectscikit-learn:ticket_familypr                        0.171675    
## projectscipy:ticket_familypr                     0.0000239742006909 ***
## projectsphinx-gallery:ticket_familypr                      0.516605    
## open_time:ticket_familypr                        0.0000000000000516 ***
## comment_sentiment_mean:ticket_familypr                     0.944566    
## comment_sentiment_max_negative:ticket_familypr             0.315308    
## comment_grateful_cumulative:ticket_familypr                0.993993    
## number_of_comments:ticket_familypr                         0.067227 .  
## comment_member_ratio:ticket_familypr             0.0000408215799721 ***
## ---
## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
## 
## (Dispersion parameter for binomial family taken to be 1)
## 
##     Null deviance: 20872  on 16584  degrees of freedom
## Residual deviance: 20172  on 16557  degrees of freedom
##   (870 observations deleted due to missingness)
## AIC: 20228
## 
## Number of Fisher Scoring iterations: 4
```





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
