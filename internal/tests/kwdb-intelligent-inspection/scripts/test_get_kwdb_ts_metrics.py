#!/usr/bin/env python3
"""Tests for get_kwdb_ts_metrics.py"""

import json
import subprocess
from unittest.mock import patch, MagicMock

import pytest

import get_kwdb_ts_metrics as gtm


# Sample data fixtures

SAMPLE_API_RESPONSE = {
    "results": [
        {
            "query": {
                "name": "cr.node.sys.cpu.user.percent",
                "sources": ["1", "2"],
            },
            "datapoints": [
                {"timestampNanos": "1745846400000000000", "value": 10.5},
                {"timestampNanos": "1745846460000000000", "value": 12.3},
                {"timestampNanos": "1745846520000000000", "value": 11.8},
            ],
        },
        {
            "query": {
                "name": "cr.node.liveness.livenodes",
                "sources": ["1"],
            },
            "datapoints": [
                {"timestampNanos": "1745846400000000000", "value": 3},
                {"timestampNanos": "1745846460000000000", "value": 3},
                {"timestampNanos": "1745846520000000000", "value": 3},
            ],
        },
        {
            "query": {
                "name": "cr.store.capacity",
                "sources": ["1", "2"],
            },
            "datapoints": [
                {"timestampNanos": "1745846400000000000", "value": 500000000000},
                {"timestampNanos": "1745846460000000000", "value": 500000000000},
                {"timestampNanos": "1745846520000000000", "value": 500000000000},
            ],
        },
        {
            "query": {
                "name": "cr.node.sql.query.count",
                "sources": ["1"],
            },
            "datapoints": [],  # empty
        },
    ]
}


class TestFormatBytes:
    def test_bytes_b(self):
        assert gtm.format_bytes(500) == "500.00B"

    def test_bytes_kb(self):
        assert gtm.format_bytes(2048) == "2.00KB"

    def test_bytes_mb(self):
        assert gtm.format_bytes(2 * 1024 * 1024) == "2.00MB"

    def test_bytes_gb(self):
        assert gtm.format_bytes(1.5 * 1024 * 1024 * 1024) == "1.50GB"

    def test_bytes_tb(self):
        assert gtm.format_bytes(2 * 1024 * 1024 * 1024 * 1024) == "2.00TB"

    def test_bytes_pb(self):
        assert gtm.format_bytes(1.5 * 1024 * 1024 * 1024 * 1024 * 1024) == "1.50PB"

    def test_bytes_negative(self):
        assert gtm.format_bytes(-1024) == "-1.00KB"


class TestFormatDuration:
    def test_seconds_less_than_minute(self):
        assert gtm.format_duration(30.5) == "30.5s"

    def test_seconds_minutes(self):
        assert gtm.format_duration(120.0) == "2.0m"

    def test_seconds_hours(self):
        assert gtm.format_duration(7200.0) == "2.0h"

    def test_seconds_days(self):
        assert gtm.format_duration(172800.0) == "2.0d"

    def test_seconds_boundary(self):
        assert gtm.format_duration(59.9) == "59.9s"
        assert gtm.format_duration(60.0) == "1.0m"


class TestParseIsoToNs:
    def test_iso_with_z_suffix(self):
        # "2026-04-28T10:00:00Z" should be exactly 1 hour after "2026-04-28T09:00:00Z"
        t1 = gtm._parse_iso_to_ns("2026-04-28T09:00:00Z")
        t2 = gtm._parse_iso_to_ns("2026-04-28T10:00:00Z")
        assert t2 - t1 == 3600 * 1_000_000_000

    def test_iso_without_timezone_vs_z_suffix(self):
        # Without timezone is treated as UTC, so T10:00:00Z == T10:00:00 (naive)
        t1 = gtm._parse_iso_to_ns("2026-04-28T10:00:00")
        t2 = gtm._parse_iso_to_ns("2026-04-28T10:00:00Z")
        assert t1 == t2

    def test_iso_with_timezone_offset(self):
        # +08:00 18:00 should equal 10:00 UTC
        t1 = gtm._parse_iso_to_ns("2026-04-28T18:00:00+08:00")
        t2 = gtm._parse_iso_to_ns("2026-04-28T10:00:00Z")
        assert t1 == t2

    def test_iso_different_times(self):
        # T11:00 should be 1 hour after T10:00
        t1 = gtm._parse_iso_to_ns("2026-04-28T10:00:00Z")
        t2 = gtm._parse_iso_to_ns("2026-04-28T11:00:00Z")
        assert t2 - t1 == 3600 * 1_000_000_000

    def test_invalid_iso_format(self):
        with pytest.raises(ValueError):
            gtm._parse_iso_to_ns("not-a-date")


class TestParseMetrics:
    def test_parse_metrics_with_datapoints(self):
        result = gtm.parse_metrics(SAMPLE_API_RESPONSE)
        cpu_metric = next(m for m in result if m["name"] == "cr.node.sys.cpu.user.percent")
        assert cpu_metric["display_name"] == "CPU User"
        assert cpu_metric["unit"] == "%"
        assert cpu_metric["latest_value"] == 11.8
        assert cpu_metric["min"] == 10.5
        assert cpu_metric["max"] == 12.3
        assert cpu_metric["datapoints_count"] == 3
        assert cpu_metric["sources"] == ["1", "2"]

    def test_parse_metrics_empty_datapoints(self):
        result = gtm.parse_metrics(SAMPLE_API_RESPONSE)
        empty_metric = next(m for m in result if m["name"] == "cr.node.sql.query.count")
        assert empty_metric["latest_value"] is None
        assert empty_metric["min"] is None
        assert empty_metric["max"] is None
        assert empty_metric["avg"] is None
        assert empty_metric["datapoints_count"] == 0

    def test_parse_metrics_unknown_metric(self):
        data = {
            "results": [
                {
                    "query": {"name": "unknown.metric", "sources": []},
                    "datapoints": [{"timestampNanos": "1745846400000000000", "value": 42}],
                }
            ]
        }
        result = gtm.parse_metrics(data)
        assert result[0]["display_name"] == "unknown.metric"
        assert result[0]["unit"] == ""

    def test_parse_metrics_timestamp_conversion(self):
        result = gtm.parse_metrics(SAMPLE_API_RESPONSE)
        cpu_metric = next(m for m in result if m["name"] == "cr.node.sys.cpu.user.percent")
        # timestampNanos 1745846520000000000 -> ms = 1745846520000
        assert cpu_metric["timestamp"] == 1745846520000

    def test_parse_metrics_avg_calculation(self):
        result = gtm.parse_metrics(SAMPLE_API_RESPONSE)
        cpu_metric = next(m for m in result if m["name"] == "cr.node.sys.cpu.user.percent")
        expected_avg = (10.5 + 12.3 + 11.8) / 3
        assert abs(cpu_metric["avg"] - expected_avg) < 0.001

    def test_parse_metrics_livenodes_integer(self):
        result = gtm.parse_metrics(SAMPLE_API_RESPONSE)
        ln_metric = next(m for m in result if m["name"] == "cr.node.liveness.livenodes")
        assert ln_metric["latest_value"] == 3

    def test_parse_metrics_empty_results(self):
        result = gtm.parse_metrics({"results": []})
        assert result == []


class TestFormatMetricsTable:
    def test_format_table_empty(self):
        result = gtm.format_metrics_table([])
        assert result == "No metrics data available."

    def test_format_table_basic(self):
        metrics = [
            {
                "display_name": "CPU User",
                "unit": "%",
                "latest_value": 50.0,
                "min": 30.0,
                "max": 80.0,
                "avg": 50.0,
                "sources": ["1"],
            }
        ]
        result = gtm.format_metrics_table(metrics)
        assert "CPU User" in result
        assert "50.0000%" in result
        assert "1" in result

    def test_format_table_sorted_alphabetically(self):
        metrics = [
            {"display_name": "Zebra", "unit": "count", "latest_value": 1, "min": 1, "max": 1, "avg": 1, "sources": []},
            {"display_name": "Apple", "unit": "count", "latest_value": 2, "min": 2, "max": 2, "avg": 2, "sources": []},
        ]
        result = gtm.format_metrics_table(metrics)
        lines = result.split("\n")
        apple_idx = next(i for i, l in enumerate(lines) if "Apple" in l)
        zebra_idx = next(i for i, l in enumerate(lines) if "Zebra" in l)
        assert apple_idx < zebra_idx

    def test_format_table_bytes_formatted(self):
        metrics = [
            {"display_name": "Disk Total", "unit": "bytes", "latest_value": 500000000000,
             "min": 500000000000, "max": 500000000000, "avg": 500000000000, "sources": []},
        ]
        result = gtm.format_metrics_table(metrics)
        assert "GB" in result or "TB" in result

    def test_format_table_none_value(self):
        metrics = [
            {"display_name": "No Data", "unit": "count", "latest_value": None,
             "min": None, "max": None, "avg": None, "sources": []},
        ]
        result = gtm.format_metrics_table(metrics)
        assert "NAN" in result

    def test_format_table_unknown_unit(self):
        metrics = [
            {"display_name": "Custom", "unit": "unknown_unit", "latest_value": 42,
             "min": 42, "max": 42, "avg": 42, "sources": []},
        ]
        result = gtm.format_metrics_table(metrics)
        assert "42" in result

    def test_format_table_no_sources(self):
        metrics = [
            {"display_name": "Test", "unit": "count", "latest_value": 1,
             "min": 1, "max": 1, "avg": 1, "sources": []},
        ]
        result = gtm.format_metrics_table(metrics)
        assert "N/A" in result

    def test_format_table_multiple_sources(self):
        metrics = [
            {"display_name": "Test", "unit": "count", "latest_value": 1,
             "min": 1, "max": 1, "avg": 1, "sources": ["1", "2", "3"]},
        ]
        result = gtm.format_metrics_table(metrics)
        assert "1,2,3" in result

    def test_format_table_ops_per_second(self):
        metrics = [
            {"display_name": "Writes/s", "unit": "ops/s", "latest_value": 1234.567,
             "min": 1000, "max": 1500, "avg": 1250, "sources": []},
        ]
        result = gtm.format_metrics_table(metrics)
        assert "/s" in result

    def test_format_table_ms_latency(self):
        metrics = [
            {"display_name": "Latency", "unit": "ms", "latest_value": 1.234,
             "min": 1.0, "max": 2.0, "avg": 1.5, "sources": []},
        ]
        result = gtm.format_metrics_table(metrics)
        assert "ms" in result

    def test_format_table_ns_latency(self):
        metrics = [
            {"display_name": "Clock Offset", "unit": "ns", "latest_value": 1000000,
             "min": 500000, "max": 2000000, "avg": 1000000, "sources": []},
        ]
        result = gtm.format_metrics_table(metrics)
        assert "ns" in result


class TestBuildTsQuery:
    @patch("subprocess.run")
    def test_build_ts_query_success(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(SAMPLE_API_RESPONSE)
        )
        result = gtm.build_ts_query("localhost", 8080, 0, 1000000, 60000000000)
        assert "results" in result
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "curl" in cmd
        assert "-X" in cmd
        assert "POST" in cmd
        assert "http://localhost:8080/ts/query" in cmd

    @patch("subprocess.run")
    def test_build_ts_query_with_metric_filter(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps({"results": []})
        )
        gtm.build_ts_query("localhost", 8080, 0, 1000000, 60000000000,
                          metric_filter=["cr.node.sys.cpu.user.percent"])
        cmd = mock_run.call_args[0][0]
        payload = json.loads(cmd[cmd.index("-d") + 1])
        assert len(payload["queries"]) == 1
        assert payload["queries"][0]["name"] == "cr.node.sys.cpu.user.percent"

    @patch("subprocess.run")
    def test_build_ts_query_includes_all_query_params(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps({"results": []})
        )
        gtm.build_ts_query("localhost", 8080, 0, 1000000, 60000000000)
        cmd = mock_run.call_args[0][0]
        payload = json.loads(cmd[cmd.index("-d") + 1])
        query = payload["queries"][0]
        assert "downsampler" in query
        assert "source_aggregator" in query
        assert "derivative" in query

    @patch("subprocess.run")
    def test_build_ts_query_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd=[], timeout=30)
        with pytest.raises(SystemExit) as exc_info:
            gtm.build_ts_query("localhost", 8080, 0, 1000000, 60000000000)
        assert exc_info.value.code == 1

    @patch("subprocess.run")
    def test_build_ts_query_curl_error(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=1, stderr="curl: error"
        )
        with pytest.raises(SystemExit) as exc_info:
            gtm.build_ts_query("localhost", 8080, 0, 1000000, 60000000000)
        assert exc_info.value.code == 1

    @patch("subprocess.run")
    def test_build_ts_query_invalid_json_response(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="not json"
        )
        with pytest.raises(SystemExit) as exc_info:
            gtm.build_ts_query("localhost", 8080, 0, 1000000, 60000000000)
        assert exc_info.value.code == 1


class TestMain:
    @patch("sys.argv", ["get_kwdb_ts_metrics.py", "--host", "testhost", "--port", "9999",
                        "--start", "1745846400000000000", "--end", "1745847000000000000"])
    @patch("get_kwdb_ts_metrics.build_ts_query")
    def test_main_default(self, mock_build, capsys):
        mock_build.return_value = SAMPLE_API_RESPONSE
        gtm.main()
        out = capsys.readouterr().out
        assert "KaiwuDB Time Series Metrics" in out
        assert "Host: testhost:9999" in out
        assert "Metrics Retrieved: 4" in out

    @patch("sys.argv", ["get_kwdb_ts_metrics.py", "--json",
                        "--start", "1745846400000000000", "--end", "1745847000000000000"])
    @patch("get_kwdb_ts_metrics.build_ts_query")
    def test_main_json_output(self, mock_build, capsys):
        mock_build.return_value = SAMPLE_API_RESPONSE
        gtm.main()
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert "results" in parsed

    @patch("sys.argv", ["get_kwdb_ts_metrics.py", "--start", "2026-04-28T10:00:00",
                        "--end", "2026-04-28T11:00:00"])
    @patch("get_kwdb_ts_metrics.build_ts_query")
    def test_main_iso_time_format(self, mock_build, capsys):
        mock_build.return_value = SAMPLE_API_RESPONSE
        gtm.main()
        out = capsys.readouterr().out
        assert "KaiwuDB Time Series Metrics" in out

    @patch("sys.argv", ["get_kwdb_ts_metrics.py", "--metric", "cr.node.sys.cpu.user.percent",
                        "--start", "1745846400000000000", "--end", "1745847000000000000"])
    @patch("get_kwdb_ts_metrics.build_ts_query")
    def test_main_metric_filter_single(self, mock_build, capsys):
        mock_build.return_value = {"results": []}
        gtm.main()
        mock_build.assert_called_once()
        call_args = mock_build.call_args[0]
        # build_ts_query signature: host, port, start_ns, end_ns, sample_ns, metric_filter
        assert call_args[5] == ["cr.node.sys.cpu.user.percent"]

    @patch("sys.argv", ["get_kwdb_ts_metrics.py", "--metric", "cr.node.sys.cpu.user.percent",
                        "--metric", "cr.node.liveness.livenodes",
                        "--start", "1745846400000000000", "--end", "1745847000000000000"])
    @patch("get_kwdb_ts_metrics.build_ts_query")
    def test_main_metric_filter_multiple(self, mock_build, capsys):
        mock_build.return_value = {"results": []}
        gtm.main()
        mock_build.assert_called_once()
        call_args = mock_build.call_args[0]
        assert call_args[5] == ["cr.node.sys.cpu.user.percent", "cr.node.liveness.livenodes"]

    @patch("sys.argv", ["get_kwdb_ts_metrics.py", "--metric", "unknown.metric",
                        "--start", "1745846400000000000", "--end", "1745847000000000000"])
    def test_main_unknown_metric_error(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            gtm.main()
        assert exc_info.value.code == 1
        out, err = capsys.readouterr()
        assert "Unknown metric" in err

    @patch("sys.argv", ["get_kwdb_ts_metrics.py", "--start", "invalid-format",
                        "--end", "1745847000000000000"])
    def test_main_invalid_start_format(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            gtm.main()
        assert exc_info.value.code == 1
        out, err = capsys.readouterr()
        assert "Invalid --start format" in err

    @patch("sys.argv", ["get_kwdb_ts_metrics.py", "--start", "1745846400000000000",
                        "--end", "invalid-format"])
    def test_main_invalid_end_format(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            gtm.main()
        assert exc_info.value.code == 1
        out, err = capsys.readouterr()
        assert "Invalid --end format" in err

    @patch("sys.argv", ["get_kwdb_ts_metrics.py", "--start", "2026-04-28T10:00:00Z",
                        "--end", "2026-04-28T11:00:00Z"])
    @patch("get_kwdb_ts_metrics.build_ts_query")
    def test_main_iso_with_z_suffix(self, mock_build, capsys):
        mock_build.return_value = SAMPLE_API_RESPONSE
        gtm.main()
        mock_build.assert_called_once()

    @patch("sys.argv", ["get_kwdb_ts_metrics.py", "--start", "2026-04-28T10:00:00+08:00",
                        "--end", "2026-04-28T11:00:00+08:00"])
    @patch("get_kwdb_ts_metrics.build_ts_query")
    def test_main_iso_with_timezone_offset(self, mock_build, capsys):
        mock_build.return_value = SAMPLE_API_RESPONSE
        gtm.main()
        mock_build.assert_called_once()

    @patch("sys.argv", ["get_kwdb_ts_metrics.py", "--sample", "300",
                        "--start", "1745846400000000000", "--end", "1745847000000000000"])
    @patch("get_kwdb_ts_metrics.build_ts_query")
    def test_main_custom_sample_interval(self, mock_build, capsys):
        mock_build.return_value = SAMPLE_API_RESPONSE
        gtm.main()
        mock_build.assert_called_once()
        call_args = mock_build.call_args[0]
        # build_ts_query signature: host, port, start_ns, end_ns, sample_ns, metric_filter
        assert call_args[4] == 300 * 1_000_000_000

    @patch("sys.argv", ["get_kwdb_ts_metrics.py", "--help"])
    def test_main_help(self):
        with pytest.raises(SystemExit) as exc_info:
            gtm.main()
        assert exc_info.value.code == 0

    @patch("sys.argv", ["get_kwdb_ts_metrics.py"])
    @patch("get_kwdb_ts_metrics.build_ts_query")
    def test_main_default_time_range(self, mock_build, capsys):
        mock_build.return_value = SAMPLE_API_RESPONSE
        gtm.main()
        mock_build.assert_called_once()
        call_args = mock_build.call_args[0]
        # build_ts_query signature: host, port, start_ns, end_ns, sample_ns, metric_filter
        assert call_args[0] == "localhost"
        assert call_args[1] == 8080


class TestMetricsMap:
    def test_all_metrics_have_required_fields(self):
        for name, info in gtm.METRICS_MAP.items():
            assert info.display.display_name, f"{name} missing display_name"
            assert info.display.unit is not None, f"{name} missing unit"
            assert info.query.downsampler is not None, f"{name} missing downsampler"
            assert info.query.source_aggregator is not None, f"{name} missing source_aggregator"
            assert info.query.derivative is not None, f"{name} missing derivative"

    def test_all_metrics_have_unique_names(self):
        names = list(gtm.METRICS_MAP.keys())
        assert len(names) == len(set(names)), "Duplicate metric names found"

    def test_q_gauge_and_q_latency_exist(self):
        assert gtm.Q_GAUGE is not None
        assert gtm.Q_LATENCY is not None
        assert gtm.Q_GAUGE.downsampler == 1
        assert gtm.Q_GAUGE.source_aggregator == 2
        assert gtm.Q_GAUGE.derivative == 0
        assert gtm.Q_LATENCY.downsampler == 1
        assert gtm.Q_LATENCY.source_aggregator == 1
        assert gtm.Q_LATENCY.derivative == 0
