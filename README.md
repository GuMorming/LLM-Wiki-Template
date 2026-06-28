# LLM Research Wiki Template

A personal, LLM-maintained research knowledge base built on plain Markdown
files and operated with Codex repo instructions.

## Origin

This template follows the [LLM-Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern: immutable raw sources are converted
into a persistent, structured wiki that compounds over time. Instead of asking
an LLM to re-read the same PDFs, notes, manuscripts, and reviews for every
question, you ask it to maintain an explicit knowledge layer.

This repository is a generalized template. Fork it, replace the placeholders in
`AGENTS.md`, and adapt the folder/page schema to your own domain.

## Template vs. Live Wiki

This directory is the publishable template. It should not contain a researcher's
private manuscripts, personal notes, reviewer comments, unpublished results, or
domain-specific claims.

Your live wiki should be a separate working copy where you add:

- your identity and research context,
- your active projects,
- your private raw sources,
- your own page conventions,
- your ingested source notes and syntheses.

## What It Does

Every time a source is ingested, Codex reads it, extracts claims and evidence,
and writes or updates Markdown pages across the wiki: source notes, concepts,
methods, systems, datasets, claims, experiments, syntheses, and project pages.

The raw documents are never modified. The wiki is the living layer that
accumulates research knowledge across sources.

## Architecture

| Layer | Contents | Who writes it |
|---|---|---|
| `raw/` | Immutable source documents: papers, notes, manuscripts, datasets, reviews, figures | You |
| `wiki/` | Structured Markdown pages: source notes, concepts, methods, claims, experiments, syntheses, projects | Codex |
| schema | `AGENTS.md`, `index.md`, `log.md` | You + Codex |

The operational rules live in [AGENTS.md](AGENTS.md). Codex should read that
file first when working in the repository.

## Workflows

### INGEST

Place a source under `raw/`, then prompt:

```text
ingest raw/papers/example-paper.pdf
```

OR, use skill `llm-wiki-ingest`:

```text
$llm-wiki-ingest raw/papers/example-paper.pdf
```

Codex reads the source, summarizes key takeaways, creates a source note, updates
affected wiki pages, and logs the change.

### QUERY

Ask a research question. Codex starts from [index.md](index.md), identifies the
relevant cluster, reads synthesis pages when they exist, follows `related:`
frontmatter links, and answers from the wiki with traceable citations.

### LINT

Prompt:

```text
lint
```

OR, use the skill `llm-wiki-lint`:

```text
$llm-wiki-lint
```

Codex audits duplicates, stale pages, weak source support, broken links, orphan
pages, missing pages, contradictions, and unsupported own-work claims. Nothing
is auto-fixed unless you explicitly ask.

## Folder Structure

```text
raw/
  own works/      private manuscripts and project artifacts
  papers/         external papers, arXiv PDFs, conference papers
  codebases/      external system/code artifacts and docs
  datasets/       dataset cards, benchmark specs, workload docs
  reviews/        review and rebuttal materials
  notes/          your research notes and research maps
  articles/       general articles or legacy imports
  books/          books
  chapters/       book chapters
  images/         figures, diagrams, sketches, plots
  _staging/       candidate sources before ingest

wiki/
  source-notes/   one page per ingested source
  concepts/       technical or theoretical concepts
  methods/        algorithms, methods, techniques
  systems/        systems, tools, implementations
  benchmarks/     benchmark and metric pages
  datasets/       dataset/workload pages
  experiments/    experiment records
  claims/         claim-level evidence ledgers
  syntheses/      reusable literature syntheses
  projects/       one subfolder per active project
  authors/        optional recurring researchers/authors/labs
  debates/        trade-offs and research debates
  themes/         broad cross-cutting themes

outputs/
  paper-drafts/   assembled drafts
  rebuttals/      response letters and rebuttal drafts
  surveys/        related-work drafts and survey tables
  figures/        final figures
  slides/         decks
  tables/         comparison tables

archive/          deprecated or superseded wiki pages
conversations/    optional saved agent conversations or exports
```

## Page Types

Page templates are defined in `AGENTS.md`.

| Type | Location | Purpose |
|---|---|---|
| Source note | `wiki/source-notes/` | One page per ingested source: summary, claims, evidence, quotes, links |
| Concept | `wiki/concepts/` | Definitions, distinctions, source support, open questions |
| Method | `wiki/methods/` | Algorithms or techniques, assumptions, strengths, failure modes |
| System | `wiki/systems/` | Serving engines, tools, architectures, implementations |
| Benchmark/Dataset | `wiki/benchmarks/`, `wiki/datasets/` | Workloads, metrics, caveats |
| Claim | `wiki/claims/` | Evidence-backed statements used in projects or papers |
| Experiment | `wiki/experiments/` | Setup, results, interpretation, reproducibility |
| Synthesis | `wiki/syntheses/` | Evolving cross-source arguments and surveys |
| Project | `wiki/projects/` | Active work, claims, sources, risks, outputs |

## Navigation Design

The wiki is designed around a three-step navigation cascade:

1. `index.md` organizes pages into clusters.
2. `wiki/syntheses/` stores standing overviews for mature clusters.
3. `related:` frontmatter lists 3-5 close neighbors by filename stem.

This keeps query cost manageable as the wiki grows.

## Getting Started

1. Fork/Clone this template.

2. Open the folder in Codex.

3. Edit `AGENTS.md` and replace bracketed placeholders such as `[YOUR NAME]`,
   `[YOUR ROLE]`, `[YOUR INSTITUTION]`, `[PRIMARY RESEARCH AREA]`, and
   `[ACTIVE PROJECT]`.

4. Write a short research map in your own words and place it at
   `raw/notes/research-map.md`.

5. Ask Codex:

   ```text
   $llm-wiki-ingest raw/notes/research-map.md
   ```

6. Watch the wiki populate with concept pages from your first source

7. Add raw sources one at a time. Supervise the first 5-10 ingests closely.

## Included Repo Skills

This template includes repository-scoped Codex skills under `.agents/skills/`:

- `$llm-wiki-ingest` for source ingestion.
- `$llm-wiki-lint` for wiki health checks.

## Conventions

- Filenames use lowercase kebab case: `example-concept.md`.
- Every wiki page starts with YAML frontmatter.
- Wiki links are relative Markdown links.
- Raw files are immutable after ingest.
- Durable changes are appended to `log.md`.
- Never invent citations, paper status, baselines, numbers, or results.

## Scaling Advice

- Start with your own research map as the first ingest.
- Ingest sources one at a time for the first 10-15 sources.
- Do not ingest your entire library by default; prioritize sources tied to
  active projects.
- Use `raw/_staging/` as a holding pen for candidate sources.
- Run lint after every 10-15 ingests.
- Create the first synthesis page when a cluster has enough source support to
  become a recurring query target.

## Requirements

- Codex with repository access.
- `AGENTS.md` in the repository root.
- No database, embeddings, or vector store required.

## Credits

- Pattern: [Andrej Karpathy's LLM Wiki idea](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).
- Prior template inspiration: [MetamusicX LLM research wiki template](https://github.com/MetamusicX/llm-research-wiki).
- This template is provided as a generalized starting point for personal
  research wikis.

## License

MIT. Replace the placeholder name in [LICENSE](LICENSE) before publishing.
