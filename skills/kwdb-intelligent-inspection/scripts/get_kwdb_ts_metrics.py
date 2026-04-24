#!/usr/bin/env python3
"""
KaiwuDB Time Series Metrics Processor

Process and extract inspection-relevant metrics from KaiwuDB's /ts/query API response.
The API returns a large JSON object with many metrics; this script filters and formats
only the metrics needed for inspection per references/report-template.md.

Usage:
    python3 get_kwdb_ts_metrics.py [--host HOST] [--port PORT] [--start TIME] [--end TIME]
                                    [--sample INTERVAL] [--metric NAME] [--json]

Options:
    --host           KaiwuDB admin host (default: localhost)
    --port           KaiwuDB admin port (default: 8080)
    --start          Start time (ISO format or unix timestamp in ns, default: 1 hour ago)
    --end            End time (ISO format or unix timestamp in ns, default: now)
    --sample         Sample interval in seconds (default: 60)
    --metric         Filter by specific metric name (e.g., sys.cpu.user.percent)
    --json           Output raw JSON data
"""

import argparse
import json
import subprocess
import sys
import time
from typing import Any


# Metrics mapping from report-template.md
# Format: (api_name, display_name, unit, is_latency)
METRICS_MAP = {
    # Basic Indicators
    "liveness.livenodes": ("Live Nodes", "nodes", False),
    "sys.uptime": ("Uptime", "seconds", False),
    # System Resources
    "sys.cpu.user.percent": ("CPU User", "%", False),
    "sys.cpu.sys.percent": ("CPU Sys", "%", False),
    "sys.cpu.combined.percent-normalized": ("CPU Combined", "%", False),
    "capacity": ("Disk Total", "bytes", False),
    "capacity.available": ("Disk Available", "bytes", False),
    "capacity.used": ("Disk Used", "bytes", False),
    "sys.rss": ("Memory RSS", "bytes", False),
    "sys.go.allocbytes": ("Go Alloc", "bytes", False),
    "sys.go.totalbytes": ("Go Total", "bytes", False),
    # Database Performance
    "sql.insert.count": ("SQL Insert Count", "count", False),
    "sql.update.count": ("SQL Update Count", "count", False),
    "sql.delete.count": ("SQL Delete Count", "count", False),
    "sql.select.count": ("SQL Select Count", "count", False),
    "sql.query.count": ("SQL Query Count", "count", False),
    "rebalancing.writespersecond": ("Rebalancing Writes/s", "ops/s", False),
    "rebalancing.queriespersecond": ("Rebalancing Queries/s", "ops/s", False),
    "sql.exec.latency": ("SQL Exec Latency", "ms", True),
    "sql.service.latency": ("SQL Service Latency", "ms", True),
    "sql.distsql.exec.latency": ("DistSQL Exec Latency", "ms", True),
    # Storage
    "totalbytes": ("Total Bytes", "bytes", False),
    "livebytes": ("Live Bytes", "bytes", False),
    # Cluster
    "replicas": ("Replicas", "count", False),
    "replicas.leaders": ("Raft Leaders", "count", False),
    "replicas.leaseholders": ("Lease Holders", "count", False),
    "ranges.unavailable": ("Unavailable Ranges", "count", False),
    "ranges.underreplicated": ("Under-replicated Ranges", "count", False),
    "ranges.overreplicated": ("Over-replicated Ranges", "count", False),
    "raftlog.behind": ("Raftlog Behind", "count", False),
    "wal.replica.data.latency": ("WAL Replica Data Latency", "ms", True),
    "raft.replica.consistent.latency": ("Raft Consistent Latency", "ms", True),
    # Network
    "round-trip-latency": ("Round-trip Latency", "ms", True),
    "clock-offset.meannanos": ("Clock Offset Mean", "ns", True),
}


def build_ts_query(host: str, port: int, start_ns: int, end_ns: int, sample_ns: int,
                   metric_filter: list[str] | None = None) -> dict:
    """Build and execute /ts/query API request."""

    # Gauge/Counter metrics: d:1, sa:2, der:0
    # Latency metrics: d:1, sa:1, der:0
    latency_metrics = {
        "sql.exec.latency", "sql.service.latency", "sql.distsql.exec.latency",
        "wal.replica.data.latency", "raft.replica.consistent.latency",
        "round-trip-latency", "clock-offset.meannanos"
    }

    queries = []
    metrics_to_query = metric_filter if metric_filter else list(METRICS_MAP.keys())

    for name in metrics_to_query:
        if name in latency_metrics:
            queries.append({
                "name": f"cr.node.{name}",
                "downsampler": 1,
                "source_aggregator": 1,
                "derivative": 0
            })
        else:
            queries.append({
                "name": f"cr.node.{name}",
                "downsampler": 1,
                "source_aggregator": 2,
                "derivative": 0
            })

    payload = {
        "start_nanos": start_ns,
        "end_nanos": end_ns,
        "sample_nanos": sample_ns,
        "queries": queries
    }

    curl_cmd = [
        "curl", "-s", "--insecure", "-X", "POST",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload),
        f"http://{host}:{port}/ts/query"
    ]

    result = subprocess.run(curl_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: Failed to fetch metrics: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON response: {e}", file=sys.stderr)
        sys.exit(1)


def parse_metrics(data: dict) -> list[dict[str, Any]]:
    """Parse /ts/query response and extract latest values for each metric."""
    results = []

    for r in data.get("results", []):
        # Extract metric name (remove cr.node. prefix)
        full_name = r.get("query", {}).get("name", "")
        if full_name.startswith("cr.node."):
            name = full_name[8:]  # Remove "cr.node."
        else:
            name = full_name

        sources = r.get("query", {}).get("sources", [])
        datapoints = r.get("datapoints", [])

        # Include metric even if no datapoints (show NULL/NAN)
        if datapoints:
            latest = datapoints[-1]
            timestamp = int(latest.get("timestampNanos", 0)) // 1_000_000  # Convert to ms
            results.append({
                "name": name,
                "display_name": METRICS_MAP.get(name, (name, "", False))[0],
                "unit": METRICS_MAP.get(name, ("", "", False))[1],
                "is_latency": METRICS_MAP.get(name, ("", "", False))[2],
                "latest_value": latest.get("value", 0),
                "sources": sources,
                "datapoints_count": len(datapoints),
                "timestamp": timestamp,
                "min": min(dp.get("value", 0) for dp in datapoints),
                "max": max(dp.get("value", 0) for dp in datapoints),
                "avg": sum(dp.get("value", 0) for dp in datapoints) / len(datapoints),
            })
        else:
            results.append({
                "name": name,
                "display_name": METRICS_MAP.get(name, (name, "", False))[0],
                "unit": METRICS_MAP.get(name, ("", "", False))[1],
                "is_latency": METRICS_MAP.get(name, ("", "", False))[2],
                "latest_value": None,
                "sources": sources,
                "datapoints_count": 0,
                "timestamp": None,
                "min": None,
                "max": None,
                "avg": None,
            })

    return results


def format_metrics_table(metrics: list[dict]) -> str:
    """Format metrics as a table."""
    if not metrics:
        return "No metrics data available."

    # Determine column widths
    name_width = max(len(m["display_name"]) for m in metrics) + 2
    val_width = 18
    min_width = 12
    max_width = 12
    avg_width = 12

    lines = []
    header = (f"{'Metric':<{name_width}}"
              f"{'Latest':>{val_width}}"
              f"{'Min':>{min_width}}"
              f"{'Max':>{max_width}}"
              f"{'Avg':>{avg_width}}"
              f"  Sources")
    lines.append(header)
    lines.append("-" * len(header))

    for m in sorted(metrics, key=lambda x: x["display_name"]):
        value = m["latest_value"]
        unit = m["unit"]

        # Format value with unit (handle None)
        if value is None:
            value_str = "NAN"
        elif unit == "bytes":
            value_str = format_bytes(value)
        elif unit == "%":
            value_str = f"{value:.4f}%"
        elif unit == "ms":
            value_str = f"{value:.3f}ms"
        elif unit == "ns":
            value_str = f"{value:.0f}ns"
        elif unit == "seconds":
            value_str = format_duration(value)
        elif unit == "count" or unit == "nodes":
            value_str = f"{int(value)}"
        elif unit == "ops/s":
            value_str = f"{value:.2f}/s"
        else:
            value_str = f"{value}"

        # Format min/max/avg (handle None)
        def fmt(v):
            if v is None:
                return "NAN"
            return f"{v:.3f}"

        lines.append(
            f"{m['display_name']:<{name_width}}"
            f"{value_str:>{val_width}}"
            f"{fmt(m['min']):>{min_width}}"
            f"{fmt(m['max']):>{max_width}}"
            f"{fmt(m['avg']):>{avg_width}}"
            f"  {','.join(m['sources']) if m['sources'] else 'N/A'}"
        )

    return "\n".join(lines)


def format_bytes(num: float) -> str:
    """Format bytes as human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(num) < 1024.0:
            return f"{num:.2f}{unit}"
        num /= 1024.0
    return f"{num:.2f}PB"


def format_duration(seconds: float) -> str:
    """Format seconds as human-readable duration."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    elif seconds < 86400:
        return f"{seconds/3600:.1f}h"
    else:
        return f"{seconds/86400:.1f}d"


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and process time series metrics from KaiwuDB"
    )
    parser.add_argument("--host", default="localhost", help="KaiwuDB admin host")
    parser.add_argument("--port", type=int, default=8080, help="KaiwuDB admin port")
    parser.add_argument("--start", help="Start time (ISO format or unix timestamp in ns)")
    parser.add_argument("--end", help="End time (ISO format or unix timestamp in ns)")
    parser.add_argument("--sample", type=int, default=60, help="Sample interval in seconds")
    parser.add_argument("--metric", action="append", help="Filter by metric name (can repeat)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    # Calculate time range
    now_ns = int(time.time_ns())  # Use time_ns() for integer precision
    hour_ns = 3600 * 1_000_000_000

    if args.start:
        try:
            start_ns = int(args.start)
        except ValueError:
            # Assume ISO format, use as-is (would need dateutil for proper parsing)
            start_ns = now_ns - hour_ns
    else:
        start_ns = now_ns - hour_ns

    if args.end:
        try:
            end_ns = int(args.end)
        except ValueError:
            end_ns = now_ns
    else:
        end_ns = now_ns

    sample_ns = args.sample * 1_000_000_000

    data = build_ts_query(args.host, args.port, start_ns, end_ns, sample_ns,
                          args.metric)

    if args.json:
        print(json.dumps(data, indent=2))
        return

    metrics = parse_metrics(data)

    print(f"KaiwuDB Time Series Metrics")
    print(f"{'='*80}")
    print(f"Host: {args.host}:{args.port}")
    print(f"Time Range: {start_ns} - {end_ns} ({args.sample}s intervals)")
    print(f"Metrics Retrieved: {len(metrics)}")
    print()
    print(format_metrics_table(metrics))


if __name__ == "__main__":
    main()
