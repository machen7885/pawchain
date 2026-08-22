# evals/golden/capture/ — the REQ-001 answer key

`manifest.json` is currently empty (`"images": []`), on purpose — no photograph has been
labelled yet (`EVIDENCE.md`, Week 2). `make eval-capture` reads this file first and reports
`status: "golden_set_empty"` and exits non-zero until it has real entries, rather than
printing a plausible number (ADR-0005).

This file holds only labels, hashes and (for a subset) hand-marked landmark points — never
image bytes. See `specs/decisions/ADR-0006.md` for where the pixels themselves live.

## How to fill this in

1. Capture photos with your own phone, following the same protocol as the Week 1 homework
   (`course/week-01/homework-capture-protocol.md`) — or the expanded one due before Week 3
   (`course/week-02/homework-identity-photos.md`) — and put the resulting images under
   `$PAWCHAIN_GOLDEN_IMAGES` (defaults to `data/golden/capture/`, already gitignored).
2. Sort 150 of the resulting **aligned** crops by eye into `usable` / `not_usable`, and for
   `not_usable` pick a reason: `no_cat`, `wrong_crop`, `blur`, `pose`, `illumination`, or
   `other`. Do this before looking at any measured score (facilitator guide, Idea 12).
3. For a subset of those — landmarking is the expensive part, so label only enough to check
   the sweep is stable (facilitator guide, Idea 4) — also mark the five ground-truth
   landmark points (`left_eye`, `right_eye`, `nose`, `left_ear`, `right_ear`, each an
   `[x, y]` pixel pair on the *original*, unaligned frame). These are what let
   `make eval-capture` compute the blur/pose/illumination sweep before a landmark model is
   trained (task-202) — the threshold question and the model-training question are
   deliberately decoupled.
4. Compute each file's SHA-256 (`shasum -a 256 <file>` or `hashlib.sha256` in Python) and
   add one entry to `manifest.json["images"]` per the schema in
   `specs/tasks/task-201.md`.
5. Run `make eval-capture`. It verifies every hash before computing anything, and fails
   loudly — `status: "integrity_error"` — if a file's bytes no longer match what the
   manifest recorded.
6. Never edit a label directly in this file once it is committed. Use
   `evals/golden_capture.py::record_relabel`, which returns a new manifest and appends an
   entry to `relabels` explaining why, in a commit that touches nothing else.

## Schema

See `specs/tasks/task-201.md` for the full field table. Minimal example:

```json
{
  "version": 1,
  "images": [
    {
      "id": "cat3-session1-0007",
      "relative_path": "cat3/session1/0007.jpg",
      "sha256": "…",
      "label": "not_usable",
      "reason": "blur",
      "landmarks": null
    }
  ],
  "relabels": []
}
```
