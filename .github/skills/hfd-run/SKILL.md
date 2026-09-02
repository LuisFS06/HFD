---
name: hfd-run
description: >
  Execute ONE slice from the plan: implement its steps with script-managed
  checkpoints, evaluate the quantitative gate, record the result, and
  escalate to the human if the gate fails. Automatically resumes from the
  last checkpoint after a crash or interrupted session. Use to execute or
  resume the next pending slice, or a specific slice number.
argument-hint: "[slice N] [what changed since planning]"
copilot-model: GPT-5.4 mini
---

Start by loading exactly what this skill declares — no more, in this order:

```
python .hfd/scripts/context.py pack hfd-run
```

The manifest is generated from `.hfd/context.json`; the order is what keeps
the stable inputs byte-identical between sessions, which is what makes them
cacheable.

## Session start (cheap, script-first)

1. `python .hfd/scripts/hfd_status.py` — identifies
   the active or next slice and unmet dependencies. Do not read
   docs/prd-slices.md to figure this out.
2. Load ONLY the active slice's plan:
   `python .hfd/scripts/get_slice.py <N>`
3. Read: the design decisions referenced by the slice's "Asume decisión"
   field, docs/coding-standards.md, and the constitution's glossary +
   cancellation criteria sections. Nothing else.
4. Announce: "Executing Slice {N}: {title}. Gate: {metric} {op}
   {threshold}. Action if fail: {action}." Wait for user confirmation.

If status shows a slice `en_progreso`, this is a **resume**: run
`checkpoint.py show <N>`, verify each step marked `done` has its artifact
on disk (missing artifact → `checkpoint.py step N M reset`), read the tail
of docs/state/journal.md for that slice's notes, announce "Resuming Slice
{N} from step {next}", confirm, continue. Never re-execute steps whose
artifacts verify.

## Execution loop

`checkpoint.py start <N>` (it enforces dependency gating), then per step:

```
checkpoint.py step N M start
... implement (code per docs/coding-standards.md, canonical paths) ...
checkpoint.py step N M done --artifact <path>
```

Checkpoint after EVERY step — never batch. Crash recovery depends on it,
and it never touches the plan doc, so the plan stays prompt-cached.
Record notable mid-slice decisions immediately:
`checkpoint.py note N "chose X because Y"`.

Do not add steps not in the slice. Do not refactor beyond what the slice
requires. Notebook exploration must have its reusable functions extracted
to src/ before the slice completes.

## Gate evaluation

Run the exact command from the slice's "Cómo se computa" field. Technical
errors (missing dep, wrong path) are not gate failures — fix the command,
re-run, report the fix. Then:

```
checkpoint.py gate N --value <number>
```

The script computes pass/fail, persists it, and journals the evidence.
Never modify the threshold after seeing the result (that is a /hfd-slices
revision), and never skip the gate even if the code "looks correct."

## After the gate

- **Pass**: append a dated entry to docs/model-card.md "Actualizaciones"
  (planned → real metrics/architecture, new limitations — append-only, at
  the END of the file). Report and stop — one slice per invocation.
- **Fail — cancelar**: mark the linked CC as "Disparado" (date + value) in
  the constitution's CC table. Report: metric obtained, threshold,
  recommendation to stop. Await human decision. Do NOT continue.
- **Fail — pivotar**: report the declared pivot slice; do NOT auto-execute it.
- **Fail — iterar**: `checkpoint.py iterate N`; if iterations < max,
  propose the slice's declared adjustment, wait for confirmation,
  re-execute. If exhausted: report best value vs threshold and the three
  options (accept / redesign via /hfd-slices / cancel). Await decision.

## Report (end of every run)

Estado + valor obtenido, gate, steps completed, artifacts produced with
paths, tests run, next action. A short paragraph — the durable record
already lives in docs/state/.

## Context contract

Load: status output + ONE slice section + referenced decisions +
coding-standards + constitution (glossary, CCs). Do NOT load:
blind-research, hypothesis-doc, other slices, completed-slice journal
history, or docs/prd-slices.md in full. Never rewrite docs/prd-slices.md.

This contract is machine-readable in `.hfd/context.json`:
`context.py pack hfd-run` prints it, estimates its cost, and
flags anything over budget.
