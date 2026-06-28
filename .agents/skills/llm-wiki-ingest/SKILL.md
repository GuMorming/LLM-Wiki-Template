---
name: llm-wiki-ingest
description: Ingest raw sources into this repository-local LLM Research Wiki. Use when the user asks to "ingest" a paper, PDF, LaTeX manuscript, own-work folder, review, dataset, codebase notes, or any source under raw/ into wiki pages; also use for follow-up ingest maintenance such as updating source notes, concepts, methods, systems, claims, experiments, index.md, and log.md after reading raw materials.
---

# LLM Wiki Ingest

## Overview

Use this skill to turn immutable raw research materials into structured wiki
knowledge for this repository. Treat repository `AGENTS.md` as the governing
schema; this skill provides the repeatable ingest procedure, helper scripts, and
validation steps.

## Required First Steps

1. Read `AGENTS.md` in the repository root before doing any ingest work.
2. Read `index.md` to understand existing clusters and avoid duplicate pages.
3. Resolve the requested source path. Prefer:
   `python3 .agents/skills/llm-wiki-ingest/scripts/resolve_source.py "<user path>"`.
4. If the resolved source is not under `raw/`, ask the user to move it into
   `raw/` or explicitly authorize the different source path.
5. Decide the ingest type:
   - `raw/own works/...` -> own-work ingest.
   - other `raw/...` papers, PDFs, notes, datasets, reviews, or code docs ->
     external-source ingest unless the source clearly belongs to the repository owner.

## Source Reading

Read the source sufficiently to extract actual claims, mechanisms, evidence,
limitations, and links to the repository owner's projects.

- For PDFs, use the PDF skill if available. Extract text and verify key
  figures/tables visually when numbers or claims depend on them.
- For LaTeX projects, inspect the main `.tex`, included section files,
  figures/tables as needed, and `references.bib` when citation status matters.
- For codebases or datasets, read README/spec files and any evaluation or schema documents before writing wiki pages.
- Preserve confidentiality for under-review own work. Do not disclose private manuscript content outside this wiki unless the user asks for an output.

Before editing wiki files, summarize the source to the user in a short takeaway block: problem, method/system, key claims, evidence, limitations, and relevance to existing wiki clusters.

## Wiki Update Procedure

Use `references/ingest-checklist.md` as the task checklist during an ingest.
Write only in `wiki/`, `index.md`, `log.md`, and other schema/output locations
authorized by `AGENTS.md`. Do not modify files under `raw/`.

Minimum durable output for a normal ingest:

- one source note in `wiki/source-notes/`,
- updated `index.md`,
- updated `log.md`,
- updated or newly created concept/method/system/benchmark/dataset/project pages touched by the source.

For own-work ingests, also create or update claim and experiment pages for main paper claims when the evidence is explicit. For external sources, create claim or experiment pages only when the claim/result is important enough to reuse.

## Traceability Rules

- Never invent citations, venues, paper status, numbers, baselines, or results.
- Attach exact section, figure, table, or page references when recording numeric
  claims.
- Clearly label agent inferences.
- Use relative Markdown links inside wiki pages.
- Use lowercase-kebab-case filenames for wiki pages.
- Keep raw filenames unchanged.
- If a useful recurring page is missing, create a stub only when it is likely to
  recur; otherwise log `PAGE NEEDED`.

## Validation

Run these checks before finishing:

```bash
python3 .agents/skills/llm-wiki-ingest/scripts/audit_wiki.py
python3 .agents/skills/llm-wiki-ingest/scripts/check_raw_clean.py
```

Also inspect `git status --short`. Do not stage or commit unless the user asks.
If temporary extraction files were created, keep them under ignored `tmp/` or remove them only with appropriate permission.

## Bundled Resources

- `scripts/resolve_source.py` resolves requested raw paths and catches common
  path typos such as `raw/artical` vs `raw/articles`.
- `scripts/audit_wiki.py` checks wiki frontmatter and relative Markdown links.
- `scripts/check_raw_clean.py` flags tracked raw-file modifications/deletions.
- `references/ingest-checklist.md` gives the detailed step-by-step checklist for
  external and own-work ingests.

## Completion Response

Summarize pages created/updated, validation run, and any unresolved gaps. Mention raw path corrections explicitly, such as when `raw/artical/vLLM` resolves to
`raw/articles/vLLM.pdf`.
