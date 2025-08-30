# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:		 BP
# Maintainers: BP
# Copyright:	 2024, HRDAG, GPL v2 or later
# =========================================

url := "https://idoc.illinois.gov/facilities.html"
html := output/facility_soup.html
lost := output/lost.yml
pages := output/pages.parquet
stats := output/facility_stats.parquet

.PHONY: all clean

all: $(html) $(pages)

clean:
	-rm -r output/*

$(stats): \
	src/format.py \
	$(html)
	python $< \
		--input=$(html)\
		--lost=$(lost)\
		--output=$@

$(pages): \
	src/scrape-batch.py
	-mkdir output
	python $< \
		--url=$(url)\
		--output=$@

$(html): \
	../../shared/src/scrape.py
	-mkdir output
	python $< \
		--url=$(url)\
		--output=$@

# done
