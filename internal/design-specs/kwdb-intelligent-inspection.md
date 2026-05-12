# kwdb-intelligent-inspection Design Spec

## Function Overview

Perform metrics inspection on the KaiwuDB database and generate a readable report containing key database and system metrics as well as abnormal status alerts.

## Hard Constraints

- Metrics data must be fetched exclusively via the `/ts/query` API endpoint (except for slow query information and port listening status, which use other methods).
- The report must include metrics for all nodes in the database cluster.
- Before inspection, detect TLS mode using the method in [Limitations](#limitations).

## Report Template (Default)

| Metric Categories | Metric Name | Metrics |
| --- | --- | --- |
| Basic Metrics | Node Running Status | Process uptime: `cr.node.sys.uptime`<br>Number of live nodes in the cluster: `cr.node.liveness.livenodes` |
| Basic Metrics | Node Liveness Information | Number of live nodes in the cluster: `cr.node.liveness.livenodes`<br>Successful node liveness heartbeats: `cr.node.liveness.heartbeatsuccesses`<br>Failed node liveness heartbeats: `cr.node.liveness.heartbeatfailures`<br>Node liveness heartbeat latency: `cr.node.liveness.heartbeatlatency` |
| Basic Metrics | Service Port Listening Status | Port listening status (true/false) for default database port 26257 and admin console port 8080. Inspection is performed via `check_kwdb_port_listener.sh` script, which uses OS-level commands (`ss` on Linux, `lsof` on macOS) to check if the ports are listening. Output format: JSON array with fields: `port`, `listening`, `process_hint`, `raw_line`. |
| System Resources | CPU Utilization | Current user CPU percentage: `cr.node.sys.cpu.user.percent`<br>Current system CPU percentage: `cr.node.sys.cpu.sys.percent`<br>Combined user+system CPU percentage, normalized by core count: `cr.node.sys.cpu.combined.percent-normalized` |
| System Resources | Memory Utilization | Current process RSS memory: `cr.node.sys.rss`<br>Current bytes allocated by Go runtime: `cr.node.sys.go.allocbytes`<br>Total bytes allocated by Go runtime (including unreleased): `cr.node.sys.go.totalbytes` |
| System Resources | Disk Utilization | Total storage capacity: `cr.store.capacity`<br>Available storage capacity: `cr.store.capacity.available`<br>Used storage capacity: `cr.store.capacity.used` |
| Database Performance | Write/Query QPS | Number of INSERT statements successfully executed: `cr.node.sql.insert.count`<br>Number of UPDATE statements successfully executed: `cr.node.sql.update.count`<br>Number of DELETE statements successfully executed: `cr.node.sql.delete.count`<br>Keys written per second (Raft-applied, rebalancing average): `cr.store.rebalancing.writespersecond`<br>Number of SELECT statements successfully executed: `cr.node.sql.select.count`<br>Number of SQL queries executed: `cr.node.sql.query.count`<br>KV-level requests received per second (rebalancing average): `cr.store.rebalancing.queriespersecond` |
| Database Performance | Exec Latency | Latency of SQL statement execution: `cr.node.exec.latency-p99`<br>Latency of SQL request execution (service time): `cr.node.sql.service.latency-p99`<br>Latency of DistSQL statement execution: `cr.node.sql.distsql.exec.latency-p99` |
| Database Performance | Slow Query Information | Available via `/_status/statements` API using `scripts/get_kwdb_statements.py` |
| Storage | Total Data Size | Total bytes of keys and values including non-live data: `cr.store.totalbytes`<br>Bytes of live data (keys + values): `cr.store.livebytes`<br>Used storage capacity: `cr.store.capacity.used` |
| Cluster | Replica Status | Number of replicas: `cr.store.replicas`<br>Number of Raft leaders: `cr.store.replicas.leaders`<br>Number of lease holders: `cr.store.replicas.leaseholders`<br>Ranges with fewer replicas than quorum requires: `cr.store.ranges.unavailable`<br>Ranges with fewer replicas than replication target: `cr.store.ranges.underreplicated`<br>Ranges with more replicas than replication target: `cr.store.ranges.overreplicated` |
| Cluster | Replication Sync Status | WAL replication lag latency: `cr.store.raft.replica.consistent.latency-p99`<br>Raft log entries followers are behind: `cr.store.raftlog.behind`<br>Raft replicate consistent latency: `cr.store.raft.replica.consistent.latency-p99` |
| Cluster | Data Distribution Balance | Ranges with fewer replicas than replication target: `cr.store.ranges.underreplicated`<br>Ranges with more replicas than replication target: `cr.store.ranges.overreplicated`<br>Keys written per second (rebalancing average): `cr.store.rebalancing.writespersecond`<br>KV requests per second (rebalancing average): `cr.store.rebalancing.queriespersecond` |
| Network | Peer-to-peer Latency Between Nodes | Round-trip latency distribution with other nodes: `round-trip-latency`<br>Mean clock offset with other nodes: `cr.node.clock-offset.meannanos` |

## Anomaly Detection Rules

| Condition | Description | Default Rules |
| --- | --- | --- |
| Database Down | The database service/process/container has died | Fixed rule, cannot be overridden |
| Frequent Restarts | Database restarts frequently | Restart interval less than 1 day |
| Port Anomaly | Port listening anomaly | Default database listening port: 26257; default management console port: 8080 |
| High CPU Utilization | CPU utilization continuously above 80%; high CPU but low QPS; sudden CPU drop | No alert by default unless the user specifies an explicit rule |
| High Memory Usage | Memory utilization exceeds 80% of available memory | No alert by default unless the user specifies an explicit rule |
| QPS Anomaly | Write/query QPS sudden spike or drop | No alert by default unless the user specifies an explicit rule |
| Write/Query Latency Anomaly | Write/query latency is high or spikes suddenly | No alert by default unless the user specifies an explicit rule |
| Replication Lag | Replica sync lag exceeds a threshold | `cr.store.raft.replica.consistent.latency-p99` > 5s |
| Unavailable Replicas | Range unavailable count exceeds threshold | `cr.store.ranges.unavailable` > 0 |

## Report Format

- **Default**: Markdown
- **Optional**: HTML / PDF

## Alert Threshold Configuration

- Alert thresholds can be set/modified via **natural language messages**; the LLM interprets them and converts them into structured parameters.
  - Example: `Set the CPU alert threshold to 90% and the replica sync lag threshold to 10s`
- Confirm threshold changes with an **echo confirmation** before applying them.

## Confirmation Workflow

Before collecting any metrics, present the full menu of available inspection dimensions to the user:
1. List all metrics under **Required Report Sections** (Basic indicators, System resources, Database performance, Storage, Cluster, Network).
2. List all anomaly rules under **Anomaly Rules**, separating **Fixed Rules** (always applied, cannot be disabled) from **Configurable Rules** (disabled by default, require explicit user enablement and threshold).
3. Ask the user to confirm which metrics to inspect and which configurable rules (with what thresholds) to enable.
4. Only proceed to metric collection after user confirmation.

## Limitations

- This skill does not support Windows operating systems.
- **TLS mode inspection is not supported**: This skill does not support inspecting KaiwuDB deployed with TLS mode enabled. Detection method: use `curl --insecure https://<host>:8080/_status/statements` to check if it returns an SSL error.
