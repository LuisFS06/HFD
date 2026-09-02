#!/usr/bin/env python3
"""Deterministic data profiler for HFD blind research.

Profiles CSV/TSV/Parquet/JSON/JSONL/Excel files and prints a factual
markdown report: rows, columns, dtypes, null percentages, duplicates, time
ranges, and optional target distribution. The agent interprets the output
instead of writing throwaway pandas code every session.

Column output is capped (--max-cols) because a 400-column table pasted into
a session costs more context than the analysis it feeds.

Usage:
    python profile_data.py data/raw/                 # every table under the dir
    python profile_data.py data/raw/tx.csv --target churned
    python profile_data.py a.csv b.parquet --sample 200000 --max-cols 40
"""

import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    import pandas as pd
except ImportError:
    print("ERROR: pandas is required. Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(2)


SUFFIXES = (".csv", ".tsv", ".txt", ".parquet", ".json", ".jsonl", ".ndjson",
            ".xlsx", ".xls")
DATE_HINTS = ("date", "time", "fecha", "hora", "dia", "día", "mes", "anio",
              "año", "periodo", "período", "timestamp", "ts_")


def load(path: Path, sample: int) -> "pd.DataFrame":
    suffix = path.suffix.lower()
    if suffix == ".parquet":
        df = pd.read_parquet(path)
    elif suffix in (".jsonl", ".ndjson"):
        df = pd.read_json(path, lines=True, nrows=sample or None)
    elif suffix == ".json":
        df = pd.read_json(path)
    elif suffix in (".xlsx", ".xls"):
        df = pd.read_excel(path, nrows=sample or None)
    elif suffix == ".tsv":
        return pd.read_csv(path, nrows=sample or None, sep="\t", low_memory=False)
    elif suffix == ".txt":
        # unknown delimiter: let the python engine sniff it
        return pd.read_csv(path, nrows=sample or None, sep=None, engine="python")
    else:
        return pd.read_csv(path, nrows=sample or None, low_memory=False)
    return df.head(sample) if sample and len(df) > sample else df


def profile(path: Path, target: str | None, sample: int, max_cols: int) -> None:
    print(f"\n## {path.as_posix()}")
    try:
        df = load(path, sample)
    except Exception as e:
        print(f"- **Accesible**: no — {type(e).__name__}: {e}")
        return

    sampled = f" (muestra de {sample:,})" if sample and len(df) == sample else ""
    print(f"- **Registros**: {len(df):,}{sampled} | **Columnas**: {df.shape[1]}")
    dupes = int(df.duplicated().sum())
    print(f"- **Duplicados exactos**: {dupes:,} ({dupes / max(len(df), 1):.1%})")

    columns = list(df.columns)
    shown = columns[:max_cols] if max_cols else columns
    if len(shown) < len(columns):
        print(f"- **Columnas mostradas**: {len(shown)} de {len(columns)} "
              f"(usar --max-cols 0 para todas)")

    print("\n| Columna | Dtype | Nulls % | Unicos | Ejemplo |")
    print("|---------|-------|---------|--------|---------|")
    for col in shown:
        s = df[col]
        nulls = s.isna().mean()
        uniq = s.nunique(dropna=True)
        example = next((repr(v)[:30] for v in s.dropna().head(1)), "-")
        print(f"| {col} | {s.dtype} | {nulls:.1%} | {uniq:,} | {example} |")

    # Time range for datetime-like columns (English and Spanish naming)
    for col in shown:
        s = df[col]
        name = col.lower() if isinstance(col, str) else ""
        if any(k in name for k in DATE_HINTS) or str(s.dtype).startswith("datetime"):
            try:
                parsed = pd.to_datetime(s, errors="coerce")
                if parsed.notna().any():
                    print(f"- **Rango temporal `{col}`**: {parsed.min()} a {parsed.max()} "
                          f"({parsed.isna().mean():.1%} no parseable)")
            except Exception:
                pass

    if target:
        if target in df.columns:
            dist = df[target].value_counts(normalize=True, dropna=False)
            parts = ", ".join(f"{k}: {v:.1%}" for k, v in dist.head(10).items())
            print(f"- **Distribucion target `{target}`**: {parts}")
        else:
            print(f"- **Target `{target}`**: AUSENTE en este archivo")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="files or directories to profile")
    ap.add_argument("--target", default=None, help="target column to report distribution for")
    ap.add_argument("--sample", type=int, default=0, help="row cap per file (0 = all)")
    ap.add_argument("--max-cols", type=int, default=60,
                    help="column cap per file, for context economy (0 = all)")
    args = ap.parse_args()

    files: list[Path] = []
    for p in map(Path, args.paths):
        if p.is_dir():
            files += sorted(f for f in p.rglob("*") if f.suffix.lower() in SUFFIXES)
        elif p.exists():
            files.append(p)
        else:
            print(f"## {p.as_posix()}\n- **Existe**: no")
    if not files:
        print("(no tabular files found — looked for " + ", ".join(SUFFIXES) + ")")
        return 1

    print(f"# Data profile — {len(files)} archivo(s)")
    for f in files:
        profile(f, args.target, args.sample, args.max_cols)
    return 0


if __name__ == "__main__":
    sys.exit(main())
