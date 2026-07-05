---
name: hfd-status
description: >
  Instant HFD project dashboard: which artifacts exist, slice/gate status,
  experiment ledger best metrics, and the recommended next command. Use
  when the user asks "where are we", "what's next", "project status", or
  at the start of any session before picking an HFD command.
model: haiku
---

Status is computed deterministically — never derive it by reading docs.

## Procedure

1. Run:

   ```
   python .claude/skills/hfd-shared/scripts/hfd_status.py
   ```

2. Relay the dashboard, then add AT MOST three sentences of interpretation:
   what the state means and why the suggested next command is right (or,
   if the user's stated goal points elsewhere, which command fits better —
   e.g. a small post-baseline change is `/hfd-experiment`, not a re-plan).

3. If the script reports failed slices awaiting human decision, surface the
   declared fail action (`cancelar` / `pivotar` / `iterar`) prominently.

## Context contract

Load: script output only. Do NOT open docs/prd-slices.md, docs/constitution.md
or any planning doc from this skill — that is the job of the command the
user runs next.
