---
name: llm-wiki-lint
description: Audit this repository-local LLM Research Wiki for structural, linking, evidence, and knowledge-quality issues. Use when the user says "lint", asks to lint/check/audit the wiki, asks for duplicate pages, stale pages, contradictions, missing concept/method/system pages, orphan pages, weak source support, broken links, or own-work claims without explicit evidence.
---

# LLM Wiki Lint

## Overview

Use this skill to run the repository's wiki lint workflow and report prioritized
issues without automatically fixing them. Treat repository `AGENTS.md` as the
governing schema; this skill supplies the repeatable audit procedure and helper
script.

## Required First Steps

1. Read `AGENTS.md` in the repository root, especially Workflow 6: LINT.
2. Read `index.md` to understand intended clusters and navigation.
3. Run the mechanical lint script:

```bash
python3 .agents/skills/llm-wiki-lint/scripts/lint_wiki.py
```

4. Read `references/lint-playbook.md` for the manual review checklist and
   severity rubric.

## Lint Scope

Check for:

- duplicate pages covering the same source, concept, method, system, dataset, or
  claim,
- stale pages that likely were not updated after relevant ingests,
- contradictions between source notes, claims, and project pages,
- recurring concepts/methods/systems mentioned but lacking pages,
- orphan pages with no inbound wiki/index links,
- overgrown pages that should be split,
- weak pages with vague definitions or no source support,
- thin source support for important concepts/debates,
- broken relative links or malformed frontmatter,
- own-work claims without explicit evidence.

## Rules

- Do not modify wiki files during lint unless the repository owner explicitly asks for
  fixes.
- Do not reread raw files unless a specific quote, result, baseline, or evidence
  reference needs verification.
- Prefer wiki pages and `log.md` for the first lint pass.
- Separate script-backed findings from agent judgment.
- Use relative paths in reported findings.
- If the lint reveals durable gaps, report them; append to `log.md` only when
  the user asks for durable logging or when `AGENTS.md` requires it for the
  current task.

## Output Format

Lead with findings, ordered by severity:

- `P0` blocks reliable use of the wiki, such as broken core navigation or raw
  mutation.
- `P1` can mislead research work, such as unsupported own-work claims,
  contradictory project/source pages, or wrong paper status.
- `P2` degrades maintainability or retrieval, such as orphan pages, missing
  backlinks, thin source support, and missing recurring pages.
- `P3` is cleanup, style, naming, or organization polish.

For each finding, include:

- severity,
- short title,
- affected file path(s),
- evidence from the script or page text,
- recommended fix.

After findings, add:

- open questions or assumptions,
- checks run,
- residual risks or areas not manually inspected.

## Bundled Resources

- `scripts/lint_wiki.py` runs mechanical wiki lint checks and prints
  prioritized findings.
- `references/lint-playbook.md` gives the manual review checklist and final
  reporting rubric.

## Completion Response

Report the lint result and avoid saying the wiki is clean unless both the script
and the manual checklist found no actionable issues. If the user asks to fix
issues, treat that as a separate edit task and preserve unrelated changes.
