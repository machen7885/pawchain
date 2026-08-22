# The course

PawChain ID is built inside an 8-week applied AI intensive: two live sessions per week
(deep dive + build review), agent-driven build sprints in between, and one shipped artifact
every single week. No slide-only weeks — every week ends with working code in this
repository.

Prerequisites: basic Python. Everything else is taught in flight, agent-assisted.

| Week | Session | Ships |
|---|---|---|
| [1](week-01/) | Problem framing and the agent-native dev environment | Spec + threat model + monorepo scaffold with a working agent harness |
| [2](week-02/) | Cat detection and landmark alignment | Real-time capture pipeline: phone frame in → aligned, quality-gated face + nose crops out |
| 3 | The fingerprint: nose-print and facial embeddings | Embedding service hitting target verification accuracy on unseen cats, sub-100 ms 1:N lookup |
| 4 | Agentic data engineering and the evaluation harness | Self-serving data flywheel + eval dashboard; model quality becomes a CI number |
| 5 | The registry: backend and Mini Program enrollment | End-to-end enrollment — scan a real cat on a phone, get a PetID issued |
| 6 | The identity layer: DID, VCs and RWA design | Deployed soulbound PetID contract on a local consortium devnet, wired to the registry |
| 7 | The accountability engine: deposits, attestations, slashing | The full incentive lifecycle running live |
| 8 | Integration, hardening and demo day | Live demo + whitepaper + pitch deck |

## The stack, by layer

| Layer | Stack |
|---|---|
| Agent tooling | Claude Code, Cursor, `CLAUDE.md` project constitutions, MCP servers, eval harnesses, CI gates |
| Vision / ML | PyTorch, YOLOv8 / RT-DETR, keypoint alignment, ArcFace / triplet metric learning, ONNX Runtime, FAISS / Milvus |
| Backend / App | FastAPI, PostgreSQL, Redis, S3-compatible object store, WeChat Mini Program |
| Identity / Chain | W3C DID + Verifiable Credentials, Solidity, soulbound-token pattern, consortium chain, escrow + oracle design |

## Design notes baked in from day one

- **Compliance is a feature, not a footnote.** Public-chain stablecoin payments are not
  deployable in the target context, so the money leg is engineered as fiat/e-CNY escrow on
  permissioned infrastructure. Owner data handling is designed against PIPL from the first
  schema.
- **Incentive over seizure.** A voluntary-then-mandated refundable deposit is deployable;
  direct deduction of household assets is not. Same behavioural pressure, shippable design.
- **Every penalty has a human gate.** Biometric matches open cases; adjudicators close
  them. We measure our own false-match rate and size the appeal window around it.

## What accumulates over eight weeks

| Artifact | Where | Used for |
|---|---|---|
| Commit history | `git log` | Dated proof of sustained work. Not squashed |
| 8 evidence entries | `EVIDENCE.md` | Raw material for essays and interview answers |
| 8+ decision records | `specs/decisions/` | Judgment under uncertainty, which is the trait actually being assessed |
| Eval numbers per commit | `evals/out/` | Turns "it works" into a defensible claim |
| Threat model | `specs/01-threat-model.md` | The single most unusual document a portfolio can contain |
| Demo video and whitepaper | Week 8 | Portfolio link, competition entry, interview opener |

> Session decks and facilitator material are distributed separately and are not committed
> to this public repository.
