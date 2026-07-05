#!/usr/bin/env python3
"""HFD project status — deterministic dashboard, zero LLM tokens.

Reads artifact presence in docs/ plus volatile state in docs/state/ and
prints a compact dashboard with the recommended next command.

Usage:
    python hfd_status.py            # human-readable dashboard
    python hfd_status.py --json     # machine-readable
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path.cwd()
DOCS = ROOT / "docs"
STATE = DOCS / "state"

ARTIFACTS = [
    ("constitution", DOCS / "constitution.md", "/hfd-grill"),
    ("hypothesis", DOCS / "hypothesis-doc.md", "/hfd-grill"),
    ("blind-research", DOCS / "blind-research.md", "/hfd-research"),
    ("design-decisions", DOCS / "design-decisions.md", "/hfd-design"),
    ("model-card", DOCS / "model-card.md", "/hfd-design"),
    ("prd-slices", DOCS / "prd-slices.md", "/hfd-slices"),
]


def load_slices() -> dict:
    f = STATE / "slices.json"
    if not f.exists():
        return {}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"WARNING: {f} unreadable ({e})", file=sys.stderr)
        return {}


def load_experiments() -> list[dict]:
    f = STATE / "experiments.jsonl"
    if not f.exists():
        return []
    rows = []
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows


def next_command(artifacts: dict, slices: dict) -> str:
    if not (ROOT / "src").is_dir():
        return "/hfd-init  (no src/ found - bootstrap the project structure)"
    for name, path, cmd in ARTIFACTS:
        if not artifacts[name]:
            return f"{cmd}  (docs/{path.name} missing)"
    sl = slices.get("slices", {})
    if not sl:
        return "/hfd-run  (slices planned but state not initialised - executor will sync)"
    in_progress = [k for k, v in sl.items() if v.get("status") == "en_progreso"]
    if in_progress:
        return f"/hfd-run  (resume Slice {in_progress[0]} from checkpoint)"
    pending = [k for k, v in sl.items() if v.get("status") == "pendiente"]
    if pending:
        return f"/hfd-run  (next: Slice {pending[0]})"
    failed = [k for k, v in sl.items() if str(v.get("status", "")).startswith("fail")]
    if failed:
        return f"human decision pending on failed Slice(s): {', '.join(failed)}"
    return "/hfd-experiment  (all slices passed - iterate incrementally)"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    artifacts = {name: path.exists() for name, path, _ in ARTIFACTS}
    slices = load_slices()
    experiments = load_experiments()

    sl = slices.get("slices", {})
    counts = {"pendiente": 0, "en_progreso": 0, "pass": 0, "fail": 0}
    for v in sl.values():
        s = str(v.get("status", "pendiente"))
        key = "fail" if s.startswith("fail") else s
        counts[key] = counts.get(key, 0) + 1

    best = {}
    for e in experiments:
        m, v = e.get("metric"), e.get("value")
        if m is None or v is None:
            continue
        higher_is_better = e.get("direction", "max") == "max"
        if m not in best or (v > best[m] if higher_is_better else v < best[m]):
            best[m] = v

    nxt = next_command(artifacts, slices)

    if args.json:
        print(json.dumps({
            "date": str(date.today()),
            "artifacts": artifacts,
            "slice_counts": counts,
            "slices": sl,
            "experiments": len(experiments),
            "best_metrics": best,
            "next": nxt,
        }, indent=2, ensure_ascii=False))
        return 0

    print(f"HFD STATUS - {date.today()}")
    print("=" * 46)
    print("Artifacts:")
    for name, path, _ in ARTIFACTS:
        mark = "[x]" if artifacts[name] else "[ ]"
        print(f"  {mark} docs/{path.name}")
    if sl:
        print(f"\nSlices: {counts['pass']} pass | {counts['fail']} fail | "
              f"{counts['en_progreso']} in progress | {counts['pendiente']} pending")
        for k in sorted(sl, key=lambda x: int(x) if x.isdigit() else 99):
            v = sl[k]
            steps = v.get("steps", {})
            done = sum(1 for s in steps.values() if s.get("status") == "done")
            gate = v.get("gate", {})
            gate_s = f"{gate.get('metric', '?')} {gate.get('op', '?')} {gate.get('threshold', '?')}"
            result = f" -> {v['result']}" if v.get("result") is not None else ""
            print(f"  Slice {k}: {v.get('status', '?')}{result} | steps {done}/{len(steps)} | gate: {gate_s}")
    if experiments:
        print(f"\nExperiments: {len(experiments)} logged")
        for m, v in best.items():
            print(f"  best {m}: {v}")
        last = experiments[-1]
        print(f"  last: [{last.get('id', '?')}] {last.get('change', '?')[:60]} -> {last.get('verdict', '?')}")
    print(f"\nNEXT: {nxt}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
