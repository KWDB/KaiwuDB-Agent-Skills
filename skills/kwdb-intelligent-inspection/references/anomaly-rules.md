## Anomaly Rules

These rules apply only when the user requests alerting. If no alerting is requested, skip all rules.

### Default Rules (applied when user requests alerting without custom thresholds)

1. **Database Down**: `liveness.livenodes == 0` or port listener check failure
2. **Port Anomaly**: Port 26257 or 8080 not listening
3. **Frequent Restarts**: Database restarts > 1 time/day
4. **Replica sync lag > 5s**: `wal.replica.data.latency` via `/ts/query` API

### Configurable Rules (require explicit user threshold)

- **CPU > threshold%**: `sys.cpu.combined.percent-normalized`
- **Memory > threshold%**: `sys.rss`
- **QPS anomaly**: requires sampling window, do not claim from single snapshot
- **Write/Query latency anomaly**: requires sampling window, do not claim from single snapshot
