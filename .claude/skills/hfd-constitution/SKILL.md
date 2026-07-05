---
name: hfd-constitution
description: >
  Surgical revision of docs/constitution.md — new data source discovered,
  success criteria changed, scope narrowed, glossary reconciliation after
  a pivot — with cascade checking against downstream artifacts. Never the
  bootstrap step (/hfd-grill creates it). Use when project ground truth
  changes mid-flight.
argument-hint: "<what changed> [verify downstream]"
model: haiku
---

## Prerequisites

docs/constitution.md exists (else → /hfd-grill). Read it fully — it is
the only doc loaded upfront.

## Procedure

1. **Scope the revision.** Ask what changed and which sections need
   revision if not stated. One section at a time — surgical edits only.
   This is the one planning doc edited in place; revisions are rare and
   deliberate, so the cache cost is accepted.

2. **Cascade check.** After each change, grep docs/ for references to the
   changed content (term, metric name, CC-ID, source name) and open ONLY
   the files that match:
   - hipótesis central changed → does hypothesis-doc still align?
   - criterios de éxito changed → do gate thresholds in prd-slices and
     docs/state/slices.json still match?
   - fuentes de datos changed → is blind-research still current?
     (suggest `/hfd-research refresh <source>`)
   - criterios de cancelación changed → is any criterion now triggered
     by a recorded gate result in docs/state/slices.json?
   - glosario changed → search downstream docs for the old term.
   Surface each cascade; do NOT auto-fix downstream artifacts — flag them
   and let the user decide which command to re-run.

3. **Cancellation criteria gate.** A proposed new CC must satisfy all
   three: hard to reverse, surprising without context, result of a real
   trade-off. If one is missing, say which and suggest strengthening or
   skipping.

4. **Update the executive summary** to the post-revision state, and
   append a row to the revision history table (move older rows to
   docs/revision-history.md beyond 5).

## Constraints

- Never delete triggered cancellation criteria — mark "Disparado" + date.
- Glossary stays free of implementation terms.
- Sole output: updated docs/constitution.md. No new files.

## Context contract

Load: constitution + the user's declared change. Downstream docs only
when the cascade grep hits them, one at a time.
