# AGENTS.md

## Purpose

This file defines the top-level collaboration rules for the `KaiwuDB-Agent-Skills` repository.
It is intended to keep skill development consistent across contributors and agents.

## Repository Scope

This repository is a monorepo for KaiwuDB / KWDB agent skills.

Its goals are:

- maintain a unified set of KWDB skills
- separate publishable runtime files from internal development materials
- keep structure, writing style, and release boundaries consistent across skills

## Planned Skills

The repository currently plans to maintain these skills:

- `kwdb-schema-design`
- `kwdb-performance-review`
- `kwdb-nl2sql-mcp`
- `kwdb-install-deploy`
- `kwdb-troubleshooting`
- `kwdb-data-migration`
- `kwdb-ts-anomaly-detection`
- `kwdb-intelligent-inspection`

## Stack Baseline

The repository is still in an early stage. The current baseline is:

- Git for version control
- Markdown for skills, design docs, test assets, and training materials
- YAML frontmatter for `SKILL.md` metadata
- Bash for future validation, packaging, and release scripts
- GitHub Actions for future CI and release workflows

Until runtime versions are explicitly pinned, skills must not depend on machine-specific local behavior.

## Repository Layout

```text
KaiwuDB-Agent-Skills/
├── skills/
├── internal/
├── .github/workflows/
├── AGENTS.md
└── README.md
```

Top-level rules:

- `skills/` contains publishable skills only
- `internal/` contains internal development materials only
- `.github/workflows/` is reserved for CI, validation, packaging, and release automation

During early development, a planned skill directory may temporarily exist as a placeholder.
Only a skill directory that contains `SKILL.md` plus its required runtime files should be treated as publishable.

Recommended structure for each skill:

```text
skill-name/
├── SKILL.md
├── references/
└── assets/
```

## Development Order

Use this order when developing a skill:

1. write `internal/design-specs/`
2. write `internal/activation-designs/`
3. prepare the skill-specific `references/`
4. write a minimal `SKILL.md`
5. add `assets/`
6. create test assets
7. perform real-environment validation

Do not:

- start with a large all-in-one `SKILL.md`
- build demos first and reverse-engineer the design later
- prepare a release package before testing is in place

## Skill File Conventions

### Naming

- skill directories must use kebab-case
- the main skill file must be named exactly `SKILL.md`
- files under `references/` and `assets/` should use stable, descriptive names

### `SKILL.md`

Rules:

- must include frontmatter
- should stay concise and focused on runtime protocol
- should not include long review notes, test methodology, or design history
- should stay under 500 lines when possible

### `references/`

Rules:

- store runtime knowledge and rules that may need on-demand loading
- keep the structure shallow when possible
- do not store unrelated development records here

### `assets/`

Rules:

- store supporting materials such as demo prompts, demo schemas, and output templates
- only include files that help skill use or demonstration

## Writing Style

General rules:

- use ASCII by default
- prefer short sentences, short paragraphs, and short lists
- avoid repeating the same guidance in both `SKILL.md` and `references/`
- keep instructions direct, concrete, and executable

Skill design rules:

- define the problem before the process
- write hard rules before examples
- define boundaries before capabilities
- prefer progressive disclosure

## Error Handling And Validation

When information is missing or execution fails:

- explain what is missing or what failed
- provide the next action
- do not guess a final answer when required information is unavailable

Validation rules:

- for executable content, prefer explicit validation steps
- for SQL-focused skills, prefer `EXPLAIN` or a minimal executable query
- for process-oriented skills, keep checkpoints and stage acceptance criteria

## Testing Expectations

Each skill should eventually have at least:

- trigger tests
- functional tests
- regression prompts
- baseline comparison
- a documented test method

If the skill includes executable behavior, add real execution reports when available.

## Release Boundary

Release rules:

- only publish content from `skills/<skill-name>/`
- nothing under `internal/` should be part of external delivery
- release workflows should use a whitelist, not a blacklist

Recommended whitelist:

- `SKILL.md`
- `references/**`
- `assets/**`
