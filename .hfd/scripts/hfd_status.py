#!/usr/bin/env python3
"""HFD project status — deterministic dashboard, zero LLM tokens.

Reads artifact presence in docs/, volatile state in docs/state/ and the
context lock, then prints a compact dashboard with the recommended next
command. Covers both tracks: modeling (slices + gates + experiments) and
analysis/daily development (worklog units + their verification verdicts).

Usage:
    python hfd_status.py            # human-readable dashboard
    python hfd_status.py --json     # machine-readable
    python hfd_status.py --track analysis   # force a track's next-step logic
"""

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path.cwd()
DOCS = ROOT / "docs"
STATE = DOCS / "state"
SCRIPTS = ROOT / ".hfd" / "scripts"

ARTIFACTS = [
    ("constitution", DOCS / "constitution.md", "/hfd-grill"),
    ("hypothesis", DOCS / "hypothesis-doc.md", "/hfd-grill"),
    ("blind-research", DOCS / "blind-research.md", "/hfd-research"),
    ("design-decisions", DOCS / "design-decisions.md", "/hfd-design"),
    ("model-card", DOCS / "model-card.md", "/hfd-design"),
    ("prd-slices", DOCS / "prd-slices.md", "/hfd-slices"),
]


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"WARNING: {path} unreadable ({e})", file=sys.stderr)
        return {}


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows


def fold_worklog(events: list[dict]) -> list[dict]:
    """Same fold as worklog.py, inlined so the dashboard stays one process."""
    state: dict = {}
    for e in events:
        wid = e.get("id")
        if not wid:
            continue
        rec = state.setdefault(wid, {"id": wid})
        rec["updated"] = e.get("date", rec.get("updated"))
        for k in ("title", "intent", "kind", "status", "verified", "verification",
                  "finding", "files", "artifacts", "tags"):
            if e.get(k) not in (None, "", []):
                rec[k] = e[k]
        if e.get("event") == "close":
            rec["status"] = e.get("status", "done")
    return [state[k] for k in sorted(state)]


def context_health() -> dict:
    script = SCRIPTS / "context.py"
    if not script.exists():
        return {}
    try:
        proc = subprocess.run([sys.executable, str(script), "verify", "--json", "--soft"],
                              capture_output=True, text=True, timeout=60)
        payload = json.loads(proc.stdout)
    except (OSError, ValueError, subprocess.SubprocessError):
        return {}
    arts = payload.get("artifacts", [])
    return {
        "broken": payload.get("failures", []),
        "cacheable_tokens": sum(a.get("tokens", 0) for a in arts
                                if a.get("level") == "OK"),
        "unlocked": [a["artifact"] for a in arts if a.get("level") == "NEW"],
    }


def detect_track(artifacts: dict, slices: dict, work: list[dict]) -> str:
    modeling = any(artifacts[k] for k in ("hypothesis", "prd-slices")) or bool(slices)
    analysis = any(w.get("kind") == "analysis" for w in work) or (DOCS / "data-contracts.md").exists()
    if modeling and analysis:
        return "both"
    if analysis:
        return "analysis"
    if modeling:
        return "modeling"
    return "unset"


def next_command(artifacts: dict, slices: dict, work: list[dict], track: str) -> tuple[str, list[str]]:
    also = []
    if not (ROOT / "src").is_dir():
        return "/hfd-init  (no src/ found — bootstrap the project structure)", also

    open_units = [w for w in work if w.get("status") in ("wip", "blocked")]
    if open_units:
        u = open_units[0]
        skill = "/hfd-analyze" if u.get("kind") == "analysis" else "/hfd-feature"
        also = [f"{len(open_units)} open work unit(s) in the ledger"]
        return f"{skill}  (resume {u['id']}: {u.get('title', '')[:48]})", also

    if track in ("analysis", "unset"):
        hint = ("/hfd-analyze <question>  (answer a data question, reproducibly)"
                if track == "analysis" else
                "/hfd-analyze <question>  for analysis work, or /hfd-grill to start a modeling hypothesis")
        if track == "unset":
            also.append("no track chosen yet — analysis and modeling can coexist in one repo")
        return hint, also

    sl = slices.get("slices", {})
    for name, path, cmd in ARTIFACTS:
        if not artifacts[name]:
            return f"{cmd}  (docs/{path.name} missing)", also
    if not sl:
        return "/hfd-run  (slices planned but state not initialised — executor will sync)", also
    in_progress = [k for k, v in sl.items() if v.get("status") == "en_progreso"]
    if in_progress:
        return f"/hfd-run  (resume Slice {in_progress[0]} from checkpoint)", also
    pending = [k for k, v in sl.items() if v.get("status") == "pendiente"]
    if pending:
        return f"/hfd-run  (next: Slice {pending[0]})", also
    failed = [k for k, v in sl.items() if str(v.get("status", "")).startswith("fail")]
    if failed:
        return f"human decision pending on failed Slice(s): {', '.join(failed)}", also
    return "/hfd-experiment  (all slices passed — iterate incrementally)", also


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--track", choices=["modeling", "analysis", "both"], default=None,
                    help="override track detection")
    args = ap.parse_args()

    artifacts = {name: path.exists() for name, path, _ in ARTIFACTS}
    slices = read_json(STATE / "slices.json")
    experiments = read_jsonl(STATE / "experiments.jsonl")
    work = fold_worklog(read_jsonl(STATE / "worklog.jsonl"))
    ctx = context_health()

    sl = slices.get("slices", {})
    counts = {"pendiente": 0, "en_progreso": 0, "pass": 0, "fail": 0}
    for v in sl.values():
        s = str(v.get("status", "pendiente"))
        key = "fail" if s.startswith("fail") else s
        counts[key] = counts.get(key, 0) + 1

    work_counts: dict = {}
    for w in work:
        work_counts[w.get("status", "?")] = work_counts.get(w.get("status", "?"), 0) + 1

    best: dict = {}
    for e in experiments:
        m, v = e.get("metric"), e.get("value")
        if m is None or v is None:
            continue
        higher_is_better = e.get("direction", "max") == "max"
        if m not in best or (v > best[m] if higher_is_better else v < best[m]):
            best[m] = v

    track = args.track or detect_track(artifacts, slices, work)
    nxt, also = next_command(artifacts, slices, work, track)

    if args.json:
        print(json.dumps({
            "date": str(date.today()),
            "track": track,
            "artifacts": artifacts,
            "slice_counts": counts,
            "slices": sl,
            "experiments": len(experiments),
            "best_metrics": best,
            "work_counts": work_counts,
            "open_work": [w for w in work if w.get("status") in ("wip", "blocked")],
            "context": ctx,
            "next": nxt,
            "notes": also,
        }, indent=2, ensure_ascii=False))
        return 0

    print(f"HFD STATUS — {date.today()}   track: {track}")
    print("=" * 52)
    if track in ("modeling", "both", "unset") or any(artifacts.values()):
        print("Planning artifacts:")
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
        print(f"  last: [{last.get('id', '?')}] {last.get('change', '?')[:56]} -> {last.get('verdict', '?')}")
    if work:
        summary = ", ".join(f"{k}={v}" for k, v in sorted(work_counts.items()))
        print(f"\nWork units: {len(work)} ({summary})")
        for w in work[-4:]:
            mark = {"done": "x", "wip": ">", "blocked": "!"}.get(w.get("status", ""), "?")
            print(f"  [{mark}] {w['id']} {w.get('kind', '?'):<9} {w.get('verified', 'pending'):<8} "
                  f"{w.get('title', '')[:44]}")
    if ctx:
        broken = f" | BROKEN: {', '.join(ctx['broken'])}" if ctx.get("broken") else ""
        print(f"\nContext: {ctx.get('cacheable_tokens', 0)} tok cacheable across sessions{broken}")
    for note in also:
        print(f"note: {note}")
    print(f"\nNEXT: {nxt}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
