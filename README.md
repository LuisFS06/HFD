# Hypothesis-First Development (HFD)

> Un flujo de trabajo para ciencia de datos implementado como preset de
> agentes de IA para GitHub Copilot. Reemplaza el ciclo de vida de
> ingeniería de software con uno nativo de ML: hipótesis falsable →
> investigación ciega → decisiones de diseño → slices verticales →
> ejecución con gates cuantitativos.

---

## ¿Por qué HFD?

En ingeniería de software empiezas con un lienzo en blanco: defines user
stories, planificas tareas, implementas. En ciencia de datos, el lienzo ya
tiene una imagen pintada — tus datos, tus modelos existentes, tus métricas
actuales — y esa imagen determina qué puedes pintar encima.

Las herramientas de planificación de software (Spec-Kit incluido) asumen
que puedes construir lo que diseñas. En ML eso no es cierto: los datos
restringen las decisiones, las dependencias son circulares, y no hay
concepto de "la realidad limita el spec". HFD cierra esas brechas con
un flujo diseñado para esa realidad.

**Frase corta**: HFD empieza con una sesión de interrogación para construir
una hipótesis falsable, mapea qué datos y modelos ya existen antes de tomar
cualquier decisión de diseño, y ejecuta en slices verticales donde cada uno
tiene un gate cuantitativo de pass/fail.

---

## El flujo

```
/initproject → /grillme → /blindresearch → /designaligner → /slicearchitect → /executor
                                                 ↕
                                          /constitution (revisión, en cualquier momento)
```

| Paso | Comando | Qué hace | Produce |
|------|---------|----------|---------|
| 0 | `/initproject` | Crea estructura de carpetas y archivos base | Proyecto ML canónico |
| 1 | `/grillme` | Sesión socrática para construir la hipótesis | `docs/hypothesis-doc.md`, `docs/constitution.md` |
| — | `/constitution` | Revisa constitution.md cuando algo cambia | `docs/constitution.md` (actualizado) |
| 2 | `/blindresearch` | Mapea datos y modelos SIN conocer la hipótesis | `docs/blind-research.md` |
| 3 | `/designaligner` | Decisiones técnicas con grilling de arquitectura | `docs/design-decisions.md`, `docs/model-card.md` |
| 4 | `/slicearchitect` | Descompone en slices verticales con gates | `docs/prd-slices.md` |
| 5 | `/executor` | Ejecuta UN slice, evalúa gate, checkpoints | Código + artefactos + `docs/prd-slices.md` actualizado |

Todos los documentos se escriben en `docs/`. Código en `src/`, tests en `tests/`.

---

## Instalación

### Prerrequisitos

- [GitHub Copilot](https://github.com/features/copilot) habilitado en tu IDE o en GitHub.com
- Plan con acceso a modelos premium (para poder asignar modelos por agente)

### Opción A — Clonar e instalar

```bash
# 1. Clonar este repositorio
git clone https://github.com/{usuario}/hypothesis-first-development.git

# 2. Copiar al proyecto destino
cd /ruta/a/tu-proyecto-ml
cp -r /ruta/a/hypothesis-first-development/.github/ ./.github/
cp -r /ruta/a/hypothesis-first-development/docs/ ./docs/
```

### Opción B — Clonar como subtree (mantiene actualizaciones)

```bash
cd /ruta/a/tu-proyecto-ml
git subtree add --prefix=.hfd https://github.com/{usuario}/hypothesis-first-development.git main --squash

# Copiar a ubicación final
cp -r .hfd/.github/ ./.github/
cp -r .hfd/docs/ ./docs/
```

### Opción C — Descarga manual

1. Ir a la [página de releases](https://github.com/{usuario}/hypothesis-first-development/releases)
2. Descargar el source code del último release
3. Copiar las carpetas `.github/` y `docs/` a la raíz de tu proyecto ML

### Verificar instalación

Después de copiar, tu proyecto debe tener esta estructura:

```
tu-proyecto-ml/
├── .github/
│   ├── copilot-instructions.md           # Instrucciones globales (always-on)
│   ├── agents/
│   │   ├── hfd.initproject.agent.md
│   │   ├── hfd.grillme.agent.md
│   │   ├── hfd.blindresearch.agent.md
│   │   ├── hfd.designaligner.agent.md
│   │   ├── hfd.slicearchitect.agent.md
│   │   ├── hfd.executor.agent.md
│   │   └── hfd.constitution.agent.md
│   ├── prompts/
│   │   ├── initproject.prompt.md
│   │   ├── grillme.prompt.md
│   │   ├── blindresearch.prompt.md
│   │   ├── designaligner.prompt.md
│   │   ├── slicearchitect.prompt.md
│   │   ├── executor.prompt.md
│   │   └── constitution.prompt.md
│   ├── instructions/
│   │   └── python-ml.instructions.md     # Auto-aplicado a *.py
│   └── skills/
│       └── ml-templates/                 # Templates cargados on-demand
│           ├── constitution-template.md
│           ├── hypothesis-template.md
│           ├── plan-template.md
│           └── tasks-template.md
└── docs/
    └── coding-standards.md
```

### Configurar modelos (opcional)

Cada agente tiene un modelo por defecto optimizado para su tarea. Para
cambiarlo, edita el frontmatter del archivo `.agent.md`:

```yaml
---
name: hfd.executor
model: gpt-4.1          # ← Cambia aquí
---
```

**Modelos recomendados por paso:**

| Agente | Modelo por defecto | Tarea | Razón |
|--------|-------------------|-------|-------|
| `hfd.grillme` | Claude Sonnet 4.6 | Conversar y decidir | Matiz conversacional, desafío de supuestos |
| `hfd.blindresearch` | GPT-5 mini | Analizar datos | Contexto largo, análisis factual |
| `hfd.designaligner` | Claude Sonnet 4.6 | Decidir y justificar | Cross-referencing, honestidad en assumptions |
| `hfd.slicearchitect` | GPT-5 mini | Planificar | Planificación estructurada, múltiples inputs |
| `hfd.executor` | GPT-5.4 mini | Codear | Eficiente, se ejecuta N veces por proyecto |
| `hfd.constitution` | Claude Haiku 4.5 | Editar | Tarea ligera, edición quirúrgica |
| `hfd.initproject` | Claude Haiku 4.5 | Crear estructura | Tarea estructural simple |

**Regla simple**: Sonnet para conversar, GPT para codear, Haiku para editar.

---

## Primeros pasos

### 1. Inicializar el proyecto

```
/initproject
```

Crea la estructura canónica de carpetas ML (`src/`, `data/`, `notebooks/`,
`tests/`), `.gitignore`, `requirements.txt`, y placeholders con type hints.

### 2. Construir la hipótesis

```
/grillme

Quiero predecir churn de clientes usando datos transaccionales.
Tenemos datos en data/raw/transactions.csv y data/raw/customers.csv.
Hoy no hay modelo — la decisión se toma manualmente.
```

El agente interroga tu hipótesis pregunta por pregunta, afina terminología,
y produce `docs/constitution.md` + `docs/hypothesis-doc.md`.

### 3. Investigación ciega

```
/blindresearch

Los datos están en data/raw/. No hay documentación de los campos.
No sé si hay modelos en producción.
```

Explora datos y modelos SIN conocer la hipótesis. Produce un mapa factual
de la realidad en `docs/blind-research.md`.

### 4. Decisiones de diseño

```
/designaligner

Lo que más me preocupa es la calidad de los labels.
El equipo tiene experiencia en scikit-learn y XGBoost.
Quiero empezar simple.
```

Toma decisiones técnicas ancladas en los hallazgos. El área de arquitectura
de modelo usa un **grilling socrático** — no presenta opciones, interroga tu
elección.

### 5. Arquitectura de slices

```
/slicearchitect

Lo que más necesito saber primero es si los labels son confiables.
Máximo 6 slices.
```

Descompone el proyecto en slices verticales ordenados por valor de
información — si el proyecto va a morir, que muera en el slice 1.

### 6. Ejecutar

```
/executor
```

Ejecuta el siguiente slice pendiente con **checkpointing paso a paso**.
Si la sesión se interrumpe, `/executor` retoma desde el último checkpoint.

---

## Características principales

### Resumen ejecutivo en cada documento

Todos los documentos producidos incluyen un `## Resumen ejecutivo` al
inicio. Si no tienes tiempo de auditar el documento completo, el resumen
cubre los puntos clave en 5-8 líneas.

### Checkpointing en el executor

Si el executor se interrumpe (timeout, crash, cierre de sesión):

1. Detecta el slice `en progreso`
2. Lee la tabla de estado paso a paso
3. Verifica que los artefactos de pasos completados existen en disco
4. Continúa desde el siguiente paso pendiente
5. Lee las notas de ejecución para contexto de la sesión anterior

No se pierde trabajo. No se rehace lo ya completado.

### Grilling socrático en arquitectura de modelo

El `/designaligner` no presenta un menú de opciones. Interroga al
científico en tres fases: elicitar la intención, desafiar contra los datos
del blind research, y anclar en especificaciones concretas (modelo, config,
evaluación, capacidad del equipo).

### Investigación ciega

`/blindresearch` mapea la realidad de los datos sin conocer la hipótesis
propuesta. Esto evita el sesgo de confirmación — exploras lo que hay, no
lo que esperas encontrar.

---

## Estructura del proyecto ML generado

Después del flujo completo, un proyecto HFD tiene esta estructura:

```
tu-proyecto/
├── .github/                        # Agentes y prompts de HFD
├── data/
│   ├── raw/                        # Datos crudos (inmutables)
│   ├── processed/                  # Datos limpios y transformados
│   └── external/                   # Datos de terceros
├── notebooks/                      # Solo exploración
├── src/
│   ├── data/                       # Carga y preprocesamiento
│   ├── features/                   # Feature engineering
│   ├── models/                     # Entrenamiento y evaluación
│   ├── visualization/              # Gráficos y reportes
│   └── utils/                      # Funciones compartidas
├── tests/
├── docs/
│   ├── coding-standards.md         # Estándares de código
│   ├── constitution.md             # ← /grillme
│   ├── hypothesis-doc.md           # ← /grillme
│   ├── blind-research.md           # ← /blindresearch
│   ├── design-decisions.md         # ← /designaligner
│   ├── model-card.md               # ← /designaligner
│   └── prd-slices.md               # ← /slicearchitect
├── main.py
├── requirements.txt
└── .gitignore
```

---

## Artefactos

| Artefacto | Producido por | Descripción |
|-----------|--------------|-------------|
| `docs/constitution.md` | `/grillme` | Fuente de verdad: hipótesis, criterios, glosario, datos |
| `docs/hypothesis-doc.md` | `/grillme` | Hipótesis verificables con gates cuantitativos |
| `docs/blind-research.md` | `/blindresearch` | Mapa factual de datos y modelos existentes |
| `docs/design-decisions.md` | `/designaligner` | Decisiones técnicas firmadas por el científico |
| `docs/model-card.md` | `/designaligner` | Tarjeta del modelo (planificado → real, actualizada por executor) |
| `docs/prd-slices.md` | `/slicearchitect` | Slices verticales con gates, checkpoints y notas de ejecución |
| `docs/coding-standards.md` | `/initproject` | Estándares de código (referencia humana) |

---

## Guía de prompts

Cada comando ya tiene instrucciones completas. Tu prompt le da el
**contexto que no puede inferir**: dónde están los datos, qué te
preocupa, qué restricciones hay.

### Palabras clave por paso

| Comando | Frases que mejoran la sesión |
|---------|----------------------------|
| `/grillme` | "busca en data/raw/", "no hay documentación", "el equipo define X como..." |
| `/blindresearch` | "busca en {ruta}", "no sé si hay modelos", "no tengo acceso a {fuente}" |
| `/designaligner` | "lo que más me preocupa", "el equipo tiene experiencia en", "empezar simple" |
| `/slicearchitect` | "lo que más necesito saber primero", "máximo N slices", "antes de construir nada" |
| `/executor` | "desde que planificamos cambió", "verifica antes de arrancar", "tengo N horas" |
| `/constitution` | "verifica downstream", "muéstrame dónde se usa" |

---

## Costo estimado

Con la selección de modelos optimizada, un proyecto de 8 slices cuesta
aproximadamente **585–757 credits** de Copilot. Sin estructura (un solo
modelo para todo), el mismo proyecto cuesta 1,000–1,800 credits. El 84%
del ahorro viene de eliminar re-trabajo, no de usar modelos baratos.

---

## FAQ

### ¿Puedo usar HFD sin GitHub Copilot?

Los archivos `.agent.md` son markdown con instrucciones detalladas. Puedes
copiar el contenido de cualquier agente y usarlo como system prompt en
Claude Code, ChatGPT, o cualquier otro LLM. Pierdes la integración de
slash commands y la asignación de modelos por agente, pero las instrucciones
funcionan igual.

### ¿Puedo saltarme pasos?

Cada agente verifica que los artefactos anteriores existan. Si intentas
ejecutar `/designaligner` sin `docs/blind-research.md`, te dirá que
ejecutes `/blindresearch` primero. El orden existe porque en ciencia de
datos, lo que ya existe define lo que es posible.

### ¿Puedo agregar mis propios agentes?

Sí. Crea un `.agent.md` en `.github/agents/` y un `.prompt.md` en
`.github/prompts/` que lo referencie. Los agentes de HFD usan el
prefijo `hfd.` por convención.

---

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
| ADR | Criterio de cancelación |

---

## Contribuciones

Las contribuciones son bienvenidas. Por favor abre un issue antes de
enviar un PR para discutir el cambio propuesto.

## Licencia

[MIT](LICENSE)
