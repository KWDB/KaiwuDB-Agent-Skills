# Pattern Selection

Pick the dominant skill pattern before drafting `SKILL.md`. A good skill usually has one primary pattern and, at most, one supporting pattern.

## Decision Guide

- **Tool Wrapper**: Use when the skill teaches the agent how to work with a system, API, framework, protocol, or internal ruleset.
- **Generator**: Use when the main value is producing a stable output format from a template or schema.
- **Reviewer**: Use when the skill inspects existing code, content, or configuration against a checklist and reports issues by severity.
- **Inversion**: Use when the agent must interview the user first and should not act until critical context is collected.
- **Pipeline**: Use when the task has hard checkpoints, ordered stages, or explicit approval gates that cannot be skipped.

## How To Choose

1. Write the job in one sentence.
2. Ask what would fail first if the agent improvised:
   - Missing domain knowledge -> `Tool Wrapper`
   - Inconsistent output shape -> `Generator`
   - Superficial critique -> `Reviewer`
   - Acting before clarifying requirements -> `Inversion`
   - Skipping mandatory stages -> `Pipeline`
3. Keep the first choice unless a second pattern is clearly necessary.

## Combination Rules

- `Tool Wrapper` + `Reviewer`: review against a domain-specific checklist.
- `Tool Wrapper` + `Pipeline`: apply domain rules inside a strict workflow.
- `Inversion` + `Generator`: collect inputs first, then fill a template.
- Avoid combining more than two patterns unless the failure mode is impossible to model otherwise.

## Anti-Patterns

- Do not choose a pattern based on file layout alone.
- Do not start with a giant `SKILL.md` and infer the pattern later.
- Do not use `Pipeline` when a short ordered checklist is enough.
- Do not use `Inversion` if the user already supplied the required constraints.
