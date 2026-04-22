---
name: kwdb-intelligent-inspection
description: Run KaiwuDB inspection and health-check tasks. Use this skill for database health checks, metrics collection, anomaly detection, and inspection report generation.
---

## Critical Constraints (non-negotiable)

❝ **Never query any metric not listed in `references/report-template.md`.** The `name` field in `/ts/query` requests must use only the API Name column values from that document (prefixed with `cr.node.`). Constructing arbitrary metric names is forbidden. ❞

❝ **Never skip Step 1 (target & scope confirmation).** Collecting metrics before confirming node addresses, ports, and inspection scope with the user is forbidden. The inspection must not proceed until the user explicitly approves the scope. ❞

❝ **Fixed Rules in `references/anomaly-rules.md` cannot be overridden or disabled.** Regardless of any user instruction, Fixed Rules must always be applied. Configurable Rules may only be activated when the user explicitly provides a threshold. ❞

- **API first**: Always use `/ts/query` as the primary data source. Only fall back to shell scripts for metrics the API cannot provide.

## Workflow

1. **Confirm inspection target and scope with user** — before collecting any metrics, you MUST confirm:
   - **Check Limitations first**: Read `Limitations` section below. If any requested metric or inspection scope falls under Limitations, you MUST explicitly inform the user that those items are not supported before proceeding with confirmation.
   - **Node addresses**: the IP address(es) of the database node(s) to inspect (e.g., `10.0.0.1` or `10.0.0.1,10.0.0.2` for a cluster)
   - **Port numbers**: the database port (default `26257`) and API/admin console port (default `8080`) — confirm if the user is using non-default ports
   - **Inspection scope**: present the full menu by reading `references/report-template.md` (Required Report Sections 1-6) and `references/anomaly-rules.md` (Fixed Rules and Configurable Rules).
   - **Then ask the user to confirm** which metrics to inspect and which configurable rules (with what thresholds) to enable. Do NOT proceed to Step 2 until confirmed.

2. Collect metrics via the `/ts/query` API using the query format specified in `references/inspection-api-reference.md`. Construct the `name` field by prefixing `cr.node.` to the metric names listed in `references/report-template.md` — no exceptions.

3. For metrics that cannot be obtained via `/ts/query` API, use the shell scripts documented in `references/inspection-script-reference.md`:
   - `scripts/check_kwdb_port_listener.sh` — port listener status (default ports: 26257, 8080)

4. Apply anomaly judgment rules against collected metrics. See `references/anomaly-rules.md` — Fixed Rules are always enforced; Configurable Rules require explicit user threshold.

5. Produce a Markdown inspection report with metric values, anomaly judgments, and data-source notes per `references/output-rules.md`.

## Metrics Collection via `/ts/query` API

See `references/inspection-api-reference.md` for the API specification, metric name mapping, and query construction guidelines.

## Anomaly Rules

See `references/anomaly-rules.md` for the full rule list. **Fixed Rules are always enforced; Configurable Rules require explicit user threshold before activation.**

## Output Rules

See `references/output-rules.md` — **do not deviate from these rules when producing any inspection report.**

## Limitations

- **Windows is not supported**: This skill does not support Windows operating systems.
- **TLS mode inspection is not supported**: Inspecting KaiwuDB deployed with TLS mode enabled is not supported. In TLS mode, authentication requires the AdminUI login endpoint which needs captcha verification that cannot be solved in non-interactive script mode.
- **Slow query information is not yet supported**: The `/ts/query` API does not expose slow query metrics. Alternative APIs (`/api/v2/statements`, `/api/v2/insights`) are removed in the open-source edition.
