---
description: "Bootstrap the canonical HFD ML project structure (src/, data/, docs/, tests/, placeholders, .gitignore, requirements.txt)."
model: Claude Haiku 4.5
---

Load and follow the `hfd-init` skill (.github/skills/hfd-init/SKILL.md) exactly —
including its context contract: load what it declares, in the declared order,
and nothing else.

Before loading anything, run:

```
python .hfd/scripts/context.py pack hfd-init
```

Follow that manifest top to bottom. The order is what keeps the stable inputs
byte-identical between requests, which is what makes them cacheable.

User input: ${input}
