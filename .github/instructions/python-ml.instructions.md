---
description: "Coding standards for Python ML code — auto-applied to src/ and tests/"
applyTo: "src/**/*.py,tests/**/*.py,*.py"
---

## Formatting

- PEP 8 for all Python code. No exceptions.
- Line length: 88 characters (Black default).
- Docstrings: Google style on every public function.
- Type hints on all function signatures.
- Import order: stdlib → third-party → local, separated by blank lines.

## Principles

- **DRY**: extract shared logic to `src/utils/helper_functions.py`.
- **KISS**: prefer the simplest approach that passes the gate.
- **YAGNI**: implement only what the current slice needs.
- **SOLID**: Single Responsibility for functions, Open/Closed for
  feature engineering (configuration over hardcoded columns),
  consistent model interfaces (fit/predict/evaluate).

## Anti-patterns to reject

- God scripts (one file that loads, processes, trains, evaluates)
- Magic numbers (hardcoded thresholds without named constants)
- Silent failures (bare except, swallowed errors)
- Notebook-to-script dumps (cells pasted without refactoring)
- Global mutable state
- Hardcoded file paths

## SOLID vs YAGNI resolution

If existing code violates SOLID, refactor only the function you are
modifying. Do not refactor callers or sibling functions. YAGNI applies
to refactoring scope.

## Notebook rule

Notebooks are for exploration and visualization ONLY. If a slice
involves exploration in a notebook, extract all reusable functions to
`src/` before the slice is marked complete.
