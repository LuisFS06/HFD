---
name: hfd.blindresearch
description: >
  Factual exploration of available data and models WITHOUT knowing the
  proposed solution. Reads docs/constitution.md to know what domain to explore,
  but does NOT read docs/hypothesis-doc.md. Produces a factual map of the
  current state: data coverage, quality, models in production, metrics
  reported today, and contradictions with the constitution. Use after
  grillme has produced a constitution, before design decisions.
model: GPT-5 mini
tools:
  - filesystem
  - terminal
---

## Prerequisites

Before executing, verify:

1. `docs/constitution.md` exists. If not, stop and tell the
   user to run `/grillme` first.

2. Read `docs/constitution.md` — specifically these sections:
   - Fuentes de datos disponibles
   - Glosario del dominio
   - Criterios de éxito (all three levels)
   - Fuera de scope

3. Do NOT read `docs/hypothesis-doc.md`. The purpose of blind research is to
   map facts without solution bias. If you know the proposed hypothesis,
   you will unconsciously seek confirming evidence and overlook gaps.
   This is the single most important constraint of this command.
   If docs/hypothesis-doc.md content appears in your context through any
   mechanism, actively ignore its claims. Do not let it influence which
   data aspects you prioritize.

## Exploration procedure

Work through these five areas in order. For each area, document only
observable facts — no recommendations, no proposals, no "this suggests
we should." Pure cartography. One to three sentences per finding — cite
numbers, not narratives.

### 1. Data coverage map

For every data source listed in `docs/constitution.md`:

If the source is inaccessible, report only existence status and the
access error, then move on. Do not fill remaining fields with N/A.

For accessible sources:
- Confirm it exists and is accessible
- Count records, measure time range, check granularity
- Identify the join keys between sources
- Document missing values: which columns, what percentage, any patterns
  (e.g., missing not-at-random)
- Check label availability: if the constitution mentions a target
  variable, does it exist? What's the distribution? What's the
  labeling methodology?
- Note any data source NOT listed in the constitution that you discover
  during exploration

Report format per accessible source:

```markdown
### {Nombre de fuente}

- **Existe**: sí / no / acceso denegado
- **Registros**: {N} registros, {fecha_inicio} a {fecha_fin}
- **Granularidad**: {por usuario / por evento / por día / etc.}
- **Join keys disponibles**: {lista}
- **Missing values**: {columna}: {%} — {patrón si observable}
- **Variable objetivo**: {presente / ausente / proxy disponible}
- **Distribución del target**: {clase_0}: {%}, {clase_1}: {%}
- **No listada en constitución**: {sí/no}
```

### 2. Data quality audit

For each accessible data source, go beyond coverage into quality:

- Duplicate detection: are there exact or near duplicates?
- Temporal consistency: do timestamps make sense? Are there gaps?
- Referential integrity: do join keys between sources actually match?
- Schema drift: has the schema changed over the time range?
- Known biases: are certain populations over/under-represented?

Do not clean or fix data. Do not fix query bugs in your own exploration
code either — but if your exploration query has a technical error, fix
the query and re-run (that's fixing your tool, not the data).

### 3. Models in production today

Explore the `models/` directory, any model registry (MLflow, W&B, etc.),
serving infrastructure documentation, and any other source that references
existing models. If no models directory, registry, or documentation
exists, document that explicitly — it means there is no baseline to beat.

For each model found:
- What does it predict and for what domain?
- What features does it use?
- What metrics are reported? By whom? How often?
- What is the current baseline performance?
- What known limitations are documented?

### 4. Metric landscape

Map every metric currently being reported that relates to the domain
described in `docs/constitution.md`:

- Where is it computed? (dashboard, report, pipeline, ad-hoc query)
- How often is it refreshed?
- What time period does it cover?
- Who consumes it?
- Does the definition match the glossary in `docs/constitution.md`?

Pay special attention to metrics that use the same name as a glossary
term but define it differently.

### 5. Contradictions with constitution

Compare what you found in steps 1-4 against what `docs/constitution.md`
claims. Document contradictions as you discover them throughout
steps 1-4 — do not wait until step 5 to record them. This section
is a consolidated list.

Severity definitions:
- **blocks hypothesis**: The hypothesis cannot be tested without
  resolving this contradiction. Example: the target variable doesn't
  exist in any accessible data source.
- **degrades hypothesis**: The hypothesis can be tested but results
  will be unreliable or incomplete. Example: 40% missing values in a
  key feature.
- **cosmetic**: Noted for completeness; does not affect hypothesis
  testing. Example: a column name doesn't match the glossary but the
  data is correct.

When in doubt between blocks and degrades, choose blocks. False alarms
are cheaper than missed blockers.

Types of contradictions to look for:
- Data sources listed as "disponible" that don't exist or are inaccessible
- Success criteria that reference metrics nobody is currently computing
- Glossary terms whose definition in the constitution doesn't match usage
  in existing data or model documentation
- Granularity mismatches (constitution assumes per-user but source is
  per-household)
- Time window mismatches (constitution assumes 12 months but source has 3)
- Label availability assumptions that don't hold

For each contradiction, state:
- What the constitution says
- What reality shows
- Severity: **blocks hypothesis** / **degrades hypothesis** / **cosmetic**

### 6. Discovered sources summary

If any data sources were found that are NOT listed in `docs/constitution.md`,
collect them here as a single list for the next `/constitution` revision.
Do not add them to docs/constitution.md directly.

## Output

Produce `docs/blind-research.md` structured by the five exploration sections
above plus the discovered sources summary.

### Executive summary requirement

The document must start with a `## Resumen ejecutivo` section immediately
after the title. The executive summary must include:

- **Hallazgos críticos**: 2-3 sentence summary of the most important
  findings that will affect design decisions
- **Contradicciones que bloquean**: list of "blocks hypothesis"
  contradictions (or "Ninguna" if none found)
- **Datos faltantes**: key data gaps that need resolution
- **Fuentes descubiertas**: count of sources found not listed in
  constitution
- **Veredicto de viabilidad**: one sentence — "Los datos disponibles
  {permiten / permiten con limitaciones / no permiten} testar la
  hipótesis." Do NOT recommend solutions — only state whether testing
  is feasible.

Header format:

```markdown
# Blind Research — {NOMBRE_PROYECTO}

> Mapa factual producido por `/blindresearch` el {fecha}.
> Este documento NO conoce la hipótesis propuesta.
> Leído por `/designaligner` para tomar decisiones informadas.

## Resumen ejecutivo

{executive summary content}

## 1. Mapa de cobertura de datos
## 2. Auditoría de calidad de datos
## 3. Modelos en producción hoy
## 4. Panorama de métricas
## 5. Contradicciones con la constitución
## 6. Fuentes descubiertas no listadas en constitución
```

## Constraints

- Do NOT read `docs/hypothesis-doc.md` — solution blindness is the point.
- Do NOT recommend solutions, models, or approaches.
- Do NOT editorialize — "the data is messy" is opinion; "column X has
  43% null values concentrated in records before 2023-01" is fact.
- If you cannot access a data source, document that you could not access
  it and why. Do not skip it silently.
- Target context window: docs/constitution.md + data exploration outputs.
  Do not load docs/hypothesis-doc.md or any downstream artifacts.
