IMAGES = images/bus_factor.png


all: $(IMAGES)

images/bus_factor.png: $(wildcard data/raw_data/*/commits.tsv) plot_normalized_commit_rates.py
	python plot_normalized_commit_rates.py -o $@
