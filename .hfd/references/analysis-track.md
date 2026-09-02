# The analysis track

HFD runs two tracks over the same repository, the same scripts and the same
context discipline. They differ in what counts as done.

| | Modeling track | Analysis track |
|---|---|---|
| Unit of work | slice | question |
| Planned by | `/hfd-slices` | nothing — questions arrive |
| Executed by | `/hfd-run` | `/hfd-analyze` |
| Gate | metric vs numeric threshold | the number reproduces, and survives its validity checks |
| Ledger | `experiments.jsonl` (metric deltas) | `worklog.jsonl` (units + verdicts) |
| Output | model + gate result | dated report in `reports/` |
| Iteration | `/hfd-experiment` | `/hfd-analyze refresh <W-id>` |
| Shared | `/hfd-feature`, `/hfd-review`, `/hfd-status`, `/hfd-context` | |

Most real projects use both: the analysis track answers what is happening
while the modeling track tries to predict it, and pipeline work under
`/hfd-feature` feeds both.

## Why analysis needs a harness at all

The failure mode of daily analysis is not a bad model, it is an
irreproducible number: a query run in a notebook three months ago, with
filters nobody wrote down, cited in a deck that is still circulating. The
track answers that with four requirements, all cheap:

1. **A definition** — `docs/data-contracts.md` says what the metric means
   before anyone computes it. Two analyses of the same metric must return
   the same number or explicitly disagree with the contract.
2. **A script** — `src/analysis/<slug>.py` runs end to end and prints the
   number with n and window. Notebooks explore; scripts answer.
3. **A verification command** — stored in the ledger, re-runnable by
   `worklog.py recheck`. A number nobody can recompute is a rumor.
4. **Validity checks** — sample size, coverage, grain, nulls, outliers, mix
   shift. Six checks catch most wrong answers, and they cost seconds.

## Routing

| Request | Skill |
|---------|-------|
| "how many / which segment / did X move / why did Y drop" | `/hfd-analyze` |
| "same report but for October" | `/hfd-analyze refresh <W-id>` |
| "we need this number every Monday" | `/hfd-feature` (schedule the script) + a contract |
| "add this column to the pipeline" | `/hfd-feature` |
| "can we predict it" | `/hfd-grill` (modeling track starts) |
| "this metric means something different to Finance" | `/hfd-constitution` |

## Regression safety

`worklog.py recheck --all` re-runs every stored verification command. Run it
after any `/hfd-feature` unit that touches shared data code: it is how a
change to a loader that silently moves last quarter's reported churn number
surfaces the same day instead of in a meeting.
