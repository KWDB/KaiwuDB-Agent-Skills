# kwdb-intelligent-inspection Design Spec

## Function Overview

Perform metrics inspection on the KaiwuDB database and generate a readable report containing key database and system metrics as well as abnormal status alerts.

## Hard Constraints

- The skill does not support inspecting KaiwuDB deployed with TLS mode enabled.
- Metrics data must be fetched exclusively via the `/ts/query` API endpoint (except for slow query information and port listening status, which use other methods).
- The report must include metrics for all nodes in the database cluster.

## Report Template (Default)

| Metric Categories | Metric Name | Metrics |
| --- | --- | --- |
| Basic Metrics | Node Running Status | Process uptime: `sys.uptime`<br>Number of live nodes in the cluster: `liveness.livenodes` |
| Basic Metrics | Node Liveness Information | Number of live nodes in the cluster: `liveness.livenodes`<br>Successful node liveness heartbeats: `liveness.heartbeatsuccesses`<br>Failed node liveness heartbeats: `liveness.heartbeatfailures`<br>Node liveness heartbeat latency: `liveness.heartbeatlatency` |
| Basic Metrics | Service Port Listening Status | Port listening status (true/false) for default database port 26257 and admin console port 8080. Inspection is performed via `check_kwdb_port_listener.sh` script, which uses OS-level commands (`ss` on Linux, `lsof` on macOS) to check if the ports are listening. Output format: JSON array with fields: `port`, `listening`, `process_hint`, `raw_line`. |
| System Resources | CPU Utilization | Current user CPU percentage: `sys.cpu.user.percent`<br>Current system CPU percentage: `sys.cpu.sys.percent`<br>Combined user+system CPU percentage, normalized by core count: `sys.cpu.combined.percent-normalized` |
| System Resources | Memory Utilization | Current process RSS memory: `sys.rss`<br>Current bytes allocated by Go runtime: `sys.go.allocbytes`<br>Total bytes allocated by Go runtime (including unreleased): `sys.go.totalbytes` |
| System Resources | Disk Utilization | Total storage capacity: `capacity`<br>Available storage capacity: `capacity.available`<br>Used storage capacity: `capacity.used` |
| Database Performance | Write/Query QPS | Number of INSERT statements successfully executed: `sql.insert.count`<br>Number of UPDATE statements successfully executed: `sql.update.count`<br>Number of DELETE statements successfully executed: `sql.delete.count`<br>Keys written per second (Raft-applied, rebalancing average): `rebalancing.writespersecond`<br>Number of SELECT statements successfully executed: `sql.select.count`<br>Number of SQL queries executed: `sql.query.count`<br>KV-level requests received per second (rebalancing average): `rebalancing.queriespersecond` |
| Database Performance | Exec Latency | Latency of SQL statement execution: `sql.exec.latency`<br>Latency of SQL request execution (service time): `sql.service.latency`<br>Latency of DistSQL statement execution: `sql.distsql.exec.latency` |
| Database Performance | Slow Query Information | Not yet supported. The `/ts/query` API does not expose slow query metrics. Alternative APIs such as `/api/v2/statements` and `/api/v2/insights` are removed in the open-source edition. In TLS mode, authentication requires the AdminUI login endpoint which needs captcha verification that cannot be solved in non-interactive script mode. |
| Storage | Total Data Size | Total bytes of keys and values including non-live data: `totalbytes`<br>Bytes of live data (keys + values): `livebytes`<br>Used storage capacity: `capacity.used` |
| Cluster | Replica Status | Number of replicas: `replicas`<br>Number of Raft leaders: `replicas.leaders`<br>Number of lease holders: `replicas.leaseholders`<br>Number of quiesced replicas: `replicas.quiescent`<br>Ranges with fewer replicas than quorum requires: `ranges.unavailable`<br>Ranges with fewer replicas than replication target: `ranges.underreplicated`<br>Ranges with more replicas than replication target: `ranges.overreplicated` |
| Cluster | Replication Sync Status | WAL replication lag latency: `wal.replica.data.latency`<br>Raft log entries followers are behind: `raftlog.behind`<br>Raft replicate consistent latency: `raft.replica.consistent.latency` |
| Cluster | Data Distribution Balance | Ranges with fewer replicas than replication target: `ranges.underreplicated`<br>Ranges with more replicas than replication target: `ranges.overreplicated`<br>Keys written per second (rebalancing average): `rebalancing.writespersecond`<br>KV requests per second (rebalancing average): `rebalancing.queriespersecond` |
| Network | Peer-to-peer Latency Between Nodes | Round-trip latency distribution with other nodes: `round-trip-latency`<br>Mean clock offset with other nodes: `clock-offset.meannanos` |

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
| Replication Lag | Replica sync lag exceeds a threshold | 5s |

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
