---
description: "Write rules for HFD documents and state — auto-applied to docs/"
applyTo: "docs/**/*.md,docs/**/*.json,docs/**/*.jsonl"
---

## Documents in docs/ are append-only

New content goes at the END of the file as a dated section. Never edit the
middle or the top: every session re-reads these files, and a changed prefix
invalidates the cached context for all of them.

| File | How it changes |
|------|----------------|
| `hypothesis-doc.md` | `## Enmienda {fecha}` at the end |
| `blind-research.md` | `## Addendum {fecha} — {fuente}` at the end |
| `design-decisions.md` | `## Decisión {N}bis ({fecha}) — supersedes Decisión {N}` |
| `model-card.md` | entry under "Actualizaciones" at the end |
| `prd-slices.md` | new `## Slice N` at the end (`/hfd-slices add`) |
| `data-contracts.md` | new `## Contrato — {métrica} ({fecha})` at the end |
| `constitution.md` | the one exception: revised in place, by `/hfd-constitution` only |

Executive summaries describe the plan, never live status. Live status
belongs to `docs/state/` and is read with `hfd_status.py`.

## docs/state/ is script-owned

Never hand-edit `slices.json`, `experiments.jsonl`, `worklog.jsonl`,
`journal.md` or `context-lock.json`. Use `checkpoint.py`, `experiment.py`,
`worklog.py` and `context.py` — they write atomically, validate inputs and
keep the ledgers append-only.

## Proof

`python .hfd/scripts/context.py verify` fails when a document was edited
mid-file. Run `context.py freeze` after any deliberate, accepted change.
