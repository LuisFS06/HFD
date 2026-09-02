# HFD state model — why planning docs are immutable

Every HFD session re-reads the same inputs (coding standards, constitution,
plan, contracts). Prompt caching only pays off when those inputs are
**byte-identical between sessions**. The old design rewrote
`prd-slices.md` after every step — invalidating the cache on the project's
largest document dozens of times per slice, and forcing every resume to
re-ingest the whole file.

The fix is a strict read/write split, now enforced by
`.hfd/scripts/context.py` rather than by convention. The full mechanic
lives in [context-management.md](context-management.md); this file is the
map of which file belongs to which side.

## Immutable after creation (cache-stable, re-read every session)

| File | Created by | May change only via |
|------|-----------|---------------------|
| `docs/coding-standards.md` | preset | never (frozen) |
| `docs/constitution.md` | /hfd-grill | /hfd-constitution (rare, deliberate revision) |
| `docs/hypothesis-doc.md` | /hfd-grill | dated `## Enmienda` appended at END |
| `docs/blind-research.md` | /hfd-research | dated addendum appended at END |
| `docs/design-decisions.md` | /hfd-design | superseding decision appended at END |
| `docs/model-card.md` | /hfd-design | "planificado -> real" updates appended at END |
| `docs/prd-slices.md` | /hfd-slices | new slices appended at END (`/hfd-slices add`) |
| `docs/data-contracts.md` | /hfd-analyze | new/revised contract appended at END |
| `reports/YYYY-MM-DD-*.md` | /hfd-analyze | never — a new number is a new dated report |

Rule of thumb: **append at the end, never edit the middle or top.** A stable
prefix is a cached prefix. This is also why executive summaries in these
docs describe the *plan*, never live status — live status would force
rewrites at the top of the file.

## Volatile state (small, script-managed, cheap to re-read)

| File | Owner script | Contents |
|------|-------------|----------|
| `docs/state/slices.json` | `checkpoint.py` | slice/step status, gate results, iteration counts |
| `docs/state/journal.md` | `checkpoint.py note` | append-only execution notes with dates |
| `docs/state/experiments.jsonl` | `experiment.py` | append-only experiment ledger, one JSON per line |
| `docs/state/worklog.jsonl` | `worklog.py` | append-only work ledger: analyses, features, fixes |
| `docs/state/context-lock.json` | `context.py` | hashes proving the docs above stayed append-only |

Agents never hand-edit these — they call the scripts, which write atomically
and validate inputs. Reading them costs a few hundred tokens, not tens of
thousands.

## Context budget per session

Load only what the skill's contract declares. `context.py pack <skill>`
prints that contract, in load order, with a cost estimate. Use the
extraction commands instead of whole files:

- `python .hfd/scripts/hfd_status.py` — project state in ~30 lines
- `python .hfd/scripts/get_slice.py N` — one slice, not the whole plan
- `python .hfd/scripts/context.py show "constitution#Glosario"` — one section
- `python .hfd/scripts/experiment.py best --metric AUC` — the number to beat
- `python .hfd/scripts/worklog.py show --open` — what is unfinished

## Proving it holds

```
python .hfd/scripts/context.py freeze    # after a deliberate change
python .hfd/scripts/context.py verify    # exit 1 if a doc was edited mid-file
```

CI runs `verify`. That turns "we append at the end" from a habit the next
contributor may not share into a check that fails the build.
