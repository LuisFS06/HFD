# Model Card — {NOMBRE_PROYECTO}

> Creada por `/hfd-design` el {fecha}. Describe lo que el modelo VA A SER.
> Actualizaciones posteriores (`/hfd-run`, `/hfd-experiment`) se agregan
> como entradas fechadas en "Actualizaciones" AL FINAL del documento —
> el cuerpo original nunca se reescribe (estabilidad para caching).

## Resumen ejecutivo

- **Propósito**: {qué predice, para qué decisión de negocio}
- **Modelo planificado**: {familia + algoritmo}
- **Métrica principal**: {métrica} ≥ {threshold} (baseline actual: {valor})
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

| Métrica | Threshold | Baseline | Slice |
|---------|-----------|----------|-------|
| {métrica} | {threshold} | {baseline} | Slice {N} |

<!-- Resultados reales: ver docs/state/slices.json y docs/state/experiments.jsonl -->

## Limitaciones conocidas antes de entrenar

{Contradicciones de blind-research con severidad "degrades", o "Ninguna
identificada en blind research."}

## Sesgos conocidos antes de entrenar

{Hallazgos de sesgo del quality audit, o "Ninguno identificado en blind research."}

## Criterios de cancelación vinculados

| CC-ID | Condición | Testeable en |
|-------|-----------|-------------|
| CC-{NNNN} | {condición} | Slice {N} |

---

## Actualizaciones

<!--
Append-only. Cada entrada: fecha, comando, qué cambió de planificado a real.
Formato:
### [{fecha}] {comando} — Slice {N} / Experimento {E-NNN}
- {métrica}: planificado {threshold} -> real {valor}
- Arquitectura: planificado {X} -> real {Y}
- Nueva limitación descubierta: {descripción}
Nunca borrar entradas anteriores.
-->
