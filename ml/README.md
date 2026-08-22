# ml/ — biometric engine (Weeks 2–4)

Detector, landmark aligner, embedding model, and the 1:N vector index.

| Lands | What | Status |
|---|---|---|
| Week 2 | `capture.process(frame)`: detect, select, landmark, align, quality-gate (REQ-001); export/benchmark tooling (REQ-011) | pipeline and gate implemented and tested (`ml/capture/`); detector and landmark model not trained yet — blocked on the golden set (`specs/open-questions.md` OQ-011) |
| Week 3 | Metric-learning embedding (ArcFace-style angular margin), two-stream face + nose-print fusion, HNSW index, dedup (REQ-003 – REQ-007) | not started |
| Week 4 | Auto-labelling pipeline, hard-negative mining on littermates, frozen golden sets, bad-slice discovery | not started |

## `ml/capture/`

`capture.process(frame)` — phone frame in, `AlignedCrop` or a stage-tagged `Reject` out.
Five stages (`specs/tasks/task-203.md`): `detect.py`, `select.py`, `landmark.py`,
`align.py`, `quality.py`, wired together in `pipeline.py`. `export.py` holds the
ONNX-export and latency-benchmark tooling (`specs/tasks/task-204.md`).

`detect.py` and `landmark.py` intentionally raise (`DetectorUnavailable`,
`LandmarkerUnavailable`) rather than guessing — no model has been trained yet, because no
labelled photograph exists yet. `capture.process` turns that into an honest, stage-tagged
reject. Every other stage (`select`, `align`, `quality`) is real, working code.

Constraint that shapes everything here: templates carry a `model_version` and templates
from different generations are never compared (REQ-008).
