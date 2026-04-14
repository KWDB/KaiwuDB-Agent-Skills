# Zero-To-One Workflow

Build skills in design order, not file order.

## Recommended Sequence

1. Define the task, trigger conditions, success criteria, non-goals, and tool dependencies.
2. Choose the dominant pattern before writing `SKILL.md`.
3. Design activation boundaries: trigger prompts, non-trigger prompts, false positives, false negatives, and the first post-activation action.
4. Plan the file split:
   - `SKILL.md` for runtime protocol
   - `references/` for domain rules and detailed guidance
   - `assets/` for copied or consumed output resources
   - `scripts/` for deterministic or repetitive operations
5. Write the supporting references before expanding the main file.
6. Draft the minimal `SKILL.md`: workflow, guardrails, error handling, output expectations.
7. Add demo prompts or example inputs only after the workflow is stable.
8. Build trigger, functional, and regression tests.
9. Validate in the real environment if the skill depends on tools, APIs, or MCPs.
10. Fix the failing layer instead of piling more prose into `SKILL.md`.
11. Package only the runtime assets that need to ship.

## Core Principle

Do not treat `SKILL.md` as the place where every design and testing note belongs. It should stay small enough to execute, while design artifacts and validation assets stay separate.
