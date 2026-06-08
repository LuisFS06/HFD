# PRD Slices — {NOMBRE_PROYECTO}

> Producido por `/slicearchitect` el {fecha}.
> Ejecutado por `/executor` slice por slice.
> Estado actualizado por `/executor` al completar cada gate.

---

## Resumen ejecutivo

<!--
Actualizado por /slicearchitect al crear y por /executor después de cada slice.
Dashboard del proyecto para revisión rápida.
-->

- **Total de slices**: {N} planificados
- **Próximo slice**: Slice {N} — {título}
- **Slices completados**: {N} pass, {N} fail
- **Criterios de cancelación cubiertos**: {N} de {total}
- **Assumptions por validar**: {N}
- **Mayor riesgo**: Slice {N} — si falla, {consecuencia}

### Dashboard

| Slice | Título | Gate | Threshold | Acción si falla | Estado |
|-------|--------|------|-----------|----------------|--------|
| 1 | {título} | {métrica} | {operador} {valor} | cancelar CC-{NNNN} / pivotar a Slice {X} / iterar (máx {N}) | pendiente |
| 2 | {título} | {métrica} | {operador} {valor} | cancelar / pivotar / iterar | pendiente |

---

## Criterios de ordenamiento aplicados

<!--
NOTA: esta sección es para revisión humana y /analyze.
El executor NO carga esta sección — salta directo al slice pendiente.
-->

1. **Risk-first**: slices que testan criterios de cancelación van primero.
   → Slices afectados: {lista}
2. **Data-before-model**: slices que validan supuestos de datos van antes
   de slices que entrenan modelos.
   → Slices afectados: {lista}
3. **Dependency chains**: Slice {A} → Slice {B} → Slice {C}
4. **Assumptions first**: decisiones marcadas `[ASSUMPTION]` generan
   slices de validación antes de slices dependientes.
   → Slices afectados: {lista}

---

## Slice 1: {Título descriptivo}

### Hipótesis a validar

{Qué aspecto específico de la hipótesis principal prueba este slice.
Una oración. Referencia: docs/hypothesis-doc.md H{N}.}

### Dependencias

| Tipo | Referencia | Estado requerido |
|------|-----------|-----------------|
| Artefacto de slice | {Slice N o "ninguno"} | pass |
| Datos de | {fuente de docs/constitution.md} | disponible |
| Decisión de | {design-decisions.md decisión N} | firmada |

### Implementación mínima

<!--
Solo lo necesario para llegar al gate. Nada más.
Cada paso declara el artefacto que produce y dónde vive.
-->

| # | Paso | Artefacto producido | Ruta en estructura canónica |
|---|------|--------------------|-----------------------------|
| 1 | {descripción del paso} | {nombre del artefacto} | src/{módulo}/{archivo}.py |
| 2 | {descripción del paso} | {nombre del artefacto} | data/processed/{archivo} |
| 3 | {descripción del paso} | {nombre del artefacto} | src/models/{archivo}.py |

### Estado de implementación

<!--
Actualizado por /executor paso a paso durante la ejecución.
Permite crash recovery: si la sesión se interrumpe, el próximo executor
lee esta tabla para saber dónde retomar.

Estados posibles:
  ⬜ pendiente — no iniciado
  ⏳ en progreso — iniciado, no completado
  ✅ completo — artefacto producido y verificado
-->

| # | Paso | Estado | Artefacto | Verificado |
|---|------|--------|-----------|------------|
| 1 | {descripción del paso} | ⬜ pendiente | — | — |
| 2 | {descripción del paso} | ⬜ pendiente | — | — |
| 3 | {descripción del paso} | ⬜ pendiente | — | — |

### Gate cuantitativo

| Campo | Valor |
|-------|-------|
| **Métrica** | {nombre exacto — debe estar en glosario de docs/constitution.md} |
| **Dataset de evaluación** | {nombre, con split, de docs/design-decisions.md} |
| **Threshold** | {operador} {valor numérico} |
| **Baseline de comparación** | {de docs/blind-research.md §3, o "sin baseline"} |
| **Cómo se computa** | {comando exacto: `python main.py --evaluate --slice 1`} |

### Acción si falla

<!--
Marcar exactamente UNA opción.
-->

- [ ] **Cancelar** — vinculado a criterio de cancelación CC-{NNNN}.
      Si falla, el criterio se dispara.

- [ ] **Pivotar** — si falla, ejecutar Slice {X} que prueba
      {descripción breve del enfoque alternativo}.

- [ ] **Iterar** — si falla, repetir con {ajuste específico}.
      Máximo {N} iteraciones. Si se agotan, escalar a decisión humana.

### Artefactos producidos

| Artefacto | Ruta | Consumido por |
|-----------|------|--------------|
| {nombre} | {ruta en estructura canónica} | Slice {N} / docs/model-card.md / ninguno |

### Notas de ejecución

<!--
Append-only. El executor registra aquí decisiones menores tomadas durante
la implementación. Esto sobrevive entre sesiones y permite que al retomar,
el científico vea qué se decidió sin repetir análisis.

Formato:
  [fecha] [sesión N] nota

Nunca borrar notas anteriores. Si una nota es invalidada por una decisión
posterior, marcarla como "[SUPERSEDED by nota de {fecha}]".
-->

{Vacío hasta la primera ejecución}

### Estado

`pendiente`

<!--
Actualizado por /executor a uno de:
- en progreso
- pass ({valor obtenido}) — e.g., pass (AUC = 0.83)
- fail ({valor obtenido}) — e.g., fail (AUC = 0.64)
- fail → pivotar a Slice {X}
- fail → iterar (intento M de N)
- fail → cancelar CC-{NNNN} — pending decisión humana
-->

---

## Slice 2: {Título descriptivo}

{Misma estructura que Slice 1, incluyendo Estado de implementación y Notas de ejecución}

---

## Registro de ejecución

<!--
Append-only. El executor agrega una fila después de cada slice.
Nunca se borran filas — el registro es el historial del proyecto.
-->

| Slice | Fecha | Métrica obtenida | Threshold | Resultado | Acción tomada | Decisión humana |
|-------|-------|-----------------|-----------|-----------|--------------|----------------|
| 1 | {fecha} | {valor} | {threshold} | pass/fail | — / pivotar / iterar / cancelar | {aprobado/rechazado/pendiente} |

### Archival rule

When the execution log exceeds 10 rows, the executor archives all rows
for slices with status `pass` or `cancelar` to `docs/execution-history.md`.
Only rows for `pendiente`, `en progreso`, `fail → iterar`, and the most
recent 3 completed slices remain in this file.

---

## Trazabilidad

<!--
NOTA: estas matrices son para /slicearchitect y /analyze.
El executor NO carga esta sección — la salta al leer docs/prd-slices.md.
Permite verificar que ninguna hipótesis queda sin slice y ningún
criterio de cancelación queda sin checkpoint.
-->

### Hipótesis → Slices

| Hipótesis | Slices que la validan | Gate más exigente |
|-----------|----------------------|------------------|
| H1 | Slice {N}, Slice {M} | {métrica} {operador} {threshold} |
| H2 | Slice {N} | {métrica} {operador} {threshold} |

### Criterios de cancelación → Slices

| CC-ID | Slice más temprano que lo evalúa | Estado actual |
|-------|--------------------------------|--------------|
| CC-{NNNN} | Slice {N} | activo / disparado {fecha} |

### Assumptions → Slices de validación

| Assumption de docs/design-decisions.md | Slice que lo valida | Estado |
|----------------------------------|--------------------|---------| 
| {descripción del assumption} | Slice {N} | pendiente / validado / invalidado |
