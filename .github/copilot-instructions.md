# Hypothesis-First Development (HFD) — Global Instructions

> Always-on context for every Copilot interaction in this project.

ML/DS workflow: falsifiable hypothesis → blind research → design decisions
→ vertical slices with quantitative gates → incremental experiments.

## Workflow

```
/hfd-init → /hfd-grill → /hfd-research → /hfd-design → /hfd-slices → /hfd-run (xN)
                                                                        ↓ baseline
/hfd-status (anytime)   /hfd-constitution (revisions)            /hfd-experiment (loop)
```

Post-baseline incremental paths — never re-run the full workflow for a
small change: small tweak → `/hfd-experiment`; new hypothesis aspect →
`/hfd-slices add`; changed ground truth → `/hfd-constitution`; changed
data → `/hfd-research refresh <source>`; re-open one decision →
`/hfd-design revisit <N>`.

## Global rules

1. **State split (context economy)**: planning docs in `docs/` are
   immutable after creation — new content is appended at the END, never
   edited mid-file, so they stay byte-stable across sessions and never
   need re-summarizing. Volatile state (checkpoints, gate results,
   experiment ledger) lives in `docs/state/` and is written ONLY through
   the scripts in `.hfd/scripts/` (checkpoint.py, experiment.py).
   Details: `.hfd/references/state-and-caching.md`.
2. **Scripts before prose**: project status via
   `python .hfd/scripts/hfd_status.py`, slice extraction via
   `get_slice.py`, data profiles via `profile_data.py` — never derive
   these by reading and summarizing whole documents.
3. **Context contract**: each agent declares what it loads; do not load
   artifacts outside that contract "for context".
4. **Gates are numeric** and never renegotiated after seeing the result.
5. **One question at a time** in interrogation agents (grill, design).
6. **Language**: artifact content in Spanish; agent status messages and
   code comments in English. Every planning doc starts with `## Resumen
   ejecutivo` describing the plan (never live status).
7. ML terminology, not software terminology: user story → hipótesis de
   negocio; acceptance criteria → gate cuantitativo; task breakdown →
   slice architecture; definition of done → gate pass/fail.

## Code

- Standards: `docs/coding-standards.md` (auto-applied via
  `.github/instructions/python-ml.instructions.md`).
- Docs → `docs/`, code → `src/`, tests → `tests/`, exploration only →
  `notebooks/` (reusable functions extracted to `src/` before a slice closes).
