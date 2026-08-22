# task-201 — Freeze the golden capture set: schema, manifest, no implementation

**Implements** REQ-001, REQ-009, REQ-011 (`specs/00-system-spec.md` §6) · **Week** 2 ·
**Status** done (schema and tooling shipped; empty of real labels — see task-202)

## Goal

Define the format that turns 150 hand-labelled photos into evidence: a label schema, a
manifest format with a SHA-256 per image, and the rule for how a relabel gets recorded —
before a single photo is labelled. Writing this after labelling starts lets the schema bend
to whatever the labels happen to look like, which is the exact failure Idea 12 (facilitator
guide) warns about: the answer key has to exist before the answers.

This task defines the format. It does not label any photos — no data exists yet to label
(see `EVIDENCE.md`, Week 2 entry, left for the household's own decision once photos exist).

## Files touched

- `evals/golden/capture/manifest.json` — empty manifest (`{"version": 1, "images": []}`),
  the frozen-format placeholder that `evals/golden_capture.py` loads
- `evals/golden/capture/README.md` — the label schema, in full
- `evals/golden_capture.py` — `GoldenManifest`, `GoldenImage`, `load_manifest`,
  `verify_hashes`, `record_relabel`
- `specs/decisions/ADR-0006.md` — where the pixels behind the manifest live

## Label schema

Each entry in `manifest.json["images"]`:

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Stable identifier, e.g. `cat3-session1-0007` |
| `relative_path` | string | Path under `PAWCHAIN_GOLDEN_IMAGES` (ADR-0006) |
| `sha256` | string | Content hash of the file at that path, checked on every load |
| `label` | `"usable"` \| `"not_usable"` | The household's own eye, recorded before any model output is seen |
| `reason` | string \| null | Required when `label` is `"not_usable"`; one of the five failure classes from Block 0 (`no_cat`, `wrong_crop`, `blur`, `pose`, `illumination`) |
| `landmarks` | object \| null | Optional ground-truth five points (`left_eye`, `right_eye`, `nose`, `left_ear`, `right_ear`, each `[x, y]`), present only for the subset the operator also hand-labelled for the blur/pose/illumination sweep (task-202) |

## How a relabel is recorded

Per `evals/golden/README.md` rule 2 and `CLAUDE.md`'s "never rewrite a test to make it
pass": a label is never silently edited. `record_relabel(manifest, image_id, new_label,
new_reason, note)` returns a **new** manifest with the one entry changed and appends a
`relabels` array entry: `{image_id, old_label, new_label, note, at}`. The caller commits
that new manifest in a change that touches nothing else, with `note` explaining why the
original label was wrong — never to make a threshold look better.

## Acceptance criteria

| # | Assertion | Command that proves it |
|---|---|---|
| 1 | An empty manifest (`images: []`) loads without error | `pytest evals/test_golden_capture.py -k empty -q` |
| 2 | `load_manifest` raises on a manifest entry missing a required field | `pytest evals/test_golden_capture.py -k schema -q` |
| 3 | `verify_hashes` reports a mismatch when a referenced file's bytes differ from its recorded `sha256` | `pytest evals/test_golden_capture.py -k hash -q` |
| 4 | `record_relabel` never mutates the manifest object passed in, and appends exactly one `relabels` entry | `pytest evals/test_golden_capture.py -k relabel -q` |
| 5 | No image bytes are tracked by git anywhere under `evals/golden/` | `git ls-files evals/golden \| grep -Ei '\.(jpg\|jpeg\|png\|heic)$'` returns nothing |

## Out of scope

Labelling any real photograph. Training or tuning anything against the manifest — that is
task-202, and only once the manifest has real entries in it.
