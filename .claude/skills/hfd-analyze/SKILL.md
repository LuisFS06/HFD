---
name: hfd-analyze
description: >
  Answer ONE data question reproducibly: sharpen it into a computable
  form, agree the metric definition, compute it in a script (not a
  throwaway query), run validity checks, publish a dated report and log
  it in the work ledger. Use for analysis requests — "how many", "which
  segment", "did X move", "why did Y drop", recurring reports — instead
  of ad-hoc exploration that nobody can reproduce next month.
argument-hint: "<question in one line> | refresh <W-id> | contract <metric>"
copilot-model: GPT-5.4 mini
---

The analysis track's workhorse. A question is closed when someone else can
re-run the number and get the same answer — that is this track's gate, and
it replaces the modeling track's metric threshold.

## Session start

```
python .hfd/scripts/context.py pack hfd-analyze
```

Load what it lists, in the order it lists. Nothing else: the modeling plan
is not needed to answer a question about data.

## Modes

- **Question** (default): one question, end to end, below.
- **Refresh** (`refresh W012`): re-run a past analysis on current data.
  Read that unit (`worklog.py show --id W012`), run its stored verification
  command unchanged, and report the new number **and the delta**. Change the
  method only if the data changed shape — and if you do, say so explicitly:
  a silent method change makes the comparison a lie.
- **Contract** (`contract <metric>`): only agree a definition, write no
  analysis. Append a `## Contrato` block at the END of
  `docs/data-contracts.md`.

## 1. Sharpen the question (before any code)

Restate it with all five parts filled in, and confirm in ONE message:

| Part | Example |
|------|---------|
| Metric | churn rate = clientes sin transacción en 90 días / clientes activos |
| Population | clientes B2B con ≥1 transacción en el periodo |
| Window | 2026-07-01 a 2026-09-30 |
| Grain | uno por cliente-mes |
| Comparison | vs. mismo trimestre 2025 |

Propose your recommended answer for every blank instead of asking an open
question. A question that cannot be written this way is not an analysis
request — it is a modeling hypothesis (`/hfd-grill`) or a pipeline change
(`/hfd-feature`).

## 2. Honour the data contract

Check `docs/data-contracts.md` for the metric. If it is defined there, use
that definition **verbatim**, even if you would define it differently — the
place to argue is a new contract entry, not this analysis. If it is absent
and the metric will recur, append a dated `## Contrato — {metric}` section
at the END of the file (definition, source tables, filters, known
exclusions, owner). Create the file from
`.hfd/templates/data-contracts-template.md` the first time.

If the metric name exists in the constitution glossary with a different
definition, stop and surface the conflict: that is `/hfd-constitution`
work, not something to resolve inside an analysis.

## 3. Open the work unit

```
python .hfd/scripts/worklog.py add --kind analysis \
  --title "..." --intent "<the question, one line>" \
  --verification "python src/analysis/<slug>.py --check"
```

Declare the verification command up front, before writing the analysis.
Writing it afterwards means writing whatever the code happens to do.

## 4. Profile before querying

```
python .hfd/scripts/profile_data.py <path> [--sample 200000]
```

Never assume coverage, grain or null behaviour. If the profile contradicts
the question's premise (the window has no data, the join key is not unique),
report that as the answer and stop — a wrong premise is a finding.

## 5. Compute it in a script

`src/analysis/<slug>.py`, per `docs/coding-standards.md`. Requirements:

- Runs end to end from raw/processed data with no manual steps.
- Prints the headline number **with n and the date range** — a number
  without its denominator is not an answer.
- Filters and exclusions are named constants at the top, never inline
  magic values.
- `--check` mode re-computes and exits non-zero if the number moved beyond
  a declared tolerance. That is what makes the unit re-verifiable.
- SQL lives in `sql/`, read by the script — not embedded as long strings.

Notebooks are allowed for looking at distributions and drafting charts.
Nothing that produces the reported number may stay in a notebook.

## 6. Validity checks (run them, then report which ran)

Cheap checks that catch most wrong analyses:

1. **Sample size** at the reporting grain — flag any cell below n=30.
2. **Coverage**: rows per period across the window; a period at 10% of the
   others is a pipeline gap, not a business collapse.
3. **Grain integrity**: duplicates at the declared key.
4. **Null sensitivity**: recompute excluding rows with nulls in the driving
   columns; if the number moves materially, say so.
5. **Outlier sensitivity**: recompute with the top 1% trimmed.
6. **Segment shift**: check whether a mix change explains an aggregate move
   before attributing it to behaviour (Simpson's paradox is the single most
   common wrong answer in this track).

## 7. Publish the report

`reports/{YYYY-MM-DD}-{slug}.md` from
`.hfd/templates/analysis-template.md`: the answer in one sentence, the
number with n and window, method, validity checks run and their outcome,
caveats, and the exact reproduction command. Charts are optional; the
number and its denominator are not.

## 8. Close the unit

```
python .hfd/scripts/worklog.py close <ID> --verified pass \
  --finding "SMB concentra 63% del churn (n=12,481, 2026-07..09)" \
  --artifacts reports/2026-09-02-churn-por-segmento.md \
  --files src/analysis/churn_por_segmento.py
```

`--verified fail` is a legitimate outcome: the question could not be
answered with available data. Log it — the next person deserves to know
the road is closed.

## Report to the user

One sentence with the number, then: the strongest caveat, what would change
the answer, and the reproduction command. Do not editorialize beyond what
the computed values support; "the data suggests" without a number is noise.

## Escalation

- Question needs a predictive model → `/hfd-grill`.
- Metric definition conflicts with the glossary → `/hfd-constitution`.
- The answer requires a pipeline change → `/hfd-feature` first, then this.
- Same question asked for the third time → propose making it a scheduled
  script plus a contract entry, not a fourth ad-hoc analysis.

## Context contract

Load: coding-standards, data-contracts, the constitution glossary section,
recent work units, and the data you profile. Do NOT load hypothesis-doc,
blind-research, design-decisions, prd-slices, model-card or the experiment
ledger — an analysis that needs the modeling plan is a slice, not an
analysis.
