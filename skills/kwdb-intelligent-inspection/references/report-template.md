## Required Report Sections

The default inspection report must cover these sections unless the user explicitly narrows scope. Each section identifies its data source as `API` (via `/ts/query`) or `OS` (via shell scripts under `scripts/`).

### 1. Basic Indicators

| Metric | Source | API Name |
|--------|--------|----------|
| Database running state | API | `liveness.livenodes` |
| Uptime | API | `sys.uptime` |
| Service port listener state | OS | `scripts/check_kwdb_port_listener.sh` |

### 2. System Resources

| Metric | Source | API Name |
|--------|--------|----------|
| CPU user % | API | `sys.cpu.user.percent` |
| CPU sys % | API | `sys.cpu.sys.percent` |
| CPU combined % (normalized) | API | `sys.cpu.combined.percent-normalized` |
| Disk total | API | `capacity` |
| Disk available | API | `capacity.available` |
| Disk used | API | `capacity.used` |
| Memory RSS | API | `sys.rss` |
| Go alloc bytes | API | `sys.go.allocbytes` |
| Go total bytes | API | `sys.go.totalbytes` |

### 3. Database Performance

| Metric | Source | API Name |
|--------|--------|----------|
| Write QPS (insert + update + delete + rebalancing writes) | API | `sql.insert.count`, `sql.update.count`, `sql.delete.count`, `rebalancing.writespersecond` |
| Query QPS (select + query + rebalancing queries) | API | `sql.select.count`, `sql.query.count`, `rebalancing.queriespersecond` |
| Exec latency | API | `sql.exec.latency`, `sql.service.latency`, `sql.distsql.exec.latency` |
| Slow query information | API | `/_status/statements` — use `scripts/get_kwdb_statements.py` to fetch slow query records |

### 4. Storage

| Metric | Source | API Name |
|--------|--------|----------|
| Total data size | API | `totalbytes`, `livebytes`, `capacity.used` |

### 5. Cluster

| Metric | Source | API Name |
|--------|--------|----------|
| Replicas | API | `replicas` |
| Raft leaders | API | `replicas.leaders` |
| Lease holders | API | `replicas.leaseholders` |
| Unavailable ranges | API | `ranges.unavailable` |
| Under-replicated ranges | API | `ranges.underreplicated` |
| Over-replicated ranges | API | `ranges.overreplicated` |
| Sync lag | API | `wal.replica.data.latency`, `raftlog.behind`, `raft.replica.consistent.latency` |
| Data distribution balance | API | `ranges.underreplicated`, `ranges.overreplicated`, `rebalancing.writespersecond`, `rebalancing.queriespersecond` |

### 6. Network

| Metric | Source | API Name |
|--------|--------|----------|
| Node-to-node latency | API | `round-trip-latency`, `clock-offset.meannanos` |
