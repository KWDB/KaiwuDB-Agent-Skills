# KaiwuDB Agent Skills

KaiwuDB Agent Skills is a community skill collection for KaiwuDB / KWDB related agent tasks.

This repository is planned to be published at:

- `https://github.com/KWDB/KaiwuDB-Agent-Skills`

## Install

Install one skill:

```bash
git clone https://github.com/KWDB/KaiwuDB-Agent-Skills.git
cd KaiwuDB-Agent-Skills
cp -R skills/<skill-name> ~/.codex/skills/
```

Install all skills:

```bash
git clone https://github.com/KWDB/KaiwuDB-Agent-Skills.git
cd KaiwuDB-Agent-Skills
cp -R skills/* ~/.codex/skills/
```

If your agent uses a different local skills directory, replace `~/.codex/skills/` with the correct target path.

## Implemented Baseline Skill

- `kwdb-schema-design`: Design KWDB schemas and minimal DDL for relational, time-series, and mixed workloads.

## Planned Skills

- `kwdb-performance-review`: Review slow SQL, schema issues, execution plans, and tuning options.
- `kwdb-nl2sql-mcp`: Turn natural language into KWDB SQL with MCP-assisted query generation and validation.
- `kwdb-install-deploy`: Install and deploy KWDB with standard single-node and cluster workflows.
- `kwdb-troubleshooting`: Diagnose KWDB errors, connectivity issues, stability problems, and common failures.
- `kwdb-data-migration`: Plan and execute KWDB data migration, import/export, upgrade, and sync workflows.
- `kwdb-ts-anomaly-detection`: Build anomaly detection SQL for KWDB time-series data.
- `kwdb-intelligent-inspection`: Run health checks and inspection workflows based on KWDB monitoring and system views.

## Validate

```bash
python3 scripts/validate_repo.py
python3 -m unittest tests.test_validate_repo
```

## Status

This repository is still being built. `kwdb-schema-design` is the reviewed baseline example skill. The remaining planned skills are not implemented yet.
