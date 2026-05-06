---
name: kwdb-intelligent-inspection
description: Run KaiwuDB inspection and health-check tasks. Use this skill for database health checks, metrics collection, anomaly detection, and inspection report generation.
---

## Critical Constraints (non-negotiable)

❝ **Never skip Step 1.** Collecting metrics before confirming node addresses, ports, and inspection scope with the user is forbidden. The inspection must not proceed until the user explicitly confirms the node addresses, ports, and inspection scope. ❞

❝ **Anomaly rules are user-driven.** If user does not request alerting, skip alerting. If user requests alerting without specific thresholds, apply default rules from `references/anomaly-rules.md`. If user provides custom thresholds, use those instead. ❞

## Workflow

### Step 1: Confirm target and scope

**Before collecting any metrics**, follow `references/inspection-requirements-confirmation.md` EXACTLY in order:
1. Parse user intent → confirm target (host, ports)
2. Probe connectivity → verify ports reachable (see `references/inspection-port-listening-reference.md`)
3. TLS mode detection → determine if inspection supported
4. Present scope menu → user confirms before proceeding

### Step 2: Collect metrics

- **Port listener status**: Use Step 1 connectivity probe results.
- **Most metrics**: Use `scripts/get_kwdb_ts_metrics.py` per `references/ts-metrics-script-usage.md`.
- **Slow queries**: Use `scripts/get_kwdb_statements.py` per `references/statements-script-usage.md`.

### Step 3: Apply anomaly rules

Apply anomaly judgment rules only when user requests alerting. See `references/anomaly-rules.md` for default rules and configurable rules.

### Step 4: Generate report

Produce a Markdown inspection report with metric values, anomaly judgments, and data-source notes per `references/output-rules.md`.

## Anomaly Rules

See `references/anomaly-rules.md` for default rules and configurable rules.

## Output Rules

See `references/output-rules.md` — **do not deviate from these rules when producing any inspection report.**

## Limitations

- **Windows is not supported**: This skill does not support Windows operating systems.
- **TLS mode inspection is not supported**: This skill does not support inspecting KaiwuDB deployed with TLS mode enabled.