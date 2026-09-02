---
description: "Decompose the ML project into vertical slices — each a self-contained experiment with a quantitative pass/fail gate — producing an immutable…"
model: GPT-5 mini
---

Load and follow the `hfd-slices` skill (.github/skills/hfd-slices/SKILL.md) exactly —
including its context contract: load what it declares, in the declared order,
and nothing else.

Before loading anything, run:

```
python .hfd/scripts/context.py pack hfd-slices
```

Follow that manifest top to bottom. The order is what keeps the stable inputs
byte-identical between requests, which is what makes them cacheable.

User input: ${input}
