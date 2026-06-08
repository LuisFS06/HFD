---
name: hfd.initproject
description: >
  Bootstraps the ML project structure: canonical directories, .github/
  agent configuration, .gitignore, requirements.txt. Run before /grillme
  as step 0. Idempotent — safe to re-run on an existing project.
model: claude-haiku-4.5
tools:
  - filesystem
  - terminal
---

## Purpose

Create the project skeleton so that all HFD agents have a predictable
filesystem to read from and write to. This is step 0 — nothing in
the workflow works without a consistent structure.

## Execution procedure

### 1. Detect existing structure

Scan the current working directory for:

- `.github/agents/` — HFD agent files
- `.github/prompts/` — HFD prompt files
- `src/`, `data/`, `notebooks/`, `tests/`, `docs/`
- `docs/constitution.md`, `docs/hypothesis-doc.md` (indicates grillme already ran)

Report what exists and what will be created. Ask the user for
confirmation before creating anything.

### 2. Create ML canonical directories

If they do not exist, create:

```
{project-name}/
├── data/
│   ├── raw/                    # Immutable raw data
│   │   └── .gitkeep
│   ├── processed/              # Cleaned and transformed data
│   │   └── .gitkeep
│   └── external/               # Third-party data sources
│       └── .gitkeep
├── notebooks/                  # Exploration only — no pipeline logic
│   └── .gitkeep
├── src/
│   ├── data/
│   │   ├── __init__.py
│   │   ├── load_data.py        # Data loading functions
│   │   └── preprocess.py       # Data cleaning and preprocessing
│   ├── features/
│   │   ├── __init__.py
│   │   └── build_features.py   # Feature engineering functions
│   ├── models/
│   │   ├── __init__.py
│   │   ├── train_model.py      # Model training logic
│   │   └── evaluate_model.py   # Model evaluation and gate checking
│   ├── visualization/
│   │   ├── __init__.py
│   │   └── visualize.py        # Plotting and reporting functions
│   └── utils/
│       ├── __init__.py
│       └── helper_functions.py # Shared utility functions
├── tests/                      # Unit and integration tests
│   └── .gitkeep
├── docs/                       # Project documentation
│   └── .gitkeep
├── main.py                     # Entry point — orchestrates pipeline
├── requirements.txt
├── .gitignore
└── README.md
```

For each `src/` Python file, create a minimal placeholder with a
docstring explaining its role. Do NOT add implementation — just the
function signatures with `pass` bodies and type hints.

Example `src/data/load_data.py`:
```python
"""Data loading functions for the ML pipeline."""

from pathlib import Path
import pandas as pd


def load_raw_data(source_path: Path) -> pd.DataFrame:
    """Load raw data from the specified source.

    Args:
        source_path: Path to the raw data file.

    Returns:
        Raw dataframe without any transformations.
    """
    pass
```

### 3. Create .gitignore

If `.gitignore` does not exist, create it with ML-appropriate rules:

```gitignore
# Data — raw and large files
data/raw/*
!data/raw/.gitkeep
data/processed/*
!data/processed/.gitkeep
data/external/*
!data/external/.gitkeep

# Models — serialized files
*.pkl
*.joblib
*.h5
*.pt
*.pth
*.onnx
models/

# Notebooks — checkpoints
.ipynb_checkpoints/

# Python
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
dist/
build/
.eggs/
*.egg

# Virtual environments
.venv/
venv/
env/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Environment variables
.env
.env.local

# OS
.DS_Store
Thumbs.db

# MLflow / DVC / Experiment tracking
mlruns/
.dvc/cache/
.dvc/tmp/
wandb/
```

### 4. Create requirements.txt

If `requirements.txt` does not exist, create it with base ML
dependencies:

```
pandas>=2.0
numpy>=1.24
scikit-learn>=1.3
pytest>=7.0
```

Ask the user if they want to add framework-specific dependencies
(XGBoost, LightGBM, PyTorch, TensorFlow) and append accordingly.

### 5. Create docs/coding-standards.md

If `docs/coding-standards.md` does not exist, copy it from the
HFD skill templates (`.github/skills/ml-templates/` does not include
it — the coding standards live in `.github/instructions/` and are
auto-applied, but also need a readable copy in `docs/` for human
reference).

### 6. Optional: experiment tracking setup

Ask the user: "Do you want to initialize experiment tracking? Options:
(a) DVC for data versioning, (b) MLflow for experiment tracking,
(c) both, (d) skip for now."

- **DVC**: run `dvc init` if DVC is installed, else add `dvc` to
  requirements.txt and tell the user to run `pip install dvc && dvc init`.
- **MLflow**: add `mlflow` to requirements.txt, create
  `mlflow_config.py` placeholder in `src/utils/`.
- **Skip**: no action.

### 7. Verify and report

After creating the structure, list all created files and directories.
Confirm the project is ready for `/grillme`.

## Output

A ready-to-use project skeleton. No documents are produced — structure only.

Report format:

```
## Resumen ejecutivo

Proyecto inicializado con estructura ML canónica.
- Directorios creados: {N}
- Archivos placeholder: {N}
- Dependencias base: {lista}
- Tracking: {DVC / MLflow / ninguno}
- Siguiente paso: ejecutar `/grillme` para iniciar la sesión de hipótesis.

## Archivos creados
{lista completa con rutas}

## Archivos que ya existían (no modificados)
{lista o "ninguno"}
```

## Constraints

- **Idempotent**: never overwrite existing files. If a file exists,
  skip it and report that it was skipped.
- **No implementation**: placeholder files have signatures only, no
  logic. The executor fills in implementation during slice execution.
- **No data**: never create fake or sample data files. The `data/`
  directories contain only `.gitkeep` files.
- Never run `pip install` automatically — only update `requirements.txt`
  and tell the user to install.
- This command does NOT create `docs/constitution.md` or `docs/hypothesis-doc.md`.
  Those are created by `/grillme`.
