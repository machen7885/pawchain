# Week 2 artifact — ship checklist

Due before session 3.

- [x] `ml/capture/` — `capture.process(frame)`, all five stages wired, tested against
  synthetic fixtures ([task-203](../../specs/tasks/task-203.md))
- [x] `make eval-capture` real and green-on-data, currently red-on-no-data —
  `status: "golden_set_empty"`, not a fake number ([task-202](../../specs/tasks/task-202.md))
- [x] `evals/golden/capture/manifest.json` — schema and tooling shipped, zero real entries
  ([task-201](../../specs/tasks/task-201.md))
- [x] Export/benchmark tooling built and tested, blocked on a trained model
  ([task-204](../../specs/tasks/task-204.md))
- [x] ADR-0004 (dependencies), ADR-0005 (blur threshold — proposed, pending measurement),
  ADR-0006 (where golden imagery lives)
- [x] Three reject messages, each under eight words, no numbers
  (`ml/capture/types.py::REJECT_MESSAGES`, tested)
- [ ] `EVIDENCE.md` entry 2 — **yours to write**, once you have run the sweep on your own
  photos (see below)
- [ ] Capture homework: expand to 8 cats, littermate pair if possible — see
  [homework-identity-photos.md](homework-identity-photos.md)

**What is honestly not done, and why:** REQ-001's number is still 120 — a Week 1 placeholder
— because no photograph has been labelled yet. REQ-011 (on-device model size) is `blocked`
in `evals/out/capture.json`, because no detector or landmark model is trained yet. Both are
tracked, not hidden: ADR-0005 and [OQ-011](../../specs/open-questions.md).

---

## How the artifact is graded

| Criterion | Points | Full marks looks like |
|---|---|---|
| `capture.process` implements all five stages with real, tested logic | 2 | `pytest ml/capture -q` green; detect/landmark honestly raise, not guess |
| `make eval-capture` measures for real, fails honestly without data | 2 | `capture.json` has a specific `status`, never a fabricated `accept_rate` |
| Golden set schema and manifest tooling | 1 | Loads, verifies hashes, records relabels without mutation |
| ADR-0005 names the exact procedure that replaces 120 | 1 | Sweep already implemented, waiting on data, not on more code |
| Reject messages pass the eight-word, no-numbers test | 1 | Enforced by a test, not a reviewer's eyeball |
| `EVIDENCE.md` entry 2 | 1 | Written by you, from your own sweep, once it exists |

**Nothing is deducted for `make eval-capture` still exiting non-zero.** Points are deducted
for a suite that reports a number nothing measured.

---

## The evidence log, five minutes, once you have real data

`EVIDENCE.md` entry 2 is deliberately left blank in this repository — it is written by the
architect, from the architect's own measurement, not generated ahead of the data it is
supposed to describe. Once you have run the sweep on your own photos:

1. Which decision did I own this week?
2. What were the alternatives, and what did I give up?
3. What number or fact did I decide on?
4. What broke, and what did I change because of it?

The shape a good entry 2 takes: *"My spec said reject a frame below a blur score of 120. I
had written that number before I owned a single photograph. I labelled 150 of my own crops
by hand, swept the threshold, and found that at 120 I was still admitting crops I had
personally marked unusable. I moved it, and I now reject more good frames than I would
like. I accepted that because a rejected frame costs a household seconds and an admitted
bad template raises a false-accept rate that costs someone a deposit. The spec now carries
the sweep table next to the number."*
