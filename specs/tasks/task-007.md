# task-007 — Dedup on enrolment

**Implements** REQ-007 (`specs/00-system-spec.md` §6) · **Week** 3 · **Status** not started

## Goal

Run a 1:N search before issuing any PetID, so the same animal cannot be registered twice —
by one household or by two. Enrolment without dedup is the single largest design hole in
animal re-identification, and it is the transition `pending_dedup → active` in the PetID
state machine.

## Files I will touch

- `ml/search/index.py` — HNSW index build and 1:N query
- `ml/search/dedup.py` — the dedup decision and its threshold constant
- `api/enrolment.py` — the 409 path and the admin surfacing
- `evals/run.py` — implement the `dedup` suite
- `evals/golden/dedup/` — frozen identity pairs including littermates, never used for tuning

## Acceptance criteria

| # | Assertion | Command that proves it |
|---|---|---|
| 1 | `dedup.check(template)` returns the top-1 match and its cosine similarity from a 1:N HNSW search | `pytest ml/search/test_dedup.py -q` |
| 2 | A template with top-1 cosine similarity ≥ 0.62 is classified duplicate; below 0.62 it is classified new | `pytest ml/search/test_dedup.py -q` |
| 3 | The threshold is a single named constant, sourced from the measured operating point, not a literal | `grep -rn "0.62" ml/ \| grep -v "DEDUP_THRESHOLD"` returns nothing |
| 4 | Templates of different `model_version` are never compared; attempting it raises (REQ-008) | `pytest ml/search/test_dedup.py::test_cross_version_raises -q` |
| 5 | Enrolment of a duplicate returns HTTP 409 and does not create a PetID row | `pytest api/test_enrolment.py::test_duplicate_returns_409 -q` |
| 6 | A 409 surfaces the existing PetID to a registry admin queue and performs no automatic merge | `pytest api/test_enrolment.py::test_duplicate_creates_admin_review -q` |
| 7 | A dedup rejection can be overridden by a registry admin, and the override is recorded with an actor and a reason | `pytest api/test_enrolment.py::test_admin_override_recorded -q` |
| 8 | `make eval-dedup` writes `evals/out/dedup.json` with `far`, `frr`, `threshold`, `index_size` and `model_version` | `make eval-dedup && python -c "import json;d=json.load(open('evals/out/dedup.json'));assert {'far','frr','threshold','index_size','model_version'} <= d.keys()"` |
| 9 | On the frozen golden set, FAR ≤ 1% and FRR ≤ 10% at the reported threshold (REQ-004, REQ-005) | `make eval-dedup` — the suite exits non-zero if either budget is exceeded |
| 10 | The littermate slice is reported separately, and its false-duplicate rate is stated rather than hidden in the average | `make eval-dedup && python -c "import json;d=json.load(open('evals/out/dedup.json'));assert 'littermate_false_duplicate_rate' in d"` |
| 11 | 1:N query p95 latency ≤ 100 ms over a 100k-vector index (REQ-006) | `make eval-search` — reported as `p95_ms` in `evals/out/search.json` |

## Notes and risks

- **0.62 is a placeholder.** It was written into the spec before any measurement on cats
  and is tracked as OQ-001. The correct value is the operating point where the measured
  curve satisfies FAR ≤ 1%; if no single threshold satisfies both budgets, that fact is
  reported and ADR-0003 is revised, not quietly relaxed.
- Criterion 10 exists because littermates are the failure mode the average will hide
  (threat model row 10). A 1% aggregate FAR with a 20% littermate false-duplicate rate is a
  system that locks out exactly the households most likely to enrol more than one cat.
- Dedup is a *false reject at enrolment*. It fails closed for a legitimate owner, which is
  why criterion 7 (human override) is not optional.

## Out of scope

Lost-pet 1:N matching for case opening (Week 7), index sharding (later, named not built),
and any automatic merge of two PetIDs — the spec forbids it.
