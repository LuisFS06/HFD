---
description: "Inspect and repair the project's context economy: what each skill loads and what it costs, which documents are still byte-stable enough to be…"
model: Claude Haiku 4.5
---

Load and follow the `hfd-context` skill (.github/skills/hfd-context/SKILL.md) exactly —
including its context contract: load what it declares, in the declared order,
and nothing else.

Before loading anything, run:

```
python .hfd/scripts/context.py pack hfd-context
```

Follow that manifest top to bottom. The order is what keeps the stable inputs
byte-identical between requests, which is what makes them cacheable.

User input: ${input}
