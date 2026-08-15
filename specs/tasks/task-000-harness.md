# task-000 — Stand up the agent harness

**Implements** `specs/00-system-spec.md` §3 · **Week** 1 · **Status** done

## Goal

Create the machine that checks the machine: a repository layout, a constitution, a
one-command gate, and CI that runs it on every pull request — before any application code
exists. Nothing gets written until there is a gate that can check it.

## Files I will touch

- `CLAUDE.md`
- `Makefile`
- `pyproject.toml`
- `.gitignore`
- `EVIDENCE.md`
- `specs/00-system-spec.md`, `specs/01-threat-model.md`, `specs/02-glossary.md`, `specs/open-questions.md`
- `specs/tasks/`, `specs/decisions/`
- `evals/run.py`, `evals/test_run.py`, `evals/golden/README.md`, `evals/out/.gitkeep`
- `ml/README.md`, `api/README.md`, `contracts/README.md`, `miniapp/README.md`
- `.github/workflows/gates.yml`

## Acceptance criteria

| # | Assertion | Command that proves it |
|---|---|---|
| 1 | The repository contains exactly the folders named in the spec, each empty folder carrying a README naming its purpose | `ls -R specs evals ml api contracts miniapp` |
| 2 | Lint passes with no findings | `make lint` |
| 3 | Type checking passes with no errors | `make types` |
| 4 | The test suite runs and passes at least one test | `make test` |
| 5 | The eval target writes `evals/out/metrics.json` and exits non-zero if it did not | `make eval && test -f evals/out/metrics.json` |
| 6 | `make gate` runs lint, types, test, eval in that order and prints `gate: GREEN` | `make gate` |
| 7 | `make gate` fails on the first failing stage and does not run later stages | introduce an unused import in a Python file, then `make gate`; expect a ruff failure and no `gate: GREEN` |
| 8 | Every requirement in the spec names a measurement command that exists as a Makefile target | `make -qp \| grep -E '^eval-(capture\|liveness\|identify\|dedup\|search\|policy):'` |
| 9 | A measurement command for an unimplemented suite exits non-zero rather than reporting a fake number | `make eval-identify; echo "exit=$?"` — expect a non-zero exit |
| 10 | CI runs `make gate` on every pull request and on pushes to main | GitHub Actions run on the pull request for this task, showing the `gate` job green |
| 11 | No raw pet imagery or generated metrics are tracked by git | `git ls-files \| grep -Ei '\.(jpg\|jpeg\|png\|heic\|mp4\|mov)$\|^evals/out/[^.]'` returns nothing |

## Out of scope

Any application code in `ml/`, `api/`, `contracts/` or `miniapp/`. The point of this task
is that the gate exists first.
