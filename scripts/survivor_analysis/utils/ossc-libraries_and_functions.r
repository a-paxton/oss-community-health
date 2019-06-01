#### ossc-libraries_and_functions.r: Part of `oss_community-langauge_dynamics.Rmd` ####
#
# This script loads libraries and creates a number of 
# additional functions to facilitate data prep and analysis.
#
# Written by: A. Paxton (University of Connecticut)
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
  'jtools'
)

# load required packages
invisible(lapply(required_packages, library, character.only = TRUE))

#### Prevent scientific notation ####
options(scipen=999)

# read in pander_lme
pander_lme_url = "https://raw.githubusercontent.com/a-paxton/stats-tools/1829d77f99cf1c6a58c87bdadf7313c74c7dd6dc/pander_lme.R"
pander_lme_file = getURL(pander_lme_url, ssl.verifypeer = FALSE)
eval(parse(text = pander_lme_file))
