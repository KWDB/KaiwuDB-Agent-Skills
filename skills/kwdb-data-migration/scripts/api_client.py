"""
api_client.py - Unified KDTS Server API Client

Provides complete REST API interaction with KDTS Server for heterogeneous database migration.
All 10 API endpoints are wrapped with request building, response parsing, and error handling.

Configuration Priority (highest to lowest):
1. Environment variables: KDTS_BASE_URL or KDTS_HOST + KDTS_PORT
2. Explicit parameters passed to constructor
3. Config file: kdts_config.json (in script dir or CWD)
4. Default: http://127.0.0.1:8989

Usage:
    python api_client.py <action> [options]

Actions:
    test_connection     Test data source connectivity
    list_databases      List databases on source
    read_metadata       Read source metadata (tables, columns, etc.)
    preview_ddl         Preview DDL for target KaiwuDB
    execute_ddl         Execute DDL on target KaiwuDB
    build_migration     Build DataX migration script
    execute_migration   Execute built migration scripts
    query_status        Query migration task status
    control_task        Kill or query running task
"""

import requests
import json
import sys
import time
import logging
from typing import Dict, List, Optional, Any

# Handle imports for both package and direct script usage
try:
    from .config import KDTSConfig, resolve_base_url, get_environment_info
    from .data_source import DataSourceManager
except ImportError:
    from config import KDTSConfig, resolve_base_url, get_environment_info
    from data_source import DataSourceManager

logger = logging.getLogger(__name__)


class KDTSClient:
    """
    Unified client for KDTS Server REST API.

    Handles all API interactions including request building,
    response parsing, timeout management, and error code conversion.
    """

    def __init__(self, base_url: Optional[str] = None,
                 timeout: Optional[int] = None,
                 connect_timeout: Optional[int] = None,
                 api_prefix: Optional[str] = None,
                 config_file: Optional[str] = None):
        """
        Initialize KDTS API client with multi-layer configuration.

        Configuration Priority:
        1. Environment variables (KDTS_BASE_URL, KDTS_HOST, etc.)
        2. Explicit constructor parameters
        3. Config file (kdts_config.json)
        4. Default values (127.0.0.1:8989)

        Args:
            base_url: Explicit KDTS Server URL (highest priority)
                     If None, checks environment then config file then default.
            timeout: Read timeout in seconds (default: from config or 30)
            connect_timeout: Connection timeout in seconds (default: from config or 5)
            api_prefix: API path prefix (default: from config or /kdts/api/v1)
            config_file: Optional path to config file

        Example:
            # Use environment variables
            export KDTS_BASE_URL="http://10.0.0.1:8989"
            client = KDTSClient()

            # Or explicit configuration
            client = KDTSClient(base_url="http://127.0.0.1:8989")

            # Or with config file
            client = KDTSClient(config_file="/path/to/kdts_config.json")
        """
        # Initialize configuration manager
        config_manager = KDTSConfig(config_file)

        # Resolve base_url with priority chain
        self.base_url = config_manager.get_base_url(base_url).rstrip('/')

        # Resolve other parameters
        self.api_prefix = api_prefix or config_manager.get_api_prefix()
        self.timeout = timeout or config_manager.get_timeout()
        self.connect_timeout = connect_timeout or config_manager.get_connect_timeout()

        # Log configuration source
        config_source = config_manager.detect_config_source()
        logger.info(f"KDTSClient initialized: base_url={self.base_url}, "
                     f"source={config_source}")

        # Initialize HTTP session
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def _build_url(self, endpoint: str) -> str:
        """Build full API URL from endpoint path."""
        return f"{self.base_url}{self.api_prefix}{endpoint}"

    def _request(self, method: str, endpoint: str,
                 data: Optional[Dict] = None,
                 params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Send HTTP request and parse response.

        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint path (e.g., /health, /datasource/validate)
            data: Request body dict (for POST)
            params: Query params dict (for GET)

        Returns:
            Parsed response dict with format: {code, message, timestamp, data}

        Raises:
            requests.exceptions.RequestException: Network errors
        """
        url = self._build_url(endpoint)

        try:
            if method == 'GET':
                response = self.session.get(
                    url, params=params,
                    timeout=(self.connect_timeout, self.timeout)
                )
            elif method == 'POST':
                response = self.session.post(
                    url, json=data,
                    timeout=(self.connect_timeout, self.timeout)
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Handle HTTP-level errors (503 for resource exhaustion)
            if response.status_code == 503:
                retry_after = response.headers.get('Retry-After', '60')
                return {
                    "code": 5001,
                    "message": f"Service unavailable. Retry after {retry_after} seconds.",
                    "timestamp": int(time.time() * 1000),
                    "data": None
                }

            response.raise_for_status()
            return response.json()

        except requests.exceptions.ConnectionError as e:
            return {
                "code": 2001,
                "message": f"Connection failed: {str(e)}",
                "timestamp": int(time.time() * 1000),
                "data": None
            }
        except requests.exceptions.Timeout as e:
            return {
                "code": 4003,
                "message": f"Request timeout: {str(e)}",
                "timestamp": int(time.time() * 1000),
                "data": None
            }
        except json.JSONDecodeError as e:
            return {
                "code": 1005,
                "message": f"Response parse error: {str(e)}",
                "timestamp": int(time.time() * 1000),
                "data": None
            }
        except requests.exceptions.RequestException as e:
            return {
                "code": 9999,
                "message": f"Request error: {str(e)}",
                "timestamp": int(time.time() * 1000),
                "data": None
            }

    # ==================== Basic API ====================

    def health_check(self) -> Dict[str, Any]:
        """
        Check KDTS Server health status.

        Returns:
            Response dict with status info.
        """
        return self._request('GET', '/health')

    # ==================== DataSource API ====================

    def test_connection(self, source_config: Dict,
                        is_target: bool = False) -> Dict[str, Any]:
        """
        Test data source connectivity.

        Args:
            source_config: DataSource request dict with engine, type, host, port, username, password
            is_target: If True, marks this as target-side validation

        Returns:
            Validation result dict. On success, data contains 'SUCCEED'.
        """
        request = source_config.copy()
        request['isTarget'] = is_target
        return self._request('POST', '/datasource/validate', data=request)

    def list_databases(self, source_config: Dict) -> Dict[str, Any]:
        """
        List all databases on source.

        Args:
            source_config: DataSource request dict

        Returns:
            Response with data containing list of database names.
        """
        return self._request('POST', '/datasource/databases', data=source_config)

    def read_metadata(self, source_config: Dict,
                      metadata_options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Read complete source metadata (tables, columns, constraints, etc.).

        Args:
            source_config: DataSource request dict (must include dbName)
            metadata_options: Optional dict with keys (MetaData fields):
                - enable (bool): Enable metadata extraction (default: True)
                - autoDdl (bool): Auto-generate DDL (default: True)
                - primaryKey (bool): Include primary keys (default: True)
                - constraint (bool): Include constraints (default: True)
                - comment (bool): Include column comments (default: True)
                - index (bool): Include indexes (default: True)
                - view (bool): Include views (default: False)

        Returns:
            Response with data containing Database object (tables, columns, etc.)
        """
        # Default metadata options matching MetaData.java
        default_metadata = {
            "enable": True,
            "autoDdl": True,
            "primaryKey": True,
            "constraint": True,
            "comment": True,
            "index": True,
            "view": False
        }

        # Merge with user-provided options
        metadata = {**default_metadata, **(metadata_options or {})}

        request = {
            "source": source_config,
            "metadata": metadata
        }
        return self._request('POST', '/datasource/metadata', data=request)

    # ==================== Metadata API ====================

    def preview_ddl(self, target_config: Dict,
                    source_db: Dict,
                    metadata: Optional[Dict] = None,
                    is_time_series: bool = False) -> Dict[str, Any]:
        """
        Preview generated DDL for target KaiwuDB.

        Args:
            target_config: Target DataSource request dict (must be KAIWUDB)
            source_db: Complete Database object from read_metadata response
                Structure: {
                    "type": "MYSQL",
                    "name": "source_db",
                    "encoding": "UTF-8",
                    "tableMap": { "tableName": { ... Table object ... } },
                    "viewMap": { "viewName": { ... View object ... } }
                }
            metadata: Optional MetaData config dict (same as read_metadata):
                {
                    "primaryKey": True,
                    "constraint": True,
                    "comment": True,
                    "index": True,
                    "view": False
                }
            is_time_series: If True, generate time series table DDL (default: False)

        Returns:
            Response with data containing DdlScript:
                {
                    "dbName": "SOURCE_DB",
                    "createDb": "CREATE DATABASE ...",
                    "table": { "tableName": "CREATE TABLE xxx" },
                    "view": { "viewName": "CREATE VIEW xxx" }
                }
        """
        # Default metadata if not provided
        default_metadata = {
            "primaryKey": True,
            "constraint": True,
            "comment": True,
            "index": True,
            "view": False
        }

        request = {
            "target": target_config,
            "sourceDb": source_db,
            "metadata": metadata or default_metadata,
            "isTimeSeries": is_time_series
        }
        return self._request('POST', '/metadata/preview', data=request)

    def execute_ddl(self, target_config: Dict, ddl_script: Dict, auto_ddl: bool = True) -> Dict[str, Any]:
        """
        Execute DDL on target KaiwuDB.

        Args:
            target_config: Target DataSource request dict
            ddl_script: DdlScript from preview_ddl response data
                Structure: {
                    "dbName": "SOURCE_DB",
                    "createDb": "CREATE DATABASE ...",
                    "table": { "tableName": "CREATE TABLE xxx" },
                    "view": { "viewName": "CREATE VIEW xxx" }
                }
            auto_ddl: If True, auto-create database and tables (default: True)

        Returns:
            Response with data containing absolute path of SQL execution log file.
        """
        request = {
            "target": target_config,
            "ddlScript": ddl_script,
            "autoDdl": auto_ddl
        }
        return self._request('POST', '/metadata/execute', data=request)

    # ==================== DataX API ====================

    def build_migration(self, source: Dict, target: Dict,
                        tables: Optional[List[Dict]] = None,
                        data_config: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Build DataX migration script.

        Args:
            source: Source DataSource request dict
            target: Target DataSource request dict (type must be KAIWUDB)
            tables: Optional list of TableMapping dicts.
                Empty or None = auto-discover all tables (full migration)
                Each mapping has 'source' and 'target' keys.
            data_config: Optional data migration settings dict with keys:
                - enable (bool): Enable data migration (default: True)
                - fetchSize (int): Rows per fetch (default: 1000)
                - batchSize (int): Rows per batch (default: 1000)
                - setting (dict): speed and errorLimit settings

        Returns:
            Response with data containing list of generated script file names.
        """
        request = {
            "source": source,
            "target": target,
            "tables": tables or [],
            "data": data_config or {"enable": True}
        }
        return self._request('POST', '/datax/build', data=request)

    def execute_migration(self, script_names: List[str]) -> Dict[str, Any]:
        """
        Execute built migration scripts.

        Args:
            script_names: List of script file names (from build_migration response)

        Returns:
            Response with data containing list of log file paths.

        Note: KDTS API expects the request body to be a direct list of strings,
        not an object with a scriptNames field.
        """
        # Directly send the list as request body (KDTS expects List<String>)
        return self._request('POST', '/datax/execute', data=script_names)

    def query_status(self, script_name: str) -> Dict[str, Any]:
        """
        Query migration task status.

        Args:
            script_name: Migration script file name

        Returns:
            Response with data containing JobStatusResponse:
                - status: JobStatus enum (SUBMITTED, RUNNING, SUCCEEDED, FAILED, KILLED, UNKNOWN)
                - progress: Progress percentage (0-100)
                - message: Status message
        """
        return self._request('GET', '/datax/status', params={'scriptName': script_name})

    def control_task(self, script_name: str, action: str = "KILL") -> Dict[str, Any]:
        """
        Control running migration task.

        Args:
            script_name: Migration script file name
            action: Control action:
                - "QUERY": Query current status
                - "KILL": Kill running task (use with caution!)

        Returns:
            Response with data containing JobStatus after control action.
        """
        request = {
            "scriptName": script_name,
            "action": action
        }
        return self._request('POST', '/datax/control', data=request)


def build_source_config(source_type: str,
                        host: str, port: int,
                        username: str, password: str,
                        engine: str,
                        db_name: Optional[str] = None,
                        url: Optional[str] = None) -> Dict[str, Any]:
    """
    Helper function to build DataSource request dict.
    
    Note: engine is REQUIRED for all source configs per KDTS API specification.
    Use SourceType.get_engine(source_type) to determine the correct engine value.

    Args:
        source_type: Source type (MYSQL, ORACLE, KAIWUDB, etc.)
        host: Hostname or IP
        port: Port number
        username: Database username
        password: Database password
        engine: REQUIRED - Engine type (RELATIONAL or TIMESERIES)
        db_name: Optional database name
        url: Optional full JDBC URL (overrides host:port)

    Returns:
        DataSource request dict ready for API calls.

    Raises:
        ValueError: If engine is not 'RELATIONAL' or 'TIMESERIES'
    """
    # Validate engine value
    if engine not in ('RELATIONAL', 'TIMESERIES'):
        raise ValueError(f"engine must be 'RELATIONAL' or 'TIMESERIES', got '{engine}'")
    
    config = {
        "engine": engine,
        "type": source_type,
        "host": host,
        "port": port,
        "username": username,
        "password": password
    }

    if url:
        config["url"] = url
    if db_name:
        config["dbName"] = db_name

    return config


def build_target_config(engine: str,
                        host: str, port: int = 26257,
                        username: str = "root", password: str = "",
                        db_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Helper function to build KAIWUDB target config.
    
    Note: engine is REQUIRED for target config (RELATIONAL or TIMESERIES).

    Args:
        engine: Required engine type (RELATIONAL or TIMESERIES)
        host: KAIWUDB host
        port: KAIWUDB port (default: 26257)
        username: KAIWUDB username (default: root)
        password: KAIWUDB password
        db_name: Target database name

    Returns:
        Target DataSource request dict ready for API calls.
    """
    config = {
        "engine": engine,
        "type": "KAIWUDB",
        "host": host,
        "port": port,
        "username": username,
        "password": password,
        "isTarget": True
    }

    if db_name:
        config["dbName"] = db_name

    return config


def build_table_mapping(source_type: str, source_table: str,
                        target_table: Optional[str] = None,
                        columns: Optional[str] = None,
                        write_mode: str = "insert",
                        source_source_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Helper function to build table mapping for migration.

    Args:
        source_type: KDTS source type (for determining sourceSourceType)
        source_table: Source table name
        target_table: Target table name (default: same as source)
        columns: Column selection string (e.g., "col1,col2,col3")
        write_mode: Write mode for target KaiwuDB (insert, replace, etc.)
        source_source_type: Override sourceSourceType (auto-detected if None)

    Returns:
        TableMapping dict ready for build_migration.
    """
    # Auto-detect sourceSourceType from KDTS source type
    if not source_source_type:
        source_source_type_map = {
            "MYSQL": "RDBMS", "ORACLE": "RDBMS", "POSTGRESQL": "RDBMS",
            "SQLSERVER": "RDBMS", "CLICKHOUSE": "RDBMS",
            "KAIWUDB": "KAIWUDB",
            "TDENGINE2X": "TDENGINE", "TDENGINE3X": "TDENGINE",
            "INFLUXDB1X": "INFLUXDB", "INFLUXDB2X": "INFLUXDB",
            "OPENTSDB": "OPENTSDB",
            "MONGODB": "MONGODB",
            "FTP": "FTP", "SFTP": "FTP",
            "HDFS": "HDFS"
        }
        source_source_type = source_source_type_map.get(source_type.upper(), "RDBMS")

    return {
        "source": {
            "sourceType": source_source_type,
            "table": source_table,
            "column": columns or "*"
        },
        "target": {
            "sourceType": "KAIWUDB",
            "table": target_table or source_table,
            "column": columns or "*",
            "writeMode": write_mode
        }
    }


# ==================== CLI Entry Point ====================

def main():
    """
    CLI entry point for quick testing and automation.

    Parses command line arguments and executes the specified action.
    """
    if len(sys.argv) < 2:
        print("Usage: python api_client.py <action> [options]")
        print("\nActions:")
        print("  test_connection     Test data source connectivity")
        print("  list_databases      List databases on source")
        print("  read_metadata       Read source metadata")
        print("  preview_ddl         Preview DDL for target")
        print("  execute_ddl         Execute DDL on target")
        print("  build_migration     Build migration script")
        print("  execute_migration   Execute migration")
        print("  query_status        Query task status")
        print("  control_task        Kill/control task")
        sys.exit(1)

    action = sys.argv[1]

    # Quick example usage
    if action == "test_connection":
        client = KDTSClient(base_url="http://localhost:8989")
        # engine is REQUIRED for all source configs per KDTS API
        source = build_source_config(
            source_type="MYSQL",
            host="127.0.0.1", port=3306,
            username="root", password="123456",
            engine="RELATIONAL"
        )
        result = client.test_connection(source)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
