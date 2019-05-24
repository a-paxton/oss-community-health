PROJECTS = $(patsubst data/raw_data/%, %, $(wildcard data/raw_data/*))
HIST_COMMENTS = $(patsubst %, images/%/hist_comments.png, $(PROJECTS))
HIST_COMMITS = $(patsubst %, images/%/hist_commits.png, $(PROJECTS))
HIST_ISSUES = $(patsubst %, images/%/hist_issues.png, $(PROJECTS))


all: img

img: histograms

histograms: $(HIST_COMMENTS) $(HIST_COMMITS) $(HIST_ISSUES)

images/%/hist_comments.png: data/raw_data/%/comments.tsv plot_number_comments_time.py ../bot_names.txt
	python plot_number_comments_time.py $* -o $@

images/%/hist_issues.png: data/raw_data/%/issues.tsv plot_number_issues_time.py ../bot_names.txt
	python plot_number_issues_time.py $* -o $@


images/%/hist_commits.png: data/raw_data/%/commits.tsv plot_number_commits_time.py ../bot_names.txt
	python plot_number_commits_time.py $* -o $@

clean:
	rm -rf results
	rm -rf images
