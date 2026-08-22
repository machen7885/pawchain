# Task briefs

One unit of work per file, with its acceptance criteria attached. The agent implements the
file, not a conversation.

Every task brief contains exactly four things:

1. **Goal** — one paragraph, and the requirement it implements.
2. **Files you will touch** — decided before the work starts, so scope creep is visible in
   the diff.
3. **Acceptance criteria** — a numbered list of assertions.
4. **The command that proves each assertion** — an assertion with no command is not a
   criterion, it is a hope.

The loop this enables:

```
write task spec  ->  agent implements  ->  make gate  ->  review the diff  ->  merge
                          ^                   |
                          +----- red ---------+
```

You never enter the red loop. The agent reads the gate output and fixes its own work; you
look only at green diffs, and you review them against the task file rather than line by
line. Three failed gate cycles on the same task means the spec is wrong, not the agent —
stop and rewrite the criterion.

| Task | Implements | Week | Status |
|---|---|---|---|
| [task-000-harness](task-000-harness.md) | spec §3, the harness itself | 1 | done |
| [task-001](task-001.md) | REQ-001 capture quality gate | 2 | in progress — blocked on golden-set photos |
| [task-201](task-201.md) | golden capture set: schema and manifest | 2 | done |
| [task-202](task-202.md) | `make eval-capture` | 2 | done — exits non-zero until the golden set is real |
| [task-203](task-203.md) | `capture.process(frame)` | 2 | done |
| [task-204](task-204.md) | export and measure | 2 | infrastructure done, blocked on a trained model |
| [task-007](task-007.md) | REQ-007 dedup on enrolment | 3 | not started |
