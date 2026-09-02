---
name: hfd-experiment
description: >
  Incremental experiment loop for a project that already has a baseline:
  add a feature, tweak hyperparameters, try a data-cleaning change, test a
  small idea — as a micro-hypothesis measured against the current best
  metric, logged in an append-only ledger. Use for any small post-baseline
  change ("add feature X", "try lr=0.05", "would dropping nulls help?")
  instead of re-running the planning skills.
argument-hint: "<one-line change to try> [--metric AUC]"
copilot-model: GPT-5.4 mini
---

Start by loading exactly what this skill declares — no more, in this order:

```
python .hfd/scripts/context.py pack hfd-experiment
```

The manifest is generated from `.hfd/context.json`; the order is what keeps
the stable inputs byte-identical between sessions, which is what makes them
cacheable.

This is the day-to-day workhorse once slices have produced a baseline.
No new docs, no plan rewrite, no re-grilling — one change, one number,
one ledger row. Cost per experiment stays flat because the inputs it
loads are small and stable.

## Preconditions

At least one slice with status `pass` (check via `hfd_status.py`). If
there is no baseline yet, redirect to `/hfd-run`. If the proposed change
actually tests a NEW aspect of the hypothesis (new data source, new
target, new model family), redirect to `/hfd-slices add` — experiments
refine, slices validate. If it does not move a metric at all (a pipeline
feature, a fix, a refactor, a report), it belongs to `/hfd-feature`: the
experiment ledger is for numbers that beat other numbers.

## Loop

1. **The number to beat**:
   `python .hfd/scripts/experiment.py best --metric <m>`
   (falls back to the gate result in docs/state/slices.json if the ledger
   is empty). Recent context, if needed:
   `experiment.py show --last 5` — never re-read old experiment code.

2. **Micro-hypothesis** (state it before touching code, one line each):
   - Change: what will be modified, in one sentence
   - Why: the mechanism by which it should move the metric
   - Gate: `<metric>` must beat current best (or user-stated tolerance)
   If the user gave a vague idea, sharpen it to this form and confirm —
   one question maximum, not a grilling session.

3. **Implement minimally.** Touch the fewest files possible; follow
   docs/coding-standards.md; keep the change behind the same evaluation
   command the slices use so numbers stay comparable. Never change the
   evaluation dataset or split — that would make the ledger meaningless
   (dataset changes are a /hfd-design revisit).

4. **Evaluate** with the same command as the relevant slice's gate
   ("Cómo se computa"). Same data, same split, same seed policy.

5. **Log the verdict** (always — discards are as valuable as adopts):

   ```
   python .hfd/scripts/experiment.py add \
     --change "..." --hypothesis "..." --metric AUC --value 0.842 \
     --verdict adopt|discard|inconclusive --files "src/features/build_features.py"
   ```

6. **Adopt or revert**:
   - **adopt**: keep the code. If it changed the model's architecture,
     features, or headline metric, append a dated entry to
     docs/model-card.md "Actualizaciones".
   - **discard**: revert the code changes completely (git checkout or
     undo edits). The ledger row is the only trace — that's the point.
   - **inconclusive**: revert too, note what would disambiguate.

7. Report: verdict, value vs previous best (the script prints the delta),
   files touched, and — if a pattern is emerging across recent ledger
   rows (e.g., three feature ideas in a row failed) — one sentence saying
   so and what it suggests.

## Escalation rules

- An experiment that would violate a signed design decision → stop, name
  the decision, suggest `/hfd-design revisit <N>`.
- A result that trips a cancellation criterion threshold → surface the
  CC immediately, as /hfd-run would.
- More than ~3 related adopted experiments drifting the model away from
  its model card → suggest consolidating via a dated model-card update.

## Context contract

Load: experiment.py output (best + last 5), the one gate command, the
specific files being changed, coding-standards. Do NOT load: constitution,
hypothesis-doc, blind-research, design-decisions, prd-slices — the ledger
and state files carry everything this loop needs. This is what keeps
incremental iterations cheap.

This contract is machine-readable in `.hfd/context.json`:
`context.py pack hfd-experiment` prints it, estimates its cost, and
flags anything over budget.
