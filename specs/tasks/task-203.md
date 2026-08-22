# task-203 — `capture.process(frame)`: five stages, one signature

**Implements** REQ-001 (`specs/00-system-spec.md` §6) · **Week** 2 · **Status** done

## Goal

One function. A phone frame goes in; an `AlignedCrop` or a stage-tagged `Reject` comes out.
No third outcome. `capture.process` is the signature both Week 3's embedder and Week 5's
mini-program capture flow call — see `ml/README.md`.

## Files touched

- `ml/capture/__init__.py`
- `ml/capture/types.py` — `Point`, `BBox`, `Landmarks`, `AlignedCrop`, `Reject`,
  `RejectStage`, `RejectReason`, `REJECT_MESSAGES`
- `ml/capture/detect.py` — the detect-stage contract; the default raises
  `DetectorUnavailable` (see Notes)
- `ml/capture/select.py` — the selection rule (largest box, most central, highest
  confidence), and when it is genuinely ambiguous
- `ml/capture/landmark.py` — the landmark-stage contract; the default raises
  `LandmarkerUnavailable`
- `ml/capture/align.py` — `CANONICAL_TEMPLATE`, `similarity_transform`, `warp_affine`
- `ml/capture/quality.py` — `laplacian_variance`, `illumination_stats`, `QualityThresholds`
- `ml/capture/pipeline.py` — `process`, wiring the five stages together
- One test file per module above

## Behaviour

`capture.process(frame, *, detect=default_detect, select_fn=select, locate=default_locate,
thresholds=DEFAULT_THRESHOLDS)`:

1. **detect** — reject `INVALID_INPUT` if `frame` is not an `(H, W, 3)` array; reject
   `NO_CAT_FOUND` if the detector returns no candidates; reject `DETECTOR_NOT_TRAINED` if
   the detector is unavailable (see Notes)
2. **select** — apply the rule; reject `AMBIGUOUS_CANDIDATES` only in the genuine near-tie
   case (Idea 3, facilitator guide)
3. **landmark** — reject `LANDMARK_MODEL_NOT_TRAINED` if unavailable, `LOW_LANDMARK_CONFIDENCE`
   below the confidence floor
4. **align** — solve the similarity transform onto `CANONICAL_TEMPLATE`; reject
   `POSE_TOO_EXTREME` if the residual exceeds `QualityThresholds.pose_residual_max`
5. **quality** — reject `BLUR` below `QualityThresholds.blur_min`, `ILLUMINATION` above
   `QualityThresholds.illumination_clip_max`

Every `Reject` carries an internal `detail` string (the exact measured value, for the log)
and an external `user_message` (`REJECT_MESSAGES[reason]`, under eight words, no numbers —
Exercise 3, Block 3) so the internal log and the phone screen never show the same string.

## Notes: why detect and landmark raise instead of returning a fake answer

No cat photograph exists yet to train a detector or landmark model against (`EVIDENCE.md`
Week 2, and OQ-011). Shipping a hand-tuned heuristic and calling it "the detector" would be
the exact failure this course spends two decks warning about: a plausible number nobody
measured. `default_detect` and `default_locate` raise a named exception instead, which
`process` converts to a stage-tagged reject — the same pattern `evals/run.py` already uses
for a suite that has not landed (`run_unimplemented_suite`), applied at the pipeline level.
Every other function in this task (`select`, `similarity_transform`, `warp_affine`,
`laplacian_variance`, `illumination_stats`) is real, working code, tested against synthetic
fixtures, with no dependency on a trained model or a real photograph.

## Acceptance criteria

| # | Assertion | Command that proves it |
|---|---|---|
| 1 | `quality.laplacian_variance(crop)` returns a float for a valid aligned crop and raises on a wrongly shaped input | `pytest ml/capture/test_quality.py -q` |
| 2 | A synthetic crop with Laplacian variance below `BLUR_THRESHOLD` is rejected; at or above it is accepted | `pytest ml/capture/test_quality.py -q` |
| 3 | `BLUR_THRESHOLD` is read from a single named constant, never repeated as a literal elsewhere in `ml/` | `pytest ml/capture/test_quality.py -k single_constant -q` |
| 4 | `similarity_transform` recovers a known rotation/scale/translation to within floating-point tolerance and reports near-zero residual | `pytest ml/capture/test_align.py -q` |
| 5 | `select` is deterministic: same candidates in, same choice out, across the largest → most-central → highest-confidence cascade | `pytest ml/capture/test_select.py -q` |
| 6 | `process` with the default (untrained) detector always rejects at stage `detect`, reason `DETECTOR_NOT_TRAINED`, never a false accept | `pytest ml/capture/test_pipeline.py -k not_trained -q` |
| 7 | `process` with injected fake detector/landmarker exercises the full happy path to `AlignedCrop` | `pytest ml/capture/test_pipeline.py -k happy_path -q` |
| 8 | Every `RejectReason` has an entry in `REJECT_MESSAGES` that is eight words or fewer and contains no digit | `pytest ml/capture/test_types.py -k reject_messages -q` |
| 9 | `warp_affine` under the identity transform reproduces the source region exactly (no stretching or bending — Idea 5) | `pytest ml/capture/test_align.py -k identity -q` |

## Out of scope

Liveness (REQ-002, Week 5), any server-side re-validation, training the detector or
landmark model.
