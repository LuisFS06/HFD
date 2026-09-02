# ML Coding Standards

> Read before writing any code — slice execution (`/hfd-run`), experiments
> (`/hfd-experiment`), daily features (`/hfd-feature`) and analyses
> (`/hfd-analyze`). Non-negotiable, including for "quick experiments".
>
> This file is `frozen` in `.hfd/context.json`: it is loaded by almost every
> skill, so it must stay byte-stable. Changes are rare and deliberate, and
> are followed by `python .hfd/scripts/context.py freeze`.

## Principles

- **DRY** (Don't Repeat Yourself) — extract shared logic into
  reusable functions in `src/utils/helper_functions.py`. If you
  write the same transformation twice, refactor immediately.

- **KISS** (Keep It Simple, Stupid) — prefer the simplest approach
  that passes the gate. No premature abstraction, no frameworks
  beyond what the slice requires.

- **YAGNI** (You Aren't Gonna Need It) — implement only what the
  current slice needs. Do not add features, parameters, or
  abstractions "in case we need them later."

- **SOLID** — apply to ML code:
  - Single Responsibility: one function does one thing. `load_data()`
    loads data; it does not also clean it.
  - Open/Closed: feature engineering functions accept configuration,
    not hardcoded column names.
  - Liskov Substitution: model classes expose a consistent interface
    (`fit`, `predict`, `evaluate`) regardless of the underlying
    algorithm.
  - Interface Segregation: evaluation functions don't require training
    artifacts they don't use.
  - Dependency Inversion: pipeline steps depend on abstractions (e.g.,
    a data loader interface), not on concrete file paths.

## Formatting

- **PEP 8** for all Python code. No exceptions.
- Line length: 88 characters (Black default).
- Docstrings: Google style on every public function.
- Type hints on all function signatures.
- Import order: stdlib → third-party → local, separated by blank lines.

## Anti-patterns to avoid

Never produce code that exhibits these patterns:

- **God script**: a single file that loads data, processes features,
  trains, and evaluates. Split into the canonical structure below.
- **Magic numbers**: hardcoded thresholds, column indices, or
  hyperparameters without named constants or config.
- **Silent failures**: bare `except: pass`, swallowed errors, or
  missing logging on data quality issues.
- **Leaky abstraction**: evaluation code that imports training
  internals, or feature code that assumes a specific model.
- **Notebook-to-script dump**: copy-pasting notebook cells into .py
  files without refactoring into functions with proper interfaces.
- **Global mutable state**: global variables modified across functions.
  Pass data explicitly through function arguments.
- **Hardcoded paths**: file paths embedded in code instead of using
  configuration or path constants.

## Canonical project structure

All code must be organized into this folder structure. If the structure
does not yet exist, create the necessary directories and files as part
of the first slice execution.

```
{project-name}/
├── data/
│   ├── raw/                    # Immutable raw data — never modified
│   ├── processed/              # Cleaned and transformed data
│   └── external/               # Third-party data sources
├── notebooks/                  # Jupyter notebooks for exploration only
├── src/
│   ├── data/
│   │   ├── load_data.py        # Data loading functions
│   │   └── preprocess.py       # Data cleaning and preprocessing
│   ├── features/
│   │   └── build_features.py   # Feature engineering functions
│   ├── models/
│   │   ├── train_model.py      # Model training logic
│   │   └── evaluate_model.py   # Model evaluation and gate checking
│   ├── visualization/
│   │   └── visualize.py        # Plotting and reporting functions
│   └── utils/
│       └── helper_functions.py # Shared utility functions (DRY target)
├── tests/                      # Unit and integration tests
├── .gitignore
├── README.md
├── requirements.txt
└── main.py                     # Entry point — orchestrates the pipeline
```

Rules for placement:

- Raw data goes in `data/raw/` and is NEVER modified in place.
  Processing writes to `data/processed/`.
- Notebooks are for exploration and visualization ONLY. No pipeline
  logic lives in notebooks. If a slice involves exploration in a
  notebook, extract all reusable functions to `src/` before the
  slice is marked complete. The notebook retains only visualization
  and narrative.
- Each `src/` module has a single responsibility matching its name.
- `main.py` is the orchestrator. It calls functions from `src/`
  modules in sequence. It contains no business logic itself.
- Tests mirror the `src/` structure: `tests/test_load_data.py`,
  `tests/test_build_features.py`, etc.
- Every new dependency added during a slice must be appended to
  `requirements.txt` immediately.

## SOLID vs YAGNI resolution

If existing code you must modify violates SOLID, refactor only the
function you are modifying. Do not refactor callers or sibling functions.
YAGNI applies to refactoring scope — fix what you touch, leave the rest.

## Analysis code (`src/analysis/`)

An analysis module answers exactly one question and is judged by whether
someone else gets the same number tomorrow:

- Runs end to end from `data/` with no manual steps and no hidden state.
- Prints the headline number **with n and the date range**; a number
  without its denominator is not an answer.
- Filters, windows, exclusions and tolerances are named constants at the
  top of the module.
- Exposes a `--check` mode that recomputes the number and exits non-zero if
  it moved beyond the declared tolerance — this is the command recorded in
  the work ledger and re-run by `worklog.py recheck`.
- Uses the definition in `docs/data-contracts.md` verbatim; SQL lives in
  `sql/`, one query per file, read by the script.

## Verification

Every behavioural change ships with the command that proves it: a numeric
gate for a slice or experiment, a stored verification command for a work
unit. Write the failing test first — a test that never failed proves
nothing. Never weaken a test to make it pass.
