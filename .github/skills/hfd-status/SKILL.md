---
name: hfd-status
description: >
  Instant HFD project dashboard: which artifacts exist, slice/gate status,
  experiment ledger best metrics, and the recommended next command. Use
  when the user asks "where are we", "what's next", "project status", or
  at the start of any session before picking an HFD command.
model: haiku
copilot-model: Claude Haiku 4.5
---

Status is computed deterministically — never derive it by reading docs.

## Procedure

1. Run:

   ```
   python .hfd/scripts/hfd_status.py
   ```

2. Relay the dashboard, then add AT MOST three sentences of interpretation:
   what the state means and why the suggested next command is right (or,
   if the user's stated goal points elsewhere, which command fits better).
   The dashboard reports a track — `modeling`, `analysis`, `both` or
   `unset`. Route accordingly: a small post-baseline metric change is
   `/hfd-experiment`, a data question is `/hfd-analyze`, a pipeline change
   is `/hfd-feature`, and none of them is a re-plan.

   Open work units outrank everything else: an unfinished unit in the
   ledger is the next thing to do, not a new one.

3. If the script reports failed slices awaiting human decision, surface the
   declared fail action (`cancelar` / `pivotar` / `iterar`) prominently.

## Context contract

Load: script output only. Do NOT open docs/prd-slices.md, docs/constitution.md
or any planning doc from this skill — that is the job of the command the
user runs next.

This contract is machine-readable in `.hfd/context.json`:
`context.py pack hfd-status` prints it, estimates its cost, and
flags anything over budget.
