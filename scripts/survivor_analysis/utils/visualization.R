library(graphics)

colors = c("#e66101", # issue: post (darker)
           "#fdb863", # issue: reply (lighter)
           "#5e3c99", # PR: post (darker)
           "#b2abd2") # PR: reply (lighter)

names(colors) = c("issue_post", "issue_reply", "pr_post", "pr_reply")
all_years = 2009:2019

plot_timecourse = function(project_to_plot, means){
    # Should probably get the yrange from the data.
    graphics::par(mfrow=c(1, 2))

    .plot_member_timecourse(project_to_plot, "member", means)
    .plot_member_timecourse(project_to_plot, "nonmember", means)

}

.plot_member_timecourse = function(project_to_plot, membership_type, means){

    xrange = range(all_years)
    yrange = c(-0.2, 0.5)

    graphics::plot(xrange, yrange, type="n",
		   main=paste(project_to_plot, "-", membership_type),
		   cex=0.8)

    for(group in c("issue_post", "pr_post", "issue_reply", "pr_reply")){
	group_to_plot = paste(project_to_plot, group, membership_type, sep=":")
	rows_of_interest =  grep(group_to_plot, names(means))
	years = as.numeric(
	    unlist(
		lapply(strsplit(names(means)[rows_of_interest], ":"),
		    function(x) x[4])))

	graphics::lines(years, means[rows_of_interest], type="l", lwd=2,
			col=colors[group])
    }
}

