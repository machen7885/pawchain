"""Tests for the eval runner.

These are the assertions behind task-000 acceptance criteria 4, 5 and 9. They exist to
prove the pipeline is wired, and — more importantly — that a suite nobody has implemented
fails instead of reporting a number.
"""

from __future__ import annotations

import json

from evals import run


def test_gate_suite_writes_metrics_and_passes():
    """Criterion 5: `make eval` writes evals/out/metrics.json and succeeds."""
    assert run.run_suite("gate") == 0
    metrics_path = run.OUT_DIR / "metrics.json"
    assert metrics_path.is_file()
    document = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert document["status"] == "ok"
    assert document["suite"] == "gate"
    assert document["model_version"] == run.MODEL_VERSION


def test_unimplemented_suite_fails_rather_than_reporting_a_number():
    """Criterion 9: a scheduled-but-unbuilt measurement exits non-zero."""
    assert run.run_suite("dedup") == 1
    document = json.loads((run.OUT_DIR / "dedup.json").read_text(encoding="utf-8"))
    assert document["status"] == "not_implemented"
    assert "far" not in document
    assert "frr" not in document


def test_unknown_suite_is_an_error():
    """A typo in a measurement command must not silently pass."""
    assert run.run_suite("does-not-exist") == 2


def test_every_suite_names_the_week_it_lands():
    """A measurement with no scheduled week is a requirement nobody owns."""
    for name, suite in run.SUITES.items():
        assert suite.implemented_in_week is not None, name
        assert suite.filename.endswith(".json"), name


def test_every_requirement_with_a_measurement_maps_to_exactly_one_suite():
    """No requirement may be measured by two suites; that is how numbers disagree."""
    seen: set[str] = set()
    for suite in run.SUITES.values():
        for requirement in suite.requirements:
            assert requirement not in seen, f"{requirement} measured by more than one suite"
            seen.add(requirement)
