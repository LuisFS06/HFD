#!/usr/bin/env python3
"""Mirror HFD skills between .claude/skills/ and .github/skills/.

Both Claude Code and GitHub Copilot consume the same Agent Skills format
(SKILL.md); they just look in different directories. The canonical copy
lives in .claude/skills/ — this script mirrors the hfd-* skills to
.github/skills/ so Copilot users get identical behavior.

Usage:
    python .hfd/scripts/sync_skills.py           # .claude -> .github
    python .hfd/scripts/sync_skills.py --check   # report drift, exit 1 if any
"""

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SRC = Path(".claude/skills")
DST = Path(".github/skills")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report drift without copying")
    args = ap.parse_args()

    if not SRC.is_dir():
        print(f"ERROR: {SRC} not found (run from the repo root).", file=sys.stderr)
        return 2

    skills = sorted(p for p in SRC.iterdir() if p.is_dir() and p.name.startswith("hfd-"))
    drift = []
    for skill in skills:
        target = DST / skill.name
        for f in sorted(skill.rglob("*")):
            if not f.is_file():
                continue
            t = target / f.relative_to(skill)
            if not t.exists() or not filecmp.cmp(f, t, shallow=False):
                drift.append(str(t))
                if not args.check:
                    t.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, t)
    # remove skills in DST that no longer exist in SRC
    if DST.is_dir():
        for stale in sorted(p for p in DST.iterdir()
                            if p.is_dir() and p.name.startswith("hfd-")
                            and not (SRC / p.name).exists()):
            drift.append(f"{stale} (stale)")
            if not args.check:
                shutil.rmtree(stale)

    if args.check:
        if drift:
            print("DRIFT (run: python .hfd/scripts/sync_skills.py):")
            for d in drift:
                print(f"  {d}")
            return 1
        print(f"In sync: {len(skills)} skills mirrored.")
        return 0

    print(f"Synced {len(skills)} skills, {len(drift)} file(s) updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
