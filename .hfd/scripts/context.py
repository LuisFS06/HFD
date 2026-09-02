#!/usr/bin/env python3
"""Context manager for HFD — the harness's cache-aware working memory.

Reads the JSON registry at .hfd/context.json (tiers, artifacts, probes and
one context contract per skill) and answers four questions deterministically,
so no session has to guess them:

  what do I load    -> `pack <skill>`   ordered manifest + exact commands
  give me just that -> `show <ref>`     one file, or ONE section of it
  is my cache warm  -> `verify`         append-only proof against the lock
  what does it cost -> `budget|stats`   token estimates per contract/tier

Why the ordering matters: LLM prompt caches (Claude Code and GitHub Copilot
alike) reuse a request's longest byte-identical PREFIX. Loading immutable
docs first and volatile state last keeps that prefix intact across sessions;
loading the same files in a different order every day guarantees a miss.

Usage:
    python .hfd/scripts/context.py pack hfd-run --slice 3
    python .hfd/scripts/context.py pack hfd-analyze --emit > /tmp/pack.md
    python .hfd/scripts/context.py show "constitution#Glosario"
    python .hfd/scripts/context.py freeze
    python .hfd/scripts/context.py verify [--json] [--update]
    python .hfd/scripts/context.py budget [--json]
    python .hfd/scripts/context.py stats
"""

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
from datetime import date, datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REGISTRY = Path(".hfd/context.json")
LOCK = Path("docs/state/context-lock.json")
CACHEABLE = ("frozen", "append-only", "revisable")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")


# --------------------------------------------------------------------- utils

def die(msg: str, code: int = 2) -> "None":
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def load_registry() -> dict:
    if not REGISTRY.exists():
        die(f"{REGISTRY} not found (run from the repo root of an HFD project).")
    try:
        return json.loads(REGISTRY.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        die(f"{REGISTRY} is not valid JSON: {e}")


def load_lock() -> dict:
    if LOCK.exists():
        try:
            return json.loads(LOCK.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"WARNING: {LOCK} unreadable, treating as empty", file=sys.stderr)
    return {"updated": None, "artifacts": {}, "packs": {}}


def save_lock(lock: dict) -> None:
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    lock["updated"] = datetime.now().isoformat(timespec="seconds")
    fd, tmp = tempfile.mkstemp(dir=str(LOCK.parent), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        json.dump(lock, f, indent=2, ensure_ascii=False, sort_keys=True)
    os.replace(tmp, LOCK)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tokens_of(data: bytes) -> int:
    """Cheap, dependency-free estimate: ~4 bytes per token."""
    return max(1, len(data) // 4)


def fold(text: str) -> str:
    """Accent- and case-insensitive fold, so 'Criterios de cancelacion'
    matches 'Criterios de cancelación' in the Spanish artifacts."""
    stripped = "".join(c for c in unicodedata.normalize("NFD", text)
                       if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", stripped).strip().lower()


def extract_section(text: str, query: str) -> "str | None":
    """Return one markdown section (heading + body until the next heading of
    the same or higher level). Matching is fold-insensitive and prefix-based."""
    lines = text.splitlines()
    want = fold(query)
    start = level = None
    for i, line in enumerate(lines):
        m = HEADING.match(line)
        if not m:
            continue
        title = fold(m.group(2))
        if start is None and (title.startswith(want) or want in title):
            start, level = i, len(m.group(1))
            continue
        if start is not None and len(m.group(1)) <= level:
            return "\n".join(lines[start:i]).rstrip()
    if start is None:
        return None
    return "\n".join(lines[start:]).rstrip()


# ----------------------------------------------------------------- resolution

def resolve(ref: str, reg: dict, params: dict, lock: dict) -> dict:
    """Turn a contract reference into a concrete, ordered pack item.

    A ref may be prefixed with "?" to mark it optional: the artifact is used
    when it exists (an analysis-only project has no constitution) and is
    reported as absent rather than as a warning when it does not."""
    optional = ref.startswith("?")
    ref = ref.lstrip("?")
    if ref.startswith("probe:"):
        name = ref[len("probe:"):]
        probe = reg.get("probes", {}).get(name)
        if not probe:
            return {"ref": ref, "kind": "probe", "tier": "probe", "status": "unknown",
                    "tokens": 0, "command": None,
                    "warning": f"probe '{name}' is not in the registry"}
        cmd, warning = probe["cmd"], None
        for p in probe.get("params", []):
            value = params.get(p)
            if value in (None, ""):
                warning = f"probe '{name}' needs --{p}; substitute it before running"
                value = f"<{p}>"
            cmd = cmd.replace("{" + p + "}", str(value))
        return {"ref": ref, "kind": "probe", "tier": "probe", "status": "ok",
                "tokens": probe.get("est_tokens", 300), "command": cmd,
                "path": None, "warning": warning}

    name, _, section = ref.partition("#")
    art = reg.get("artifacts", {}).get(name)
    if not art:
        return {"ref": ref, "kind": "unknown", "tier": "task", "status": "unknown",
                "tokens": 0, "command": None,
                "warning": f"'{name}' is not a registered artifact"}

    path = Path(art["path"])
    item = {"ref": ref, "kind": "section" if section else "file", "tier": art["tier"],
            "path": path.as_posix(), "owner": art.get("owner"), "section": section or None,
            "optional": optional,
            "command": f'python .hfd/scripts/context.py show "{ref}"', "warning": None}

    if not path.exists():
        item.update(status="optional-absent" if optional else "missing", tokens=0,
                    warning=None if optional else
                    f"{path} does not exist yet (produced by {art.get('owner', '?')})")
        return item

    raw = path.read_bytes()
    if section:
        body = extract_section(raw.decode("utf-8", "replace"), section)
        if body is None:
            item.update(status="optional-absent" if optional else "section-not-found",
                        tokens=0, warning=None if optional else
                        f"section '{section}' not found in {path} — load the file or fix the ref")
            return item
        payload = body.encode("utf-8")
    else:
        payload = raw

    item.update(status="ok", tokens=tokens_of(payload), sha256=sha(payload)[:16],
                bytes=len(payload))

    locked = lock.get("artifacts", {}).get(name)
    if locked and art["tier"] == "append-only" and not section:
        prev = locked.get("bytes", 0)
        if len(raw) > prev and sha(raw[:prev]) == locked.get("sha256"):
            item["cache_note"] = f"appended (+{tokens_of(raw[prev:])} tok, prefix intact)"
        elif sha(raw) != locked.get("sha256"):
            item["cache_note"] = "MUTATED mid-file — cache invalidated from here on"
    return item


def cache_digest(items: list, lock: dict) -> str:
    """Digest of the cacheable prefix only. For append-only artifacts this
    hashes the bytes that were already there at freeze time, because the
    appended tail does not invalidate the cached prefix."""
    h = hashlib.sha256()
    for it in items:
        if it["tier"] not in CACHEABLE or it["status"] != "ok" or not it.get("path"):
            continue
        raw = Path(it["path"]).read_bytes()
        locked = lock.get("artifacts", {}).get(it["ref"].split("#")[0], {})
        if it["tier"] == "append-only" and locked.get("bytes"):
            raw = raw[:locked["bytes"]]
        h.update(it["ref"].encode("utf-8") + b"\0" + sha(raw).encode("ascii") + b"\n")
    return h.hexdigest()


def build_pack(skill: str, reg: dict, params: dict, lock: dict) -> dict:
    contract = reg.get("contracts", {}).get(skill)
    if not contract:
        known = ", ".join(sorted(reg.get("contracts", {})))
        die(f"no context contract for '{skill}'. Known skills: {known}")

    order = {k: v["order"] for k, v in reg["tiers"].items()}
    items = [resolve(r, reg, params, lock) for r in contract.get("load", [])]
    items.sort(key=lambda i: order.get(i["tier"], 99))
    for n, it in enumerate(items, 1):
        it["seq"] = n

    digest = cache_digest(items, lock)
    recorded = lock.get("packs", {}).get(skill, {})
    if not recorded.get("prefix_hash"):
        cache_state, cache_note = "unknown", "first pack for this skill — nothing to compare against"
    elif recorded["prefix_hash"] == digest:
        cache_state = "hit-eligible"
        cache_note = f"cacheable prefix unchanged since {recorded.get('recorded', '?')[:10]}"
    else:
        cache_state = "miss"
        cache_note = "cacheable prefix changed since the last pack — first request this session pays full price"

    estimated = sum(i["tokens"] for i in items)
    warnings = list(dict.fromkeys(i["warning"] for i in items if i.get("warning")))
    budget = contract.get("budget_tokens", 0)
    if budget and estimated > budget:
        warnings.append(f"estimated {estimated} tok exceeds the {budget} tok budget — "
                        "load sections instead of whole files, or split the task")
    return {
        "skill": skill,
        "track": contract.get("track", "both"),
        "generated": str(date.today()),
        "budget_tokens": budget,
        "estimated_tokens": estimated,
        "cacheable_tokens": sum(i["tokens"] for i in items if i["tier"] in CACHEABLE),
        "cache_state": cache_state,
        "cache_note": cache_note,
        "cache_prefix_hash": digest,
        "load_order": items,
        "never_load": contract.get("never", []),
        "notes": contract.get("doc"),
        "warnings": warnings,
    }


# ------------------------------------------------------------------ commands

def cmd_pack(args, reg) -> int:
    lock = load_lock()
    params = {"slice": args.slice, "metric": args.metric, "path": args.path}
    pack = build_pack(args.skill, reg, params, lock)

    if not args.no_record:
        lock.setdefault("packs", {})[args.skill] = {
            "prefix_hash": pack["cache_prefix_hash"],
            "recorded": datetime.now().isoformat(timespec="seconds"),
        }
        save_lock(lock)

    if args.json:
        print(json.dumps(pack, indent=2, ensure_ascii=False))
        return 0

    if args.emit:
        return emit_pack(pack)

    pct = f"{100 * pack['estimated_tokens'] / pack['budget_tokens']:.0f}%" if pack["budget_tokens"] else "n/a"
    print(f"CONTEXT PACK — {pack['skill']}  (track: {pack['track']})")
    print("=" * 62)
    print(f"budget {pack['budget_tokens']} tok | estimated {pack['estimated_tokens']} tok ({pct} used) | "
          f"{pack['cacheable_tokens']} tok cacheable")
    print(f"cache: {pack['cache_state'].upper()} — {pack['cache_note']}")
    print("\nLOAD IN THIS ORDER (the order is what keeps the prefix cacheable):")
    if not pack["load_order"]:
        print("  (nothing — this skill runs on script output alone)")
    for it in pack["load_order"]:
        target = it.get("path") or ""
        if it.get("section"):
            target += f"  §{it['section']}"
        flag = "" if it["status"] == "ok" else f"  [{it['status']}]"
        if it.get("optional") and it["status"] != "ok":
            flag = "  [optional, not present]"
        print(f"  {it['seq']} [{it['tier']:<11}] {it['tokens']:>5} tok  {target or it['ref']}{flag}")
        if it.get("command"):
            print(f"      $ {it['command']}")
        if it.get("cache_note"):
            print(f"      ~ {it['cache_note']}")
    if pack["never_load"]:
        print(f"\nNEVER LOAD (contract violation, not a preference): {', '.join(pack['never_load'])}")
    if pack["notes"]:
        print(f"\nNote: {pack['notes']}")
    for w in pack["warnings"]:
        print(f"WARNING: {w}")
    return 0


def emit_pack(pack: dict) -> int:
    """Print the whole context as ONE deterministic blob, stable tiers first.
    Handing a single ordered string to the model is the most cache-friendly
    shape available in chat surfaces such as GitHub Copilot."""
    print(f"<!-- HFD context pack: {pack['skill']} | prefix {pack['cache_prefix_hash'][:16]} -->")
    for it in pack["load_order"]:
        if it["status"] != "ok" or not it.get("path"):
            continue
        text = Path(it["path"]).read_text(encoding="utf-8")
        if it.get("section"):
            text = extract_section(text, it["section"]) or ""
        print(f"\n===== [{it['tier']}] {it['ref']} =====")
        print(text.rstrip())
    probes = [i for i in pack["load_order"] if i["tier"] == "probe" and i.get("command")]
    if probes:
        print("\n===== [probe] run these and paste their output below =====")
        for it in probes:
            print(f"$ {it['command']}")
    return 0


def cmd_show(args, reg) -> int:
    name, _, section = args.ref.partition("#")
    art = reg.get("artifacts", {}).get(name)
    if not art:
        die(f"'{name}' is not a registered artifact. See .hfd/context.json.")
    path = Path(art["path"])
    if not path.exists():
        die(f"{path} does not exist yet (produced by {art.get('owner', '?')}).", 1)
    text = path.read_text(encoding="utf-8")
    if section:
        body = extract_section(text, section)
        if body is None:
            die(f"section '{section}' not found in {path}.", 1)
        text = body
    if args.tail:
        text = "\n".join(text.splitlines()[-args.tail:])
    print(text.rstrip())
    return 0


def scan_artifacts(reg: dict, lock: dict, cacheable_only: bool = False) -> list:
    """Inventory every registered artifact. Volatile files are excluded from
    lock/verify runs: they are rewritten by design, so drift there is not news."""
    rows = []
    for name, art in reg.get("artifacts", {}).items():
        if cacheable_only and art["tier"] not in CACHEABLE:
            continue
        path, locked = Path(art["path"]), lock.get("artifacts", {}).get(name)
        row = {"artifact": name, "path": path.as_posix(), "tier": art["tier"],
               "owner": art.get("owner"), "exists": path.exists()}
        if not path.exists():
            row["state"] = "absent" if not locked else "missing"
            row["tokens"] = 0
            rows.append(row)
            continue
        raw = path.read_bytes()
        row.update(bytes=len(raw), tokens=tokens_of(raw), sha256=sha(raw))
        if not locked:
            row["state"] = "unlocked"
        elif locked.get("sha256") == row["sha256"]:
            row["state"] = "unchanged"
        elif len(raw) >= locked.get("bytes", 0) and sha(raw[:locked["bytes"]]) == locked.get("sha256"):
            row["state"] = "appended"
            row["added_tokens"] = tokens_of(raw[locked["bytes"]:])
        else:
            row["state"] = "mutated"
        rows.append(row)
    order = {k: v["order"] for k, v in reg["tiers"].items()}
    rows.sort(key=lambda r: (order.get(r["tier"], 99), r["artifact"]))
    return rows


def cmd_freeze(args, reg) -> int:
    lock = load_lock()
    today, arts = str(date.today()), lock.setdefault("artifacts", {})
    frozen = 0
    for row in scan_artifacts(reg, lock, cacheable_only=True):
        if not row["exists"]:
            continue
        prev = arts.get(row["artifact"], {})
        changed = prev.get("sha256") != row["sha256"]
        arts[row["artifact"]] = {
            "path": row["path"], "tier": row["tier"], "sha256": row["sha256"],
            "bytes": row["bytes"], "tokens": row["tokens"],
            "first_seen": prev.get("first_seen", today),
            "last_change": today if changed else prev.get("last_change", today),
            "changes": prev.get("changes", 0) + (1 if changed and prev else 0),
        }
        frozen += 1
    save_lock(lock)
    print(f"Locked {frozen} artifact(s) in {LOCK}. "
          "Run `context.py verify` in CI to prove the planning docs stay append-only.")
    return 0


def cmd_verify(args, reg) -> int:
    lock = load_lock()
    rows = scan_artifacts(reg, lock, cacheable_only=True)
    verdicts, failures = [], []
    for row in rows:
        state, tier = row["state"], row["tier"]
        if state == "mutated" and tier in ("frozen", "append-only"):
            level, msg = "FAIL", ("edited mid-file — every cached prefix downstream is dead. "
                                  "Move the change to the END of the file.")
        elif state == "mutated":
            level, msg = "WARN", "revised in place (expected for this tier — cache re-warms next session)"
        elif state == "missing":
            level, msg = "FAIL", "was locked but no longer exists on disk"
        elif state == "appended":
            level, msg = "OK", f"appended +{row.get('added_tokens', 0)} tok, prefix intact"
        elif state == "unchanged":
            level, msg = "OK", "byte-identical since the lock — fully cacheable"
        elif state == "unlocked":
            level, msg = "NEW", "not in the lock yet — run `context.py freeze`"
        else:
            level, msg = "SKIP", "not created yet"
        verdicts.append({**row, "level": level, "message": msg})
        if level == "FAIL":
            failures.append(row["artifact"])

    if args.json:
        print(json.dumps({"date": str(date.today()), "failures": failures,
                          "artifacts": verdicts}, indent=2, ensure_ascii=False))
    else:
        print(f"CONTEXT CACHE HEALTH — {date.today()}")
        print("=" * 62)
        for v in verdicts:
            if v["level"] == "SKIP" and not args.all:
                continue
            print(f"  [{v['level']:<4}] {v['artifact']:<18} {v['tier']:<12} {v['message']}")
        cacheable = sum(v["tokens"] for v in verdicts
                        if v["tier"] in CACHEABLE and v["level"] == "OK")
        print(f"\n{cacheable} tok of cacheable context is intact across sessions.")
        if failures:
            print(f"BROKEN: {', '.join(failures)} — see .hfd/references/context-management.md")

    if args.update:
        return cmd_freeze(args, reg)
    return 1 if failures and not args.soft else 0


def cmd_budget(args, reg) -> int:
    lock = load_lock()
    rows = []
    for skill in reg.get("contracts", {}):
        pack = build_pack(skill, reg, {}, lock)
        rows.append({"skill": skill, "track": pack["track"], "budget": pack["budget_tokens"],
                     "estimated": pack["estimated_tokens"], "cacheable": pack["cacheable_tokens"],
                     "over": bool(pack["budget_tokens"]) and pack["estimated_tokens"] > pack["budget_tokens"]})
    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return 0
    print(f"{'skill':<20}{'track':<11}{'budget':>8}{'est.':>8}{'cacheable':>11}")
    print("-" * 58)
    for r in rows:
        flag = "  OVER" if r["over"] else ""
        print(f"{r['skill']:<20}{r['track']:<11}{r['budget']:>8}{r['estimated']:>8}"
              f"{r['cacheable']:>11}{flag}")
    print("\nEstimates cover declared context only; task files are unbounded by design.")
    return 0 if not any(r["over"] for r in rows) else 1


def cmd_stats(args, reg) -> int:
    lock = load_lock()
    rows = scan_artifacts(reg, lock)
    by_tier: dict = {}
    for r in rows:
        t = by_tier.setdefault(r["tier"], {"files": 0, "tokens": 0})
        if r["exists"]:
            t["files"] += 1
            t["tokens"] += r["tokens"]
    if args.json:
        print(json.dumps({"tiers": by_tier, "artifacts": rows}, indent=2, ensure_ascii=False))
        return 0
    print(f"CONTEXT INVENTORY — {date.today()}")
    print("=" * 62)
    order = {k: v["order"] for k, v in reg["tiers"].items()}
    for tier in sorted(by_tier, key=lambda t: order.get(t, 99)):
        info = reg["tiers"].get(tier, {})
        t = by_tier[tier]
        print(f"  {tier:<13} {t['files']:>2} file(s)  {t['tokens']:>6} tok   cache: {info.get('cache', '?')}")
    total = sum(t["tokens"] for t in by_tier.values())
    cacheable = sum(t["tokens"] for k, t in by_tier.items() if k in CACHEABLE)
    share = f"{100 * cacheable / total:.0f}%" if total else "n/a"
    print(f"\n  total {total} tok | cacheable {cacheable} tok ({share} of the corpus)")
    print("  Raise that share by appending instead of rewriting.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="HFD context manager")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("pack", help="ordered context manifest for one skill")
    p.add_argument("skill")
    p.add_argument("--slice", default=None, help="slice number for probes that need it")
    p.add_argument("--metric", default=None, help="metric name for ledger probes")
    p.add_argument("--path", default=None, help="data path for profiler probes")
    p.add_argument("--json", action="store_true")
    p.add_argument("--emit", action="store_true", help="print the assembled context, stable tiers first")
    p.add_argument("--no-record", action="store_true", help="do not update the pack hash in the lock")

    p = sub.add_parser("show", help="print one artifact or one of its sections")
    p.add_argument("ref", help='artifact name, or "artifact#Section"')
    p.add_argument("--tail", type=int, default=0, help="only the last N lines")

    p = sub.add_parser("freeze", help="record artifact hashes in docs/state/context-lock.json")

    p = sub.add_parser("verify", help="prove planning docs stayed append-only")
    p.add_argument("--json", action="store_true")
    p.add_argument("--all", action="store_true", help="include artifacts not created yet")
    p.add_argument("--soft", action="store_true", help="always exit 0")
    p.add_argument("--update", action="store_true", help="re-freeze after reporting")

    p = sub.add_parser("budget", help="estimated context cost per skill")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("stats", help="context inventory by cache tier")
    p.add_argument("--json", action="store_true")

    args = ap.parse_args()
    reg = load_registry()
    return {"pack": cmd_pack, "show": cmd_show, "freeze": cmd_freeze,
            "verify": cmd_verify, "budget": cmd_budget, "stats": cmd_stats}[args.cmd](args, reg)


if __name__ == "__main__":
    sys.exit(main())
