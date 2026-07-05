#!/usr/bin/env python3
"""Extract a single slice section from docs/prd-slices.md.

Lets the executor load ONE slice into context instead of the whole plan.

Usage:
    python get_slice.py 3            # print '## Slice 3: ...' section only
    python get_slice.py --list       # list slice numbers and titles
"""

import argparse
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PLAN = Path("docs/prd-slices.md")
HEADER = re.compile(r"^##\s+Slice\s+(\d+)\s*[:.]\s*(.*)$", re.MULTILINE)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("n", nargs="?")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    if not PLAN.exists():
        print(f"ERROR: {PLAN} not found. Run /hfd-slices first.", file=sys.stderr)
        return 1
    text = PLAN.read_text(encoding="utf-8")
    matches = list(HEADER.finditer(text))
    if args.list or not args.n:
        for m in matches:
            print(f"Slice {m.group(1)}: {m.group(2)}")
        return 0

    for i, m in enumerate(matches):
        if m.group(1) == args.n:
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            # stop at the next top-level section if it comes before the next slice
            tail = re.search(r"^##\s+(?!Slice)", text[m.end():end], re.MULTILINE)
            stop = m.end() + tail.start() if tail else end
            print(text[m.start():stop].rstrip())
            return 0
    print(f"ERROR: Slice {args.n} not found. Use --list to see available slices.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
