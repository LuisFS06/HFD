# Hypothesis-First Development (HFD) — Global Instructions

> Always-on context for every Copilot interaction in this project.
> Equivalent to preset.yml in Spec-Kit.

## What this is

This project uses **Hypothesis-First Development** — a workflow for
ML/Data Science that replaces the software engineering lifecycle
(user stories → tasks → implement) with one native to ML (falsifiable
hypothesis → blind research → design decisions → vertical slices →
execution with quantitative gates).

## Terminology map

Do not use software engineering terms. Use ML equivalents:

| Software term | ML equivalent |
|--------------|---------------|
| User Story | Hipótesis de negocio |
| Specification | Hypothesis document |
| Acceptance Criteria | Gate cuantitativo |
| Implementation Plan | Design decisions |
| Task breakdown | Slice architecture |
| Definition of Done | Gate pass/fail |
| Research | Blind research |
| CONTEXT.md | docs/constitution.md |
| ADR | Criterio de cancelación |

## Workflow order

```
/initproject → /grillme → /blindresearch → /designaligner → /slicearchitect → /executor
                                                ↕
                                         /constitution (revision only, any time)
```

| Step | Command | Produces | Requires |
|------|---------|----------|----------|
| 0 | `/initproject` | Project structure, .github/ setup | Nothing |
| 1 | `/grillme` | docs/hypothesis-doc.md, docs/constitution.md | Project structure |
| — | `/constitution` | docs/constitution.md (revision) | docs/constitution.md exists |
| 2 | `/blindresearch` | docs/blind-research.md | docs/constitution.md |
| 3 | `/designaligner` | docs/design-decisions.md, docs/model-card.md | docs/hypothesis-doc.md, docs/blind-research.md |
| 4 | `/slicearchitect` | docs/prd-slices.md | docs/design-decisions.md, docs/model-card.md |
| 5 | `/executor` | Code, artifacts, updated docs/prd-slices.md | docs/prd-slices.md |

## Global rules

1. Every command verifies that artifacts from the previous step exist
   before executing.
2. Target context window usage: below 40% per session.
3. All ML terminology replaces software terminology per the map above.
4. **Language**: templates and artifact content are in Spanish. Agent
   status messages and code comments are in English.
5. **Executive summary**: every agent that produces or updates a
   document must include a `## Resumen ejecutivo` section at the top
   summarizing the key points for quick review.
6. **One question at a time**: agents that interrogate the user
   (grillme, designaligner) ask one question, wait for response,
   then proceed.
7. **Output location**: all document artifacts are written to
   `docs/`. Code artifacts go to `src/`, `tests/`, or
   `notebooks/` per the canonical project structure.
