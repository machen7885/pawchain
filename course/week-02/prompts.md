# Week 2 — the four prompts

Run these in order. They map onto `specs/tasks/task-201.md` through `task-204.md`.

---

## P1 — golden set

```
Write specs/tasks/task-201.md for freezing a golden capture set. It must define the
label schema (usable / not_usable / reason), the manifest format with a SHA-256 per
image, where images live given REQ-009, and how a relabel is recorded. Acceptance
criteria as assertions with the command that proves each. No implementation.
```

Result: [`specs/tasks/task-201.md`](../../specs/tasks/task-201.md), the manifest schema in
[`evals/golden/capture/README.md`](../../evals/golden/capture/README.md), and the storage
decision in [ADR-0006](../../specs/decisions/ADR-0006.md).

---

## P2 — the eval before the model

```
Implement make eval-capture against specs/tasks/task-202.md. It reads the golden
manifest, computes per-stage yield and the blur sweep, writes evals/out/capture.json,
and fails if yield or threshold are absent. Stages that do not exist yet must report
"not implemented" and count as rejects — never as passes.
```

Result: [`evals/golden_capture.py`](../../evals/golden_capture.py) and the `capture` suite
in [`evals/run.py`](../../evals/run.py). Run it: `make eval-capture`. It exits non-zero
today — `status: "golden_set_empty"` — because the manifest has zero labelled images.

---

## P3 — the pipeline

```
Implement capture.process(frame) per specs/tasks/task-203.md: detect, select,
landmark, align, gate. It returns either an AlignedCrop or a Reject carrying stage
and reason. Every reject reason is an enum member, not a free string. Re-run
make eval-capture and report the change in each per-stage number.
```

Result: [`ml/capture/`](../../ml/capture/). Run the tests:
`pytest ml/capture -q`. There is no real per-stage number to report yet — every image
rejects at `detect` (`DETECTOR_NOT_TRAINED`) until the golden set exists, exactly as the
task brief's Notes section explains.

---

## P4 — export and measure

```
Export detector and aligner to ONNX per task-204.md. Report file sizes in bytes,
p50 and p95 single-frame latency over 200 runs after 20 warm-up runs, on CPU with
one thread. Then quantise to FP16, re-run make eval-capture, and report both the
new sizes and the change in yield. Do not report a size without a yield beside it.
```

Result: [`ml/capture/export.py`](../../ml/capture/export.py) — the export and
p50/p95-benchmark tooling, tested against a trivial dummy module. **Stops there.** No
detector or landmark model is trained yet, so there is nothing real to export; running
this tooling against an untrained network and reporting its size would satisfy the letter
of REQ-011 while violating the rule in the prompt above — a size with no yield beside it.
See the Notes section of [`task-204`](../../specs/tasks/task-204.md).

---

## If you run out of time

The pipeline, the eval harness, and the tooling all exist and are tested against synthetic
fixtures. What is missing is real data. Commit what exists, push it, and finish the capture
homework before Week 3 — a pushed, honestly-labelled "not yet measured" beats a faked
number every time.
