# Week 2 — Cat detection and landmark alignment

**Before you can recognise a cat you must find it and normalise it — at phone-camera
quality, on your own photographs.**

Session 3 of 16 · 120 minutes · Ships: a capture pipeline that turns a phone frame into an
aligned, quality-gated crop, or a labelled reason it could not.

---

## Where we are

Week 1 built the judge — the gate, the spec, the threat model. Week 2 gives it something to
judge.

| Requirement | Status before this week | Status after this week |
|---|---|---|
| REQ-001 (capture quality gate) | `make eval-capture` exits non-zero; nothing measures it | Implemented and tested; still exits non-zero — `status: "golden_set_empty"` — because no photograph has been labelled yet ([ADR-0005](../../specs/decisions/ADR-0005.md)) |
| REQ-011 (on-device model size) | No artefacts exist | Export/benchmark tooling built and tested (task-204); nothing to export yet — no detector or landmark model is trained ([OQ-011](../../specs/open-questions.md)) |

**The claim this week rests on:** geometry beats architecture. Alignment is the accuracy
lever, not the model — a mediocre backbone on well-aligned crops beats a strong backbone on
raw ones. This is why Week 2 is its own week rather than a footnote to Week 3.

---

## The five stages

`capture.process(frame)` — one function, phone frame in, `AlignedCrop` or a labelled
`Reject` out. No third outcome.

| Stage | Question it asks | When it refuses |
|---|---|---|
| 1 · Detect | Is there a cat in this photo, and where? | No cat found — or, today, no detector is trained yet |
| 2 · Select | Two candidates. Which one do we mean? | Genuinely cannot tell |
| 3 · Landmark | Where exactly are the eyes, the nose, the ear tips? | Cannot find them confidently — or, today, no landmark model is trained yet |
| 4 · Align | How do I rotate and resize this so those points land in standard positions? | The head is turned too far to fix |
| 5 · Quality | Is this picture actually good enough to use? | Too blurry, too dark, too bright |

Find it, straighten it, judge it. Any one of the five can say no. See
[`ml/capture/`](../../ml/capture/) and [task-203](../../specs/tasks/task-203.md).

## Why stages 1 and 3 honestly say "not yet"

No detector or landmark model exists, because no labelled photograph exists yet — training
either needs the golden set, and the golden set needs your cats. `ml/capture/detect.py` and
`ml/capture/landmark.py` raise a named, caught exception rather than guessing. Stages 2, 4
and 5 are real, working code today: the selection rule, the similarity-transform alignment,
and the three-signal quality gate (blur, pose residual, illumination) are all pure
arithmetic, tested against synthetic fixtures, no model or real photograph required.

## Rejects multiply, they do not add

Five stages each passing 90% of what reaches them is not 90% end to end — it is roughly
59%. `evals/golden_capture.py::stage_yield` reports each stage's yield separately, never a
single blended number, for exactly this reason.

## Where 120 came from, and why it hasn't moved

REQ-001 rejects a blur score below 120. That number was written in Week 1, before a single
photograph existed — a placeholder wearing the costume of a decision. It moves only once
150 of your own aligned crops are labelled and swept ([ADR-0005](../../specs/decisions/ADR-0005.md)).
`make eval-capture` already runs the real sweep; it is just waiting for real data.

---

## Ship checklist

See [`ship-checklist.md`](ship-checklist.md). Homework: [`homework-identity-photos.md`](homework-identity-photos.md).

## Next week

**You can now find a cat's face and put it in the same place every time. Next week you find
out whose it is.**
