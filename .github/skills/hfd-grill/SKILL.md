---
name: hfd-grill
description: >
  Socratic grilling session that builds a falsifiable ML hypothesis:
  challenges terminology, cross-references claims against real data, and
  produces docs/constitution.md + docs/hypothesis-doc.md. Use when starting
  a new ML project, proposing a new hypothesis, stress-testing an existing
  one, or amending a hypothesis after new findings.
argument-hint: "[business problem + data locations] | amend <what changed>"
---

Interview the user relentlessly about their ML hypothesis until shared
understanding is reached. One question at a time — wait for each answer.
For every question, offer your recommended answer. If a question can be
answered by exploring available data or docs, explore instead of asking
(use `python .hfd/scripts/profile_data.py <path>` for
quick factual profiles rather than writing ad-hoc pandas).

## Modes

- **Full session** (default): new hypothesis from scratch.
- **Amend** (`/hfd-grill amend ...`): incremental. Read the executive
  summaries of docs/constitution.md and docs/hypothesis-doc.md, grill ONLY
  the aspect that changed, and record the outcome as: (a) glossary/criteria
  edits via /hfd-constitution semantics, and (b) a dated `## Enmienda
  {fecha}` section appended at the END of docs/hypothesis-doc.md. Never
  rewrite the existing body — appends keep the doc cache-stable.

## During the session

- **Challenge against the glossary**: if the user's term conflicts with
  docs/constitution.md, call it out immediately and force a resolution.
- **Sharpen fuzzy language**: "good performance" becomes "AUC >= 0.85 on
  the holdout set" — propose the precise form.
- **Stress-test with concrete scenarios**: invent edge cases that force
  precise boundaries ("zero transactions in 90 days but logged in
  yesterday — churned or active?").
- **Cross-reference with data**: verify domain claims against actual data;
  surface contradictions as you find them.
- **Update docs/constitution.md inline** as each term resolves — glossary
  format from the template. Don't batch. Create the file from
  `.hfd/templates/constitution-template.md` the first
  time you have content.
- **Cancellation criteria — offer sparingly.** Only when all three hold:
  hard to reverse, surprising without context, result of a real trade-off.

## Execution boundaries

- MAY read files, data dictionaries, run read-only exploratory queries.
- MUST NOT train models, build features, or modify data.

## Minimum coverage before offering to conclude

- [ ] Problem context (business motivation)
- [ ] ≥1 verifiable hypothesis with a quantitative gate
- [ ] ≥1 cancellation criterion (or explicit discussion of why none apply)
- [ ] ≥3 glossary terms resolved
- [ ] Data sources identified and cross-referenced

The session ends only when the user confirms. Then produce
docs/hypothesis-doc.md from
`.hfd/templates/hypothesis-template.md` (read the
template only at this point — not at session start). Both documents start
with `## Resumen ejecutivo` describing the PLAN (hypothesis, gates, risks) —
never live status.

## Re-run semantics

If docs/hypothesis-doc.md exists and the user wants a new full session,
ask: replace, or numbered variant (hypothesis-doc-2.md)? Never overwrite
silently. If docs/constitution.md exists, read it as context and challenge
against it — do not recreate it.

## Context contract

Load: docs/constitution.md (if exists), user conversation, data
exploration output. Templates only at write time. Do NOT load
blind-research, design-decisions, prd-slices, or state files.
