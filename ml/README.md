# ml/ — biometric engine (Weeks 2–4)

Detector, landmark aligner, embedding model, and the 1:N vector index.

Empty on purpose. Nothing is written here until `make gate` exists and can check it —
which is the entire point of Week 1.

| Lands | What |
|---|---|
| Week 2 | Cat face detection (YOLOv8 / RT-DETR), keypoint model, affine alignment, quality gating (REQ-001), ONNX export (REQ-011) |
| Week 3 | Metric-learning embedding (ArcFace-style angular margin), two-stream face + nose-print fusion, HNSW index, dedup (REQ-003 – REQ-007) |
| Week 4 | Auto-labelling pipeline, hard-negative mining on littermates, frozen golden sets, bad-slice discovery |

Constraint that shapes everything here: templates carry a `model_version` and templates
from different generations are never compared (REQ-008).
