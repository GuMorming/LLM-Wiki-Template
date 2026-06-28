# Lint Playbook

Use this after reading repository `AGENTS.md` and running
`scripts/lint_wiki.py`.

## Manual Review Checklist

### Duplicate Pages

- Compare source-note titles, normalized stems, and page titles.
- Check whether a concept/method/system appears under multiple folders with
  overlapping scope.
- Recommend merge/split only when the intended boundary is clear.

### Staleness

- Read recent `log.md` entries.
- Check whether later source ingests should have updated older concept, method,
  system, project, claim, experiment, or synthesis pages.
- Flag pages whose `updated` date predates clearly relevant ingests.

### Contradictions

- Compare project pages against linked source notes and claim pages.
- Look for mismatched status, venue, headline numbers, baselines, and project
  framing.
- Treat under-review status and unpublished results conservatively.

### Missing Pages

- Search for repeated technical nouns or systems in source notes, project pages,
  and log gaps.
- Prefer logging `PAGE NEEDED` over creating pages during lint.
- Flag missing pages as P2 unless they block major navigation or own-work claims.

### Orphans and Backlinks

- Use script output for pages without inbound links.
- Decide whether the page is intentionally standalone. Source notes and seed
  project pages may be acceptable, but important reusable pages need index or
  cluster backlinks.

### Overgrown or Weak Pages

- Split pages when they mix multiple concepts, methods, systems, and experiments.
- Flag weak pages with vague definitions, no source support, or no relationship
  to the repository owner's research.
- Flag thin support when an important concept/debate depends on only one source
  and is used broadly.

### Own-Work Evidence

- For own-work claims, verify that evidence points to a section, figure, table,
  experiment page, raw artifact, or source note.
- Claims with only narrative support are P1 if they could affect manuscript
  writing or rebuttal strategy.

## Severity Rubric

- `P0`: wiki cannot be trusted or navigated; broken root index, missing core
  files, raw mutation, or many broken links.
- `P1`: likely to mislead research writing; unsupported own-work claims,
  contradictory results/status, wrong baselines, or invented metadata.
- `P2`: hurts retrieval or maintenance; orphan pages, duplicate scope, stale
  backlinks, missing recurring pages, thin source support.
- `P3`: cleanup; naming/style consistency, minor frontmatter polish, optional
  cross-links.

## Final Report Template

```markdown
Findings:

- [P1] Short title - `path/to/file.md`
  Evidence: ...
  Recommended fix: ...

Open questions:
- ...

Checks run:
- `python3 .agents/skills/llm-wiki-lint/scripts/lint_wiki.py`

Residual risk:
- ...
```
