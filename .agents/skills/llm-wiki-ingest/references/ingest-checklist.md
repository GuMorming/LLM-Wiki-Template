# Ingest Checklist

Use this checklist after reading repository `AGENTS.md`. Do not treat this file
as a replacement for the repo schema.

## 1. Resolve and Classify

- Resolve the user-provided path with `scripts/resolve_source.py`.
- Confirm the source is under `raw/`.
- Classify source kind:
  - `own-work`: under `raw/own works/`.
  - `external-paper`: paper PDF, arXiv export, conference PDF, technical report.
  - `codebase`: code snapshot, README export, artifact docs.
  - `dataset`: dataset card, benchmark spec, workload description.
  - `review`: reviewer comments, rebuttal material, meta-review.
  - `note`: meeting note, brainstorm, local research note.
- Determine likely target clusters from `index.md`.

## 2. Read Source

- Read the whole source or enough of a multi-file folder to cover the claims and
  evidence actually used.
- For PDFs, extract text and visually verify figures/tables used for exact
  numbers.
- For LaTeX, inspect the main file, included sections, figures/tables, and
  bibliography when relevant.
- Record title, authors, year, venue/status, raw path, and citation key if
  available.
- Record problem, method/system, assumptions, main evidence, limitations, and
  relevance to the repository owner's research.

## 3. Pre-Write Summary

Before editing files, give the user a short summary:

- problem and motivation,
- method/system design,
- key claims and exact numbers,
- evidence setup and baselines,
- limitations and risks,
- relevance to existing wiki clusters/projects.

## 4. Create or Update Pages

Always create:

- `wiki/source-notes/<author-year-short-title>.md`

Always update:

- `index.md`
- `log.md`

Update or create as warranted:

- `wiki/concepts/`
- `wiki/methods/`
- `wiki/systems/`
- `wiki/benchmarks/`
- `wiki/datasets/`
- `wiki/projects/<project>/index.md`
- `wiki/claims/`
- `wiki/experiments/`
- `wiki/syntheses/`
- `wiki/debates/`

For own-work ingest:

- update the project page,
- create claim pages for main paper claims,
- create experiment pages for explicit evaluations,
- connect each claim to section/figure/table/experiment evidence,
- preserve under-review confidentiality.

For external-source ingest:

- create method/system/dataset pages only for reusable recurring entities,
- create claim/experiment pages only for important reusable evidence,
- connect source support to affected concepts and projects.

## 5. Cross-Link

- Link first mentions of existing wiki pages.
- Use relative Markdown links only.
- Add source support backlinks from concept/method/system pages.
- If a source affects an own-work project, update that project page.
- If a source supports or weakens a claim, update the claim page.
- Log missing recurring pages as `PAGE NEEDED`.

## 6. Validate

Run:

```bash
python3 .agents/skills/llm-wiki-ingest/scripts/audit_wiki.py
python3 .agents/skills/llm-wiki-ingest/scripts/check_raw_clean.py
git status --short
```

Confirm:

- no broken relative links,
- every wiki page has YAML frontmatter with required keys,
- no tracked raw files were modified or deleted,
- temporary extraction files are ignored or intentionally removed,
- unrelated dirty worktree changes were not reverted.

## 7. Final Response

Report:

- resolved source path,
- pages created,
- pages updated,
- validation run,
- unresolved gaps or `PAGE NEEDED` entries,
- whether changes were committed/pushed only if the user requested that.
