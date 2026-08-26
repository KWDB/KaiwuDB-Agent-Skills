"""
test_migration_flow.py - End-to-End Migration Flow Test

A comprehensive test script that validates the complete migration workflow
from MySQL to KaiwuDB using the mock KDTS server.

Test Flow:
1. Start mock KDTS server
2. Initialize client and managers
3. Build source/target configurations
4. Test connections
5. Read metadata from source
6. Preview DDL for target
7. Execute DDL on target
8. Build migration scripts
9. Execute migration
10. Monitor migration progress
11. Verify final status

Usage:
    # Run full test suite
    python test_migration_flow.py

    # Run with custom mock server port
    python test_migration_flow.py --port 9999

    # Run specific test
    python test_migration_flow.py --test connection
"""

import sys
import os
import time
import argparse
import logging
from typing import Dict, Any, Optional, List

# Add the skills scripts directory to path
# From internal/tests/kwdb-data-migration/scripts/ to skills/kwdb-data-migration/scripts/
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR))))
SKILLS_SCRIPTS_PATH = os.path.join(PROJECT_ROOT, 'skills', 'kwdb-data-migration', 'scripts')
sys.path.insert(0, SKILLS_SCRIPTS_PATH)

# Also add current directory for mock_server
sys.path.insert(0, CURRENT_DIR)

from mock_server import start_mock_server, MockKDSServer
from config import get_environment_info

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MigrationFlowTester:
    """End-to-end migration flow tester."""

    def __init__(self, mock_port: int = 8989):
        """
        Initialize tester.

        Args:
            mock_port: Port for mock KDTS server
        """
        self.mock_port = mock_port
        self.mock_server: Optional[MockKDSServer] = None
        self.client = None
        self.ds_manager = None
        self.workflow = None
        self.test_results: List[Dict[str, Any]] = []

    def setup(self):
        """Setup test environment."""
        logger.info("=" * 60)
        logger.info("SETUP: Starting mock KDTS server")
        logger.info("=" * 60)

        # Start mock server
        self.mock_server = start_mock_server(port=self.mock_port)
        time.sleep(0.5)  # Wait for server to start

        # Import after server is ready
        from api_client import KDTSClient
        from data_source import DataSourceManager
        from migration_task import MigrationWorkflowManager

        # Initialize client pointing to mock server
        mock_url = f"http://127.0.0.1:{self.mock_port}"
        logger.info(f"Initializing KDTSClient with: {mock_url}")
        self.client = KDTSClient(base_url=mock_url)

        # Initialize managers
        self.ds_manager = DataSourceManager(api_client=self.client)
        self.workflow = MigrationWorkflowManager(api_client=self.client)

        logger.info("Setup complete!")
        self._add_result("setup", True, "Test environment initialized")

    def teardown(self):
        """Cleanup test environment."""
        logger.info("=" * 60)
        logger.info("TEARDOWN: Stopping mock KDTS server")
        logger.info("=" * 60)

        if self.mock_server:
            self.mock_server.stop()

        logger.info("Teardown complete!")

    def _add_result(self, test_name: str, passed: bool, message: str,
                    details: Optional[Dict] = None):
        """Add test result."""
        result = {
            "test": test_name,
            "passed": passed,
            "message": message,
            "details": details,
            "timestamp": time.time()
        }
        self.test_results.append(result)

        status = "PASSED" if passed else "FAILED"
        logger.info(f"[{status}] {test_name}: {message}")

    def test_health_check(self):
        """Test 1: Health check."""
        logger.info("-" * 40)
        logger.info("TEST 1: Health Check")
        logger.info("-" * 40)

        try:
            response = self.client.health_check()
            if response.get("code") == 0:
                self._add_result("health_check", True, "Server is healthy", response)
            else:
                self._add_result("health_check", False, f"Unexpected response: {response}")
        except Exception as e:
            self._add_result("health_check", False, str(e))

    def test_build_configs(self):
        """Test 2: Build source and target configurations."""
        logger.info("-" * 40)
        logger.info("TEST 2: Build Configurations")
        logger.info("-" * 40)

        try:
            # Build source config (MySQL)
            source_config = self.ds_manager.build_config(
                source_type="MYSQL",
                host="192.168.1.100",
                port=3306,
                username="root",
                password="secret",
                db_name="shop_db"
            )

            # Build target config (KaiwuDB)
            target_config = self.ds_manager.build_target_config(
                engine="RELATIONAL",
                host="127.0.0.1",
                port=26257,
                username="root",
                password="dummy_password",  # Use dummy password for testing
                db_name="kwdb_target"
            )

            # Validate configurations
            from config_validator import ConfigValidator
            source_valid = ConfigValidator.validate_source_config(source_config)
            target_valid = ConfigValidator.validate_target_config(target_config)

            if source_valid.get("valid") and target_valid.get("valid"):
                self._add_result("build_configs", True,
                                 "Configurations built and validated",
                                 {"source": source_config, "target": target_config})
                return source_config, target_config
            else:
                self._add_result("build_configs", False,
                                 f"Validation failed: source={source_valid}, target={target_valid}")
                return None, None

        except Exception as e:
            self._add_result("build_configs", False, str(e))
            return None, None

    def test_connections(self, source_config: Dict, target_config: Dict):
        """Test 3: Test source and target connections."""
        logger.info("-" * 40)
        logger.info("TEST 3: Connection Tests")
        logger.info("-" * 40)

        try:
            # Test source connection
            source_result = self.client.test_connection(source_config, is_target=False)
            source_ok = source_result.get("code") == 0

            # Test target connection
            target_result = self.client.test_connection(target_config, is_target=True)
            target_ok = target_result.get("code") == 0

            if source_ok and target_ok:
                self._add_result("connections", True,
                                 "Both source and target connections successful",
                                 {"source": source_result, "target": target_result})
            else:
                self._add_result("connections", False,
                                 f"Failed: source={'OK' if source_ok else 'FAILED'}, "
                                 f"target={'OK' if target_ok else 'FAILED'}")

        except Exception as e:
            self._add_result("connections", False, str(e))

    def test_list_databases(self, source_config: Dict):
        """Test 4: List source databases."""
        logger.info("-" * 40)
        logger.info("TEST 4: List Source Databases")
        logger.info("-" * 40)

        try:
            response = self.client.list_databases(source_config)
            databases = response.get("data", [])

            if response.get("code") == 0 and len(databases) > 0:
                self._add_result("list_databases", True,
                                 f"Found {len(databases)} databases: {databases}",
                                 response)
            else:
                self._add_result("list_databases", False,
                                 f"No databases found or error: {response}")

        except Exception as e:
            self._add_result("list_databases", False, str(e))

    def test_read_metadata(self, source_config: Dict):
        """Test 5: Read source metadata."""
        logger.info("-" * 40)
        logger.info("TEST 5: Read Source Metadata")
        logger.info("-" * 40)

        try:
            metadata_options = {
                "enable": True,
                "autoDdl": True,
                "primaryKey": True,
                "constraint": True,
                "comment": True,
                "index": True,
                "view": False,
            }

            response = self.client.read_metadata(source_config, metadata_options)

            if response.get("code") == 0:
                db_data = response.get("data", {})
                table_count = len(db_data.get("tables", []))
                self._add_result("read_metadata", True,
                                 f"Read metadata for {table_count} tables",
                                 {"tables": [t["name"] for t in db_data.get("tables", [])]})
                return response
            else:
                self._add_result("read_metadata", False, f"Error: {response}")
                return None

        except Exception as e:
            self._add_result("read_metadata", False, str(e))
            return None

    def test_preview_ddl(self, target_config: Dict, source_metadata: Dict):
        """Test 6: Preview DDL for target."""
        logger.info("-" * 40)
        logger.info("TEST 6: Preview DDL")
        logger.info("-" * 40)

        try:
            db_data = source_metadata.get("data", {}) if source_metadata else {}

            response = self.client.preview_ddl(
                target_config=target_config,
                source_db=db_data,
                metadata=source_metadata.get("data", {}),
                is_time_series=False
            )

            if response.get("code") == 0:
                ddl_data = response.get("data", {})
                tables = ddl_data.get("ddlScript", {}).get("tables", [])
                self._add_result("preview_ddl", True,
                                 f"Generated DDL for {len(tables)} tables",
                                 response)
                return response
            else:
                self._add_result("preview_ddl", False, f"Error: {response}")
                return None

        except Exception as e:
            self._add_result("preview_ddl", False, str(e))
            return None

    def test_execute_ddl(self, target_config: Dict, ddl_preview: Dict):
        """Test 7: Execute DDL on target."""
        logger.info("-" * 40)
        logger.info("TEST 7: Execute DDL")
        logger.info("-" * 40)

        try:
            ddl_script = ddl_preview.get("data", {}) if ddl_preview else {}

            response = self.client.execute_ddl(
                target_config=target_config,
                ddl_script=ddl_script,
                auto_ddl=True
            )

            if response.get("code") == 0:
                self._add_result("execute_ddl", True,
                                 f"DDL executed: {response.get('data', {})}",
                                 response)
            else:
                self._add_result("execute_ddl", False, f"Error: {response}")

        except Exception as e:
            self._add_result("execute_ddl", False, str(e))

    def test_build_migration(self, source_config: Dict, target_config: Dict):
        """Test 8: Build migration scripts."""
        logger.info("-" * 40)
        logger.info("TEST 8: Build Migration Scripts")
        logger.info("-" * 40)

        try:
            response = self.client.build_migration(
                source=source_config,
                target=target_config,
                tables=None,  # All tables
                data_config=None
            )

            if response.get("code") == 0:
                data = response.get("data", {})
                script_names = data.get("scriptNames", [])
                self._add_result("build_migration", True,
                                 f"Built {len(script_names)} scripts: {script_names}",
                                 response)
                return script_names
            else:
                self._add_result("build_migration", False, f"Error: {response}")
                return []

        except Exception as e:
            self._add_result("build_migration", False, str(e))
            return []

    def test_execute_migration(self, script_names: List[str]):
        """Test 9: Execute migration."""
        logger.info("-" * 40)
        logger.info("TEST 9: Execute Migration")
        logger.info("-" * 40)

        try:
            response = self.client.execute_migration(script_names)

            if response.get("code") == 0:
                self._add_result("execute_migration", True,
                                 f"Migration started: {response.get('data', {})}",
                                 response)
                return True
            else:
                self._add_result("execute_migration", False, f"Error: {response}")
                return False

        except Exception as e:
            self._add_result("execute_migration", False, str(e))
            return False

    def test_monitor_progress(self, script_names: List[str], max_checks: int = 3):
        """Test 10: Monitor migration progress."""
        logger.info("-" * 40)
        logger.info("TEST 10: Monitor Migration Progress")
        logger.info("-" * 40)

        try:
            for script_name in script_names:
                for check_num in range(max_checks):
                    response = self.client.query_status(script_name)

                    if response.get("code") == 0:
                        status_data = response.get("data", {})
                        status = status_data.get("status", "UNKNOWN")
                        progress = status_data.get("progress", 0)
                        logger.info(f"  [{check_num + 1}/{max_checks}] {script_name}: "
                                   f"status={status}, progress={progress}%")

                        if status == "SUCCEEDED":
                            break

                    time.sleep(0.2)  # Small delay between checks

            self._add_result("monitor_progress", True,
                             "Migration progress monitored successfully")

        except Exception as e:
            self._add_result("monitor_progress", False, str(e))

    # ==================== Helper Function Tests ====================

    def test_build_table_mapping(self):
        """Test build_table_mapping: source field per type, where, preSql, target_columns."""
        logger.info("-" * 40)
        logger.info("TEST 11: build_table_mapping (field map / where / preSql / target_columns)")
        logger.info("-" * 40)
        try:
            from api_client import build_table_mapping

            # Source identifier per type
            m = build_table_mapping("MYSQL", "users")
            assert m["source"]["table"] == "users", "RDBMS should use 'table'"
            m = build_table_mapping("INFLUXDB2X", "test_tb")
            assert m["source"]["measurement"] == "test_tb", "INFLUXDB should use 'measurement'"
            m = build_table_mapping("MONGODB", "my_collection")
            assert m["source"]["collectionName"] == "my_collection", "MONGODB should use 'collectionName'"

            # where + preSql/postSql + target_columns
            m = build_table_mapping(
                "MYSQL", "test_tb",
                columns="ts,c1,1 as t1",
                target_columns="ts,c1,t1",
                where="ts >= '2025-01-01 00:00:00'",
                pre_sql=["drop table if exists test_tb"],
                post_sql=["vacuum"],
            )
            assert m["source"]["where"].startswith("ts >="), "where missing"
            assert m["target"]["column"] == "ts,c1,t1", "target_columns not applied"
            assert m["target"]["preSql"] == ["drop table if exists test_tb"], "preSql missing"
            assert m["target"]["postSql"] == ["vacuum"], "postSql missing"

            # FTP/HDFS rejected
            try:
                build_table_mapping("FTP", "x")
                raise AssertionError("FTP should be rejected")
            except ValueError:
                pass

            self._add_result("build_table_mapping", True, "All mapping variants verified")
        except Exception as e:
            self._add_result("build_table_mapping", False, str(e))

    def test_build_influxdb_mapping(self):
        """Test build_influxdb_mapping: measurement, _time columns, required time range."""
        logger.info("-" * 40)
        logger.info("TEST 12: build_influxdb_mapping (time range REQUIRED)")
        logger.info("-" * 40)
        try:
            from api_client import build_influxdb_mapping

            source_db = {
                "tableMap": {
                    "test_tb": {
                        "columns": [
                            {"sourceColumnName": "_time", "columnName": "ts"},
                            {"sourceColumnName": "c1", "columnName": "c1"},
                            {"sourceColumnName": "t1", "columnName": "t1"},
                        ]
                    }
                }
            }
            # Time range is REQUIRED
            try:
                build_influxdb_mapping(source_db, "test_tb")
                raise AssertionError("Missing time range should raise")
            except ValueError:
                pass

            m = build_influxdb_mapping(
                source_db, "test_tb",
                begin_datetime="2025-10-22 00:00:00",
                end_datetime="2025-10-26 00:00:00",
            )
            assert m["source"]["measurement"] == "test_tb", "measurement missing"
            assert m["source"]["column"].startswith("_time,"), "source column must start with _time"
            assert m["target"]["column"].startswith("ts,"), "target column uses columnName"
            assert m["source"]["splitIntervalS"] == 86400, "default splitIntervalS"
            assert m["source"]["beginDateTime"] == "2025-10-22 00:00:00", "beginDateTime"

            self._add_result("build_influxdb_mapping", True, "Mapping + required range verified")
        except Exception as e:
            self._add_result("build_influxdb_mapping", False, str(e))

    def test_build_added_column(self):
        """Test build_added_column: type from default value; float -> ordinary tag only."""
        logger.info("-" * 40)
        logger.info("TEST 13: build_added_column (type derivation + float demotion)")
        logger.info("-" * 40)
        try:
            from api_client import build_added_column

            # int default -> INT4, eligible for primary tag, NOT NULL
            c = build_added_column("t1", 1, source_type="MYSQL", is_tag=True, is_primary_tag=True)
            assert c["columnType"] == "INT4" and c["isPrimaryTag"] is True and c["nullAble"] is False

            # InfluxDB int -> INT8
            c = build_added_column("t1", 1, source_type="INFLUXDB2X", is_tag=True, is_primary_tag=True)
            assert c["columnType"] == "INT8", "InfluxDB int should map to INT8"

            # str default -> VARCHAR
            c = build_added_column("t2", "x", source_type="MYSQL", is_tag=True, is_primary_tag=True)
            assert c["columnType"] == "VARCHAR"

            # float default -> FLOAT4, FORCED to ordinary tag
            c = build_added_column("t3", 1.5, source_type="MYSQL", is_tag=True, is_primary_tag=True)
            assert c["columnType"] == "FLOAT4" and c["isPrimaryTag"] is False and c["isTag"] is True

            # Source column types per source type
            assert build_added_column("t1", 1, source_type="ORACLE")["sourceColumnType"] == "NUMBER(10,0)"
            assert build_added_column("t1", 1, source_type="POSTGRESQL")["sourceColumnType"] == "INTEGER"

            self._add_result("build_added_column", True, "Type derivation verified")
        except Exception as e:
            self._add_result("build_added_column", False, str(e))

    def test_build_manual_metadata(self):
        """Test build_manual_metadata: Database object from user-provided structure."""
        logger.info("-" * 40)
        logger.info("TEST 14: build_manual_metadata (sources without metadata support)")
        logger.info("-" * 40)
        try:
            from api_client import build_manual_metadata

            db = build_manual_metadata(
                "CLICKHOUSE", "clickhouse_kwdb", "test_tb",
                columns=[
                    {"columnName": "ts", "sourceColumnType": "TIMESTAMP(3)"},
                    {"columnName": "c1", "sourceColumnType": "Int32"},
                ],
            )
            t = db["tableMap"]["test_tb"]
            assert len(t["columns"]) == 2, "column count"
            assert t["columns"][0]["columnName"] == "ts", "first column"
            assert t["columns"][0]["isTs"] is False, "no marks yet"

            self._add_result("build_manual_metadata", True, "Manual metadata built")
        except Exception as e:
            self._add_result("build_manual_metadata", False, str(e))

    def test_mark_time_series_columns(self):
        """Test mark_time_series_columns: ts/tag/primaryTag marks + NOT NULL for primary tags."""
        logger.info("-" * 40)
        logger.info("TEST 15: mark_time_series_columns (marks + nullAble)")
        logger.info("-" * 40)
        try:
            from api_client import mark_time_series_columns

            db = {
                "tableMap": {
                    "orders": {
                        "columns": [
                            {"columnName": "order_time", "nullAble": True},
                            {"columnName": "customer_id", "nullAble": True},
                            {"columnName": "status", "nullAble": True},
                        ]
                    }
                }
            }
            mark_time_series_columns(db, "orders", time_column="order_time",
                                     primary_tags=["customer_id"], tags=["status"])
            cols = {c["columnName"]: c for c in db["tableMap"]["orders"]["columns"]}
            assert cols["order_time"]["isTs"] is True, "time column mark"
            assert cols["customer_id"]["isTag"] is True and cols["customer_id"]["isPrimaryTag"] is True
            assert cols["customer_id"]["nullAble"] is False, "primary tag auto NOT NULL"
            assert cols["status"]["isTag"] is True and cols["status"]["isPrimaryTag"] is False

            self._add_result("mark_time_series_columns", True, "Marks verified")
        except Exception as e:
            self._add_result("mark_time_series_columns", False, str(e))

    def test_connection_normalization(self):
        """Test test_connection normalization: code=0 + non-SUCCEED data -> 2001."""
        logger.info("-" * 40)
        logger.info("TEST 16: test_connection normalization (KDTS returns code=0 on failure)")
        logger.info("-" * 40)
        try:
            from api_client import KDTSClient

            class MockClient(KDTSClient):
                def __init__(self, fake):
                    self.fake = fake
                    super().__init__(base_url="http://x")
                def _request(self, *a, **k):
                    return dict(self.fake)

            # Failure with code=0 + error text in data (e.g. TDengine driver missing)
            c = MockClient({"code": 0, "data": "Connection failed: Cannot locate driver", "timestamp": 1, "message": None})
            r = c.test_connection({})
            assert r["code"] == 2001, "should normalize to 2001"
            assert "Cannot locate driver" in r["message"]

            # Success
            c2 = MockClient({"code": 0, "data": "SUCCEED", "timestamp": 1, "message": None})
            r2 = c2.test_connection({})
            assert r2["code"] == 0, "success unchanged"

            self._add_result("connection_normalization", True, "Normalization verified")
        except Exception as e:
            self._add_result("connection_normalization", False, str(e))

    def test_execute_migration_batches(self):
        """Test execute_migration_batches: batched execution with per-batch monitoring."""
        logger.info("-" * 40)
        logger.info("TEST 17: execute_migration_batches (batch execution)")
        logger.info("-" * 40)
        try:
            from migration_task import MigrationWorkflowManager

            class MockClient:
                def __init__(self):
                    self.execute_calls = []
                    self.status_calls = {}
                def execute_migration(self, names):
                    self.execute_calls.append(list(names))
                    return {"code": 0, "data": ["log.txt"]}
                def query_status(self, name):
                    n = self.status_calls.get(name, 0)
                    self.status_calls[name] = n + 1
                    return {"code": 0, "data": {"status": "SUCCEEDED" if n > 0 else "UNKNOWN"}}

            mgr = MigrationWorkflowManager(api_client=MockClient())
            scripts = [f"script_{i}.json" for i in range(25)]
            result = mgr.execute_migration_batches(scripts, batch_size=10, poll_interval=0)

            assert result["total_batches"] == 3, "batches: 10/10/5"
            assert result["all_succeeded"] is True, "all batches succeeded"
            assert len(mgr.api_client.execute_calls) == 3, "3 execute calls"
            assert [len(b) for b in mgr.api_client.execute_calls] == [10, 10, 5]

            self._add_result("execute_migration_batches", True, "Batch execution verified")
        except Exception as e:
            self._add_result("execute_migration_batches", False, str(e))

    def run_full_test_suite(self):
        """Run complete migration flow test suite."""
        logger.info("=" * 60)
        logger.info("STARTING FULL MIGRATION FLOW TEST SUITE")
        logger.info("=" * 60)

        start_time = time.time()

        try:
            # Setup
            self.setup()

            # Test 1: Health check
            self.test_health_check()

            # Test 2: Build configurations
            source_config, target_config = self.test_build_configs()
            if not source_config or not target_config:
                logger.error("Cannot continue: Config building failed")
                return self._print_summary(start_time)

            # Test 3: Connection tests
            self.test_connections(source_config, target_config)

            # Test 4: List databases
            self.test_list_databases(source_config)

            # Test 5: Read metadata
            source_metadata = self.test_read_metadata(source_config)

            # Test 6: Preview DDL
            ddl_preview = self.test_preview_ddl(target_config, source_metadata)

            # Test 7: Execute DDL
            self.test_execute_ddl(target_config, ddl_preview)

            # Test 8: Build migration scripts
            script_names = self.test_build_migration(source_config, target_config)

            # Test 9: Execute migration
            if script_names:
                self.test_execute_migration(script_names)

                # Test 10: Monitor progress
                self.test_monitor_progress(script_names)

            # Tests 11-17: Helper functions and new features (no server needed)
            self.test_build_table_mapping()
            self.test_build_influxdb_mapping()
            self.test_build_added_column()
            self.test_build_manual_metadata()
            self.test_mark_time_series_columns()
            self.test_connection_normalization()
            self.test_execute_migration_batches()

            # Try the high-level workflow
            self._test_high_level_workflow(source_config, target_config)

        finally:
            # Teardown
            self.teardown()

        return self._print_summary(start_time)

    def _test_high_level_workflow(self, source_config: Dict, target_config: Dict):
        """Test high-level workflow methods."""
        logger.info("-" * 40)
        logger.info("TEST: High-Level Workflow (run_full_migration)")
        logger.info("-" * 40)

        try:
            # This is a simplified workflow test
            # In production, run_full_migration would orchestrate all steps
            result = self.workflow.run_full_migration(
                source_config=source_config,
                target_config=target_config,
                timeout=60,
                poll_interval=0.2
            )

            self._add_result("high_level_workflow", result.get("success", False),
                             f"Workflow completed (success={result.get('success')})",
                             result)

        except Exception as e:
            self._add_result("high_level_workflow", False, str(e))

    def _print_summary(self, start_time: float):
        """Print test summary."""
        logger.info("=" * 60)
        logger.info("TEST SUMMARY")
        logger.info("=" * 60)

        elapsed = time.time() - start_time
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["passed"])
        failed = total - passed

        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Elapsed: {elapsed:.2f}s")

        if failed > 0:
            logger.info("\nFailed Tests:")
            for result in self.test_results:
                if not result["passed"]:
                    logger.info(f"  - {result['test']}: {result['message']}")

        logger.info("=" * 60)

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "elapsed": elapsed,
            "results": self.test_results,
            "success": failed == 0
        }


def main():
    parser = argparse.ArgumentParser(description="Test Migration Flow")
    parser.add_argument("--port", type=int, default=8989,
                       help="Mock server port (default: 8989)")
    parser.add_argument("--test", type=str, default=None,
                       help="Run specific test (e.g., health, connection, metadata)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")

    args = parser.parse_args()

    # Show environment info
    env_info = get_environment_info()
    logger.info(f"Environment: {env_info}")

    # Run tests
    tester = MigrationFlowTester(mock_port=args.port)

    if args.test:
        # Run specific test
        tester.setup()
        try:
            if args.test == "health":
                tester.test_health_check()
            # Add more specific tests here
        finally:
            tester.teardown()
    else:
        # Run full test suite
        result = tester.run_full_test_suite()

        # Exit with appropriate code
        sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
