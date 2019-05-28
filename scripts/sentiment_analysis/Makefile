ALL_COMMENTS = $(wildcard data/raw_data/*/*/comments.tsv)
OUTPUT_FOLDERS = $(patsubst data/raw_data/%/comments.tsv, data/processed_data/%/processed-joined.csv, $(ALL_COMMENTS))


all: $(OUTPUT_FOLDERS)

data/processed_data/%/processed-joined.csv: data/raw_data/%/comments.tsv extract_features.py
	python extract_features.py -o $(@D) $(<D)

