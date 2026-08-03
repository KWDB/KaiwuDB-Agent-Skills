# Port Reachability Detection Reference

## Critical Constraint (non-negotiable)

**Do not SSH into the target server to run inspection commands there.**
Always use local tools on the machine where the inspection is being
performed. Reachability is checked via the local script
`scripts/probe_ports.py` invoked directly with `python3`. This script
uses Python stdlib only (`asyncio` + `socket`); it does **not** shell
out to `nc` / `curl` / `wget` / `telnet`.

## Default Ports

| Service | Default Port | Description |
|---------|-------------|-------------|
| SQL Port | `26257` | KaiwuDB SQL/API port |
| Admin Console | `8080` | Admin UI port |

## Invocation

```
python3 scripts/probe_ports.py \
    --host <target_ip_or_dns> \
    --port 26257 \
    --port 8080 \
    [--timeout 5]
```

## Result Handling

The script returns a JSON document with one entry per port:
`port`, `reachable`, `response_time_ms`, and an `error` field when
`reachable` is false. Iterate the results and report per-port status
to the user. Do not infer a global "host is down" from a single port.

## Multi-port Scanning

Call `probe_ports.py` once with all required `--port` flags. The script
deduplicates ports and caps the batch at 32. The skill workflow always
passes both 26257 and 8080 in a single call.

## Tool Installation

`probe_ports.py` is a single Python file with no third-party
dependencies. If `python3` is missing on the host, the runtime image
must be rebuilt — do not attempt to install Python on demand.

## Expected Output

```json
{
  "host": "10.110.10.146",
  "results": [
    {"port": 26257, "reachable": true,  "response_time_ms": 12},
    {"port": 8080,   "reachable": false, "response_time_ms": 5000, "error": "ConnectionRefusedError"}
  ]
}
```
