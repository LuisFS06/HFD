---
description: "Execute ONE slice from the plan: implement its steps with script-managed checkpoints, evaluate the quantitative gate, record the result, and…"
model: GPT-5.4 mini
---

Load and follow the `hfd-run` skill (.github/skills/hfd-run/SKILL.md) exactly —
including its context contract: load what it declares, in the declared order,
and nothing else.

Before loading anything, run:

```
python .hfd/scripts/context.py pack hfd-run
```

Follow that manifest top to bottom. The order is what keeps the stable inputs
byte-identical between requests, which is what makes them cacheable.

User input: ${input}
