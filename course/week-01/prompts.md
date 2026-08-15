# Week 1 — the four prompts

Run these in order, in Claude Code, from inside an empty `pawchain-id/` directory. Paste
them; do not retype and do not improvise. The point of the exercise is that a specification
is obeyed.

---

## P1 — scaffold

```
Create the repository structure exactly as listed below. Every empty folder gets a
README.md naming its purpose in one line. Do not write any application code, and do
not add any folder that is not on this list. Then print the resulting tree and stop.

pawchain-id/
  CLAUDE.md
  Makefile
  EVIDENCE.md
  specs/
    00-system-spec.md
    01-threat-model.md
    02-glossary.md
    open-questions.md
    tasks/
    decisions/
  evals/
    golden/
    out/
  ml/
  api/
  contracts/
  miniapp/
  .github/workflows/
```

**If the agent invents its own folders** — extra names, a `src/` nobody asked for — re-run
with "exactly as listed, no additional folders". Do not accept "close enough".

**If the agent writes application code** — a working FastAPI app appears — delete it, and
say why out loud: nothing gets written before there is a gate that can check it.

---

## P2 — gates

```
Add a Makefile with targets: lint, types, test, eval, gate. The gate target runs all
four in that order and fails on the first failure. Use ruff for lint, pyright for
types, pytest for test. The eval target runs evals/run.py, which for now writes a
placeholder JSON file to evals/out/metrics.json and exits non-zero if the file was
not written.

Add .github/workflows/gates.yml that runs `make gate` on every pull request and on
pushes to main. Add one trivial passing test so the pipeline is provably wired.

Do not weaken, skip or ignore any check in order to make the gate pass. If something
cannot pass, report it and stop.
```

**If the agent weakens a check to make the gate pass** — a rule added to an ignore list, a
test marked skip — this is the most important teaching moment in the session. Revert it,
and put the house rule in `CLAUDE.md`: never weaken a check to pass it; report the failure
instead.

---

## Deliberate breakage

A gate you have never seen fail is not a gate you trust.

```
Add an unused import to any Python file in evals/. Do not fix anything else.
```

Run `make gate`, watch ruff stop the run before types, tests and evals ever execute. Then:

```
Read the failing gate output and fix the cause. Do not modify the lint configuration.
```

---

## P3 — spec to task

```
Read specs/00-system-spec.md. For requirement REQ-001 only, write
specs/tasks/task-001.md containing exactly these sections: goal, files you will
touch, acceptance criteria as a numbered list of assertions, and for each assertion
the command that proves it. Write no implementation code yet.
```

---

## P4 — self-review

```
Review your own diff against specs/tasks/task-001.md. For each acceptance criterion,
state PASS or FAIL and the evidence you are relying on. If any criterion is not
testable as written, say so and propose a testable replacement. Do not edit the spec
yourself.
```

P4 is the one people skip. Asking the agent to grade itself against a written criterion
catches roughly half of the mismatches before a human ever looks.

---

## If you run out of time

Stop, commit whatever exists, and push it. Finish P3 and P4 as homework. **A pushed
half-repo beats an unpushed whole one**, and the git log is the evidence that this happened
over eight weeks rather than in one panicked weekend.
