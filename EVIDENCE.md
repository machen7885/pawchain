# Evidence log

Four questions, 150 words, every week. Written by the architect, not the agent.

Eight entries by Week 8. That is a portfolio README, an activity description and two essay
drafts, assembled from work actually done — which is the only kind that survives an
interview question.

---

## Week 1 — Problem framing and the agent-native dev environment

**Which decision did I own this week?**

The error budget. I set the false-reject budget at 10% and the false-accept budget at 1%
(ADR-0003), before any model existed to make the number convenient.

**What were the alternatives, and what did I give up?**

A symmetric budget treats both errors as equally bad, and a near-zero FAR eliminates wrong
matches at the cost of a system that constantly fails to recognise enrolled cats. I gave up
the second: at a 10% FRR, one scan in ten fails and the user tries again. I also gave up the
comfort of claiming the system is simply accurate.

**What number or fact did I decide on?**

FAR ≤ 1%, FRR ≤ 10%, both at the same operating threshold, both measured on identities never
seen in training. They trade against each other on a single dial, so I had to decide which
error I would rather cause. A false reject means someone scans their cat again. A false
accept means a household is accused of abandoning a cat they never owned and loses their
deposit. I would rather inconvenience ten people than accuse one. That asymmetry is now
written into the spec, and Week 7's 30-day appeal window is sized from the same number.

**What broke, and what did I change because of it?**

The gate, on purpose. An unused import in `evals/` turned `make gate` red, ruff stopped the
run before the type, test and eval stages, and CI blocked the pull request. That was the
point: a gate nobody has watched fail is not a gate anyone should trust. What changed is
smaller and more useful than the fix — writing the Deposit state machine exposed that a
vet losing their licence after signing has *no* good transition, which forces a revocation
registry and a decision about whether attestations are valid as of signing time or read
time. That is now OQ-004 rather than an assumption buried in Week 7's contract.

---

## Week 2 — Cat detection and landmark alignment

**Which decision did I own this week?**

**What were the alternatives, and what did I give up?**

**What number or fact did I decide on?**

**What broke, and what did I change because of it?**

---

## Week 3 — The fingerprint: nose-print and facial embeddings

**Which decision did I own this week?**

**What were the alternatives, and what did I give up?**

**What number or fact did I decide on?**

**What broke, and what did I change because of it?**

---

## Week 4 — Agentic data engineering and the evaluation harness

**Which decision did I own this week?**

**What were the alternatives, and what did I give up?**

**What number or fact did I decide on?**

**What broke, and what did I change because of it?**

---

## Week 5 — The registry: backend and Mini Program enrollment

**Which decision did I own this week?**

**What were the alternatives, and what did I give up?**

**What number or fact did I decide on?**

**What broke, and what did I change because of it?**

---

## Week 6 — The identity layer: DID, VCs and RWA design

**Which decision did I own this week?**

**What were the alternatives, and what did I give up?**

**What number or fact did I decide on?**

**What broke, and what did I change because of it?**

---

## Week 7 — The accountability engine: deposits, attestations, slashing

**Which decision did I own this week?**

**What were the alternatives, and what did I give up?**

**What number or fact did I decide on?**

**What broke, and what did I change because of it?**

---

## Week 8 — Integration, hardening and demo day

**Which decision did I own this week?**

**What were the alternatives, and what did I give up?**

**What number or fact did I decide on?**

**What broke, and what did I change because of it?**
