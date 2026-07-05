---
name: hfd-research
description: >
  Blind factual exploration of available data and models WITHOUT knowing
  the proposed hypothesis — produces docs/blind-research.md (coverage,
  quality, existing models, metrics, contradictions with the constitution).
  Use after /hfd-grill and before /hfd-design, or to refresh findings for
  a single source ("refresh <source>") when data changed mid-project.
argument-hint: "[data locations / access constraints] | refresh <source>"
---

## Blindness constraint (the single most important rule)

Do NOT read docs/hypothesis-doc.md, docs/design-decisions.md, or
docs/prd-slices.md. Blind research maps facts without solution bias. If
hypothesis content appears in context anyway, actively ignore its claims
and do not let it steer which data aspects you prioritize.

## Prerequisites

`docs/constitution.md` must exist — read ONLY these sections: Fuentes de
datos disponibles, Glosario del dominio, Criterios de éxito, Fuera de
scope. If missing, stop and tell the user to run `/hfd-grill`.

## Modes

- **Full** (default): all five areas below, producing docs/blind-research.md.
- **Refresh** (`/hfd-research refresh <source>`): incremental. Re-profile
  ONLY the named source and append a dated section
  `## Addendum {fecha} — {source}` at the END of docs/blind-research.md
  with what changed vs the original findings. Never rewrite existing
  sections — appending keeps the doc cache-stable for downstream skills.

## Exploration procedure

Profile mechanically first, interpret second:

```
python .claude/skills/hfd-shared/scripts/profile_data.py <path> [--target <col>] [--sample N]
```

gives rows, dtypes, null %, duplicates, time ranges, and target
distribution per file. Write custom exploration code only for what the
profiler can't answer (join-key integrity, schema drift, bias checks).

Document only observable facts — numbers, not narratives. No
recommendations, no "this suggests we should". 1-3 sentences per finding.

1. **Data coverage map** — per source in the constitution: existence,
   records, time range, granularity, join keys, missing-value patterns,
   label availability and distribution. Inaccessible source: report the
   access error and move on. Note any source NOT listed in the constitution.
2. **Data quality audit** — duplicates, temporal consistency, referential
   integrity between sources, schema drift, representation biases. Never
   clean or fix data (fixing your own broken exploration query is fine).
3. **Models in production today** — models/ dir, registries (MLflow, W&B),
   serving docs. Per model: what it predicts, features, reported metrics,
   baseline performance, known limitations. If none exist, state that
   explicitly — it means there is no baseline to beat.
4. **Metric landscape** — every metric currently reported in this domain:
   where computed, refresh cadence, consumers, and whether its definition
   matches the glossary. Flag same-name-different-definition cases.
5. **Contradictions with constitution** — record them as discovered, then
   consolidate. Severity: **blocks hypothesis** (untestable until
   resolved) / **degrades hypothesis** (testable but unreliable) /
   **cosmetic**. When in doubt between blocks and degrades, choose blocks.
6. **Discovered sources** — list sources not in the constitution for the
   next /hfd-constitution revision; do not add them yourself.

## Output

docs/blind-research.md, sections 1-6 above, starting with `## Resumen
ejecutivo`: hallazgos críticos (2-3 sentences), contradicciones que
bloquean, datos faltantes, fuentes descubiertas (count), and a
feasibility verdict — "Los datos disponibles {permiten / permiten con
limitaciones / no permiten} testar la hipótesis" — with NO solution
recommendations.

Header note: "> Este documento NO conoce la hipótesis propuesta."

## Context contract

Load: constitution (4 sections above) + profiler output + your own
exploration results. Do NOT load: hypothesis-doc, design-decisions,
prd-slices, docs/state/.
