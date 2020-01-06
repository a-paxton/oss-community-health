PROJECTS = scikit-image \
	   scikit-learn \
	   matplotlib \
	   numpy \
	   scipy \
	   mayavi \
	   sphinx-gallery \
	   pandas 

SENTIMENT_PLOTS = $(patsubst %, figures/supp/sentiment_%.pdf, $(PROJECTS))
SENTIMENT_TIMECOURSE_PLOTS = $(patsubst %, figures/supp/timecourse_sentiment_%.pdf, $(PROJECTS))

GRATITUDE_PLOTS = $(patsubst %, figures/supp/gratitude_%.pdf, $(PROJECTS))
GRATITUDE_TIMECOURSE_PLOTS = $(patsubst %, figures/supp/timecourse_gratitude_%.pdf, $(PROJECTS))


all:  $(SENTIMENT_PLOTS) $(GRATITUDE_PLOTS) $(GRATITUDE_TIMECOURSE_PLOTS) $(SENTIMENT_TIMECOURSE_PLOTS)

figures/supp/sentiment_%.pdf: results/models/model-1.1c.tsv figure_supp_emotions_by_author_group_membership_projects.py
	python figure_supp_emotions_by_author_group_membership_projects.py $* -o $@


figures/supp/gratitude_%.pdf: results/models/model-1.1c.tsv figure_supp_gratitude_by_author_group_membership_projects.py
	python figure_supp_gratitude_by_author_group_membership_projects.py $* -o $@


figures/supp/timecourse_sentiment_%.pdf: results/models/model-1.2.tsv figure_supp_emotions_timecourse_by_projects.py
	python figure_supp_emotions_timecourse_by_projects.py $* -o $@

figures/supp/timecourse_gratitude_%.pdf: results/models/model-1.2.tsv figure_supp_gratitude_timecourse_by_projects.py
	python figure_supp_gratitude_timecourse_by_projects.py $* -o $@

