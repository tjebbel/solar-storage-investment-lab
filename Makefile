# Solar + Storage Investment Lab
PY ?= python3
export PYTHONPATH := src

.PHONY: all setup test run run-live clean

all: test run

setup:
	$(PY) -m pip install -r requirements.txt

test:
	$(PY) -m unittest discover -s tests -v

run:
	$(PY) -m eti --db data/eti.db --out reports

# Real Dutch data from the Energy-Charts API (internet needed). Example: make run-live YEAR=2025
YEAR ?= 2025
run-live:
	$(PY) -m eti --source live --year $(YEAR) --db data/eti_live_$(YEAR).db --out reports/live_$(YEAR)

clean:
	rm -rf data/eti.db reports/results.* reports/*.csv reports/*.png reports/figures
