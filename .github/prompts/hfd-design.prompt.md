---
description: "Technical design decisions for the ML project — data strategy, model architecture (via Socratic grilling), risk/cancellation alignment,…"
model: Claude Sonnet 4.6
---

Load and follow the `hfd-design` skill (.github/skills/hfd-design/SKILL.md) exactly —
including its context contract: load what it declares, in the declared order,
and nothing else.

Before loading anything, run:

```
python .hfd/scripts/context.py pack hfd-design
```

Follow that manifest top to bottom. The order is what keeps the stable inputs
byte-identical between requests, which is what makes them cacheable.

User input: ${input}
