# HFD state model — why planning docs are immutable

Every HFD session re-reads the same planning docs (constitution, hypothesis,
design decisions, slice plan). LLM prompt caching only pays off when those
inputs are **byte-identical between sessions**. The old design rewrote
`prd-slices.md` after every step — invalidating the cache on the project's
largest document dozens of times per slice, and forcing every resume to
re-ingest the whole file.

The fix is a strict read/write split:

## Immutable after creation (cache-stable, re-read every session)

| File | Created by | May change only via |
|------|-----------|---------------------|
| `docs/constitution.md` | /hfd-grill | /hfd-constitution (rare, deliberate revision) |
| `docs/hypothesis-doc.md` | /hfd-grill | /hfd-grill re-run (creates numbered variant) |
| `docs/blind-research.md` | /hfd-research | dated addendum section appended at END of file |
| `docs/design-decisions.md` | /hfd-design | superseding decision appended at END of file |
| `docs/model-card.md` | /hfd-design | "planificado -> real" updates appended at END |
| `docs/prd-slices.md` | /hfd-slices | new slices appended at END (`/hfd-slices add`) |

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

Agents never hand-edit these — they call the scripts, which write atomically
and validate inputs. Reading them costs a few hundred tokens, not tens of
thousands.

## Context budget per session

Load only what the current skill declares in its "Context contract" section.
Use the extraction scripts instead of whole files:

- `python .hfd/scripts/hfd_status.py` — project state in ~30 lines
- `python .hfd/scripts/get_slice.py N` — one slice, not the whole plan
- `python .hfd/scripts/experiment.py best --metric AUC` — the number to beat
