---
description: "Blind factual exploration of available data and models WITHOUT knowing the proposed hypothesis — produces docs/blind-research.md (coverage, quality,…"
model: GPT-5 mini
---

Load and follow the `hfd-research` skill (.github/skills/hfd-research/SKILL.md) exactly —
including its context contract: load what it declares, in the declared order,
and nothing else.

Before loading anything, run:

```
python .hfd/scripts/context.py pack hfd-research
```

Follow that manifest top to bottom. The order is what keeps the stable inputs
byte-identical between requests, which is what makes them cacheable.

User input: ${input}
