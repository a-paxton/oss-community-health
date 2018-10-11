
ISSUES = $(wildcard data/*/issues.tsv)
HISTOGRAM_CONTRIBUTORS = $(patsubst data/%/issues.tsv, images/%/histogram_pull_request_pre_contributor.png, $(ISSUES))


all: img

img: $(HISTOGRAM_CONTRIBUTORS)

images/%/histogram_pull_request_pre_contributor.png: data/%/issues.tsv plot_histogram_of_num_pull_request_per_contributor.py
	python plot_histogram_of_num_pull_request_per_contributor.py $< -o $@
