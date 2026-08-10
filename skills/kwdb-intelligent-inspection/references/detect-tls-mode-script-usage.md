---
name: detect_tls_mode.py script usage
description: Exact CLI reference for the TLS-mode detector. Read before calling the script for the first time.
---

# `detect_tls_mode.py` - CLI Reference

依赖: Python 标准库（`ssl` + `asyncio` + `socket`）。

Entry point: `scripts/detect_tls_mode.py`. **Replaces the legacy `curl -k https://<host>:<port>/health` recipe.**

## Synopsis

```
python3 scripts/detect_tls_mode.py \
    --host <remote_ip_or_dns> \
    --port <admin_port> \
    [--timeout 5]
```

## Options

| Flag | Required | Default | Notes |
|------|----------|---------|-------|
| `--host` | yes | - | Remote host. **Must not be a loopback name** (`localhost`, `ip6-localhost`, `ip6-loopback`) **or loopback IP literal** (`127.0.0.1`, `::1`); use the remote IP or non-loopback DNS name. |
| `--port` | yes | - | 1..65535. |
| `--timeout` | no | `5` | 1..15 seconds. |

## Output

Single JSON object on stdout:

```json
{"host": "...", "port": 8080, "determined": true,  "tls_enabled": true,  "detail": "tls handshake ok"}
{"host": "...", "port": 8080, "determined": true,  "tls_enabled": false, "detail": "wrong version number"}
{"host": "...", "port": 8080, "determined": false, "error":  "ConnectionRefusedError: ..."}
```

| Field | When |
|-------|------|
| `determined: true, tls_enabled: true` | Handshake succeeded -> TLS is enforced. Inspection **requires kwdb-mcp-server MCP tools** (`query-metrics` / `query-slow-sql`); legacy scripts in this skill are insecure-only. |
| `determined: true, tls_enabled: false` | Server explicitly rejected TLS (`wrong version number` / `0A00010B`) -> plaintext. |
| `determined: false` | Other failures (refused, timed out, network error, unknown SSL error). **Do not assume plaintext.** |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Classification completed (any of the three outcomes above). |
| 1 | Bad CLI args. |

## Common Mistakes

- **Treating `determined: false` as plaintext**: the script refuses to guess. Stop the workflow and ask the user / check reachability with `probe_ports.py` first.
- **Replacing this with `curl -k`**: the `kwdb-intelligent-inspection` skill explicitly forbids `curl` / `wget` invocations; use this script instead.
- **Calling on `localhost` / `127.0.0.1` / `::1`**: rejected at the CLI layer.
- **Passing `--port` as a JSON number without the leading `--port` flag**: the script's argparse treats bare numeric args as positionals (and will error with "the following arguments are required: --host, --port"). Always wrap every port value in the matching `--port` flag, never as a bare positional.
