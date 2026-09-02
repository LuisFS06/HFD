---
name: hfd-context
description: >
  Inspect and repair the project's context economy: what each skill loads
  and what it costs, which documents are still byte-stable enough to be
  cached, and which were edited mid-file and broke that. Use when a
  session feels expensive, when CI reports context drift, before adding a
  new document, or when asked "why is this so slow / so many tokens".
argument-hint: "[pack <skill> | verify | freeze | budget | stats | show <ref>]"
copilot-model: Claude Haiku 4.5
---

Everything here is a script. Run it, read it, act on it — do not open
documents to answer questions this tool already answers.

## The model in one paragraph

Both Claude Code and GitHub Copilot reuse the longest byte-identical
**prefix** of a request. HFD therefore splits every input into tiers:
`frozen` (never changes) → `append-only` (grows at the end, prefix intact)
→ `revisable` (edited in place, rarely) → `volatile` (script-managed state)
→ `probe` (command output) → `task` (today's files). Loading them in that
order keeps the expensive, stable half of the context identical between
sessions, so only the cheap tail is new. Editing a planning doc in the
middle destroys that for every session afterwards — which is why it is a
FAIL, not a style preference. Full rationale:
`.hfd/references/context-management.md`.

## Commands

```
python .hfd/scripts/context.py stats            # inventory by tier, cacheable share
python .hfd/scripts/context.py budget           # estimated cost per skill vs its budget
python .hfd/scripts/context.py verify           # append-only proof against the lock
python .hfd/scripts/context.py freeze           # re-lock after deliberate changes
python .hfd/scripts/context.py pack <skill>     # what that skill loads, in order
python .hfd/scripts/context.py show "constitution#Glosario"   # one section, not the file
python .hfd/scripts/context.py pack <skill> --emit            # the whole pack as one blob
```

## Procedure

1. Run `verify`. Then `stats` and `budget` only if the question needs them.
2. Interpret, in at most five lines:
   - **MUTATED (FAIL)** — name the file and the fix: move the edit to the
     END as a dated section, restore the original prefix, then `freeze`.
     If the mid-file edit was correct and necessary (a wrong glossary
     definition, say), keep it — accept one cache miss, run `freeze`, and
     say the cost was paid deliberately.
   - **OVER budget** — the contract loads whole files where a section
     would do. Propose the specific `context.py show "doc#Section"` refs,
     or splitting the document.
   - **NEW (unlocked)** — run `freeze`.
3. `freeze` is the only write this skill makes. Never edit
   `docs/state/context-lock.json` by hand.

## Adding a document to the registry

New shared document → add it to `.hfd/context.json` under `artifacts` with
its tier and owner, add the ref to the contracts that genuinely need it,
then `freeze`. Prefix the ref with `?` when the document is track-specific
(`?constitution#Glosario` in an analysis contract): optional refs are used
when present and skipped silently when the project never creates them.

If a document is not in a contract, no skill may load it: that is the point
of the registry, and "for context" is not a reason.

## For GitHub Copilot specifically

Copilot rebuilds the request per turn, so ordering matters more, not less:

- Start a session with `pack <skill>` and load exactly that, top to bottom.
- Prefer `--emit` when pasting context into a chat surface — one ordered
  blob beats several ad-hoc file mentions, which arrive in whatever order
  the editor picked.
- Keep `.github/copilot-instructions.md` small and stable; it is prepended
  to every request, so churn there invalidates every cached prefix.
- Path-scoped `.github/instructions/*.instructions.md` attach only to
  matching files, so heavy rules do not ride along on unrelated turns.

## Context contract

Load: script output only. This skill never opens a planning document —
if it did, it would be part of the problem it diagnoses.
