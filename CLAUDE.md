# PawChain ID — project constitution

Read this file before every task. If anything here conflicts with an instruction in
chat, follow this file and say so.

## What this is

An open-set biometric identity system for individual cats, bound to a responsible
household, with vet-attested sterilisation status and a refundable deposit.
Prototype, pilot scale, single city. Not a deployed product.

## Stack, pinned

- Python 3.11, PyTorch 2.x, ONNX Runtime
- FastAPI, PostgreSQL 16, Redis
- Solidity 0.8.x, local consortium-chain devnet
- WeChat Mini Program for capture

Do not upgrade a pinned version without a decision record in `specs/decisions/`.

## Directory map

- `specs/` — the requirement of record. Code implements specs, never the reverse.
- `specs/tasks/` — one unit of work, with acceptance criteria attached.
- `specs/decisions/` — architecture decision records. Read these before proposing a
  design that contradicts one.
- `evals/golden/` — frozen evaluation data. NEVER use for training, tuning, threshold
  selection or augmentation. Do not modify, move or add to this folder.
- `evals/out/` — generated metrics, gitignored.
- `ml/`, `api/`, `contracts/`, `miniapp/` — implementation.
- `course/` — session material for the 8-week programme. Not part of the system.
  Do not import from it, and do not let it affect the gate.

## Definition of done

A task is done when all of the following hold:

1. `make gate` passes locally and in CI.
2. Every acceptance criterion in the task file is marked PASS with the command that
   proves it.
3. Any metric the task touches is written to `evals/out/` and reported in the pull
   request description.
4. The pull request names the spec file it implements.

"It ran without errors" is not done.

## House rules

- No new dependency without a decision record.
- No secrets, keys or credentials in code or in commit messages.
- Every public function has type annotations.
- Never weaken, skip or ignore a check to make the gate pass. Report the failure.
- Never delete or rewrite a test to make it pass. Fix the code or challenge the spec.
- Raw pet imagery is never committed to the repository.
- Prefer small pull requests that each reference one task file.

## How to verify

```
make gate
```

That command is the only definition of correctness in this project. It runs lint,
types, tests and evals in that order.

## When unsure

Do not guess. Write a section headed `QUESTIONS` listing what is ambiguous and what
you would need to decide, append the same items to `specs/open-questions.md`, and
stop. A stopped task with good questions is more useful than a finished task built on
an assumption.
