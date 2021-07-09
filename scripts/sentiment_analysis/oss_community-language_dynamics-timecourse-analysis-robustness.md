---
title: "Temporal communication dynamics in OSS communities: Robustness analyses"
output:
  html_document:
    keep_md: yes
    number_sections: yes
    toc: true
---

This R markdown provides the robustness analysis for our forthcoming manuscript
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
(CNRS)

**Date last compiled**:  2021-07-08 17:20:15



***

# Preliminaries


```r
# clear everything
rm(list=ls())

# load libraries and add new functions
source('./utils/ossc-libraries_and_functions.r')
source("./utils/data-loading-robustness.R")
```

***

# Create robustness datasets

Here, we'll load the data and specify two additional membership cutoffs: 
7 contributions and 10 contributions.


```r
# specify 7-contribution cutoff
tickets_frame_7 = loading_tickets_data(dataset="original", membership_cutoff = 7)
comments_frame_7 = loading_comments_data(dataset="original", membership_cutoff = 7)

# specify 10-contribution cutoff
tickets_frame_10 = loading_tickets_data(dataset="original", membership_cutoff = 10)
comments_frame_10 = loading_comments_data(dataset="original", membership_cutoff = 10)
```

***

# Data analysis: 7-contribution cutoff

***

### Data preparation



```r
sentiment_frame_7 = combine_tickets_and_comments(tickets_frame_7, comments_frame_7)
```

### Model 1.2: Do tickets and comments materially differ in emotion over time?

#### Robustness Model 1.2: 7-contribution cutoff


```r
# create year factor
sentiment_frame_7$year = as.factor(sentiment_frame_7$year)

# specify model
timecourse_compound_emotion_7 = lmer(
  compound_emotion ~ 0 + project:type:author_group:year + (1 | author_name),
  data=sentiment_frame_7,
  REML=FALSE)
```

```
## fixed-effect model matrix is rank deficient so dropping 101 columns / coefficients
```


```r
coefficients_and_se_7 = data.frame(
  summary(timecourse_compound_emotion_7)$coefficients)

row_names = gsub(
  "project", "", gsub(
    "author_group", "", gsub(
      "type", "", row.names(coefficients_and_se_7))))

row_names = gsub(
  "year", "", row_names)

# replace hyphens in project names with periods
row_names = gsub(
  "scikit-", "scikit.", gsub(
    "sphinx-", "sphinx.", row_names))

# convert model estimates to a dataframe
means = coefficients_and_se_7$Estimate
names(means) = row_names

# convert standard error to dataframe
se = coefficients_and_se_7$Std..Error
names(se) = row_names
```


```r
dir.create("results/models", showWarnings=FALSE)
write.table(coefficients_and_se_7,
            file="results/models/model-1.2-7cutoff.tsv",
            sep="\t")
```

#### Robustness Model 1.2 across projects: 7-contribution cutoff


```r
all_project_tests_7 = NA
all_projects = unique(sentiment_frame_7$project)

# We're going to fit the model for each projects, and concatenate the results
# in a dataframe. Then, we'll apply multiple correction and display the
# results
for(project in all_projects){
  sentiment_frame_7$test_group = sentiment_frame_7$project == project
  one_versus_all_emotion = lmer(
    compound_emotion ~ 0 + type:author_group:test_group:year + (1|author_name),
    data=sentiment_frame_7,
    REML=FALSE)
  
  # Clean up mode
  coefficients_and_se_7 = data.frame(
    summary(one_versus_all_emotion)$coefficients)
  row_names = gsub(
    "author_group", "", 
    gsub("type", "",
         gsub("project", "", row.names(coefficients_and_se_7))))
  
  means = coefficients_and_se_7$Estimate
  names(means) = row_names
  se = coefficients_and_se_7$Std..Error
  names(se) = row_names
  
  template_contrasts = c(
    "issue_post:member:test_groupTRUE-issue_post:member:test_groupFALSE",
    "pr_post:member:test_groupTRUE-pr_post:member:test_groupFALSE",
    "issue_reply:member:test_groupTRUE-issue_reply:member:test_groupFALSE",
    "pr_reply:member:test_groupTRUE-pr_reply:member:test_groupFALSE",
    "issue_post:nonmember:test_groupTRUE-issue_post:nonmember:test_groupFALSE",
    "pr_post:nonmember:test_groupTRUE-pr_post:nonmember:test_groupFALSE",
    "issue_reply:nonmember:test_groupTRUE-issue_reply:nonmember:test_groupFALSE",
    "pr_reply:nonmember:test_groupTRUE-pr_reply:nonmember:test_groupFALSE"
  )
  
  # Now, extend this to all years.
  contrasts = c(
    unlist(
      lapply(gsub("-", ":year2009-", template_contrasts),
             function(x) paste(x, ":year2009", sep=""))),
    unlist(
      lapply(gsub("-", ":year2010-", template_contrasts),
             function(x) paste(x, ":year2010", sep=""))),
    unlist(
      lapply(gsub("-", ":year2011-", template_contrasts),
             function(x) paste(x, ":year2011", sep=""))),
    unlist(
      lapply(gsub("-", ":year2012-", template_contrasts),
             function(x) paste(x, ":year2012", sep=""))),
    unlist(
      lapply(gsub("-", ":year2013-", template_contrasts),
             function(x) paste(x, ":year2013", sep=""))),
    unlist(
      lapply(gsub("-", ":year2014-", template_contrasts),
             function(x) paste(x, ":year2014", sep=""))),
    unlist(
      lapply(gsub("-", ":year2015-", template_contrasts),
             function(x) paste(x, ":year2015", sep=""))),
    unlist(
      lapply(gsub("-", ":year2016-", template_contrasts),
             function(x) paste(x, ":year2016", sep=""))),
    unlist(
      lapply(gsub("-", ":year2017-", template_contrasts),
             function(x) paste(x, ":year2017", sep=""))),
    unlist(
      lapply(gsub("-", ":year2018-", template_contrasts),
             function(x) paste(x, ":year2018", sep=""))))
  
  
  one_versus_all_emotion_tests_7 = compute_t_statistics(
    means, se,
    contrasts)
  one_versus_all_emotion_tests_7[, "p_value"] = compute_p_value_from_t_stats(
    one_versus_all_emotion_tests_7$t_stats)
  
  # Add unique identifier based on the project of interest in the table.
  row.names(one_versus_all_emotion_tests_7) = gsub(
    "test_group", project,
    row.names(one_versus_all_emotion_tests_7))
  
  if(is.null(dim(all_project_tests_7))){
    all_project_tests_7 = one_versus_all_emotion_tests_7
  }else{
    all_project_tests_7 = rbind(
      all_project_tests_7, one_versus_all_emotion_tests_7)
  }
}
```

```
## fixed-effect model matrix is rank deficient so dropping 36 columns / coefficients
```

```
## fixed-effect model matrix is rank deficient so dropping 21 columns / coefficients
```

```
## fixed-effect model matrix is rank deficient so dropping 8 columns / coefficients
## fixed-effect model matrix is rank deficient so dropping 8 columns / coefficients
## fixed-effect model matrix is rank deficient so dropping 8 columns / coefficients
```

```
## fixed-effect model matrix is rank deficient so dropping 16 columns / coefficients
```

```
## fixed-effect model matrix is rank deficient so dropping 4 columns / coefficients
```


```r
all_project_tests_7 = all_project_tests_7[!is.na(all_project_tests_7[, "p_value"]), ]
pander_clean_anova(all_project_tests_7, rename_columns=FALSE,
                   display_only_significant=TRUE)
```



|                                                &nbsp;                                                | t_stats | p_value | p_adj  | sig |
|:----------------------------------------------------------------------------------------------------:|:-------:|:-------:|:------:|:---:|
|  **issue_reply:member:sphinx-galleryTRUE:year2017-issue_reply:member:sphinx-galleryFALSE:year2017**  |  3.089  |  0.002  | 0.016  |  *  |
|  **issue_reply:member:sphinx-galleryTRUE:year2018-issue_reply:member:sphinx-galleryFALSE:year2018**  |  3.574  | 0.0004  | 0.004  | **  |
|          **pr_reply:nonmember:mayaviTRUE:year2014-pr_reply:nonmember:mayaviFALSE:year2014**          | -2.724  |  0.006  | 0.039  |  *  |
|       **issue_reply:nonmember:mayaviTRUE:year2017-issue_reply:nonmember:mayaviFALSE:year2017**       | -2.998  |  0.003  |  0.02  |  *  |
|          **issue_reply:member:mayaviTRUE:year2018-issue_reply:member:mayaviFALSE:year2018**          | -3.109  |  0.002  | 0.016  |  *  |
|            **issue_post:member:numpyTRUE:year2012-issue_post:member:numpyFALSE:year2012**            | -3.106  |  0.002  | 0.016  |  *  |
|               **pr_post:member:numpyTRUE:year2012-pr_post:member:numpyFALSE:year2012**               | -3.339  |  0.001  | 0.009  | **  |
|           **issue_reply:member:numpyTRUE:year2012-issue_reply:member:numpyFALSE:year2012**           | -4.219  | 0.0001  |   0    | *** |
|              **pr_reply:member:numpyTRUE:year2012-pr_reply:member:numpyFALSE:year2012**              | -6.221  | 0.0001  | 0.0001 | *** |
|        **issue_reply:nonmember:numpyTRUE:year2012-issue_reply:nonmember:numpyFALSE:year2012**        | -3.192  |  0.001  | 0.013  |  *  |
|           **issue_reply:member:numpyTRUE:year2013-issue_reply:member:numpyFALSE:year2013**           | -3.297  |  0.001  |  0.01  |  *  |
|         **issue_post:nonmember:numpyTRUE:year2013-issue_post:nonmember:numpyFALSE:year2013**         | -2.759  |  0.006  | 0.037  |  *  |
|           **issue_reply:member:numpyTRUE:year2014-issue_reply:member:numpyFALSE:year2014**           | -4.111  | 0.0001  | 0.001  | **  |
|            **issue_post:member:numpyTRUE:year2016-issue_post:member:numpyFALSE:year2016**            | -3.223  |  0.001  | 0.012  |  *  |
|         **issue_post:nonmember:numpyTRUE:year2016-issue_post:nonmember:numpyFALSE:year2016**         | -3.796  | 0.0001  | 0.002  | **  |
|            **issue_post:member:numpyTRUE:year2017-issue_post:member:numpyFALSE:year2017**            |  -2.63  |  0.009  | 0.047  |  *  |
|           **issue_reply:member:numpyTRUE:year2017-issue_reply:member:numpyFALSE:year2017**           | -7.538  | 0.0001  | 0.0001 | *** |
|            **pr_post:nonmember:numpyTRUE:year2017-pr_post:nonmember:numpyFALSE:year2017**            |  -2.71  |  0.007  |  0.04  |  *  |
|           **issue_reply:member:numpyTRUE:year2018-issue_reply:member:numpyFALSE:year2018**           | -3.679  | 0.0002  | 0.003  | **  |
|         **issue_post:nonmember:numpyTRUE:year2018-issue_post:nonmember:numpyFALSE:year2018**         | -4.245  | 0.0001  |   0    | *** |
|        **issue_reply:nonmember:numpyTRUE:year2018-issue_reply:nonmember:numpyFALSE:year2018**        | -3.114  |  0.002  | 0.016  |  *  |
|       **pr_reply:member:scikit-imageTRUE:year2013-pr_reply:member:scikit-imageFALSE:year2013**       |  3.629  | 0.0003  | 0.004  | **  |
|       **pr_reply:member:scikit-imageTRUE:year2015-pr_reply:member:scikit-imageFALSE:year2015**       |  2.945  |  0.003  | 0.023  |  *  |
|     **issue_post:member:scikit-imageTRUE:year2016-issue_post:member:scikit-imageFALSE:year2016**     | -2.755  |  0.006  | 0.037  |  *  |
|     **pr_post:nonmember:scikit-imageTRUE:year2016-pr_post:nonmember:scikit-imageFALSE:year2016**     |  5.356  | 0.0001  | 0.0001 | *** |
|    **issue_reply:member:scikit-imageTRUE:year2017-issue_reply:member:scikit-imageFALSE:year2017**    |  2.63   |  0.009  | 0.047  |  *  |
|       **pr_reply:member:scikit-imageTRUE:year2017-pr_reply:member:scikit-imageFALSE:year2017**       |  3.043  |  0.002  | 0.018  |  *  |
|     **pr_post:nonmember:scikit-imageTRUE:year2017-pr_post:nonmember:scikit-imageFALSE:year2017**     |  8.813  | 0.0001  | 0.0001 | *** |
|    **pr_reply:nonmember:scikit-imageTRUE:year2017-pr_reply:nonmember:scikit-imageFALSE:year2017**    |  4.416  | 0.0001  | 0.0002 | *** |
|        **pr_post:member:scikit-imageTRUE:year2018-pr_post:member:scikit-imageFALSE:year2018**        |  6.594  | 0.0001  | 0.0001 | *** |
|     **pr_post:nonmember:scikit-imageTRUE:year2018-pr_post:nonmember:scikit-imageFALSE:year2018**     |  6.022  | 0.0001  | 0.0001 | *** |
| **issue_reply:nonmember:scikit-imageTRUE:year2018-issue_reply:nonmember:scikit-imageFALSE:year2018** |  3.354  |  0.001  | 0.008  | **  |
|    **pr_reply:nonmember:scikit-imageTRUE:year2018-pr_reply:nonmember:scikit-imageFALSE:year2018**    |  5.701  | 0.0001  | 0.0001 | *** |
|          **pr_post:member:matplotlibTRUE:year2011-pr_post:member:matplotlibFALSE:year2011**          |  -4.37  | 0.0001  | 0.0003 | *** |
|      **issue_reply:member:matplotlibTRUE:year2011-issue_reply:member:matplotlibFALSE:year2011**      | -3.802  | 0.0001  | 0.002  | **  |
|       **issue_post:member:matplotlibTRUE:year2013-issue_post:member:matplotlibFALSE:year2013**       | -3.381  |  0.001  | 0.008  | **  |
|         **pr_reply:member:matplotlibTRUE:year2013-pr_reply:member:matplotlibFALSE:year2013**         | -2.987  |  0.003  | 0.021  |  *  |
|   **issue_reply:nonmember:matplotlibTRUE:year2014-issue_reply:nonmember:matplotlibFALSE:year2014**   | -3.845  | 0.0001  | 0.002  | **  |
|       **issue_post:member:matplotlibTRUE:year2015-issue_post:member:matplotlibFALSE:year2015**       |  2.614  |  0.009  | 0.048  |  *  |
|         **pr_reply:member:matplotlibTRUE:year2015-pr_reply:member:matplotlibFALSE:year2015**         | -4.563  | 0.0001  | 0.0001 | *** |
|    **issue_post:nonmember:matplotlibTRUE:year2015-issue_post:nonmember:matplotlibFALSE:year2015**    |  2.634  |  0.008  | 0.047  |  *  |
|         **pr_reply:member:matplotlibTRUE:year2016-pr_reply:member:matplotlibFALSE:year2016**         | -4.167  | 0.0001  | 0.001  | **  |
|      **pr_reply:nonmember:matplotlibTRUE:year2016-pr_reply:nonmember:matplotlibFALSE:year2016**      | -2.921  |  0.004  | 0.024  |  *  |
|    **issue_post:nonmember:matplotlibTRUE:year2017-issue_post:nonmember:matplotlibFALSE:year2017**    | -2.677  |  0.007  | 0.043  |  *  |
|      **pr_reply:nonmember:matplotlibTRUE:year2017-pr_reply:nonmember:matplotlibFALSE:year2017**      | -3.045  |  0.002  | 0.018  |  *  |
|              **pr_reply:member:scipyTRUE:year2013-pr_reply:member:scipyFALSE:year2013**              |  6.265  | 0.0001  | 0.0001 | *** |
|              **pr_reply:member:scipyTRUE:year2015-pr_reply:member:scipyFALSE:year2015**              |  4.954  | 0.0001  | 0.0001 | *** |
|        **issue_reply:nonmember:scipyTRUE:year2015-issue_reply:nonmember:scipyFALSE:year2015**        |  2.781  |  0.005  | 0.036  |  *  |
|           **pr_reply:nonmember:scipyTRUE:year2015-pr_reply:nonmember:scipyFALSE:year2015**           |  4.295  | 0.0001  | 0.0004 | *** |
|              **pr_reply:member:scipyTRUE:year2016-pr_reply:member:scipyFALSE:year2016**              |  7.445  | 0.0001  | 0.0001 | *** |
|           **pr_reply:nonmember:scipyTRUE:year2016-pr_reply:nonmember:scipyFALSE:year2016**           |  3.073  |  0.002  | 0.016  |  *  |
|            **issue_post:member:scipyTRUE:year2017-issue_post:member:scipyFALSE:year2017**            | -3.924  | 0.0001  | 0.002  | **  |
|              **pr_reply:member:scipyTRUE:year2018-pr_reply:member:scipyFALSE:year2018**              |  3.431  |  0.001  | 0.007  | **  |
|           **pr_reply:nonmember:scipyTRUE:year2018-pr_reply:nonmember:scipyFALSE:year2018**           |  3.388  |  0.001  | 0.008  | **  |
|        **pr_post:member:scikit-learnTRUE:year2011-pr_post:member:scikit-learnFALSE:year2011**        |  5.914  | 0.0001  | 0.0001 | *** |
|        **pr_post:member:scikit-learnTRUE:year2012-pr_post:member:scikit-learnFALSE:year2012**        |  2.748  |  0.006  | 0.037  |  *  |
|    **issue_reply:member:scikit-learnTRUE:year2012-issue_reply:member:scikit-learnFALSE:year2012**    |  3.567  | 0.0004  | 0.004  | **  |
|       **pr_reply:member:scikit-learnTRUE:year2012-pr_reply:member:scikit-learnFALSE:year2012**       |  3.594  | 0.0003  | 0.004  | **  |
|     **pr_post:nonmember:scikit-learnTRUE:year2012-pr_post:nonmember:scikit-learnFALSE:year2012**     |  2.813  |  0.005  | 0.033  |  *  |
|        **pr_post:member:scikit-learnTRUE:year2013-pr_post:member:scikit-learnFALSE:year2013**        |  3.662  | 0.0003  | 0.003  | **  |
|       **pr_reply:member:scikit-learnTRUE:year2013-pr_reply:member:scikit-learnFALSE:year2013**       |  4.932  | 0.0001  | 0.0001 | *** |
|       **pr_reply:member:scikit-learnTRUE:year2014-pr_reply:member:scikit-learnFALSE:year2014**       |  2.873  |  0.004  | 0.028  |  *  |
|    **issue_reply:member:scikit-learnTRUE:year2015-issue_reply:member:scikit-learnFALSE:year2015**    | -3.311  |  0.001  | 0.009  | **  |
|       **pr_reply:member:scikit-learnTRUE:year2015-pr_reply:member:scikit-learnFALSE:year2015**       | -2.702  |  0.007  |  0.04  |  *  |
|        **pr_post:member:scikit-learnTRUE:year2018-pr_post:member:scikit-learnFALSE:year2018**        | -2.899  |  0.004  | 0.026  |  *  |
|     **pr_post:nonmember:scikit-learnTRUE:year2018-pr_post:nonmember:scikit-learnFALSE:year2018**     | -4.675  | 0.0001  | 0.0001 | *** |
| **issue_reply:nonmember:scikit-learnTRUE:year2018-issue_reply:nonmember:scikit-learnFALSE:year2018** |  2.676  |  0.007  | 0.043  |  *  |
|    **pr_reply:nonmember:scikit-learnTRUE:year2018-pr_reply:nonmember:scikit-learnFALSE:year2018**    |  4.017  | 0.0001  | 0.001  | **  |
|        **issue_post:nonmember:pandasTRUE:year2012-issue_post:nonmember:pandasFALSE:year2012**        |  2.646  |  0.008  | 0.046  |  *  |
|       **issue_reply:nonmember:pandasTRUE:year2012-issue_reply:nonmember:pandasFALSE:year2012**       |  2.711  |  0.007  |  0.04  |  *  |
|           **issue_post:member:pandasTRUE:year2013-issue_post:member:pandasFALSE:year2013**           |  3.098  |  0.002  | 0.016  |  *  |
|             **pr_reply:member:pandasTRUE:year2013-pr_reply:member:pandasFALSE:year2013**             | -7.915  | 0.0001  | 0.0001 | *** |
|       **issue_reply:nonmember:pandasTRUE:year2013-issue_reply:nonmember:pandasFALSE:year2013**       |  4.673  | 0.0001  | 0.0001 | *** |
|           **issue_post:member:pandasTRUE:year2014-issue_post:member:pandasFALSE:year2014**           |  2.748  |  0.006  | 0.037  |  *  |
|          **issue_reply:member:pandasTRUE:year2014-issue_reply:member:pandasFALSE:year2014**          |  2.754  |  0.006  | 0.037  |  *  |
|       **issue_reply:nonmember:pandasTRUE:year2014-issue_reply:nonmember:pandasFALSE:year2014**       |  4.639  | 0.0001  | 0.0001 | *** |
|           **issue_post:member:pandasTRUE:year2016-issue_post:member:pandasFALSE:year2016**           |  3.177  |  0.002  | 0.013  |  *  |
|        **issue_post:nonmember:pandasTRUE:year2016-issue_post:nonmember:pandasFALSE:year2016**        |  3.623  | 0.0003  | 0.004  | **  |
|           **pr_post:nonmember:pandasTRUE:year2016-pr_post:nonmember:pandasFALSE:year2016**           | -3.183  |  0.002  | 0.013  |  *  |
|          **pr_reply:nonmember:pandasTRUE:year2016-pr_reply:nonmember:pandasFALSE:year2016**          | -3.307  |  0.001  | 0.009  | **  |
|           **issue_post:member:pandasTRUE:year2017-issue_post:member:pandasFALSE:year2017**           |  3.193  |  0.001  | 0.013  |  *  |
|          **issue_reply:member:pandasTRUE:year2017-issue_reply:member:pandasFALSE:year2017**          |  3.286  |  0.001  |  0.01  |  *  |
|        **issue_post:nonmember:pandasTRUE:year2017-issue_post:nonmember:pandasFALSE:year2017**        |  3.736  | 0.0002  | 0.003  | **  |
|           **pr_post:nonmember:pandasTRUE:year2017-pr_post:nonmember:pandasFALSE:year2017**           | -2.945  |  0.003  | 0.023  |  *  |
|           **issue_post:member:pandasTRUE:year2018-issue_post:member:pandasFALSE:year2018**           |  3.389  |  0.001  | 0.008  | **  |
|        **issue_post:nonmember:pandasTRUE:year2018-issue_post:nonmember:pandasFALSE:year2018**        |  3.832  | 0.0001  | 0.002  | **  |
|           **pr_post:nonmember:pandasTRUE:year2018-pr_post:nonmember:pandasFALSE:year2018**           |  4.539  | 0.0001  | 0.0001 | *** |
|          **pr_reply:nonmember:pandasTRUE:year2018-pr_reply:nonmember:pandasFALSE:year2018**          | -7.929  | 0.0001  | 0.0001 | *** |


```r
all_project_tests_7$p_val_adjusted = p.adjust(all_project_tests_7$p_value, method="BH")
write.table(all_project_tests_7,
            file="results/models/model-timecourse-emotion-pvalues-7cutoff.tsv")
```

### Model 1.4: Do tickets and comments materially differ in gratitude over time?

#### Robustness Model 1.4: 7-contribution cutoff


```r
sentiment_frame_7$year = as.factor(sentiment_frame_7$year)
timecourse_grateful_counts = lmer(
  log(grateful_count + 1) ~ 0 + project:type:author_group:year + (1 | author_name),
  data=sentiment_frame_7,
  REML=FALSE)
```

```
## fixed-effect model matrix is rank deficient so dropping 101 columns / coefficients
```


```r
coefficients_and_se_7 = data.frame(
  summary(timecourse_grateful_counts)$coefficients)

row_names = gsub(
  "project", "", gsub(
    "author_group", "", gsub(
      "type", "", row.names(coefficients_and_se_7))))

row_names = gsub(
  "year", "", row_names)

# replace hyphens in project names with periods
row_names = gsub(
  "scikit-", "scikit.", gsub(
    "sphinx-", "sphinx.", row_names))

# convert model estimates to a dataframe
means = coefficients_and_se_7$Estimate
names(means) = row_names

# convert standard error to dataframe
se = coefficients_and_se_7$Std..Error
names(se) = row_names
```


```r
dir.create("results/models", showWarnings=FALSE)
write.table(coefficients_and_se_7,
            file="results/models/model-1.4-7cutoff.tsv",
            sep="\t")
```

#### Robustness Model 1.4 across projects: 7-contribution cutoff


```r
all_project_tests_7 = NA
all_projects = unique(sentiment_frame_7$project)

# We're going to fit the model for each projects, and concatenate the results
# in a dataframe. Then, we'll apply multiple correction and display the
# results
for(project in all_projects){
  sentiment_frame_7$test_group = sentiment_frame_7$project == project
  one_versus_all_emotion = lmer(
    log(grateful_count + 1) ~ 0 + type:author_group:test_group:year + (1|author_name),
    data=sentiment_frame_7,
    REML=FALSE)
  
  # Clean up mode
  coefficients_and_se_7 = data.frame(
    summary(one_versus_all_emotion)$coefficients)
  row_names = gsub(
    "author_group", "", 
    gsub("type", "",
         gsub("project", "", row.names(coefficients_and_se_7))))
  
  means = coefficients_and_se_7$Estimate
  names(means) = row_names
  se = coefficients_and_se_7$Std..Error
  names(se) = row_names
  
  template_contrasts = c(
    "issue_post:member:test_groupTRUE-issue_post:member:test_groupFALSE",
    "pr_post:member:test_groupTRUE-pr_post:member:test_groupFALSE",
    "issue_reply:member:test_groupTRUE-issue_reply:member:test_groupFALSE",
    "pr_reply:member:test_groupTRUE-pr_reply:member:test_groupFALSE",
    "issue_post:nonmember:test_groupTRUE-issue_post:nonmember:test_groupFALSE",
    "pr_post:nonmember:test_groupTRUE-pr_post:nonmember:test_groupFALSE",
    "issue_reply:nonmember:test_groupTRUE-issue_reply:nonmember:test_groupFALSE",
    "pr_reply:nonmember:test_groupTRUE-pr_reply:nonmember:test_groupFALSE"
  )
  
  # Now, extend this to all years.
  contrasts = c(
    unlist(
      lapply(gsub("-", ":year2009-", template_contrasts),
             function(x) paste(x, ":year2009", sep=""))),
    unlist(
      lapply(gsub("-", ":year2010-", template_contrasts),
             function(x) paste(x, ":year2010", sep=""))),
    unlist(
      lapply(gsub("-", ":year2011-", template_contrasts),
             function(x) paste(x, ":year2011", sep=""))),
    unlist(
      lapply(gsub("-", ":year2012-", template_contrasts),
             function(x) paste(x, ":year2012", sep=""))),
    unlist(
      lapply(gsub("-", ":year2013-", template_contrasts),
             function(x) paste(x, ":year2013", sep=""))),
    unlist(
      lapply(gsub("-", ":year2014-", template_contrasts),
             function(x) paste(x, ":year2014", sep=""))),
    unlist(
      lapply(gsub("-", ":year2015-", template_contrasts),
             function(x) paste(x, ":year2015", sep=""))),
    unlist(
      lapply(gsub("-", ":year2016-", template_contrasts),
             function(x) paste(x, ":year2016", sep=""))),
    unlist(
      lapply(gsub("-", ":year2017-", template_contrasts),
             function(x) paste(x, ":year2017", sep=""))),
    unlist(
      lapply(gsub("-", ":year2018-", template_contrasts),
             function(x) paste(x, ":year2018", sep=""))))
  
  
  one_versus_all_emotion_tests_7 = compute_t_statistics(
    means, se,
    contrasts)
  one_versus_all_emotion_tests_7[, "p_value"] = compute_p_value_from_t_stats(
    one_versus_all_emotion_tests_7$t_stats)
  
  # Add unique identifier based on the project of interest in the table.
  row.names(one_versus_all_emotion_tests_7) = gsub(
    "test_group", project,
    row.names(one_versus_all_emotion_tests_7))
  
  if(is.null(dim(all_project_tests_7))){
    all_project_tests_7 = one_versus_all_emotion_tests_7
  }else{
    all_project_tests_7 = rbind(
      all_project_tests_7, one_versus_all_emotion_tests_7)
  }
}
```

```
## fixed-effect model matrix is rank deficient so dropping 36 columns / coefficients
```

```
## fixed-effect model matrix is rank deficient so dropping 21 columns / coefficients
```

```
## fixed-effect model matrix is rank deficient so dropping 8 columns / coefficients
## fixed-effect model matrix is rank deficient so dropping 8 columns / coefficients
## fixed-effect model matrix is rank deficient so dropping 8 columns / coefficients
```

```
## fixed-effect model matrix is rank deficient so dropping 16 columns / coefficients
```

```
## fixed-effect model matrix is rank deficient so dropping 4 columns / coefficients
```


```r
all_project_tests_7 = all_project_tests_7[!is.na(all_project_tests_7[, "p_value"]), ]
pander_clean_anova(all_project_tests_7, rename_columns=FALSE,
                   display_only_significant=TRUE)
```



|                                                  &nbsp;                                                  | t_stats | p_value | p_adj  | sig |
|:--------------------------------------------------------------------------------------------------------:|:-------:|:-------:|:------:|:---:|
|    **pr_reply:nonmember:sphinx-galleryTRUE:year2015-pr_reply:nonmember:sphinx-galleryFALSE:year2015**    | -2.899  |  0.004  | 0.022  |  *  |
|       **pr_reply:member:sphinx-galleryTRUE:year2017-pr_reply:member:sphinx-galleryFALSE:year2017**       | -3.287  |  0.001  | 0.008  | **  |
|  **issue_post:nonmember:sphinx-galleryTRUE:year2017-issue_post:nonmember:sphinx-galleryFALSE:year2017**  |  3.118  |  0.002  | 0.013  |  *  |
| **issue_reply:nonmember:sphinx-galleryTRUE:year2018-issue_reply:nonmember:sphinx-galleryFALSE:year2018** |  3.316  |  0.001  | 0.008  | **  |
|            **pr_reply:nonmember:mayaviTRUE:year2012-pr_reply:nonmember:mayaviFALSE:year2012**            |  2.874  |  0.004  | 0.023  |  *  |
|            **pr_reply:nonmember:mayaviTRUE:year2013-pr_reply:nonmember:mayaviFALSE:year2013**            |  3.102  |  0.002  | 0.013  |  *  |
|            **issue_reply:member:mayaviTRUE:year2014-issue_reply:member:mayaviFALSE:year2014**            | -3.057  |  0.002  | 0.014  |  *  |
|          **issue_post:nonmember:mayaviTRUE:year2015-issue_post:nonmember:mayaviFALSE:year2015**          |  3.621  | 0.0003  | 0.003  | **  |
|            **issue_reply:member:mayaviTRUE:year2016-issue_reply:member:mayaviFALSE:year2016**            |  3.656  | 0.0003  | 0.003  | **  |
|               **pr_reply:member:mayaviTRUE:year2016-pr_reply:member:mayaviFALSE:year2016**               |  4.272  | 0.0001  | 0.0003 | *** |
|          **issue_post:nonmember:mayaviTRUE:year2016-issue_post:nonmember:mayaviFALSE:year2016**          |  2.848  |  0.004  | 0.024  |  *  |
|         **issue_reply:nonmember:mayaviTRUE:year2016-issue_reply:nonmember:mayaviFALSE:year2016**         |  2.948  |  0.003  |  0.02  |  *  |
|            **pr_reply:nonmember:mayaviTRUE:year2016-pr_reply:nonmember:mayaviFALSE:year2016**            |  2.663  |  0.008  | 0.039  |  *  |
|               **pr_reply:member:mayaviTRUE:year2017-pr_reply:member:mayaviFALSE:year2017**               |  5.098  | 0.0001  | 0.0001 | *** |
|                **pr_post:member:mayaviTRUE:year2018-pr_post:member:mayaviFALSE:year2018**                |  -3.31  |  0.001  | 0.008  | **  |
|            **issue_reply:member:mayaviTRUE:year2018-issue_reply:member:mayaviFALSE:year2018**            | -2.661  |  0.008  | 0.039  |  *  |
|               **pr_reply:member:mayaviTRUE:year2018-pr_reply:member:mayaviFALSE:year2018**               |  3.341  |  0.001  | 0.007  | **  |
|          **issue_post:nonmember:mayaviTRUE:year2018-issue_post:nonmember:mayaviFALSE:year2018**          |  4.456  | 0.0001  | 0.0001 | *** |
|         **issue_reply:nonmember:mayaviTRUE:year2018-issue_reply:nonmember:mayaviFALSE:year2018**         |  6.081  | 0.0001  | 0.0001 | *** |
|                **pr_reply:member:numpyTRUE:year2011-pr_reply:member:numpyFALSE:year2011**                | -5.033  | 0.0001  | 0.0001 | *** |
|                 **pr_post:member:numpyTRUE:year2012-pr_post:member:numpyFALSE:year2012**                 | -2.663  |  0.008  | 0.039  |  *  |
|             **issue_reply:member:numpyTRUE:year2012-issue_reply:member:numpyFALSE:year2012**             | -4.155  | 0.0001  | 0.0004 | *** |
|                **pr_reply:member:numpyTRUE:year2012-pr_reply:member:numpyFALSE:year2012**                | -9.641  | 0.0001  | 0.0001 | *** |
|             **issue_reply:member:numpyTRUE:year2013-issue_reply:member:numpyFALSE:year2013**             | -5.121  | 0.0001  | 0.0001 | *** |
|                **pr_reply:member:numpyTRUE:year2013-pr_reply:member:numpyFALSE:year2013**                | -4.196  | 0.0001  | 0.0004 | *** |
|             **issue_reply:member:numpyTRUE:year2014-issue_reply:member:numpyFALSE:year2014**             | -5.174  | 0.0001  | 0.0001 | *** |
|           **issue_post:nonmember:numpyTRUE:year2014-issue_post:nonmember:numpyFALSE:year2014**           |  -2.63  |  0.009  | 0.042  |  *  |
|                **pr_reply:member:numpyTRUE:year2015-pr_reply:member:numpyFALSE:year2015**                |  2.974  |  0.003  | 0.018  |  *  |
|             **issue_reply:member:numpyTRUE:year2016-issue_reply:member:numpyFALSE:year2016**             | -2.852  |  0.004  | 0.024  |  *  |
|          **issue_reply:nonmember:numpyTRUE:year2016-issue_reply:nonmember:numpyFALSE:year2016**          | -2.857  |  0.004  | 0.024  |  *  |
|             **issue_reply:member:numpyTRUE:year2017-issue_reply:member:numpyFALSE:year2017**             | -4.201  | 0.0001  | 0.0004 | *** |
|                **pr_reply:member:numpyTRUE:year2017-pr_reply:member:numpyFALSE:year2017**                | -5.916  | 0.0001  | 0.0001 | *** |
|             **issue_reply:member:numpyTRUE:year2018-issue_reply:member:numpyFALSE:year2018**             | -2.739  |  0.006  | 0.032  |  *  |
|          **issue_reply:nonmember:numpyTRUE:year2018-issue_reply:nonmember:numpyFALSE:year2018**          |  3.531  | 0.0004  | 0.004  | **  |
|         **pr_reply:member:scikit-imageTRUE:year2011-pr_reply:member:scikit-imageFALSE:year2011**         |  3.549  | 0.0004  | 0.004  | **  |
|   **issue_reply:nonmember:scikit-imageTRUE:year2011-issue_reply:nonmember:scikit-imageFALSE:year2011**   | -2.681  |  0.007  | 0.038  |  *  |
|          **pr_post:member:scikit-imageTRUE:year2012-pr_post:member:scikit-imageFALSE:year2012**          | -3.239  |  0.001  | 0.009  | **  |
|      **pr_reply:nonmember:scikit-imageTRUE:year2012-pr_reply:nonmember:scikit-imageFALSE:year2012**      | -3.535  | 0.0004  | 0.004  | **  |
|         **pr_reply:member:scikit-imageTRUE:year2015-pr_reply:member:scikit-imageFALSE:year2015**         |  2.946  |  0.003  |  0.02  |  *  |
|         **pr_reply:member:scikit-imageTRUE:year2018-pr_reply:member:scikit-imageFALSE:year2018**         |  -5.07  | 0.0001  | 0.0001 | *** |
|         **issue_post:member:matplotlibTRUE:year2011-issue_post:member:matplotlibFALSE:year2011**         |  6.933  | 0.0001  | 0.0001 | *** |
|            **pr_post:member:matplotlibTRUE:year2012-pr_post:member:matplotlibFALSE:year2012**            |  5.625  | 0.0001  | 0.0001 | *** |
|        **pr_reply:nonmember:matplotlibTRUE:year2012-pr_reply:nonmember:matplotlibFALSE:year2012**        |  3.538  | 0.0004  | 0.004  | **  |
|        **issue_reply:member:matplotlibTRUE:year2013-issue_reply:member:matplotlibFALSE:year2013**        |  3.113  |  0.002  | 0.013  |  *  |
|            **pr_post:member:matplotlibTRUE:year2015-pr_post:member:matplotlibFALSE:year2015**            |  2.878  |  0.004  | 0.023  |  *  |
|        **issue_reply:member:matplotlibTRUE:year2015-issue_reply:member:matplotlibFALSE:year2015**        |  3.78   | 0.0002  | 0.002  | **  |
|           **pr_reply:member:matplotlibTRUE:year2015-pr_reply:member:matplotlibFALSE:year2015**           |  -3.25  |  0.001  | 0.009  | **  |
|            **pr_post:member:matplotlibTRUE:year2016-pr_post:member:matplotlibFALSE:year2016**            |  3.833  | 0.0001  | 0.001  | **  |
|        **issue_reply:member:matplotlibTRUE:year2016-issue_reply:member:matplotlibFALSE:year2016**        |  3.306  |  0.001  | 0.008  | **  |
|           **pr_reply:member:matplotlibTRUE:year2016-pr_reply:member:matplotlibFALSE:year2016**           | -2.923  |  0.004  | 0.021  |  *  |
|            **pr_post:member:matplotlibTRUE:year2017-pr_post:member:matplotlibFALSE:year2017**            |  3.378  |  0.001  | 0.006  | **  |
|        **issue_reply:member:matplotlibTRUE:year2017-issue_reply:member:matplotlibFALSE:year2017**        |  3.149  |  0.002  | 0.012  |  *  |
|           **pr_reply:member:matplotlibTRUE:year2017-pr_reply:member:matplotlibFALSE:year2017**           | -3.298  |  0.001  | 0.008  | **  |
|            **pr_post:member:matplotlibTRUE:year2018-pr_post:member:matplotlibFALSE:year2018**            |  3.973  | 0.0001  | 0.001  | **  |
|        **issue_reply:member:matplotlibTRUE:year2018-issue_reply:member:matplotlibFALSE:year2018**        |  4.763  | 0.0001  | 0.0001 | *** |
|           **pr_reply:member:matplotlibTRUE:year2018-pr_reply:member:matplotlibFALSE:year2018**           | -4.642  | 0.0001  | 0.0001 | *** |
|     **issue_reply:nonmember:matplotlibTRUE:year2018-issue_reply:nonmember:matplotlibFALSE:year2018**     |  2.859  |  0.004  | 0.024  |  *  |
|                **pr_reply:member:scipyTRUE:year2013-pr_reply:member:scipyFALSE:year2013**                |  8.964  | 0.0001  | 0.0001 | *** |
|          **issue_reply:nonmember:scipyTRUE:year2013-issue_reply:nonmember:scipyFALSE:year2013**          | -2.595  |  0.009  | 0.046  |  *  |
|                **pr_reply:member:scipyTRUE:year2014-pr_reply:member:scipyFALSE:year2014**                |  3.336  |  0.001  | 0.007  | **  |
|             **pr_reply:nonmember:scipyTRUE:year2014-pr_reply:nonmember:scipyFALSE:year2014**             |  3.468  |    0    | 0.005  | **  |
|                **pr_reply:member:scipyTRUE:year2015-pr_reply:member:scipyFALSE:year2015**                |  3.143  |  0.002  | 0.012  |  *  |
|             **pr_reply:nonmember:scipyTRUE:year2015-pr_reply:nonmember:scipyFALSE:year2015**             |  2.787  |  0.005  | 0.029  |  *  |
|                **pr_reply:member:scipyTRUE:year2016-pr_reply:member:scipyFALSE:year2016**                |  5.986  | 0.0001  | 0.0001 | *** |
|                **pr_reply:member:scipyTRUE:year2017-pr_reply:member:scipyFALSE:year2017**                |  4.898  | 0.0001  | 0.0001 | *** |
|                **pr_reply:member:scipyTRUE:year2018-pr_reply:member:scipyFALSE:year2018**                |  7.779  | 0.0001  | 0.0001 | *** |
|      **issue_reply:member:scikit-learnTRUE:year2012-issue_reply:member:scikit-learnFALSE:year2012**      |  4.92   | 0.0001  | 0.0001 | *** |
|         **pr_reply:member:scikit-learnTRUE:year2012-pr_reply:member:scikit-learnFALSE:year2012**         |  3.08   |  0.002  | 0.013  |  *  |
|      **issue_reply:member:scikit-learnTRUE:year2013-issue_reply:member:scikit-learnFALSE:year2013**      |  3.118  |  0.002  | 0.013  |  *  |
|         **pr_reply:member:scikit-learnTRUE:year2013-pr_reply:member:scikit-learnFALSE:year2013**         |  4.466  | 0.0001  | 0.0001 | *** |
|         **pr_reply:member:scikit-learnTRUE:year2015-pr_reply:member:scikit-learnFALSE:year2015**         | -3.258  |  0.001  | 0.009  | **  |
|    **issue_post:nonmember:scikit-learnTRUE:year2015-issue_post:nonmember:scikit-learnFALSE:year2015**    |  3.723  | 0.0002  | 0.002  | **  |
|   **issue_reply:nonmember:scikit-learnTRUE:year2016-issue_reply:nonmember:scikit-learnFALSE:year2016**   | -3.243  |  0.001  | 0.009  | **  |
|          **pr_post:member:scikit-learnTRUE:year2017-pr_post:member:scikit-learnFALSE:year2017**          | -3.078  |  0.002  | 0.013  |  *  |
|       **issue_post:member:scikit-learnTRUE:year2018-issue_post:member:scikit-learnFALSE:year2018**       | -2.731  |  0.006  | 0.033  |  *  |
|          **pr_post:member:scikit-learnTRUE:year2018-pr_post:member:scikit-learnFALSE:year2018**          | -4.769  | 0.0001  | 0.0001 | *** |
|      **issue_reply:member:scikit-learnTRUE:year2018-issue_reply:member:scikit-learnFALSE:year2018**      | -5.456  | 0.0001  | 0.0001 | *** |
|         **pr_reply:member:scikit-learnTRUE:year2018-pr_reply:member:scikit-learnFALSE:year2018**         | -11.18  | 0.0001  | 0.0001 | *** |
|   **issue_reply:nonmember:scikit-learnTRUE:year2018-issue_reply:nonmember:scikit-learnFALSE:year2018**   | -4.702  | 0.0001  | 0.0001 | *** |
|      **pr_reply:nonmember:scikit-learnTRUE:year2018-pr_reply:nonmember:scikit-learnFALSE:year2018**      | -4.674  | 0.0001  | 0.0001 | *** |
|             **issue_post:member:pandasTRUE:year2011-issue_post:member:pandasFALSE:year2011**             | -4.304  | 0.0001  | 0.0002 | *** |
|               **pr_reply:member:pandasTRUE:year2011-pr_reply:member:pandasFALSE:year2011**               |  8.243  | 0.0001  | 0.0001 | *** |
|         **issue_reply:nonmember:pandasTRUE:year2011-issue_reply:nonmember:pandasFALSE:year2011**         |  3.979  | 0.0001  | 0.001  | **  |
|             **issue_post:member:pandasTRUE:year2012-issue_post:member:pandasFALSE:year2012**             | -4.432  | 0.0001  | 0.0001 | *** |
|                **pr_post:member:pandasTRUE:year2012-pr_post:member:pandasFALSE:year2012**                | -2.618  |  0.009  | 0.043  |  *  |
|            **issue_reply:member:pandasTRUE:year2012-issue_reply:member:pandasFALSE:year2012**            | -3.853  | 0.0001  | 0.001  | **  |
|               **pr_reply:member:pandasTRUE:year2012-pr_reply:member:pandasFALSE:year2012**               |  7.171  | 0.0001  | 0.0001 | *** |
|         **issue_reply:nonmember:pandasTRUE:year2012-issue_reply:nonmember:pandasFALSE:year2012**         |  3.303  |  0.001  | 0.008  | **  |
|               **pr_reply:member:pandasTRUE:year2013-pr_reply:member:pandasFALSE:year2013**               | -7.363  | 0.0001  | 0.0001 | *** |
|         **issue_reply:nonmember:pandasTRUE:year2013-issue_reply:nonmember:pandasFALSE:year2013**         |  4.572  | 0.0001  | 0.0001 | *** |
|         **issue_reply:nonmember:pandasTRUE:year2014-issue_reply:nonmember:pandasFALSE:year2014**         |  3.082  |  0.002  | 0.013  |  *  |
|          **issue_post:nonmember:pandasTRUE:year2016-issue_post:nonmember:pandasFALSE:year2016**          | -4.075  | 0.0001  | 0.001  | **  |
|            **pr_reply:nonmember:pandasTRUE:year2016-pr_reply:nonmember:pandasFALSE:year2016**            | -2.758  |  0.006  | 0.031  |  *  |
|               **pr_reply:member:pandasTRUE:year2017-pr_reply:member:pandasFALSE:year2017**               |  5.13   | 0.0001  | 0.0001 | *** |
|          **issue_post:nonmember:pandasTRUE:year2017-issue_post:nonmember:pandasFALSE:year2017**          | -3.694  | 0.0002  | 0.002  | **  |
|               **pr_reply:member:pandasTRUE:year2018-pr_reply:member:pandasFALSE:year2018**               |  10.8   | 0.0001  | 0.0001 | *** |
|          **issue_post:nonmember:pandasTRUE:year2018-issue_post:nonmember:pandasFALSE:year2018**          |  -2.92  |  0.004  | 0.021  |  *  |
|         **issue_reply:nonmember:pandasTRUE:year2018-issue_reply:nonmember:pandasFALSE:year2018**         | -5.551  | 0.0001  | 0.0001 | *** |


```r
all_project_tests_7$p_val_adjusted = p.adjust(all_project_tests_7$p_value, method="BH")
write.table(all_project_tests_7,
            file="results/models/model-timecourse-gratitude-pvalues-7cutoff.tsv")
```

***

# Data analysis: 10-contribution cutoff

***

### Data preparation



```r
sentiment_frame_10 = combine_tickets_and_comments(tickets_frame_10, comments_frame_10)
```

### Model 1.2: Do tickets and comments materially differ in emotion over time?

#### Robustness Model 1.2: 10-contribution cutoff


```r
# create year factor
sentiment_frame_10$year = as.factor(sentiment_frame_10$year)

# specify model
timecourse_compound_emotion_10 = lmer(
  compound_emotion ~ 0 + project:type:author_group:year + (1 | author_name),
  data=sentiment_frame_10,
  REML=FALSE)
```

```
## fixed-effect model matrix is rank deficient so dropping 104 columns / coefficients
```


```r
coefficients_and_se_10 = data.frame(
  summary(timecourse_compound_emotion_10)$coefficients)

row_names = gsub(
  "project", "", gsub(
    "author_group", "", gsub(
      "type", "", row.names(coefficients_and_se_10))))

row_names = gsub(
  "year", "", row_names)

# replace hyphens in project names with periods
row_names = gsub(
  "scikit-", "scikit.", gsub(
    "sphinx-", "sphinx.", row_names))

# convert model estimates to a dataframe
means = coefficients_and_se_10$Estimate
names(means) = row_names

# convert standard error to dataframe
se = coefficients_and_se_10$Std..Error
names(se) = row_names
```


```r
dir.create("results/models", showWarnings=FALSE)
write.table(coefficients_and_se_10,
            file="results/models/model-1.2-10cutoff.tsv",
            sep="\t")
```

#### Robustness Model 1.2 across projects: 10-contribution cutoff


```r
all_project_tests_10 = NA
all_projects = unique(sentiment_frame_10$project)

# We're going to fit the model for each projects, and concatenate the results
# in a dataframe. Then, we'll apply multiple correction and display the
# results
for(project in all_projects){
  sentiment_frame_10$test_group = sentiment_frame_10$project == project
  one_versus_all_emotion = lmer(
    compound_emotion ~ 0 + type:author_group:test_group:year + (1|author_name),
    data=sentiment_frame_10,
    REML=FALSE)
  
  # Clean up mode
  coefficients_and_se_10 = data.frame(
    summary(one_versus_all_emotion)$coefficients)
  row_names = gsub(
    "author_group", "", 
    gsub("type", "",
         gsub("project", "", row.names(coefficients_and_se_10))))
  
  means = coefficients_and_se_10$Estimate
  names(means) = row_names
  se = coefficients_and_se_10$Std..Error
  names(se) = row_names
  
  template_contrasts = c(
    "issue_post:member:test_groupTRUE-issue_post:member:test_groupFALSE",
    "pr_post:member:test_groupTRUE-pr_post:member:test_groupFALSE",
    "issue_reply:member:test_groupTRUE-issue_reply:member:test_groupFALSE",
    "pr_reply:member:test_groupTRUE-pr_reply:member:test_groupFALSE",
    "issue_post:nonmember:test_groupTRUE-issue_post:nonmember:test_groupFALSE",
    "pr_post:nonmember:test_groupTRUE-pr_post:nonmember:test_groupFALSE",
    "issue_reply:nonmember:test_groupTRUE-issue_reply:nonmember:test_groupFALSE",
    "pr_reply:nonmember:test_groupTRUE-pr_reply:nonmember:test_groupFALSE"
  )
  
  # Now, extend this to all years.
  contrasts = c(
    unlist(
      lapply(gsub("-", ":year2009-", template_contrasts),
             function(x) paste(x, ":year2009", sep=""))),
    unlist(
      lapply(gsub("-", ":year2010-", template_contrasts),
             function(x) paste(x, ":year2010", sep=""))),
    unlist(
      lapply(gsub("-", ":year2011-", template_contrasts),
             function(x) paste(x, ":year2011", sep=""))),
    unlist(
      lapply(gsub("-", ":year2012-", template_contrasts),
             function(x) paste(x, ":year2012", sep=""))),
    unlist(
      lapply(gsub("-", ":year2013-", template_contrasts),
             function(x) paste(x, ":year2013", sep=""))),
    unlist(
      lapply(gsub("-", ":year2014-", template_contrasts),
             function(x) paste(x, ":year2014", sep=""))),
    unlist(
      lapply(gsub("-", ":year2015-", template_contrasts),
             function(x) paste(x, ":year2015", sep=""))),
    unlist(
      lapply(gsub("-", ":year2016-", template_contrasts),
             function(x) paste(x, ":year2016", sep=""))),
    unlist(
      lapply(gsub("-", ":year20110-", template_contrasts),
             function(x) paste(x, ":year2017", sep=""))),
    unlist(
      lapply(gsub("-", ":year2018-", template_contrasts),
             function(x) paste(x, ":year2018", sep=""))))
  
  
  one_versus_all_emotion_tests_10 = compute_t_statistics(
    means, se,
    contrasts)
  one_versus_all_emotion_tests_10[, "p_value"] = compute_p_value_from_t_stats(
    one_versus_all_emotion_tests_10$t_stats)
  
  # Add unique identifier based on the project of interest in the table.
  row.names(one_versus_all_emotion_tests_10) = gsub(
    "test_group", project,
    row.names(one_versus_all_emotion_tests_10))
  
  if(is.null(dim(all_project_tests_10))){
    all_project_tests_10 = one_versus_all_emotion_tests_10
  }else{
    all_project_tests_10 = rbind(
      all_project_tests_10, one_versus_all_emotion_tests_10)
  }
}
```

```
## fixed-effect model matrix is rank deficient so dropping 37 columns / coefficients
```

```
## fixed-effect model matrix is rank deficient so dropping 22 columns / coefficients
```

```
## fixed-effect model matrix is rank deficient so dropping 11 columns / coefficients
```

```
## fixed-effect model matrix is rank deficient so dropping 9 columns / coefficients
## fixed-effect model matrix is rank deficient so dropping 9 columns / coefficients
```

```
## fixed-effect model matrix is rank deficient so dropping 17 columns / coefficients
```

```
## fixed-effect model matrix is rank deficient so dropping 3 columns / coefficients
```

```
## fixed-effect model matrix is rank deficient so dropping 5 columns / coefficients
```


```r
all_project_tests_10 = all_project_tests_10[!is.na(all_project_tests_10[, "p_value"]), ]
pander_clean_anova(all_project_tests_10, rename_columns=FALSE,
                   display_only_significant=TRUE)
```



|                                                &nbsp;                                                | t_stats | p_value | p_adj  | sig |
|:----------------------------------------------------------------------------------------------------:|:-------:|:-------:|:------:|:---:|
|  **issue_reply:member:sphinx-galleryTRUE:year2018-issue_reply:member:sphinx-galleryFALSE:year2018**  |  3.685  | 0.0002  | 0.003  | **  |
|          **pr_reply:nonmember:mayaviTRUE:year2014-pr_reply:nonmember:mayaviFALSE:year2014**          | -2.831  |  0.005  | 0.036  |  *  |
|               **pr_post:member:numpyTRUE:year2012-pr_post:member:numpyFALSE:year2012**               | -3.861  | 0.0001  | 0.002  | **  |
|           **issue_reply:member:numpyTRUE:year2012-issue_reply:member:numpyFALSE:year2012**           | -3.763  | 0.0002  | 0.002  | **  |
|              **pr_reply:member:numpyTRUE:year2012-pr_reply:member:numpyFALSE:year2012**              | -5.774  | 0.0001  | 0.0001 | *** |
|         **issue_post:nonmember:numpyTRUE:year2012-issue_post:nonmember:numpyFALSE:year2012**         | -2.698  |  0.007  | 0.047  |  *  |
|        **issue_reply:nonmember:numpyTRUE:year2012-issue_reply:nonmember:numpyFALSE:year2012**        | -3.734  | 0.0002  | 0.002  | **  |
|           **issue_reply:member:numpyTRUE:year2013-issue_reply:member:numpyFALSE:year2013**           |  -3.06  |  0.002  | 0.019  |  *  |
|         **issue_post:nonmember:numpyTRUE:year2013-issue_post:nonmember:numpyFALSE:year2013**         | -2.841  |  0.004  | 0.035  |  *  |
|           **issue_reply:member:numpyTRUE:year2014-issue_reply:member:numpyFALSE:year2014**           | -4.091  | 0.0001  | 0.001  | **  |
|         **issue_post:nonmember:numpyTRUE:year2016-issue_post:nonmember:numpyFALSE:year2016**         |  -4.43  | 0.0001  | 0.0002 | *** |
|           **issue_reply:member:numpyTRUE:year2018-issue_reply:member:numpyFALSE:year2018**           | -3.294  |  0.001  | 0.009  | **  |
|         **issue_post:nonmember:numpyTRUE:year2018-issue_post:nonmember:numpyFALSE:year2018**         | -4.509  | 0.0001  | 0.0002 | *** |
|        **issue_reply:nonmember:numpyTRUE:year2018-issue_reply:nonmember:numpyFALSE:year2018**        | -3.571  | 0.0004  | 0.004  | **  |
|       **pr_reply:member:scikit-imageTRUE:year2013-pr_reply:member:scikit-imageFALSE:year2013**       |  3.872  | 0.0001  | 0.002  | **  |
|     **pr_post:nonmember:scikit-imageTRUE:year2013-pr_post:nonmember:scikit-imageFALSE:year2013**     |  2.814  |  0.005  | 0.037  |  *  |
|       **pr_reply:member:scikit-imageTRUE:year2015-pr_reply:member:scikit-imageFALSE:year2015**       |  3.046  |  0.002  | 0.019  |  *  |
|     **issue_post:member:scikit-imageTRUE:year2016-issue_post:member:scikit-imageFALSE:year2016**     |  -2.86  |  0.004  | 0.034  |  *  |
|     **pr_post:nonmember:scikit-imageTRUE:year2016-pr_post:nonmember:scikit-imageFALSE:year2016**     |  5.158  | 0.0001  | 0.0001 | *** |
|        **pr_post:member:scikit-imageTRUE:year2018-pr_post:member:scikit-imageFALSE:year2018**        |  6.134  | 0.0001  | 0.0001 | *** |
|     **pr_post:nonmember:scikit-imageTRUE:year2018-pr_post:nonmember:scikit-imageFALSE:year2018**     |  6.527  | 0.0001  | 0.0001 | *** |
| **issue_reply:nonmember:scikit-imageTRUE:year2018-issue_reply:nonmember:scikit-imageFALSE:year2018** |  3.779  | 0.0002  | 0.002  | **  |
|    **pr_reply:nonmember:scikit-imageTRUE:year2018-pr_reply:nonmember:scikit-imageFALSE:year2018**    |  6.319  | 0.0001  | 0.0001 | *** |
|          **pr_post:member:matplotlibTRUE:year2011-pr_post:member:matplotlibFALSE:year2011**          | -3.942  | 0.0001  | 0.001  | **  |
|      **issue_reply:member:matplotlibTRUE:year2011-issue_reply:member:matplotlibFALSE:year2011**      | -3.255  |  0.001  |  0.01  |  *  |
|   **issue_reply:nonmember:matplotlibTRUE:year2014-issue_reply:nonmember:matplotlibFALSE:year2014**   | -3.936  | 0.0001  | 0.001  | **  |
|       **issue_post:member:matplotlibTRUE:year2015-issue_post:member:matplotlibFALSE:year2015**       |  2.859  |  0.004  | 0.034  |  *  |
|         **pr_reply:member:matplotlibTRUE:year2015-pr_reply:member:matplotlibFALSE:year2015**         | -4.477  | 0.0001  | 0.0002 | *** |
|         **pr_reply:member:matplotlibTRUE:year2016-pr_reply:member:matplotlibFALSE:year2016**         | -3.903  | 0.0001  | 0.001  | **  |
|      **pr_reply:nonmember:matplotlibTRUE:year2016-pr_reply:nonmember:matplotlibFALSE:year2016**      | -3.812  | 0.0001  | 0.002  | **  |
|              **pr_reply:member:scipyTRUE:year2013-pr_reply:member:scipyFALSE:year2013**              |  6.135  | 0.0001  | 0.0001 | *** |
|              **pr_reply:member:scipyTRUE:year2015-pr_reply:member:scipyFALSE:year2015**              |  4.751  | 0.0001  | 0.0001 | *** |
|        **issue_reply:nonmember:scipyTRUE:year2015-issue_reply:nonmember:scipyFALSE:year2015**        |  3.191  |  0.001  | 0.012  |  *  |
|           **pr_reply:nonmember:scipyTRUE:year2015-pr_reply:nonmember:scipyFALSE:year2015**           |  4.688  | 0.0001  | 0.0001 | *** |
|              **pr_reply:member:scipyTRUE:year2016-pr_reply:member:scipyFALSE:year2016**              |  7.321  | 0.0001  | 0.0001 | *** |
|           **pr_reply:nonmember:scipyTRUE:year2016-pr_reply:nonmember:scipyFALSE:year2016**           |  3.592  | 0.0003  | 0.004  | **  |
|              **pr_reply:member:scipyTRUE:year2018-pr_reply:member:scipyFALSE:year2018**              |  3.446  |  0.001  | 0.005  | **  |
|           **pr_reply:nonmember:scipyTRUE:year2018-pr_reply:nonmember:scipyFALSE:year2018**           |  3.479  |    0    | 0.005  | **  |
|        **pr_post:member:scikit-learnTRUE:year2011-pr_post:member:scikit-learnFALSE:year2011**        |  5.204  | 0.0001  | 0.0001 | *** |
|        **pr_post:member:scikit-learnTRUE:year2012-pr_post:member:scikit-learnFALSE:year2012**        |  2.724  |  0.006  | 0.044  |  *  |
|    **issue_reply:member:scikit-learnTRUE:year2012-issue_reply:member:scikit-learnFALSE:year2012**    |  3.51   | 0.0004  | 0.005  | **  |
|       **pr_reply:member:scikit-learnTRUE:year2012-pr_reply:member:scikit-learnFALSE:year2012**       |  3.322  |  0.001  | 0.008  | **  |
|        **pr_post:member:scikit-learnTRUE:year2013-pr_post:member:scikit-learnFALSE:year2013**        |  3.444  |  0.001  | 0.005  | **  |
|       **pr_reply:member:scikit-learnTRUE:year2013-pr_reply:member:scikit-learnFALSE:year2013**       |  4.529  | 0.0001  | 0.0002 | *** |
|    **issue_reply:member:scikit-learnTRUE:year2015-issue_reply:member:scikit-learnFALSE:year2015**    | -3.485  |    0    | 0.005  | **  |
|       **pr_reply:member:scikit-learnTRUE:year2015-pr_reply:member:scikit-learnFALSE:year2015**       |  -2.8   |  0.005  | 0.037  |  *  |
|        **pr_post:member:scikit-learnTRUE:year2018-pr_post:member:scikit-learnFALSE:year2018**        | -2.803  |  0.005  | 0.037  |  *  |
|     **pr_post:nonmember:scikit-learnTRUE:year2018-pr_post:nonmember:scikit-learnFALSE:year2018**     | -4.746  | 0.0001  | 0.0001 | *** |
|    **pr_reply:nonmember:scikit-learnTRUE:year2018-pr_reply:nonmember:scikit-learnFALSE:year2018**    |  4.309  | 0.0001  | 0.0003 | *** |
|        **issue_post:nonmember:pandasTRUE:year2012-issue_post:nonmember:pandasFALSE:year2012**        |  2.727  |  0.006  | 0.044  |  *  |
|       **issue_reply:nonmember:pandasTRUE:year2012-issue_reply:nonmember:pandasFALSE:year2012**       |  2.749  |  0.006  | 0.043  |  *  |
|             **pr_reply:member:pandasTRUE:year2013-pr_reply:member:pandasFALSE:year2013**             | -8.174  | 0.0001  | 0.0001 | *** |
|       **issue_reply:nonmember:pandasTRUE:year2013-issue_reply:nonmember:pandasFALSE:year2013**       |  4.458  | 0.0001  | 0.0002 | *** |
|       **issue_reply:nonmember:pandasTRUE:year2014-issue_reply:nonmember:pandasFALSE:year2014**       |  4.869  | 0.0001  | 0.0001 | *** |
|        **issue_post:nonmember:pandasTRUE:year2016-issue_post:nonmember:pandasFALSE:year2016**        |  4.151  | 0.0001  | 0.001  | **  |
|           **pr_post:nonmember:pandasTRUE:year2016-pr_post:nonmember:pandasFALSE:year2016**           |  -3.64  | 0.0003  | 0.003  | **  |
|          **pr_reply:nonmember:pandasTRUE:year2016-pr_reply:nonmember:pandasFALSE:year2016**          | -3.881  | 0.0001  | 0.002  | **  |
|        **issue_post:nonmember:pandasTRUE:year2018-issue_post:nonmember:pandasFALSE:year2018**        |  4.257  | 0.0001  | 0.0004 | *** |
|           **pr_post:nonmember:pandasTRUE:year2018-pr_post:nonmember:pandasFALSE:year2018**           |  4.156  | 0.0001  | 0.001  | **  |
|          **pr_reply:nonmember:pandasTRUE:year2018-pr_reply:nonmember:pandasFALSE:year2018**          | -8.912  | 0.0001  | 0.0001 | *** |


```r
all_project_tests_10$p_val_adjusted = p.adjust(all_project_tests_10$p_value, method="BH")
write.table(all_project_tests_10,
            file="results/models/model-timecourse-emotion-pvalues-10cutoff.tsv")
```

### Model 1.4: Do tickets and comments materially differ in gratitude over time?

#### Robustness Model 1.4: 10-contribution cutoff


```r
sentiment_frame_10$year = as.factor(sentiment_frame_10$year)
timecourse_grateful_counts = lmer(
  log(grateful_count + 1) ~ 0 + project:type:author_group:year + (1 | author_name),
  data=sentiment_frame_10,
  REML=FALSE)
```

```
## fixed-effect model matrix is rank deficient so dropping 104 columns / coefficients
```


```r
coefficients_and_se_10 = data.frame(
  summary(timecourse_grateful_counts)$coefficients)

row_names = gsub(
  "project", "", gsub(
    "author_group", "", gsub(
      "type", "", row.names(coefficients_and_se_10))))

row_names = gsub(
  "year", "", row_names)

# replace hyphens in project names with periods
row_names = gsub(
  "scikit-", "scikit.", gsub(
    "sphinx-", "sphinx.", row_names))

# convert model estimates to a dataframe
means = coefficients_and_se_10$Estimate
names(means) = row_names

# convert standard error to dataframe
se = coefficients_and_se_10$Std..Error
names(se) = row_names
```


```r
dir.create("results/models", showWarnings=FALSE)
write.table(coefficients_and_se_10,
            file="results/models/model-1.4-10cutoff.tsv",
            sep="\t")
```

#### Robustness Model 1.4 across projects: 10-contribution cutoff


```r
all_project_tests_10 = NA
all_projects = unique(sentiment_frame_10$project)

# We're going to fit the model for each projects, and concatenate the results
# in a dataframe. Then, we'll apply multiple correction and display the
# results
for(project in all_projects){
  sentiment_frame_10$test_group = sentiment_frame_10$project == project
  one_versus_all_emotion = lmer(
    log(grateful_count + 1) ~ 0 + type:author_group:test_group:year + (1|author_name),
    data=sentiment_frame_10,
    REML=FALSE)
  
  # Clean up mode
  coefficients_and_se_10 = data.frame(
    summary(one_versus_all_emotion)$coefficients)
  row_names = gsub(
    "author_group", "", 
    gsub("type", "",
         gsub("project", "", row.names(coefficients_and_se_10))))
  
  means = coefficients_and_se_10$Estimate
  names(means) = row_names
  se = coefficients_and_se_10$Std..Error
  names(se) = row_names
  
  template_contrasts = c(
    "issue_post:member:test_groupTRUE-issue_post:member:test_groupFALSE",
    "pr_post:member:test_groupTRUE-pr_post:member:test_groupFALSE",
    "issue_reply:member:test_groupTRUE-issue_reply:member:test_groupFALSE",
    "pr_reply:member:test_groupTRUE-pr_reply:member:test_groupFALSE",
    "issue_post:nonmember:test_groupTRUE-issue_post:nonmember:test_groupFALSE",
    "pr_post:nonmember:test_groupTRUE-pr_post:nonmember:test_groupFALSE",
    "issue_reply:nonmember:test_groupTRUE-issue_reply:nonmember:test_groupFALSE",
    "pr_reply:nonmember:test_groupTRUE-pr_reply:nonmember:test_groupFALSE"
  )
  
  # Now, extend this to all years.
  contrasts = c(
    unlist(
      lapply(gsub("-", ":year2009-", template_contrasts),
             function(x) paste(x, ":year2009", sep=""))),
    unlist(
      lapply(gsub("-", ":year2010-", template_contrasts),
             function(x) paste(x, ":year2010", sep=""))),
    unlist(
      lapply(gsub("-", ":year2011-", template_contrasts),
             function(x) paste(x, ":year2011", sep=""))),
    unlist(
      lapply(gsub("-", ":year2012-", template_contrasts),
             function(x) paste(x, ":year2012", sep=""))),
    unlist(
      lapply(gsub("-", ":year2013-", template_contrasts),
             function(x) paste(x, ":year2013", sep=""))),
    unlist(
      lapply(gsub("-", ":year2014-", template_contrasts),
             function(x) paste(x, ":year2014", sep=""))),
    unlist(
      lapply(gsub("-", ":year2015-", template_contrasts),
             function(x) paste(x, ":year2015", sep=""))),
    unlist(
      lapply(gsub("-", ":year2016-", template_contrasts),
             function(x) paste(x, ":year2016", sep=""))),
    unlist(
      lapply(gsub("-", ":year20110-", template_contrasts),
             function(x) paste(x, ":year2017", sep=""))),
    unlist(
      lapply(gsub("-", ":year2018-", template_contrasts),
             function(x) paste(x, ":year2018", sep=""))))
  
  
  one_versus_all_emotion_tests_10 = compute_t_statistics(
    means, se,
    contrasts)
  one_versus_all_emotion_tests_10[, "p_value"] = compute_p_value_from_t_stats(
    one_versus_all_emotion_tests_10$t_stats)
  
  # Add unique identifier based on the project of interest in the table.
  row.names(one_versus_all_emotion_tests_10) = gsub(
    "test_group", project,
    row.names(one_versus_all_emotion_tests_10))
  
  if(is.null(dim(all_project_tests_10))){
    all_project_tests_10 = one_versus_all_emotion_tests_10
  }else{
    all_project_tests_10 = rbind(
      all_project_tests_10, one_versus_all_emotion_tests_10)
  }
}
```

```
## fixed-effect model matrix is rank deficient so dropping 37 columns / coefficients
```

```
## fixed-effect model matrix is rank deficient so dropping 22 columns / coefficients
```

```
## fixed-effect model matrix is rank deficient so dropping 11 columns / coefficients
```

```
## fixed-effect model matrix is rank deficient so dropping 9 columns / coefficients
## fixed-effect model matrix is rank deficient so dropping 9 columns / coefficients
```

```
## fixed-effect model matrix is rank deficient so dropping 17 columns / coefficients
```

```
## fixed-effect model matrix is rank deficient so dropping 3 columns / coefficients
```

```
## fixed-effect model matrix is rank deficient so dropping 5 columns / coefficients
```


```r
all_project_tests_10 = all_project_tests_10[!is.na(all_project_tests_10[, "p_value"]), ]
pander_clean_anova(all_project_tests_10, rename_columns=FALSE,
                   display_only_significant=TRUE)
```



|                                                  &nbsp;                                                  | t_stats | p_value | p_adj  | sig |
|:--------------------------------------------------------------------------------------------------------:|:-------:|:-------:|:------:|:---:|
|       **pr_reply:member:sphinx-galleryTRUE:year2015-pr_reply:member:sphinx-galleryFALSE:year2015**       |  -2.65  |  0.008  | 0.037  |  *  |
| **issue_reply:nonmember:sphinx-galleryTRUE:year2015-issue_reply:nonmember:sphinx-galleryFALSE:year2015** | -2.647  |  0.008  | 0.037  |  *  |
|    **pr_reply:nonmember:sphinx-galleryTRUE:year2015-pr_reply:nonmember:sphinx-galleryFALSE:year2015**    | -2.561  |  0.01   | 0.045  |  *  |
| **issue_reply:nonmember:sphinx-galleryTRUE:year2018-issue_reply:nonmember:sphinx-galleryFALSE:year2018** |  3.467  |    0    | 0.004  | **  |
|            **pr_reply:nonmember:mayaviTRUE:year2012-pr_reply:nonmember:mayaviFALSE:year2012**            |  2.99   |  0.003  | 0.016  |  *  |
|            **pr_reply:nonmember:mayaviTRUE:year2013-pr_reply:nonmember:mayaviFALSE:year2013**            |  3.236  |  0.001  | 0.008  | **  |
|            **issue_reply:member:mayaviTRUE:year2014-issue_reply:member:mayaviFALSE:year2014**            | -3.224  |  0.001  | 0.008  | **  |
|          **issue_post:nonmember:mayaviTRUE:year2015-issue_post:nonmember:mayaviFALSE:year2015**          |  3.628  | 0.0003  | 0.003  | **  |
|            **issue_reply:member:mayaviTRUE:year2016-issue_reply:member:mayaviFALSE:year2016**            |  3.634  | 0.0003  | 0.003  | **  |
|               **pr_reply:member:mayaviTRUE:year2016-pr_reply:member:mayaviFALSE:year2016**               |  4.137  | 0.0001  | 0.0004 | *** |
|          **issue_post:nonmember:mayaviTRUE:year2016-issue_post:nonmember:mayaviFALSE:year2016**          |  2.881  |  0.004  | 0.021  |  *  |
|         **issue_reply:nonmember:mayaviTRUE:year2016-issue_reply:nonmember:mayaviFALSE:year2016**         |  3.311  |  0.001  | 0.007  | **  |
|            **pr_reply:nonmember:mayaviTRUE:year2016-pr_reply:nonmember:mayaviFALSE:year2016**            |  3.476  |    0    | 0.004  | **  |
|                **pr_post:member:mayaviTRUE:year2018-pr_post:member:mayaviFALSE:year2018**                | -3.442  |  0.001  | 0.004  | **  |
|            **issue_reply:member:mayaviTRUE:year2018-issue_reply:member:mayaviFALSE:year2018**            | -2.746  |  0.006  | 0.029  |  *  |
|               **pr_reply:member:mayaviTRUE:year2018-pr_reply:member:mayaviFALSE:year2018**               |  3.295  |  0.001  | 0.007  | **  |
|          **issue_post:nonmember:mayaviTRUE:year2018-issue_post:nonmember:mayaviFALSE:year2018**          |  4.376  | 0.0001  | 0.0002 | *** |
|         **issue_reply:nonmember:mayaviTRUE:year2018-issue_reply:nonmember:mayaviFALSE:year2018**         |  5.84   | 0.0001  | 0.0001 | *** |
|                **pr_reply:member:numpyTRUE:year2011-pr_reply:member:numpyFALSE:year2011**                | -4.637  | 0.0001  | 0.0001 | *** |
|                 **pr_post:member:numpyTRUE:year2012-pr_post:member:numpyFALSE:year2012**                 | -2.754  |  0.006  | 0.029  |  *  |
|             **issue_reply:member:numpyTRUE:year2012-issue_reply:member:numpyFALSE:year2012**             | -3.673  | 0.0002  | 0.002  | **  |
|                **pr_reply:member:numpyTRUE:year2012-pr_reply:member:numpyFALSE:year2012**                | -9.217  | 0.0001  | 0.0001 | *** |
|          **issue_reply:nonmember:numpyTRUE:year2012-issue_reply:nonmember:numpyFALSE:year2012**          | -3.073  |  0.002  | 0.013  |  *  |
|             **pr_reply:nonmember:numpyTRUE:year2012-pr_reply:nonmember:numpyFALSE:year2012**             |  -3.55  | 0.0004  | 0.003  | **  |
|             **issue_reply:member:numpyTRUE:year2013-issue_reply:member:numpyFALSE:year2013**             | -5.102  | 0.0001  | 0.0001 | *** |
|                **pr_reply:member:numpyTRUE:year2013-pr_reply:member:numpyFALSE:year2013**                | -4.259  | 0.0001  | 0.0003 | *** |
|             **issue_reply:member:numpyTRUE:year2014-issue_reply:member:numpyFALSE:year2014**             | -5.302  | 0.0001  | 0.0001 | *** |
|           **issue_post:nonmember:numpyTRUE:year2014-issue_post:nonmember:numpyFALSE:year2014**           | -2.589  |  0.01   | 0.042  |  *  |
|                **pr_reply:member:numpyTRUE:year2015-pr_reply:member:numpyFALSE:year2015**                |  3.134  |  0.002  | 0.011  |  *  |
|             **issue_reply:member:numpyTRUE:year2016-issue_reply:member:numpyFALSE:year2016**             | -2.892  |  0.004  | 0.021  |  *  |
|          **issue_reply:nonmember:numpyTRUE:year2016-issue_reply:nonmember:numpyFALSE:year2016**          |  -2.79  |  0.005  | 0.026  |  *  |
|             **issue_reply:member:numpyTRUE:year2018-issue_reply:member:numpyFALSE:year2018**             | -2.842  |  0.004  | 0.023  |  *  |
|          **issue_reply:nonmember:numpyTRUE:year2018-issue_reply:nonmember:numpyFALSE:year2018**          |  3.636  | 0.0003  | 0.003  | **  |
|   **issue_reply:nonmember:scikit-imageTRUE:year2011-issue_reply:nonmember:scikit-imageFALSE:year2011**   | -2.558  |  0.011  | 0.045  |  *  |
|          **pr_post:member:scikit-imageTRUE:year2012-pr_post:member:scikit-imageFALSE:year2012**          | -3.199  |  0.001  | 0.009  | **  |
|      **pr_reply:nonmember:scikit-imageTRUE:year2012-pr_reply:nonmember:scikit-imageFALSE:year2012**      | -3.632  | 0.0003  | 0.003  | **  |
|         **pr_reply:member:scikit-imageTRUE:year2015-pr_reply:member:scikit-imageFALSE:year2015**         |  3.471  |    0    | 0.004  | **  |
|         **pr_reply:member:scikit-imageTRUE:year2018-pr_reply:member:scikit-imageFALSE:year2018**         | -4.447  | 0.0001  | 0.0001 | *** |
|         **issue_post:member:matplotlibTRUE:year2011-issue_post:member:matplotlibFALSE:year2011**         |  6.922  | 0.0001  | 0.0001 | *** |
|            **pr_post:member:matplotlibTRUE:year2012-pr_post:member:matplotlibFALSE:year2012**            |  5.667  | 0.0001  | 0.0001 | *** |
|           **pr_reply:member:matplotlibTRUE:year2012-pr_reply:member:matplotlibFALSE:year2012**           | -2.824  |  0.005  | 0.024  |  *  |
|     **issue_reply:nonmember:matplotlibTRUE:year2012-issue_reply:nonmember:matplotlibFALSE:year2012**     |  -2.62  |  0.009  | 0.039  |  *  |
|        **pr_reply:nonmember:matplotlibTRUE:year2012-pr_reply:nonmember:matplotlibFALSE:year2012**        |  3.484  |    0    | 0.004  | **  |
|        **issue_reply:member:matplotlibTRUE:year2013-issue_reply:member:matplotlibFALSE:year2013**        |  3.039  |  0.002  | 0.014  |  *  |
|           **pr_reply:member:matplotlibTRUE:year2014-pr_reply:member:matplotlibFALSE:year2014**           | -2.874  |  0.004  | 0.021  |  *  |
|            **pr_post:member:matplotlibTRUE:year2015-pr_post:member:matplotlibFALSE:year2015**            |  2.954  |  0.003  | 0.017  |  *  |
|        **issue_reply:member:matplotlibTRUE:year2015-issue_reply:member:matplotlibFALSE:year2015**        |  3.667  | 0.0002  | 0.002  | **  |
|           **pr_reply:member:matplotlibTRUE:year2015-pr_reply:member:matplotlibFALSE:year2015**           | -3.531  | 0.0004  | 0.003  | **  |
|         **issue_post:member:matplotlibTRUE:year2016-issue_post:member:matplotlibFALSE:year2016**         |  2.727  |  0.006  |  0.03  |  *  |
|            **pr_post:member:matplotlibTRUE:year2016-pr_post:member:matplotlibFALSE:year2016**            |  3.861  | 0.0001  | 0.001  | **  |
|        **issue_reply:member:matplotlibTRUE:year2016-issue_reply:member:matplotlibFALSE:year2016**        |  2.986  |  0.003  | 0.016  |  *  |
|           **pr_reply:member:matplotlibTRUE:year2016-pr_reply:member:matplotlibFALSE:year2016**           | -3.262  |  0.001  | 0.008  | **  |
|            **pr_post:member:matplotlibTRUE:year2018-pr_post:member:matplotlibFALSE:year2018**            |  3.736  | 0.0002  | 0.002  | **  |
|        **issue_reply:member:matplotlibTRUE:year2018-issue_reply:member:matplotlibFALSE:year2018**        |  4.572  | 0.0001  | 0.0001 | *** |
|           **pr_reply:member:matplotlibTRUE:year2018-pr_reply:member:matplotlibFALSE:year2018**           |  -4.92  | 0.0001  | 0.0001 | *** |
|     **issue_reply:nonmember:matplotlibTRUE:year2018-issue_reply:nonmember:matplotlibFALSE:year2018**     |  3.006  |  0.003  | 0.015  |  *  |
|                **pr_reply:member:scipyTRUE:year2013-pr_reply:member:scipyFALSE:year2013**                |  8.828  | 0.0001  | 0.0001 | *** |
|          **issue_reply:nonmember:scipyTRUE:year2013-issue_reply:nonmember:scipyFALSE:year2013**          | -3.099  |  0.002  | 0.012  |  *  |
|                **pr_reply:member:scipyTRUE:year2014-pr_reply:member:scipyFALSE:year2014**                |  2.717  |  0.007  | 0.031  |  *  |
|             **pr_reply:nonmember:scipyTRUE:year2014-pr_reply:nonmember:scipyFALSE:year2014**             |  4.25   | 0.0001  | 0.0003 | *** |
|                **pr_reply:member:scipyTRUE:year2015-pr_reply:member:scipyFALSE:year2015**                |  2.951  |  0.003  | 0.017  |  *  |
|             **pr_reply:nonmember:scipyTRUE:year2015-pr_reply:nonmember:scipyFALSE:year2015**             |  2.629  |  0.009  | 0.038  |  *  |
|                **pr_reply:member:scipyTRUE:year2016-pr_reply:member:scipyFALSE:year2016**                |  5.847  | 0.0001  | 0.0001 | *** |
|                **pr_reply:member:scipyTRUE:year2018-pr_reply:member:scipyFALSE:year2018**                |  7.498  | 0.0001  | 0.0001 | *** |
|          **issue_reply:nonmember:scipyTRUE:year2018-issue_reply:nonmember:scipyFALSE:year2018**          |  3.153  |  0.002  | 0.011  |  *  |
|             **pr_reply:nonmember:scipyTRUE:year2018-pr_reply:nonmember:scipyFALSE:year2018**             |  3.024  |  0.002  | 0.015  |  *  |
|      **issue_reply:member:scikit-learnTRUE:year2012-issue_reply:member:scikit-learnFALSE:year2012**      |  4.983  | 0.0001  | 0.0001 | *** |
|         **pr_reply:member:scikit-learnTRUE:year2012-pr_reply:member:scikit-learnFALSE:year2012**         |  3.246  |  0.001  | 0.008  | **  |
|      **issue_reply:member:scikit-learnTRUE:year2013-issue_reply:member:scikit-learnFALSE:year2013**      |  3.358  |  0.001  | 0.006  | **  |
|         **pr_reply:member:scikit-learnTRUE:year2013-pr_reply:member:scikit-learnFALSE:year2013**         |  4.645  | 0.0001  | 0.0001 | *** |
|         **pr_reply:member:scikit-learnTRUE:year2015-pr_reply:member:scikit-learnFALSE:year2015**         | -3.147  |  0.002  | 0.011  |  *  |
|    **issue_post:nonmember:scikit-learnTRUE:year2015-issue_post:nonmember:scikit-learnFALSE:year2015**    |  3.586  | 0.0003  | 0.003  | **  |
|   **issue_reply:nonmember:scikit-learnTRUE:year2016-issue_reply:nonmember:scikit-learnFALSE:year2016**   | -3.621  | 0.0003  | 0.003  | **  |
|       **issue_post:member:scikit-learnTRUE:year2018-issue_post:member:scikit-learnFALSE:year2018**       | -2.645  |  0.008  | 0.037  |  *  |
|          **pr_post:member:scikit-learnTRUE:year2018-pr_post:member:scikit-learnFALSE:year2018**          | -4.723  | 0.0001  | 0.0001 | *** |
|      **issue_reply:member:scikit-learnTRUE:year2018-issue_reply:member:scikit-learnFALSE:year2018**      |  -4.92  | 0.0001  | 0.0001 | *** |
|         **pr_reply:member:scikit-learnTRUE:year2018-pr_reply:member:scikit-learnFALSE:year2018**         | -11.15  | 0.0001  | 0.0001 | *** |
|   **issue_reply:nonmember:scikit-learnTRUE:year2018-issue_reply:nonmember:scikit-learnFALSE:year2018**   | -5.265  | 0.0001  | 0.0001 | *** |
|      **pr_reply:nonmember:scikit-learnTRUE:year2018-pr_reply:nonmember:scikit-learnFALSE:year2018**      | -4.298  | 0.0001  | 0.0002 | *** |
|             **issue_post:member:pandasTRUE:year2011-issue_post:member:pandasFALSE:year2011**             | -4.401  | 0.0001  | 0.0002 | *** |
|               **pr_reply:member:pandasTRUE:year2011-pr_reply:member:pandasFALSE:year2011**               |  8.277  | 0.0001  | 0.0001 | *** |
|         **issue_reply:nonmember:pandasTRUE:year2011-issue_reply:nonmember:pandasFALSE:year2011**         |  4.561  | 0.0001  | 0.0001 | *** |
|             **issue_post:member:pandasTRUE:year2012-issue_post:member:pandasFALSE:year2012**             | -4.281  | 0.0001  | 0.0003 | *** |
|                **pr_post:member:pandasTRUE:year2012-pr_post:member:pandasFALSE:year2012**                |  -2.59  |  0.01   | 0.042  |  *  |
|            **issue_reply:member:pandasTRUE:year2012-issue_reply:member:pandasFALSE:year2012**            | -4.089  | 0.0001  |   0    | *** |
|               **pr_reply:member:pandasTRUE:year2012-pr_reply:member:pandasFALSE:year2012**               |  7.54   | 0.0001  | 0.0001 | *** |
|         **issue_reply:nonmember:pandasTRUE:year2012-issue_reply:nonmember:pandasFALSE:year2012**         |  4.062  | 0.0001  | 0.001  | **  |
|               **pr_reply:member:pandasTRUE:year2013-pr_reply:member:pandasFALSE:year2013**               |  -7.02  | 0.0001  | 0.0001 | *** |
|         **issue_reply:nonmember:pandasTRUE:year2013-issue_reply:nonmember:pandasFALSE:year2013**         |  4.743  | 0.0001  | 0.0001 | *** |
|         **issue_reply:nonmember:pandasTRUE:year2014-issue_reply:nonmember:pandasFALSE:year2014**         |  2.764  |  0.006  | 0.028  |  *  |
|          **issue_post:nonmember:pandasTRUE:year2016-issue_post:nonmember:pandasFALSE:year2016**          | -3.972  | 0.0001  | 0.001  | **  |
|            **pr_reply:nonmember:pandasTRUE:year2016-pr_reply:nonmember:pandasFALSE:year2016**            | -3.904  | 0.0001  | 0.001  | **  |
|            **issue_reply:member:pandasTRUE:year2018-issue_reply:member:pandasFALSE:year2018**            |  2.868  |  0.004  | 0.021  |  *  |
|               **pr_reply:member:pandasTRUE:year2018-pr_reply:member:pandasFALSE:year2018**               |  11.18  | 0.0001  | 0.0001 | *** |
|          **issue_post:nonmember:pandasTRUE:year2018-issue_post:nonmember:pandasFALSE:year2018**          | -2.725  |  0.006  |  0.03  |  *  |
|         **issue_reply:nonmember:pandasTRUE:year2018-issue_reply:nonmember:pandasFALSE:year2018**         | -5.733  | 0.0001  | 0.0001 | *** |


```r
all_project_tests_10$p_val_adjusted = p.adjust(all_project_tests_10$p_value, method="BH")
write.table(all_project_tests_10,
            file="results/models/model-timecourse-gratitude-pvalues-10cutoff.tsv")
```
