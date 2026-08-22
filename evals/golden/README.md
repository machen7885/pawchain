# evals/golden/ — frozen evaluation data

**Nothing in this folder is ever used for training, tuning, threshold selection or
augmentation.** The moment you tune against it, your numbers stop being measurements and
become marketing.

Rules:

1. Do not modify, move, or delete anything here.
2. Adding data is a deliberate, reviewed act with its own commit and a note saying where
   the data came from and which identities it contains.
3. No identity that appears here may appear in any training or validation split. An
   identity leaking across splits makes every number in the repository meaningless — this
   is the failure mode that is easiest to cause and hardest to notice.
4. Raw pet imagery is never committed. Golden sets reference data by content hash and are
   fetched from the pilot store; only labels, splits and hashes live in git.

Contents:

| Path | Contents | Lands | Status |
|---|---|---|---|
| `capture/` | Frames labelled usable / unusable, for REQ-001 | Week 2 | schema and manifest tooling shipped (task-201); `manifest.json` has zero real entries — see `capture/README.md` |
| `identify/` | Held-out identities never seen in training, for REQ-003/004/005 | Week 3 | not started |
| `dedup/` | Identity pairs including a labelled littermate slice, for REQ-007 | Week 3 | not started |

`capture/manifest.json` is real, loadable, and tested against synthetic fixtures
(`evals/test_golden_capture.py`) — it is simply empty, because no photograph has been
labelled yet. `make eval-capture` says so explicitly rather than reporting a number nothing
measured (ADR-0005).
