---
name: hfd-slices
description: >
  Decompose the ML project into vertical slices — each a self-contained
  experiment with a quantitative pass/fail gate — producing an immutable
  docs/prd-slices.md plus script-managed state. Use after /hfd-design, or
  "add <goal>" to append a new slice mid-project without replanning
  (new feature idea, extra validation, post-pivot work).
argument-hint: "[max N slices, biggest uncertainty first] | add <goal>"
---

## Prerequisites

constitution, hypothesis-doc, blind-research, design-decisions, model-card
must exist (missing → /hfd-grill, /hfd-research, /hfd-design respectively).
Context discipline: from blind-research load sections 1 and 5 in full;
if the doc exceeds ~1,500 words summarize sections 2-4 in ≤3 sentences each.

## Modes

- **Full plan** (default): produce docs/prd-slices.md from
  `.claude/skills/hfd-shared/templates/slices-template.md` (read at write
  time).
- **Add** (`/hfd-slices add <goal>`): incremental — the common case once
  a project is running. Do NOT regenerate the plan. Read only: the slice
  list (`python .claude/skills/hfd-shared/scripts/get_slice.py --list`),
  current state (`hfd_status.py`), and the design decisions the new slice
  touches. Construct ONE slice (same anatomy below), append it at the END
  of docs/prd-slices.md with the next number and a dated title, register
  it with `checkpoint.py add-slice`, and confirm with the user. If the
  goal is a small tweak against an existing metric rather than a new
  hypothesis aspect, recommend `/hfd-experiment` instead — it's cheaper.

## What a slice is

The smallest unit of ML work producing a verifiable result: vertical
(data→model→evaluation), tests exactly one aspect of the hypothesis, one
gate metric with a numeric threshold, one declared action if it fails
(cancelar / pivotar / iterar), executable in a single session (1-4 hours
of compute), artifacts declared with disk paths. More than 4 hours or
multiple gate metrics → split it.

## Ordering logic

1. **Risk-first**: cancellation-criteria tests before performance
   refinement — if the project will die, it dies in slice 1. Needed
   infrastructure rides inside that slice's steps.
2. **Data-before-model**: validate data assumptions before training on them.
3. **Dependency chains**: producers before consumers, declared explicitly.
4. **Assumptions first**: every `[ASSUMPTION]` in design-decisions gets a
   validation slice before dependent work.

## Construction procedure

1. List every testable claim from hypothesis-doc (candidate slices), every
   `[ASSUMPTION]` (validation slices), every testable cancellation
   criterion (mapped to its earliest slice).
2. Order per the logic above.
3. Apply the minimal-implementation test to EACH slice: "what is the least
   work that produces a number comparable to the threshold?" Strip the rest.
4. Walk the user through the plan slice by slice — position rationale and
   fail consequences — and wait for confirm/reorder/merge/split.
5. Write docs/prd-slices.md, then register every slice in state:

   ```
   python .claude/skills/hfd-shared/scripts/checkpoint.py add-slice <N> \
     --title "..." --metric <m> --op ">=" --threshold <t> \
     --fail-action "cancelar CC-NNNN|pivotar Slice X|iterar max N" \
     --steps "paso 1;paso 2;paso 3" [--depends-on 1,2]
   ```

## Constraints

- Exactly one numeric gate per slice; no qualitative gates.
- Every "cancelar" references a CC-ID from the constitution.
- Metric names must match the glossary; new metrics → flag for
  /hfd-constitution.
- No standalone infrastructure slices — setup rides inside the first slice
  that needs it (slice 1 may be bigger; that's expected).
- Slices share state only through declared on-disk artifacts.
- docs/prd-slices.md is IMMUTABLE once written: no status sections, no
  execution logs inside it. Live state belongs to docs/state/ via
  checkpoint.py. This keeps the plan cache-stable across every /hfd-run
  session.

## Context contract

Load: the five prerequisite docs (with the blind-research trimming rule).
Do NOT load docs/state/ history or src/ code. In add mode, load only the
slice list + status + touched decisions.
