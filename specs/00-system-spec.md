# PawChain ID — system spec v0.1

Status: draft · Owner: Han's Applied AI Tutoring / PawChain ID · Last updated: 2026-08-15

This file is the requirement of record. Code implements this file; this file never
documents code after the fact. Every number below is a chosen number, and every chosen
number carries the defence for choosing it. A number with no defence is not a decision,
it is a default someone else picked.

---

## 1. Outcome

A specific animal is bound to a specific responsible household, and a stranger can
verify that binding in under 30 seconds with a phone.

That sentence is checkable by someone who does not work here. If a change to this system
does not make that sentence more true, it is out of scope.

### What is already solved, and what is not

Cat face recognition and pet nose-print matching exist commercially, and animal
re-identification is an active academic field. The recognition is the known part. What is
unbuilt — and what this project contributes — is **binding recognition to an
accountability mechanism with a measured error budget and a human appeal path.** Claims
in this repository are limited to that.

---

## 2. The four primitives

Derived by the delete test: remove one and state what collapses.

| Primitive | Question it answers | Delete it and | Built in |
|---|---|---|---|
| Identity | Which animal is this, independent of collar, chip or claim? | Registration is a name on paper. Nothing is verifiable, so nothing is enforceable | Weeks 2–4 |
| Registration | Which household is answerable, and since when? | You can recognise a cat and still have nobody to hold responsible | Week 5 |
| Attestation | Who is trusted to assert a fact, and how is it checked? | Sterilisation status is self-reported, and self-reported compliance is not compliance | Weeks 6–7 |
| Incentive | Why would any household do this at all? | A beautiful registry with zero rows in it | Week 7 |

Order matters. Each primitive is worthless before the one under it exists. That is the
reason for the 8-week sequence, not tradition.

---

## 3. Repository structure

```
pawchain-id/
  CLAUDE.md            constitution
  Makefile             one entry point: make gate
  EVIDENCE.md          weekly log
  specs/
    00-system-spec.md
    01-threat-model.md
    02-glossary.md
    open-questions.md
    tasks/
    decisions/
  evals/
    golden/            frozen, never trained on
    out/               gitignored metrics
  ml/                  weeks 2-4
  api/                 week 5
  contracts/           weeks 6-7
  miniapp/             week 5
  .github/workflows/gates.yml
```

Rules that make this work:

- `specs/` before code. No pull request without a spec file it references.
- One entry point. Everything runs through `make gate`, so the agent, CI and a human all
  check identically.
- `evals/golden/` is sacred. Nothing in it is ever used for training, tuning or threshold
  selection, or the numbers become fiction.
- Empty folders now. The structure is a promise about where things go; an agent told to
  "put it somewhere sensible" will invent four different sensible places.

---

## 4. Entities and states

The entities are the nouns that must survive a server restart. Anything not listed here is
a screen, not a thing.

**Entities:** PetID · Household · Deposit · Attestation · Case · Template

For every transition, two questions must be answered: **who may trigger it**, and **what
evidence must exist first**. A transition failing either question is a design bug, not an
implementation bug — and it is where fraud enters.

### 4.1 PetID

States: `unenrolled` → `pending_dedup` → `active`, with `transfer_pending`,
`reported_missing`, `case_open`, `adjudicated`, and terminals `rejected_dup`, `revoked`,
`deceased`.

| From | To | Trigger | Actor | Evidence required |
|---|---|---|---|---|
| unenrolled | pending_dedup | enrolment submitted | household | 5+ quality-gated frames (REQ-001) + liveness pass (REQ-002) + proof of custody (REQ-016) |
| pending_dedup | active | no duplicate found | system | 1:N top-1 similarity below dedup threshold (REQ-007) |
| pending_dedup | rejected_dup | duplicate found | system | 1:N top-1 at or above dedup threshold (REQ-007) |
| rejected_dup | pending_dedup | dedup appeal upheld (littermate case) | registry admin | admin review record + both PetIDs' capture sets side by side |
| active | transfer_pending | transfer initiated | current household | signed transfer request from current household key |
| transfer_pending | active | transfer ceremony complete | system | both households' signatures + cooling period elapsed (REQ-014) |
| transfer_pending | active | transfer cancelled or expired | either household, or system | cancellation signature, or cooling-period timeout |
| active | reported_missing | loss reported | household | signed report from binding household |
| reported_missing | active | animal recovered | household | signed recovery statement, or 1:1 verification at reunion |
| active / reported_missing | case_open | abandonment case opened | reporter, via registry | 1:N match above threshold + evidence bundle (REQ-018) |
| case_open | adjudicated | adjudicator rules | registry adjudicator (human) | written finding, referencing the evidence bundle (REQ-010) |
| adjudicated | active | finding dismissed, or appeal upheld | adjudicator | dismissal record, or new evidence inside appeal window (REQ-015) |
| active | revoked | fraudulent enrolment established | registry admin | adjudicated finding of enrolment fraud |
| active | deceased | death recorded | household + vet | vet-signed death attestation VC |

Notes on the diagram:

- `case_open → adjudicated → deposit_slashed` is the only path that takes money from a
  person. All of Week 7 exists to make that path survive scrutiny.
- There is no automated edge into any penalty state. Every one passes through a human.

### 4.2 Deposit

States: `not_posted`, `held`, `releasable`, `released`, `contested`, `slashed`,
`refunded`, `released_to_prior_owner`.

| From | To | Trigger | Actor | Evidence required |
|---|---|---|---|---|
| not_posted | held | household pays deposit | household | payment confirmation from the escrow contract |
| held | releasable | sterilisation attested | licensed vet | vet-signed VC, issuer key valid and not revoked at signing time (REQ-013) |
| releasable | released | automatic, after 24h delay | system | delay elapsed and no case opened in the window |
| held | contested | abandonment case opened | reporter, via registry | evidence bundle admitted (REQ-018) |
| contested | slashed | adjudicator upholds the report | registry adjudicator (human) | written finding (REQ-010) |
| contested | held | adjudicator dismisses the report | registry adjudicator (human) | written dismissal |
| held | refunded | animal died | household + vet | vet-signed death attestation VC |
| held | released_to_prior_owner | transfer ceremony completed | system | completed two-party transfer (REQ-014); the incoming household posts its own deposit |
| slashed | contested | appeal filed with new evidence, once only | prior household | new evidence inside the appeal window (REQ-015) |

**`slashed` is deliberately not terminal.** The 24-hour release delay and the single
appeal edge are the two mechanisms that let this system correct its own errors. A deposit
scheme with no path back from a slash cannot correct a false accusation, and a scheme that
cannot correct a false accusation is politically undeployable — nobody would rationally
post a deposit into it. The appeal edge is not a courtesy; it is the reason the primitive
works at all.

**The vet-licence problem has no good transition.** If a vet loses their licence after
signing, there is no state in this machine that repairs the attestations they already
issued. That gap forces a **revocation registry** with attestation validity evaluated at
signing time, not at read time — otherwise a single revocation retroactively invalidates
every deposit that vet ever released. Recorded as open question OQ-004.

### 4.3 Attestation

States: `issued`, `verified`, `expired`, `revoked`.

| From | To | Trigger | Actor | Evidence required |
|---|---|---|---|---|
| — | issued | vet signs a claim about a PetID | licensed vet | vet signing key, active in the registry at signing time |
| issued | verified | registry validates signature and issuer | system | signature valid, issuer key in registry, not revoked as of the signing timestamp |
| verified | expired | validity period elapses | system | attestation type's stated validity window |
| verified | revoked | issuer key revoked, or attestation withdrawn | registry admin | revocation record naming the reason and the effective date |

### 4.4 Case

States: `reported`, `evidence_bundled`, `open`, `adjudicated_upheld`,
`adjudicated_dismissed`, `appealed`, `closed`.

| From | To | Trigger | Actor | Evidence required |
|---|---|---|---|---|
| — | reported | found-cat scan submitted | any reporter | scan meeting capture quality gate (REQ-001) |
| reported | evidence_bundled | 1:N match above threshold | system | match score, matched PetID, scan metadata, reporter identity |
| evidence_bundled | open | bundle admitted | registry admin | rate limits and reporter reputation checks passed (REQ-017) |
| open | adjudicated_upheld / adjudicated_dismissed | adjudicator rules | registry adjudicator (human) | written finding (REQ-010) |
| adjudicated_upheld | appealed | appeal filed, once only | accused household | new evidence, inside the appeal window (REQ-015) |
| any adjudicated state | closed | appeal window elapses | system | window elapsed with no admitted appeal |

### 4.5 Household and Template

- **Household** — `unverified` → `verified` → `suspended`. A household is the unit that is
  answerable. Verification is out of v1 scope beyond a WeChat-bound account; recorded as
  open question OQ-002.
- **Template** — a 512-d embedding plus the model version that produced it. Templates are
  immutable. A retrained model produces a new template generation; templates of different
  generations are never compared (REQ-008).

---

## 5. Budgets

A number without a defence in the right-hand column is not a chosen number.

| Budget | v1 target | Defence — what this trades away |
|---|---|---|
| Enrolment time, phone in hand | ≤ 3 min | Longer capture gives better templates and more abandoned sign-ups |
| 1:N search, 100k index | ≤ 100 ms | Faster search costs index memory and a coarser recall stage |
| Top-1 identification, unseen cats | ≥ 90% | Every extra point costs data collection we have to do ourselves |
| False accept rate at operating threshold | ≤ 1% | Tightening raises false rejects |
| False reject rate | ≤ 10% | Loosening lets wrong matches through |
| On-device model size | ≤ 25 MB | Mini-program package limit; a bigger backbone means a server round-trip |
| Time from case opened to adjudication | ≤ 7 days | Faster costs adjudicator capacity; slower leaves a household under accusation |
| Appeal window after a slash | 30 days | Longer delays the community fund; shorter denies a real appeal the time to gather evidence |

### The asymmetry that sets the threshold

One dial controls both error rates.

```
Turn it up   ->  fewer wrong matches, more failed scans.
Turn it down ->  fewer failed scans, more wrong matches.
```

There is no position where both are zero. So the threshold is not chosen by maximising
accuracy. It is chosen by deciding which harm we are willing to cause, and how often.

- A **false reject** means a user scans their cat again. The cost is annoyance, measured
  in seconds.
- A **false accept** means an innocent household is accused of abandonment and loses a
  deposit. The cost is injustice, measured in money and reputation.

We would rather inconvenience ten people than falsely accuse one. FRR is therefore
budgeted at 10% and FAR at 1%. See ADR-0003 for the full decision and its cost.

---

## 6. Requirements

Every requirement has four fields. No exceptions.

- **behaviour** — what the system does, in one clause.
- **number** — the threshold or budget.
- **measurement** — the command that produces that number, and the file it writes.
- **consequence** — what happens when it fails. A consequence is enforced by a machine or
  it does not exist.

Requirements marked *(planned: Week n)* have their measurement command wired but not yet
implemented; the command exits non-zero until that week. See `evals/run.py`.

### REQ-001 — Capture quality gate

- **behaviour** — Reject an enrolment frame whose aligned face crop is too blurred to embed
- **number** — Laplacian variance below 120 on the aligned crop
- **measurement** — `make eval-capture`, writes `evals/out/capture.json` *(planned: Week 2)*
- **consequence** — Camera re-prompts the user; the frame is never sent to the server

### REQ-002 — Multi-frame liveness

- **behaviour** — Reject an enrolment whose frames show no inter-frame variation consistent with a live animal
- **number** — At least 5 accepted frames, with mean inter-frame landmark displacement ≥ 2.0 px on the aligned crop and non-zero focus variation across the macro nose sequence
- **measurement** — `make eval-liveness`, writes `evals/out/liveness.json` *(planned: Week 5)*
- **consequence** — Enrolment is refused with a re-capture prompt; three consecutive failures from one account are flagged for registry review

### REQ-003 — Open-set identification accuracy

- **behaviour** — Identify the correct PetID as top-1 for a query image of an enrolled cat
- **number** — Top-1 ≥ 90% on held-out identities never seen in training
- **measurement** — `make eval-identify`, writes `evals/out/identify.json` *(planned: Week 3)*
- **consequence** — Below target blocks the merge. No model is promoted on a closed-set number

### REQ-004 — False accept rate

- **behaviour** — Do not return a match for a cat that is not enrolled
- **number** — FAR ≤ 1% at the operating threshold, measured on unseen identities
- **measurement** — `make eval-identify`, writes `evals/out/identify.json` *(planned: Week 3)*
- **consequence** — Below target blocks the merge. The operating threshold is set from this measurement, never chosen by hand

### REQ-005 — False reject rate

- **behaviour** — Return a match for a cat that is enrolled
- **number** — FRR ≤ 10% at the operating threshold used for REQ-004
- **measurement** — `make eval-identify`, writes `evals/out/identify.json` *(planned: Week 3)*
- **consequence** — Above target blocks the merge. FRR and FAR are reported from the same threshold or neither number is reported

### REQ-006 — 1:N search latency

- **behaviour** — Return 1:N search results within the interaction budget
- **number** — p95 ≤ 100 ms over a 100k-vector HNSW index, server-side
- **measurement** — `make eval-search`, writes `evals/out/search.json` *(planned: Week 3)*
- **consequence** — Above budget blocks the merge; the index configuration is tuned, not the budget

### REQ-007 — Dedup on enrolment

- **behaviour** — Reject enrolment if the new template matches an existing PetID above threshold
- **number** — cosine similarity ≥ 0.62, top-1 of a 1:N HNSW search
- **measurement** — `make eval-dedup`, writes `evals/out/dedup.json` *(planned: Week 3)*
- **consequence** — Enrolment returns 409 and surfaces the existing PetID to a registry admin. No automatic merge, and a documented human override path for the littermate case

### REQ-008 — Template generation versioning

- **behaviour** — Never compare two templates produced by different model versions
- **number** — Every stored template carries a `model_version` string; cross-version comparison count must be 0
- **measurement** — `make eval-policy`, writes `evals/out/policy.json` *(planned: Week 5)*
- **consequence** — A cross-version comparison raises an error rather than returning a score; a model upgrade requires a re-embedding migration plan before it may be deployed

### REQ-009 — Raw imagery retention

- **behaviour** — Discard raw enrolment frames after template extraction
- **number** — Raw frames retained ≤ 24 h; retained raw frames after that window must be 0
- **measurement** — `make eval-policy`, writes `evals/out/policy.json` *(planned: Week 5)*
- **consequence** — A retention sweep deletes the frames; a non-zero count fails the gate. A cat's nose print cannot be reissued after a breach, so this is not negotiable for convenience

### REQ-010 — Human adjudication gate

- **behaviour** — No deposit is slashed without a written finding by a human adjudicator
- **number** — Automated slashes permitted: 0
- **measurement** — `make eval-policy`, writes `evals/out/policy.json` *(planned: Week 7)*
- **consequence** — The contract rejects any slash transaction not carrying an adjudicator signature. A biometric match may open a case; only a person may close one

### REQ-011 — On-device model size

- **behaviour** — Ship the detector and aligner inside the mini-program package
- **number** — Combined ONNX artefacts ≤ 25 MB
- **measurement** — `make eval-capture`, writes `evals/out/capture.json` *(planned: Week 2)*
- **consequence** — Above budget, the model is quantised or the stage moves server-side; the package limit is not negotiable

### REQ-012 — Enrolment duration

- **behaviour** — Complete enrolment within the attention span of a real household
- **number** — p90 wall-clock ≤ 3 min from first camera frame to PetID issued
- **measurement** — `make eval-policy`, writes `evals/out/policy.json` *(planned: Week 5)*
- **consequence** — Above budget, the capture protocol is shortened before any model change is considered

### REQ-013 — Attestation authority

- **behaviour** — Accept a sterilisation claim only from a registered vet signing key valid at signing time
- **number** — Attestations accepted from unregistered or revoked-at-signing-time keys: 0
- **measurement** — `make eval-policy`, writes `evals/out/policy.json` *(planned: Week 7)*
- **consequence** — The attestation is rejected and logged. A field anyone can set is not a fact, it is a rumour with a schema

### REQ-014 — Transfer ceremony

- **behaviour** — Transfer a PetID only through a two-party signed ceremony with a cooling period
- **number** — Both household keys required; cooling period 72 h before the transfer finalises
- **measurement** — `make eval-policy`, writes `evals/out/policy.json` *(planned: Week 6)*
- **consequence** — A single-party transfer is impossible at the contract level; the full transfer history stays readable on the pet DID

### REQ-015 — Appeal window

- **behaviour** — Allow one appeal against an upheld finding, on new evidence
- **number** — 30 days from the adjudication record; one appeal per case
- **measurement** — `make eval-policy`, writes `evals/out/policy.json` *(planned: Week 7)*
- **consequence** — Slashed funds are not disbursed to the community fund until the window closes. The window is sized from the measured FAR — at 1% FAR, wrong matches are expected, so the path back must exist by design

### REQ-016 — Proof of custody at enrolment

- **behaviour** — Require evidence of custody before binding an animal to a household
- **number** — At least 2 capture sessions on different days, ≥ 24 h apart, from the same account
- **measurement** — `make eval-policy`, writes `evals/out/policy.json` *(planned: Week 5)*
- **consequence** — Enrolment stays `pending_dedup` until satisfied; a contested-ownership path exists for the neighbour-enrols-your-cat case

### REQ-017 — Report rate limiting

- **behaviour** — Limit how many abandonment reports one account can open
- **number** — ≤ 3 admitted cases per reporter per 30 days; an evidence bundle is mandatory
- **measurement** — `make eval-policy`, writes `evals/out/policy.json` *(planned: Week 7)*
- **consequence** — Excess reports are queued for manual triage, not auto-admitted; reporter reputation is recorded

### REQ-018 — Evidence bundle completeness

- **behaviour** — Open a case only on a complete evidence bundle
- **number** — Bundle must contain: match score, matched PetID, scan timestamp and location, reporter identity, and the model version used. Incomplete bundles admitted: 0
- **measurement** — `make eval-policy`, writes `evals/out/policy.json` *(planned: Week 7)*
- **consequence** — An incomplete bundle cannot be admitted; the adjudicator sees exactly what the system saw

---

## 7. Scope

**v1, 8 weeks** — cats only, one breed-agnostic model; face plus nose-print two-stream
template; single-city pilot-scale index; local consortium devnet; human adjudication on
every penalty.

**Later, named but not built** — dogs and other species; city-scale sharded index; real
vet-clinic system integration; insurance and licensing tie-ins.

**Never, and why**

| We will not build | Because |
|---|---|
| Automatic slashing with no human gate | An error becomes an injustice with no correction path, and at a 1% FAR errors are certain |
| Indefinite retention of raw owner or pet imagery | Biometrics cannot be reissued after a breach; a leaked template is permanent in a way a leaked password is not |
| Public-chain token trading of any PawChain asset | Not lawful in the deployment context, and it would turn a responsibility into an asset |
| Any claim of legal enforcement authority | We have none. The system produces evidence for humans who do |
| A PetID that can be sold | Responsibility is not tradeable. See ADR-0001 |

The "never" column is the one that matters. Anyone can list features; writing down what
you refuse to build, with a reason, is the part that requires having thought about
consequences.

---

## 8. What this spec does not yet decide

See `specs/open-questions.md`. Every open question is resolved by a measurement or a
decision record, one per week minimum. A stopped task with a good question is worth more
than a finished task built on an assumption.
