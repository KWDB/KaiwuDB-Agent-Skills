---
name: skill-creator
description: Use when users want to create a new skill or improve an existing one, especially when they need help defining scope, choosing a skill pattern, designing activation boundaries, structuring references or scripts, or validating the final package.
---

# Skill Creator

## Overview

Design first, implementation second. The goal is a minimal, executable skill whose trigger boundary is clear and whose runtime instructions stay separate from design, testing, and packaging notes.

## Workflow

1. Define scope before editing files.
   - Capture the task, trigger prompts, success criteria, non-goals, and required tools or MCPs.
   - If the skill is new or underspecified, read `references/workflows.md`.
2. Choose the dominant pattern before drafting `SKILL.md`.
   - Read `references/pattern-selection.md`.
   - Use one primary pattern unless a second pattern is necessary to prevent a concrete failure mode.
3. Design activation before implementation.
   - Read `references/activation-design.md`.
   - Write trigger prompts, non-trigger prompts, false-positive risks, false-negative risks, and the first action after activation.
4. Split files by responsibility.
   - Keep runtime protocol in `SKILL.md`.
   - Put detailed domain rules, checklists, and examples in `references/`.
   - Put copied or consumed output resources in `assets/`.
   - Add `scripts/` only when a manual step is repetitive or needs deterministic execution.
5. Write the minimal runtime protocol.
   - Frontmatter: only `name` and `description`.
   - Description: explain when to use the skill, not how it works.
   - Body: include workflow, guardrails, error handling, and output expectations.
6. Validate and package deliberately.
   - Read `references/validation-and-distribution.md`.
   - Add trigger, functional, and regression prompts as internal test assets when the skill will be maintained.
   - Package only the runtime files that should ship.

## Guardrails

- Do not expand `SKILL.md` before the scope, pattern, and activation boundary are clear.
- Do not keep long design notes, activation analysis, or test methodology in `SKILL.md`.
- Do not scaffold placeholder files "just in case". Add `scripts/` and `assets/` only when they solve a real repeated need.
- When validation fails, fix the right layer:
  - trigger issue -> activation design or description
  - workflow issue -> `SKILL.md`
  - missing domain rule -> `references/`
  - brittle manual step -> `scripts/`
  - package bloat -> distribution selection

## Reference Map

- `references/workflows.md`: recommended sequence for building a skill from scope to distribution
- `references/pattern-selection.md`: how to choose among Tool Wrapper, Generator, Reviewer, Inversion, and Pipeline
- `references/activation-design.md`: trigger boundary checklist and description rules
- `references/validation-and-distribution.md`: test assets, verification flow, and runtime packaging rules

## Commands

```bash
python3 scripts/init_skill.py my-skill --path /path/to/skills
python3 scripts/quick_validate.py /path/to/skills/my-skill
python3 scripts/package_skill.py /path/to/skills/my-skill ./dist
```
