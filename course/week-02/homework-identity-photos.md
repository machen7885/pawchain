# Homework — the identity problem needs identities

Before session 3 (Week 3).

Week 3 measures whether the system can tell cats apart. With three cats a coin flip looks
impressive; identity *count*, not image count, is what makes that number mean anything —
which is why this homework expands the roster before it expands the model.

## Collect

- Expand from 3 cats to **at least 8** — neighbours, a shelter, a vet's waiting room,
  anyone who will let you.
- Per cat: **20 aligned-quality face captures** and **15 macro nose captures**, across
  **two separate days**.
- **If at all possible, one littermate pair.** Two cats that look alike is the single most
  valuable data point you can bring to Week 3 — it is what makes a dedup threshold mean
  anything (REQ-007, [OQ-001](../../specs/open-questions.md)).

## Before you collect

- Run every capture through your own pipeline on the spot
  (`python -c "from ml.capture import process; ..."` against a saved frame) and re-shoot
  anything it rejects, rather than finding out later.
- Record cat identity as a stable ID, not a name — two cats will be called Mimi.
- Never let one cat appear under two IDs. That single mistake makes every Week 3 number
  wrong in a direction you cannot detect afterwards.

## Label as you go, for `evals/golden/capture/manifest.json`

This is also the Week 2 golden-set homework, if you have not done it yet — see
[`evals/golden/capture/README.md`](../../evals/golden/capture/README.md) for the exact
schema. Sort each aligned crop `usable` / `not_usable` **before** looking at any measured
score; for a subset (landmarking is the expensive part — label only enough to check the
sweep is stable), also mark the five ground-truth points.

## Do not clean the data

The bad shots are the point. They are what the quality gate has to catch, and a cleaned
dataset silently deletes the evidence that the gate is needed at all (same rule as the Week
1 homework).

**`data/` is gitignored on purpose** — raw pet imagery is never committed to the repository
(threat model row 4: biometrics cannot be reissued after a breach). Keep the images local;
only the manifest — hashes, labels, points — goes in git.
