---
description: "Incremental development loop for one unit of work that has no metric gate: a pipeline feature, a new data source, a bug fix, a refactor, a scheduled…"
model: GPT-5.4 mini
---

Load and follow the `hfd-feature` skill (.github/skills/hfd-feature/SKILL.md) exactly —
including its context contract: load what it declares, in the declared order,
and nothing else.

Before loading anything, run:

```
python .hfd/scripts/context.py pack hfd-feature
```

Follow that manifest top to bottom. The order is what keeps the stable inputs
byte-identical between requests, which is what makes them cacheable.

User input: ${input}
