---
name: hfd-feature
description: >
  Incremental development loop for one unit of work that has no metric
  gate: a pipeline feature, a new data source, a bug fix, a refactor, a
  scheduled report. Test-first, verified by a declared command, logged in
  the append-only work ledger. Use for daily "add / change / fix this"
  requests instead of re-running the planning skills or opening a slice.
argument-hint: "<what to build or fix> | resume <W-id>"
copilot-model: GPT-5.4 mini
---

The day-to-day loop for code that is not an experiment. A slice validates a
hypothesis; an experiment moves a metric; a feature makes the pipeline or
the reporting do something new — and its gate is a command that proves it
works, not a number that beats a threshold.

## Session start

```
python .hfd/scripts/context.py pack hfd-feature
```

If `worklog.py show --open` lists an unfinished unit related to this
request, resume it instead of opening a second one.

## 0. Route it before you build it

| The request… | belongs to |
|--------------|-----------|
| moves a modeled metric (feature, hyperparameter, cleaning rule) | `/hfd-experiment` |
| tests a NEW aspect of the hypothesis (new target, source, model family) | `/hfd-slices add` |
| asks a question about data rather than changing behaviour | `/hfd-analyze` |
| changes signed design intent | `/hfd-design revisit <N>` |
| changes what the project believes is true | `/hfd-constitution` |
| anything else that changes code or data flow | **this skill** |

Routing wrongly is the expensive mistake here: a metric change logged as a
feature never reaches the experiment ledger, and the next person re-tries it.

## 1. Frame the unit (one message, then build)

- **Change**: what will be different when this is done, in one sentence.
- **Blast radius**: which existing outputs could move — name the analyses,
  reports or slices that read the code you are about to touch.
- **Verification**: the exact command that will prove it works, written
  BEFORE the implementation. No command → no unit.

```
python .hfd/scripts/worklog.py add --kind feature|fix|refactor|data \
  --title "..." --intent "..." --verification "pytest tests/test_x.py -q"
```

## 2. Test first

Write the failing test before the implementation, in `tests/`:

- **Pure logic** → a unit test on a fixture, not on production data.
- **Pipeline step** → a test on a small committed fixture in
  `tests/fixtures/`, asserting shape, key uniqueness, null rate and dtypes
  — the contract, not the values.
- **Analysis script** → its `--check` mode, asserting the number is stable
  within a declared tolerance.
- **Bug fix** → a regression test that fails on the current code. If you
  cannot make it fail first, you have not found the bug yet.

Run it and watch it fail. A test that never failed proves nothing.

## 3. Implement minimally

Per `docs/coding-standards.md`. Touch the fewest files that make the test
pass. Do not refactor callers, rename unrelated things, or "clean up while
we're here" — YAGNI applies to refactoring scope, and a wide diff hides the
change that matters. Extract anything reusable to `src/utils/`; extract any
notebook logic to `src/` before closing.

Record decisions worth remembering as you make them:

```
python .hfd/scripts/worklog.py update <ID> --notes "usé merge_asof porque los timestamps no alinean"
```

## 4. Verify, then check the blast radius

```
python .hfd/scripts/verify.py --quick      # structure, context, state, docs
<the unit's verification command>          # the actual proof
python .hfd/scripts/worklog.py recheck --all   # do past analyses still reproduce?
```

`recheck` is what makes this loop safe to run daily: it re-runs every stored
verification command, so a change that silently moves last month's reported
number surfaces now instead of in a meeting. Any recheck that flips to
`fail` is part of THIS unit — either fix it or, if the number legitimately
changed, say so and update the affected report with a dated note.

## 5. Close it

```
python .hfd/scripts/worklog.py close <ID> --verified pass \
  --files "src/data/load_data.py,tests/test_load_data.py" \
  --notes "<what changed for downstream consumers>"
```

Blocked instead of done → `worklog.py update <ID> --status blocked --notes "<what unblocks it>"`.
An open unit is a handoff, not a failure; leaving it silent is the failure.

## Report to the user

What changed, the command that proves it, what moved downstream (or that
nothing did), and any follow-up unit you opened. Two short paragraphs at
most — the ledger holds the durable record.

## Constraints

- Never close a unit whose verification command you did not run.
- Never weaken a test to make it pass; never delete a failing test that
  belongs to someone else's unit — report it instead.
- Never edit `docs/state/*` by hand; the scripts own those files.
- Never rewrite a planning doc mid-file to reflect a code change: append a
  dated note at the END, or the cached prefix dies for every session after.

## Context contract

Load: coding-standards, open + recent work units, and the files this unit
touches. Do NOT load constitution, hypothesis-doc, blind-research,
design-decisions, prd-slices or model-card — if the unit genuinely needs
them, it was routed wrong in step 0.
