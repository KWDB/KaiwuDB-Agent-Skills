## Time Series Metrics Script Usage

Use `scripts/get_kwdb_ts_metrics.py` to collect time series metrics from KaiwuDB.

## Prerequisites

Before calling this script you MUST have already called
`probe_ports.py` to confirm the target admin port is reachable AND
`detect_tls_mode.py` to confirm TLS is not enforced. See
`inspection-requirements-confirmation.md` for the full workflow.

### Full Collection (all metrics)

```
python3 scripts/get_kwdb_ts_metrics.py --host <host>
```

### Partial Collection (specific metrics)

```
python3 scripts/get_kwdb_ts_metrics.py \
    --host <host> \
    --metric <metric_name> [--metric <metric_name> ...]
```

Example:
```
python3 scripts/get_kwdb_ts_metrics.py \
    --host 10.110.10.146 \
    --metric cr.node.sys.cpu.user.percent \
    --metric cr.node.sql.insert.count
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--host` | localhost | KaiwuDB admin host |
| `--port` | 8080 | KaiwuDB admin port |
| `--start` | 1 hour ago | Start time (unix timestamp in ns) |
| `--end` | now | End time (unix timestamp in ns) |
| `--sample` | 60 | Sample interval in seconds |
| `--metric` | all | Filter by metric name (can repeat) |

### Available Metrics

See `references/metric-types.md` for the complete list of available metrics.

### Success signal

The call is successful only when the script exits with code 0 and
stdout is present (not empty).
