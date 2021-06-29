ALL_COMMENTS = $(wildcard data/raw_data/*/comments.tsv)
OUTPUT_FOLDERS = $(patsubst data/raw_data/%/comments.tsv, data/processed_data/%/processed-comments.csv, $(ALL_COMMENTS))

SUPP_TABLES = results/latex/model-1.1b_final_pvalues.tex \
	      results/latex/model-1.3b_final_pvalues.tex \
	      results/latex/model-timecourse-emotion-pvalues.tex \
	      results/latex/model-timecourse-gratitude-pvalues.tex \
	      results/latex/model_2.tex



all: $(OUTPUT_FOLDERS)

supp_tables: $(SUPP_TABLES)

results/latex/model_2.tex: results/models/model_2.tsv export_supp_table_model_2.1.py
	python export_supp_table_model_2.1.py

results/latex/%_pvalues.tex: results/models/%_pvalues.tsv export_supp_tables_pvalues.py columns
	python export_supp_tables_pvalues.py $< -o $@


results/latex/%-pvalues.tex: results/models/%-pvalues.tsv export_supp_timecourse_pvalues.py columns
	python export_supp_timecourse_pvalues.py $< -o $@


data/processed_data/%/processed-comments.csv: data/raw_data/%/comments.tsv extract_features.py ../bot_names.txt
	python extract_features.py -o $(@D) $(<D)
