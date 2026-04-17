# KWDB Inspection SQL Reference

This document contains the standard SQL statements used for inspection, executed via the `read-query` MCP tool.

---

## 1. basic — Node Running Status

### node_running_state
```sql
SELECT node_id, address, sql_address, started_at, is_live, ranges, leases
FROM kwdb_internal.gossip_nodes
ORDER BY node_id;
```
**Description**: Query node running status, addresses, start time, liveness state, range count, and lease state.

---

### node_liveness
```sql
SELECT node_id, epoch, expiration, draining, decommissioning, upgrading, updated_at
FROM kwdb_internal.gossip_liveness
ORDER BY node_id;
```
**Description**: Query node liveness information, including epoch, expiration time, draining status, decommissioning status, and upgrading status.

---

## 2. system_resources — System Resources

### node_metrics
```sql
SELECT store_id, name, value
FROM kwdb_internal.node_metrics
WHERE name IN (
  'sys.uptime',
  'sys.cpu.combined.percent-normalized',
  'sys.rss',
  'sys.go.allocbytes'
)
ORDER BY name, store_id;
```
**Description**: Query node OS resource consumption metrics, including uptime, CPU usage, RSS memory, and Go memory allocation.

---

### disk_usage
```sql
SELECT node_id, store_id,
       ROUND(100.0 * used / NULLIF(capacity, 0), 2) AS disk_usage_pct,
       used, available, capacity
FROM kwdb_internal.kv_store_status
ORDER BY node_id, store_id;
```
**Description**: Query disk usage percentage and capacity information.

---

## 3. db_performance — Database Performance

### sql_counters_latency
```sql
SELECT store_id, name, value
FROM kwdb_internal.node_metrics
WHERE name IN (
  'sql.select.count',
  'sql.insert.count',
  'sql.update.count',
  'sql.delete.count',
  'sql.service.latency.avg',
  'sql.exec.latency'
)
ORDER BY name, store_id;
```
**Description**: Query SQL execution counts (SELECT/INSERT/UPDATE/DELETE) and latency metrics.

---

### slow_sql_candidates
```sql
SELECT node_id, application_name, database, count, failed_count,
       service_lat_avg, run_lat_avg, key
FROM kwdb_internal.node_statement_statistics
ORDER BY service_lat_avg DESC;
```
**Description**: Query slow SQL candidates, ordered by average service latency descending. Note: Returns candidates only; requires sampling window confirmation for definitive judgment.

---

### current_long_queries
```sql
SELECT query_id, node_id, user_name, start, query, phase
FROM kwdb_internal.cluster_queries
ORDER BY start;
```
**Description**: Query currently running long-running queries.

---

## 4. storage — Storage

### data_size_by_database
```sql
SELECT database_name, SUM(range_size) AS total_bytes, COUNT(*) AS range_count
FROM kwdb_internal.ranges
GROUP BY database_name
ORDER BY total_bytes DESC;
```
**Description**: Query total data size and range count grouped by database.

---

## 5. cluster — Cluster Replication and Balance

### replication_stats
```sql
SELECT *
FROM system.replication_stats;
```
**Description**: Query replication statistics, including replica count, synchronization status, and lag.

---

### store_balance_metrics
```sql
SELECT node_id, store_id,
       metrics->>'ranges.unavailable' AS unavailable_ranges,
       metrics->>'ranges.underreplicated' AS underreplicated_ranges,
       metrics->>'ranges.overreplicated' AS overreplicated_ranges,
       metrics->>'rebalancing.queriespersecond' AS rebalance_qps,
       metrics->>'rebalancing.writespersecond' AS rebalance_wps
FROM kwdb_internal.kv_store_status
ORDER BY node_id, store_id;
```
**Description**: Query store-level balance metrics, including unavailable replicas, under-replicated replicas, over-replicated replicas, and rebalancing QPS/WPS.

---

## 6. network — Network

### peer_latency
```sql
SELECT node_id, activity->'1'->>'latency' AS peer1_latency
FROM kwdb_internal.kv_node_status;
```
**Description**: Query peer-to-peer latency between nodes.

---

## Appendix: Anomaly Thresholds

| Metric | Threshold | Data Source |
|--------|-----------|-------------|
| CPU Usage | > 80% | SQL `sys.cpu.combined.percent-normalized` or Shell `get_node_resource_snapshot.sh` (loadavg) |
| Replica Sync Lag | > 5s | `kv.closed_timestamp.max_behind_nanos` related metrics |
| Memory Usage | > 80% | **Must** use Shell `get_node_resource_snapshot.sh` (system-level); SQL `sys.rss` is process RSS, not system memory usage |
| Restart Frequency | > 1 per day | Shell `scripts/count_kwdb_restart_events.sh` |

---

## Appendix: Metrics Requiring Sampling Window

The following metrics cannot be determined from a single snapshot and require a sampling window:

- `cpu_sustained_high` — Sustained high CPU
- `cpu_high_but_qps_low` — High CPU but low QPS
- `cpu_drop` — Sudden CPU drop
- `qps_spike_or_drop` — QPS spike or drop
- `latency_spike` — Latency spike

---

## Appendix: SQL Generation Restrictions

**Important**: When calling `read-query`, **only use the SQL statements defined in this reference document**. Absolutely do not generate other SQL statements on your own.

### Why Self-Generated SQL is Prohibited

KWDB database has specific syntax conventions. SQL statements generated by LLM on their own usually:
1. Do not take effect (syntax incompatibility)
2. May return incorrect results
3. In extreme cases, may cause dangerous operations (such as accidental data deletion)

### Error Handling

If SQL statements in this reference document fail to execute:
- **Do not** attempt to construct alternative SQL on your own
- Report the metric as unavailable
- Try to supplement with shell scripts under `scripts/`

### Whitelist SQL List

All SQL statements defined in this document are the whitelist allowed for execution:

- `basic` category: `node_running_state`, `node_liveness`
- `system_resources` category: `node_metrics`, `disk_usage`
- `db_performance` category: `sql_counters_latency`, `slow_sql_candidates`, `current_long_queries`
- `storage` category: `data_size_by_database`
- `cluster` category: `replication_stats`, `store_balance_metrics`
- `network` category: `peer_latency`