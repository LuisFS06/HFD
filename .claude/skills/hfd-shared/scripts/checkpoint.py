#!/usr/bin/env python3
"""Checkpoint manager for HFD slice execution.

Owns docs/state/slices.json (volatile state) so planning docs never get
rewritten — that keeps them stable for prompt caching. All writes are
atomic. The journal (docs/state/journal.md) is append-only.

Usage:
    python checkpoint.py add-slice 1 --title "Label quality" \
        --metric label_agreement --op ">=" --threshold 0.9 \
        --fail-action "cancelar CC-0001" --steps "Load labels;Sample audit;Compute agreement"
    python checkpoint.py start 1                # slice -> en_progreso
    python checkpoint.py step 1 2 start
    python checkpoint.py step 1 2 done --artifact data/processed/audit.parquet
    python checkpoint.py gate 1 --value 0.93    # computes pass/fail vs threshold
    python checkpoint.py iterate 1              # bump iteration counter
    python checkpoint.py note 1 "chose stratified sample because ..."
    python checkpoint.py show [1]
"""

import argparse
import json
import os
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

STATE_DIR = Path("docs/state")
STATE_FILE = STATE_DIR / "slices.json"
JOURNAL = STATE_DIR / "journal.md"

OPS = {">=": lambda a, b: a >= b, "<=": lambda a, b: a <= b,
       ">": lambda a, b: a > b, "<": lambda a, b: a < b,
       "==": lambda a, b: a == b}


def load() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"updated": None, "slices": {}}


def save(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state["updated"] = datetime.now().isoformat(timespec="seconds")
    fd, tmp = tempfile.mkstemp(dir=STATE_DIR, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    os.replace(tmp, STATE_FILE)


def get_slice(state: dict, n: str) -> dict:
    if n not in state["slices"]:
        print(f"ERROR: slice {n} not in {STATE_FILE}. Run add-slice first.", file=sys.stderr)
        sys.exit(1)
    return state["slices"][n]


def append_journal(slice_n: str, text: str) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with JOURNAL.open("a", encoding="utf-8", newline="\n") as f:
        f.write(f"\n### [{date.today()}] Slice {slice_n}\n{text}\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("add-slice")
    p.add_argument("n")
    p.add_argument("--title", required=True)
    p.add_argument("--metric", required=True)
    p.add_argument("--op", required=True, choices=list(OPS))
    p.add_argument("--threshold", type=float, required=True)
    p.add_argument("--fail-action", required=True,
                   help='e.g. "cancelar CC-0001", "pivotar Slice 4", "iterar max 3"')
    p.add_argument("--steps", required=True, help="semicolon-separated step descriptions")
    p.add_argument("--depends-on", default="", help="comma-separated slice numbers")

    p = sub.add_parser("start")
    p.add_argument("n")

    p = sub.add_parser("step")
    p.add_argument("n")
    p.add_argument("m")
    p.add_argument("status", choices=["start", "done", "reset"])
    p.add_argument("--artifact", default=None)

    p = sub.add_parser("gate")
    p.add_argument("n")
    p.add_argument("--value", type=float, required=True)

    p = sub.add_parser("iterate")
    p.add_argument("n")

    p = sub.add_parser("note")
    p.add_argument("n")
    p.add_argument("text")

    p = sub.add_parser("show")
    p.add_argument("n", nargs="?")

    args = ap.parse_args()
    state = load()

    if args.cmd == "add-slice":
        steps = [s.strip() for s in args.steps.split(";") if s.strip()]
        state["slices"][args.n] = {
            "title": args.title,
            "status": "pendiente",
            "gate": {"metric": args.metric, "op": args.op, "threshold": args.threshold},
            "fail_action": args.fail_action,
            "depends_on": [d.strip() for d in args.depends_on.split(",") if d.strip()],
            "iterations": 0,
            "result": None,
            "steps": {str(i + 1): {"desc": d, "status": "pendiente", "artifact": None}
                      for i, d in enumerate(steps)},
        }
        save(state)
        print(f"Slice {args.n} registered with {len(steps)} steps.")

    elif args.cmd == "start":
        sl = get_slice(state, args.n)
        unmet = [d for d in sl.get("depends_on", [])
                 if state["slices"].get(d, {}).get("status") != "pass"]
        if unmet:
            print(f"BLOCKED: dependencies not passed: {', '.join(unmet)}", file=sys.stderr)
            return 1
        sl["status"] = "en_progreso"
        save(state)
        print(f"Slice {args.n} -> en_progreso")

    elif args.cmd == "step":
        sl = get_slice(state, args.n)
        step = sl["steps"].get(args.m)
        if not step:
            print(f"ERROR: step {args.m} not found in slice {args.n}", file=sys.stderr)
            return 1
        step["status"] = {"start": "en_progreso", "done": "done", "reset": "pendiente"}[args.status]
        if args.artifact:
            step["artifact"] = args.artifact
        if args.status == "done" and step["artifact"] and not Path(step["artifact"]).exists():
            print(f"WARNING: declared artifact {step['artifact']} does not exist on disk",
                  file=sys.stderr)
        save(state)
        done = sum(1 for s in sl["steps"].values() if s["status"] == "done")
        print(f"Slice {args.n} step {args.m} -> {step['status']} ({done}/{len(sl['steps'])} done)")

    elif args.cmd == "gate":
        sl = get_slice(state, args.n)
        g = sl["gate"]
        passed = OPS[g["op"]](args.value, g["threshold"])
        sl["result"] = args.value
        sl["status"] = "pass" if passed else "fail"
        sl["gate_date"] = str(date.today())
        save(state)
        verdict = "PASS" if passed else f"FAIL (action: {sl['fail_action']})"
        print(f"Slice {args.n} gate: {g['metric']} = {args.value} {g['op']} {g['threshold']} -> {verdict}")
        append_journal(args.n, f"Gate evaluated: {g['metric']} = {args.value} "
                               f"(threshold {g['op']} {g['threshold']}) -> {verdict}")

    elif args.cmd == "iterate":
        sl = get_slice(state, args.n)
        sl["iterations"] += 1
        sl["status"] = "en_progreso"
        save(state)
        print(f"Slice {args.n} iteration count: {sl['iterations']}")

    elif args.cmd == "note":
        get_slice(state, args.n)
        append_journal(args.n, args.text)
        print(f"Note appended to {JOURNAL}")

    elif args.cmd == "show":
        if args.n:
            print(json.dumps(get_slice(state, args.n), indent=2, ensure_ascii=False))
        else:
            print(json.dumps(state, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
