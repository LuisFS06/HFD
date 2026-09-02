# Hypothesis-First Development (HFD)

> Un harness de trabajo diario para ciencia de datos **y** análisis de
> datos, implementado como **Agent Skills** — el mismo formato abierto
> (SKILL.md) funciona en **Claude Code** y en **GitHub Copilot**. No solo
> arma la base del proyecto: gobierna el día a día — features
> incrementales, preguntas de negocio, fixes, reviews — con verificación
> obligatoria y un manejo de contexto explícito en JSON diseñado para que
> el prompt cache realmente amortice.

---

## Qué resuelve

En ingeniería de software empiezas con un lienzo en blanco. En datos, el
lienzo ya tiene una imagen pintada — tus datos, tus modelos, tus métricas
actuales — y esa imagen determina qué puedes pintar encima.

Y el trabajo real no es un proyecto: son **dos flujos que conviven**.

| | Track de modelado | Track de análisis |
|---|---|---|
| Unidad | slice | pregunta |
| Ejecuta | `/hfd-run` | `/hfd-analyze` |
| Gate | métrica vs umbral numérico | el número se reproduce y sobrevive sus chequeos de validez |
| Ledger | `experiments.jsonl` | `worklog.jsonl` |
| Entrega | modelo + resultado de gate | reporte fechado en `reports/` |
| Itera con | `/hfd-experiment` | `/hfd-analyze refresh <W-id>` |

Y el desarrollo diario que alimenta a los dos — pipelines, fuentes nuevas,
fixes, refactors, reportes programados — vive en `/hfd-feature`, con
test primero y comando de verificación obligatorio.

---

## El flujo

```
setup      /hfd-init
modelado   /hfd-grill → /hfd-research → /hfd-design → /hfd-slices → /hfd-run (×N)
                                                                       ↓ baseline
                                                            /hfd-experiment (loop)
análisis   /hfd-analyze <pregunta>  →  /hfd-analyze refresh <W-id>
diario     /hfd-feature <cambio>  →  /hfd-review  →  commit
siempre    /hfd-status    /hfd-context    /hfd-constitution
```

| Skill | Qué hace | Produce |
|-------|----------|---------|
| `/hfd-init` | Scaffolding idempotente (`--track both\|modeling\|analysis`) | Estructura canónica |
| `/hfd-grill` | Sesión socrática para construir la hipótesis | `constitution.md`, `hypothesis-doc.md` |
| `/hfd-research` | Mapea datos y modelos SIN conocer la hipótesis | `blind-research.md` |
| `/hfd-design` | Decisiones técnicas con grilling de arquitectura | `design-decisions.md`, `model-card.md` |
| `/hfd-slices` | Slices verticales con gates, ordenados por valor de información | `prd-slices.md` (append-only) + estado |
| `/hfd-run` | Ejecuta UN slice con checkpoints, evalúa el gate | Código + artefactos + estado |
| `/hfd-experiment` | Micro-experimento contra la mejor métrica actual | Ledger de experimentos |
| **`/hfd-analyze`** | Responde UNA pregunta de forma reproducible | Reporte fechado + contrato de datos |
| **`/hfd-feature`** | Unidad de desarrollo diario, test primero | Código + test + unidad en el ledger |
| **`/hfd-review`** | Gate pre-commit determinista + review del diff | Veredicto + mensaje de commit propuesto |
| **`/hfd-context`** | Diagnostica y repara la economía de contexto | Lock de contexto actualizado |
| `/hfd-constitution` | Revisión quirúrgica con cascade check | `constitution.md` actualizado |
| `/hfd-status` | Dashboard determinista de ambos tracks | Salida de script (0 tokens de análisis) |

---

## Manejo de contexto (el centro del harness)

El caching de prompts — en Claude Code y en GitHub Copilot — reutiliza el
**prefijo byte-idéntico** más largo de un request. Dos consecuencias:
un byte cambiado arriba invalida todo lo que sigue, y el **orden** es parte
de la identidad del prefijo. HFD lo trata como un recurso administrado, no
como una buena costumbre.

**Registro** — `.hfd/context.json` declara cada artefacto, su *tier* de
cache y el contrato de cada skill (`load`, `never`, `budget_tokens`).

**Herramienta** — `.hfd/scripts/context.py`:

```bash
python .hfd/scripts/context.py pack hfd-run --slice 3   # qué cargar, en orden, y cuánto cuesta
python .hfd/scripts/context.py show "constitution#Glosario"  # una sección, no el documento
python .hfd/scripts/context.py verify                   # prueba de que los docs siguen siendo append-only
python .hfd/scripts/context.py budget                   # costo estimado por skill vs su presupuesto
python .hfd/scripts/context.py freeze                   # re-lockea tras un cambio deliberado
```

```
CONTEXT PACK — hfd-run  (track: modeling)
budget 15000 tok | estimated 6120 tok (41% used) | 4870 tok cacheable
cache: HIT-ELIGIBLE — cacheable prefix unchanged since 2026-09-01

LOAD IN THIS ORDER (the order is what keeps the prefix cacheable):
  1 [frozen     ]  1252 tok  docs/coding-standards.md
  2 [append-only]  2100 tok  docs/data-contracts.md      ~ appended (+140 tok, prefix intact)
  3 [revisable  ]   310 tok  docs/constitution.md  §Glosario
  4 [probe      ]   400 tok  $ python .hfd/scripts/hfd_status.py
  5 [probe      ]   700 tok  $ python .hfd/scripts/get_slice.py 3

NEVER LOAD (contract violation, not a preference): blind-research, hypothesis-doc, prd-slices
```

**Tiers**: `frozen` → `append-only` → `revisable` → `volatile` → `probe` →
`task`. Se cargan en ese orden, así la mitad cara del contexto es idéntica
entre sesiones y solo la cola barata es nueva.

**Lock** — `docs/state/context-lock.json` guarda hashes. `verify` clasifica
cada documento en `unchanged` / `appended` (prefijo intacto, la cache
sobrevive) / `mutated` (**FAIL**: se editó en el medio y se murió la cache
de ahí en adelante) / `missing`. CI corre `verify`, así "agregamos al final"
deja de ser una costumbre y pasa a ser un check que rompe el build.

Detalle completo: [`.hfd/references/context-management.md`](.hfd/references/context-management.md).

### Específico de GitHub Copilot

- `.github/copilot-instructions.md` se antepone a **cada** request: se
  mantiene corto y estable; cambiarlo invalida todos los prefijos cacheados.
- `.github/instructions/*.instructions.md` se adjuntan por glob de path
  (`src/**`, `src/analysis/**`, `docs/**`), así las reglas pesadas viajan
  solo en los turnos que tocan esos archivos.
- `.github/prompts/hfd-*.prompt.md` se **generan** desde el frontmatter de
  cada skill (`sync_skills.py`), con el modelo fijado por paso — mismas
  instrucciones en ambas plataformas, sin drift posible.
- En chat, `context.py pack <skill> --emit` entrega el contexto como un
  solo blob ordenado, en vez de varias menciones sueltas que llegan en el
  orden que elija el editor.

| Paso | Modelo (Copilot) | Razón |
|------|------------------|-------|
| init, status, context, constitution | Claude Haiku 4.5 | Casi todo lo hace un script |
| grill, design | Claude Sonnet 4.6 | Matiz conversacional, grilling socrático |
| research, slices, review | GPT-5 mini | Análisis factual y planificación estructurada |
| run, experiment, feature, analyze | GPT-5.4 mini | Codean y corren N veces por día |

---

## Instalación

Requisito: Python ≥ 3.10 y [Claude Code](https://claude.com/claude-code)
**o** [GitHub Copilot](https://github.com/features/copilot).

```bash
cd /ruta/a/tu-proyecto

# Común a ambas plataformas (scripts, registro de contexto, templates)
cp -r /ruta/a/HFD/.hfd ./.hfd
mkdir -p docs && cp /ruta/a/HFD/docs/coding-standards.md ./docs/

# Claude Code
cp -r /ruta/a/HFD/.claude ./.claude
cp /ruta/a/HFD/CLAUDE.md ./CLAUDE.md

# GitHub Copilot (skills espejo + prompts /hfd-* + instrucciones)
cp -r /ruta/a/HFD/.github ./.github

python .hfd/scripts/context.py freeze   # lockea los documentos cacheables
```

Verificar: correr `/hfd-status` en el chat de tu herramienta.

---

## Un día de trabajo

```
/hfd-status
  → NEXT: /hfd-feature  (resume W014: soportar parquet en el loader)

/hfd-feature terminar el soporte de parquet
  → test primero (falla), implementación mínima, verify.py --quick,
    worklog.py recheck --all  → W014 cerrado con su comando de verificación

/hfd-analyze ¿el churn de SMB subió respecto al trimestre pasado?
  → afila la pregunta (métrica, población, ventana, grano, comparación)
  → usa la definición de docs/data-contracts.md, perfila los datos
  → src/analysis/churn_smb.py + 6 chequeos de validez
  → reports/2026-09-02-churn-smb.md, W015 cerrado
  → "SMB subió de 4.1% a 6.3% (n=12,481, 2026-07..09). El caveat que más
     amenaza la conclusión: julio tiene 40% menos filas que agosto."

/hfd-review
  → verify.py: structure PASS | context PASS | state PASS | lint PASS | tests PASS
  → review del diff, mensaje de commit propuesto con W014, W015
```

Y en el track de modelado, el loop incremental sigue costando lo mismo por
iteración:

```
[E001] 2026-09-02 adopt    AUC=0.780            add feature days_since_last_tx
[E002] 2026-09-02 discard  AUC=0.775 (-0.005)   tune max_depth 6->8
[E003] 2026-09-02 adopt    AUC=0.801 (+0.021)   target-encode segment
```

Los descartes valen tanto como los adoptados: quedan registrados y nadie
vuelve a probar lo mismo.

---

## Verificación en todos lados

Nada se cierra sin el comando que lo prueba:

| Unidad | Prueba |
|--------|--------|
| Slice | gate numérico, evaluado con el comando declarado en el plan |
| Experimento | misma métrica, mismo split, misma semilla, delta contra el mejor |
| Análisis | script con modo `--check` + 6 chequeos de validez |
| Feature / fix | test que falla primero, después pasa |
| Commit | `verify.py`: estructura, contexto, estado, docs, lint, tests |

`worklog.py recheck --all` vuelve a correr **todos** los comandos de
verificación guardados. Es lo que hace seguro el trabajo diario: un cambio
en un loader que mueve silenciosamente el número reportado el mes pasado
aparece hoy, no en una reunión.

---

## Estado y archivos

```
docs/                          # APPEND-ONLY tras su creación (cache-estables)
├── coding-standards.md        #   frozen — nunca cambia
├── constitution.md            #   la única excepción: /hfd-constitution la revisa
├── hypothesis-doc.md          #   enmiendas fechadas AL FINAL
├── blind-research.md          #   addenda fechados AL FINAL
├── design-decisions.md        #   decisiones superseding AL FINAL
├── model-card.md              #   "Actualizaciones" AL FINAL
├── prd-slices.md              #   slices nuevos AL FINAL
├── data-contracts.md          #   definiciones de métricas, AL FINAL
└── state/                     # VOLÁTIL — chico, solo vía scripts
    ├── slices.json            #   checkpoints y gates (checkpoint.py)
    ├── journal.md             #   notas de ejecución (checkpoint.py note)
    ├── experiments.jsonl      #   ledger de experimentos (experiment.py)
    ├── worklog.jsonl          #   ledger de trabajo diario (worklog.py)
    └── context-lock.json      #   hashes del contexto cacheable (context.py)

reports/                       # un reporte fechado por pregunta respondida
sql/                           # una consulta por archivo, sin resultados pegados
src/analysis/                  # un script por pregunta
```

### Scripts (`.hfd/scripts/`)

| Script | Hace | Lo usa |
|--------|------|--------|
| `context.py` | Packs, secciones, budget, lock y verificación de cache | todas |
| `hfd_status.py` | Dashboard de ambos tracks + siguiente comando (`--json`) | /hfd-status, /hfd-run |
| `worklog.py` | Ledger de trabajo: add/update/close/show/recheck/stats | /hfd-analyze, /hfd-feature |
| `verify.py` | Estructura, contexto, estado, docs, lint, tests | /hfd-review, CI |
| `experiment.py` | Ledger de experimentos con delta contra el mejor | /hfd-experiment |
| `checkpoint.py` | Estado de slices: add-slice/start/step/gate/iterate/note | /hfd-slices, /hfd-run |
| `get_slice.py` | Extrae UN slice del plan | /hfd-run |
| `profile_data.py` | Perfil factual de CSV/TSV/Parquet/JSON/Excel | /hfd-research, /hfd-analyze |
| `init_project.py` | Scaffolding idempotente por track | /hfd-init |
| `sync_skills.py` | Espeja skills y genera los prompts de Copilot (`--check` en CI) | mantenimiento |

Crash recovery: si `/hfd-run` se interrumpe, la próxima invocación lee
`slices.json`, verifica que los artefactos de pasos completados existan en
disco y retoma desde el siguiente paso pendiente. En el track de análisis
lo equivalente es una unidad abierta en el worklog: `/hfd-status` la pone
como siguiente acción.

---

## Guía de prompts

| Skill | Frases que mejoran la sesión |
|-------|------------------------------|
| `/hfd-grill` | "busca en data/raw/", "el equipo define X como...", `amend <qué cambió>` |
| `/hfd-research` | "busca en {ruta}", "no tengo acceso a {fuente}", `refresh <fuente>` |
| `/hfd-design` | "lo que más me preocupa", "el equipo tiene experiencia en", `revisit <N>` |
| `/hfd-slices` | "lo que más necesito saber primero", "máximo N slices", `add <objetivo>` |
| `/hfd-run` | "desde que planificamos cambió...", "tengo N horas" |
| `/hfd-experiment` | una línea concreta: "probar X", opcionalmente `--metric AUC` |
| `/hfd-analyze` | la pregunta con ventana y población si las tienes; `refresh <W-id>` |
| `/hfd-feature` | qué debe ser distinto al terminar, y qué se rompería si sale mal |
| `/hfd-review` | `--quick` si solo quieres estructura/estado/contexto |

---

## Conceptos clave

| Concepto de software | Equivalente HFD |
|---------------------|-----------------|
| User Story | Hipótesis de negocio |
| Acceptance Criteria | Gate cuantitativo |
| Implementation Plan | Design decisions |
| Task breakdown | Slice architecture |
| Definition of Done | Gate pass/fail (modelado) / comando de verificación (análisis) |
| Research | Blind research |
| CONTEXT.md | constitution.md |
| Hotfix / small PR | `/hfd-experiment` o `/hfd-feature` |
| Ticket diario | Unidad del worklog |
| Data dictionary | `docs/data-contracts.md` |

---

## FAQ

**¿Puedo saltarme pasos?** Sí. El track de análisis no necesita hipótesis
ni slices: `/hfd-init --track analysis` y `/hfd-analyze` alcanzan. Cada
skill verifica sus prerequisitos y te dice qué falta.

**¿Puedo usar los dos tracks en el mismo repo?** Es el caso esperado.
`/hfd-status` detecta el track (`modeling`, `analysis`, `both`) y prioriza
el trabajo abierto sobre empezar algo nuevo.

**¿Y si no uso Claude Code ni Copilot?** Los SKILL.md son markdown con
instrucciones; sirven como system prompt en cualquier LLM. Los scripts de
`.hfd/scripts/` funcionan solos con Python ≥ 3.10 (solo `profile_data.py`
necesita pandas).

**¿Copilot y Claude Code se comportan igual?** Sí — cargan el mismo
SKILL.md (espejado con `sync_skills.py`, verificado en CI) y llaman los
mismos scripts. En Copilot además los `.github/prompts/` fijan un modelo
por paso para optimizar credits.

**¿Por qué los documentos no muestran el estado actual?** Para que el
prompt cache los amortice. El estado vive en `docs/state/` y se consulta
con `/hfd-status` en ~30 líneas.

**¿Cómo sé si el caching está funcionando?** `/hfd-context`, o directamente
`python .hfd/scripts/context.py verify` y `stats`: te dicen cuántos tokens
siguen siendo idénticos entre sesiones y qué documento rompió el prefijo.

---

## Desarrollo del preset

```bash
python .hfd/scripts/sync_skills.py --check   # drift entre .claude/ y .github/
python -m pytest .hfd/tests -q               # tests del harness
python .hfd/scripts/context.py verify        # disciplina append-only
```

`.claude/skills/` es la copia canónica; `.github/` se genera. CI corre los
tres.

## Licencia

[MIT](LICENSE)
