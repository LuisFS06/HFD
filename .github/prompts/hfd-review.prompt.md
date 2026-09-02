---
description: "Pre-commit gate for an HFD project: run the deterministic verification pass (structure, context cache health, state consistency, docs discipline,…"
model: GPT-5 mini
---

Load and follow the `hfd-review` skill (.github/skills/hfd-review/SKILL.md) exactly —
including its context contract: load what it declares, in the declared order,
and nothing else.

Before loading anything, run:

```
python .hfd/scripts/context.py pack hfd-review
```

Follow that manifest top to bottom. The order is what keeps the stable inputs
byte-identical between requests, which is what makes them cacheable.

User input: ${input}
