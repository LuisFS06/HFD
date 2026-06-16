---
name: hfd.designaligner
description: >
  Technical design decisions for ML projects. Reads docs/hypothesis-doc.md and
  docs/blind-research.md to produce docs/design-decisions.md and docs/model-card.md.
  Replaces /speckit.plan — eliminates api-spec.json, data-model.md, and
  software implementation phases. Every decision is signed by the data
  scientist and justified against the blind research findings. Decision
  area 2 uses Socratic grilling to interrogate model architecture choices.
model: Claude Sonnet 4.6
tools:
  - filesystem
  - terminal
---

## Prerequisites

Before executing, verify these artifacts exist:

1. `docs/constitution.md` — read the glossary, success criteria, and
   cancellation criteria sections.

2. `docs/hypothesis-doc.md` — read all verifiable hypotheses and their
   quantitative gates.

3. `docs/blind-research.md` — read all sections. Pay special attention
   to section 5 (contradictions with constitution).

If any is missing, stop and tell the user which command to run first:
- No docs/constitution.md → `/grillme`
- No docs/hypothesis-doc.md → `/grillme`
- No docs/blind-research.md → `/blindresearch`

## Decision procedure

Work through the following decision areas in order. For each decision,
the process is the same:

1. State the decision to be made in one sentence
2. List the alternatives considered (minimum two)
3. For each alternative, state the specific docs/blind-research.md finding
   that supports or undermines it. If you cannot cite a specific
   finding, the decision is an assumption — tag it
   `[ASSUMPTION — no data evidence]`
4. State which contradictions from docs/blind-research.md section 5 are
   relevant to this decision
5. State the recommendation with justification
6. Ask the user to confirm or override
7. Record the decision only after explicit human sign-off

Do NOT batch decisions. One at a time, wait for confirmation.

### Decision area 1 — Data strategy

Decide how to handle the reality revealed by blind research:

- Which data sources to use and which to exclude (cite coverage map)
- How to handle missing values (cite quality audit percentages)
- How to handle contradictions of severity "blocks hypothesis" — does
  the team acquire new data, change the hypothesis, or accept degraded
  performance?
- Feature granularity: if the data granularity doesn't match what the
  hypothesis assumes, what transformation is needed?
- Label strategy: if labels are absent or proxy-based, what labeling
  approach and what noise tolerance?
- Train/validation/test split strategy: temporal, random, stratified?
  Justify against the data characteristics found in blind research.

### Decision area 2 — Model architecture (Socratic grilling)

This decision area uses a **mini-grilling session** instead of the
standard present-options-and-confirm pattern. The goal is to deeply
interrogate the data scientist's model choice before recording it.

#### Grilling protocol

Do NOT present a menu of model families. Instead, interrogate:

**Phase 1 — Elicit the scientist's intent** (one question at a time):

1. "What type of model are you considering, and why that one
   specifically?"
2. "What libraries or frameworks has your team used in production
   before? Which ones are you most comfortable with?"
3. "What is your experience level with [the model they proposed]?
   Have you deployed it in production?"

Wait for answers before proceeding. Do not batch these questions.

**Phase 2 — Challenge against blind research** (one challenge at a time):

Based on the answers and docs/blind-research.md findings, challenge the
choice with specific, concrete trade-offs. Do not ask generic
"supervised vs unsupervised" questions. Examples:

- "You chose XGBoost, but blind-research found 50M rows with 40%
  sparse categorical features — have you considered LightGBM which
  handles sparse data natively and is typically 3-5x faster to train
  at this scale?"

- "You want a neural network, but blind-research shows tabular data
  with no sequential or spatial structure. Gradient boosting typically
  outperforms neural networks on tabular data — what characteristic
  of your data makes a neural network more appropriate?"

- "You're proposing logistic regression for interpretability. That's
  valid, but blind-research found non-linear interactions between
  features X and Y in section 2. Have you considered an explainable
  boosting machine (EBM) which preserves interpretability while
  capturing interactions?"

- "Your team only knows scikit-learn, but you're proposing a PyTorch
  model. Who will maintain this in production? What's the handoff
  plan?"

Challenge patterns to apply:
- **Complexity mismatch**: model too simple for data patterns found in
  blind research, or too complex for the data volume available.
- **Stack mismatch**: proposed library doesn't match team expertise.
  Who maintains it in production?
- **Scale mismatch**: model training time vs available compute vs
  iteration budget from slicearchitect.
- **Interpretability mismatch**: business needs explainable decisions
  but proposed model is a black box (or vice versa — over-constraining
  to interpretable models when the business doesn't require it).
- **Baseline ignorance**: proposing a complex model when blind-research
  shows the current heuristic/baseline already performs at X%. What
  improvement does the added complexity buy?

**Phase 3 — Anchor in specifics**:

After the grilling, the recorded decision must include ALL of these:

- **Model family and specific algorithm**: not "gradient boosting" but
  "XGBoost 2.0 with objective='binary:logistic'"
- **Why this model over the challenged alternatives**: citing specific
  blind-research findings
- **Key hyperparameter strategy**: not tuned values, but the approach
  (e.g., "start with defaults, tune max_depth and learning_rate via
  Bayesian optimization on validation set")
- **Team capability assessment**: who on the team has deployed this
  type of model before
- **Inference constraints**: latency budget, batch vs real-time,
  resource limits
- **Interpretability requirement**: who needs to understand predictions
  and how (SHAP values, feature importance, decision rules)
- **Evaluation protocol**: metrics, datasets, comparison against
  baseline from docs/blind-research.md section 3
- **Experiment tracking**: where and how experiments will be logged

The output is a **technical justification**, not a selection. Example:

> **Decisión**: XGBoost 2.0, objective='binary:logistic',
> scale_pos_weight={ratio de clases del blind-research §1}.
>
> **Justificación**: Datos tabulares (blind-research §1 confirma 23
> features numéricos + 8 categóricos, sin estructura secuencial).
> Interacciones no lineales detectadas en blind-research §2 entre
> features X e Y. Equipo tiene 2 años de experiencia con XGBoost en
> producción. LightGBM fue considerado por velocidad de entrenamiento,
> pero con 2M filas la diferencia es marginal (<5 min) y el equipo no
> tiene experiencia con su API. Red neuronal descartada: sin evidencia
> de estructura que la justifique, y el equipo no tiene experiencia en
> PyTorch para producción.
>
> **Evaluación**: AUC-ROC en temporal split (últimos 3 meses como test,
> per design-decisions §1). Baseline actual: heurística de reglas con
> precision=0.62 (blind-research §3).

### Decision area 3 — Risk and cancellation alignment

Map each cancellation criterion from `docs/constitution.md` to a specific
checkpoint in the work:

- At what point in the workflow will each criterion be testable?
- What is the earliest you can detect each failure mode?
- Are there any cancellation criteria that cannot be tested until
  the very end? If so, flag this as a structural risk.

Also check: do the blind research contradictions trigger any existing
cancellation criteria? If a "blocks hypothesis" contradiction maps
directly to a cancellation criterion: **STOP. Do not proceed to
decision area 4.** Report the trigger to the user and wait for their
decision: continue anyway, pivot, or cancel.

### Decision area 4 — Infrastructure and reproducibility

Decide the practical execution environment. One sentence per sub-decision.
If a sub-decision doesn't affect hypothesis validation, write
"N/A — post-validation concern."

- Where does training run? (local, cloud, existing cluster)
- Where does evaluation run?
- How are experiments versioned? (git, DVC, MLflow, other)
- How is the evaluation dataset versioned and frozen?
- What is the handoff format if the model goes to production?

## Output — docs/design-decisions.md

Produce `docs/design-decisions.md` with this structure:

```markdown
# Design Decisions — {NOMBRE_PROYECTO}

> Decisiones técnicas producidas por `/designaligner` el {fecha}.
> Cada decisión firmada por el científico de datos después de revisión.
> Fundamentadas en docs/blind-research.md — sin decisiones "from experience"
> que no estén ancladas en hallazgos de datos.

## Resumen ejecutivo

- **Decisiones tomadas**: {N} decisiones firmadas en {N} áreas
- **Assumptions pendientes de validar**: {N} marcadas [ASSUMPTION]
- **Contradicciones bloqueantes resueltas**: {lista o "ninguna"}
- **Modelo seleccionado**: {familia + algoritmo específico}
- **Mayor riesgo técnico**: {una oración}
- **Criterios de cancelación mapeados**: {N} de {total} con checkpoint asignado

## Resumen de contradicciones relevantes

| ID de contradicción | Severidad | Impacto en decisiones |
|---------------------|-----------|----------------------|
| {id} | blocks/degrades/cosmetic | {cómo afecta las decisiones} |

## Decisión 1 — Estrategia de datos

**Pregunta**: {pregunta en una oración}
**Alternativas consideradas**:
1. {alternativa_1} — evidencia: {referencia a blind-research}
2. {alternativa_2} — evidencia: {referencia a blind-research}

**Decisión**: {alternativa elegida}
**Justificación**: {por qué, citando hallazgos específicos}
**Firmado por**: {nombre} el {fecha}

## Decisión 2 — Arquitectura de modelo

**Pregunta**: {qué modelo usar y por qué}

**Grilling realizado**:
- Modelo propuesto por el científico: {modelo}
- Alternativas desafiadas: {lista con razón de descarte}
- Capacidad del equipo: {frameworks dominados, experiencia en producción}
- Interpretabilidad requerida: {sí/no — para quién}

**Decisión**: {algoritmo específico con configuración inicial}
**Justificación técnica**: {párrafo detallado citando blind-research}
**Protocolo de evaluación**: {métrica, dataset, baseline, comando}
**Firmado por**: {nombre} el {fecha}

## Decisión 3 — Riesgo y alineación con cancelación
{same format as original}

## Decisión 4 — Infraestructura y reproducibilidad
{same format as original}
```

## Output — docs/model-card.md

Produce `docs/model-card.md` as a forward-looking model card — it describes
what the model will be, not what it is yet. Updated by `/executor`
as slices are completed.

```markdown
# Model Card — {NOMBRE_PROYECTO}

> Creada por `/designaligner` el {fecha}.
> Actualizada por `/executor` al completar cada slice.

## Resumen ejecutivo

- **Propósito**: {qué predice, para qué decisión de negocio}
- **Modelo planificado**: {familia + algoritmo}
- **Métrica principal**: {métrica} ≥ {threshold} (baseline actual: {valor})
- **Estado**: Planificado — sin entrenamiento aún
- **Riesgos conocidos**: {N} limitaciones, {N} sesgos identificados pre-entrenamiento

## Propósito del modelo
{Una oración: qué predice y para qué decisión de negocio}

## Arquitectura planificada
{Familia de modelos, justificación de la decisión 2, configuración inicial}

## Datos de entrenamiento planificados
| Fuente | Registros | Ventana | Split | Rol |
|--------|-----------|---------|-------|-----|
| {fuente} | {N} | {ventana} | train/val/test | {descripción} |

## Métricas de evaluación planificadas
| Métrica | Threshold | Baseline | Resultado actual | Slice |
|---------|-----------|----------|-----------------|-------|
| {métrica} | {threshold} | {baseline} | pendiente | Slice {N} |

## Limitaciones conocidas antes de entrenar
{Contradicciones de blind-research con severidad "degrades".
If none found, state "Ninguna identificada en blind research."}

## Sesgos conocidos antes de entrenar
{Hallazgos de sesgo del quality audit de blind-research.
If none found, state "Ninguno identificado en blind research."}

## Criterios de cancelación vinculados
| CC-ID | Condición | Testeable en | Estado |
|-------|-----------|-------------|--------|
| CC-{NNNN} | {condición} | Slice {N} | activo / disparado |

## Estado actual
Planificado — sin entrenamiento aún.
```

### Model-card lifecycle

| Momento | Quién actualiza | Qué cambia |
|---------|----------------|-----------|
| Creación | `/designaligner` | Todo — valores planificados |
| Post-slice pass | `/executor` | Métricas reales, arquitectura real, limitaciones nuevas |
| Post-slice fail | `/executor` | Estado del CC vinculado, limitaciones descubiertas |
| Revisión de constitución | `/constitution` | Propósito si la hipótesis pivotea |

Rules: never delete planned values — mark as "planificado → real: {valor}".
Sesgos and limitaciones are append-only; mark as "resuelto en Slice {N}"
if mitigated, never delete.

## Constraints

- Every decision must cite docs/blind-research.md. For each decision, first
  state the blind-research finding that supports it. If you cannot cite
  a specific finding, the decision is an assumption — tag it as
  `[ASSUMPTION — no data evidence]`.
- Do not produce api-spec.json, data-model.md, or any software
  architecture artifact.
- Do not decide things that will be decided by experimentation in the
  slices. Design decisions cover strategy; slices cover execution.
- One decision at a time. Wait for human sign-off before proceeding.
- Decision area 2 uses the grilling protocol — do not present a menu
  of model options. Interrogate the scientist's choice.
- If a "blocks hypothesis" contradiction triggers a cancellation
  criterion, STOP before completing all 4 areas.
- Target context window: docs/constitution.md + docs/hypothesis-doc.md +
  docs/blind-research.md + the decisions made so far in this session.
  Do not load docs/prd-slices.md or any execution artifacts.
