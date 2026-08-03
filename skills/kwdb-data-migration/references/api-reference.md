# KDTS API Reference (Simplified)

This document provides a condensed reference for all KDTS REST API endpoints.
For full documentation, see `kw-datax-utils/docs/api.md`.

## Base Configuration

- **Base URL**: `http://{host}:{port}` (default port: 8080)
- **API Prefix**: `/kdts/api/v1`
- **Content-Type**: `application/json`
- **Response Format**: `Result<T>` wrapper:
  ```json
  {
    "code": 0,
    "message": "success",
    "timestamp": 1719290000000,
    "data": {}
  }
  ```

---

## 1. Health Check

### GET /health

Check if KDTS server is running.

**Request**: No parameters

**Response**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "status": "UP"
  }
}
```

---

## 2. DataSource APIs

### POST /datasource/validate

Test connection to data source or target.

**Request Body**: `DataSourceRequest`

```json
{
  "engine": "RELATIONAL",
  "type": "MYSQL",
  "url": "jdbc:mysql://host:3306/db",
  "host": "127.0.0.1",
  "port": 3306,
  "username": "user",
  "password": "pass",
  "dbName": "database",
  "isTarget": false
}
```

| Field    | Type    | Required | Description                         |
|----------|---------|----------|-------------------------------------|
| engine   | String  | Yes      | "RELATIONAL" or "TIMESERIES"        |
| type     | String  | Yes      | Source type (MYSQL, ORACLE, etc.)   |
| url      | String  | No       | Full JDBC URL (overrides host:port) |
| host     | String  | No*      | Hostname or IP                      |
| port     | Integer | No*      | Port number                         |
| username | String  | Yes      | Database username                   |
| password | String  | Yes      | Database password                   |
| dbName   | String  | No       | Default database                    |
| isTarget | Boolean | No       | Set true for target validation      |

*Required if url not provided

**Response**:

```json
{
  "code": 0,
  "message": "success",
  "data": "SUCCEED"
}
```

### POST /datasource/databases

List all databases on source.

**Request Body**: `DataSourceRequest` (engine, type, host, port, username, password required)

**Response**:

```json
{
  "code": 0,
  "data": [
    "db1",
    "db2",
    "db3"
  ]
}
```

### POST /datasource/metadata

Read source metadata (tables, columns, PKs, constraints, indexes).

**Request Body**: `MetadataRequest`

```json
{
  "source": {},
  "metadata": {
    "enable": true,
    "autoDdl": true,
    "primaryKey": true,
    "constraint": true,
    "comment": true,
    "index": false,
    "view": false
  }
}
```

**Response**:

```json
{
  "code": 0,
  "data": {
    "name": "source_db",
    "tables": [
      {
        "name": "users",
        "columns": [
          {
            "name": "id",
            "type": "BIGINT",
            "nullable": false
          },
          {
            "name": "name",
            "type": "VARCHAR(100)",
            "nullable": true
          }
        ],
        "primaryKeys": [
          "id"
        ],
        "comment": "User table"
      }
    ]
  }
}
```

---

## 3. Metadata APIs

### POST /metadata/preview

Preview DDL for target KaiwuDB.

**Request Body**: `PreviewDdlRequest`

```json
{
  "target": {},
  "sourceDb": {},
  "metadata": {
    "primaryKey": true,
    "constraint": true,
    "comment": true,
    "index": true,
    "view": false
  },
  "isTimeSeries": false
}
```

**Response**:

```json
{
  "code": 0,
  "data": {
    "dbName": "SOURCE_DB",
    "createDb": "CREATE DATABASE \"SOURCE_DB\"",
    "table": {
      "users": "CREATE TABLE \"users\" (\"id\" BIGINT NOT NULL, \"name\" VARCHAR(100), PRIMARY KEY (\"id\"))"
    },
    "view": {}
  }
}
```

### POST /metadata/execute

Execute DDL on target KaiwuDB.

**Request Body**: `ExecuteDdlRequest`

```json
{
  "target": {},
  "ddlScript": {},
  "autoDdl": true
}
```

**Response**:

```json
{
  "code": 0,
  "data": "/opt/kdts/data/sql/kaiwudb_ddl_1719290000.sql"
}
```

---

## 4. DataX APIs

### POST /datax/build

Build DataX migration job script.

**Request Body**: `MigrateDataRequest`

```json
{
  "source": {},
  "target": {},
  "tables": [
    {
      "source": {
        "sourceType": "RDBMS",
        "table": "users",
        "column": "id,name,email"
      },
      "target": {
        "sourceType": "KAIWUDB",
        "table": "users",
        "column": "id,name,email",
        "writeMode": "insert"
      }
    }
  ],
  "data": {
    "enable": true,
    "fetchSize": 1000,
    "batchSize": 1000,
    "setting": {
      "speed": {
        "channel": 1
      },
      "errorLimit": {
        "percentage": 0.02
      }
    }
  }
}
```

**KeyNotes**:

- Empty `tables` array = full database migration (auto-discover)
- `tables` with items = table-level migration
- Target `sourceType` must be "KAIWUDB"

**Response**:

```json
{
  "code": 0,
  "data": [
    "MYSQL2KAIWUDB_1719290000.json"
  ]
}
```

### POST /datax/execute

Execute built migration scripts.

**Request Body**: List of script names

```json
[
  "MYSQL2KAIWUDB_1719290000.json"
]
```

**Response**:

```json
{
  "code": 0,
  "data": [
    "/opt/kdts/data/log/kaiwudb_migrate_1719290000.log"
  ]
}
```

### GET /datax/status

Query migration task status.

**Query Parameter**: `scriptName` (script file name)

**Response**:

```json
{
  "code": 0,
  "data": {
    "scriptName": "MYSQL2KAIWUDB_1719290000.json",
    "status": "RUNNING",
    "progress": 45.2,
    "message": "Processing batch 452/1000",
    "startTime": 1719290000000,
    "elapsedTime": 125000
  }
}
```

**Status Values**:

| Status    | Description                      |
|-----------|----------------------------------|
| SUBMITTED | Script built, not yet started    |
| RUNNING   | Migration in progress            |
| SUCCEEDED | Migration completed successfully |
| FAILED    | Migration failed                 |
| KILLED    | Migration killed by user         |
| UNKNOWN   | Status cannot be determined      |

### POST /datax/control

Control migration task (query or kill).

**Request Body**: `JobControlRequest`

```json
{
  "scriptName": "MYSQL2KAIWUDB_1719290000.json",
  "action": "KILL"
}
```

| Action | Description                              |
|--------|------------------------------------------|
| QUERY  | Get current status (same as GET /status) |
| KILL   | Terminate running migration process      |

**Response**:

```json
{
  "code": 0,
  "data": {
    "status": "KILLED",
    "message": "Process terminated by user"
  }
}
```

---

## 5. Common Response Patterns

### Success (code = 0)

```json
{
  "code": 0,
  "message": "success",
  "data": "result"
}
```

### Business Error (code != 0, HTTP 200)

```json
{
  "code": 2001,
  "message": "Connection failed",
  "data": null
}
```

### System Error (HTTP 500)

```json
{
  "code": 9999,
  "message": "Internal server error",
  "data": null
}
```

### Resource Unavailable (HTTP 503)

```json
{
  "code": 5001,
  "message": "Thread pool full",
  "data": null
}
```

---

## 6. Timeout and Retry

- **Connection Timeout**: 5 seconds (recommended)
- **Read Timeout**: 30 seconds for standard operations, longer for large migrations
- **Retry Logic**:
    - 503 errors: respect Retry-After header
    - 2001 errors: check configuration before retrying
    - Other errors: retry only after fixing root cause

---

## 7. File Paths

- **Script Output**: `/opt/kdts/datax/job/{SCRIPT_NAME}`
- **Log Output**: `/opt/kdts/data/log/{LOG_FILE}`
- **SQL Output**: `/opt/kdts/data/sql/{SQL_FILE}`
- **DataX Home**: Configured in KDTS application.yml

---

## 8. Version Information

This API reference is based on KDTS Server v1.0.0 (kw-datax-utils latest).
For API changes, update this document accordingly.
