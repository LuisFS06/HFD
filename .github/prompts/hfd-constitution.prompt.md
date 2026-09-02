---
description: "Surgical revision of docs/constitution.md — new data source discovered, success criteria changed, scope narrowed, glossary reconciliation after a…"
model: Claude Haiku 4.5
---

Load and follow the `hfd-constitution` skill (.github/skills/hfd-constitution/SKILL.md) exactly —
including its context contract: load what it declares, in the declared order,
and nothing else.

Before loading anything, run:

```
python .hfd/scripts/context.py pack hfd-constitution
```

Follow that manifest top to bottom. The order is what keeps the stable inputs
byte-identical between requests, which is what makes them cacheable.

User input: ${input}
