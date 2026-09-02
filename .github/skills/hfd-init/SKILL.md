---
name: hfd-init
description: >
  Bootstrap the canonical HFD ML project structure (src/, data/, docs/,
  tests/, placeholders, .gitignore, requirements.txt). Step 0, before
  /hfd-grill. Idempotent — safe on existing projects. Use when starting
  a new data science project or when the user asks to scaffold/initialize
  an ML repo.
argument-hint: "[--frameworks xgboost,lightgbm] [--tracking mlflow|dvc|both]"
model: haiku
copilot-model: Claude Haiku 4.5
---

Scaffolding is deterministic — a script does all of it. Do not create the
tree by hand and do not write placeholder files yourself.

## Procedure

1. Run the scaffold script (pass through any user preferences):

   ```
   python .hfd/scripts/init_project.py [--frameworks ...] [--tracking mlflow|dvc|both]
   ```

   It never overwrites existing files and prints a created/skipped report.

2. If `docs/coding-standards.md` was not created because it already existed,
   leave it alone. If it does not exist in this repo at all, copy it from the
   HFD preset (`docs/coding-standards.md` in the preset repository).

3. If the user did not specify frameworks or tracking, ask once (single
   question, both topics) AFTER running with defaults — the script is
   idempotent, so re-running with `--frameworks`/`--tracking` later only
   touches `requirements.txt` if it was just created. If it already existed,
   append the chosen packages with Edit instead.

4. Relay the script's report verbatim, then state the next step:
   run `/hfd-grill` to build the hypothesis.

## Constraints

- Never run `pip install` — only requirements.txt changes.
- Never create sample/fake data. `data/` holds only `.gitkeep` files.
- This skill does NOT create docs/constitution.md or docs/hypothesis-doc.md
  (that is /hfd-grill's job).

## Context contract

Load: nothing beyond the script output. Do not read the created files back.

This contract is machine-readable in `.hfd/context.json`:
`context.py pack hfd-init` prints it, estimates its cost, and
flags anything over budget.
