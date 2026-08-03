---
name: probe_ports.py script usage
description: Exact CLI reference for the remote TCP port probe. Read before calling the script for the first time.
---

# `probe_ports.py` - CLI Reference

依赖: Python 标准库（`asyncio` + `socket`）。

Entry point: `scripts/probe_ports.py`. **Stdlib only - no `nc` / `curl` / `wget` / `telnet`.**

## Synopsis

```
python3 scripts/probe_ports.py \
    --host <remote_ip_or_dns> \
    --port <port1> [--port <port2> ...] \
    [--timeout 5]
```

## Options

| Flag | Required | Default | Notes |
|------|----------|---------|-------|
| `--host` | yes | - | Remote host. **Must not be `localhost` / `127.0.0.1` / `::1`** - this script is for *remote* reachability. |
| `--port` | yes (repeat) | - | 1..65535. Repeatable, up to 32 unique entries (duplicates silently deduped, first occurrence wins). |
| `--timeout` | no | `5` | Per-port seconds, 1..30. |

## Output

Single JSON object on stdout:

```json
{
  "host": "10.0.0.1",
  "results": [
    {"port": 26257, "reachable": true,  "response_time_ms": 12},
    {"port": 8080,   "reachable": false, "response_time_ms": 5000, "error": "ConnectionRefusedError"}
  ]
}
```

`error` is present only when `reachable` is false. `response_time_ms` is always present (elapsed wall-clock to either connect or fail).

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Probing completed (any combination of reachable / unreachable). |
| 1 | Bad CLI args (missing host, no ports, too many ports, out-of-range port, etc.). |

Network errors are reported in the JSON, not as a non-zero exit code.

## Common Mistakes

- **Probing `localhost` / `127.0.0.1`**: rejected at the CLI layer. Use the `bash` / `python` scripts for local checks.
- **Passing `--port` as a bare positional (e.g. `python3 scripts/probe_ports.py 26257` without the leading `--port` flag)**: the script will treat `26257` as a positional arg and fail with "the following arguments are required: --host, --port". Always wrap numeric port values in the matching `--port` flag (e.g. `--port 26257`).
- **Single port per call vs. batch**: this script is the batch version. Call once with all ports you need; do not loop `--port` yourself.
- **Treating `unreachable` as a failure**: an unreachable port is normal data. Re-read the workflow rules in `inspection-requirements-confirmation.md` before retrying.
