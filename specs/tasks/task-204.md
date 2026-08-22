# task-204 — Export and measure: the tooling, ready before there is a model

**Implements** REQ-011 (`specs/00-system-spec.md` §6) · **Week** 2 ·
**Status** infrastructure done; blocked on a trained model (OQ-011)

## Goal

Build and test the export and benchmarking path so that the day a detector and landmark
model exist, turning them into on-device artefacts is a function call, not a research
project: export to ONNX, measure the real file size, measure p50/p95 latency correctly
(warm-up excluded, tail reported, whole-function timing — Block 4, "Benchmark honestly or
do not benchmark"), and never let a size be reported without a yield beside it.

## Files touched

- `ml/capture/export.py` — `export_onnx`, `file_size_bytes`, `benchmark`
- `ml/capture/test_export.py`

## Behaviour

- `export_onnx(model, dummy_input, path)` — lazily imports `torch`; calls
  `torch.onnx.export`; lazily imports `onnx` to run `onnx.checker.check_model` on the result
  before returning the path. Raises rather than returning a path to an artefact that failed
  validation.
- `file_size_bytes(path)` — the real byte count on disk. No estimate.
- `benchmark(fn, *, n=200, warmup=20)` — runs `fn` `warmup` times and discards those results,
  then runs it `n` more times on a single thread, and returns `p50`, `p95`, and the discarded
  `cold_start` (the first warm-up call, timed and kept, because a user feels it once per
  session — Block 4, "Cold versus warm").

## Why this stops here this week

No detector or landmark model has been trained (task-203's Notes, OQ-011) — there is
nothing real to export yet. Running `export_onnx` against an untrained, randomly-initialised
network and reporting its size would satisfy the letter of REQ-011 while violating its
point: a size number is only useful next to a yield number from the same model
(`evals/out/capture.json`), and an untrained model's yield is meaningless noise, not zero.
This task therefore ships the tooling, tested against a trivial dummy `torch.nn.Module`
that is never presented as a cat model, and stops. `evals/out/capture.json`'s `req_011`
field stays `{"status": "blocked", "reason": "no trained detector or landmark model exists
yet"}` until a real model exists to run through this path.

## Acceptance criteria

| # | Assertion | Command that proves it |
|---|---|---|
| 1 | `export_onnx` on a trivial dummy module produces a file that `onnx.checker.check_model` accepts | `pytest ml/capture/test_export.py -k export -q` |
| 2 | `export_onnx` raises, and writes no file, if the exported graph fails validation | `pytest ml/capture/test_export.py -k invalid -q` |
| 3 | `file_size_bytes` returns the exact byte count of the exported file | `pytest ml/capture/test_export.py -k size -q` |
| 4 | `benchmark` excludes warm-up runs from `p50`/`p95`, and `p50 <= p95` holds on every run | `pytest ml/capture/test_export.py -k benchmark -q` |
| 5 | `benchmark` reports `cold_start` separately and it is never averaged into `p50`/`p95` | `pytest ml/capture/test_export.py -k cold_start -q` |

## Out of scope

Training the detector or landmark model. Quantisation (FP16/INT8) — the utility here
operates on whatever `torch.nn.Module` it is given; choosing and training that module is
future work tracked at OQ-011.
