---
description: "Execute a single slice — implement, evaluate gate, checkpoint progress"
agent: hfd.executor
---

Execute the next pending slice from docs/prd-slices.md. If a slice is already
in progress, resume from the last checkpoint. Implement each step, update
checkpoints, evaluate the gate, and report.

Context the user should provide:
- Whether anything changed since the slice was planned
- Whether to verify existing artifacts before starting
- Time constraints for this session
- Any issues from the previous session (if resuming)
