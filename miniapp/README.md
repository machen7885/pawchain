# miniapp/ — WeChat Mini Program capture flow (Week 5)

Guided multi-frame face and macro nose capture, on-device quality gating, and
frame-consistency liveness.

Empty on purpose until Week 5.

Design constraints already fixed by the spec:

- A frame that fails the quality gate never leaves the device (REQ-001).
- Liveness is multi-frame consistency, not a single-frame classifier (REQ-002).
- The on-device detector and aligner must fit the package limit: ≤ 25 MB combined
  (REQ-011).
- Whole enrolment completes in ≤ 3 min p90, phone in hand (REQ-012). If we miss that, the
  capture protocol gets shorter before the model gets bigger.
- Offline retry queue: capture must survive a dead network without asking the household to
  start again.
