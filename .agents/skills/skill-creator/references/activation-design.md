# Activation Design

Design activation before implementation. The goal is to make the trigger boundary explicit enough that future agents know when to load the skill and what to do first.

## Required Questions

Answer these before expanding `SKILL.md`:

1. Which prompts should trigger the skill?
2. Which prompts should not trigger it?
3. What false positives are likely?
4. What false negatives are likely?
5. After activation, what is the first concrete action?

## Output Template

Use this structure in an internal design note such as `references/activation-design.md` for the new skill:

```markdown
# Activation Design

## Trigger Prompts
- ...

## Non-Trigger Prompts
- ...

## False Positives
- Risk:
- Mitigation:

## False Negatives
- Risk:
- Mitigation:

## First Action After Activation
- ...
```

## Description Rules

- `description` should start with `Use when...`
- Describe triggering situations, not the workflow
- Prefer symptoms and contexts over implementation details
- Keep it in third person

## Repair Strategy

- Wrong skill loads -> tighten trigger prompts or narrow the description
- Skill does not load -> add missing trigger phrases and synonyms
- Skill loads but starts incorrectly -> fix the "first action" definition, not just the prose in `SKILL.md`
