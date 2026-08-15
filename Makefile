.PHONY: lint types test eval gate \
	eval-capture eval-liveness eval-identify eval-dedup eval-search eval-policy

PYTHON ?= python3

lint:
	ruff check .

types:
	pyright

test:
	pytest -q

eval:
	$(PYTHON) evals/run.py --suite gate

gate: lint types test eval
	@echo "gate: GREEN"

# Per-requirement measurement commands. Each writes one JSON file to evals/out/
# and exits non-zero until the suite it names is implemented in its scheduled week.
# A requirement whose measurement command does not exist is not a requirement.

eval-capture:
	$(PYTHON) evals/run.py --suite capture

eval-liveness:
	$(PYTHON) evals/run.py --suite liveness

eval-identify:
	$(PYTHON) evals/run.py --suite identify

eval-dedup:
	$(PYTHON) evals/run.py --suite dedup

eval-search:
	$(PYTHON) evals/run.py --suite search

eval-policy:
	$(PYTHON) evals/run.py --suite policy
