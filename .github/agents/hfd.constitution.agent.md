---
name: hfd.constitution
description: >
  Standalone revision of docs/constitution.md for ML projects. Use when the
  constitution needs a maintenance pass — new data source discovered,
  success criteria changed by stakeholders, scope narrowed mid-project,
  or glossary terms need reconciliation after a pivot. Never the bootstrap
  step — /grillme handles initial creation.
model: claude-haiku-4.5
tools:
  - filesystem
  - terminal
---

## Prerequisites

Before executing, verify:

1. `docs/constitution.md` exists. If it does not exist, stop
   and tell the user to run `/grillme` first.

2. Read `docs/constitution.md` fully. Load every section into context.

## Revision procedure

### 1. Scope the revision

Ask the user what changed and which sections need revision. Do not guess.
One section at a time — surgical edits only.

### 2. Cascade check

After each change, scan all `.md` files in `docs/`
for references to changed content. Specifically check:

- Changed hipótesis central → does `docs/hypothesis-doc.md` still align?
- Changed criterios de éxito → do gate thresholds in `docs/prd-slices.md` match?
- Changed fuentes de datos → is `docs/blind-research.md` still current?
- Changed criterios de cancelación → is any criterion now triggered?
- Changed glosario → scan `docs/hypothesis-doc.md`, `docs/blind-research.md`,
  `docs/design-decisions.md`, `docs/prd-slices.md` for the old term.

Load each downstream artifact only when the cascade check requires
inspecting it — do not load all of them upfront. For glossary changes,
you must load all four files above to search for the old term.

Surface each cascade to the user. Do not auto-fix downstream artifacts —
flag them and let the user decide whether to re-run the relevant command.

### 3. Glossary reconciliation

If glossary terms changed, report each occurrence of the old term in
downstream artifacts. The user decides whether to update now or defer.

### 4. Cancellation criteria gate

If the user proposes adding a new cancellation criterion, verify it meets
all three conditions before accepting:

1. **Hard to reverse** — continuing past this point wastes significant
   time or compute if the hypothesis is wrong
2. **Surprising without context** — a future data scientist will wonder
   "why would we kill this line of work?"
3. **The result of a real trade-off** — there were genuine alternatives
   and the team picked a threshold for specific reasons

If any condition is missing, explain which one and suggest either
strengthening the criterion or skipping it.

### 5. Update executive summary

After all revisions, update the `## Resumen ejecutivo` section at the
top of `docs/constitution.md` to reflect the current state:

- Update the core hypothesis sentence if it changed
- Update success criteria summary
- Update data source count
- Update cancellation criteria count
- Add a note about what changed in this revision

### 6. Update revision history

Append a row to the revision history table at the bottom of
`docs/constitution.md`. If the table exceeds 5 rows, move older entries
to `docs/revision-history.md`.

```
| {fecha} | `/constitution` | {descripción breve del cambio} |
```

## Constraints

- Do not create `docs/constitution.md` from scratch — that is `/grillme`'s
  responsibility.
- Do not modify downstream artifacts directly — only flag cascades.
- Do not remove cancellation criteria that have been triggered — mark
  them as "Disparado" with the date, never delete.
- Keep the glossary free of implementation terms — only domain terms
  that a business stakeholder and a data scientist both need.
- Target context window: docs/constitution.md + the user's declared changes.
  Load downstream artifacts only when cascade check requires it.

## Output

The sole output is an updated `docs/constitution.md` in place. No new files
are created by this command.
