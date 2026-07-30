"""
mock_server.py - Mock KDTS Server for Local Testing

A lightweight mock server that simulates KDTS REST API responses.
Supports all 10 API endpoints with realistic mock data for MySQL to KaiwuDB migration.

Usage:
    # Start mock server on default port (8989)
    python mock_server.py

    # Start on custom port
    python mock_server.py --port 9999

    # Start in background for testing
    import threading
    server_thread = threading.Thread(target=start_mock_server, args=(8989,))
    server_thread.start()
"""

import json
import time
import threading
import argparse
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


# ==================== Mock Data ====================

MOCK_MYSQL_DATABASE = {
    "name": "shop_db",
    "type": "MySQL",
    "tables": [
        {
            "name": "users",
            "columns": [
                {"name": "id", "type": "INT", "primaryKey": True, "nullable": False},
                {"name": "username", "type": "VARCHAR(50)", "nullable": False},
                {"name": "email", "type": "VARCHAR(100)", "nullable": True},
                {"name": "created_at", "type": "DATETIME", "nullable": False},
                {"name": "status", "type": "TINYINT", "nullable": False, "default": "1"},
            ],
            "primaryKey": {"columns": ["id"], "name": "PRIMARY"},
            "indexes": [
                {"name": "idx_username", "columns": ["username"], "unique": True},
            ],
        },
        {
            "name": "orders",
            "columns": [
                {"name": "order_id", "type": "BIGINT", "primaryKey": True, "nullable": False},
                {"name": "user_id", "type": "INT", "nullable": False},
                {"name": "total_amount", "type": "DECIMAL(10,2)", "nullable": False},
                {"name": "status", "type": "VARCHAR(20)", "nullable": False},
                {"name": "order_time", "type": "DATETIME", "nullable": False},
            ],
            "primaryKey": {"columns": ["order_id"], "name": "PRIMARY"},
            "foreignKeys": [
                {"name": "fk_user_id", "columns": ["user_id"], "referenceTable": "users", "referenceColumns": ["id"]},
            ],
            "indexes": [
                {"name": "idx_user_id", "columns": ["user_id"]},
                {"name": "idx_order_time", "columns": ["order_time"]},
            ],
        },
    ],
}

MOCK_DDL_RESPONSE = {
    "ddlScript": {
        "database": "shop_db",
        "createDatabase": "CREATE DATABASE IF NOT EXISTS shop_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        "tables": [
            {
                "name": "users",
                "ddl": """CREATE TABLE users (
    id INT NOT NULL,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    created_at DATETIME NOT NULL,
    status TINYINT NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    UNIQUE INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;""",
            },
            {
                "name": "orders",
                "ddl": """CREATE TABLE orders (
    order_id BIGINT NOT NULL,
    user_id INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    order_time DATETIME NOT NULL,
    PRIMARY KEY (order_id),
    INDEX idx_user_id (user_id),
    INDEX idx_order_time (order_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;""",
            },
        ],
    }
}

MOCK_MIGRATION_SCRIPT = {
    "scripts": [
        {
            "name": "shop_db_to_kwdb_20260730_120000",
            "source": {
                "engine": "MySQL",
                "table": "users",
                "columns": ["id", "username", "email", "created_at", "status"],
            },
            "target": {
                "engine": "KaiwuDB",
                "table": "users",
                "columns": ["id", "username", "email", "created_at", "status"],
            },
            "config": {
                "reducers": {
                    "id": "long",
                    "username": "string",
                    "email": "string",
                    "created_at": "string",
                    "status": "int",
                },
                "speed": 100,
                "channel": 1,
            },
        },
    ],
}

# Mock task states
class MockTaskState:
    def __init__(self):
        self.states = {}

    def get_state(self, script_name: str) -> Dict[str, Any]:
        if script_name not in self.states:
            self.states[script_name] = {
                "status": "RUNNING",
                "progress": 0,
                "total": 1000,
                "processed": 0,
                "startTime": int(time.time() * 1000),
            }
        return self.states[script_name]

    def update_state(self, script_name: str, state: Dict[str, Any]):
        self.states[script_name] = state

    def simulate_progress(self, script_name: str):
        state = self.get_state(script_name)
        if state["status"] == "RUNNING":
            state["progress"] = min(state["progress"] + 20, 100)  # Faster progress for testing
            state["processed"] = int(state["total"] * state["progress"] / 100)
            if state["progress"] >= 100:
                state["status"] = "SUCCEEDED"  # Match MigrationStatus.SUCCEEDED
                state["endTime"] = int(time.time() * 1000)


# ==================== Request Handler ====================

class MockKDTSHandler(BaseHTTPRequestHandler):
    """HTTP request handler for mock KDTS server."""

    # Class-level task state
    task_state = MockTaskState()

    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {format % args}")

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # Health check
        if path == "/kdts/api/v1/health" or path == "/health":
            self._send_response(200, {
                "code": 0,
                "message": "OK",
                "timestamp": int(time.time() * 1000),
                "data": {"status": "UP", "version": "2.0.0-MOCK"},
            })
        # Query task status
        elif path.endswith("/migration/status") or path.endswith("/datax/status") or path.endswith("/status"):
            script_name = query.get("scriptName", ["unknown"])[0]
            # Simulate progress before returning state
            self.task_state.simulate_progress(script_name)
            state = self.task_state.get_state(script_name)
            self._send_response(200, {
                "code": 0,
                "message": "Success",
                "timestamp": int(time.time() * 1000),
                "data": state,
            })
        else:
            self._send_response(404, {
                "code": 404,
                "message": f"Mock endpoint not found: {path}",
                "timestamp": int(time.time() * 1000),
            })

    def do_POST(self):
        """Handle POST requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        # Log incoming request
        logger.info(f"POST {path}")

        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b''

        try:
            data = json.loads(body.decode('utf-8')) if body else {}
        except json.JSONDecodeError:
            self._send_response(400, {"code": 400, "message": "Invalid JSON", "timestamp": int(time.time() * 1000)})
            return

        # Route to mock handlers (check more specific paths first)
        if path.endswith("/datasource/validate") or path.endswith("/validate"):
            logger.info("Routing to: _handle_validate")
            self._handle_validate(data)
        elif path.endswith("/datasource/databases") or path.endswith("/databases"):
            logger.info("Routing to: _handle_list_databases")
            self._handle_list_databases(data)
        elif path.endswith("/datasource/metadata"):
            logger.info("Routing to: _handle_read_metadata")
            self._handle_read_metadata(data)
        elif path.endswith("/metadata/preview") or path.endswith("/preview"):
            logger.info("Routing to: _handle_preview_ddl")
            self._handle_preview_ddl(data)
        elif path.endswith("/metadata/execute") or path.endswith("/execute-ddl"):
            logger.info("Routing to: _handle_execute_ddl")
            self._handle_execute_ddl(data)
        elif path.endswith("/migration/build") or path.endswith("/build"):
            logger.info("Routing to: _handle_build_migration")
            self._handle_build_migration(data)
        elif path.endswith("/migration/execute") or path.endswith("/execute"):
            logger.info("Routing to: _handle_execute_migration")
            self._handle_execute_migration(data)
        elif path.endswith("/migration/control") or path.endswith("/control"):
            logger.info("Routing to: _handle_control_task")
            self._handle_control_task(data)
        else:
            logger.warning(f"No route found for: {path}")
            self._send_response(404, {
                "code": 404,
                "message": f"Mock endpoint not found: {path}",
                "timestamp": int(time.time() * 1000),
            })

    def _handle_validate(self, data: Dict):
        """Mock connection validation."""
        host = data.get("host", "localhost")
        port = data.get("port", 3306)
        logger.info(f"Mock validate connection to {host}:{port}")

        # Simulate successful connection
        self._send_response(200, {
            "code": 0,
            "message": "Connection successful",
            "timestamp": int(time.time() * 1000),
            "data": "SUCCEED",
        })

    def _handle_list_databases(self, data: Dict):
        """Mock list databases."""
        logger.info("Mock list databases")

        self._send_response(200, {
            "code": 0,
            "message": "Success",
            "timestamp": int(time.time() * 1000),
            "data": ["shop_db", "test_db", "user_db"],
        })

    def _handle_read_metadata(self, data: Dict):
        """Mock read metadata."""
        db_name = data.get("dbName", "shop_db")
        logger.info(f"Mock read metadata for {db_name}")

        self._send_response(200, {
            "code": 0,
            "message": "Success",
            "timestamp": int(time.time() * 1000),
            "data": MOCK_MYSQL_DATABASE,
        })

    def _handle_preview_ddl(self, data: Dict):
        """Mock preview DDL."""
        logger.info("Mock preview DDL")

        self._send_response(200, {
            "code": 0,
            "message": "Success",
            "timestamp": int(time.time() * 1000),
            "data": MOCK_DDL_RESPONSE,
        })

    def _handle_execute_ddl(self, data: Dict):
        """Mock execute DDL."""
        auto_ddl = data.get("autoDdl", True)
        logger.info(f"Mock execute DDL (auto={auto_ddl})")

        self._send_response(200, {
            "code": 0,
            "message": "DDL executed successfully",
            "timestamp": int(time.time() * 1000),
            "data": {
                "tablesCreated": 2,
                "executionTime": 150,
            },
        })

    def _handle_build_migration(self, data: Dict):
        """Mock build migration."""
        logger.info("Mock build migration")
        scripts = MOCK_MIGRATION_SCRIPT["scripts"]
        script_names = [s["name"] for s in scripts]

        self._send_response(200, {
            "code": 0,
            "message": "Migration scripts built successfully",
            "timestamp": int(time.time() * 1000),
            "data": {
                "scriptNames": script_names,
                "scriptCount": len(scripts),
            },
        })

    def _handle_execute_migration(self, data: Dict):
        """Mock execute migration."""
        script_names = data.get("scriptNames", [])
        logger.info(f"Mock execute migration: {script_names}")

        # Initialize task states
        for name in script_names:
            self.task_state.get_state(name)

        self._send_response(200, {
            "code": 0,
            "message": "Migration tasks started",
            "timestamp": int(time.time() * 1000),
            "data": {
                "taskIds": [f"TASK_{i}" for i in range(len(script_names))],
                "status": "RUNNING",
            },
        })

    def _handle_control_task(self, data: Dict):
        """Mock control task."""
        action = data.get("action", "")
        script_name = data.get("scriptName", "")
        logger.info(f"Mock control task: {action} on {script_name}")

        if action.upper() == "KILL":
            state = self.task_state.get_state(script_name)
            state["status"] = "KILLED"
            state["endTime"] = int(time.time() * 1000)

        self._send_response(200, {
            "code": 0,
            "message": f"Task {action} executed",
            "timestamp": int(time.time() * 1000),
            "data": state if action.upper() == "KILL" else {"action": action},
        })

    def _send_response(self, status_code: int, response_data: Dict):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode('utf-8'))


# ==================== Server Control ====================

class MockKDSServer:
    """Mock KDTS Server with controllable state."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8989):
        self.host = host
        self.port = port
        self.http_server = None
        self.server_thread = None

    def start(self):
        """Start mock server in background thread."""
        self.http_server = HTTPServer((self.host, self.port), MockKDTSHandler)
        logger.info(f"Mock KDTS server starting on {self.host}:{self.port}")

        self.server_thread = threading.Thread(target=self.http_server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        logger.info(f"Mock KDTS server running on http://{self.host}:{self.port}")

    def stop(self):
        """Stop mock server."""
        if self.http_server:
            self.http_server.shutdown()
            logger.info("Mock KDTS server stopped")

    def wait(self, timeout: float = None):
        """Wait for server thread."""
        if self.server_thread:
            self.server_thread.join(timeout)


def start_mock_server(port: int = 8989, host: str = "127.0.0.1") -> MockKDSServer:
    """
    Start mock KDTS server.

    Args:
        port: Server port (default: 8989)
        host: Server host (default: 127.0.0.1)

    Returns:
        MockKDSServer instance
    """
    server = MockKDSServer(host, port)
    server.start()
    return server


# ==================== CLI Entry Point ====================

def main():
    parser = argparse.ArgumentParser(description="Mock KDTS Server for local testing")
    parser.add_argument("--port", type=int, default=8989, help="Server port (default: 8989)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Server host (default: 127.0.0.1)")
    parser.add_argument("--no-ssl", action="store_true", help="Disable SSL (always disabled for mock)")

    args = parser.parse_args()

    server = MockKDSServer(args.host, args.port)
    server.start()

    try:
        logger.info("Press Ctrl+C to stop the server")
        server.wait()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        server.stop()


if __name__ == "__main__":
    main()
