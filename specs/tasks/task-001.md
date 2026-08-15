# task-001 — Capture quality gate

**Implements** REQ-001 (`specs/00-system-spec.md` §6) · **Week** 2 · **Status** not started

## Goal

Reject an enrolment frame whose aligned face crop is too blurred to embed, on the device,
before the frame is ever sent to the server. A blurred frame that reaches the template
extractor produces a weak template, and a weak template is the exact condition threat
model row 9 (deliberate degradation) relies on.

## Files I will touch

- `ml/capture/quality.py` — the blur metric and the accept/reject decision
- `ml/capture/__init__.py`
- `evals/run.py` — implement the `capture` suite
- `evals/golden/capture/` — frozen labelled frames (accept / reject), never used for tuning
- `Makefile` — `eval-capture` already exists; it must stop exiting non-zero

## Acceptance criteria

Each assertion is checkable by a command. An assertion without a command is not an
acceptance criterion, it is a hope.

| # | Assertion | Command that proves it |
|---|---|---|
| 1 | `quality.laplacian_variance(crop)` returns a float for a valid aligned crop and raises on a wrongly shaped input | `pytest ml/capture/test_quality.py -q` |
| 2 | A frame with Laplacian variance below 120 on the aligned crop is rejected; at or above 120 it is accepted | `pytest ml/capture/test_quality.py -q` |
| 3 | The threshold 120 is read from a single named constant, not repeated as a literal anywhere else | `grep -rn "120" ml/ \| grep -v "BLUR_THRESHOLD" ` returns nothing |
| 4 | `make eval-capture` writes `evals/out/capture.json` containing `accept_rate`, `reject_rate`, `threshold` and `model_version` | `make eval-capture && python -c "import json;d=json.load(open('evals/out/capture.json'));assert {'accept_rate','reject_rate','threshold','model_version'} <= d.keys()"` |
| 5 | Measured on the frozen golden set, the gate rejects ≥ 95% of frames labelled unusable and ≤ 5% of frames labelled usable | `make eval-capture` — the suite exits non-zero if either bound is missed |
| 6 | The combined on-device ONNX artefacts for detector and aligner are ≤ 25 MB (REQ-011) | `make eval-capture` — reported as `ondevice_bytes` in `evals/out/capture.json`, suite fails above the budget |
| 7 | No golden-set frame is used to select the threshold | `git log --oneline -- evals/golden/` shows no commit that changes golden data in the same commit as a threshold change |
| 8 | A rejected frame never leaves the device | `pytest miniapp/test_capture_flow.py -q` — asserts no upload call on the reject path |

## Notes and risks

- The 120 figure is inherited from the spec draft and has not been measured against real
  phone captures of real cats. Week 2 opens with the capture homework precisely so this
  number can be replaced by a measured one. If the golden set says a different number, the
  spec changes and this task file changes with it.
- Laplacian variance is scale-sensitive: it must be computed on the *aligned* crop at a
  fixed resolution, or the number means nothing across devices.

## Out of scope

Liveness (REQ-002), pose and illumination gating beyond blur, and any server-side
re-validation.
