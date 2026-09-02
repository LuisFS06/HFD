#!/usr/bin/env python3
"""Append-only work ledger for HFD daily development.

Covers the day-to-day units that are NOT metric experiments: analysis
questions, pipeline features, fixes, refactors, data onboarding. One event
per line in docs/state/worklog.jsonl — nothing is ever rewritten, so the
file stays a stable cached prefix and grows only at the end. Current state
is folded from the events at read time.

Every unit of work carries a verification command. That is the analysis-track
equivalent of a quantitative gate: an analysis whose number nobody can
recompute is not done, it is a rumor.

Usage:
    python worklog.py add --kind analysis --title "Churn por segmento Q3" \
        --intent "responder si el segmento SMB explica la caida" \
        --verification "python src/analysis/churn_by_segment.py --check"
    python worklog.py update W003 --status wip --notes "esperando acceso a CRM"
    python worklog.py close W003 --verified pass \
        --finding "SMB concentra 63% del churn (n=12,481, 2026-07..09)" \
        --artifacts reports/2026-09-02-churn-por-segmento.md
    python worklog.py show [--last 10] [--open] [--kind analysis] [--json]
    python worklog.py recheck [W003 | --all] [--dry-run]
    python worklog.py stats
"""

import argparse
import json
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

LEDGER = Path("docs/state/worklog.jsonl")
KINDS = ["analysis", "feature", "fix", "refactor", "data", "chore"]
STATUSES = ["wip", "blocked", "done", "abandoned"]
VERDICTS = ["pass", "fail", "skipped", "pending"]
FIELDS = ("title", "intent", "kind", "status", "verified", "verification",
          "finding", "notes", "files", "artifacts", "tags")


def read_events() -> list[dict]:
    if not LEDGER.exists():
        return []
    events = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return events


def append(event: dict) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def fold(events: list[dict]) -> dict:
    """Collapse the event stream into current state, keyed by work id."""
    state: dict = {}
    for e in events:
        wid = e.get("id")
        if not wid:
            continue
        rec = state.setdefault(wid, {"id": wid, "opened": e.get("date"), "events": 0})
        rec["events"] += 1
        rec["updated"] = e.get("date")
        for k in FIELDS:
            if e.get(k) not in (None, "", []):
                rec[k] = e[k]
        if e.get("event") == "close":
            rec["status"] = e.get("status", "done")
    return state


def next_id(events: list[dict]) -> str:
    used = [int(e["id"][1:]) for e in events
            if isinstance(e.get("id"), str) and e["id"][1:].isdigit()]
    return f"W{max(used, default=0) + 1:03d}"


def csv(value: str) -> list[str]:
    return [v.strip() for v in (value or "").split(",") if v.strip()]


def line_of(rec: dict) -> str:
    mark = {"done": "x", "wip": ">", "blocked": "!", "abandoned": "-"}.get(rec.get("status", "wip"), "?")
    verdict = rec.get("verified", "pending")
    return (f"[{mark}] {rec['id']} {rec.get('updated', '?')} {rec.get('kind', '?'):<9} "
            f"{verdict:<8} {rec.get('title', '(untitled)')}")


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("add", help="open a new unit of work")
    p.add_argument("--kind", required=True, choices=KINDS)
    p.add_argument("--title", required=True)
    p.add_argument("--intent", required=True, help="what question or change this closes")
    p.add_argument("--verification", default="",
                   help="the command that proves it works / reproduces the number")
    p.add_argument("--files", default="")
    p.add_argument("--artifacts", default="")
    p.add_argument("--tags", default="")
    p.add_argument("--status", default="wip", choices=STATUSES)

    p = sub.add_parser("update", help="append a state change to an existing unit")
    p.add_argument("id")
    p.add_argument("--status", choices=STATUSES)
    p.add_argument("--verified", choices=VERDICTS)
    p.add_argument("--verification")
    p.add_argument("--notes")
    p.add_argument("--files")
    p.add_argument("--artifacts")
    p.add_argument("--finding")

    p = sub.add_parser("close", help="close a unit with its verification verdict")
    p.add_argument("id")
    p.add_argument("--verified", required=True, choices=VERDICTS)
    p.add_argument("--finding", default="", help="the answer, with n and date range")
    p.add_argument("--artifacts", default="")
    p.add_argument("--files", default="")
    p.add_argument("--notes", default="")
    p.add_argument("--status", default="done", choices=STATUSES)

    p = sub.add_parser("show")
    p.add_argument("--last", type=int, default=10)
    p.add_argument("--open", action="store_true", help="only unfinished work")
    p.add_argument("--kind", choices=KINDS)
    p.add_argument("--id")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("recheck", help="re-run stored verification commands")
    p.add_argument("id", nargs="?")
    p.add_argument("--all", action="store_true", help="every closed unit that has one")
    p.add_argument("--dry-run", action="store_true", help="print the commands, run nothing")

    p = sub.add_parser("stats")
    p.add_argument("--json", action="store_true")

    args = ap.parse_args()
    events = read_events()
    state = fold(events)
    today = str(date.today())

    if args.cmd == "add":
        wid = next_id(events)
        append({"id": wid, "event": "open", "date": today,
                "ts": datetime.now().isoformat(timespec="seconds"),
                "kind": args.kind, "title": args.title, "intent": args.intent,
                "verification": args.verification, "status": args.status,
                "verified": "pending", "files": csv(args.files),
                "artifacts": csv(args.artifacts), "tags": csv(args.tags)})
        print(f"{wid} opened ({args.kind}): {args.title}")
        if not args.verification:
            print("  no --verification recorded: declare one before closing, "
                  "or the result is not reproducible.")
        return 0

    if args.cmd in ("update", "close"):
        if args.id not in state:
            print(f"ERROR: {args.id} not in {LEDGER}. Run `worklog.py show` for ids.",
                  file=sys.stderr)
            return 1
        event = {"id": args.id, "event": args.cmd, "date": today,
                 "ts": datetime.now().isoformat(timespec="seconds")}
        for key in ("status", "verified", "verification", "notes", "finding"):
            value = getattr(args, key, None)
            if value:
                event[key] = value
        for key in ("files", "artifacts"):
            value = getattr(args, key, None)
            if value:
                event[key] = csv(value)
        append(event)
        merged = fold(read_events())[args.id]
        print(line_of(merged))
        if args.cmd == "close":
            missing = [a for a in merged.get("artifacts", []) if not Path(a).exists()]
            for m in missing:
                print(f"  WARNING: declared artifact {m} is not on disk")
            if merged.get("verified") == "pending":
                print("  WARNING: closed without a verdict — was it actually verified?")
        return 0

    if args.cmd == "show":
        rows = list(state.values())
        if args.id:
            rows = [r for r in rows if r["id"] == args.id]
        if args.kind:
            rows = [r for r in rows if r.get("kind") == args.kind]
        if args.open:
            rows = [r for r in rows if r.get("status") in ("wip", "blocked")]
        rows.sort(key=lambda r: r["id"])
        rows = rows[-args.last:] if not (args.open or args.id) else rows
        if args.json:
            print(json.dumps(rows, indent=2, ensure_ascii=False))
            return 0
        if not rows:
            print("(no matching work logged)")
            return 0
        for r in rows:
            print(line_of(r))
            if args.id or args.open:
                if r.get("intent"):
                    print(f"      intent: {r['intent']}")
                if r.get("finding"):
                    print(f"      finding: {r['finding']}")
                if r.get("verification"):
                    print(f"      verify: {r['verification']}")
                if r.get("artifacts"):
                    print(f"      artifacts: {', '.join(r['artifacts'])}")
        return 0

    if args.cmd == "recheck":
        targets = [state[args.id]] if args.id and args.id in state else []
        if args.all:
            targets = [r for r in state.values() if r.get("verification")]
        if args.id and not targets:
            print(f"ERROR: {args.id} not found.", file=sys.stderr)
            return 1
        if not targets:
            print("Nothing to recheck (no stored verification commands).")
            return 0
        failed = 0
        for rec in sorted(targets, key=lambda r: r["id"]):
            cmd = rec.get("verification")
            if not cmd:
                print(f"{rec['id']}: no verification command recorded — skipped")
                continue
            print(f"{rec['id']} $ {cmd}")
            if args.dry_run:
                continue
            proc = subprocess.run(cmd, shell=True)
            verdict = "pass" if proc.returncode == 0 else "fail"
            failed += proc.returncode != 0
            append({"id": rec["id"], "event": "recheck", "date": today,
                    "ts": datetime.now().isoformat(timespec="seconds"),
                    "verified": verdict, "notes": f"recheck exit={proc.returncode}"})
            print(f"  -> {verdict}")
        return 1 if failed else 0

    if args.cmd == "stats":
        by_kind: dict = {}
        by_status: dict = {}
        for r in state.values():
            by_kind[r.get("kind", "?")] = by_kind.get(r.get("kind", "?"), 0) + 1
            by_status[r.get("status", "?")] = by_status.get(r.get("status", "?"), 0) + 1
        unverified = [r["id"] for r in state.values()
                      if r.get("status") == "done" and r.get("verified") not in ("pass", "skipped")]
        payload = {"total": len(state), "by_kind": by_kind, "by_status": by_status,
                   "closed_unverified": unverified}
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return 0
        print(f"WORKLOG — {len(state)} unit(s), {len(events)} event(s)")
        print("  by kind:   " + (", ".join(f"{k}={v}" for k, v in sorted(by_kind.items())) or "-"))
        print("  by status: " + (", ".join(f"{k}={v}" for k, v in sorted(by_status.items())) or "-"))
        if unverified:
            print(f"  closed without a passing verification: {', '.join(unverified)}")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
