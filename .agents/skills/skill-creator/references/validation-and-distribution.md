# Validation And Distribution

A skill is not done when the prose looks good. Validate trigger behavior, execution behavior, and the runtime package separately.

## Minimum Validation Assets

Keep these as internal development assets when the skill is important enough to maintain over time:

- `trigger-tests.md`: prompts that should and should not activate the skill
- `functional-tests.md`: prompts that exercise the intended workflow
- `regression-prompts.md`: prompts for bugs or past failures
- `baseline-comparison.md`: before/after notes showing what the skill fixes
- `test-method.md`: how the skill was validated in real use

## Validation Sequence

1. Validate metadata and structure with `python3 scripts/quick_validate.py <skill-dir>`
2. Run trigger prompts and confirm the skill loads only when expected
3. Run functional prompts and verify the first action and workflow order
4. Re-run regression prompts after every meaningful change
5. If the skill depends on real tools or MCPs, validate against the real environment rather than simulated answers

## Fix At The Right Layer

- Trigger bug -> activation design or description
- Workflow bug -> `SKILL.md`
- Missing domain rule -> `references/`
- Repetitive or brittle manual step -> `scripts/`
- Package too heavy -> distribution selection

## Distribution Rule

Package the smallest runtime set that still works:

- `SKILL.md`
- required `references/`
- required `assets/`
- required `scripts/`

Keep internal planning, activation analysis, and test notes out of the distributable package unless the recipient explicitly needs them.
