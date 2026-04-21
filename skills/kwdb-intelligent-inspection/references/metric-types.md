## Metric Types

This document maps each inspectable metric to its `/ts/query` query params. Query params are read from this file when constructing API requests — do not infer or invent values.

### Notation

- `d` = downsampler
- `sa` = source_aggregator
- `der` = derivative

### Gauge / Counter Metrics

These metrics use: `d:1, sa:2, der:0`

| Metric Name |
|-------------|
| `liveness.livenodes` |
| `sys.uptime` |
| `sys.cpu.user.percent` |
| `sys.cpu.sys.percent` |
| `sys.cpu.combined.percent-normalized` |
| `capacity` |
| `capacity.available` |
| `capacity.used` |
| `sys.rss` |
| `sys.go.allocbytes` |
| `sys.go.totalbytes` |
| `sql.insert.count` |
| `sql.update.count` |
| `sql.delete.count` |
| `rebalancing.writespersecond` |
| `sql.select.count` |
| `sql.query.count` |
| `rebalancing.queriespersecond` |
| `totalbytes` |
| `livebytes` |
| `replicas` |
| `replicas.leaders` |
| `replicas.leaseholders` |
| `ranges.unavailable` |
| `ranges.underreplicated` |
| `ranges.overreplicated` |
| `raftlog.behind` |

### Latency Metrics

These metrics use: `d:1, sa:1, der:0`

| Metric Name |
|-------------|
| `sql.exec.latency` |
| `sql.service.latency` |
| `sql.distsql.exec.latency` |
| `wal.replica.data.latency` |
| `raft.replica.consistent.latency` |
| `round-trip-latency` |
| `clock-offset.meannanos` |
