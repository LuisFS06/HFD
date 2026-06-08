# Constitución del proyecto — {NOMBRE_PROYECTO}

> Documento persistente. Creado por `/grillme` durante la primera sesión
> de grilling. Revisado por `/constitution` cuando cambian las condiciones
> del proyecto. Leído por todos los demás comandos como contexto base.

---

## Resumen ejecutivo

<!--
Actualizado por /grillme al crear y por /constitution en cada revisión.
Resumen rápido para quien no quiera leer el documento completo.
-->

- **Hipótesis central**: {una oración}
- **Criterio de éxito principal**: {métrica de modelo} ≥ {threshold}
- **Criterio de éxito de negocio**: {métrica de negocio} ≥ {threshold}
- **Criterio de éxito de datos**: {métrica de datos} ≥ {threshold}
- **Fuentes de datos**: {N} identificadas ({N} disponibles, {N} requieren acceso)
- **Criterios de cancelación**: {N} definidos
- **Mayor riesgo**: {una oración describiendo el riesgo principal}
- **Última revisión**: {fecha} por {comando}

---

## Hipótesis central

<!--
Una oración que conecta la predicción con la decisión de negocio.
Formato: "Creemos que [señal] predice [resultado] con suficiente
confianza para habilitar [decisión de negocio]."
-->

{HIPOTESIS_CENTRAL}

---

## Criterios de éxito

<!--
Nivel de negocio: métricas operativas (revenue, retention, cost).
Nivel de modelo: métricas de ML (AUC, precision, recall, latency).
Nivel de datos: métricas de calidad de datos que deben cumplirse
ANTES de entrenar (completeness, coverage, freshness).
Boundary rule: if the metric is computed from model output, it's
nivel de modelo. If it's computed from raw data alone, it's nivel
de datos.
-->

### Nivel de negocio

| Criterio | Métrica | Umbral mínimo | Cómo se mide |
|----------|---------|---------------|-------------|
| {criterio_negocio} | {métrica} | {umbral} | {método_medición} |

### Nivel de modelo

| Criterio | Métrica | Umbral mínimo | Baseline actual | Dataset de evaluación |
|----------|---------|---------------|-----------------|----------------------|
| {criterio_modelo} | {métrica} | {umbral} | {baseline} | {dataset} |

### Nivel de datos

| Criterio | Métrica | Umbral mínimo | Estado actual |
|----------|---------|---------------|--------------|
| {criterio_datos} | {métrica} | {umbral} | {estado} |

---

## Fuentes de datos disponibles

| Fuente | Descripción | Granularidad | Ventana temporal | Acceso | Calidad conocida |
|--------|-------------|-------------|-----------------|--------|-----------------|
| {fuente} | {descripción} | {granularidad} | {ventana} | {acceso} | {calidad} |

<!--
Acceso: disponible / requiere permisos / requiere ETL / no existe aún
Calidad conocida: auditada (por blind-research) / no auditada / problemas conocidos (describir)
-->

---

## Criterios de cancelación

<!--
Condiciones explícitas bajo las cuales este proyecto se cancela o pivotea.
Solo documentar cuando se cumplen las 3 condiciones:
  1. Hard to reverse — continuar desperdicia tiempo/compute significativo
  2. Surprising without context — un futuro data scientist no entendería por qué
  3. Real trade-off — había alternativas genuinas y se eligió un umbral por razones específicas

Cada criterio vive SOLO en esta tabla (fuente única de verdad).
Si se necesita documentación extensa, agregar un campo "Contexto" debajo de la tabla.
-->

| ID | Título | Condición cuantitativa | Alternativas consideradas | Acción si se dispara | Estado |
|----|--------|----------------------|--------------------------|---------------------|--------|
| CC-0001 | {título} | {condición} | {alternativas evaluadas} | cancelar / pivotar a {X} / escalar | propuesto |

---

## Fuera de scope

<!--
Qué NO va a hacer este proyecto. Cada ítem es algo que alguien
razonablemente esperaría que estuviera incluido pero que se decidió excluir.
-->

- {cosa_excluida} — {razón}

---

## Glosario del dominio

<!--
Términos canónicos del proyecto. Creados uno a uno durante la sesión de
grilling, no en batch. Si un término aparece aquí, todos los artefactos
del proyecto deben usar esta definición exacta.
No incluir términos de implementación — solo términos que un experto del
dominio y un científico de datos necesitan compartir.
-->

| Término | Definición | Ejemplo concreto |
|---------|-----------|-----------------|
| {término} | {definición} | {ejemplo} |

---

## Historial de revisiones

<!--
Keep only the last 5 revisions here. If more exist, older entries live
in docs/revision-history.md.
-->

| Fecha | Comando | Cambio |
|-------|---------|--------|
| {fecha} | `/grillme` | Creación inicial |
