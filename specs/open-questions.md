# Open questions

Things this project has not decided. Each one is resolved by a measurement or a decision
record — one per week, minimum. Nothing here may be silently assumed away in code.

Rule: when a task is blocked by ambiguity, the agent writes a `QUESTIONS` block, appends
the items here, and stops. A stopped task with a good question is more useful than a
finished task built on an assumption.

| ID | Question | Blocks | Resolved by | Status |
|---|---|---|---|---|
| OQ-001 | Is 0.62 the right dedup threshold, or is it a placeholder copied from human face recognition? It was chosen before any measurement on cats. | REQ-007 | Week 3 measurement on held-out identities; then update the spec with the measured value | open |
| OQ-002 | What counts as a verified household? A WeChat account is not an identity, and the deposit leg will eventually need one. | REQ-016, deposit escrow | Week 5 decision record | open |
| OQ-003 | Do face and nose-print streams get one fused threshold or two independent ones? Two thresholds means two FAR numbers and a combination rule nobody has written. | REQ-003, REQ-004, REQ-007 | Week 3 measurement, then ADR | open |
| OQ-004 | A vet loses their licence after signing. Are attestations evaluated at signing time or at read time? Read-time validity retroactively invalidates every deposit that vet released; signing-time validity means a corrupt vet's signatures survive their revocation. | Deposit state machine, REQ-013 | Week 7 decision record | open — leaning signing-time, with a targeted re-review list |
| OQ-005 | Does the project need a blockchain at all, or is a signed append-only log in PostgreSQL sufficient? | contracts/, Weeks 6–7 | ADR-0002 (written, revisit trigger stated) | provisionally answered |
| OQ-006 | Who funds and who governs the community TNR/shelter fund that receives slashed deposits? An unowned pot of forfeited money is a governance problem, not a technical one. | Week 7 | Week 7 pilot design | open |
| OQ-007 | How is audit-log integrity protected against an insider with database write access? | Threat model row 13 | Week 8 hardening | open |
| OQ-008 | What is the re-enrolment cadence that catches deliberate degradation without annoying honest households into leaving? | REQ-001, threat model row 9 | Week 5, after real capture data exists | open |
| OQ-009 | Is proof of custody across two sessions ≥ 24 h apart acceptable friction for a real household, or does it kill the sign-up funnel? | REQ-016 | Week 5 pilot observation | open |
| OQ-010 | What is the minimum viable index size at which the ≤ 100 ms p95 budget stops being trivially met? The 100k figure is an assumption about pilot scale, not a measurement. | REQ-006 | Week 3 benchmark | open |

## Resolved

| ID | Question | Resolved by | Answer |
|---|---|---|---|
| OQ-000 | Which error do we prefer to make, and how often? | ADR-0003 | FRR ≤ 10%, FAR ≤ 1%. We would rather inconvenience ten people than falsely accuse one. |
