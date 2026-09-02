---
description: "Socratic grilling session that builds a falsifiable ML hypothesis: challenges terminology, cross-references claims against real data, and produces…"
model: Claude Sonnet 4.6
---

Load and follow the `hfd-grill` skill (.github/skills/hfd-grill/SKILL.md) exactly —
including its context contract: load what it declares, in the declared order,
and nothing else.

Before loading anything, run:

```
python .hfd/scripts/context.py pack hfd-grill
```

Follow that manifest top to bottom. The order is what keeps the stable inputs
byte-identical between requests, which is what makes them cacheable.

User input: ${input}
