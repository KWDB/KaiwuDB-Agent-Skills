---
name: kwdb-intelligent-inspection
description: Run KaiwuDB inspection and health-check tasks. Use this skill for database health checks, metrics collection, anomaly detection, and inspection report generation.
---

Read `references/inspection-config.md` to understand available tools and their capabilities. Read `references/inspection-sql-reference.md` for the canonical inspection SQL reference before starting an inspection task.

## Workflow

1. Confirm the inspection scope, time range, target nodes, threshold overrides, and output format with the user.
2. Check if `read-query` MCP tool is available:
   - **If available**: Execute the inspection SQL queries from `references/inspection-sql-reference.md` via `read-query` to collect internal database metrics.
   - **If unavailable**: Fall back to shell scripts under `scripts/` and report metrics as unavailable.
3. Supplement with OS-level metrics using shell scripts under `scripts/` when SQL cannot provide stable answers:
   - `scripts/get_node_resource_snapshot.sh` - Host-level CPU, memory, Swap, disk metrics
   - `scripts/get_kwdb_service_status.sh` - Service running status
   - `scripts/check_kwdb_port_listener.sh` - Port listener status
   - `scripts/read_kwdb_recent_logs.sh` - Recent logs
   - `scripts/count_kwdb_restart_events.sh` - Restart event count
   - `scripts/check_node_network_connectivity.sh` - Node-to-node connectivity
4. Apply anomaly judgment rules against collected metrics.
5. Produce a Markdown inspection report with metric values, anomaly judgments, and data-source notes.

## Data Collection Strategy

### SQL-First (via read-query)

When `read-query` is available, **always prefer** executing the inspection SQL queries from `references/inspection-sql-reference.md`. The SQL reference provides:
- Node running state and liveness (`basic`)
- CPU, memory, uptime metrics (`system_resources`)
- Disk usage and data size (`storage`)
- Query/write counts and latency (`db_performance`)
- Slow SQL candidates (`db_performance`)
- Replica health and sync lag (`cluster`)
- Network latency evidence (`network`)

### Shell Scripts under `scripts/`

When SQL cannot provide a stable answer, use the shell scripts under `scripts/`. All scripts support both Linux and macOS.

- **`scripts/get_node_resource_snapshot.sh`**: Get host-level CPU, memory, Swap, and disk metrics
  - From `/proc/meminfo`: total memory, available memory, used memory, and usage percentage (Linux)
  - From `sysctl`: memory information (macOS)
  - From `/proc/loadavg`: CPU cores and 1-minute load average (Linux)
  - From `uptime`: load average (macOS)
  - From `df`: total disk, used, available space, and usage percentage
  - **Note**: This script provides system-level memory usage, which differs from SQL's `sys.rss` (process RSS). Reports should distinguish between these two data sources.

- **`scripts/check_kwdb_port_listener.sh`**: Check if KWDB ports are actually listening at the OS level
  - Accepts port list parameter (default: 26257,8080)
  - Uses `ss` or `netstat` to detect listening status (Linux)
  - Uses `netstat` or `lsof` to detect listening status (macOS)
  - Used for port listener anomaly detection

- **`scripts/get_kwdb_service_status.sh`**: Get KWDB service running status
  - Uses `systemctl` to get active/sub state, MainPID, and start time (Linux)
  - Uses `launchctl` to get service status (macOS)
  - Uses `ps` and `docker ps` to get process/container clues
  - Used for service status and uptime in basic indicators

- **`scripts/read_kwdb_recent_logs.sh`**: Read recent KWDB logs within a time window
  - Prefers `journalctl` (Linux), falls back to specified log files
  - Uses `log show` (macOS) to read system logs
  - Accepts since (default: 1 hour ago), lines (default: 200), and log_path parameters
  - Used for log analysis during anomaly investigation

- **`scripts/count_kwdb_restart_events.sh`**: Count KWDB restart events within a time window
  - Counts Starting/Started/Restarting/Stopped events from `journalctl` (Linux)
  - Falls back to `systemctl show -p NRestarts` (Linux)
  - Uses `launchctl` and `pgrep` (macOS)
  - Used for frequent restart detection (alert if >1 per day)

- **`scripts/check_node_network_connectivity.sh`**: Check TCP connectivity and latency to target nodes
  - Accepts comma-separated target host list and port parameter (default: 26257)
  - Uses `/dev/tcp` for TCP connectivity check (Linux), uses `nc` (macOS)
  - Measures latency via ping
  - Used for network connectivity and node-to-node latency detection

## Anomaly Rules

Apply these default judgments unless the user overrides thresholds:

1. **CPU > 80%**: judge from SQL `sys.cpu.combined.percent-normalized` or `scripts/get_node_resource_snapshot.sh` (loadavg_1m as load indicator).
2. **Replica sync lag > 5s**: judge from `kv.closed_timestamp.max_behind_nanos` related metrics.
3. **Replica unavailable / under-replicated**: judge from `system.replication_stats` and store metrics.
4. **Memory usage > 80%**: only make a strong judgment when `scripts/get_node_resource_snapshot.sh` (system-level) is available; SQL's `sys.rss` is process-level memory, not system memory usage.
5. **Frequent restart > 1/day**: use `scripts/count_kwdb_restart_events.sh`; do not infer only from a single `started_at`.
6. **CPU sustained high, CPU high but QPS low, CPU drop, QPS spike/drop, latency spike**:
   - mark as `requires sampling window`
   - do not overclaim from one snapshot
   - `current_long_queries` can be used as an auxiliary diagnosis for latency spike: if there are currently long-running queries, they may be one of the root causes of the latency spike

## Required Report Sections

The default inspection report must cover these sections unless the user explicitly narrows scope:

1. **Basic indicators**:
   - database running state
   - uptime
   - service port listener state
2. **System resources**:
   - CPU usage
   - disk usage
   - memory usage
3. **Database performance**:
   - write QPS / write latency
   - query QPS / query latency
   - slow SQL candidates
4. **Storage**:
   - total data size
5. **Cluster**:
   - replica health / sync lag
   - data distribution balance
6. **Network**:
   - node-to-node latency or connectivity evidence

For clusters, include all nodes in each applicable section and state clearly when evidence is complete versus partial.

## Output Rules

1. For every section, identify the data source as one of:
   - `SQL` (via read-query with inspection SQL reference)
   - `OS` (via shell scripts under `scripts/`)
   - `SQL + OS`
   - `needs sampling`
2. If a metric is only partially supported, say so explicitly.
3. If multi-node evidence is incomplete, say which part is inferred versus directly observed.
4. Return inline Markdown report rather than claiming a saved file path unless a file tool actually created that artifact.
5. If the task runs in cluster mode, the report must cover all nodes rather than only a single node snapshot.
6. Scheduled inspection should recover thresholds and time-range hints from the task prompt; if missing, use defaults and document that assumption.

## Guardrails

- **read-query first**: When `read-query` is available, always use the SQL statements from `references/inspection-sql-reference.md` for inspection. Do not bypass these SQL statements to query other tables directly.
- **No self-generated SQL**: When calling `read-query`, only use the whitelist SQL defined in `inspection-sql-reference.md`. Absolutely do not generate other SQL statements on your own (KWDB has special syntax; self-generated statements usually do not take effect and may cause dangerous operations).
- When SQL in `inspection-sql-reference.md` cannot retrieve a metric, **do not** construct SQL on your own. Instead, report the metric as unavailable and try to supplement with shell scripts under `scripts/`.
- HTML and PDF output are optional; default to Markdown.
- If the user explicitly asks for charts, you may hand structured metrics to a visualization tool, but chart generation failure must not block the main report.
