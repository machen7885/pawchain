# api/ — the registry (Week 5)

FastAPI + PostgreSQL + Redis. Enrollment, 1:1 verification, ownership transfer,
sterilisation status, and lost-pet 1:N matching. Every endpoint audit-logged.

Empty on purpose until Week 5.

Design constraints already fixed by the spec:

- Enrolment runs dedup before issuing any PetID, and returns 409 on a duplicate (REQ-007).
- Raw frames are discarded within 24 h of template extraction (REQ-009).
- Roles: household, vet, registry admin, adjudicator. Vets hold signing keys for Week 7
  attestations (REQ-013).
- The endpoints are the transitions in the PetID, Deposit and Case state machines
  (`specs/00-system-spec.md` §4). Anything that is not a transition is a screen.
