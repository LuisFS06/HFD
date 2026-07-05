# Hypothesis-First Development (HFD)

> Un flujo de trabajo para ciencia de datos implementado como **skills de
> Claude Code**. Reemplaza el ciclo de vida de ingeniería de software con
> uno nativo de ML: hipótesis falsable → investigación ciega → decisiones
> de diseño → slices verticales con gates cuantitativos → **loop
> incremental de experimentos**.

---

## ¿Por qué HFD?

En ingeniería de software empiezas con un lienzo en blanco. En ciencia de
datos, el lienzo ya tiene una imagen pintada — tus datos, tus modelos,
tus métricas actuales — y esa imagen determina qué puedes pintar encima.

HFD empieza con una sesión de interrogación para construir una hipótesis
falsable, mapea qué datos y modelos ya existen antes de cualquier decisión
de diseño, ejecuta en slices verticales con gates pass/fail, y — a partir
del baseline — entra en un **loop incremental barato**: cada cambio chico
(un feature nuevo, un hiperparámetro, una limpieza de datos) es un
micro-experimento de costo fijo, no una re-planificación.

## Qué cambió respecto a la versión de agentes de Copilot

La versión anterior era buena creando las bases del proyecto y poco útil
después. Esta versión está diseñada con principios de harness engineering:

1. **Scripts deterministas en vez de tokens.** El scaffolding, el
   dashboard de estado, el perfilado de datos, los checkpoints y el ledger
   de experimentos los hacen scripts de Python (`.claude/skills/hfd-shared/scripts/`),
   no el LLM. El modelo interpreta resultados; no reinventa pandas cada sesión.

2. **Documentos de planificación inmutables = prompt cache estable.** Los
   docs grandes que cada sesión relee (constitution, hypothesis, plan de
   slices) nunca se reescriben — todo lo nuevo se agrega AL FINAL. El
   estado volátil (checkpoints, gates, iteraciones) vive en `docs/state/`
   en archivos chicos gestionados por scripts. Resultado: los inputs
   grandes quedan byte-idénticos entre sesiones y el caching de prompts
   realmente amortiza. Detalle: [state-and-caching.md](.claude/skills/hfd-shared/references/state-and-caching.md).

3. **Trabajo incremental como camino de primera clase.** Ya no hace falta
   re-correr el flujo completo para un cambio chico:

   | Necesidad | Comando |
   |-----------|---------|
   | Probar un cambio chico contra la mejor métrica actual | `/hfd-experiment "agregar feature X"` |
   | Agregar un slice sin re-planificar | `/hfd-slices add <objetivo>` |
   | Refrescar hallazgos de UNA fuente de datos | `/hfd-research refresh <fuente>` |
   | Re-abrir UNA decisión de diseño firmada | `/hfd-design revisit <N>` |
   | Ver dónde está el proyecto y qué sigue | `/hfd-status` |

4. **Contratos de contexto.** Cada skill declara qué carga y qué NO carga.
   El executor carga UN slice (`get_slice.py`), no el plan completo. El
   loop de experimentos no carga ningún documento de planificación.

---

## El flujo

```
/hfd-init → /hfd-grill → /hfd-research → /hfd-design → /hfd-slices → /hfd-run (×N)
                                                                        ↓ baseline
      /hfd-status (cualquier momento)                            /hfd-experiment (loop)
      /hfd-constitution (revisiones)
```

| Paso | Skill | Qué hace | Produce |
|------|-------|----------|---------|
| 0 | `/hfd-init` | Scaffolding vía script idempotente | Estructura ML canónica |
| 1 | `/hfd-grill` | Sesión socrática para construir la hipótesis | `docs/hypothesis-doc.md`, `docs/constitution.md` |
| — | `/hfd-constitution` | Revisión quirúrgica con cascade check | `docs/constitution.md` actualizado |
| 2 | `/hfd-research` | Mapea datos y modelos SIN conocer la hipótesis | `docs/blind-research.md` |
| 3 | `/hfd-design` | Decisiones técnicas con grilling de arquitectura | `docs/design-decisions.md`, `docs/model-card.md` |
| 4 | `/hfd-slices` | Slices verticales con gates, ordenados por valor de información | `docs/prd-slices.md` (inmutable) + `docs/state/slices.json` |
| 5 | `/hfd-run` | Ejecuta UN slice con checkpoints por script, evalúa gate | Código + artefactos + estado |
| ∞ | `/hfd-experiment` | Micro-experimento contra la mejor métrica actual | Ledger append-only + código adoptado/revertido |
| — | `/hfd-status` | Dashboard determinista + comando sugerido | Salida de script (0 tokens de análisis) |

---

## Instalación

Requisito: [Claude Code](https://claude.com/claude-code) y Python ≥ 3.10.

```bash
# Copiar al proyecto destino
cd /ruta/a/tu-proyecto-ml
cp -r /ruta/a/HFD/.claude ./.claude
cp /ruta/a/HFD/CLAUDE.md ./CLAUDE.md
mkdir -p docs && cp /ruta/a/HFD/docs/coding-standards.md ./docs/
```

Verificar: abrir Claude Code en el proyecto y correr `/hfd-status`.

> Los archivos de `.github/` (agentes de GitHub Copilot) se mantienen como
> versión legacy para quien siga en Copilot, pero ya no reciben mejoras.
> La fuente de verdad es `.claude/skills/`.

---

## El loop incremental (la parte nueva importante)

Una vez que un slice produjo un baseline, el día a día es:

```
/hfd-experiment probar target encoding en la columna segment
```

El skill: (1) consulta el número a batir con `experiment.py best`,
(2) formula un micro-hipótesis de una línea, (3) implementa el cambio
mínimo, (4) evalúa con EXACTAMENTE el mismo comando/split/seed que el gate
del slice, (5) registra el veredicto en `docs/state/experiments.jsonl`
(append-only) y (6) adopta el código o lo revierte por completo.

```
[E001] 2026-07-05 adopt    AUC=0.78            add feature days_since_last_tx
[E002] 2026-07-05 discard  AUC=0.775 (-0.005)  tune max_depth 6->8
[E003] 2026-07-05 adopt    AUC=0.801 (+0.021)  target-encode segment
```

Costo por experimento ≈ constante: no carga constitution, ni hypothesis,
ni blind-research, ni el plan — solo el ledger, el comando del gate y los
archivos que toca. Los descartes valen tanto como los adoptados: quedan
registrados y nadie vuelve a probar lo mismo.

Reglas de escalamiento: si un experimento viola una decisión firmada →
`/hfd-design revisit N`; si prueba un aspecto NUEVO de la hipótesis →
`/hfd-slices add`; si dispara un criterio de cancelación → se reporta
igual que en `/hfd-run`.

---

## Estado y caching

```
docs/                          # INMUTABLES tras su creación (cache-estables)
├── constitution.md            #   solo /hfd-constitution los revisa (raro)
├── hypothesis-doc.md          #   enmiendas fechadas AL FINAL
├── blind-research.md          #   addenda fechados AL FINAL
├── design-decisions.md        #   decisiones superseding AL FINAL
├── model-card.md              #   sección "Actualizaciones" AL FINAL
├── prd-slices.md              #   slices nuevos AL FINAL (/hfd-slices add)
└── state/                     # VOLÁTIL — chico, gestionado por scripts
    ├── slices.json            #   checkpoints, gates, iteraciones (checkpoint.py)
    ├── journal.md             #   notas de ejecución append-only
    └── experiments.jsonl      #   ledger de experimentos append-only
```

Regla: **agregar al final, nunca editar el medio**. Un prefijo estable es
un prefijo cacheado. Por eso los resúmenes ejecutivos describen el plan,
nunca el estado vivo — el estado vivo se consulta con `/hfd-status`.

### Scripts compartidos (`.claude/skills/hfd-shared/scripts/`)

| Script | Hace | Lo usa |
|--------|------|--------|
| `init_project.py` | Scaffolding idempotente | /hfd-init |
| `hfd_status.py` | Dashboard + siguiente comando (`--json` disponible) | /hfd-status, /hfd-run |
| `profile_data.py` | Perfil factual de CSV/Parquet (nulls, duplicados, target) | /hfd-research, /hfd-grill |
| `get_slice.py` | Extrae UN slice del plan | /hfd-run |
| `checkpoint.py` | Estado de slices: add-slice/start/step/gate/iterate/note | /hfd-slices, /hfd-run |
| `experiment.py` | Ledger: add/best/show con delta contra el mejor | /hfd-experiment |

Crash recovery: si `/hfd-run` se interrumpe, la próxima invocación lee
`slices.json`, verifica que los artefactos de pasos completados existan en
disco y retoma desde el siguiente paso pendiente. No se rehace trabajo.

---

## Primeros pasos

```
/hfd-init
/hfd-grill  Quiero predecir churn con datos transaccionales.
            Datos en data/raw/. Hoy la decisión se toma manualmente.
/hfd-research  Los datos están en data/raw/. No hay documentación de campos.
/hfd-design  Me preocupa la calidad de los labels. El equipo domina sklearn y XGBoost.
/hfd-slices  Lo primero que necesito saber es si los labels son confiables. Máximo 6 slices.
/hfd-run
...
/hfd-experiment agregar feature days_since_last_tx
```

## Guía de prompts

Cada skill ya tiene instrucciones completas; tu prompt aporta el contexto
que no puede inferir:

| Skill | Frases que mejoran la sesión |
|-------|------------------------------|
| `/hfd-grill` | "busca en data/raw/", "el equipo define X como...", `amend <qué cambió>` |
| `/hfd-research` | "busca en {ruta}", "no tengo acceso a {fuente}", `refresh <fuente>` |
| `/hfd-design` | "lo que más me preocupa", "el equipo tiene experiencia en", `revisit <N>` |
| `/hfd-slices` | "lo que más necesito saber primero", "máximo N slices", `add <objetivo>` |
| `/hfd-run` | "desde que planificamos cambió...", "tengo N horas" |
| `/hfd-experiment` | una línea concreta: "probar X", opcionalmente "--metric AUC" |

## Conceptos clave

| Concepto de software | Equivalente HFD |
|---------------------|-----------------|
| User Story | Hipótesis de negocio |
| Acceptance Criteria | Gate cuantitativo |
| Implementation Plan | Design decisions |
| Task breakdown | Slice architecture |
| Definition of Done | Gate pass/fail |
| Research | Blind research |
| CONTEXT.md | constitution.md |
| Hotfix / small PR | `/hfd-experiment` |

## FAQ

**¿Puedo saltarme pasos?** Cada skill verifica sus prerequisitos y te dice
qué comando correr primero. `/hfd-status` siempre sabe qué sigue.

**¿Puedo usar esto sin Claude Code?** Los SKILL.md son markdown con
instrucciones; sirven como system prompt en cualquier LLM. Los scripts de
`hfd-shared/scripts/` funcionan solos con Python. La carpeta `.github/`
conserva la versión legacy para GitHub Copilot.

**¿Por qué los documentos no muestran el estado actual?** Para que el
prompt cache los amortice. El estado vive en `docs/state/` y se consulta
con `/hfd-status` en ~30 líneas.

## Licencia

[MIT](LICENSE)
