# contracts/ — identity and incentive layer (Weeks 6–7)

Solidity 0.8.x on a local consortium-chain devnet. The soulbound PetID token, the
revocation registry, and the deposit escrow state machine.

Empty on purpose until Week 6.

Design constraints already fixed by the spec and the decision records:

- The PetID is soulbound; transfer happens only through a two-party ceremony with a 72 h
  cooling period (ADR-0001, REQ-014).
- The token anchors a *salted hash commitment* of the biometric template. Templates and
  raw frames never go on chain (threat model row 4).
- No slash transaction is valid without an adjudicator signature. Automated slashes
  permitted: 0 (REQ-010).
- Slashed funds are not disbursed until the 30-day appeal window closes (REQ-015).
- The money leg is application-layer fiat/e-CNY escrow, not an on-chain asset (ADR-0002).
