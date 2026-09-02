# Hypothesis-First Development (HFD) — Global Instructions

> Always-on context for every Copilot interaction in this project. Kept
> short and stable on purpose: this file is prepended to every request, so
> churn here invalidates every cached prefix in the repo.

Two tracks over one repository:

- **Modeling** — falsifiable hypothesis → blind research → design decisions
  → vertical slices with quantitative gates → incremental experiments.
- **Analysis** — a question → an agreed metric definition → a reproducible
  script → validity checks → a dated report.

Daily development (pipeline features, fixes, refactors, scheduled reports)
is shared by both and runs through `/hfd-feature`.

## Routing

| Request | Command |
|---------|---------|
| Where are we / what's next | `/hfd-status` |
| Scaffold the project | `/hfd-init` |
| Answer a data question | `/hfd-analyze <question>` |
| Re-run a past analysis on new data | `/hfd-analyze refresh <W-id>` |
| Build/fix/refactor code, add a source | `/hfd-feature <what>` |
| Small change against a modeled metric | `/hfd-experiment <change>` |
| New aspect of the hypothesis | `/hfd-slices add <goal>` |
| Execute or resume a planned slice | `/hfd-run` |
| Ready to commit? | `/hfd-review` |
| Session feels expensive / context drift | `/hfd-context` |
| Ground truth changed | `/hfd-constitution` |
| Data changed | `/hfd-research refresh <source>` |
| Re-open a signed decision | `/hfd-design revisit <N>` |

Never re-run the full planning workflow for a small change.

## Global rules

1. **Context contract**: before loading anything, run
   `python .hfd/scripts/context.py pack <skill>` and load exactly what it
   lists, in that order. Not "for context", not "just in case" — the
   contract in `.hfd/context.json` is enforceable and CI checks it.
2. **State split (cache economy)**: documents in `docs/` are immutable
   after creation — new content is appended at the END, never edited
   mid-file, so their bytes stay identical between sessions. Volatile state
   (checkpoints, gates, ledgers) lives in `docs/state/` and is written ONLY
   through `.hfd/scripts/` (checkpoint.py, experiment.py, worklog.py,
   context.py). Details: `.hfd/references/context-management.md`.
3. **Scripts before prose**: status via `hfd_status.py`, one slice via
   `get_slice.py`, one section via `context.py show "doc#Section"`, data
   profiles via `profile_data.py`, checks via `verify.py` — never derive
   these by reading and summarizing whole documents.
4. **Everything is verified by a command.** Modeling work has a numeric
   gate; analysis and feature work have a stored verification command in
   the ledger. No command, no done.
5. **Gates are numeric** and never renegotiated after seeing the result.
6. **One question at a time** in interrogation commands (grill, design).
7. **Language**: artifact content in Spanish; status messages and code
   comments in English. Every planning doc starts with `## Resumen
   ejecutivo` describing the plan (never live status).
8. ML terminology, not software terminology: user story → hipótesis de
   negocio; acceptance criteria → gate cuantitativo; task breakdown →
   slice architecture; definition of done → gate pass/fail.

## Code

- Standards: `docs/coding-standards.md` (auto-applied via
  `.github/instructions/`).
- Docs → `docs/`, pipeline code → `src/`, analyses → `src/analysis/`,
  queries → `sql/`, reports → `reports/`, tests → `tests/`, exploration
  only → `notebooks/` (reusable functions extracted to `src/` before a unit
  or slice closes).
