# KaiwuDB Agent Skills

KaiwuDB Agent Skills is a community skill collection for KaiwuDB / KWDB related agent tasks.

This repository is planned to be published at:

- `https://github.com/KWDB/KaiwuDB-Agent-Skills`

## Install

List available public skills with the skills.sh CLI:

```bash
npx skills add https://github.com/KWDB/KaiwuDB-Agent-Skills --list
```

Install a skill by name:

```bash
npx skills add https://github.com/KWDB/KaiwuDB-Agent-Skills \
  --skill <skill-name>
```

Manual install for Codex:

```bash
git clone https://github.com/KWDB/KaiwuDB-Agent-Skills.git
cd KaiwuDB-Agent-Skills
cp -R skills/<skill-name> ~/.codex/skills/
```

Only install skills that appear in public discovery or release manifests. Planned skill directories may exist in the repository before they are ready.

## Ready Skills

- `kwdb-install-deploy`: Install and deploy KWDB with standard single-node and cluster workflows.
- `kwdb-text2sql-aiot`: Turn natural language into KWDB SQL for time-series, relational, and cross-model analysis.
- `kwdb-intelligent-inspection`: Run health checks and inspection workflows based on KWDB monitoring and system views.

## Claude Code Plugin

This repository includes a Claude Code marketplace manifest at `.claude-plugin/marketplace.json`.
It exposes skills that are ready for plugin distribution.

```bash
claude plugin marketplace add https://github.com/KWDB/KaiwuDB-Agent-Skills
claude plugin install <skill-name>@kaiwudb-agent-skills
```

## ClawHub

Find available KWDB skills on ClawHub:

```bash
clawhub search kwdb
```

Install a skill by slug:

```bash
clawhub install <skill-slug>
```

Install into a specific local skills directory when needed:

```bash
clawhub --dir ~/.codex/skills install <skill-slug>
```

## Planned Skills

- `kwdb-schema-design`: Design KWDB schemas and minimal DDL for relational, time-series, and mixed workloads.
- `kwdb-performance-review`: Review slow SQL, schema issues, execution plans, and tuning options.
- `kwdb-troubleshooting`: Diagnose KWDB errors, connectivity issues, stability problems, and common failures.
- `kwdb-data-migration`: Plan and execute KWDB data migration, import/export, upgrade, and sync workflows.
- `kwdb-ts-anomaly-detection`: Build anomaly detection SQL for KWDB time-series data.

## Validate

```bash
claude plugin validate .claude-plugin/marketplace.json
npx skills add . --list
npx skills add . --list --full-depth
```

## Status

This repository is still being built. Skills move from planned to ready when their runtime files, validation assets, and release metadata are complete.
