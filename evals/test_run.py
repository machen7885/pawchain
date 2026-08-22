"""Tests for the eval runner.

These are the assertions behind task-000 acceptance criteria 4, 5 and 9. They exist to
prove the pipeline is wired, and — more importantly — that a suite nobody has implemented
fails instead of reporting a number.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

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


def test_capture_suite_with_no_manifest_reports_golden_set_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """task-202 #1: no manifest present -> `golden_set_empty`, exit 1."""
    monkeypatch.setattr(run, "GOLDEN_DIR", tmp_path)

    assert run.run_suite("capture") == 1
    document = json.loads((run.OUT_DIR / "capture.json").read_text(encoding="utf-8"))
    assert document["status"] == "golden_set_empty"
    assert document["accept_rate"] is None


def test_capture_suite_reports_integrity_error_on_a_tampered_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """task-202 #2: a manifest whose file no longer matches its recorded hash fails loudly."""
    golden_dir = tmp_path / "golden"
    image_root = tmp_path / "images"
    image_root.mkdir(parents=True)
    image_path = image_root / "a.jpg"
    image_path.write_bytes(b"original bytes")
    digest = hashlib.sha256(image_path.read_bytes()).hexdigest()
    image_path.write_bytes(b"tampered bytes")

    manifest_path = golden_dir / "capture" / "manifest.json"
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text(
        json.dumps(
            {
                "version": 1,
                "images": [
                    {"id": "a", "relative_path": "a.jpg", "sha256": digest, "label": "usable"}
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(run, "GOLDEN_DIR", golden_dir)
    monkeypatch.setenv("PAWCHAIN_GOLDEN_IMAGES", str(image_root))

    assert run.run_suite("capture") == 1
    document = json.loads((run.OUT_DIR / "capture.json").read_text(encoding="utf-8"))
    assert document["status"] == "integrity_error"
    assert document["mismatched_ids"] == ["a"]


def test_capture_json_always_has_the_keys_task_001_requires(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """task-202 #5: accept_rate, reject_rate, threshold, model_version — always present."""
    monkeypatch.setattr(run, "GOLDEN_DIR", tmp_path)

    run.run_suite("capture")

    document = json.loads((run.OUT_DIR / "capture.json").read_text(encoding="utf-8"))
    assert {"accept_rate", "reject_rate", "threshold", "model_version"} <= document.keys()


def test_every_requirement_with_a_measurement_maps_to_exactly_one_suite():
    """No requirement may be measured by two suites; that is how numbers disagree."""
    seen: set[str] = set()
    for suite in run.SUITES.values():
        for requirement in suite.requirements:
            assert requirement not in seen, f"{requirement} measured by more than one suite"
            seen.add(requirement)
