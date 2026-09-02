# Contratos de datos

> Definiciones acordadas de métricas, segmentos y poblaciones. Un contrato
> existe para que dos análisis de la misma métrica den el mismo número.
>
> **Documento append-only**: cada contrato nuevo o cada revisión se agrega
> AL FINAL con fecha. Nunca se edita un contrato existente en el medio del
> archivo — una definición que cambió silenciosamente invalida todo reporte
> que la citó (y rompe el prefijo cacheado de cada sesión posterior).
>
> Creado por `/hfd-analyze`. Conflictos con el glosario de
> `docs/constitution.md` se resuelven con `/hfd-constitution`, no aquí.

---

## Resumen ejecutivo

- **Contratos vigentes**: {N}
- **Métricas cubiertas**: {lista corta}
- **Dueño de las definiciones**: {rol o persona}

---

## Contrato — {nombre de la métrica} ({fecha})

**Definición**: {una oración, computable. Numerador y denominador
explícitos si es una tasa.}

| Campo | Valor |
|-------|-------|
| Fuentes | {tabla(s), con esquema} |
| Grano | {una fila por ...} |
| Ventana por defecto | {p. ej. últimos 90 días} |
| Filtros incluidos | {condiciones} |
| Exclusiones | {qué queda fuera y por qué} |
| Zona horaria / corte de día | {p. ej. UTC, corte 00:00} |
| Tratamiento de nulos | {excluir / imputar / contar como categoría} |
| Latencia de datos | {p. ej. T+1, se estabiliza a los 3 días} |

**Cómo NO se calcula**: {el error común que este contrato previene}.

**Implementación de referencia**: `{src/analysis/archivo.py}` /
`{sql/archivo.sql}`

**Acordado por**: {nombre} el {fecha}
