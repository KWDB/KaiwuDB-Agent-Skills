#!/usr/bin/env python3
"""TCP port reachability probe.

Stdlib only (`asyncio` + `socket`). Probes a batch of remote ports and emits
a single JSON document on stdout. Unreachable ports are normal results, not
errors - exit 0 unless CLI args are invalid. The host must not be a loopback
address; the script is for *remote* probing per the skill contract.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from ipaddress import ip_address

MAX_PORTS = 32
LOOPBACK_NAMES = {"localhost", "ip6-localhost", "ip6-loopback"}


class _ProbePortsParser(argparse.ArgumentParser):
    """Argparse wrapper that exits with status 1 on bad CLI args.

    argparse's default `error()` (and `parse_args()` failure path) exits with
    status 2. The probe_ports contract requires exit 1 for any bad-arg case.
    `-h`/`--help` is handled by argparse's own `print_help` + `sys.exit(0)`
    BEFORE `error()` is reached, so the override below leaves the help path
    intact.
    """

    def error(self, message):
        self.print_usage(sys.stderr)
        raise SystemExit(f"probe_ports: {message}")


def _parse_args() -> argparse.Namespace:
    p = _ProbePortsParser(description="Probe TCP reachability for a batch of remote ports.")
    p.add_argument("--host", required=True, help="Remote host (IP or non-loopback DNS name).")
    p.add_argument("--port", type=int, required=True, action="append",
                   help="Port to probe (1..65535). Repeat up to 32 times.")
    p.add_argument("--timeout", type=int, default=5, help="Per-port timeout seconds (1..30).")
    args = p.parse_args()
    if not (1 <= args.timeout <= 30):
        p.error("--timeout must be in 1..30")
    if args.host.lower() in LOOPBACK_NAMES:
        p.error("--host must not be a loopback name")
    try:
        ip = ip_address(args.host)
        if ip.is_loopback:
            p.error("--host must not be a loopback IP literal (e.g. 127.0.0.1, ::1)")
    except ValueError:
        if args.host.strip() == "":
            p.error("--host must be a non-empty IP or DNS name")
    if not args.port:
        p.error("at least one --port is required")
    seen = set()
    deduped = []
    for port in args.port:
        if port in seen:
            continue
        seen.add(port)
        deduped.append(port)
    if len(deduped) > MAX_PORTS:
        p.error(f"too many --port entries ({len(deduped)} > {MAX_PORTS})")
    for port in args.port:
        if not (1 <= port <= 65535):
            p.error(f"--port must be in 1..65535, got {port}")
    args.port = deduped
    return args


async def _probe(host: str, port: int, timeout: float) -> dict:
    start = time.monotonic()
    try:
        fut = asyncio.open_connection(host=host, port=port)
        reader, writer = await asyncio.wait_for(fut, timeout=timeout)
    except asyncio.TimeoutError:
        return {"port": port, "reachable": False,
                "response_time_ms": int((time.monotonic() - start) * 1000),
                "error": "timeout"}
    except OSError as exc:
        return {"port": port, "reachable": False,
                "response_time_ms": int((time.monotonic() - start) * 1000),
                "error": type(exc).__name__}
    writer.close()
    try:
        await writer.wait_closed()
    except Exception:
        pass
    return {"port": port, "reachable": True,
            "response_time_ms": int((time.monotonic() - start) * 1000)}


async def _run(args: argparse.Namespace) -> int:
    results = await asyncio.gather(
        *(_probe(args.host, p, args.timeout) for p in args.port)
    )
    print(json.dumps({"host": args.host, "results": list(results)}, ensure_ascii=False))
    return 0


def main() -> int:
    args = _parse_args()
    return asyncio.run(_run(args))


if __name__ == "__main__":
    sys.exit(main())
