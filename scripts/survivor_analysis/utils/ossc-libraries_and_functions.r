#### ossc-libraries_and_functions.r: Part of `oss_community-langauge_dynamics.Rmd` ####
#
# This script loads libraries and creates a number of 
# additional functions to facilitate data prep and analysis.
#
# Written by: A. Paxton (University of Connecticut) & Nelle Varoquaux (University of California, Berkeley)
# Date last modified: 30 May 2019
#####################################################################################

#### Load necessary packages ####

# list of required packages
required_packages = c(
  'dplyr',
  'data.table',
  'lme4',
  'ggplot2',
  'pander',
  'gridExtra',
  'plotrix',
  'gtable',
  'viridis',
  'jsonlite',
  'tidyr',
  'tibble',
  'RCurl',
  'splines',
  'magrittr',
  'jtools',
  'splines',
  'lmerTest'
  )

# load required packages using pacman
pacman::p_load(required_packages, character.only=TRUE)

#### Prevent scientific notation ####
options(scipen=999)

#### Read in external functions ####

# read in pander_lme
pander_lme_url = "https://raw.githubusercontent.com/a-paxton/stats-tools/2a1bf715097bbcc966ab612af3a9e0b14408d4ff/pander_lme.R"
pander_lme_file = getURL(pander_lme_url, ssl.verifypeer = FALSE)
eval(parse(text = pander_lme_file))

#### Create new functions ####

# compute p-values from t-statistics (typical in psychology)
compute_p_value_from_t_stats = function(t_stats){
  p_values = 2*(1-pnorm(abs(t_stats)))
}

# Because we need splines that span independently from one another the dates
# of projects, we need to create a function that takes two variable vectors
# from the dataframe: (1) the dates; (2) the groups. We also need to provide
# to the function the value corresponding to the group of interest. The rest
# is just a normal spline.
group_date_ns = function(date, group, value, knots=NULL, degrees_of_freedom=NULL){
  
  # Estimate the number of degrees of freedom we're assigning to this spline
  range = max(sentiment_frame$date[group == value]) - min(sentiment_frame$date[group == value])
  degrees_of_freedom = floor(range / 365)
  
  # Create the basis of the right size, but with 0 everywhere
  basis = 0 * splines::ns(date, df=degrees_of_freedom)
  
  # Now, for the correct group, create the splines that span across the
  # dates of the group. This means the basis should have 0 everywhere except
  # on the dates spanning this group.
  basis[group == value,] = splines::ns(date[group == value], 
                                       knots=knots,
                                       df=degrees_of_freedom)
  return(basis)
}

# display cleaned ANOVA output
pander_clean_anova = function(model, rename_columns=TRUE,
                              pval_correction_method="BH",
			      display_only_significant=FALSE){
  # First, rename the functions into something sane.
  if(rename_columns){
    colnames(model) = c("sum_sq", "mean_sq", "num_df", "den_df",
                        "f_value", "p_value")
  }
  
  # Adjust p-values
  model$p_adj = stats::p.adjust(model$p_value, method=pval_correction_method)
  
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
  if(display_only_significant){
    pander(model[model$p_adj < 0.05, ], , split.table=Inf, style="rmarkdown")
  }else{
    pander(model, , split.table = Inf, style = 'rmarkdown')
  }
}

#' Welch t-test
compute_t_statistics = function(means, standard_error,
                                contrasts){
  all_tests = data.frame()
  for(contrast in contrasts){
    splits = unlist(strsplit(contrast, "-"))
    if(length(splits) != 2){
      error("Dunno how to deal with this just yet") 
    }
    
    group1 = splits[1]
    group2 = splits[2]
    
    t = ((means[group1] - means[group2]) /
           (standard_error[group1]**2 +
              standard_error[group2]**2)**.5)
    all_tests[contrast, "t_stats"] = t
  }
  return(all_tests) 
}
