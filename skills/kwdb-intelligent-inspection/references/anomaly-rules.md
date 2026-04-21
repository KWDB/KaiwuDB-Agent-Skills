## Anomaly Rules

Apply these default judgments unless the user overrides thresholds. Rules marked as **fixed** cannot be overridden.

### Fixed Rules (always applied)

These rules are **always enforced** and cannot be disabled:

1. **Database Down**: Database service/process/container has died — detected via `liveness.livenodes == 0` or port listener check failure.
2. **Port Anomaly**: Default database port 26257 or admin console port 8080 is not listening — detected via `scripts/check_kwdb_port_listener.sh`.
3. **Frequent Restarts**: Database restarts more than once per day — detected via `scripts/count_kwdb_restart_events.sh`.
4. **Replica sync lag > 5s**: judge from `wal.replica.data.latency` via `/ts/query` API.

### Configurable Rules (disabled by default)

These rules are **not enabled by default** — only apply them when the user explicitly specifies a threshold:

- **CPU > threshold%**: judge from `sys.cpu.combined.percent-normalized` via `/ts/query` API.
- **Memory > threshold%**: judge from `sys.rss` via `/ts/query` API (process-level RSS).
- **QPS anomaly**: write/query QPS sudden spike or drop — mark as `requires sampling window`, do not overclaim from one snapshot.
- **Write/Query latency anomaly**: latency is high or spikes suddenly — mark as `requires sampling window`, do not overclaim from one snapshot.
