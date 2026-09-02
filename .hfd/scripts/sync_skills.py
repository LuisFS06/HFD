#!/usr/bin/env python3
"""Mirror HFD skills to the GitHub Copilot surface.

Claude Code and GitHub Copilot consume the same Agent Skills format
(SKILL.md); they just look in different directories. The canonical copy
lives in .claude/skills/. This script mirrors every hfd-* skill to
.github/skills/ and regenerates the one-line .github/prompts/*.prompt.md
wrappers that expose them as Copilot slash commands, pinning the model
declared in each skill's `copilot-model:` frontmatter key.

Generating the prompts (instead of hand-writing them) means a new skill is
one file away from working on both platforms, and the model pinning can
never drift from the skill it belongs to.

Usage:
    python .hfd/scripts/sync_skills.py           # .claude -> .github
    python .hfd/scripts/sync_skills.py --check   # report drift, exit 1 if any
"""

import argparse
import filecmp
import re
import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SRC = Path(".claude/skills")
DST = Path(".github/skills")
PROMPTS = Path(".github/prompts")
DEFAULT_MODEL = "Claude Sonnet 4.6"

PROMPT_TEMPLATE = """---
description: "{description}"
model: {model}
---

Load and follow the `{name}` skill (.github/skills/{name}/SKILL.md) exactly —
including its context contract: load what it declares, in the declared order,
and nothing else.

Before loading anything, run:

```
python .hfd/scripts/context.py pack {name}
```

Follow that manifest top to bottom. The order is what keeps the stable inputs
byte-identical between requests, which is what makes them cacheable.

User input: ${{input}}
"""


def parse_frontmatter(text: str) -> dict:
    """Minimal YAML frontmatter reader — enough for `key: value` and folded
    `key: >` blocks, with no third-party dependency."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    data, key = {}, None
    for line in text[3:end].splitlines():
        if not line.strip():
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m and not line.startswith((" ", "\t")):
            key, value = m.group(1), m.group(2).strip()
            data[key] = "" if value in (">", "|", ">-", "|-") else value.strip("\"'")
        elif key:
            data[key] = (data[key] + " " + line.strip()).strip()
    return data


def one_line(text: str, limit: int = 150) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    sentence = re.split(r"(?<=\.)\s", text)[0] if text else ""
    if len(sentence) > limit:
        sentence = sentence[: limit - 1].rsplit(" ", 1)[0] + "…"
    return sentence.replace('"', "'")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report drift without writing")
    args = ap.parse_args()

    if not SRC.is_dir():
        print(f"ERROR: {SRC} not found (run from the repo root).", file=sys.stderr)
        return 2

    skills = sorted(p for p in SRC.iterdir() if p.is_dir() and p.name.startswith("hfd-"))
    drift: list[str] = []

    def sync_file(source: Path, target: Path, content: "str | None" = None) -> None:
        if content is None:
            same = target.exists() and filecmp.cmp(source, target, shallow=False)
        else:
            same = target.exists() and target.read_text(encoding="utf-8") == content
        if same:
            return
        drift.append(target.as_posix())
        if args.check:
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        if content is None:
            shutil.copy2(source, target)
        else:
            target.write_text(content, encoding="utf-8", newline="\n")

    for skill in skills:
        for f in sorted(skill.rglob("*")):
            if f.is_file():
                sync_file(f, DST / skill.name / f.relative_to(skill))

        meta = parse_frontmatter((skill / "SKILL.md").read_text(encoding="utf-8"))
        prompt = PROMPT_TEMPLATE.format(
            name=skill.name,
            model=meta.get("copilot-model", DEFAULT_MODEL),
            description=one_line(meta.get("description", skill.name)),
        )
        sync_file(skill / "SKILL.md", PROMPTS / f"{skill.name}.prompt.md", content=prompt)

    live = {s.name for s in skills}
    for stale in sorted(p for p in DST.glob("hfd-*") if p.is_dir() and p.name not in live):
        drift.append(f"{stale.as_posix()} (stale)")
        if not args.check:
            shutil.rmtree(stale)
    for stale in sorted(PROMPTS.glob("hfd-*.prompt.md")):
        if stale.name[: -len(".prompt.md")] not in live:
            drift.append(f"{stale.as_posix()} (stale)")
            if not args.check:
                stale.unlink()

    if args.check:
        if drift:
            print("DRIFT (run: python .hfd/scripts/sync_skills.py):")
            for d in drift:
                print(f"  {d}")
            return 1
        print(f"In sync: {len(skills)} skills mirrored, {len(skills)} prompts generated.")
        return 0

    print(f"Synced {len(skills)} skills and their Copilot prompts, {len(drift)} file(s) updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
