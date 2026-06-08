---
description: "Decompose ML project into vertical slices with quantitative gates"
agent: hfd.slicearchitect
---

Decompose this ML project into vertical slices. Each slice tests one
aspect of the hypothesis with a pass/fail gate. Order by information
value — kill the project early if it's going to die.

Context the user should provide:
- What they need to know first (highest uncertainty)
- Maximum number of slices they want
- Whether they want to validate assumptions before building
- Time constraints ("I have 2 weeks for the whole project")
