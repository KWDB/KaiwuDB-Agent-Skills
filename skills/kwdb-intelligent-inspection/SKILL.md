---
name: kwdb-intelligent-inspection
description: |
  Run KaiwuDB inspection and health-check tasks against insecure or TLS deployments. The skill auto-routes data collection: MCP tools (`query-metrics`, `query-slow-sql`) when `kwdb-mcp-server` v3.2.0+ is available, legacy Python scripts (`scripts/get_kwdb_ts_metrics.py`, `scripts/get_kwdb_statements.py`) when it is not — legacy scripts are insecure-only and will be rejected by TLS-deployed KaiwuDB clusters.
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

❝ **Inspect both insecure and TLS deployments — choose the right data path.** This skill works against any KaiwuDB deployment. The data collection path is selected at runtime: prefer the `kwdb-mcp-server` MCP tools (`query-metrics`, `query-slow-sql`) when they are callable in this session (works for both insecure and TLS); otherwise detect the deployment mode via `detect_tls_mode.py` and use the legacy Python scripts only when the cluster is plaintext. If the cluster is TLS and the MCP tools are not callable, you MUST stop and tell the user to install `kwdb-mcp-server` v3.2.0+ and configure a database URL with a username and password — the legacy scripts hard-code plain HTTP and do not support Basic Auth, so they will fail against TLS. ❞

❝ **Verify `kwdb-mcp-server` is healthy before calling `query-metrics` or `query-slow-sql`.** The MCP server is a separate Go binary that holds the database credentials and signs admin Basic Auth on the LLM's behalf. The skill must **never** deploy, restart, or otherwise reconfigure it (that would force credentials into the conversation context). Use `references/kwdb-mcp-server-setup.md` §1 (detect) and §2 (verify) only. Tool-call errors mentioning `connection refused`, `auth failed`, `invalid port`, `TLS admin endpoint requires credentials`, or `password authentication failed for user root` are deployment problems — stop, report the error to the user, and tell them to engage the operator with `docs/kwdb-mcp-server-deployment.md` (project root, NOT loaded by this skill). ❞

❝ **Never call a script without reading its usage doc first.** Before running any script under `scripts/` (`probe_ports.py`, `detect_tls_mode.py`, `get_local_timestamp.py`, and on the insecure fallback path also `get_kwdb_ts_metrics.py` / `get_kwdb_statements.py` — see Workflow Step 1, Step 3, Step 4a, and Step 5), you MUST read the corresponding `references/*-script-usage.md` file. This is the only way to know the correct parameters, defaults, and required arguments. Guessing parameters is forbidden. ❞

❝ **Local scripts in `scripts/` are stdlib-only Python and may be invoked directly via `python3`.** The only MCP server this skill depends on is `kwdb-mcp-server`, which exposes `query-metrics` and `query-slow-sql`. No other MCP server, tool wrapper, or remote runner is part of this skill. ❞

❝ **Use the helpers for connectivity, TLS detection, and timestamps.** Port probing goes through `probe_ports.py`. TLS detection goes through `detect_tls_mode.py` (only on the legacy fallback path — see Step 3). Local time stamps go through `get_local_timestamp.py`. Do not improvise with `curl` / `wget` / `nc` / `date`. ❞

❝ **Anomaly rules are user-driven.** If user does not request alerting, skip alerting. If user requests alerting without specific thresholds, apply default rules from `references/anomaly-rules.md`. If user provides custom thresholds, use those instead. ❞

## Workflow

### Step 1: Confirm target and scope

**Before collecting any metrics**, follow `references/inspection-requirements-confirmation.md` EXACTLY in order:
1. Parse user intent → confirm target (host, ports)
2. **Verify `kwdb-mcp-server` is reachable** — `references/kwdb-mcp-server-setup.md` §1 (detect) and §2 (verify). If the server is not running or its `/mcp` handshake fails, **stop and report to the user** — the skill does NOT deploy or restart the MCP server (that is operator-only via `docs/kwdb-mcp-server-deployment.md`). If the user has explicitly chosen the legacy insecure fallback, proceed to Step 3 only when the deployment mode is plaintext.
3. Probe connectivity → call `probe_ports.py` per `references/probe-ports-script-usage.md` against the database port (default 26257) and the admin port recorded from the MCP server's `--admin-base-url` (default 8080).
4. Present scope menu → user confirms before proceeding.

**Do NOT proceed to Step 2 until target info, ports, and the MCP server's `--admin-base-url` are confirmed with the user.**

### Step 2: Try MCP tools first (preferred path)

If `kwdb-mcp-server` v3.2.0+ is connected to this session and exposes `query-metrics` and `query-slow-sql`, **call those tools directly** for data collection. This path works against both insecure and TLS deployments because the MCP server performs the Basic Auth dance end-to-end using the `--admin-base-url` it was started with (see `references/kwdb-mcp-server-setup.md` §2).

#### Time-series metrics → `query-metrics`

Call the `query-metrics` MCP tool on `kwdb-mcp-server` with:

| Field | Required | Notes |
|---|---|---|
| `metric_names` | yes | 1 to 32 names from the fixed catalog (QPS, CPU, memory, latency, storage, cluster, network); `references/metric-types.md` lists them all. |
| `start_ms` | yes | Unix-millisecond window start. |
| `end_ms` | yes | Unix-millisecond window end; must be > `start_ms`. |
| `sample_ms` | yes | Sampling interval in ms. |

**Header semantics** (the Claude Code MCP HTTP transport does not surface header parameters; the MCP server falls back to its startup defaults — see `references/kwdb-mcp-server-setup.md` §5):

| Header | Purpose | Resolution priority |
|---|---|---|
| `X-Database-URI` | Full PostgreSQL DSN for credential extraction. | per-request header (with non-empty user + password) → startup positional DSN |
| `X-Admin-Base-URL` | Admin endpoint base URL for `/restapi/ts/query`. | per-request header → `--admin-base-url` flag → DB URL derivation `http://{host}:8080` |

When both headers are absent (the typical Claude Code case), the MCP server uses its startup DSN for credentials and the `--admin-base-url` flag for the admin endpoint.

#### Slow SQL → `query-slow-sql`

Call the `query-slow-sql` MCP tool with:

| Field | Optional | Notes |
|---|---|---|
| `limit` | yes | Default 10. |
| `min_latency_ms` | yes | Default 0 (no floor); filter is always on `service_latency_ms`. |
| `sort_by` | yes | `service_lat` (default) / `run_lat` / `plan_lat` / `count`. |

Same `X-Database-URI` header semantics as `query-metrics` apply. `query-slow-sql` runs SQL (not the admin API), so `X-Admin-Base-URL` is irrelevant.

After MCP collection succeeds, skip to Step 4 (apply anomaly rules) and Step 5 (generate report).

If `query-metrics` or `query-slow-sql` is unavailable in this session (older `kwdb-mcp-server` build, MCP server failed to start, or the tool call returned a deployment-class error), follow `references/kwdb-mcp-server-setup.md` §3 to **classify the error** and stop. Report the failure class to the user; the user escalates to the operator (`docs/kwdb-mcp-server-deployment.md`). Only when the deployment problem cannot be resolved immediately should you fall back to Step 3 — and Step 3 requires plaintext deployment (legacy scripts cannot reach TLS admin endpoints).

### Step 3: Classify KaiwuDB deployment mode (legacy fallback path only)

This step runs **only** when Step 2 could not use the MCP tools. Call `scripts/detect_tls_mode.py` via `python3 scripts/detect_tls_mode.py` against the admin port (`8080` by default). See `references/detect-tls-mode-script-usage.md` for full CLI reference.

Decision rules:

| `determined` | `tls_enabled` | Action |
|--------------|---------------|--------|
| `true` | `true`  | TLS enforced. **Stop — legacy scripts cannot work here.** Tell the user to install `kwdb-mcp-server` v3.2.0+ and configure a database URL with username + password; then re-run this skill so it can take the MCP path in Step 2. |
| `true` | `false` | Plaintext. **Proceed to Step 4a** — use the legacy Python scripts. |
| `false` | (any) | Could not classify (refused, timeout, unknown SSL error). Do not assume plaintext. Stop and ask the user / re-probe. |

**Do NOT call legacy scripts against a TLS cluster** — `scripts/get_kwdb_ts_metrics.py` and `scripts/get_kwdb_statements.py` hard-code `http://` and carry no credentials, so TLS will reject them.

### Step 4: Apply anomaly rules

Apply anomaly judgment rules only when user requests alerting. See `references/anomaly-rules.md` for default rules and configurable rules.

### Step 4a: Collect metrics via legacy scripts (insecure only)

This path runs **only** when Step 3 confirmed plaintext deployment.

#### Time-series metrics → `scripts/get_kwdb_ts_metrics.py`

Call the script via `python3 scripts/get_kwdb_ts_metrics.py` per `references/ts-metrics-script-usage.md`. Pass `--host`, optionally `--port`, `--start`, `--end`, `--sample`, and any number of `--metric` filters.

#### Slow SQL → `scripts/get_kwdb_statements.py`

Call the script via `python3 scripts/get_kwdb_statements.py` per `references/statements-script-usage.md`. Pass `--host`, optionally `--port`, `--limit`, `--min-latency-ms`, `--sort-by`.

Both scripts print results to stdout; treat empty stdout (`"命令执行成功，但未产生输出"`) as a failure and report it to the user.

### Step 5: Generate report

Produce a Markdown inspection report with metric values, anomaly judgments, and data-source notes per `references/output-rules.md`. Use `get_local_timestamp.py` to obtain the report timestamp; never fabricate it from training data or `datetime.utcnow()`. PDF / HTML rendering goes through `markdown-to-html` / `pdf` skills.

## Limitations

- **Windows is not supported**.
- **Legacy script path requires insecure deployment.** `scripts/get_kwdb_ts_metrics.py` and `scripts/get_kwdb_statements.py` hard-code plain HTTP and lack Basic Auth, so they only work against plaintext KaiwuDB clusters. For TLS deployments, deploy `kwdb-mcp-server` v3.2.0+ and the skill takes the MCP path in Step 2 instead.
- **No third-party Python deps in skill scripts**: all scripts are stdlib-only. Existing scripts (`md_to_*.sh` etc.) declare their packages via the shared `_venv.sh` wrapper.
- **The MCP path requires `kwdb-mcp-server` to be deployed and verified.** Without it, the skill cannot collect metrics or slow SQL against TLS clusters and can only fall back to plaintext-only legacy scripts. See `references/kwdb-mcp-server-setup.md` for the deployment contract.

## References

| File | Purpose | When to read |
|---|---|---|
| `references/kwdb-mcp-server-setup.md` | Detect, deploy, restart, verify `kwdb-mcp-server`; header semantics; common pitfalls | Before Step 1 if `query-metrics` / `query-slow-sql` are unavailable or erroring; before any restart |
| `references/inspection-requirements-confirmation.md` | Step 1 confirmation flow (intent parse → port probe → scope confirm) | Step 1 of the workflow |
| `references/probe-ports-script-usage.md` | CLI reference for `scripts/probe_ports.py` | Step 1 connectivity probe |
| `references/detect-tls-mode-script-usage.md` | CLI reference for `scripts/detect_tls_mode.py` | Step 3 (legacy fallback only) |
| `references/ts-metrics-script-usage.md` | CLI reference for `scripts/get_kwdb_ts_metrics.py` | Step 4a time-series (legacy fallback) |
| `references/statements-script-usage.md` | CLI reference for `scripts/get_kwdb_statements.py` | Step 4a slow SQL (legacy fallback) |
| `references/get-local-timestamp-script-usage.md` | CLI reference for `scripts/get_local_timestamp.py` | Step 5 report timestamp |
| `references/metric-types.md` | Closed catalog of 32 inspection metric names | Step 2 metric selection |
| `references/anomaly-rules.md` | Default + configurable anomaly thresholds | Step 4 (only when alerting is requested) |
| `references/output-rules.md` | Markdown report format + data-source notes | Step 5 report generation |
| `references/report-template.md` | Sections 1-6 report structure | Step 5 report generation |
