---
name: hfd-review
description: >
  Pre-commit gate for an HFD project: run the deterministic verification
  pass (structure, context cache health, state consistency, docs
  discipline, linters, tests), review the working diff against the coding
  standards, and propose a commit message tied to the ledger. Use before
  committing, before opening a PR, or when asked "is this ready".
argument-hint: "[--quick] [what changed, if not obvious from the diff]"
copilot-model: GPT-5 mini
---

Most of this review is a script. Your job is the part a script cannot do:
read the diff and judge whether the change is what the ledger says it is.

## Session start

```
python .hfd/scripts/context.py pack hfd-review
python .hfd/scripts/verify.py
git status --short && git diff --stat
```

## 1. Deterministic pass

`verify.py` returns PASS/WARN/FAIL per area. Do not re-derive any of it by
reading files. Handle FAILs in this order — each has one correct fix:

| FAIL | Fix |
|------|-----|
| `context` — a planning doc was edited mid-file | Move the change to the END of the file as a dated section; the original text goes back to what the lock has. Then `context.py freeze`. |
| `state` — a declared artifact is missing | Either produce the artifact or reset the step (`checkpoint.py step N M reset`) / reopen the unit. Never edit the JSON. |
| `state` — a unit closed without a passing verification | Run its verification command; close it again with the real verdict. |
| `lint` / `tests` | Fix the code. Never silence the check. |

## 2. Read the diff (the part that needs judgment)

Load ONLY the changed files (`git diff --name-only`). Check:

- **Scope**: does the diff match the intent recorded in the ledger unit or
  slice? Unrelated changes riding along are the finding — name them.
- **Standards**: type hints, Google docstrings, no magic numbers, no bare
  `except`, no hardcoded paths, no god scripts (`docs/coding-standards.md`).
- **Leakage**: no credentials, no absolute local paths, no data files, no
  notebook outputs, no `data/` contents staged.
- **Reproducibility**: seeds set where results depend on them; analysis
  numbers printed with n and window; SQL in `sql/`, not embedded.
- **Notebook rule**: reusable logic extracted to `src/`.
- **Tests**: every behavioural change has a test that would fail without it.

Report findings most-severe first, each as: file:line, what breaks, the fix.
Distinguish "must fix before commit" from "worth doing next".

## 3. Ledger consistency

- Work units still `wip` whose code is clearly finished → close them.
- Units closed with artifacts that are not on disk → fix before commit.
- Slices in `en_progreso` with every step done → the gate has not been
  evaluated; run `/hfd-run` rather than committing a half-closed slice.

## 4. Commit message

Propose (do not run) a message shaped like the work:

```
<type>: <what changed, imperative, one line>

<why, one or two lines>

Verified: <the exact command that proves it>
Ledger: W014  |  Slice 3 gate: AUC 0.81 >= 0.78
```

`type` ∈ feat, fix, refactor, data, analysis, docs, chore. Commit only when
the user says so; never commit with FAILs outstanding, and never `--no-verify`.

## When the review is clean

Say so plainly, in one line, with the verification command that backs it.
Then stop — a clean review does not need a summary of everything you read.

## Context contract

Load: coding-standards, verify.py output, context health, and the changed
files. Do NOT load planning documents — a review reads the diff and the
standards, not the plan.
