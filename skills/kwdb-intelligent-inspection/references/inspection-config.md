# kwdb-intelligent-inspection Inspection Tools Configuration

This document describes the inspection tools and data sources available to the kwdb-intelligent-inspection skill.

## Tool Overview

This skill uses two types of inspection tools:

1. **Shell Scripts under `scripts/`**: Located in the `scripts/` directory, used to collect OS-level metrics
2. **KWDB SQL Queries**: Executed via the `read-query` tool from `kwdb-mcp-server`, used to collect internal database metrics

## Shell Scripts under `scripts/`

### 1. get_node_resource_snapshot.sh

Get a snapshot of OS-level resource metrics for a node.

**Purpose**: Host-level CPU, memory, Swap, and disk metrics.

**Usage**:
```bash
bash scripts/get_node_resource_snapshot.sh
```

**Parameters**: None

**Returns**:
```json
{
  "os": "linux | darwin",
  "memory": {
    "total_bytes": "number",
    "available_bytes": "number",
    "used_bytes": "number",
    "usage_pct": "number"
  },
  "swap": {
    "total_bytes": "number",
    "free_bytes": "number",
    "usage_pct": "number"
  },
  "disk": {
    "mount": "string",
    "total_bytes": "number",
    "used_bytes": "number",
    "available_bytes": "number",
    "usage_pct": "number"
  },
  "cpu": {
    "cores": "number",
    "loadavg_1m": "number"
  }
}
```

**Cross-platform Support**: Linux (via /proc), macOS (via sysctl)

---

### 2. get_kwdb_service_status.sh

Check the running status of the KWDB service/process on a target node.

**Purpose**: Verify service availability and get process metadata.

**Usage**:
```bash
bash scripts/get_kwdb_service_status.sh [SERVICE_NAME]
```

**Parameters**:
- `SERVICE_NAME`: Optional, service name, defaults to `kwdb`

**Returns**:
```json
{
  "service_name": "string",
  "active_state": "active | inactive | unknown",
  "sub_state": "running | stopped | unknown",
  "main_pid": "string",
  "started_at": "string",
  "process_hint": "string",
  "container_hint": "string"
}
```

**Cross-platform Support**: Linux (systemctl), macOS (launchctl + pgrep)

---

### 3. check_kwdb_port_listener.sh

Check if KWDB common ports are actually listening at the OS level.

**Purpose**: Verify port binding status and confirm SQL/UI port availability.

**Usage**:
```bash
bash scripts/check_kwdb_port_listener.sh [PORTS]
```

**Parameters**:
- `PORTS`: Optional, comma-separated port list, defaults to `26257,8080`

**Returns**:
```json
[
  {
    "port": "number",
    "listening": "boolean",
    "process_hint": "string",
    "raw_line": "string"
  }
]
```

**Cross-platform Support**: Linux (ss/netstat), macOS (netstat/lsof)

---

### 4. read_kwdb_recent_logs.sh

Read recent KWDB log entries from a target node.

**Purpose**: Anomaly explanation through log analysis.

**Usage**:
```bash
bash scripts/read_kwdb_recent_logs.sh SINCE [LINES] [LOG_PATH]
```

**Parameters**:
- `SINCE`: Time window, e.g., "1 hour ago", defaults to "1 hour ago"
- `LINES`: Optional, maximum lines, defaults to 200
- `LOG_PATH`: Optional, log file path

**Returns**:
```json
{
  "since": "string",
  "line_count": "number",
  "logs": ["string", ...]
}
```

**Cross-platform Support**: Linux (journalctl), macOS (log show)

---

### 5. count_kwdb_restart_events.sh

Count service restart events within a time window.

**Purpose**: Detect frequent restarts indicating instability.

**Usage**:
```bash
bash scripts/count_kwdb_restart_events.sh [SINCE]
```

**Parameters**:
- `SINCE`: Optional, time window, e.g., "1 day ago", defaults to "1 day ago"

**Returns**:
```json
{
  "since": "string",
  "restart_count": "number"
}
```

**Cross-platform Support**: Linux (journalctl/systemctl), macOS (launchctl/pgrep)

---

### 6. check_node_network_connectivity.sh

Test TCP connectivity and basic latency between nodes.

**Purpose**: Verify inter-node connectivity and measure latency.

**Usage**:
```bash
bash scripts/check_node_network_connectivity.sh TARGET_HOSTS [PORT]
```

**Parameters**:
- `TARGET_HOSTS`: Comma-separated target host list (required)
- `PORT`: Optional, target port, defaults to 26257

**Returns**:
```json
{
  "port": "number",
  "targets": [
    {
      "host": "string",
      "reachable": "boolean",
      "latency_ms": "number | null"
    }
  ]
}
```

**Cross-platform Support**: Linux (/dev/tcp), macOS (nc/curl)

---

## KWDB SQL Query Tool

Execute SQL queries via the `read-query` tool from `kwdb-mcp-server` to collect internal database metrics.

### Available Inspection Query Categories

| Category | Description |
|----------|-------------|
| Node Running Status | Check if nodes are alive and accepting connections |
| CPU/Memory/Uptime | Resource metrics from database perspective |
| Disk Usage | Data directory and log directory capacity |
| Data Size and Range Distribution | Range-level data distribution |
| Query/Write Counts and Latency | QPS and transaction statistics |
| Slow SQL Candidates | Long-running queries |
| Current Long Queries | Currently running long queries |
| Replica Health Status | Replica synchronization and lag statistics |
| Store-level Metrics | Replica and rebalance metrics per Store |
| Network Latency Evidence | Inter-node RPC latency |

### Usage

```sql
-- Example: Query node status
SELECT * FROM crdb_internal.node_runtime_stats;

-- Example: Query replica status
SELECT * FROM crdb_internal.replica_stats;
```

Call via MCP tool:
```
kwdb_mcp_read_query(query="SELECT ...")
```

---

## Usage Guidelines

1. **Data Source Priority**:
   - OS-level metrics → Use shell scripts under `scripts/`
   - Internal database metrics → Use `read-query` from kwdb-mcp-server

2. **Cluster Mode**: When inspecting a cluster, execute scripts on all nodes and aggregate results.

3. **Partial Availability**: If some tools fail, record the failure reason in the report and continue with other available checks.

4. **Error Handling**: Script execution failures should not block the entire inspection process. Collect as much available data as possible and note any failures.

5. **Cross-platform Compatibility**: All scripts support both Linux and macOS, automatically detecting the OS type and using the appropriate commands.
