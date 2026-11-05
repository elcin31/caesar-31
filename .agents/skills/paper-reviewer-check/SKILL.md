---
name: paper-reviewer-check
description: Use when Codex needs to review an academic paper draft, thesis chapter, rebuttal, experiment section, or submission package for reviewer-facing weaknesses, missing citations, unsupported claims, contribution clarity, reproducibility, formatting risks, or acceptance readiness. Trigger for reviewer check, 审稿人视角, paper review, submission checklist, rebuttal risk, or camera-ready check.
---

# Paper Reviewer Check

Use this skill as a critical pre-submission pass.

## Review stance

Prioritize issues that could affect acceptance:

- unclear problem or contribution,
- unsupported novelty,
- missing or unfair baselines,
- weak ablations,
- unverified citations,
- inconsistent notation,
- dataset or metric ambiguity,
- claims not supported by experiments,
- reproducibility gaps,
- venue formatting or anonymity risks.

## Workflow

1. Identify the target venue or thesis context.
2. Inspect the relevant draft files, figures, tables, and bibliography when available.
3. List findings by severity:
   - Critical: likely rejection or correctness risk.
   - Major: weakens evidence or clarity.
   - Minor: style, grammar, or formatting.
4. For each finding, include the exact file/section/line if available, why it matters, and a concrete fix.
5. End with missing information needed from the user.

## Output rules

- Findings first, summary second.
- Be direct but constructive.
- Do not rewrite the whole paper unless asked.
- Do not invent reviewer objections unsupported by the draft.
