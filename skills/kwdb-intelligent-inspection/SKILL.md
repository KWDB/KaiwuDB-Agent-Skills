---
name: kwdb-intelligent-inspection
description: |
  Run KaiwuDB inspection and health-check tasks. Use this skill for database health checks, metrics collection, anomaly detection, and inspection report generation.
triggers:
  - show me all database metrics
  - database metrics for my KWDB cluster
  - kwdb cluster metrics
  - check database health
  - inspect KWDB cluster
  - database health check
  - collect database metrics
  - kwdb inspection
  - 巡检
  - 数据库指标
  - 查看数据库指标
  - 检查数据库健康
---

## Critical Constraints (non-negotiable)

❝ **Never skip Step 1.** Collecting metrics before confirming node addresses, ports, and inspection scope with the user is forbidden. The inspection must not proceed until the user explicitly confirms the node addresses, ports, and inspection scope. ❞

❝ **Never call a script without reading its usage doc first.** Before running any script under `scripts/`, you MUST read the corresponding `references/*-script-usage.md` file. This is the only way to know the correct parameters, defaults, and required arguments. Guessing parameters is forbidden. ❞

❝ **Scripts are pure-Python stdlib and run directly with `python3`.** Each script under `scripts/` is a standalone `#!/usr/bin/env python3` program with an `argparse` CLI; invoke it as `python3 scripts/<script>.py [flags]` (or via any host-local shell wrapper that can launch a Python script). Do not reach for agent-specific MCP wrappers (e.g. `run_skill_scripts`, `run_local_command`, `run_shell_command`) — the skill has no runtime dependency on them. ❞

❝ **Use the new helpers for connectivity and TLS.** Port probing goes through `probe_ports.py`. TLS detection goes through `detect_tls_mode.py`. Local time stamps go through `get_local_timestamp.py`. Do not improvise with `curl` / `wget` / `nc` / `date`. ❞

❝ **Anomaly rules are user-driven.** If user does not request alerting, skip alerting. If user requests alerting without specific thresholds, apply default rules from `references/anomaly-rules.md`. If user provides custom thresholds, use those instead. ❞

## Workflow

### Step 1: Confirm target and scope

**Before collecting any metrics**, follow `references/inspection-requirements-confirmation.md` EXACTLY in order:
1. Parse user intent → confirm target (host, ports)
2. Probe connectivity → call `probe_ports.py` per `references/probe-ports-script-usage.md`
3. TLS mode detection → call `detect_tls_mode.py` per `references/detect-tls-mode-script-usage.md`
4. Present scope menu → user confirms before proceeding

### Step 2: Collect metrics

**MANDATORY: Read the script usage doc BEFORE calling any script.**

| Script | Usage doc |
|--------|-----------|
| `scripts/get_kwdb_statements.py` | `references/statements-script-usage.md` |
| `scripts/get_kwdb_ts_metrics.py` | `references/ts-metrics-script-usage.md` |
| `scripts/probe_ports.py` | `references/probe-ports-script-usage.md` |
| `scripts/detect_tls_mode.py` | `references/detect-tls-mode-script-usage.md` |
| `scripts/get_local_timestamp.py` | `references/get-local-timestamp-script-usage.md` |

Do not call any script without first reading its usage doc. Verify the parameter names, required arguments, and defaults match what you are about to pass.

### Step 3: Apply anomaly rules

Apply anomaly judgment rules only when user requests alerting. See `references/anomaly-rules.md` for default rules and configurable rules.

### Step 4: Generate report

Produce a Markdown inspection report with metric values, anomaly judgments, and data-source notes per `references/output-rules.md`. Use `get_local_timestamp.py` to obtain the report timestamp; never fabricate it from training data or `datetime.utcnow()`. PDF / HTML rendering goes through the `markdown-to-html` / `pdf` skills when those are available — they are independent of this skill and may be invoked separately if needed.

## Limitations

- **Windows is not supported**.
- **TLS mode inspection is not supported**.
- **No third-party Python deps in skill scripts**: all new scripts are stdlib-only. Existing scripts (`md_to_*.sh` etc.) declare their packages via the shared `_venv.sh` wrapper.
