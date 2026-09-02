---
description: "Incremental experiment loop for a project that already has a baseline: add a feature, tweak hyperparameters, try a data-cleaning change, test a…"
model: GPT-5.4 mini
---

Load and follow the `hfd-experiment` skill (.github/skills/hfd-experiment/SKILL.md) exactly —
including its context contract: load what it declares, in the declared order,
and nothing else.

Before loading anything, run:

```
python .hfd/scripts/context.py pack hfd-experiment
```

Follow that manifest top to bottom. The order is what keeps the stable inputs
byte-identical between requests, which is what makes them cacheable.

User input: ${input}
