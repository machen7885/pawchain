"""PawChain ID evaluation runner.

One entry point for every measurement named in `specs/00-system-spec.md`. Each requirement
in the spec names a command that produces its number; this module is what those commands
run. A suite that is not implemented yet exits non-zero rather than reporting a plausible
number, because a measurement you cannot trust is worse than no measurement.

Usage:
    python evals/run.py --suite gate
    python evals/run.py --suite dedup
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from evals import golden_capture
from ml.capture.quality import BLUR_THRESHOLD

OUT_DIR = Path(__file__).resolve().parent / "out"
GOLDEN_DIR = Path(__file__).resolve().parent / "golden"

# REQ-001's target sample size (facilitator guide, Idea 8: "take 150 of your own cropped
# photos"). Below this, a sweep is measuring noise, not a distribution.
MIN_GOLDEN_SET_SIZE = 150

# Candidate cutoffs for the blur sweep (ADR-0005). BLUR_THRESHOLD (120, the Week 1
# placeholder) is always included so `req_001` can report whether it still holds.
CANDIDATE_BLUR_THRESHOLDS = sorted({40.0, 80.0, BLUR_THRESHOLD, 160.0, 200.0})

# The template generation in use. Templates from different generations are never compared
# (REQ-008). No model exists yet, so nothing has produced a template.
MODEL_VERSION = "none-week1"


@dataclass(frozen=True)
class Suite:
    """One measurable suite: what it measures, and when it becomes real."""

    name: str
    filename: str
    requirements: tuple[str, ...]
    implemented_in_week: int | None
    description: str


SUITES: dict[str, Suite] = {
    "gate": Suite(
        name="gate",
        filename="metrics.json",
        requirements=(),
        implemented_in_week=1,
        description="Harness self-check. Proves the eval stage of the gate is wired.",
    ),
    "capture": Suite(
        name="capture",
        filename="capture.json",
        requirements=("REQ-001", "REQ-011"),
        implemented_in_week=2,
        description="Capture quality gate: blur rejection rates and on-device model size.",
    ),
    "liveness": Suite(
        name="liveness",
        filename="liveness.json",
        requirements=("REQ-002",),
        implemented_in_week=5,
        description="Multi-frame liveness: inter-frame consistency against photo replay.",
    ),
    "identify": Suite(
        name="identify",
        filename="identify.json",
        requirements=("REQ-003", "REQ-004", "REQ-005"),
        implemented_in_week=3,
        description="Open-set identification: top-1, FAR and FRR at one operating threshold.",
    ),
    "dedup": Suite(
        name="dedup",
        filename="dedup.json",
        requirements=("REQ-007",),
        implemented_in_week=3,
        description="Dedup on enrolment, including the littermate slice reported separately.",
    ),
    "search": Suite(
        name="search",
        filename="search.json",
        requirements=("REQ-006",),
        implemented_in_week=3,
        description="1:N search latency over a 100k-vector index.",
    ),
    "policy": Suite(
        name="policy",
        filename="policy.json",
        requirements=(
            "REQ-008",
            "REQ-009",
            "REQ-010",
            "REQ-012",
            "REQ-013",
            "REQ-014",
            "REQ-015",
            "REQ-016",
            "REQ-017",
            "REQ-018",
        ),
        implemented_in_week=5,
        description="Policy invariants: retention, versioning, authority, human gate, appeals.",
    ),
}


def _timestamp() -> str:
    """Return an ISO-8601 UTC timestamp for the metrics file."""
    return datetime.now(UTC).isoformat(timespec="seconds")


def write_metrics(suite: Suite, payload: dict[str, object]) -> Path:
    """Write one suite's metrics to `evals/out/` and return the path written."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    destination = OUT_DIR / suite.filename
    document: dict[str, object] = {
        "suite": suite.name,
        "requirements": list(suite.requirements),
        "model_version": MODEL_VERSION,
        "generated_at": _timestamp(),
        **payload,
    }
    destination.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return destination


def run_gate_suite(suite: Suite) -> int:
    """Run the harness self-check.

    Week 1 has no model, so there is nothing to score. What this proves is that the eval
    stage of the gate runs, writes a file, and can fail. It exits non-zero if the file was
    not written, which is the only assertion available until Week 2 produces a number.
    """
    payload: dict[str, object] = {
        "status": "ok",
        "harness": "wired",
        "suites_registered": sorted(SUITES),
        "suites_implemented": sorted(
            name for name, s in SUITES.items() if s.implemented_in_week == 1
        ),
        "golden_sets_present": sorted(p.name for p in GOLDEN_DIR.glob("*") if p.is_dir()),
        "note": "No model exists in Week 1. This suite proves the gate's eval stage runs.",
    }
    destination = write_metrics(suite, payload)
    if not destination.is_file():
        print(f"eval: FAIL — {destination} was not written", file=sys.stderr)
        return 1
    print(f"eval: PASS  metrics written to {destination.relative_to(Path.cwd())}")
    return 0


def run_capture_suite(suite: Suite) -> int:
    """Measure REQ-001 and REQ-011 against the golden capture manifest.

    Three honestly distinct failure states, never confused with a real number
    (task-202): `golden_set_empty` (no manifest, or one with zero images — today's state,
    see ADR-0005), `integrity_error` (a referenced file's bytes no longer match its
    recorded hash), and `measured` (real numbers, which may still fail the suite if the
    golden set is smaller than `MIN_GOLDEN_SET_SIZE` or REQ-001's bound is not met).
    """
    base_payload: dict[str, object] = {
        "accept_rate": None,
        "reject_rate": None,
        "threshold": BLUR_THRESHOLD,
    }
    manifest_path = GOLDEN_DIR / "capture" / "manifest.json"

    try:
        manifest = golden_capture.load_manifest(manifest_path)
    except FileNotFoundError:
        payload = {
            **base_payload,
            "status": "golden_set_empty",
            "message": (
                "No golden capture manifest found. Run the Week 2 homework capture "
                "protocol, label crops usable/not_usable, then commit "
                "evals/golden/capture/manifest.json. See specs/tasks/task-201.md."
            ),
        }
        write_metrics(suite, payload)
        print(f"eval[capture]: FAIL — {payload['message']}", file=sys.stderr)
        return 1

    if not manifest.images:
        payload = {
            **base_payload,
            "status": "golden_set_empty",
            "message": "evals/golden/capture/manifest.json exists but has zero labelled images.",
        }
        write_metrics(suite, payload)
        print(f"eval[capture]: FAIL — {payload['message']}", file=sys.stderr)
        return 1

    image_root = golden_capture.default_image_root()
    mismatches = golden_capture.verify_hashes(manifest, image_root)
    if mismatches:
        payload = {
            **base_payload,
            "status": "integrity_error",
            "mismatched_ids": mismatches,
        }
        write_metrics(suite, payload)
        print(
            f"eval[capture]: FAIL — {len(mismatches)} file(s) do not match their recorded "
            f"hash: {mismatches}. A golden set that has silently drifted is worse than an "
            "empty one.",
            file=sys.stderr,
        )
        return 1

    yields = golden_capture.stage_yield(manifest, image_root)
    sweep = golden_capture.sweep_thresholds(manifest, image_root, CANDIDATE_BLUR_THRESHOLDS)

    usable_total = sum(1 for image in manifest.images if image.label == "usable")
    not_usable_total = sum(1 for image in manifest.images if image.label == "not_usable")
    chosen = next((point for point in sweep if point.threshold == BLUR_THRESHOLD), None)

    req_001_status = "not_measurable"
    req_001_pass = False
    if chosen is not None and usable_total and not_usable_total:
        # REQ-001's bound (task-001 #5): reject >= 95% of unusable frames (bad_admitted
        # <= 5%), wrongly reject <= 5% of usable ones (good_rejected <= 5%).
        req_001_pass = chosen.bad_admitted <= 0.05 and chosen.good_rejected <= 0.05
        req_001_status = "pass" if req_001_pass else "fail"

    end_to_end = yields.get("end_to_end")
    payload = {
        "status": "measured",
        "golden_set_size": len(manifest.images),
        "usable_count": usable_total,
        "not_usable_count": not_usable_total,
        "landmark_labelled_count": sum(
            1 for image in manifest.images if image.landmarks is not None
        ),
        "yield": yields,
        "accept_rate": end_to_end,
        "reject_rate": (1 - end_to_end) if end_to_end is not None else None,
        "threshold": BLUR_THRESHOLD,
        "blur_sweep": [asdict(point) for point in sweep],
        "req_001": {
            "status": req_001_status,
            "bound": "reject >= 95% of not_usable, wrongly reject <= 5% of usable, same threshold",
        },
        "req_011": {
            "status": "blocked",
            "reason": (
                "no trained detector or landmark model exists yet — "
                "see specs/open-questions.md OQ-011"
            ),
        },
    }
    destination = write_metrics(suite, payload)

    enough_data = len(manifest.images) >= MIN_GOLDEN_SET_SIZE
    if enough_data and req_001_pass:
        print(f"eval[capture]: PASS  metrics written to {destination.relative_to(Path.cwd())}")
        return 0
    print(
        f"eval[capture]: FAIL — golden set has {len(manifest.images)} image(s) "
        f"(need >= {MIN_GOLDEN_SET_SIZE}), REQ-001 status is {req_001_status!r}. "
        f"Metrics written to {destination.relative_to(Path.cwd())}.",
        file=sys.stderr,
    )
    return 1


def run_unimplemented_suite(suite: Suite) -> int:
    """Record that a scheduled measurement does not exist yet, and fail.

    This is deliberate. The spec claims a command produces each number; that claim has to
    be false loudly rather than quietly. Reporting a placeholder number here would let a
    requirement look measured when nothing measured it.
    """
    payload: dict[str, object] = {
        "status": "not_implemented",
        "implemented_in_week": suite.implemented_in_week,
        "description": suite.description,
    }
    destination = write_metrics(suite, payload)
    print(
        f"eval[{suite.name}]: NOT IMPLEMENTED — scheduled for Week "
        f"{suite.implemented_in_week}. Requirements: {', '.join(suite.requirements)}. "
        f"Placeholder written to {destination}.",
        file=sys.stderr,
    )
    return 1


def run_suite(name: str) -> int:
    """Run one suite by name and return its process exit code."""
    suite = SUITES.get(name)
    if suite is None:
        print(
            f"eval: unknown suite {name!r}. Known suites: {', '.join(sorted(SUITES))}",
            file=sys.stderr,
        )
        return 2
    if suite.name == "gate":
        return run_gate_suite(suite)
    if suite.name == "capture":
        return run_capture_suite(suite)
    return run_unimplemented_suite(suite)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--suite",
        default="gate",
        choices=sorted(SUITES),
        help="Which measurement suite to run.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns the process exit code."""
    args = build_parser().parse_args(argv)
    suite_name: str = args.suite
    return run_suite(suite_name)


if __name__ == "__main__":
    raise SystemExit(main())
