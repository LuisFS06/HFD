# Context management — how HFD keeps sessions cheap

The harness treats context as a managed resource with a registry
(`.hfd/context.json`), a tool (`.hfd/scripts/context.py`) and a lock
(`docs/state/context-lock.json`). This file explains the model; the tool
enforces it.

## The mechanic being exploited

LLM prompt caching — in Claude Code, in GitHub Copilot, in the APIs behind
both — reuses the longest **byte-identical prefix** of a request. Not "the
same files": the same bytes, in the same order, from the start. Two
consequences drive every rule below:

1. **A byte changed early invalidates everything after it.** Editing the
   top of a 4,000-token plan is as expensive as rewriting the whole plan.
2. **Order is part of the identity.** The same five documents loaded in a
   different order are a different prefix, so a session that loads whatever
   seems relevant today never hits a warm cache, even when it reads exactly
   the files it read yesterday.

## Tiers

Every registered artifact declares a tier. The tier is the cache contract.

| Tier | Changes how | Load order | Examples |
|------|-------------|-----------|----------|
| `frozen` | never after creation | 1st | `docs/coding-standards.md` |
| `append-only` | grows at the END only | 2nd | `hypothesis-doc.md`, `blind-research.md`, `design-decisions.md`, `prd-slices.md`, `data-contracts.md`, the ledgers |
| `revisable` | edited in place, rarely | 3rd | `docs/constitution.md` |
| `volatile` | rewritten by scripts | 4th | `docs/state/slices.json` |
| `probe` | computed per call | 5th | `hfd_status.py`, `get_slice.py N` |
| `task` | today's files | last | whatever the change touches |

Stable-first ordering means the expensive half of the context is identical
between sessions and only the cheap tail is new.

## Why "append at the end" is a hard rule

A dated section appended to the END of `design-decisions.md` leaves every
preceding byte untouched: the cached prefix survives, and the new content
is the only thing the model pays full price for. The same edit made in the
middle — "just fixing decision 2 in place" — invalidates the cache for that
file and everything loaded after it, in every future session, for as long
as the project lives.

That is why superseding entries, amendments, addenda and model-card updates
are all appends, and why `context.py verify` reports a mid-file edit as
FAIL rather than as a style note. It is also why planning documents describe
the *plan* and never live status: status changes daily, so a status section
inside a plan document guarantees a daily cache miss on the largest inputs.

Live state lives in `docs/state/`, is small, and is written only by
`checkpoint.py`, `experiment.py` and `worklog.py`.

## The tool

```
context.py pack <skill> [--slice N] [--metric M]   # ordered manifest + cost
context.py pack <skill> --emit                     # the pack as one ordered blob
context.py show "constitution#Glosario"            # one section, not the file
context.py freeze                                  # record hashes in the lock
context.py verify [--json]                         # append-only proof (CI gate)
context.py budget                                  # cost per skill vs its budget
context.py stats                                   # inventory, cacheable share
```

`verify` classifies each locked artifact:

- **unchanged** — byte-identical since the lock; fully cacheable.
- **appended** — the locked bytes are still a prefix of the file; the cache
  survives and only the new tail is paid for.
- **mutated** — the prefix changed. FAIL for `frozen` and `append-only`,
  WARN for `revisable` (that tier is allowed to change, and pays for it).
- **missing** — locked but gone from disk.

## Contracts

`.hfd/context.json` maps each skill to what it may load (`load`), what it
must not (`never`) and a token budget. The contract is enforceable, not
advisory: `context.py pack` prints exactly the load list, and CI can fail a
skill whose declared context exceeds its budget.

A ref prefixed with `?` is optional: `?constitution#Glosario` is loaded
when the file exists and skipped silently when it does not, so an
analysis-only project is not nagged about modeling artifacts it will never
create.

`never` entries are correctness rules as much as cost rules. `/hfd-research`
must not load `hypothesis-doc.md` — blind research that has seen the
hypothesis is not blind research, it is confirmation.

## Section refs

`context.py show "constitution#Criterios de cancelacion"` prints one
markdown section (matching is accent- and case-insensitive, so the
unaccented ref finds the accented heading). Loading a 300-token section
instead of a 4,000-token document is the cheapest available win, and it is
what lets `/hfd-run` honour the constitution without ingesting it.

## GitHub Copilot specifics

- `.github/copilot-instructions.md` is prepended to every request. Keep it
  small and stable; churn there invalidates every cached prefix in the repo.
- `.github/instructions/*.instructions.md` attach by path glob, so heavy
  rules ride along only on the turns that touch matching files.
- `.github/prompts/hfd-*.prompt.md` are generated by `sync_skills.py` from
  the skills' frontmatter — same instructions on both platforms, with the
  per-step model pinned where it belongs.
- In chat surfaces prefer `context.py pack <skill> --emit`: one ordered blob
  beats several ad-hoc file mentions arriving in editor-chosen order.

## Adding a document

1. Add it to `.hfd/context.json` under `artifacts` with a tier and owner.
2. Add its ref to the contracts that genuinely need it — if no contract
   lists it, no skill may load it.
3. `context.py freeze`.

A document nobody is contractually allowed to load is a document nobody
pays for. That is the intended default.
