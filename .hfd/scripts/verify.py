#!/usr/bin/env python3
"""Deterministic verification pass for an HFD project.

Runs every check the harness can make without a model in the loop and prints
one verdict table. Used by /hfd-review before a commit, by /hfd-feature to
close a unit of work, and by CI.

Checks: project structure, context cache health (planning docs still
append-only), state consistency (declared artifacts exist, nothing closed
unverified), document discipline, linters, tests.

Usage:
    python verify.py                # everything available
    python verify.py --quick        # skip tests and linters
    python verify.py --json
"""

import argparse
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SCRIPTS = Path(".hfd/scripts")
DOCS = Path("docs")
STATE = DOCS / "state"
PLANNING = ["constitution.md", "hypothesis-doc.md", "blind-research.md",
            "design-decisions.md", "prd-slices.md"]
# Live status inside the immutable plan is what the state split exists to prevent.
FORBIDDEN_IN_PLAN = ["## Estado actual", "## Progreso", "Checkpoint:", "Estado del slice"]


def run(cmd: list[str], timeout: int = 900) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, (proc.stdout + proc.stderr).strip()
    except subprocess.TimeoutExpired:
        return 124, f"timed out after {timeout}s: {' '.join(cmd)}"
    except OSError as e:
        return 127, str(e)


def check_structure() -> dict:
    missing = [d for d in ("src", "docs", "tests") if not Path(d).is_dir()]
    if missing:
        return {"level": "FAIL", "detail": f"missing canonical dirs: {', '.join(missing)} — run /hfd-init"}
    stray = [p.as_posix() for p in Path(".").glob("*.py")
             if p.name not in ("main.py", "setup.py", "conftest.py")]
    if stray:
        return {"level": "WARN", "detail": f"loose scripts at the repo root: {', '.join(stray[:5])}"}
    return {"level": "PASS", "detail": "canonical tree present"}


def check_context() -> dict:
    script = SCRIPTS / "context.py"
    if not script.exists():
        return {"level": "SKIP", "detail": "context.py not present"}
    code, out = run([sys.executable, str(script), "verify", "--json"])
    try:
        payload = json.loads(out)
    except json.JSONDecodeError:
        return {"level": "WARN", "detail": f"context verify unreadable: {out[:200]}"}
    broken = payload.get("failures", [])
    if broken:
        return {"level": "FAIL",
                "detail": f"planning docs edited mid-file: {', '.join(broken)} — "
                          "move changes to the END of the file to keep the cache warm"}
    unlocked = [a["artifact"] for a in payload.get("artifacts", []) if a["level"] == "NEW"]
    if unlocked:
        return {"level": "WARN", "detail": f"not in the lock yet: {', '.join(unlocked)} — run `context.py freeze`"}
    return {"level": "PASS", "detail": "cacheable context intact"}


def check_state() -> dict:
    problems = []
    slices_file = STATE / "slices.json"
    if slices_file.exists():
        try:
            data = json.loads(slices_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"level": "FAIL", "detail": f"{slices_file} is corrupt"}
        for num, sl in data.get("slices", {}).items():
            for step_n, step in sl.get("steps", {}).items():
                art = step.get("artifact")
                if step.get("status") == "done" and art and not Path(art).exists():
                    problems.append(f"slice {num} step {step_n} declares missing {art}")
    worklog = STATE / "worklog.jsonl"
    if worklog.exists():
        code, out = run([sys.executable, str(SCRIPTS / "worklog.py"), "stats", "--json"])
        if code == 0:
            try:
                stats = json.loads(out)
                for wid in stats.get("closed_unverified", []):
                    problems.append(f"{wid} closed without a passing verification")
            except json.JSONDecodeError:
                pass
        code, out = run([sys.executable, str(SCRIPTS / "worklog.py"), "show",
                         "--last", "500", "--json"])
        if code == 0:
            try:
                for unit in json.loads(out):
                    if unit.get("status") != "done":
                        continue
                    for art in unit.get("artifacts", []):
                        if not Path(art).exists():
                            problems.append(f"{unit['id']} declares missing artifact {art}")
            except json.JSONDecodeError:
                pass
    if problems:
        return {"level": "FAIL", "detail": "; ".join(problems[:6])}
    return {"level": "PASS", "detail": "state matches disk"}


def check_docs() -> dict:
    issues = []
    for name in PLANNING:
        path = DOCS / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "## Resumen ejecutivo" not in text:
            issues.append(f"{name} has no '## Resumen ejecutivo'")
        if name == "prd-slices.md":
            hits = [m for m in FORBIDDEN_IN_PLAN if m in text]
            if hits:
                issues.append(f"prd-slices.md carries live status ({hits[0]}) — that belongs in docs/state/")
    if not any((DOCS / n).exists() for n in PLANNING):
        return {"level": "SKIP", "detail": "no planning docs yet"}
    if issues:
        return {"level": "WARN", "detail": "; ".join(issues[:4])}
    return {"level": "PASS", "detail": "planning docs well formed"}


def check_lint() -> dict:
    targets = [d for d in ("src", "tests") if Path(d).is_dir()]
    if not targets:
        return {"level": "SKIP", "detail": "nothing to lint"}
    if shutil.which("ruff"):
        code, out = run(["ruff", "check", *targets])
        tool = "ruff"
    elif shutil.which("flake8"):
        code, out = run(["flake8", *targets])
        tool = "flake8"
    else:
        return {"level": "SKIP", "detail": "no linter installed (pip install ruff)"}
    if code == 0:
        return {"level": "PASS", "detail": f"{tool} clean"}
    return {"level": "FAIL", "detail": f"{tool}: " + " | ".join(out.splitlines()[:5])}


def check_tests() -> dict:
    if not Path("tests").is_dir():
        return {"level": "SKIP", "detail": "no tests/ directory"}
    cases = [p for p in Path("tests").rglob("test_*.py")]
    if not cases:
        return {"level": "WARN", "detail": "tests/ exists but holds no test_*.py"}
    code, out = run([sys.executable, "-m", "pytest", "-q", "tests"])
    if code == 0:
        tail = out.splitlines()[-1] if out else "ok"
        return {"level": "PASS", "detail": tail}
    if code == 5:
        return {"level": "WARN", "detail": "pytest collected no tests"}
    return {"level": "FAIL", "detail": " | ".join(out.splitlines()[-5:])}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="skip linters and tests")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    checks = [("structure", check_structure), ("context", check_context),
              ("state", check_state), ("docs", check_docs)]
    if not args.quick:
        checks += [("lint", check_lint), ("tests", check_tests)]

    results = {name: fn() for name, fn in checks}
    failures = [n for n, r in results.items() if r["level"] == "FAIL"]

    if args.json:
        print(json.dumps({"date": str(date.today()), "failures": failures,
                          "checks": results}, indent=2, ensure_ascii=False))
    else:
        print(f"HFD VERIFY — {date.today()}")
        print("=" * 62)
        for name, r in results.items():
            print(f"  [{r['level']:<4}] {name:<10} {r['detail']}")
        print("\n" + ("BLOCKED: fix the FAIL rows before committing."
                      if failures else "Ready to commit."))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
