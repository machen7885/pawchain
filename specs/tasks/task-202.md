# task-202 — `make eval-capture`: the measurement, before the pipeline it measures

**Implements** REQ-001, REQ-011 (`specs/00-system-spec.md` §6) · **Week** 2 ·
**Status** done (suite implemented and tested; exits non-zero today because the golden set
is empty — see ADR-0005)

## Goal

Read the golden manifest (task-201), run every labelled image through `capture.process`
(task-203), and report per-stage yield, the blur/pose/illumination sweep, and the REQ-011
byte budget — or, if no labelled images exist yet, say exactly that and fail, rather than
printing a plausible number. `evals/run.py`'s existing convention (`run_unimplemented_suite`)
already refuses to fake a number for a suite that has not landed; this suite extends the
same refusal to a suite that has landed but has no data yet, with its own explicit status
so the two failure modes are never confused with each other.

## Files touched

- `evals/run.py` — `run_capture_suite`, wired into `run_suite`
- `evals/golden_capture.py` — `sweep_thresholds`, `stage_yield`
- `evals/test_run.py`, `evals/test_golden_capture.py`

## Behaviour

1. **No manifest, or an empty one** → `evals/out/capture.json` gets
   `status: "golden_set_empty"`, all rate fields `null`, exit 1. This is today's state.
2. **Manifest present, hash mismatch on any referenced file** → `status: "integrity_error"`,
   the offending ids listed, exit 1. A silently-drifted golden set is worse than an empty
   one, because it looks trustworthy.
3. **Manifest present, hashes verified** →
   - Run every entry through `capture.process`. Tally rejects by stage
     (`detect` / `select` / `landmark` / `align` / `quality`) and compute yield at each
     stage plus `end_to_end` (REQ-001's `accept_rate`). A stage whose default implementation
     raises `DetectorUnavailable` / `LandmarkerUnavailable` (task-203) counts every image as
     a reject at that stage — never as a pass — exactly as the deck instructs for a stage
     that does not exist yet.
   - For the subset of entries carrying ground-truth `landmarks` (task-201), run the
     alignment and quality-gate stages directly against the human-labelled points, bypassing
     the untrained detector/landmarker. This is what makes the blur/pose/illumination sweep
     possible before those two models are trained — the threshold question and the
     model-training question are decoupled on purpose (facilitator guide, Idea 4).
   - `sweep_thresholds` tries each candidate cutoff against that subset and reports, per
     signal, the fraction of the `not_usable` pile still admitted and the fraction of the
     `usable` pile wrongly rejected, at every candidate value.
   - REQ-011 (`ondevice_bytes`) is reported as `{"status": "blocked", "reason": "..."}`
     until a real detector and landmark model exist to export (task-204).
4. `evals/out/capture.json` always contains the four keys task-001 names —
   `accept_rate`, `reject_rate`, `threshold`, `model_version` — `null` where not yet
   computable, so a consumer never has to guess whether a key is missing or merely empty.
5. Exit code is 0 only when a manifest with at least 150 labelled images is present, hashes
   verify, and REQ-001's bound (≥95% of `not_usable` rejected, ≤5% of `usable` rejected) is
   met at the chosen threshold.

## Acceptance criteria

| # | Assertion | Command that proves it |
|---|---|---|
| 1 | With no manifest present, `make eval-capture` writes `capture.json` with `status: "golden_set_empty"` and exits 1 | `make eval-capture; echo "exit=$?"` |
| 2 | With a manifest present but a tampered file, the suite reports `integrity_error` and exits 1 | `pytest evals/test_run.py -k integrity -q` |
| 3 | A synthetic manifest with all-synthetic (non-photographic) fixture images produces per-stage yields that multiply, not add, across the five stages | `pytest evals/test_golden_capture.py -k yield -q` |
| 4 | `sweep_thresholds` on a synthetic labelled set returns a monotonic bad-admitted curve (non-increasing as the threshold rises) and a monotonic good-rejected curve (non-decreasing) | `pytest evals/test_golden_capture.py -k sweep -q` |
| 5 | `capture.json` always contains `accept_rate`, `reject_rate`, `threshold`, `model_version`, regardless of suite status | `pytest evals/test_run.py -k capture_keys -q` |

## Out of scope

Choosing the real operating threshold — that happens once real labelled photos exist
(ADR-0005). Training the detector or landmark model (OQ-011).
