#!/usr/bin/env python3
"""Experiment ledger for HFD incremental work.

Append-only JSONL ledger (docs/state/experiments.jsonl) — cache-friendly,
trivially parseable, never rewritten. Tracks the current best per metric
so a new experiment always knows the number to beat.

Usage:
    python experiment.py best --metric AUC
    python experiment.py add --change "add feature days_since_last_tx" \
        --hypothesis "recency captures churn signal missing from volume features" \
        --metric AUC --value 0.842 --verdict adopt --files "src/features/build_features.py"
    python experiment.py show [--last 10]
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

LEDGER = Path("docs/state/experiments.jsonl")


def read() -> list[dict]:
    if not LEDGER.exists():
        return []
    rows = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows


def best_of(rows: list[dict], metric: str) -> dict | None:
    scored = [r for r in rows if r.get("metric") == metric and r.get("value") is not None
              and r.get("verdict") == "adopt"]
    if not scored:
        return None
    direction = scored[-1].get("direction", "max")
    return (max if direction == "max" else min)(scored, key=lambda r: r["value"])


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("add")
    p.add_argument("--change", required=True, help="one-line description of the change")
    p.add_argument("--hypothesis", required=True, help="why this change should help")
    p.add_argument("--metric", required=True)
    p.add_argument("--value", type=float, required=True)
    p.add_argument("--direction", choices=["max", "min"], default="max")
    p.add_argument("--verdict", required=True, choices=["adopt", "discard", "inconclusive"])
    p.add_argument("--files", default="", help="comma-separated files touched")
    p.add_argument("--notes", default="")

    p = sub.add_parser("best")
    p.add_argument("--metric", required=True)

    p = sub.add_parser("show")
    p.add_argument("--last", type=int, default=10)

    args = ap.parse_args()
    rows = read()

    if args.cmd == "add":
        prev = best_of(rows, args.metric)
        entry = {
            "id": f"E{len(rows) + 1:03d}",
            "date": str(date.today()),
            "change": args.change,
            "hypothesis": args.hypothesis,
            "metric": args.metric,
            "value": args.value,
            "direction": args.direction,
            "baseline": prev["value"] if prev else None,
            "delta": round(args.value - prev["value"], 6) if prev else None,
            "verdict": args.verdict,
            "files": [f.strip() for f in args.files.split(",") if f.strip()],
            "notes": args.notes,
        }
        LEDGER.parent.mkdir(parents=True, exist_ok=True)
        with LEDGER.open("a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        delta = f" (delta {entry['delta']:+g} vs best {entry['baseline']})" if prev else " (first entry for this metric)"
        print(f"{entry['id']} logged: {args.metric} = {args.value}{delta} -> {args.verdict}")

    elif args.cmd == "best":
        b = best_of(rows, args.metric)
        if b:
            print(json.dumps(b, indent=2, ensure_ascii=False))
        else:
            print(f"No adopted experiments for metric '{args.metric}'. "
                  "Baseline comes from docs/state/slices.json gate results.")

    elif args.cmd == "show":
        for r in rows[-args.last:]:
            delta = f" ({r['delta']:+g})" if r.get("delta") is not None else ""
            print(f"[{r['id']}] {r['date']} {r['verdict']:12s} "
                  f"{r['metric']}={r['value']}{delta}  {r['change']}")
        if not rows:
            print("(ledger empty)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
