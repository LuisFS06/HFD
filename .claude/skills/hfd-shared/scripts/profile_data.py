#!/usr/bin/env python3
"""Deterministic data profiler for HFD blind research.

Profiles CSV/Parquet files and prints a factual markdown report: rows,
columns, dtypes, null percentages, duplicates, time ranges, and optional
target distribution. The agent interprets the output instead of writing
throwaway pandas code every session.

Usage:
    python profile_data.py data/raw/                 # every csv/parquet under the dir
    python profile_data.py data/raw/tx.csv --target churned
    python profile_data.py a.csv b.parquet --sample 200000
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


def load(path: Path, sample: int) -> "pd.DataFrame":
    if path.suffix.lower() == ".parquet":
        df = pd.read_parquet(path)
        return df.head(sample) if sample and len(df) > sample else df
    return pd.read_csv(path, nrows=sample or None, low_memory=False)


def profile(path: Path, target: str | None, sample: int) -> None:
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

    print("\n| Columna | Dtype | Nulls % | Unicos | Ejemplo |")
    print("|---------|-------|---------|--------|---------|")
    for col in df.columns:
        s = df[col]
        nulls = s.isna().mean()
        uniq = s.nunique(dropna=True)
        example = next((repr(v)[:30] for v in s.dropna().head(1)), "-")
        print(f"| {col} | {s.dtype} | {nulls:.1%} | {uniq:,} | {example} |")

    # Time range for datetime-like columns
    for col in df.columns:
        s = df[col]
        if "date" in col.lower() or "time" in col.lower() or str(s.dtype).startswith("datetime"):
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
    args = ap.parse_args()

    files: list[Path] = []
    for p in map(Path, args.paths):
        if p.is_dir():
            files += sorted(p.rglob("*.csv")) + sorted(p.rglob("*.parquet"))
        elif p.exists():
            files.append(p)
        else:
            print(f"## {p.as_posix()}\n- **Existe**: no")
    if not files:
        print("(no csv/parquet files found)")
        return 1

    print(f"# Data profile — {len(files)} archivo(s)")
    for f in files:
        profile(f, args.target, args.sample)
    return 0


if __name__ == "__main__":
    sys.exit(main())
