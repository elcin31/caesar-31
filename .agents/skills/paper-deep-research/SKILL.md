---
name: paper-deep-research
description: Use when Codex needs to investigate a paper topic, survey recent or foundational literature, collect sources, find research gaps, or prepare evidence for Related Work, Introduction, Background, or thesis writing. Trigger for requests mentioning deep research, 文献调研, related work, literature survey, research gap, citation candidates, or using dzhng/deep-research for academic writing.
---

# Paper Deep Research

Use this skill to build an evidence base before drafting academic text.

## Source policy

- Prefer primary sources: papers, official proceedings, arXiv pages, DOI pages, project pages, datasets, and official documentation.
- Use Zotero or an existing `.bib` file when available; otherwise return citation candidates marked for verification.
- Do not invent citations, venues, years, metrics, ablations, or limitations.
- Mark unsupported claims as `[CITATION NEEDED]`.
- For fast-moving topics, browse or use a configured research tool before answering.

## Workflow

1. Restate the research question in one sentence.
2. List missing inputs before running research: target venue, year range, required citation style, seed papers, exclusion criteria, and whether Chinese/English output is needed.
3. If `dzhng/deep-research` is installed or available, use it as the evidence collector:
   - Set a focused query rather than a broad paper title dump.
   - Use low breadth/depth for quick checks and higher breadth/depth for survey sections.
   - Save the generated report path and cite it as intermediate evidence, not as a final scholarly source.
4. If `deep-research` is unavailable, use web search, Zotero, local PDFs, or BibTeX directly.
5. Produce a research brief with:
   - Key clusters of work.
   - Representative papers with source links or BibTeX keys.
   - Claims supported by each cluster.
   - Open gaps and how the user's paper can position itself.
   - A list of unresolved facts that still need user confirmation.

## `deep-research` integration notes

`dzhng/deep-research` is a Node/TypeScript research agent that uses Firecrawl search/scrape and an LLM to recursively generate learnings and a final Markdown report. It is useful as a first-pass collector, but its output must be checked against original sources before appearing in a paper.

If the user asks to install or run it, check for:

- Node.js and package manager availability.
- `FIRECRAWL_KEY` or equivalent Firecrawl configuration.
- LLM API key and model configuration.
- A target output directory inside the workspace.

Ask for missing credentials or install approval when needed.
