# Hypothesis-First Development (HFD)

Two tracks over one repository, sharing scripts, ledgers and context rules:

- **Modeling**: falsifiable hypothesis → blind research → design decisions
  → vertical slices with quantitative gates → incremental experiments.
- **Analysis**: question → agreed metric definition → reproducible script →
  validity checks → dated report.

Daily development (features, fixes, refactors, new sources) is shared and
runs through `/hfd-feature`.

## Workflow

```
setup     /hfd-init
modeling  /hfd-grill → /hfd-research → /hfd-design → /hfd-slices → /hfd-run (xN)
                                                                     ↓ baseline
                                                          /hfd-experiment (loop)
analysis  /hfd-analyze <question>  →  /hfd-analyze refresh <W-id>
daily     /hfd-feature <change>  →  /hfd-review  →  commit
anytime   /hfd-status   /hfd-context   /hfd-constitution
```

Post-baseline incremental paths: small metric change → `/hfd-experiment`;
code/pipeline change → `/hfd-feature`; data question → `/hfd-analyze`;
new hypothesis aspect → `/hfd-slices add`; changed ground truth →
`/hfd-constitution`; changed data → `/hfd-research refresh <source>`;
re-open a decision → `/hfd-design revisit <N>`.

## Global rules

1. **Context contract**: run `python .hfd/scripts/context.py pack <skill>`
   before loading anything, and load exactly what it lists, in that order.
   Contracts live in `.hfd/context.json`; loading outside them is a
   violation, not a judgment call.
2. **State split (cache discipline)**: planning docs in `docs/` are
   immutable after creation — new content is appended at the END, never
   edited mid-file. Volatile state (checkpoints, gate results, ledgers)
   lives in `docs/state/` and is written ONLY through `.hfd/scripts/`
   (checkpoint.py, experiment.py, worklog.py, context.py).
   Details: `.hfd/references/context-management.md`.
3. **Scripts before prose**: project status via `hfd_status.py`, slice
   extraction via `get_slice.py`, one doc section via `context.py show
   "doc#Section"`, data profiles via `profile_data.py`, pre-commit checks
   via `verify.py` — never derive these by reading and summarizing whole
   documents.
4. **Everything is verified by a command**: a numeric gate for slices and
   experiments, a stored verification command for analyses and features.
   No command, no done.
5. **Gates are numeric** and never renegotiated after seeing the result.
6. **One question at a time** in interrogation skills (grill, design).
7. **Language**: artifact content in Spanish; status messages and code
   comments in English. Every planning doc starts with `## Resumen
   ejecutivo` describing the plan (never live status).
8. ML terminology, not software terminology: user story → hipótesis de
   negocio; acceptance criteria → gate cuantitativo; task breakdown →
   slice architecture; definition of done → gate pass/fail.

## Code

- Standards: `docs/coding-standards.md` (read before writing pipeline or
  analysis code).
- Docs → `docs/`, pipeline code → `src/`, analyses → `src/analysis/`,
  queries → `sql/`, reports → `reports/`, tests → `tests/`, exploration
  only → `notebooks/` (reusable functions extracted to `src/` before a
  slice or work unit closes).

## Maintaining this preset

`.claude/skills/` is canonical. After editing a skill run
`python .hfd/scripts/sync_skills.py` to mirror it to `.github/skills/` and
regenerate the Copilot prompt wrappers; CI runs `--check`. Harness tests
live in `.hfd/tests/`.
