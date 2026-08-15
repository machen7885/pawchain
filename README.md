# PawChain ID

An open-set biometric identity system for individual cats, bound to a responsible
household, with vet-attested sterilisation status and a refundable deposit.

**A specific animal is bound to a specific responsible household, and a stranger can
verify that binding in under 30 seconds with a phone.**

That is the outcome sentence. It is checkable by someone who does not work here, and every
change is judged against it.

> Prototype, pilot scale, single city. Not a deployed product, and not a claim of
> regulatory adoption. See [What this is not](#what-this-is-not).

---

## Status

| Week | Ships | State |
|---|---|---|
| **1 — Problem framing and the agent-native dev environment** | Spec + threat model + monorepo scaffold with a working agent harness | ✅ done |
| 2 — Cat detection and landmark alignment | Real-time capture pipeline: phone frame in → aligned, quality-gated crops out | planned |
| 3 — Nose-print and facial embeddings | Embedding service, open-set accuracy, sub-100 ms 1:N lookup | planned |
| 4 — Agentic data engineering and the eval harness | Data flywheel + eval dashboard; quality becomes a CI number | planned |
| 5 — The registry | End-to-end enrollment: scan a real cat, get a PetID issued | planned |
| 6 — Identity layer: DID, VCs, soulbound PetID | PetID contract on a local consortium devnet, wired to the registry | planned |
| 7 — Accountability engine | register → deposit → vet attests → release; report → match → adjudicate → slash | planned |
| 8 — Integration, hardening, demo day | Live demo, whitepaper, pitch deck | planned |

---

## Start here

| Read | For |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | The project constitution. Every agent reads this before every task |
| [`specs/00-system-spec.md`](specs/00-system-spec.md) | The requirement of record: primitives, state machines, budgets, REQ-001 – REQ-018, scope |
| [`specs/01-threat-model.md`](specs/01-threat-model.md) | 13 attacks, seven columns each, residual risk stated on every row |
| [`specs/02-glossary.md`](specs/02-glossary.md) | The terms, so two people can argue precisely |
| [`specs/decisions/`](specs/decisions/) | Why this and not that — including why there is a chain at all |
| [`specs/open-questions.md`](specs/open-questions.md) | What is still undecided, and what will decide it |
| [`EVIDENCE.md`](EVIDENCE.md) | The weekly log: which decision was owned, and what it cost |

---

## Verify

```bash
pip install ruff pyright pytest
make gate
```

`make gate` runs lint → types → tests → evals, in that order, and stops at the first
failure. It is the only definition of correctness in this project. CI runs the same command
on every pull request and every push to `main`, so the agent, the CI server and a human all
check identically.

```
ruff .................. PASS
types ................. PASS
test .................. PASS  5 passed
eval .................. PASS  metrics written
gate: GREEN
```

Per-requirement measurements run separately: `make eval-capture`, `eval-identify`,
`eval-dedup`, `eval-search`, `eval-liveness`, `eval-policy`. Each one that is scheduled for
a later week **exits non-zero** rather than printing a placeholder, because a requirement
that looks measured when nothing measured it is worse than one that is openly unmeasured.

---

## How this repository is built

This is an agent-first codebase. The specs are written before the code, the gate is built
before the implementation, and an agent does the typing.

```
write task spec  →  agent implements  →  make gate  →  review the diff  →  merge
                         ↑                   │
                         └─────── red ───────┘
```

Six files and one CI workflow are the whole of the harness:

| Component | Lives at | Its one job |
|---|---|---|
| Constitution | `CLAUDE.md` | Standing rules the agent reads before every task |
| Specs | `specs/*.md` | The requirement of record. The agent implements the file, not a mood |
| Task briefs | `specs/tasks/*.md` | One unit of work, with acceptance criteria attached |
| Gates | `Makefile` + CI | Lint, types, tests, evals. Red means not done, regardless of opinion |
| Golden sets | `evals/golden/` | Frozen data, never trained on. The only defence against silent regression |
| Decision records | `specs/decisions/` | Why this over that |

The honest answer to "you did not really build it, the AI did": the thing that decides
whether the AI's work is acceptable is in this repository, dated, and it has rejected work.

---

## Layout

```
CLAUDE.md            constitution
Makefile             one entry point: make gate
EVIDENCE.md          weekly log
specs/               the requirement of record
  tasks/  decisions/  open-questions.md
evals/
  golden/            frozen, never trained on
  out/               gitignored metrics
ml/                  weeks 2-4    api/         week 5
contracts/           weeks 6-7    miniapp/     week 5
course/              8-week session material
.github/workflows/gates.yml
```

`course/` holds the teaching material for the programme this project is built in. It is not
part of the system, nothing imports from it, and it is excluded from lint and type checking.

---

## The one idea worth taking away

One threshold controls both error rates, in opposite directions. There is no setting where
both are zero.

- A **false reject** means someone scans their cat again. The cost is annoyance, measured
  in seconds.
- A **false accept** means an innocent household is accused of abandonment and loses a
  deposit. The cost is injustice, measured in money and reputation.

So the threshold is not chosen by maximising accuracy. It is chosen by deciding which harm
you are willing to cause, and how often. We chose FAR ≤ 1% and FRR ≤ 10%
([ADR-0003](specs/decisions/ADR-0003.md)) — we would rather inconvenience ten people than
falsely accuse one. Because 1% of matches will be wrong by design, every penalty path runs
through a human adjudicator and a 30-day appeal window.

---

## What this is not

- **Not national-grade, and not deployed.** A working prototype, evaluated on N cats, with
  a pilot design.
- **Not a solution to pet abandonment.** One measured component of a proposed
  accountability system.
- **Not novel recognition.** Commercial pet nose-print apps exist and animal
  re-identification is an active research field. The recognition is the known part. The
  contribution is binding recognition to an accountability mechanism with a measured error
  budget and a human appeal path.
- **Not an authority.** The system produces evidence for humans who have authority. It has
  none.
- **No accuracy number without a method.** Every figure gets its dataset size and the phrase
  "on cats never seen in training", or it does not get published.

---

Built with Han's Applied AI Tutoring — 8-week applied AI intensive.
Licensed under the MIT License. See [LICENSE](LICENSE).
