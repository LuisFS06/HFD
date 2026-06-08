# Plan de diseño ML — {NOMBRE_PROYECTO}

> Este preset produce tres artefactos de diseño en lugar del plan monolítico
> del core de Spec-Kit. Cada artefacto tiene su formato definido en el
> agente que lo produce (single source of truth).

## Artefactos de diseño

| Artefacto | Producido por | Formato definido en |
|-----------|--------------|-------------------|
| docs/blind-research.md | `/blindresearch` | hfd.blindresearch.agent.md §Output |
| docs/design-decisions.md | `/designaligner` | hfd.designaligner.agent.md §Output |
| docs/model-card.md | `/designaligner` | hfd.designaligner.agent.md §Output |

## Artefactos del core de Spec-Kit NO producidos en este preset

| Artefacto core | Razón de eliminación |
|---------------|---------------------|
| api-spec.json | ML no produce APIs en fase de validación |
| data-model.md | Estructura de datos documentada en docs/blind-research.md §1 y model-card |
| Implementation phases | Reemplazado por slices verticales en docs/prd-slices.md |
