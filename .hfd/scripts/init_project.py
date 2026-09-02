#!/usr/bin/env python3
"""Idempotent ML project scaffold for HFD.

Creates the canonical directory tree, placeholder modules, .gitignore and
requirements.txt. Never overwrites existing files. Prints a created/skipped
report so the agent only has to relay it.

Usage:
    python init_project.py [--track both|modeling|analysis] \
        [--frameworks xgboost,lightgbm] [--tracking mlflow|dvc|both]
"""

import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path.cwd()

PLACEHOLDER = '''"""{doc}"""

from pathlib import Path

import pandas as pd


def {func}({args}) -> {ret}:
    """{func_doc}

    Args:
        {args_doc}

    Returns:
        {ret_doc}
    """
    raise NotImplementedError("Implemented during slice execution - see docs/prd-slices.md")
'''

MODULES = {
    "src/data/load_data.py": dict(
        doc="Data loading functions for the ML pipeline.",
        func="load_raw_data", args="source_path: Path", ret="pd.DataFrame",
        func_doc="Load raw data from the specified source.",
        args_doc="source_path: Path to the raw data file.",
        ret_doc="Raw dataframe without any transformations."),
    "src/data/preprocess.py": dict(
        doc="Data cleaning and preprocessing.",
        func="preprocess", args="df: pd.DataFrame", ret="pd.DataFrame",
        func_doc="Clean and preprocess raw data.",
        args_doc="df: Raw dataframe.",
        ret_doc="Cleaned dataframe ready for feature engineering."),
    "src/features/build_features.py": dict(
        doc="Feature engineering functions.",
        func="build_features", args="df: pd.DataFrame", ret="pd.DataFrame",
        func_doc="Build model features from preprocessed data.",
        args_doc="df: Preprocessed dataframe.",
        ret_doc="Feature matrix ready for training."),
    "src/models/train_model.py": dict(
        doc="Model training logic.",
        func="train", args="features: pd.DataFrame, target: pd.Series", ret="object",
        func_doc="Train the model defined in docs/design-decisions.md.",
        args_doc="features: Feature matrix.\n        target: Target vector.",
        ret_doc="Trained model object."),
    "src/models/evaluate_model.py": dict(
        doc="Model evaluation and gate checking.",
        func="evaluate", args="model: object, features: pd.DataFrame, target: pd.Series", ret="dict",
        func_doc="Evaluate a model and return gate metrics.",
        args_doc="model: Trained model.\n        features: Evaluation features.\n        target: Evaluation target.",
        ret_doc="Mapping of metric name to value."),
    "src/visualization/visualize.py": dict(
        doc="Plotting and reporting functions.",
        func="plot_metric", args="values: pd.Series, title: str", ret="None",
        func_doc="Plot a metric series.",
        args_doc="values: Metric values.\n        title: Plot title.",
        ret_doc="None. Saves or shows the figure."),
    "src/analysis/example_question.py": dict(
        doc="One analysis = one script = one reproducible answer.\n\nCopy this module per question. It must run end to end from raw data and\nprint the number it claims, so /hfd-review can recompute it later.",
        func="answer", args="source_path: Path", ret="dict",
        func_doc="Answer one business question from raw data.",
        args_doc="source_path: Path to the source table.",
        ret_doc="Mapping with the headline number, the sample size and the date range."),
    "src/utils/helper_functions.py": dict(
        doc="Shared utility functions.",
        func="set_seed", args="seed: int", ret="None",
        func_doc="Set global random seeds for reproducibility.",
        args_doc="seed: Seed value.",
        ret_doc="None."),
}

GITIGNORE = """\
# Data - raw and large files
data/raw/*
!data/raw/.gitkeep
data/processed/*
!data/processed/.gitkeep
data/external/*
!data/external/.gitkeep

# Models - serialized files
*.pkl
*.joblib
*.h5
*.pt
*.pth
*.onnx
models/

# Notebooks - checkpoints
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
"""

BASE_REQS = ["pandas>=2.0", "numpy>=1.24", "scikit-learn>=1.3", "pytest>=7.0"]

# Shared by both tracks.
DIRS_BASE = [
    "data/raw", "data/processed", "data/external",
    "notebooks", "tests", "docs", "docs/state",
    "src/data", "src/utils",
]
# Modeling track: hypothesis -> slices -> gates.
DIRS_MODELING = ["src/features", "src/models", "src/visualization"]
# Analysis track: question -> reproducible script -> dated report.
DIRS_ANALYSIS = ["src/analysis", "sql", "reports"]

PKG_BASE = ["src", "src/data", "src/utils"]
PKG_MODELING = ["src/features", "src/models", "src/visualization"]
PKG_ANALYSIS = ["src/analysis"]

MODELING_MODULES = ("src/features/build_features.py", "src/models/train_model.py",
                    "src/models/evaluate_model.py", "src/visualization/visualize.py")
ANALYSIS_MODULES = ("src/analysis/example_question.py",)

PYPROJECT = """\
[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
"""

REPORTS_README = """\
# Reports

Un archivo por pregunta respondida, con fecha en el nombre:
`YYYY-MM-DD-pregunta-corta.md`. Cada reporte declara el numero, el tamano
de muestra, el rango de fechas, los filtros aplicados y el comando exacto
que lo reproduce. Se registran en el ledger con:

    python .hfd/scripts/worklog.py close <ID> --verified pass \\
        --finding "..." --artifacts reports/<archivo>.md
"""

SQL_README = """\
# SQL

Consultas versionadas, una por archivo, sin resultados pegados adentro.
Cada consulta empieza con un comentario: pregunta que responde, tablas
fuente y granularidad de salida. Los scripts de `src/analysis/` las leen
desde aqui en vez de embeber SQL en Python.
"""

MAIN_PY = '''"""Entry point - orchestrates the ML pipeline slice by slice.

Each slice in docs/prd-slices.md wires its steps here behind a CLI flag,
e.g. `python main.py --evaluate --slice 1`.
"""


def main() -> None:
    raise NotImplementedError("Wired up during slice execution.")


if __name__ == "__main__":
    main()
'''


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--track", choices=["both", "modeling", "analysis"], default="both",
                    help="which track's directories to scaffold (default: both)")
    ap.add_argument("--frameworks", default="",
                    help="comma-separated extras appended to requirements.txt")
    ap.add_argument("--tracking", choices=["mlflow", "dvc", "both", "none"], default="none")
    args = ap.parse_args()

    dirs = list(DIRS_BASE)
    packages = list(PKG_BASE)
    modules = {}
    if args.track in ("both", "modeling"):
        dirs += DIRS_MODELING
        packages += PKG_MODELING
        modules.update({k: v for k, v in MODULES.items()
                        if k in MODELING_MODULES or k.startswith(("src/data/", "src/utils/"))})
    if args.track in ("both", "analysis"):
        dirs += DIRS_ANALYSIS
        packages += PKG_ANALYSIS
        modules.update({k: v for k, v in MODULES.items()
                        if k in ANALYSIS_MODULES or k.startswith(("src/data/", "src/utils/"))})

    created, skipped = [], []

    def write(rel: str, content: str) -> None:
        p = ROOT / rel
        if p.exists():
            skipped.append(rel)
            return
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8", newline="\n")
        created.append(rel)

    for d in dirs:
        p = ROOT / d
        if not p.exists():
            p.mkdir(parents=True)
            created.append(d + "/")
        keep = p / ".gitkeep"
        if d.split("/")[0] in ("data", "notebooks", "tests", "docs") and not any(p.iterdir()):
            keep.touch()

    for pkg in packages:
        write(f"{pkg}/__init__.py", "")

    for rel, spec in modules.items():
        write(rel, PLACEHOLDER.format(**spec))

    write("main.py", MAIN_PY)
    write(".gitignore", GITIGNORE)
    write("pyproject.toml", PYPROJECT)
    if args.track in ("both", "analysis"):
        write("reports/README.md", REPORTS_README)
        write("sql/README.md", SQL_README)

    reqs = list(BASE_REQS)
    reqs += [f for f in args.frameworks.split(",") if f.strip()]
    if args.tracking in ("mlflow", "both"):
        reqs.append("mlflow")
    if args.tracking in ("dvc", "both"):
        reqs.append("dvc")
    write("requirements.txt", "\n".join(reqs) + "\n")

    print("CREATED:")
    for c in created:
        print(f"  {c}")
    if skipped:
        print("SKIPPED (already existed, untouched):")
        for s in skipped:
            print(f"  {s}")
    print(f"\nDone: {len(created)} created, {len(skipped)} skipped (track: {args.track}). "
          "Install deps with: pip install -r requirements.txt")
    print("Next: python .hfd/scripts/context.py freeze  (locks the cacheable docs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
