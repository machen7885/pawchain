# PawChain ID — threat model v0.1

Status: draft · Owner: Han's Applied AI Tutoring / PawChain ID · Last updated: 2026-08-15

The moment a refundable deposit exists, three populations appear that did not exist
before: people who want the money back without doing the thing, people who want someone
else blamed, and people who want the database.

Every row needs all seven columns. **A row with no residual risk stated is not finished** —
a threat model with no accepted residual risk is a fantasy, and reviewers know it.

The column people forget is *cost to attacker*. Attacks do not need to be impossible. They
need to cost more than the deposit is worth. That is a budget, and budgets are defensible.

---

## Attack table

| # | Attack | Actor | Cost to attacker | Signal it leaves | Mitigation | Ships | Residual risk we accept |
|---|---|---|---|---|---|---|---|
| 1 | **Photo replay** — hold a printed photo or phone screen to the camera | anyone | near zero | single-frame capture, no parallax, flat focus response | multi-frame consistency, parallax across frames, forced macro nose focus (REQ-002) | W5 | high-quality video replay on a large screen defeats this; we do not detect it |
| 2 | **Double enrolment** — same cat registered by two households, or twice by one | household | near zero | 1:N hit at enrolment | dedup-on-enrol before any ID is issued; 409 plus human review (REQ-007) | W3 | littermates below the dedup threshold enrol as separate cats; see row 10 for the inverse |
| 3 | **Ghost cat** — enrol an internet photo of a cat that does not exist | household | low | no vet attestation ever follows the enrolment | liveness gate plus vet co-signature on the first attestation (REQ-002, REQ-013) | W5, W7 | the pre-attestation window: a ghost cat exists in the registry until the first attestation is due |
| 4 | **Template theft** — registry database leaks; templates are reusable forever | external | high | none, until the templates are used | salted hash commitment on chain, template held server-side, raw frames discarded within 24 h (REQ-009) | W5, W6 | templates cannot be reissued after a breach — a password can be changed, a nose print cannot. This is the argument for storing hashes rather than images, and it is stronger than "for privacy" |
| 5 | **Vet collusion** — a licensed vet signs "sterilised" for a fee, without surgery | vet | medium | anomalous attestation rate per issuer | signing-key rotation, attestation-rate anomaly monitoring, random audit, revocation registry (REQ-013) | W7 | low-volume collusion below the detection threshold is undetectable by design |
| 6 | **False accusation** — a found stray matches the wrong household above threshold | accidental | n/a | an appeal is filed | operating threshold set from measured FAR, mandatory human adjudication, appeal window (REQ-004, REQ-010, REQ-015) | W7 | 1% of matches, by design and in writing. We chose this number; see ADR-0003 |
| 7 | **Transfer laundering** — fake a legitimate re-homing to shed responsibility before abandoning | household | medium | rapid transfer immediately before a report | two-party transfer ceremony with both keys, 72 h cooling period, transfer history on the DID (REQ-014) | W6 | two colluding households can still launder a transfer; we detect the pattern, we do not prevent it |
| 8 | **Report spam** — flood abandonment reports to harass a household or the registry | anyone | near zero | report volume concentrated in one reporter | rate limits, reporter reputation, mandatory evidence bundle to open a case (REQ-017, REQ-018) | W7 | coordinated reporting across many accounts stays below per-account limits |
| 9 | **Deliberate degradation** — an owner intending to abandon damages capture quality on purpose (dirty nose, poor light) so 1:N will not match later | household | low | low capture quality score at enrolment | minimum accepted quality score at enrolment, periodic re-enrolment (REQ-001) | W5 | slow drift just above the minimum score is below detection |
| 10 | **Littermate confusion** — two cats from one litter enrol an hour apart; dedup rejects the second as a duplicate | accidental | n/a | dedup rejection with two capture sets from one address, close in time | hard-negative training on littermates, plus a documented human override path on dedup rejection (REQ-007) | W4 | a legitimate owner is locked out until an admin reviews. This is a **false reject at enrolment**, and it is the failure mode most likely to make a real user quit |
| 11 | **Shelter quota gaming** — a shelter under pressure to report high sterilisation rates enrols only already-sterilised cats | shelter | low | attestation timestamps clustered at, or before, enrolment timestamps | enrolment and attestation are separable events with separate timestamps; the compliance metric is per-enrolment-cohort, never per-attestation | W7 | a shelter can still choose which animals to enrol at all; we measure the cohort, we cannot force the intake |
| 12 | **Denial of enrolment** — someone enrols a neighbour's cat first, capturing the binding | neighbour | near zero | two accounts submitting captures of the same animal from one location | proof of custody at enrolment across two sessions ≥ 24 h apart, plus a contested-ownership path (REQ-016) | W5 | a determined attacker with sustained physical access to the animal satisfies proof of custody |
| 13 | **Adjudicator capture** — the person who closes cases is bribed or pressured | registry adjudicator | medium | rulings skewed by reporter or household | written findings on every case, appeal path, rotation of adjudicators, audit of upheld-rate per adjudicator | W7 | a single adjudicator acting alone within normal rates is undetectable at pilot volume |

---

## The pattern to notice

Every mitigation in this table is a **gate, a rate limit, or a human**. Not one of them is
a better model. Accuracy is not a security strategy — it is an input to one.

## What the table does not cover

- Attacks against the WeChat platform account layer itself (out of our control, out of v1
  scope).
- Physical harm to the animal to defeat identification. Noted, not modelled — the
  mitigation is not technical.
- Insider access at the registry with database write privileges. Partially covered by
  audit-log integrity work in Week 8; recorded as OQ-007.
