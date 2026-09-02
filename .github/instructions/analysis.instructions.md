---
description: "Standards for analysis scripts, SQL and notebooks — auto-applied to the analysis track"
applyTo: "src/analysis/**/*.py,sql/**/*.sql,notebooks/**/*.ipynb"
---

## An analysis is a script, not a session

- One question per module in `src/analysis/`, named after the question.
- Runs end to end from `data/` with no manual steps and no hidden state.
- Prints the headline number **with n and the date range**. A number
  without its denominator is not an answer.
- Exposes a `--check` mode that recomputes the number and exits non-zero if
  it moved beyond a declared tolerance. That command goes in the ledger.

## Definitions

- Use the definition in `docs/data-contracts.md` verbatim. If the metric is
  not there and will recur, append a contract before publishing the number.
- Filters, exclusions, windows and tolerances are named constants at the
  top of the module — never inline magic values, never buried in a query.
- If a metric name means something different in `docs/constitution.md`,
  stop and raise it (`/hfd-constitution`); do not silently pick one.

## SQL

- One query per file in `sql/`, read by the analysis script — not embedded
  as a long Python string.
- Header comment: the question it answers, source tables, output grain.
- No `SELECT *` in anything whose output is reported.
- Results are never pasted back into the `.sql` file.

## Validity checks before publishing

Sample size per reported cell, coverage per period, grain integrity
(duplicates at the key), null sensitivity, outlier sensitivity, and mix
shift (Simpson's paradox) — run them, then state in the report which ran
and what they showed.

## Notebooks

Exploration and charts only. Anything that produces a reported number moves
to `src/analysis/` before the work unit closes. Never commit a notebook
whose outputs contain customer-level data.

## Reports

`reports/YYYY-MM-DD-slug.md` from `.hfd/templates/analysis-template.md`.
Immutable: a new number is a new dated report, not an edit to the old one.
