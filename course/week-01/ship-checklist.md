# Week 1 artifact — ship checklist

Due before session 2.

- [x] Public GitHub repository, committed under your own account
- [x] `specs/00-system-spec.md` — four primitives, entity state machines, budget table with defences
- [x] `specs/01-threat-model.md` — at least nine attacks, all seven columns, residual risk stated
- [x] `CLAUDE.md` — all seven sections
- [x] `make gate` green in CI on a real pull request
- [x] ADR-0001 written
- [x] `EVIDENCE.md` entry 1
- [ ] Capture homework started — see [homework-capture-protocol.md](homework-capture-protocol.md)

**Do not squash your history.** Small honest commits with real messages are the proof that
this happened over eight weeks rather than in one panicked weekend. The git log is evidence.

---

## How the artifact is graded

| Criterion | Points | Full marks looks like |
|---|---|---|
| System spec with four primitives and entity state machines | 2 | Every arrow labelled with actor and evidence |
| Budget table with a written defence per number | 2 | Each defence names what is traded away |
| Threat model, 9+ attacks, all columns | 2 | Residual risk stated for every row |
| `CLAUDE.md` with all seven sections | 1 | Includes the "when unsure, ask" rule |
| Green gate in CI on a real pull request | 2 | Four checks wired, one seen to fail and be fixed |
| ADR-0001 and evidence log entry 1 | 1 | Alternatives named, cost accepted |

**Nothing is deducted for a spec that turns out to be wrong later. Points are deducted for a
spec that cannot be shown wrong.**

---

## The evidence log, five minutes every week

Four questions, 150 words:

1. Which decision did I own this week?
2. What were the alternatives, and what did I give up?
3. What number or fact did I decide on?
4. What broke, and what did I change because of it?

Eight entries by Week 8 is a portfolio README, an activity description and two essay drafts,
assembled from work actually done.

---

## What not to claim

- Not "national-grade" or "deployed" → a working prototype, evaluated on N cats, with a
  pilot design.
- Not "solved pet abandonment" → built and measured one component of a proposed
  accountability system.
- Never a number without a method attached → every accuracy figure gets the dataset size and
  the phrase "on cats never seen in training".

The strongest sentence available at the end of Week 8:

> *"I built a system that can accuse someone, so I spent the first week deciding how often
> it was allowed to be wrong, and the last week proving it stayed inside that number."*

Nothing in a list of frameworks competes with that — and it is only true if Week 1 was run
properly.
