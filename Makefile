.PHONY: lint types test eval gate \
	eval-capture eval-liveness eval-identify eval-dedup eval-search eval-policy

PYTHON ?= python3

lint:
	ruff check .

types:
	pyright

test:
	pytest -q

# Run as a module, not a script: evals/run.py imports from the evals and ml packages
# (evals.golden_capture, ml.capture), which only resolve when the repo root is on
# sys.path — which `-m` guarantees and a bare script path does not.
eval:
	$(PYTHON) -m evals.run --suite gate

gate: lint types test eval
	@echo "gate: GREEN"

# Per-requirement measurement commands. Each writes one JSON file to evals/out/
# and exits non-zero until the suite it names is implemented in its scheduled week.
# A requirement whose measurement command does not exist is not a requirement.

eval-capture:
	$(PYTHON) -m evals.run --suite capture

eval-liveness:
	$(PYTHON) -m evals.run --suite liveness

eval-identify:
	$(PYTHON) -m evals.run --suite identify

eval-dedup:
	$(PYTHON) -m evals.run --suite dedup

eval-search:
	$(PYTHON) -m evals.run --suite search

eval-policy:
	$(PYTHON) -m evals.run --suite policy
