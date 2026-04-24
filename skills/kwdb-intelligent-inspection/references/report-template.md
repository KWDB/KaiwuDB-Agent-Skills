## Required Report Sections

The default inspection report must cover these sections unless the user explicitly narrows scope.

### Data Source Priority

1. **Port listener status**: Use Workflow Step 1 connectivity probe results (no fixed script) in SKILL.md
2. **Slow queries**: Use `scripts/get_kwdb_statements.py` (`/_status/statements` API)
3. **All other metrics**: Use `scripts/get_kwdb_ts_metrics.py` (`/ts/query` API)

### Report Sections

#### 1. Basic Indicators

- Database running state (`liveness.livenodes`)
- Uptime (`sys.uptime`)

#### 2. System Resources

- CPU user % (`sys.cpu.user.percent`)
- CPU sys % (`sys.cpu.sys.percent`)
- CPU combined % normalized (`sys.cpu.combined.percent-normalized`)
- Disk total/available/used (`capacity`, `capacity.available`, `capacity.used`)
- Memory RSS (`sys.rss`)
- Go alloc/total bytes (`sys.go.allocbytes`, `sys.go.totalbytes`)

#### 3. Database Performance

- Write QPS: insert + update + delete + rebalancing writes
- Query QPS: select + query + rebalancing queries
- Exec latency: sql.exec.latency, sql.service.latency, sql.distsql.exec.latency
- Slow query information (via `/_status/statements` API)

#### 4. Storage

- Total data size (`totalbytes`, `livebytes`, `capacity.used`)

#### 5. Cluster

- Replicas, Raft leaders, Lease holders (`replicas`, `replicas.leaders`, `replicas.leaseholders`)
- Unavailable/Under-replicated/Over-replicated ranges
- Sync lag (`wal.replica.data.latency`, `raftlog.behind`, `raft.replica.consistent.latency`)
- Data distribution balance

#### 6. Network

- Node-to-node latency (`round-trip-latency`, `clock-offset.meannanos`)
