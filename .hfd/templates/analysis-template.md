# {Pregunta en una línea} — {fecha}

> Producido por `/hfd-analyze`. Unidad de trabajo: {W-id}.
> **Documento inmutable**: si el número cambia, se publica un reporte nuevo
> con fecha nueva; este no se reescribe. Correcciones menores van como
> `## Nota {fecha}` AL FINAL.

---

## Respuesta

**{Una oración con el número.}** Ejemplo: "El segmento SMB concentra el
63.4% del churn del trimestre (n=12,481 clientes, 2026-07-01 a 2026-09-30)."

| Campo | Valor |
|-------|-------|
| Métrica | {nombre exacto del contrato en docs/data-contracts.md} |
| Valor | {número con unidad} |
| n | {tamaño de muestra al grano reportado} |
| Ventana | {fecha inicio} a {fecha fin} |
| Población | {filtros aplicados} |
| Comparación | {contra qué, y su valor} |

---

## Método

1. **Fuentes**: {tabla / archivo} — {granularidad} — {corte de datos usado}.
2. **Transformaciones**: {joins, agregaciones, deduplicación} en el orden
   aplicado.
3. **Exclusiones**: {qué filas se excluyeron y por qué} — {cuántas filas}.
4. **Definición usada**: {cita textual del contrato de datos}.

---

## Chequeos de validez

| Chequeo | Resultado | Impacto en la respuesta |
|---------|-----------|-------------------------|
| Tamaño de muestra por celda | {mínimo n = X} | {ninguno / celdas suprimidas} |
| Cobertura por periodo | {filas por mes} | {ninguno / gap en mes X} |
| Integridad del grano | {duplicados en la clave} | {ninguno / dedup aplicado} |
| Sensibilidad a nulos | {valor sin nulos} | {delta} |
| Sensibilidad a outliers | {valor con 1% recortado} | {delta} |
| Cambio de mezcla (Simpson) | {sí / no} | {qué explica el movimiento} |

---

## Caveats

- {Lo que más amenaza la conclusión, primero.}
- {Qué dato haría falta para cerrar esa duda.}
- {Qué NO responde este análisis, para que nadie lo cite de más.}

---

## Reproducción

```
{comando exacto}
```

Verificación registrada: `{comando --check}` — vuelve a correr el número y
falla si se movió fuera de la tolerancia declarada.

Código: `{src/analysis/archivo.py}` | SQL: `{sql/archivo.sql}`
