# Week 1 — Problem framing and the agent-native dev environment

**Turn a social problem into a system spec — then build the machine that builds the machine.**

Session 1 of 16 · 120 minutes · Ships: spec + threat model + working agent harness

---

## The claim this whole course rests on

> **The code is free now. The spec, the eval, and the gate are not.**

| An agent gives you for free | Nobody can generate for you |
|---|---|
| Working-looking implementations of anything with a name | Which errors you are willing to make, and at what rate |
| Boilerplate, wiring, refactors, tests written from a description | Who is authorised to change what, and on what evidence |
| Confident answers to questions it was never asked to verify | The number that decides whether it is done |

Every week you ship code. What you are actually graded on — by the eval harness, and later
by anyone reading this repository — is the set of decisions the code encodes.

---

## Session map

| Clock | Min | Block | You leave with |
|---|---|---|---|
| 0:00 | 12 | Why "just ask the AI" is not a plan | The six questions no prompt answers |
| 0:12 | 20 | Decompose: the four primitives | Entity list + state machines |
| 0:32 | 23 | The v1 spec: making disagreements decidable | Budget table with your numbers |
| 0:55 | 8 | Break | — |
| 1:03 | 22 | Threat model: who cheats, and how | Attack table, 7+ rows |
| 1:25 | 27 | Build the harness, live | Repo + CLAUDE.md + green CI gate |
| 1:52 | 8 | Ship, evidence log, homework | Week 1 artifact checklist |

---

## Block 0 — Why "just ask the AI" is not a plan

Type this. Watch what comes back.

```
Build me a pet ID system that recognises individual cats from their face and
nose print, stores an ID for each cat, and links it to the owner.
```

You will get a tidy FastAPI service with `/enroll` and `/verify`, a cosine-similarity
comparison, a database table — something that runs, imports cleanly and looks finished.

You will not get any statement of how often it is allowed to be wrong, any defence against
someone who *wants* it to be wrong, or any way to tell next month whether it got worse.

The output is not bad. **It is undecidable.** Nothing in it lets two people settle an
argument about whether it works.

### The six questions the generated code cannot answer

These are not gaps in the model's knowledge. They are choices, and choices belong to the
architect.

1. **Threshold.** At what similarity score do you declare "same cat"? Who chose that number, from what data?
2. **Error budget.** What false-accept rate is acceptable — and what happens to the household falsely matched to an abandoned cat?
3. **Liveness.** What stops me enrolling a photograph of a cat I found online?
4. **Uniqueness.** What stops the same cat being enrolled twice, by two different households?
5. **Versioning.** When the model is retrained next month, does an ID issued today still resolve to the same cat?
6. **Authority.** Who is allowed to assert "this cat is sterilised" — and what stops them lying for money?

Where each one landed in this repository: REQ-007 · ADR-0003 · REQ-002 · REQ-007 ·
REQ-008 · REQ-013.

### The division of labour for eight weeks

| Task | Owner | Because |
|---|---|---|
| Problem decomposition | **You** | Requires deciding what the system is for, which is not in any training set |
| Interface contracts | **You** | Two components agreeing is a negotiation, not a lookup |
| Thresholds and budgets | **You** | Encodes which harm you accept; a moral choice with a number attached |
| Threat model | **You** | Requires modelling an adversary's incentives, not the average case |
| Acceptance criteria | **You** | Defines "done"; if you don't, the agent will define it for you, generously |
| Implementation, tests, refactors, docs | Agent | Bounded, checkable, and cheaper than your time |

Consequence: you review gate results, not lines of code. Building the gate is therefore the
first week's job.

---

## Block 1 — Decompose: the four primitives

Four moves from problem to spec, and they transfer to any system:

1. **Write the outcome as one sentence a stranger could check.** Not a mission — a
   checkable claim. Ours: *a specific animal is bound to a specific responsible household,
   and a stranger can verify that binding in under 30 seconds with a phone.*
2. **List the nouns that must survive a server restart.** Those are your entities. Anything
   not on the list is a screen, not a thing.
3. **For each entity, write its states and transitions.** A system is its state machine; the
   rest is presentation.
4. **Attack each transition with two questions:** who is authorised to trigger it, and what
   evidence must exist first? A transition failing either is a design bug, not an
   implementation bug.

### The delete test

| Primitive | The question it answers | Delete it and… |
|---|---|---|
| Identity | Which animal is this, independent of collar, chip or claim? | Registration is a name on paper. Nothing is verifiable, so nothing is enforceable |
| Registration | Which household is answerable, and since when? | You can recognise a cat and still have nobody to hold responsible |
| Attestation | Who is trusted to assert a fact, and how do we check? | Sterilisation status is self-reported, and self-reported compliance is not compliance |
| Incentive | Why would any household do this at all? | A beautiful registry with zero rows in it |

Order matters: Weeks 2–4 build Identity, Week 5 Registration, Weeks 6–7 Attestation and
Incentive. Each is worthless before the one under it exists. That is the reason for the
sequence, not tradition.

Result in this repo: [`specs/00-system-spec.md` §4](../../specs/00-system-spec.md).

---

## Block 2 — Making disagreements decidable

> **A requirement is finished when two people who disagree can settle it without a third
> person.**

| Undecidable | Decidable |
|---|---|
| "The system should identify cats accurately and be fast enough for real use." | "On 200 held-out cats never seen in training, top-1 identification is ≥ 90% and FAR ≤ 1% at the operating threshold. Measured by `make eval-identify`. Reported on every commit. Below target blocks the merge." |

The second version is not more *detailed*. It is **falsifiable** — the only property that
makes an agent's work checkable at speed.

### Four fields. No exceptions.

| Field | Asks | Example |
|---|---|---|
| **behaviour** | What does the system do, in one clause? | Reject an enrolment whose face crop is too blurred to embed |
| **number** | What is the threshold or budget? | Laplacian variance below 120 on the aligned crop |
| **measurement** | What command produces that number? | `make eval-capture`, writes `evals/out/capture.json` |
| **consequence** | What happens when it fails? | Camera re-prompts the user; the frame is never sent to the server |

Behaviour tells the agent what to build. Number stops it inventing one. Measurement turns
your opinion into a file. Consequence is the part everyone skips, and it is where the
product actually lives.

Two things that are not answers: *"measurement: manual testing"* is not a measurement, it is
a mood. *"consequence: we fix it"* names no machine, and a consequence is enforced by a
machine or it does not exist.

### The most important idea in the session

One dial:

```
Turn it up   ->  fewer wrong matches, more failed scans.
Turn it down ->  fewer failed scans, more wrong matches.

There is no position where both are zero.
So the question is never "how accurate is it".
The question is "which mistake am I willing to make, and how often".
```

**FRR** — a known cat is not recognised. The user scans again. Cost: annoyance, in seconds.
**FAR** — a cat matches the wrong household. An innocent household is accused of
abandonment and loses a deposit. Cost: injustice, in money and reputation.

Result in this repo: [ADR-0003](../../specs/decisions/ADR-0003.md) and the budget table in
the spec.

---

## Block 3 — Threat model: who cheats, and how

Any system that touches money grows an adversary. The moment a refundable deposit exists,
three populations appear that did not before: people who want the money back without doing
the thing, people who want someone else blamed, and people who want the database.

Every row of the threat table has seven columns:

```
attack:                    signal it leaves:
actor:                     mitigation:
cost to attacker:          ships in week:
                           residual risk we accept:
```

The last line is compulsory. **A threat model with no accepted residual risk is a fantasy,
and reviewers know it.** And the column people forget is *cost to attacker*: attacks do not
need to be impossible, only to cost more than the deposit is worth.

Two things to notice in the finished table: every mitigation is a **gate, a rate limit, or a
human** — not one of them is a better model, because accuracy is not a security strategy.
And **template theft** is the row to understand: a password can be changed after a breach, a
cat's nose print cannot. That asymmetry is the whole argument for storing hashes and
templates rather than images, and it is a much better answer than "for privacy".

Result in this repo: [`specs/01-threat-model.md`](../../specs/01-threat-model.md) — 13
attacks, all seven columns.

---

## Block 4 — Build the harness, live

| Chat-driven | Spec-driven |
|---|---|
| The requirement lives in a conversation | The requirement lives in a file, under version control |
| You verify by reading the output and feeling satisfied | A test proves it; CI runs the test; the gate blocks the merge |
| Correctness is whatever you remembered to check | Correctness is a number on every commit |
| Week 6 you cannot say why Week 2 works | Week 6 the repository explains Week 2 to you |

Chat-driven is fine for a weekend project. It fails on anything you have to defend. The
overhead of spec-driven is one week; the payoff is the other seven.

### A harness is everything that makes agent output checkable without reading it

| Component | Lives at | Its one job |
|---|---|---|
| Constitution | `CLAUDE.md` | Standing rules the agent reads before every task |
| Specs | `specs/*.md` | The requirement of record |
| Task briefs | `specs/tasks/*.md` | One unit of work, with acceptance criteria attached |
| Gates | `Makefile` + CI | Lint, types, tests, evals. Red means not done, regardless of opinion |
| Golden sets | `evals/golden/` | Frozen data, never trained on. The only defence against silent regression |
| Decision records | `specs/decisions/` | Why you chose this over that |

Six files and one CI workflow. That is the whole of harness engineering at this scale.

### The loop you will run 200 times

```
write task spec  →  agent implements  →  make gate  →  review the diff  →  merge
                         ↑                   │              (against the spec,
                         └─────── red ───────┘               not line by line)
```

You never enter the red loop — the agent reads the gate output and fixes its own work. Your
only two jobs are writing the task spec at the front and judging the diff against it at the
back. Three failed gate cycles on the same task means the spec is wrong, not the agent. And
if you are pasting error messages back and forth, the gate is not wired to the agent yet.

The four prompts are in [`prompts.md`](prompts.md).

### The moment that matters

Break it on purpose. Ask the agent to add an unused import, then run the gate:

```
$ make gate
ruff .................. FAIL
  evals/run.py:12 unused import
types ................. skipped
test .................. skipped
eval .................. skipped
gate: BLOCKED
```

Then ask it to fix its own failure. It reads the output and repairs it.

You just built something that can say no to an AI on your behalf, and enforce it in a
repository you own. From here on, "is it done" has an answer that does not depend on
anyone's opinion. A gate you have never seen fail is not a gate you should trust.

---

## Ship checklist

See [`ship-checklist.md`](ship-checklist.md). Homework: [`homework-capture-protocol.md`](homework-capture-protocol.md).

## Next week

**You train a model. This week you built the thing that decides if it worked.**
