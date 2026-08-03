---
name: kwdb-data-migration
description: |
  Automated heterogeneous database migration skill for KaiwuDB / KWDB via KDTS REST API.
  Use this skill whenever the user mentions:
  - heterogeneous migration, cross-database migration, or data migration to KaiwuDB / KWDB
  - KDTS, migration tool, or data transfer between different databases
  - Specific source databases: MySQL, Oracle, PostgreSQL, SQL Server, ClickHouse, TDengine, InfluxDB, OpenTSDB, MongoDB, FTP, HDFS
  - Migration operations: create migration task, configure data source, test connection, import data, sync schema, batch migration
  - Migration management: query task status, view migration progress, check logs, pause/resume/kill migration, export/import config
  - Data type mapping, table structure sync, DDL generation, schema validation
  Even if the user does not explicitly say "migration", trigger this skill when they ask to transfer or sync data between databases with different engines.
version: 2.1.0
---

# KWDB Data Migration Skill

## IMPORTANT: How to Use This Skill

**This is an AI Agent Skill**, NOT a library for manual coding. Here's how it works:

### Language Support

**ALWAYS respond in the same language the user uses.** This skill fully supports both Chinese and English users:
- If user writes in Chinese, respond in Chinese
- If user writes in English, respond in English
- When displaying technical terms (e.g., JDBC, DDL, TIMESERIES, RELATIONAL), keep them in their original form
- Example Chinese responses are available in `user-interaction-scenarios.zh.md`

### Correct Usage Pattern (Natural Language)

```
User: Help me migrate MySQL database to KaiwuDB

AI Agent:
1. Reads this SKILL.md to understand the migration workflow
2. Guides user step-by-step to collect necessary parameters:
   - KDTS server address (default: http://127.0.0.1:8989)
   - MySQL connection info (host, port, user, password, database)
   - KaiwuDB connection info (host, port, user, password, database, engine type)
   - Migration mode (full/schema-only/data-only)
3. Calls the Python scripts in `scripts/` as backend tools
4. Reports progress and results to user in natural language
```

### What AI Agent Does

The AI Agent acts as an **intelligent assistant** that:

- [STEP] Understands user's migration intent from natural language
- [COLLECT] Collects all necessary parameters through guided questions
- [EXECUTE] Executes migration operations by calling KDTS API
- [VALIDATE] Validates parameters and handles errors automatically
- [REPORT] Reports progress and results in user-friendly format
- [CONFIRM] Asks for confirmation at critical steps (DDL execution, task termination)

### What User Needs to Do

User only needs to:

- [DESCRIBE] Describe migration intent in plain language (e.g., "Migrate MySQL to KaiwuDB")
- [PROVIDE] Provide connection information when asked
- [CONFIRM] Confirm critical operations when prompted

### Example Conversation

```
User: Help me migrate MySQL sales database to KaiwuDB time series

AI Agent:
  [INFO] Migration intent recognized: MySQL -> KaiwuDB (TIMESERIES)
  
  Please provide the following information:
  1. KDTS server address (default: http://127.0.0.1:8989)
  2. MySQL connection info:
     - Host:
     - Port (default 3306):
     - Username:
     - Password:
  3. KaiwuDB connection info (engine: TIMESERIES):
     - Host (default 127.0.0.1):
     - Port (default 26257):
     - Username (default root):
     - Password:
  
  [WARNING] Security reminder: Please ensure you have backed up both source and target databases before migration!

User: KDTS at http://192.168.1.100:8989, MySQL: root/password abc at 192.168.1.50:3306, KaiwuDB at 127.0.0.1:26257

AI Agent:
  [OK] Parameters collected, starting migration process...
  
  Step 1/6: Testing database connections...
  [OK] MySQL connection successful
  [OK] KaiwuDB connection successful
  
  Step 2/6: Reading MySQL metadata...
  [INFO] Found 5 tables: orders, customers, products, categories, inventory
  
  Step 3/6: Previewing DDL (KaiwuDB time series tables)...
  [Shows DDL content]
  
  [WARNING] About to execute DDL to create tables. Continue? (yes/no)
```

### Python Scripts Purpose

The Python scripts in `scripts/` are **backend tools** for the AI Agent.
They provide low-level functions that the Agent calls during migration.
Users do NOT need to read or write these scripts directly.

### Python Dependencies

The scripts require minimal dependencies:

| Dependency | Purpose                        | Installation           |
|------------|--------------------------------|------------------------|
| `requests` | HTTP client for KDTS API calls | `pip install requests` |

All other modules use Python standard library only (`typing`, `json`, `re`, `logging`, etc.).

---

## Overview

This skill provides **automated heterogeneous database migration** to KaiwuDB / KWDB through KDTS REST API. Unlike the
old version that only provided manual GUI guidance, this skill directly calls the KDTS API to automate the entire
migration workflow.

### Two Migration Paths

1. **Primary Path: KDTS REST API** (for heterogeneous databases)
    - Supports 14 source types: MySQL, Oracle, PostgreSQL, SQL Server, ClickHouse, TDengine 2.x/3.x, InfluxDB 1.x/2.x,
      OpenTSDB, MongoDB, FTP, HDFS
    - Full automation: connection test, schema migration (DDL), data migration, progress tracking

2. **Secondary Path: KWDB Built-in EXPORT/IMPORT** (for KWDB-to-KWDB only)
    - Direct data copy between KWDB instances
    - Refer to `references/kwdb-kwdb-migration.md` for details

## KDTS Server Configuration

Before any migration operations, determine the KDTS Server connection.
Configuration uses multi-layer priority (highest to lowest):

### Configuration Methods

**1. Environment Variables (Recommended for CI/CD)**

```bash
# Option A: Full URL
export KDTS_BASE_URL="http://your-kdts-server.com:8989"

# Option B: Separate host and port
export KDTS_HOST="your-kdts-server.com"
export KDTS_PORT="8989"

# Optional additional settings
export KDTS_API_PREFIX="/kdts/api/v1"  # Default
export KDTS_TIMEOUT="30"                # Default seconds
export KDTS_CONNECT_TIMEOUT="5"         # Default seconds
```

**2. Explicit Parameter**

```python
client = KDTSClient(base_url="http://your-kdts-server.com:8989")
```

**3. Configuration File (kdts_config.json)**
Create `kdts_config.json` in your project directory:

```json
{
  "base_url": "http://your-kdts-server.com:8989",
  "api_prefix": "/kdts/api/v1",
  "timeout": 30,
  "connect_timeout": 5
}
```

**4. Default (Fallback)**

```
Default: http://127.0.0.1:8989
API Prefix: /kdts/api/v1
```

### Configuration Detection

Use `get_environment_info()` to check current configuration:

```python
from scripts import get_environment_info
info = get_environment_info()
print(f"Config source: {info['config_source']}")
print(f"Current config: {info['current_config']}")
```

### Mandatory Step

Ask the user for KDTS server address if:

- No environment variables are set
- No config file exists
- Default is not appropriate for their environment

Example prompt:
> "What is your KDTS server address? (Default: http://127.0.0.1:8989)"

---

## Script Reference

All migration operations use Python scripts in `scripts/`. Read `scripts/README.md` for API details.

### Initialization

```python
from scripts import (
    KDTSClient, DataSourceManager, MigrationWorkflowManager,
    get_environment_info
)

# Check current configuration
print(get_environment_info())

# Initialize client (uses multi-layer config: env > param > file > default)
client = KDTSClient()  # Reads from env or defaults to http://127.0.0.1:8989

# Or specify explicitly
client = KDTSClient(base_url="http://your-kdts-server:8989")

# Initialize managers
ds_manager = DataSourceManager(api_client=client)
workflow = MigrationWorkflowManager(api_client=client)
```

### Config Methods

| Intent                 | Function                                   | Signature                    |
|------------------------|--------------------------------------------|------------------------------|
| Get config info        | `get_environment_info()`                   | No params, returns Dict      |
| Resolve base URL       | `resolve_base_url()`                       | `(explicit_url: str = None)` |
| Create config template | `KDTSConfig.create_config_file_template()` | `(path: str)`                |

### API Client Methods

| Intent            | Method                           | Signature                                                                                     |
|-------------------|----------------------------------|-----------------------------------------------------------------------------------------------|
| Test connection   | `KDTSClient.test_connection()`   | `(config: Dict, is_target: bool = False)`                                                     |
| List databases    | `KDTSClient.list_databases()`    | `(config: Dict, is_target: bool = False)`                                                     |
| Read metadata     | `KDTSClient.read_metadata()`     | `(source_config: Dict, metadata_options: Dict = None)`                                        |
| Preview DDL       | `KDTSClient.preview_ddl()`       | `(target_config: Dict, source_db: Dict, metadata: Dict = None, is_time_series: bool = False)` |
| Execute DDL       | `KDTSClient.execute_ddl()`       | `(target_config: Dict, ddl_script: Dict, auto_ddl: bool = True)`                              |
| Build migration   | `KDTSClient.build_migration()`   | `(source: Dict, target: Dict, tables: List = None, data_config: Dict = None)`                 |
| Execute migration | `KDTSClient.execute_migration()` | `(script_names: List[str])`                                                                   |
| Query status      | `KDTSClient.query_status()`      | `(script_name: str)`                                                                          |
| Kill task         | `KDTSClient.control_task()`      | `(script_name: str, action: str = "KILL")`                                                    |

### Data Source Methods

| Intent                | Method                                    | Signature                                                     |
|-----------------------|-------------------------------------------|---------------------------------------------------------------|
| Build source config   | `DataSourceManager.build_config()`        | `(source_type, host, port, username, password, db_name, ...)` |
| Build target config   | `DataSourceManager.build_target_config()` | `(engine, host, port, username, password, db_name)`           |
| Get source capability | `DataSourceManager.get_capability()`      | `(source_type: str)`                                          |
| Test connection       | `DataSourceManager.test_connection()`     | `(config: Dict)`                                              |

### Workflow Methods

| Intent          | Method                                                 | Signature                                            |
|-----------------|--------------------------------------------------------|------------------------------------------------------|
| Full migration  | `MigrationWorkflowManager.run_full_migration()`        | `(source_config, target_config, ...)`                |
| Schema-only     | `MigrationWorkflowManager.run_schema_only_migration()` | `(source_config, target_config, ...)`                |
| Data-only       | `MigrationWorkflowManager.run_data_only_migration()`   | `(source_config, target_config, tables, ...)`        |
| Batch migration | `MigrationWorkflowManager.run_batch_migration()`       | `(source_config, target_config, table_batches, ...)` |
| Kill task       | `MigrationWorkflowManager.kill_task()`                 | `(script_name, confirm=False)`                       |

### Utility Methods

| Intent              | Module                        | Function                                         |
|---------------------|-------------------------------|--------------------------------------------------|
| Validate config     | `scripts/config_validator.py` | `ConfigValidator.validate_source_config(config)` |
| Generate error hint | `scripts/error_handler.py`    | `ErrorHandler.get_error_hint(code)`              |

---

## Mandatory Rules

### 1. Never Guess Parameters

All migration parameters **must** be collected from the user explicitly:

- KDTS server address (default: http://localhost:8080)
- Source database: engine, type, host, port, username, password, database name
- Target KWDB: engine, host, port, username, password, database name
- Migration scope: full database or specific tables
- Migration mode: schema-only, data-only, or full

### 2. Always Validate Source Type

Before any operation, **must** call `ConfigValidator.validate_source_config()` from `scripts/config_validator.py`:

- Check if source type is in supported list (14 types)
- Check if source type supports the requested operation (metadata, full migration, etc.)
- Refer to `references/source-types.md` for full capability matrix

### 3. Always Test Connection First

Before reading metadata or building migration scripts:

```python
from scripts.api_client import KDTSClient
client = KDTSClient(base_url)

# Test source connection
result = client.test_connection(source_config, is_target=False)
if result['code'] != 0:
    raise Exception("Source connection failed")

# Test target connection  
result = client.test_connection(target_config, is_target=True)
if result['code'] != 0:
    raise Exception("Target connection failed")
```

If connection fails, **stop immediately** and show error hint from `error_handler.py`.

### 4. Mandatory Backup Reminder

Before any migration starts:
> **Reminder:** Please ensure you have backed up both source and target databases before proceeding with migration. KDTS
> migration is non-transactional for data operations and cannot be automatically rolled back.

### 5. Never Kill Running Tasks Without Confirmation

**CRITICAL:** Never execute `control_task(action="KILL")` without explicit user confirmation:

1. Show current task status and progress
2. Warn: "Killing a running migration may leave data in inconsistent state"
3. Ask: "Are you absolutely sure you want to kill this task? (type 'YES' to confirm)"
4. Only proceed after explicit confirmation

### 6. Migration Task Naming Convention

When building scripts, inform user of the generated script names:

```
Script naming: <SOURCE>2<TARGET>_<timestamp>.json
Example: MYSQL2KAIWUDB_1719290000000.json
```

---

## Supported Data Sources

Refer to `references/source-types.md` for complete capability matrix.

| Category    | Source Type  | Full Migration  | Metadata | Notes                                    |
|-------------|--------------|-----------------|----------|------------------------------------------|
| Relational  | MySQL        | Yes             | Yes      |                                          |
| Relational  | Oracle       | Yes             | Yes      |                                          |
| Relational  | PostgreSQL   | Yes             | Yes      |                                          |
| Relational  | SQL Server   | No              | Yes      | Metadata + Data, no full migration       |
| Relational  | ClickHouse   | Yes             | No       | Full migration, no metadata              |
| Relational  | KaiwuDB      | No              | No       | Data migration only (as source)          |
| Time Series | TDengine 3.x | Yes             | Yes      |                                          |
| Time Series | TDengine 2.x | No              | No       | Data migration only                      |
| Time Series | InfluxDB 1.x | No              | Yes      | Metadata + Data, no full migration       |
| Time Series | InfluxDB 2.x | No              | Yes      | Metadata + Data, no full migration       |
| Time Series | OpenTSDB     | No              | No       | Data migration only                      |
| NoSQL       | MongoDB      | No              | No       | Data migration only                      |
| File        | FTP/SFTP     | No              | No       | Data migration only                      |
| File        | HDFS         | No              | No       | Data migration only                      |

> **Note:**
> - Target is **ALWAYS** KaiwuDB with engine specified as RELATIONAL or TIMESERIES
> - Source **MUST** also specify engine field (RELATIONAL for RDBMS, TIMESERIES for others)
> - For SQL Server, InfluxDB 1.x/2.x: Use two-step migration (Schema first, then Data)

### KaiwuDB Time-Series Table Constraints

When migrating to KaiwuDB with TIMESERIES engine, the following constraints apply:

| Constraint                       | Limit     | Error Code                |
|----------------------------------|-----------|---------------------------|
| Maximum columns per table        | 128       | 3004 (TAG_LIMIT_EXCEEDED) |
| Maximum primary tags             | 4         | 3004 (TAG_LIMIT_EXCEEDED) |
| Maximum tag/column name length   | 128 bytes | 3005 (TAG_NAME_TOO_LONG)  |
| Must have at least 1 primary tag | 1         | 3006 (NO_PRIMARY_TAG)     |

**Recommendation**: When source has many columns, consider splitting into multiple tables or migrations.

---

## API Endpoint Mapping

All endpoints under `{base_url}/kdts/api/v1`:

| Method | Path                    | Purpose                         | Script Function            |
|--------|-------------------------|---------------------------------|----------------------------|
| GET    | `/health`               | Health check                    | `test_connection()`        |
| POST   | `/datasource/validate`  | Test source/target connectivity | `test_connection()`        |
| POST   | `/datasource/databases` | List databases on source        | `list_databases()`         |
| POST   | `/datasource/metadata`  | Read source metadata            | `read_metadata()`          |
| POST   | `/metadata/preview`     | Preview DDL for target          | `preview_ddl()`            |
| POST   | `/metadata/execute`     | Execute DDL on target           | `execute_ddl()`            |
| POST   | `/datax/build`          | Build DataX migration script    | `build_migration_script()` |
| POST   | `/datax/execute`        | Execute migration scripts       | `execute_migration()`      |
| GET    | `/datax/status`         | Query migration status          | `query_task_status()`      |
| POST   | `/datax/control`        | Kill or query task              | `control_task()`           |

---

## Migration Workflows

### Workflow 1: Full Migration (Schema + Data)

**When to use:** Source supports full migration:

- MYSQL, ORACLE, POSTGRESQL, CLICKHOUSE, TDENGINE3X

**Note:** KAIWUDB, SQLSERVER, INFLUXDB, and other time-series/NoSQL sources do NOT support full migration. Use Workflow 2 or 3 instead.

```
1. Collect parameters (interactive)
   +-- KDTS base URL
   +-- Source config (engine, type, host, port, user, password, db)
   |   Note: engine MUST be specified (RELATIONAL for RDBMS, TIMESERIES for others)
   +-- Target config (engine: RELATIONAL or TIMESERIES, host, port, user, password, db)
   |   Note: engine MUST be specified for KaiwuDB target
   +-- Metadata options (PK, constraint, comment, index, view)

2. Validate source type → ConfigValidator.validate_source_config()

3. Test connections → test_connection() × 2

4. Check target DB exists → list_databases()
   If not exists, remind user to create or use DDL

5. Read source metadata → read_metadata()
   Show table count, columns per table, PK/constraint info

6. Preview DDL → preview_ddl()
   Show generated DDL for each table
   Ask user to confirm before execution

7. Execute DDL → execute_ddl()
   Report success with SQL file path

8. Build migration script → build_migration_script()
   Show generated script name(s)
   For full migration, tables can be empty (auto-discover)

9. Execute migration → execute_migration()
   Return log file paths

10. Monitor progress → query_task_status() (polling every 2s)
    Show status: SUBMITTED → RUNNING → SUCCEEDED/FAILED
    Report final status

11. Verify (manual step for user)
    Remind to compare row counts between source and target
```

### Workflow 2: Schema-Only Migration

**When to use:** Only need table structure, no data transfer

```
Steps 1-7 from Workflow 1, then STOP.
Report DDL execution result.
```

### Workflow 3: Data-Only Migration

**When to use:**

- Target tables already exist, only need data sync
- For InfluxDB 1.x/2.x: Use this after Schema migration (Workflow 1 steps 1-7)

```
1. Collect parameters (interactive)
2. Validate source type
3. Test connections × 2
4. Build migration script → tables MUST be provided (table-level mapping)
5. Execute migration
6. Monitor progress
```

### Workflow 4: Table-Level Migration (Restricted Sources)

**When to use:** Source does NOT support full migration (SQL Server, TDengine 2.x, OpenTSDB, MongoDB, FTP, HDFS)

```
1. Collect ALL table mappings explicitly:
   Source: table name, columns
   Target: table name, columns, write mode (insert/upsert)

2. Build migration script with explicit tables field

3. Execute and monitor
```

---

## Source Type Configuration Templates

### Source Configuration Examples

**Important**: For ALL source configurations, the `engine` field is **REQUIRED** per KDTS API:
- Use `RELATIONAL` for: MySQL, Oracle, PostgreSQL, SQL Server, ClickHouse
- Use `TIMESERIES` for: KAIWUDB, TDengine 2.x/3.x, InfluxDB 1.x/2.x, OpenTSDB, MongoDB, FTP, HDFS

#### Relational Source (MySQL Example)

```json
{
  "engine": "RELATIONAL",
  "type": "MYSQL",
  "host": "127.0.0.1",
  "port": 3306,
  "username": "root",
  "password": "********",
  "dbName": "source_db"
}
```

#### Time Series Source (InfluxDB Example)

```json
{
  "engine": "TIMESERIES",
  "type": "INFLUXDB1X",
  "host": "127.0.0.1",
  "port": 8086,
  "username": "admin",
  "password": "********",
  "dbName": "source_db"
}
```

### Target Configuration Examples

**Note:** For target (KaiwuDB) configuration, `engine` field is REQUIRED to specify the KaiwuDB storage engine:

- Use `RELATIONAL` for relational database
- Use `TIMESERIES` for time-series database

#### KaiwuDB Target - Relational Engine

```json
{
  "type": "KAIWUDB",
  "engine": "RELATIONAL",
  "host": "127.0.0.1",
  "port": 26257,
  "username": "root",
  "password": "********",
  "dbName": "target_db",
  "isTarget": true
}
```

#### KaiwuDB Target - Time Series Engine

```json
{
  "type": "KAIWUDB",
  "engine": "TIMESERIES",
  "host": "127.0.0.1",
  "port": 26257,
  "username": "root",
  "password": "********",
  "dbName": "target_ts_db",
  "isTarget": true
}
```

### Source Type → sourceType Mapping

When building migration scripts, use the appropriate `sourceType`:

| KDTS Source Type                                 | sourceType value |
|--------------------------------------------------|------------------|
| MYSQL, ORACLE, POSTGRESQL, SQLSERVER, CLICKHOUSE | `RDBMS`          |
| KAIWUDB                                          | `KAIWUDB`        |
| TDENGINE2X, TDENGINE3X                           | `TDENGINE`       |
| INFLUXDB1X, INFLUXDB2X                           | `INFLUXDB`       |
| MONGODB                                          | `MONGODB`        |
| OPENTSDB                                         | `OPENTSDB`       |
| FTP                                              | `FTP`            |
| HDFS                                             | `HDFS`           |

---

## Error Handling

Refer to `references/error-codes.md` for complete error code reference.

When API returns error:

1. Extract `code` and `message` from response
2. Call `get_error_hint(code)` to get user-friendly explanation and fix suggestion
3. Show both original error and hint to user
4. If it's a connection/validation error, **stop and ask for corrected parameters**
5. If it's a data migration error, show partial progress and ask whether to retry or skip

### Common Error Scenarios

| Code | Meaning                 | Action                                       |
|------|-------------------------|----------------------------------------------|
| 1001 | Invalid parameters      | Show which field is missing/wrong            |
| 1002 | Unsupported source type | Show supported types, ask user to choose     |
| 2001 | Connection failed       | Check host/port/credentials, test network    |
| 3004 | Tag limit exceeded      | Reduce tag columns or split migration        |
| 4001 | Build failed            | Check table mapping, ensure both sides match |
| 4002 | Launch failed           | Check Python 3 availability on KDTS server   |
| 4003 | Timeout                 | Increase timeout or reduce data volume       |
| 5001 | Thread pool full        | Wait and retry (HTTP 503, Retry-After: 10)   |
| 5002 | Python not found        | Install Python 3 on KDTS server              |

---

## Interactive Parameter Collection

When user intent is identified but parameters are missing, collect them step by step:

### Step 1: KDTS Server

```
What is the KDTS server address?
(default: http://localhost:8080)
```

### Step 2: Migration Type

```
Select migration type:
1. Full Migration (schema + data)
2. Schema-Only Migration (DDL only)
3. Data-Only Migration (tables must exist)
```

### Step 3: Source Configuration

```
Source database type?
[MySQL, Oracle, PostgreSQL, SQL Server, ClickHouse, TDengine 2.x/3.x, 
 InfluxDB 1.x/2.x, OpenTSDB, MongoDB, FTP, HDFS, KaiwuDB]

Source connection:
Host: 
Port: (show default based on type, e.g., MySQL=3306)
Username: 
Password: 
Database:
```

### Step 4: Target Configuration

```
Target KaiwuDB connection:
Engine: [RELATIONAL, TIMESERIES]
Host: (default: 127.0.0.1)
Port: (default: 26257)
Username: (default: root)
Password: 
Database:
```

### Step 5: Migration Scope

```
Migration scope:
1. Full database (all tables)
2. Specific tables only

If specific tables:
- Table name(s):
- Columns (optional):
```

### Step 6: Data Configuration (Optional)

```
Data migration settings:
Fetch size (rows per fetch, default 1000): 
Batch size (rows per write, default 1000):
Error tolerance (% allowed, default 0.02):
Concurrency (channels, default 1):
```

---

## Confirmation Gates (Critical Safety Points)

### Gate 1: DDL Execution Confirmation

**Before executing DDL**, you MUST:

1. Show the previewed DDL to the user
2. Explain what will be created (databases, tables, indexes, constraints)
3. Warn about potential issues:
    - Existing tables will be overwritten (if `auto_ddl=true`)
    - Data loss if target already has data
4. Ask for explicit confirmation:
   ```
   [WARNING] DDL Execution Preview
   ===============================
   Database: [db_name]
   Tables to create: [count]
   - table1: [columns, PK, indexes]
   - table2: ...
   
   [WARNING] This will create tables in the target KaiwuDB.
   [WARNING] Existing tables with the same name will be overwritten.
   
   Do you want to proceed? (yes/no)
   ```
5. If user says NO, save the DDL preview and offer to show it later

### Gate 2: KILL Operation Confirmation

**Before killing a running migration**, you MUST:

1. Show current task status and progress
2. Explain the consequence:
   ```
   [WARNING] Task Termination Warning
   ===============================
   Task: [script_name]
   Status: [RUNNING/SUBMITTED]
   Progress: [X%]
   Elapsed: [minutes]
   
   [WARNING] Killing this task will:
   - Stop data transfer immediately
   - Leave partial data in target
   - Require manual cleanup or re-migration
   - Cannot be resumed
   
   Are you absolutely sure you want to kill this task? 
   (Type "YES" to confirm)
   ```
3. Only proceed if user explicitly types "YES"

### Gate 3: Source with Limited Capability

**When source doesn't support full migration**, you MUST:

1. Explain the limitation clearly:
   ```
   [WARNING] Source Type Limitation
   ===============================
   Source type: SQLSERVER
   
   This source does NOT support:
   - Automatic schema discovery
   - Full database migration
   
   Supported operations:
   - Table-level migration (you must specify each table)
   
   Please provide table mappings:
   ```
2. Help user build explicit table mappings

---

## Error Recovery Flow

### Scenario 1: Connection Failure

**Problem**: `test_connection()` returns error

**Recovery Steps**:

1. Show error details: host, port, error code, message
2. Suggest common fixes:
    - Check if database is running
    - Verify host/port accessibility
    - Confirm credentials
    - Check firewall/network
3. Ask user to verify and retry
4. If user provides new values, update config and retry

### Scenario 2: Partial Migration Failure

**Problem**: Migration fails after some data transferred

**Recovery Steps**:

1. Check which tables failed vs succeeded
2. Show summary:
   ```
   Migration Summary
   =================
   Total tables: 10
   Succeeded: 7
   Failed: 3
   
   Failed tables:
   - table_a: [error message]
   - table_b: [error message]
   - table_c: [error message]
   ```
3. Offer options:
    - **Retry failed tables only** (recommended)
    - **Restart entire migration** (cleanup first)
    - **Skip and continue** (accept partial result)
4. If retrying failed tables:
    - Use table-level migration for specific tables
    - Consider increasing error tolerance

### Scenario 3: Metadata Reading Failure

**Problem**: `read_metadata()` fails or returns empty

**Recovery Steps**:

1. Check if source is accessible (retry connection test)
2. Verify database exists and user has permissions
3. For sources without metadata support (ClickHouse, TDengine 2.x, etc.):
    - Inform user: "This source type doesn't support metadata reading"
    - Offer to skip to DDL phase or use table-level migration

### Scenario 4: DDL Execution Failure

**Problem**: `execute_ddl()` fails

**Recovery Steps**:

1. Show the exact DDL that failed
2. Highlight problematic SQL
3. Suggest fixes:
    - Syntax error: Show alternative syntax
    - Type mismatch: Show compatible types
    - Already exists: Suggest `auto_ddl=true` or manual DDL
4. Offer to:
    - Show corrected DDL
    - Skip DDL (if tables exist)
    - Retry with different options

---

## Edge Case Handling

### Edge Case 1: Large Dataset Migration (1M+ Rows)

**Symptoms**: Migration takes too long, times out, or errors

**Handling**:

1. Recommend batch migration:
   ```python
   # Split into batches of 100K rows
   batch_config = {"splitPk": "id", "channel": 10}
   ```
2. Monitor progress frequently (every 10 seconds)
3. Warn user about estimated time
4. Offer to run in background mode (poll only, no waiting)

### Edge Case 2: Concurrent Migration Tasks

**Symptoms**: Multiple migrations running simultaneously

**Handling**:

1. Query all running tasks:
   ```python
   # Check if other tasks are running
   running_tasks = client.query_all_running_tasks()
   ```
2. If other tasks exist:
    - Show their names, progress, estimated completion
    - Warn about resource contention
    - Ask user to wait or proceed anyway

### Edge Case 3: Schema Drift (Source Changed During Migration)

**Symptoms**: Source table structure changed after DDL but before data migration

**Handling**:

1. Detect schema mismatch when data errors occur
2. Show error: "Schema changed during migration"
3. Offer to:
    - Re-run metadata + DDL (will recreate target tables)
    - Continue with partial data (accept data loss for changed columns)
    - Cancel migration

### Edge Case 4: Timeout During Long Migration

**Symptoms**: `wait_for_completion()` times out

**Handling**:

1. Return current task status
2. Show progress achieved
3. Offer options:
    - **Continue waiting** (extend timeout)
    - **Poll only** (check status without waiting)
    - **Kill and restart** (if stuck)
4. Always show current progress before deciding

### Edge Case 5: Unsupported Data Types

**Symptoms**: Column type not supported in KaiwuDB

**Handling**:

1. Show problematic columns:
   ```
   [WARNING] Unsupported Type Detected
   ===============================
   Table: users
   Column: avatar
   Source type: BLOB
   
   KaiwuDB compatible alternatives:
   - BINARY (max 64KB)
   - VARBINARY (max 64KB)
   - LOB (for large objects)
   
   Please select target type:
   ```
2. Map to closest compatible type
3. Note: May need to split or convert large objects

---

## Workflow State Management

### State Tracking

Track migration progress with these states:

```
INIT → COLLECTING_PARAMS → VALIDATING → TESTING_CONNECTIONS 
    → READING_METADATA → PREVIEWING_DDL → WAITING_CONFIRMATION 
    → EXECUTING_DDL → BUILDING_SCRIPT → EXECUTING_MIGRATION 
    → MONITORING → COMPLETED | FAILED | KILLED
```

### Resume After Interruption

If conversation is interrupted:

1. When user returns, ask:
   ```
   Welcome back! I found your previous migration session:
   
   Source: MySQL @ 192.168.1.100:3306/users_db
   Target: KaiwuDB @ 127.0.0.1:26257
   Progress: DDL executed, migration in progress (60%)
   
   Would you like to:
   1. Continue monitoring current migration
   2. Check current status
   3. Start a new migration
   ```
2. If continuing, query task status immediately
3. Show latest progress

---

## Cross-Reference

- API Reference: `references/api-reference.md`
- Source Types: `references/source-types.md`
- Error Codes: `references/error-codes.md`
- Type Mapping: `references/type-mapping.md`
- Config Templates: `references/config-templates.md`
- Migration Checklist: `assets/migration-checklist.md`
- Prompt Examples: `assets/prompt-examples.md`
- Script README: `scripts/README.md`
- KDTS Docs: `{kw-datax-utils}/docs/api.md`

---

## Notes

- KDTS Server is the backend service; this skill is the AI agent interface
- All operations are stateless — the agent does NOT maintain session
- Task tracking is via `script_name` returned by build endpoint
- Migration scripts are stored on KDTS server at `/opt/kdts/datax/job/`
- Log files are at `/opt/kdts/data/log/`
- For large migrations (>1M rows), recommend monitoring with `query_task_status()` until completion
- **DO NOT** assume migration succeeded — always verify with row count comparison

## Support

If migration fails:

1. Check error codes in `references/error-codes.md`
2. Review KDTS server logs
3. Test connection again
4. Try with smaller batch size or fewer tables
