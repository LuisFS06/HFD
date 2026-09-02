---
description: "Instant HFD project dashboard: which artifacts exist, slice/gate status, experiment ledger best metrics, and the recommended next command."
model: Claude Haiku 4.5
---

Load and follow the `hfd-status` skill (.github/skills/hfd-status/SKILL.md) exactly —
including its context contract: load what it declares, in the declared order,
and nothing else.

Before loading anything, run:

```
python .hfd/scripts/context.py pack hfd-status
```

Follow that manifest top to bottom. The order is what keeps the stable inputs
byte-identical between requests, which is what makes them cacheable.

User input: ${input}
