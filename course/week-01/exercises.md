# Week 1 — exercises

Three exercises, 19 minutes total. You write; nobody rescues you mid-exercise.

---

## Exercise 1 — Draw the state machine for `Deposit` (7 min)

**Rules**

- Every state is a noun the database could store.
- Every arrow is labelled with **who triggers it** and **what evidence is required**.
- Any state with no way out is a trap — mark it and defend it.

**You are finished when you have handled all five:**

1. The cat dies.
2. The household emigrates.
3. The cat is legitimately re-homed to a friend.
4. The vet who signed loses their licence afterwards.
5. The household disputes the match.

Each of those is a real case that will happen in the first thousand users. Missing one now
is a rewrite in Week 7.

**The trap.** Most people draw `slashed` as terminal. Ask what happens when the household
later proves the match was wrong. If there is no path back, the system cannot correct its
own errors — which is exactly the property that makes a deposit scheme politically
undeployable. The appeal edge is not a nicety; it is the reason anyone would agree to post a
deposit at all.

**The one with no good answer.** Case 4 has no clean transition, and noticing that is the
best possible outcome of this exercise: it forces a revocation registry, and a decision about
whether an attestation is valid as of *signing* time or *read* time. Tracked here as
[OQ-004](../../specs/open-questions.md).

Worked result: [`specs/00-system-spec.md` §4.2](../../specs/00-system-spec.md).

---

## Exercise 2 — Rewrite three of your own sentences (6 min)

Take three lines from how you have described this project so far — to a teacher, a parent,
in your notes — and rewrite each into the four-field format.

```
REQ-007  Dedup on enrolment
  behaviour     Reject enrolment if the new template matches an existing
                PetID above the operating threshold
  number        cosine similarity >= 0.62, top-1 of a 1:N HNSW search
  measurement   make eval-dedup  ->  evals/out/dedup.json
  consequence   Enrolment returns 409 and surfaces the existing PetID to
                a registry admin for manual review. No auto-merge.
```

These become the first entries in `specs/00-system-spec.md` tonight.

Two failure patterns to catch in your own writing:

- *"measurement: manual testing"* — then it is not a measurement, it is a mood. What
  command produces the number, and where does it write it?
- *"consequence: we fix it"* — who is "we", and what stops the code shipping before you get
  to it? A consequence is enforced by a machine or it does not exist.

---

## Exercise 3 — Find two attacks that are not on the list (6 min)

**Prompts to think with**

- Who benefits if the system says *nothing* rather than something wrong?
- What does a shelter with 400 cats and a quota do?
- What happens on the day two littermates are enrolled an hour apart?
- What can be done by someone with physical access to the cat but no account?

**Fill this in for each**

```
attack:
actor:
cost to attacker:
signal it leaves:
mitigation:
ships in week:
residual risk we accept:
```

The last line is compulsory. A threat model with no accepted residual risk is a fantasy.

You are graded on the residual-risk line, not on the creativity of the attack.

Worked results: rows 10–13 of [`specs/01-threat-model.md`](../../specs/01-threat-model.md)
— littermate confusion, shelter quota gaming, denial of enrolment, adjudicator capture.
