---
name: hfd.slicearchitect
description: >
  Decomposes the ML project into vertical slices, each with a verifiable
  hypothesis, minimal implementation, quantitative gate, and explicit
  action if the gate fails. Replaces /speckit.tasks — eliminates user-story
  grouping, [P] parallelisation markers, and file-path-centric ordering.
  Each slice is an independent agent session.
model: GPT-5 mini
---

## Prerequisites

Before executing, verify these artifacts exist:

1. `docs/constitution.md` — read success criteria (all three levels) and
   cancellation criteria.

2. `docs/hypothesis-doc.md` — read all verifiable hypotheses and their
   quantitative gates.

3. `docs/blind-research.md` — read sections 1 (data coverage) and 5
   (contradictions). If docs/blind-research.md exceeds 1,500 words, load
   only sections 1 and 5 in full; summarize sections 2–4 in ≤3
   sentences each.

4. `docs/design-decisions.md` — read all four decision areas.

5. `docs/model-card.md` — read the planned architecture and evaluation
   metrics.

If any is missing, stop and tell the user which command to run:
- No docs/constitution.md or docs/hypothesis-doc.md → `/grillme`
- No docs/blind-research.md → `/blindresearch`
- No docs/design-decisions.md or docs/model-card.md → `/designaligner`

## Slicing principles

### What a slice is

A slice is the smallest unit of ML work that produces a verifiable
result. It is NOT a task — it is a self-contained experiment with a
pass/fail gate. Slices are vertical (data→model→evaluation), not
horizontal layers ("prepare data", "train model", "evaluate"). Each
slice:

- Tests exactly one aspect of the hypothesis
- Produces a measurable result that can be compared to a threshold
- Has an explicit action if the gate fails: cancel, pivot, or iterate
- Can be executed in a single agent session without referencing other
  slices mid-execution
- Produces named artifacts that downstream slices can depend on
- ML artifacts (trained models, serialized datasets, evaluation results)
  must be declared in the "Artefactos producidos" table with their
  disk path

### Sizing heuristic

A well-sized slice can be executed in 1–4 hours of compute time and
produces exactly one gate metric. If a slice requires more than 4 hours
or produces multiple gate metrics, split it.

### Ordering logic

Slices are ordered by information value — the slice that resolves the
most uncertainty goes first:

1. **Risk-first**: slices that test cancellation criteria go before
   slices that refine performance. If the project is going to die,
   find out in slice 1, not slice 8. If testing a cancellation
   criterion requires infrastructure, that infrastructure setup is
   part of the cancellation-testing slice's implementation steps.
   The slice grows, but the ordering principle holds.
2. **Data-before-model**: slices that validate data assumptions go
   before slices that train models on that data.
3. **Dependency chains**: if slice B needs an artifact from slice A,
   A goes first. Declare dependencies explicitly.
4. **Assumptions first**: any decision marked `[ASSUMPTION — no data
   evidence]` in docs/design-decisions.md gets a validation slice before
   work that depends on that assumption.

Note: Slice 1 may be larger than subsequent slices because it includes
project setup (directory structure, dependencies, data access). This is
expected when "Do not include standalone infrastructure slices" applies.

## Slice construction

For each slice, produce the structure defined in
`.github/skills/ml-templates/tasks-template.md`
(see the "Slice N" section). Each slice must include:

- Hipótesis a validar (one sentence, derivable from docs/hypothesis-doc.md)
- Dependencias (artifact dependencies, data sources, design decisions)
- Implementación mínima (concrete steps, each producing a named artifact)
- Gate cuantitativo (metric, dataset, threshold, baseline, computation command)
- Acción si falla (exactly one: cancelar, pivotar, or iterar)
- Artefactos producidos (including ML artifacts like models and datasets)
- Estado de implementación (step-level tracking table, initially all `⬜ pendiente`)
- Notas de ejecución (empty section for executor to append runtime decisions)
- Estado (initially `pendiente`)

## Construction procedure

1. Read all prerequisite artifacts.

2. List every testable claim from docs/hypothesis-doc.md. These are the
   candidate slices.

3. List every `[ASSUMPTION — no data evidence]` from docs/design-decisions.md.
   Each one becomes a validation slice.

4. List every cancellation criterion from docs/constitution.md that has a
   testable condition. Each one maps to the earliest slice that can
   evaluate it.

5. Order the candidate slices using the ordering logic above.

6. For each candidate slice, apply the minimal implementation test:
   "What is the least work that produces a number I can compare to
   the threshold?" Strip everything else. Run this test explicitly
   on each slice — do not skip it.

7. Present the full slice plan to the user. Walk through each slice
   one at a time, explaining why it's in this position and what
   happens if its gate fails.

8. Wait for the user to confirm, reorder, merge, or split slices
   before finalizing.

## Output

Produce `docs/prd-slices.md` following the full structure defined in
`.github/skills/ml-templates/tasks-template.md`, including the summary
table, ordering rationale, per-slice details (with implementation state
table and execution notes section), execution log (initially empty),
and traceability matrices.

### Executive summary requirement

The document must start with a `## Resumen ejecutivo` section immediately
after the title. The executive summary must include:

- **Total de slices**: {N} slices planificados
- **Próximo slice**: Slice {N} — {título}
- **Slices completados**: {N} pass, {N} fail (initially: "Ninguno — proyecto nuevo")
- **Criterios de cancelación cubiertos**: {N} de {total} con checkpoint asignado
- **Assumptions por validar**: {N} slices de validación de assumptions
- **Estimación de esfuerzo**: {rango de horas total basado en sizing heuristic}
- **Mayor riesgo**: {el slice que, si falla con acción "cancelar", mata el proyecto}

## Constraints

- Every slice must have exactly one gate with a numeric threshold.
  No qualitative gates ("the model looks good").
- Every "cancelar" action must reference a cancellation criterion
  from docs/constitution.md. No orphan cancellation actions.
- Every metric name must match the glossary in docs/constitution.md. If a
  slice needs a metric not in the glossary, flag it for the next
  `/constitution` revision.
- Do not include standalone infrastructure or setup slices. If setup
  is needed, it belongs in the implementation steps of the first slice
  that needs it.
- Slices do not share state except through declared artifacts. Each
  slice is a self-contained agent session. State that carries over:
  files on disk (code, data, models) declared in "Artefactos producidos."
  State that does NOT carry over: in-memory variables, environment
  state, notebook state.
- Target context window: docs/constitution.md + docs/hypothesis-doc.md +
  docs/blind-research.md (sections 1 and 5, summarize 2-4 if >1,500 words) +
  docs/design-decisions.md + docs/model-card.md.
