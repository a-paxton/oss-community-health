
ISSUES = $(wildcard data/*/issues.tsv)
HISTOGRAM_CONTRIBUTORS = $(patsubst data/%/issues.tsv, images/%/histogram_pull_request_pre_contributor.png, $(ISSUES))
HISTOGRAM_OPEN_DURATION = $(patsubst data/%/issues.tsv, images/%/histogram_duration_open_pullrequest.png, $(ISSUES)) \
			  $(patsubst data/%/issues.tsv, images/%/histogram_duration_open_tickets.png, $(ISSUES)) \

GLOBAL_IMAGES = images/survival_plot_all_projects.png \
		images/proportion_survival_at_2PR.png \
		images/proportion_survival_at_3PR.png \
		images/proportion_survival_at_4PR.png \
		images/proportion_survival_at_5PR.png \

all: img

img: $(HISTOGRAM_CONTRIBUTORS) $(GLOBAL_IMAGES) $(HISTOGRAM_OPEN_DURATION)

images/%/histogram_pull_request_pre_contributor.png: data/%/issues.tsv plot_histogram_of_num_pull_request_per_contributor.py
	python plot_histogram_of_num_pull_request_per_contributor.py $< -o $@


images/survival_plot_all_projects.png: $(ISSUES) plot_survival_curve_pull_request.py
	python plot_survival_curve_pull_request.py -o $@

images/proportion_survival_at_%PR.png: $(ISSUES) plot_proportion_survival_at_n_pullrequest.py
	python plot_proportion_survival_at_n_pullrequest.py -n $* -o $@


images/%/histogram_duration_open_pullrequest.png: data/%/issues.tsv plot_distribution_time_tickets_open.py
	python plot_distribution_time_tickets_open.py $* -o $@


images/%/histogram_duration_open_issues.png: data/%/issues.tsv plot_distribution_time_tickets_open.py
	python plot_distribution_time_tickets_open.py $* -o $@ -t issues
