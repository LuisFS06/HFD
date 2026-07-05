# PRD Slices — {NOMBRE_PROYECTO}

> Producido por `/hfd-slices` el {fecha}. **Documento inmutable**: el plan
> no se reescribe. Slices nuevos se agregan AL FINAL con `/hfd-slices add`.
> El estado vivo (checkpoints, gates, iteraciones) vive en
> `docs/state/slices.json` — consultar con `hfd_status.py`, nunca aquí.

---

## Resumen ejecutivo

<!--
Escrito una sola vez por /hfd-slices. Describe el PLAN, no el estado.
El estado vivo se consulta con: python .hfd/scripts/hfd_status.py
-->

- **Total de slices**: {N} planificados
- **Criterios de cancelación cubiertos**: {N} de {total}
- **Assumptions por validar**: {N} slices de validación
- **Estimación de esfuerzo**: {rango de horas total}
- **Mayor riesgo**: Slice {N} — si falla con acción "cancelar", {consecuencia}

---

## Criterios de ordenamiento aplicados

1. **Risk-first**: slices que testan criterios de cancelación van primero.
   → Slices afectados: {lista}
2. **Data-before-model**: validación de supuestos de datos antes de entrenar.
   → Slices afectados: {lista}
3. **Dependency chains**: Slice {A} → Slice {B} → Slice {C}
4. **Assumptions first**: decisiones `[ASSUMPTION]` generan slices de
   validación antes de slices dependientes.
   → Slices afectados: {lista}

---

## Slice 1: {Título descriptivo}

### Hipótesis a validar

{Una oración. Referencia: docs/hypothesis-doc.md H{N}.}

### Dependencias

| Tipo | Referencia | Estado requerido |
|------|-----------|-----------------|
| Artefacto de slice | {Slice N o "ninguno"} | pass |
| Datos de | {fuente de docs/constitution.md} | disponible |
| Decisión de | {design-decisions.md decisión N} | firmada |

### Implementación mínima

<!-- Solo lo necesario para llegar al gate. Cada paso declara su artefacto. -->

| # | Paso | Artefacto producido | Ruta canónica |
|---|------|--------------------|----------------|
| 1 | {paso} | {artefacto} | src/{módulo}/{archivo}.py |
| 2 | {paso} | {artefacto} | data/processed/{archivo} |

### Gate cuantitativo

| Campo | Valor |
|-------|-------|
| **Métrica** | {nombre exacto — debe estar en glosario de docs/constitution.md} |
| **Dataset de evaluación** | {nombre, con split, de docs/design-decisions.md} |
| **Threshold** | {operador} {valor numérico} |
| **Baseline de comparación** | {de docs/blind-research.md §3, o "sin baseline"} |
| **Cómo se computa** | {comando exacto: `python main.py --evaluate --slice 1`} |

### Acción si falla

<!-- Exactamente UNA opción. -->

- [ ] **Cancelar** — vinculado a criterio de cancelación CC-{NNNN}.
- [ ] **Pivotar** — ejecutar Slice {X} ({enfoque alternativo}).
- [ ] **Iterar** — repetir con {ajuste específico}. Máximo {N} iteraciones.

### Artefactos producidos

| Artefacto | Ruta | Consumido por |
|-----------|------|--------------|
| {nombre} | {ruta canónica} | Slice {N} / docs/model-card.md / ninguno |

<!--
NOTA: no hay secciones "Estado", "Estado de implementación", "Notas de
ejecución" ni "Registro de ejecución" en este documento. Todo eso vive en:
  - docs/state/slices.json   (checkpoint.py)
  - docs/state/journal.md    (checkpoint.py note)
Mantener este documento estable es lo que permite cachearlo entre sesiones.
-->

---

## Slice 2: {Título descriptivo}

{Misma estructura que Slice 1}

---

## Trazabilidad

### Hipótesis → Slices

| Hipótesis | Slices que la validan | Gate más exigente |
|-----------|----------------------|------------------|
| H1 | Slice {N}, Slice {M} | {métrica} {operador} {threshold} |

### Criterios de cancelación → Slices

| CC-ID | Slice más temprano que lo evalúa |
|-------|--------------------------------|
| CC-{NNNN} | Slice {N} |

### Assumptions → Slices de validación

| Assumption de docs/design-decisions.md | Slice que lo valida |
|----------------------------------------|---------------------|
| {descripción} | Slice {N} |

---

<!--
Slices agregados después del plan inicial (/hfd-slices add) van debajo de
esta línea, numerados consecutivamente, con la fecha de alta en el título.
-->
