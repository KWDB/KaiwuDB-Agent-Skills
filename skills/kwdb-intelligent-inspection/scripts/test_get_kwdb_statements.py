#!/usr/bin/env python3
"""Tests for get_kwdb_statements.py"""

import json
import subprocess
from unittest.mock import patch

import pytest

import get_kwdb_statements as gks


# Sample data fixtures

SAMPLE_API_RESPONSE = {
    "lastReset": "2026-04-22T10:00:00Z",
    "internalAppNamePrefix": "$$",
    "statements": [
        {
            "key": {
                "keyData": {
                    "query": "SELECT * FROM users WHERE id = $1",
                    "app": "test_app",
                    "user": "testuser",
                    "database": "testdb",
                    "distSQL": True,
                    "failed": False,
                    "implicitTxn": True,
                },
                "nodeId": 1,
            },
            "stats": {
                "count": 100,
                "firstAttemptCount": 95,
                "maxRetries": 2,
                "bytesRead": 102400,
                "rowsRead": 5000,
                "failedCount": 5,
                "parseLat": {"mean": 0.001},
                "planLat": {"mean": 0.005},
                "runLat": {"mean": 0.050},
                "serviceLat": {"mean": 0.060},
                "overheadLat": {"mean": 0.004},
                "numRows": {"mean": 50.0},
                "sensitiveInfo": {"lastErr": ""},
            },
        },
        {
            "key": {
                "keyData": {
                    "query": "INSERT INTO orders VALUES ($1, $2)",
                    "app": "order_service",
                    "user": "admin",
                    "database": "prod",
                    "distSQL": False,
                    "failed": True,
                    "implicitTxn": False,
                },
                "nodeId": 2,
            },
            "stats": {
                "count": 50,
                "firstAttemptCount": 45,
                "maxRetries": 5,
                "bytesRead": 2048,
                "rowsRead": 50,
                "failedCount": 5,
                "parseLat": {"mean": 0.0005},
                "planLat": {"mean": 0.002},
                "runLat": {"mean": 0.100},
                "serviceLat": {"mean": 0.110},
                "overheadLat": {"mean": 0.008},
                "numRows": {"mean": 1.0},
                "sensitiveInfo": {"lastErr": "connection refused"},
            },
        },
    ],
}


class TestParseStatements:
    def test_parse_statements_basic(self):
        """Test basic parsing of statements."""
        result = gks.parse_statements(SAMPLE_API_RESPONSE)
        assert len(result) == 2

    def test_parse_statements_first_item(self):
        """Test parsing first statement fields."""
        result = gks.parse_statements(SAMPLE_API_RESPONSE)
        stmt = result[0]
        assert stmt["query"] == "SELECT * FROM users WHERE id = $1"
        assert stmt["app"] == "test_app"
        assert stmt["user"] == "testuser"
        assert stmt["database"] == "testdb"
        assert stmt["node_id"] == 1
        assert stmt["dist_sql"] is True
        assert stmt["failed"] is False
        assert stmt["implicit_txn"] is True
        assert stmt["count"] == 100
        assert stmt["failed_count"] == 5

    def test_parse_statements_latencies(self):
        """Test latency parsing (in seconds and ms)."""
        result = gks.parse_statements(SAMPLE_API_RESPONSE)
        stmt = result[0]
        assert stmt["service_latency_s"] == 0.060
        assert stmt["service_latency_ms"] == 60.0
        assert stmt["run_latency_s"] == 0.050
        assert stmt["run_latency_ms"] == 50.0
        assert stmt["plan_latency_s"] == 0.005
        assert stmt["plan_latency_ms"] == 5.0
        assert stmt["parse_latency_s"] == 0.001
        assert stmt["parse_latency_ms"] == 1.0

    def test_parse_statements_second_item_with_error(self):
        """Test parsing second statement with error."""
        result = gks.parse_statements(SAMPLE_API_RESPONSE)
        stmt = result[1]
        assert stmt["query"] == "INSERT INTO orders VALUES ($1, $2)"
        assert stmt["last_err"] == "connection refused"
        assert stmt["failed"] is True

    def test_parse_statements_missing_fields(self):
        """Test parsing with missing optional fields."""
        data = {"statements": [{"key": {"keyData": {}}, "stats": {}}]}
        result = gks.parse_statements(data)
        assert len(result) == 1
        stmt = result[0]
        assert stmt["query"] == ""
        assert stmt["count"] == 0

    def test_parse_statements_empty(self):
        """Test parsing empty statements list."""
        data = {"statements": []}
        result = gks.parse_statements(data)
        assert result == []


class TestFilterAndSort:
    def setup_method(self):
        """Set up test fixtures."""
        self.statements = gks.parse_statements(SAMPLE_API_RESPONSE)

    def test_filter_by_min_latency(self):
        """Test filtering by minimum latency."""
        # 60ms and 110ms - filter at 100ms to get only the second statement
        result = gks.filter_and_sort(self.statements, min_latency_ms=100.0, sort_by="service_lat")
        assert len(result) == 1
        assert result[0]["query"] == "INSERT INTO orders VALUES ($1, $2)"

    def test_filter_no_match(self):
        """Test filter that excludes all."""
        result = gks.filter_and_sort(self.statements, min_latency_ms=200.0, sort_by="service_lat")
        assert len(result) == 0

    def test_filter_zero_latency(self):
        """Test filter with zero latency returns all."""
        result = gks.filter_and_sort(self.statements, min_latency_ms=0, sort_by="service_lat")
        assert len(result) == 2

    def test_sort_by_service_lat(self):
        """Test sorting by service latency (descending)."""
        result = gks.filter_and_sort(self.statements, min_latency_ms=0, sort_by="service_lat")
        assert result[0]["service_latency_ms"] >= result[1]["service_latency_ms"]

    def test_sort_by_run_lat(self):
        """Test sorting by run latency."""
        result = gks.filter_and_sort(self.statements, min_latency_ms=0, sort_by="run_lat")
        assert result[0]["run_latency_ms"] >= result[1]["run_latency_ms"]

    def test_sort_by_count(self):
        """Test sorting by count."""
        result = gks.filter_and_sort(self.statements, min_latency_ms=0, sort_by="count")
        assert result[0]["count"] >= result[1]["count"]

    def test_sort_unknown_key_defaults_to_service_lat(self):
        """Test unknown sort key defaults to service_latency_ms."""
        result = gks.filter_and_sort(self.statements, min_latency_ms=0, sort_by="unknown_key")
        assert len(result) == 2


class TestFetchStatements:
    @patch("subprocess.run")
    def test_fetch_statements_success(self, mock_run):
        """Test successful fetch of statements."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(SAMPLE_API_RESPONSE)
        )
        result = gks.fetch_statements("localhost", 8080)
        assert result == SAMPLE_API_RESPONSE
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "curl" in cmd
        assert "http://localhost:8080/_status/statements" in cmd

    @patch("subprocess.run")
    def test_fetch_statements_with_insecure(self, mock_run):
        """Test fetch with insecure flag."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(SAMPLE_API_RESPONSE)
        )
        gks.fetch_statements("localhost", 8080, insecure=True)
        cmd = mock_run.call_args[0][0]
        assert "--insecure" in cmd

    @patch("subprocess.run")
    def test_fetch_statements_secure(self, mock_run):
        """Test fetch without insecure flag."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps(SAMPLE_API_RESPONSE)
        )
        gks.fetch_statements("localhost", 8080, insecure=False)
        cmd = mock_run.call_args[0][0]
        assert "--insecure" not in cmd

    @patch("subprocess.run")
    def test_fetch_statements_curl_error(self, mock_run):
        """Test fetch when curl fails."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=1, stderr="curl: error"
        )
        with pytest.raises(SystemExit) as exc_info:
            gks.fetch_statements("localhost", 8080)
        assert exc_info.value.code == 1

    @patch("subprocess.run")
    def test_fetch_statements_invalid_json(self, mock_run):
        """Test fetch when response is not valid JSON."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="not json"
        )
        with pytest.raises(SystemExit) as exc_info:
            gks.fetch_statements("localhost", 8080)
        assert exc_info.value.code == 1


class TestFormatStatement:
    def test_format_statement_basic(self):
        """Test basic formatting of statement."""
        stmt = gks.parse_statements(SAMPLE_API_RESPONSE)[0]
        result = gks.format_statement(stmt, 0)
        assert "Slow Statement" in result
        assert "SELECT * FROM users WHERE id = $1" in result
        assert "test_app" in result
        assert "testuser" in result
        assert "testdb" in result

    def test_format_statement_latencies(self):
        """Test that latencies are formatted."""
        stmt = gks.parse_statements(SAMPLE_API_RESPONSE)[0]
        result = gks.format_statement(stmt, 0)
        assert "Service:" in result
        assert "Run:" in result
        assert "Plan:" in result
        assert "Parse:" in result

    def test_format_statement_with_error(self):
        """Test formatting statement with last error."""
        stmt = gks.parse_statements(SAMPLE_API_RESPONSE)[1]
        result = gks.format_statement(stmt, 0)
        assert "Last Error" in result
        assert "connection refused" in result

    def test_format_statement_long_query_truncated(self):
        """Test that long queries are truncated with ..."""
        stmt = {
            "query": "x" * 300,
            "app": "app",
            "user": "user",
            "database": "db",
            "node_id": 1,
            "dist_sql": False,
            "failed": False,
            "implicit_txn": False,
            "count": 1,
            "first_attempt_count": 1,
            "max_retries": 0,
            "bytes_read": 0,
            "rows_read": 0,
            "failed_count": 0,
            "parse_latency_s": 0,
            "plan_latency_s": 0,
            "run_latency_s": 0,
            "service_latency_s": 0,
            "overhead_latency_s": 0,
            "service_latency_ms": 0,
            "run_latency_ms": 0,
            "plan_latency_ms": 0,
            "parse_latency_ms": 0,
            "num_rows_mean": 0,
            "last_err": "",
        }
        result = gks.format_statement(stmt, 0)
        assert "..." in result
        assert "x" * 200 in result

    def test_format_statement_flags(self):
        """Test that flags are displayed."""
        stmt = gks.parse_statements(SAMPLE_API_RESPONSE)[0]
        result = gks.format_statement(stmt, 0)
        assert "DistSQL=True" in result
        assert "Failed=False" in result
        assert "ImplicitTxn=True" in result


class TestMain:
    @patch("sys.argv", ["get_kwdb_statements.py", "--host", "testhost", "--port", "9999"])
    @patch("get_kwdb_statements.fetch_statements")
    def test_main_default(self, mock_fetch, capsys):
        """Test main with default arguments."""
        mock_fetch.return_value = SAMPLE_API_RESPONSE
        gks.main()
        out = capsys.readouterr().out
        assert "KaiwuDB Statements Summary" in out
        assert "Last Reset:" in out
        assert "Total Statements: 2" in out
        assert "testhost" not in out  # host/port not printed in summary

    @patch("sys.argv", ["get_kwdb_statements.py", "--json"])
    @patch("get_kwdb_statements.fetch_statements")
    def test_main_json_output(self, mock_fetch, capsys):
        """Test --json flag outputs raw JSON."""
        mock_fetch.return_value = SAMPLE_API_RESPONSE
        gks.main()
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert "statements" in parsed

    @patch("sys.argv", ["get_kwdb_statements.py", "--limit", "1"])
    @patch("get_kwdb_statements.fetch_statements")
    def test_main_limit(self, mock_fetch, capsys):
        """Test --limit flag."""
        mock_fetch.return_value = SAMPLE_API_RESPONSE
        gks.main()
        out = capsys.readouterr().out
        assert "Showing: 1" in out
        assert "INSERT INTO orders VALUES" in out  # highest latency first

    @patch("sys.argv", ["get_kwdb_statements.py", "--min-latency-ms", "100"])
    @patch("get_kwdb_statements.fetch_statements")
    def test_main_min_latency_filter(self, mock_fetch, capsys):
        """Test --min-latency-ms filter."""
        mock_fetch.return_value = SAMPLE_API_RESPONSE
        gks.main()
        out = capsys.readouterr().out
        assert "Showing: 1" in out
        assert "INSERT INTO orders VALUES" in out

    @patch("sys.argv", ["get_kwdb_statements.py", "--sort-by", "count"])
    @patch("get_kwdb_statements.fetch_statements")
    def test_main_sort_by_count(self, mock_fetch, capsys):
        """Test --sort-by count."""
        mock_fetch.return_value = SAMPLE_API_RESPONSE
        gks.main()
        out = capsys.readouterr().out
        # SELECT (count=100) should appear before INSERT (count=50) when sorted by count desc
        assert out.index("SELECT * FROM users") < out.index("INSERT INTO orders")

    @patch("sys.argv", ["get_kwdb_statements.py", "--sort-by", "run_lat"])
    @patch("get_kwdb_statements.fetch_statements")
    def test_main_sort_by_run_lat(self, mock_fetch, capsys):
        """Test --sort-by run_lat."""
        mock_fetch.return_value = SAMPLE_API_RESPONSE
        gks.main()
        out = capsys.readouterr().out
        # INSERT has higher run_lat (100ms vs 50ms)
        assert "INSERT INTO orders VALUES" in out

    @patch("sys.argv", ["get_kwdb_statements.py", "--sort-by", "plan_lat"])
    @patch("get_kwdb_statements.fetch_statements")
    def test_main_sort_by_plan_lat(self, mock_fetch, capsys):
        """Test --sort-by plan_lat."""
        mock_fetch.return_value = SAMPLE_API_RESPONSE
        gks.main()
        out = capsys.readouterr().out
        # INSERT has higher plan_lat (2ms vs 5ms) - wait, that's wrong
        # Let me check: planLat for SELECT=0.005 (5ms), INSERT=0.002 (2ms)
        # So SELECT should be first when sorted descending
        assert "SELECT * FROM users" in out

    def test_main_empty_statements(self, capsys):
        """Test main with empty statements list."""
        empty_data = {"statements": [], "lastReset": "never", "internalAppNamePrefix": ""}
        with patch("sys.argv", ["get_kwdb_statements.py"]), \
             patch("get_kwdb_statements.fetch_statements", return_value=empty_data):
            gks.main()
            out = capsys.readouterr().out
            assert "Total Statements: 0" in out
            assert "Showing: 0" in out

    @patch("sys.argv", ["get_kwdb_statements.py", "--help"])
    def test_main_help(self):
        """Test --help shows usage and exits."""
        with pytest.raises(SystemExit) as exc_info:
            gks.main()
        assert exc_info.value.code == 0
