---
description: "Answer ONE data question reproducibly: sharpen it into a computable form, agree the metric definition, compute it in a script (not a throwaway…"
model: GPT-5.4 mini
---

Load and follow the `hfd-analyze` skill (.github/skills/hfd-analyze/SKILL.md) exactly —
including its context contract: load what it declares, in the declared order,
and nothing else.

Before loading anything, run:

```
python .hfd/scripts/context.py pack hfd-analyze
```

Follow that manifest top to bottom. The order is what keeps the stable inputs
byte-identical between requests, which is what makes them cacheable.

User input: ${input}
