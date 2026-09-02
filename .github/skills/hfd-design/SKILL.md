---
name: hfd-design
description: >
  Technical design decisions for the ML project — data strategy, model
  architecture (via Socratic grilling), risk/cancellation alignment,
  infrastructure. Produces docs/design-decisions.md and docs/model-card.md.
  Use after /hfd-research, or "revisit <N>" to re-open a single signed
  decision when reality changed (new data, failed slice, pivot).
argument-hint: "[team experience, concerns, constraints] | revisit <decision N>"
copilot-model: Claude Sonnet 4.6
---

Start by loading exactly what this skill declares — no more, in this order:

```
python .hfd/scripts/context.py pack hfd-design
```

The manifest is generated from `.hfd/context.json`; the order is what keeps
the stable inputs byte-identical between sessions, which is what makes them
cacheable.

## Prerequisites

docs/constitution.md, docs/hypothesis-doc.md, docs/blind-research.md must
exist. If missing → tell the user: constitution/hypothesis → `/hfd-grill`,
blind-research → `/hfd-research`. Read blind-research section 5
(contradictions) with special attention.

## Modes

- **Full** (default): all four decision areas, producing both documents.
- **Revisit** (`/hfd-design revisit 2`): incremental. Read ONLY the named
  decision from docs/design-decisions.md plus any blind-research addenda.
  Re-grill that one decision, then append a dated superseding entry at the
  END of the file: `## Decisión {N}bis ({fecha}) — supersedes Decisión {N}`.
  Never edit the original decision in place — the audit trail and the
  cache-stable prefix both depend on it. Add a matching dated entry to
  docs/model-card.md "Actualizaciones" if the model or evaluation changed.

## Decision procedure (areas 1, 3, 4)

For each decision: state it in one sentence → list ≥2 alternatives → cite
the specific blind-research finding supporting/undermining each (no
citation = tag `[ASSUMPTION — no data evidence]`) → note relevant
contradictions → recommend with justification → wait for explicit user
sign-off before recording. One decision at a time, never batched.

- **Area 1 — Data strategy**: sources in/out, missing-value handling,
  blocks-severity contradictions (acquire data / change hypothesis /
  accept degradation), granularity transforms, label strategy and noise
  tolerance, split strategy justified by the data's characteristics.
- **Area 3 — Risk and cancellation alignment**: map each cancellation
  criterion to the earliest checkpoint that can test it; flag any that are
  only testable at the very end as structural risk. If a "blocks
  hypothesis" contradiction directly triggers a cancellation criterion:
  STOP before area 4, report, and wait for continue/pivot/cancel.
- **Area 4 — Infrastructure & reproducibility**: one sentence each —
  where training/eval runs, experiment versioning, frozen eval dataset,
  production handoff format. Anything not affecting hypothesis validation:
  "N/A — post-validation concern."

## Area 2 — Model architecture (Socratic grilling)

Do NOT present a menu of model families. Interrogate:

1. **Elicit intent** (one question at a time): what model and why; what
   frameworks the team has run in production; their experience with the
   proposed model.
2. **Challenge against blind research** (one challenge at a time), using
   concrete trade-offs anchored in findings. Patterns: complexity
   mismatch, stack mismatch (who maintains it?), scale mismatch (training
   time vs compute vs iteration budget), interpretability mismatch (both
   directions), baseline ignorance (what does the added complexity buy
   over the current baseline?).
3. **Anchor in specifics.** The recorded decision must include: exact
   algorithm + objective/config, why it beat the challenged alternatives
   (citing findings), hyperparameter strategy (approach, not values), team
   capability, inference constraints, interpretability requirement,
   evaluation protocol vs the blind-research baseline, experiment tracking.
   The output is a technical justification, not a selection.

## Outputs

- **docs/design-decisions.md** — executive summary (decisions count,
  assumptions count, model selected, top technical risk, CC mapping),
  contradiction impact table, then one section per decision with
  Pregunta / Alternativas / Decisión / Justificación / Firmado por {name}
  el {fecha}. For area 2 include the grilling record (proposed model,
  challenged alternatives, team capability, interpretability).
- **docs/model-card.md** — from
  `.hfd/templates/model-card-template.md` (read at
  write time). Forward-looking; all later real-vs-planned changes are
  dated appends in its "Actualizaciones" section.

## Constraints

- Every decision cites blind-research or carries the `[ASSUMPTION]` tag.
- No api-spec.json, data-model.md, or software architecture artifacts.
- Don't pre-decide what slices will decide by experimentation — design
  covers strategy, slices cover execution.

## Context contract

Load: constitution + hypothesis-doc + blind-research (+ its addenda) +
decisions made so far this session. Do NOT load prd-slices, docs/state/,
or execution artifacts. In revisit mode, load only the named decision and
related findings, not the whole decision doc.

This contract is machine-readable in `.hfd/context.json`:
`context.py pack hfd-design` prints it, estimates its cost, and
flags anything over budget.
