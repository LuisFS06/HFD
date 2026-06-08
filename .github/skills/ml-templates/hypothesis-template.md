# Hypothesis Document — {NOMBRE_PROYECTO}

> Producido por `/grillme` el {fecha}.
> Contiene hipótesis verificables con gates cuantitativos, no user stories.
> Leído por `/designaligner` y `/slicearchitect` como entrada.

---

## Resumen ejecutivo

<!--
Actualizado por /grillme al crear. Resumen rápido del documento.
-->

- **Hipótesis principal**: {hipótesis en una oración}
- **Gate principal**: {métrica} {operador} {threshold}
- **Baseline actual**: {valor o "sin baseline"}
- **Mayor riesgo**: {una oración}
- **Hipótesis total**: {N} ({N} independientes, {N} con dependencias)
- **Criterios de cancelación vinculados**: {N}

---

## Contexto del problema

<!--
Qué situación de negocio motiva este proyecto. No la solución técnica —
el problema. Un párrafo que cualquier stakeholder sin background técnico
puede leer y entender por qué esto importa.
-->

{CONTEXTO_PROBLEMA}

---

## Hipótesis verificables

<!--
Cada hipótesis sigue el formato:
"Creemos que [X] predice [Y] mejor que [Z], lo que habilita [decisión de negocio]."

Reglas:
- [X] es la señal o conjunto de features.
- [Y] es el outcome que se quiere predecir.
- [Z] es el baseline actual (puede ser un modelo, una heurística, o
  "no existe predicción hoy"). If Z es "sin baseline," verify: is
  there truly no current process, heuristic, or rule-of-thumb? Even
  a business rule counts as a baseline. "Better than nothing" is valid
  but a weaker claim.
- [decisión de negocio] es lo que cambia operativamente si la hipótesis
  es correcta.
- Cada hipótesis tiene exactamente un gate cuantitativo.
- Si hay múltiples hipótesis, son independientes o tienen dependencias
  explícitas (H2 solo tiene sentido si H1 pasa — "pasa" means all
  slices validating H1 have status `pass` in docs/prd-slices.md).
-->

### H1: {Título corto}

**Hipótesis**: Creemos que {X} predice {Y} mejor que {Z}, lo que
habilita {decisión de negocio}.

**Gate cuantitativo**:

| Métrica | Threshold | Operador | Dataset de evaluación | Baseline actual |
|---------|-----------|----------|----------------------|-----------------|
| {métrica} | {valor} | >= / <= / == | {dataset} | {baseline o "sin baseline"} |

**Supuestos clave**:
<!--
Condiciones que deben ser ciertas para que esta hipótesis sea testeable.
Each assumption will be validated by a slice or by blind research.
During grillme, mark as "validado por: TBD — asignado por slicearchitect".
Slicearchitect updates this field when slices are created.
-->
- {supuesto_1} — validado por: {TBD — asignado por slicearchitect}
- {supuesto_2} — validado por: {TBD — asignado por slicearchitect}

**Dependencias entre hipótesis**:
- Requiere: {H_N pase / ninguna}
- Habilita: {H_N / ninguna}

---

### H2: {Título corto}

{Misma estructura que H1}

---

## Gates de nivel de negocio

<!--
Además de los gates por hipótesis (nivel de modelo), el proyecto tiene
gates a nivel de negocio medidos con métricas operativas. Estos vienen
de docs/constitution.md criterios de éxito nivel de negocio.

Gates measured post-deploy are outside this preset's validation scope.
Mark them explicitly so downstream commands don't try to evaluate them.
-->

| Gate | Métrica de negocio | Threshold | Cómo se mide | Cuándo se mide |
|------|--------------------|-----------|-------------|---------------|
| {gate} | {métrica} | {threshold} | {método} | {en qué slice o "post-deploy — fuera del scope de validación"} |

---

## Criterios de cancelación vinculados

<!--
Referencia cruzada con docs/constitution.md. No duplicar el contenido —
solo listar los IDs y su relación con las hipótesis.
-->

| ID | Título | Vinculado a hipótesis | Testeable en slice |
|----|--------|----------------------|-------------------|
| CC-{NNNN} | {título} | H{N} | Slice {N} |

---

## Qué NO estamos prediciendo

<!--
Derivado de "Fuera de scope" en docs/constitution.md, pero específico a
las hipótesis. Qué outcomes o señales fueron considerados y descartados
durante la sesión de grilling, con la razón.
-->

| Outcome descartado | Razón | Decidido durante |
|-------------------|-------|-----------------|
| {outcome} | {razón} | Grilling sesión {fecha} |
