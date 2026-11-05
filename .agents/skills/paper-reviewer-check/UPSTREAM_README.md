# Codex Custom Skills

A focused collection of six personal Codex skills for academic-paper workflows.

## Included skills

| Skill | Purpose |
| --- | --- |
| `paper-academic-writing` | Draft, translate, revise, shorten, expand, and polish academic prose without inventing evidence. |
| `paper-deep-research` | Collect and verify scholarly evidence, map research clusters, and identify positioning gaps. |
| `paper-experiment-writing` | Turn real tables, logs, and metrics into defensible experiment analyses and captions. |
| `paper-literature-synthesis` | Build citation-backed related-work sections, taxonomies, and comparison matrices. |
| `paper-reviewer-check` | Run a reviewer-facing pre-submission audit for evidence, clarity, reproducibility, and formatting risks. |
| `translate-paper-pdf` | Translate English research-paper PDFs into Chinese while preserving the page layout. |

`major-format` is deliberately not included in this repository.

## Installation

Copy one or more directories under `skills/` into a Codex skill directory, keeping
each directory's `SKILL.md` at its root. For example:

```text
~/.codex/skills/paper-academic-writing/SKILL.md
```

The paper skills can also be placed in `~/.agents/skills/` when that is your shared
instruction location.

## Scope

These skills are workflow instructions. They do not contain credentials, datasets,
or proprietary application source code.
