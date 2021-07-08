library(dplyr)

loading_tickets_data = function(dataset="original", membership_cutoff=5){
  # load data
  tickets_frame = read.csv(
    '../../data/analysis_data/sentiment_frame_tickets-for_r.tsv',
    sep = '\t', stringsAsFactors=FALSE)
  
  # Sometimes, R fails to load the CSV file properly and truncates it. This cell
  # does a basic check on the size of the data to make sure we have the correct
  # number of rows and colums.
  
  if(all(dim(tickets_frame) != c(90117, 36))){
    stop("Problem with the ticket frame. Not the right size!!")
  }
  
  tickets_frame = tickets_frame[tickets_frame$scip_dataset == dataset, ]
  
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
    mutate(author_group = dplyr::if_else(total_tickets < membership_cutoff,
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
              as.factor)
  
  
  # Extract year
  tickets_frame$year = unlist(lapply(
    tickets_frame$created_at,
    function(x) unlist(strsplit(x, "-"))[1]))
  
  # Now drop old columns
  tickets_frame = tickets_frame %>% 
    dplyr::select(-ends_with('_at'))
  
  return(tickets_frame)
}

loading_comments_data = function(dataset, membership_cutoff=5){
  comments_frame = read.csv(
    '../../data/analysis_data/sentiment_frame_comments-for_r.tsv',
    sep = '\t', stringsAsFactors=FALSE)
  
  # Sometimes, R fails to load the CSV file properly and truncates it. This cell
  # does a basic check on the size of the data to make sure we have the correct
  # number of rows and colums.
  if(all(dim(comments_frame) != c(524062, 29))){
    stop("Problem with the ticket frame. Not the right size!!")
  }
  
  comments_frame = comments_frame[comments_frame$scip_dataset == dataset, ]
  
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
    mutate(author_group = dplyr::if_else(total_tickets < membership_cutoff,
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
              as.factor)  
  
  # Extract year
  comments_frame$year = unlist(lapply(
    comments_frame$created_at,
    function(x) unlist(strsplit(x, "-"))[1]))
  
  comments_frame = comments_frame %>%
    # drop old columns
    dplyr::select(-ends_with('_at')) 
  return(comments_frame)
}


combine_tickets_and_comments = function(tickets_frame, comments_frame){
  # merge tickets and comments into a single frame
  sentiment_frame = tickets_frame %>%
    dplyr::bind_rows(., comments_frame) %>%
    
    # keep only select variables
    dplyr::select(project,
                  date,
                  contains('author'),
                  first_ticket,
                  contains('num_'),
                  contains("year"),
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
  
  return(sentiment_frame)
}
