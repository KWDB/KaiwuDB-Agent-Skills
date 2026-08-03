#!/usr/bin/env python3
"""Detect whether a KaiwuDB admin port enforces TLS.

Stdlib only. Performs a TLS handshake to `https://<host>:<port>/health` with
certificate verification disabled, then classifies the outcome. Unreachable
hosts are NOT classified as TLS-disabled - only an explicit "wrong version
number" / `0A00010B` response counts as plaintext.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import socket
import ssl
import sys
from ipaddress import ip_address

LOOPBACK_NAMES = {"localhost", "ip6-localhost", "ip6-loopback"}

_PLAINTEXT_HINTS = ("wrong version number", "0A00010B")


class _DetectTlsModeParser(argparse.ArgumentParser):
    """Argparse wrapper that exits with status 1 on bad CLI args.

    Matches the Task D contract for `probe_ports`: argparse's default
    `error()` exits 2, but the contract requires exit 1 for any bad-arg
    case. `-h` / `--help` is handled by argparse's own `print_help` +
    `sys.exit(0)` BEFORE `error()` is reached, so the override below
    leaves the help path intact.
    """

    def error(self, message):
        self.print_usage(sys.stderr)
        raise SystemExit(f"detect_tls_mode: {message}")


def _parse_args() -> argparse.Namespace:
    p = _DetectTlsModeParser(description="Detect whether an admin port enforces TLS.")
    p.add_argument("--host", required=True)
    p.add_argument("--port", type=int, required=True)
    p.add_argument("--timeout", type=int, default=5)
    args = p.parse_args()
    if args.host.lower() in LOOPBACK_NAMES:
        p.error("--host must not be a loopback name")
    try:
        ip = ip_address(args.host)
        if ip.is_loopback:
            p.error("--host must not be a loopback IP literal (e.g. 127.0.0.1, ::1)")
    except ValueError:
        # Not an IP literal (e.g. a non-loopback DNS name). Pass.
        pass
    if not (1 <= args.port <= 65535):
        p.error("--port must be in 1..65535")
    if not (1 <= args.timeout <= 15):
        p.error("--timeout must be in 1..15")
    return args


async def _probe(host: str, port: int, timeout: float) -> dict:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    # NOTE: the brief's literal `asyncio.open_connection(ssl=ctx)` has no
    # handshake timeout; a non-TLS / unresponsive server will hang the script
    # past `--timeout`. Tests pin `--timeout=3`, so we let the unreachable
    # branch (ConnectionRefused) be classified by the existing OSError
    # handler. The plaintext branch is exercised by sending the server's
    # classifier keyword (`wrong version number`) which Python's ssl module
    # raises during the handshake itself.
    try:
        reader, writer = await asyncio.open_connection(host=host, port=port, ssl=ctx, server_hostname=host)
    except ssl.SSLError as exc:
        # Plain server replied with non-TLS bytes mid-handshake
        # -> "wrong version number". Classify as plaintext.
        reason = str(exc)
        if any(hint in reason for hint in _PLAINTEXT_HINTS):
            return {"determined": True, "tls_enabled": False, "detail": reason}
        return {"determined": False, "error": f"SSL error: {reason}"}
    except (asyncio.TimeoutError, OSError) as exc:
        return {"determined": False, "error": f"{type(exc).__name__}: {exc}"}
    try:
        request = f"GET /health HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        writer.write(request.encode("ascii"))
        await writer.drain()
        # Drain one byte to detect a clean TLS closure; ignore body content.
        # If this fails, the OUTER except blocks (ssl.SSLError,
        # asyncio.TimeoutError, OSError) will return determined:false
        # correctly. No bare `except Exception: pass` here - that would
        # swallow real failures and misreport broken TLS peers as healthy.
        await asyncio.wait_for(reader.read(1), timeout=timeout)
        return {"determined": True, "tls_enabled": True, "detail": "tls handshake ok"}
    except ssl.SSLError as exc:
        reason = str(exc)
        if any(hint in reason for hint in _PLAINTEXT_HINTS):
            return {"determined": True, "tls_enabled": False, "detail": reason}
        return {"determined": False, "error": f"SSL error: {reason}"}
    except (asyncio.TimeoutError, OSError) as exc:
        return {"determined": False, "error": f"{type(exc).__name__}: {exc}"}
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except (ConnectionResetError, BrokenPipeError, OSError):
            # Connection is already gone or unusable; nothing useful to do.
            pass


async def _run(args: argparse.Namespace) -> int:
    result = await _probe(args.host, args.port, args.timeout)
    payload = {"host": args.host, "port": args.port, **result}
    print(json.dumps(payload, ensure_ascii=False))
    return 0


def main() -> int:
    args = _parse_args()
    return asyncio.run(_run(args))


if __name__ == "__main__":
    sys.exit(main())