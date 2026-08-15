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

Planned contents:

| Path | Contents | Lands |
|---|---|---|
| `capture/` | Frames labelled usable / unusable, for REQ-001 | Week 2 |
| `identify/` | Held-out identities never seen in training, for REQ-003/004/005 | Week 3 |
| `dedup/` | Identity pairs including a labelled littermate slice, for REQ-007 | Week 3 |

Empty until Week 2, on purpose. The capture homework is what fills it.
