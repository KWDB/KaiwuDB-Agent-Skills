# KWDB Data Migration Skill Design Specification

## Overview

This document defines the design specification for the KWDB heterogeneous database migration skill.

**Status**: First Release
**Version**: 1.0.0  
**Last Updated**: 2026-08-03

---

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        AI Agent Interface                   │
│                    (SKILL.md / Prompt Handling)              │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      Script Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ data_source │  │ config_val  │  │ error_handler│          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
│         │                │                 │                │
│         └────────────────┼─────────────────┘                │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────┐           │
│  │           migration_task (Workflow)          │           │
│  └──────────────────────┬──────────────────────┘           │
│                         ▼                                    │
│  ┌─────────────────────────────────────────────┐           │
│  │              api_client (HTTP)               │           │
│  └──────────────────────┬──────────────────────┘           │
└─────────────────────────┼───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    KDTS REST API                             │
│  ┌─────────────────────────────────────────────┐           │
│  │  /kdts/api/v1/*                              │           │
│  │  - datasource/validate, databases, metadata   │           │
│  │  - metadata/preview, execute                 │           │
│  │  - datax/build, execute, status, control     │           │
│  └─────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component            | Responsibility                | Input                          | Output            |
|----------------------|-------------------------------|--------------------------------|-------------------|
| **data_source**      | Source/target config creation | Source type, connection params | Config dict       |
| **config_validator** | Parameter validation          | Config dict                    | Validation result |
| **error_handler**    | Error code lookup             | Error code                     | Message, hint     |
| **migration_task**   | Workflow orchestration        | Configs, options               | Workflow result   |
| **api_client**       | HTTP communication            | API endpoint, params           | API response      |

---

## Module Specifications

### 1. api_client.py

**Purpose**: Unified KDTS REST API client

**Endpoints Supported**:

- `GET /health` - Health check
- `POST /datasource/validate` - Test connection
- `POST /datasource/databases` - List databases
- `POST /datasource/metadata` - Read metadata
- `POST /metadata/preview` - Preview DDL
- `POST /metadata/execute` - Execute DDL
- `POST /datax/build` - Build migration script
- `POST /datax/execute` - Execute migration
- `GET /datax/status` - Query status
- `POST /datax/control` - Control (KILL/QUERY)

**Key Methods**:

```python
class KDTSClient:
    def test_connection(self, config: Dict, is_target: bool = False) -> Dict: ...
    def list_databases(self, config: Dict, is_target: bool = False) -> Dict: ...
    def read_metadata(self, source: Dict, options: Dict = None) -> Dict: ...
    def preview_ddl(self, target: Dict, source_db: Dict, metadata: Dict = None, is_time_series: bool = False) -> Dict: ...
    def execute_ddl(self, target: Dict, ddl_script: Dict, auto_ddl: bool = True) -> Dict: ...
    def build_migration(self, source: Dict, target: Dict, tables: List = None, data_config: Dict = None) -> Dict: ...
    def execute_migration(self, script_names: List[str]) -> Dict: ...
    def query_status(self, script_name: str) -> Dict: ...
    def control_task(self, script_name: str, action: str = "KILL") -> Dict: ...
```

**Response Format**:

```json
{
  "code": 0,
  "message": "success",
  "timestamp": 1719290000000,
  "data": {}
}
```

### 2. data_source.py

**Purpose**: Comprehensive data source configuration management

**Supported Source Types** (14):

| Type       | Default Port | Full Migration | Metadata | Notes                                                     |
|------------|--------------|----------------|----------|-----------------------------------------------------------|
| MYSQL      | 3306         | Yes            | Yes      | Relational database                                       |
| ORACLE     | 1521         | Yes            | Yes      | Relational database                                       |
| POSTGRESQL | 5432         | Yes            | Yes      | Relational database                                       |
| SQLSERVER  | 1433         | No             | Yes      | Relational database, metadata + data only                 |
| CLICKHOUSE | 9000         | Yes            | No       | Relational database, full migration without metadata      |
| KAIWUDB    | 26257        | No             | No       | Source or target, data migration only                     |
| TDENGINE3X | 6030         | Yes            | Yes      | Time series database                                      |
| TDENGINE2X | 6030         | No             | No       | Time series database, older version                       |
| INFLUXDB1X | 8086         | No             | Yes      | Time series database, metadata + data, two-step migration |
| INFLUXDB2X | 8086         | No             | Yes      | Time series database, metadata + data, two-step migration |
| OPENTSDB   | 4242         | No             | No       | Time series database                                      |
| MONGODB    | 27017        | No             | No       | Document database                                         |
| FTP        | 21           | No             | No       | File source                                               |
| HDFS       | 8020         | No             | No       | File source                                               |

**Note**: Engine field is required for all source configurations per KDTS API. For KAIWUDB as source, engine must be explicitly specified (RELATIONAL or TIMESERIES). Target (KaiwuDB) must specify engine: RELATIONAL or TIMESERIES.

**Key Classes**:

```python
class Engine(str, Enum):
    """
    KDTS engine types for target (KaiwuDB) configuration.
    
    Usage:
    - For target (KaiwuDB) configuration: Must specify either RELATIONAL or TIMESERIES
    - For source configuration: Engine is auto-detected from source type
    """
    RELATIONAL = "RELATIONAL"  # For KaiwuDB relational engine
    TIMESERIES = "TIMESERIES"  # For KaiwuDB time series engine

class SourceType(str, Enum):
    # 14 types as listed above
    ...

class DataSourceManager:
    def build_config(self, source_type: str, host: str, port: int, username: str, password: str, db_name: str = None, **kwargs) -> Dict: ...
    def build_target_config(self, engine: str, host: str, port: int, username: str, password: str, db_name: str = None) -> Dict: ...
    def test_connection(self, config: Dict) -> Dict: ...
    def get_capability(self, source_type: str) -> Dict: ...
    def is_full_migration_capable(self, source_type: str) -> bool: ...
    def is_metadata_capable(self, source_type: str) -> bool: ...
```

### 3. migration_task.py

**Purpose**: Migration workflow orchestration

**Supported Workflows**:

1. **Full Migration** - Schema + Data
2. **Schema-Only** - DDL only
3. **Data-Only** - Data to existing tables
4. **Table-Level** - Specific tables (for restricted sources)

**Workflow States**:

```
INIT → COLLECTING_PARAMS → VALIDATING → TESTING_CONNECTIONS 
    → READING_METADATA → PREVIEWING_DDL → WAITING_CONFIRMATION 
    → EXECUTING_DDL → BUILDING_SCRIPT → EXECUTING_MIGRATION 
    → MONITORING → COMPLETED | FAILED | KILLED
```

**Task States** (from KDTS API):

- SUBMITTED
- RUNNING
- SUCCEEDED
- FAILED
- KILLED

**Key Classes**:

```python
class MigrationWorkflowManager:
    def test_connections(self, source: Dict, target: Dict) -> Dict: ...
    def read_source_metadata(self, source: Dict, options: Dict = None) -> Dict: ...
    def preview_ddl(self, target: Dict, source_db: Dict, metadata: Dict = None, is_time_series: bool = False) -> Dict: ...
    def execute_ddl(self, target: Dict, ddl_script: Dict, auto_ddl: bool = True) -> Dict: ...
    def build_migration_script(self, source: Dict, target: Dict, tables: List = None, data_config: Dict = None) -> Dict: ...
    def execute_migration_script(self, script_names: List[str]) -> Dict: ...
    def execute_migration_batches(self, script_names: List[str], batch_size: int = 10, batch_timeout: int = 3600, poll_interval: int = 2, on_batch_progress: Callable = None) -> Dict: ...
    def wait_for_completion(self, script_name: str, timeout: int = 3600, poll_interval: int = 10, on_progress: Callable = None) -> Dict: ...
    def kill_task(self, script_name: str, confirm: bool = False) -> Dict: ...
    def run_full_migration(self, source: Dict, target: Dict, **kwargs) -> Dict: ...
    def run_schema_only_migration(self, source: Dict, target: Dict, **kwargs) -> Dict: ...
    def run_data_only_migration(self, source: Dict, target: Dict, tables: List, **kwargs) -> Dict: ...
    def run_batch_migration(self, source: Dict, target: Dict, table_batches: List, **kwargs) -> Dict: ...
```

**Important Constraint**: KDTS API only supports KILL and QUERY - NO pause/resume

### 4. config_validator.py

**Purpose**: Validate migration parameters before API calls

**Validation Rules**:

- Source type must be in 14 supported types
- Source capability must support requested operation
- Required fields must be present
- Target must be KAIWUDB
- Table mappings must have valid structure

**Key Methods**:

```python
class ConfigValidator:
    def validate_source(self, config) -> Tuple[bool, List[str]]: ...
    def validate_target(self, config) -> Tuple[bool, List[str]]: ...
    def validate_source_operation(self, source_type, operation) -> Tuple[bool, str]: ...
    def validate_table_mapping(self, mapping) -> Tuple[bool, List[str]]: ...
    def validate_full_migration_eligible(self, source_type) -> bool: ...
```

### 5. error_handler.py

**Purpose**: Map error codes to user-friendly messages

**Error Code Ranges**:

| Range | Category   | Examples         |
|-------|------------|------------------|
| 1xxx  | Parameter  | 1001, 1002, 1003 |
| 2xxx  | Connection | 2001, 2002       |
| 3xxx  | Metadata   | 3001, 3004       |
| 4xxx  | DataX      | 4001, 4002, 4003 |
| 5xxx  | Resource   | 5001, 5002       |
| 9xxx  | System     | 9999             |

**Key Methods**:

```python
class ErrorHandler:
    @staticmethod
    def get_error_message(code: int) -> str: ...
    @staticmethod
    def get_error_hint(code: int) -> str: ...
    @staticmethod
    def get_full_error_info(code: int) -> Dict: ...
```

---

## Data Flow

### Full Migration Data Flow

```
User Request
    ↓
[1] Parameter Collection
    - KDTS server URL
    - Source config (type, host, port, user, pass, db)
    - Target config (engine, host, port, user, pass, db)
    - Metadata options
    ↓
[2] Validation (config_validator)
    - Source type check
    - Capability check
    - Required fields
    ↓
[3] Connection Test (api_client)
    - Source: POST /datasource/validate
    - Target: POST /datasource/validate
    ↓
[4] Metadata Read (api_client)
    - POST /datasource/metadata
    - Returns: Database object (tables, columns, PKs, indexes)
    ↓
[5] DDL Preview (api_client)
    - POST /metadata/preview
    - Input: target config, source_db object, metadata
    - Returns: DDL script object
    ↓
[6] User Confirmation Gate
    - Show DDL to user
    - Warn about overwriting
    - Get explicit approval
    ↓
[7] DDL Execute (api_client)
    - POST /metadata/execute
    - Input: target config, DDL script
    - Returns: Log file path
    ↓
[8] Build Script (api_client)
    - POST /datax/build
    - Input: source, target, tables, data_config
    - Returns: Script name(s)
    - IMPORTANT: `tables=[]` (auto-discovery) is ONLY valid for RELATIONAL targets.
      TIMESERIES targets MUST provide explicit table mappings — empty tables fails
      with 4001 "No datax contents generated from config" (KDTS source explicitly 
      rejects whole-database migration into time-series engine)
    - PostgreSQL: auto-discovery filters tables by `schema == dbName` — `public` schema 
      tables are filtered out, use explicit table mappings
    ↓
[9] Execute Migration (api_client / workflow)
    - POST /datax/execute
    - Input: Script name(s)
    - Returns: Task ID(s), Log file path(s)
    - MANY scripts (one per table): use `execute_migration_batches(script_names,
      batch_size=10)` — submitting dozens of scripts in one request exceeds the client read timeout;
      a 4003 on submission means the request reached the server, still monitor
    ↓
[10] Monitor Progress (api_client)
    - GET /datax/status (polling)
    - Returns: Status, progress, error info
    - Loop until SUCCEEDED | FAILED | KILLED
    ↓
[11] Final Result
    - Status: SUCCEEDED / FAILED / KILLED
    - Duration, error details
    - User verification required
```

### Key Data Structures

**Source Configuration** (engine field is REQUIRED per KDTS API — the script layer
auto-fills it via `DataSourceManager.build_config()`, but the request body always
contains it: RELATIONAL for RDBMS, TIMESERIES for others):

```json
{
  "engine": "RELATIONAL",
  "type": "MYSQL",
  "host": "192.168.1.100",
  "port": 3306,
  "username": "root",
  "password": "secret",
  "dbName": "source_db"
}
```

**Target Configuration** (engine MUST be specified):

```json
{
  "engine": "RELATIONAL",
  "type": "KAIWUDB",
  "host": "127.0.0.1",
  "port": 26257,
  "username": "root",
  "password": "kwdb_secret",
  "dbName": "target_db",
  "isTarget": true
}
```

**Table Mapping** (for table-level migration):

```json
{
  "source": {
    "sourceType": "RDBMS",
    "table": "users",
    "column": "*",
    "where": "status = 'active'"
  },
  "target": {
    "sourceType": "KAIWUDB",
    "table": "users",
    "column": "*",
    "writeMode": "insert"
  }
}
```

**Metadata Options**:

```json
{
  "enable": true,
  "autoDdl": true,
  "primaryKey": true,
  "constraint": true,
  "comment": true,
  "index": false,
  "view": false
}
```

**DataX Configuration** (for data migration, passed to `build_migration` as `data_config`):

**IMPORTANT**: DataX configuration with `core` and `setting` fields is REQUIRED for successful data migration. These fields control the speed, resource usage, and error handling of the migration process.

**Default Configuration**:

```json
{
  "batchSize": 1000,
  "core": {
    "transport": {
      "channel": {
        "speed": {
          "byte": 1048576,
          "record": 1000
        }
      }
    }
  },
  "enable": true,
  "fetchSize": 1000,
  "setting": {
    "errorLimit": {
      "percentage": 0.02
    },
    "speed": {
      "channel": 4
    }
  }
}
```

**Configuration Structure**:

| Field                                 | Type    | Required | Description                                             |
|---------------------------------------|---------|----------|---------------------------------------------------------|
| `enable`                              | boolean | Yes      | Enable DataX execution (default: true)                  |
| `fetchSize`                           | integer | No       | Records fetched per request from source (default: 1000) |
| `batchSize`                           | integer | No       | Records per batch written to target (default: 1000)     |
| `core`                                | object  | Yes      | Core transport configuration                            |
| `core.transport.channel.speed.byte`   | integer | No       | Byte limit per channel (default: 1048576 = 1MB/s)       |
| `core.transport.channel.speed.record` | integer | No       | Record limit per channel (default: 1000 records/s)      |
| `setting`                             | object  | Yes      | Global setting configuration                            |
| `setting.errorLimit.percentage`       | float   | No       | Acceptable error percentage (default: 0.02 = 2%)        |
| `setting.speed`                       | object  | Yes      | Global speed configuration                              |

**Three Configuration Methods (Mutually Exclusive)**:

| Method                        | `setting.speed` Field | Description                        |
|-------------------------------|-----------------------|------------------------------------|
| Method 1: Fixed channel count | `channel` (integer)   | Simple, recommended for most cases |
| Method 2: By byte limit       | `byte` (integer)      | Precise bandwidth control          |
| Method 3: By record limit     | `record` (integer)    | Precise QPS control                |

**Method 1: Fixed Channel Count** (Default, Recommended)

```json
{
  "setting": {
    "speed": {
      "channel": 4
    }
  }
}
```

- Set `setting.speed.channel` to the desired number of parallel channels
- `core.transport.channel.speed.byte` and `core.transport.channel.speed.record` are optional per-channel limits

**Method 2: By Byte Limit**

```json
{
  "setting": {
    "speed": {
      "byte": 52428800
    }
  },
  "core": {
    "transport": {
      "channel": {
        "speed": {
          "byte": 10485760
        }
      }
    }
  }
}
```

- Set `setting.speed.byte` to the global byte limit (e.g., 52428800 = 50MB/s)
- `core.transport.channel.speed.byte` is REQUIRED (per-channel byte limit)
- Channel count auto-calculated: global byte / per-channel byte

**Method 3: By Record Limit**

```json
{
  "setting": {
    "speed": {
      "record": 40000
    }
  },
  "core": {
    "transport": {
      "channel": {
        "speed": {
          "record": 1000
        }
      }
    }
  }
}
```

- Set `setting.speed.record` to the global record limit (e.g., 40000 = 40000 records/s)
- `core.transport.channel.speed.record` is REQUIRED (per-channel record limit)
- Channel count auto-calculated: global record / per-channel record

**Configuration Constraints**:

1. **Method Exclusivity**: Methods 1 and 2/3 are mutually exclusive - cannot mix `setting.speed.channel` with `setting.speed.byte` or `setting.speed.record`
2. **Core Field Restriction**: Do NOT configure `channel` in `core.transport.channel.speed` (only in `setting.speed`)
3. **Mutually Exclusive Parameters**:
   - `where` and `querySql` cannot be used simultaneously
   - `splitPk` and `querySql` cannot be used simultaneously
   - `column` (string) and `columns` (array) cannot be used simultaneously
   - `setting.errorLimit.record` and `setting.errorLimit.percentage` are mutually exclusive

---

## Interaction Design

### Confirmation Gates

Three mandatory confirmation points:

1. **DDL Execution** - Before creating tables in target
2. **KILL Operation** - Before terminating running task
3. **Limited Capability** - When source can't do full migration

### Error Recovery Flow

```
Error Detected
    ↓
Show Error Details (code, message)
    ↓
Get Error Hint (from error_handler)
    ↓
Display Recovery Options
    ↓
User Selects Option
    ↓
Execute Recovery
    ↓
Verify Recovery Success
```

### State Tracking

Internal state machine tracks:

- Current step
- Completed steps
- Error history
- Timestamps

### Resume Support

Can resume after interruption:

- Store last known state
- Query current task status
- Show continuation options

---

## Constraints and Limitations

### API Constraints

1. **No pause/resume** - KDTS API only supports KILL and QUERY
2. **Stateless operations** - No session management, state at workflow level
3. **Task identification** - Via script_name from build endpoint
4. **No transaction** - Migration is not atomic
5. **No rollback** - Can't undo partial migration

### Capacity Limitations

1. **Max tables per migration** - Varies by KDTS config
2. **Max data size per task** - Limited by timeout and resources
3. **Type compatibility** - Some source types have limited compatibility
4. **Resource contention** - Multiple concurrent migrations may fail

### Source Type Constraints

1. **SQLSERVER** - No full migration, only table-level
2. **TDENGINE2X** - No metadata, no full migration, only table-level
3. **INFLUXDB1X/2X** - Full migration supported, but requires two steps (Schema + Data separately)
4. **HDFS/FTP** - No metadata, no full migration, only table-level
5. **MONGODB** - No metadata, no full migration, only table-level

### Engine Compatibility Rules (STRICT)

**IMPORTANT**: The following rules are ENFORCED by KDTS. Violating these will cause migration failure.

| Source Category | Source Types                                     | Allowed Target Engines   | Restriction                  |
|-----------------|--------------------------------------------------|--------------------------|------------------------------|
| **Time Series** | TDENGINE, INFLUXDB, OPENTSDB                     | **ONLY TIMESERIES**      | Cannot migrate to RELATIONAL |
| **Relational**  | MYSQL, ORACLE, POSTGRESQL, SQLSERVER, CLICKHOUSE | RELATIONAL or TIMESERIES | Can migrate to either        |
| **File/NoSQL**  | MONGODB, FTP, HDFS                               | TIMESERIES               | Time series oriented only    |

**Handling Invalid Combinations**:
- If user requests Time Series Source → RELATIONAL Target:
  1. Explain the restriction
  2. Suggest using native tools or custom scripts
  3. Show alternative: export from source → import to KaiwuDB

### Configuration Rules (Corrected)

**Note**: The following rules update the previous configuration constraints.

1. **`setting.speed` can use `channel`, `byte`, and `record` simultaneously** - They are NOT mutually exclusive
2. **`setting.errorLimit.record` and `setting.errorLimit.percentage` can be configured together** - KDTS will use the more restrictive limit
3. **Mutually exclusive parameters**:
   - `where` and `querySql` - Cannot use both simultaneously
   - `splitPk` and `querySql` - Not recommended (splitPk requires table structure)
   - `column` (string) and `columns` (array) - Choose one format

---

## KaiwuDB DDL Requirements

**IMPORTANT**: This section summarizes critical DDL rules for migration. For complete syntax, examples, and KDTS auto-mapping implementation details, refer to `references/ddl-syntax.md`.

### Time Series Table DDL Syntax

**Complete Syntax**:
```sql
CREATE TABLE <table_name> (
    <timestamp_col> TIMESTAMPTZ NOT NULL,
    <value_col_1> <data_type> [DEFAULT <value>],
    <value_col_2> <data_type> [DEFAULT <value>],
    ...
)
[TAGS | ATTRIBUTES] (
    <tag_col_1> <data_type> NOT NULL,
    <tag_col_2> <data_type>,
    ...
)
PRIMARY [TAGS | ATTRIBUTES] (<tag_col_1>, <tag_col_2>, ...)
[RETENTIONS <keep_duration>]
[ACTIVETIME <active_duration>]
[PARTITION INTERVAL <interval>]
[DICT ENCODING];
```

**Mandatory Rules (Violation Causes Migration Failure)**:
1. **First column MUST be** `TIMESTAMP` or `TIMESTAMPTZ` with `NOT NULL`
2. **At least 1 PRIMARY TAG required** (Error 3006 if missing)
3. **Max 4 PRIMARY TAGS** per table (Error 3004 if exceeded)
4. **Max 128 TAGS** per table
5. **Max 4096 columns** total (data + tags)
6. **PRIMARY TAGS must be** in TAGS list with `NOT NULL`
7. **PRIMARY TAGS cannot be** (from KDTS TypeMapping.FLOAT_TYPE_NAMES):
   - FLOAT, FLOAT4, FLOAT8, DOUBLE, REAL, BINARY_FLOAT, BINARY_DOUBLE, DECIMAL, NUMERIC (all classified as float types)
   - Variable-length types except VARCHAR (e.g., TEXT, NVARCHAR, NCHAR, CLOB, BLOB, BYTES, VARBYTES, JSON, ARRAY, MAP, INET, INTERVAL, UUID)
   - VARCHAR length: Default 64 bytes, Max 128 bytes
8. **TAGS cannot be**: TIMESTAMP, TIMESTAMPTZ, NVARCHAR, GEOMETRY, JSON
9. **Table/column/tag names**: Max 128 bytes

**Optional Table Parameters**:

| Parameter          | Default             | Description                                    |
|--------------------|---------------------|------------------------------------------------|
| RETENTIONS         | `0d` (never expire) | Data retention period                          |
| ACTIVETIME         | `1d`                | Time before compression (`0` = no compression) |
| PARTITION INTERVAL | System default      | Time partition interval                        |
| DICT ENCODING      | Disabled            | Dictionary encoding for compression            |

**Supported Time Units**: S/SECOND, M/MINUTE, H/HOUR, D/DAY, W/WEEK, MON/MONTH, Y/YEAR (Max 1000 years)

**Example**:
```sql
CREATE TABLE sensor_readings (
    ts TIMESTAMPTZ NOT NULL,
    temperature DOUBLE,
    humidity DOUBLE,
    pressure DOUBLE
)
TAGS (
    sensor_id BIGINT NOT NULL,
    location VARCHAR(100),
    device_type VARCHAR(50)
)
PRIMARY TAGS (sensor_id)
RETENTIONS '30d'
ACTIVETIME '7d';
```

### Relational Table DDL Syntax

**Syntax**:
```sql
CREATE TABLE <table_name> (
    <col_1> <data_type> [constraints],
    <col_2> <data_type> [constraints],
    ...
    [PRIMARY KEY (col_1, col_2, ...)],
    [FOREIGN KEY (col_x) REFERENCES other_table(col_y)],
    [UNIQUE (col_a, col_b, ...)]
);
```

**Supported Data Types**:

| Category  | Types                                             |
|-----------|---------------------------------------------------|
| Integer   | TINYINT, SMALLINT, INT, BIGINT, SERIAL, BIGSERIAL |
| Float     | REAL, DOUBLE                                      |
| Decimal   | DECIMAL(p,s), NUMERIC(p,s)                        |
| String    | CHAR(n), VARCHAR(n) [max 65535 bytes], TEXT       |
| Date/Time | DATE, TIME, TIMESTAMP, TIMESTAMPTZ, INTERVAL      |
| Boolean   | BOOLEAN                                           |
| Binary    | BINARY(n), VARBINARY(n), BLOB                     |
| JSON      | JSON, JSONB                                       |

**Example**:
```sql
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    order_no VARCHAR(50) UNIQUE NOT NULL,
    customer_id BIGINT NOT NULL,
    total_amount DECIMAL(15,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

### Error Codes for DDL Generation

| Error Code | Description                 | Migration Impact | Solution                                         |
|------------|-----------------------------|------------------|--------------------------------------------------|
| 3004       | Tag limit exceeded          | BLOCKED          | Reduce tags to max 128, primary tags to max 4    |
| 3005       | Name too long               | BLOCKED          | Shorten names to max 128 bytes                   |
| 3006       | No primary tag              | BLOCKED          | Add at least 1 PRIMARY TAG                       |

> **Note**: Error codes 3007/3008/3009 (previously documented) are NOT found in the KDTS
> source. Actual KDTS behavior is auto-conversion/demotion with warnings, not hard errors:
> - Invalid tag types (NVARCHAR, TEXT, etc.) → auto-converted to VARCHAR
> - Primary tags not eligible (FLOAT, NULL, over-length) → auto-demoted to ordinary tags
> - First-column timestamp → ensured by KDTS in DDL generation

### Tag Handling for Migration

#### Scenario 1: Relational Source → Time Series Target (MOST COMPLEX)

**Problem**: KDTS `preview_ddl` generates time-series DDL from tag marks on the source
Database columns (`"isTag"`/`"isPrimaryTag"`/`"isTs"`, declared explicitly via
`@JsonProperty` in `Column.java`), with the request field `"isTimeSeries": true`
(declared via `@JsonProperty("isTimeSeries")` in `PreviewDdlRequest.java`).
The SKILL must collect tag selection and apply the marks.

**Workflow**:
```
1. Read source metadata
   - Get all columns, their types, primary keys
   
2. Identify candidate columns
   - EXCLUDE: timestamp/datetime columns (reserved for time column)
   - EXCLUDE: very long text columns (not suitable for tags)
   - INCLUDE: ID columns, category columns, status columns (good tag candidates)
   
3. Present to user for selection:
   a. Select PRIMARY TAGS (1-4, REQUIRED)
      - Show suitable candidates with types
      - Warn about FLOAT/DOUBLE/DECIMAL/NUMERIC not allowed (classified as float by KDTS)
      - Warn about VARCHAR length limits (primary tag: max 128B, default 64B)
   
   b. Select additional TAGS (optional, max 128 total)
      - Show remaining suitable columns
   
   c. Auto-select time column
      - Choose first timestamp/datetime column as time column
   
4. Apply tag marks to the source Database columns (@JsonProperty names from KDTS
   `Column.java`; use the `mark_time_series_columns()` helper in api_client.py):
   - Time column: `"isTs": true` (KDTS renders first column `TIMESTAMPTZ NOT NULL`)
   - Primary tag: `"isTag": true` AND `"isPrimaryTag": true`
   - Ordinary tag: `"isTag": true`
   - Tables with NO `"isTag": true` column are SKIPPED by KDTS (no DDL emitted)
   
5. Check PRIMARY TAG columns for NULL values in source data (CRITICAL)
   - PRIMARY TAGS must be NOT NULL; NULL source values fail the write
   - Run: SELECT COUNT(*) FROM <table> WHERE <primary_tag_col> IS NULL;
   - If count > 0: fix source data / choose different primary tags / demote to ordinary tags
   
6. Generate DDL via KDTS: `preview_ddl(target_config, source_db, metadata, is_time_series=True)`
   (api_client sends `"isTimeSeries": true` per the @JsonProperty declaration)
   - KDTS generates `CREATE TS DATABASE` + tables with `TAGS (...) PRIMARY TAGS (...)`
   - KDTS auto-demotes: FLOAT/DOUBLE/DECIMAL/NUMERIC or nullable primary tags → ordinary tags
     (nullable demoted with warning); no eligible primary tag → Error 3006
   - KDTS auto-converts: primary tags of non-VARCHAR variable-length types → VARCHAR(128),
     VARCHAR > 128 truncated, VARCHAR without length → VARCHAR(64); forbidden ordinary
     tag types (TIMESTAMP, NVARCHAR, GEOMETRY) → VARCHAR
   - > 132 tag columns → Error 3004; tag name > 128 bytes → Error 3005
   
7. Validate the KDTS-generated DDL (show to user before execution)
   - First column is TIMESTAMPTZ NOT NULL
   - PRIMARY TAGS count 1-4, in TAGS list, with NOT NULL
   - Note tables skipped (no tag columns) and any auto-conversions/demotions
   
8. Execute DDL via the KDTS `execute_ddl()` API (NOT a direct JDBC/ODBC connection —
   the agent executes through KDTS) with the previewed DdlScript.
   Note: the `createDb` field is NOT executed — KDTS generates CREATE DATABASE /
   CREATE TS DATABASE itself from the target engine when `auto_ddl=true`.
   
9. Continue with DATA-ONLY migration (KDTS API)
   - `build_migration()` has NO `dataMode` parameter — data-only means explicit
     table mappings (`tables` REQUIRED, never empty) with target tables existing
```

**Validation Checklist for DDL Generation**:
- [ ] First column is TIMESTAMPTZ NOT NULL
- [ ] PRIMARY TAGS count: 1-4
- [ ] PRIMARY TAGS are in TAGS list
- [ ] PRIMARY TAGS have NOT NULL constraint
- [ ] PRIMARY TAGS types: No FLOAT/DOUBLE/DECIMAL/NUMERIC (float types), No TEXT/NVARCHAR (variable-length)
- [ ] TAGS types: No TIMESTAMP, TIMESTAMPTZ, NVARCHAR, GEOMETRY
- [ ] Total columns: ≤ 4096
- [ ] Total tags: ≤ 128
- [ ] Name lengths: ≤ 128 bytes

**Example (MySQL → KaiwuDB Time Series)**:
```sql
-- MySQL Source
CREATE TABLE sensor_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    device_id BIGINT NOT NULL,
    location VARCHAR(100),
    reading_time DATETIME NOT NULL,
    temperature DECIMAL(10,2),
    humidity DECIMAL(10,2)
);

-- Generated KaiwuDB DDL
CREATE TABLE sensor_data (
    reading_time TIMESTAMPTZ NOT NULL,
    id BIGINT,
    temperature DECIMAL(10,2),
    humidity DECIMAL(10,2)
)
TAGS (
    device_id BIGINT NOT NULL,
    location VARCHAR(100)
)
PRIMARY TAGS (device_id);
```

#### Scenario 2: Time Series Source → Time Series Target (AUTO-MAPPED)

**Supported Sources**: TDengine 2.x/3.x, InfluxDB 1.x/2.x, OpenTSDB

**KDTS Auto-Mapping Behavior** (from source code analysis):
```
Source Tags → Filter invalid (FLOAT/DECIMAL/NUMERIC/NULL) → 
              First 4 eligible → PRIMARY TAGS + Remaining → TAGS
Source Fields → Data columns
Source Timestamp → Time column (converted to TIMESTAMPTZ)
```

**Workflow**:
```
1. Call KDTS preview_ddl with time-series mode (api_client `is_time_series=True`,
   request JSON field `"isTimeSeries": true` per the @JsonProperty declaration)
   
2. KDTS auto-generates DDL based on source metadata
   - Filters invalid primary tags (FLOAT, DOUBLE, DECIMAL, NUMERIC, NULL)
   - Maps first 4 eligible source tags to PRIMARY TAGS
   - Maps remaining tags to TAGS (up to 128)
   - Maps source fields to data columns
   
3. Validate generated DDL
   - Check tag type compatibility (convert if needed)
   - Check PRIMARY TAGS count
   
4. Present to user for confirmation
   - Show tag mapping (source tag → target tag)
   - Show any type conversions made
   
5. Execute DDL via KDTS API
   
6. Continue with migration — TIMESERIES targets still need EXPLICIT table mappings
   (auto-discovery fails with 4001 for all source types)
```

**InfluxDB mapping requirements**:
- Source identifier field is `measurement` (NOT `table`); MONGODB uses `collectionName`.
  `build_table_mapping()` handles this automatically; FTP/HDFS are rejected (file sources)
- Source column list uses `sourceColumnName` — the time column is `_time` in InfluxDB
  queries, NOT the target name `ts` (`build_influxdb_mapping()` handles this)
- Data time range (beginDateTime/endDateTime) is REQUIRED with no defaults:
  null → migration fails; too-wide range (1970~2099) → reader memory overflow.
  Collect the actual data range from the user; splitIntervalS defaults to 86400

**Mapping helpers (scripts/api_client.py)**:
- `build_table_mapping(source_type, source_table, ..., where, pre_sql, post_sql,
  target_columns)` — source identifier per type (`table`/`measurement`/`collectionName`);
  `target_columns` REQUIRED when source columns contain SQL expressions
  (e.g. source `"...,1 as t1"` → target `"...,t1"`, else DataX cannot find the column)
- `build_influxdb_mapping(source_db, measurement, begin_datetime, end_datetime,
  split_interval_s=86400, read_timeout=0, connect_timeout=0)` — InfluxDB mappings
- `build_added_column(column_name, default_value, source_type, is_tag, is_primary_tag)`
  — new columns for sources lacking them (ALL source types)
- `mark_time_series_columns(source_db, table_name, time_column, primary_tags, tags)`
  — tag marks for time-series DDL generation

**Added-column type rules (ALL source types → KaiwuDB)**:
- Type derived from the DEFAULT VALUE: int → INT4 (INT8 for InfluxDB), str → VARCHAR,
  bool → BOOL (eligible for PRIMARY TAG)
- **float → FLOAT4/FLOAT8 — ordinary TAG ONLY, NEVER a primary tag** (float types are
  demoted by KDTS; 3006 if no eligible primary tag remains)
- sourceColumnType per source for exact mapping: MySQL/SQLServer/TDengine `INT`,
  Oracle `NUMBER(10,0)`, PostgreSQL `INTEGER`, ClickHouse `INT32`, InfluxDB `INTEGER`,
  KaiwuDB `INT4` (no KDTS mapping rules — verify generated DDL)
- SELECT-based sources use a SQL expression matching the default (e.g. `1 as t1`)

**Oracle source requirements**:
- Source dbName MUST be the owner (schema) name, usually UPPERCASE — KDTS reads
  `all_tab_comments WHERE owner = dbName`; lowercase returns zero tables
- Table/column names are UPPERCASE — mapping columns must match exactly
- New-column types need exact mappings (see table above); unmapped values such as
  `NUMBER(1,0)` fall back to `NUMBER` → FLOAT → demoted primary tag → 3006

**Auto-Mapping Rules**:

| Source Type | PRIMARY TAGS Source          | Additional TAGS Source | Data Columns Source |
|-------------|------------------------------|------------------------|---------------------|
| TDengine    | First 4 eligible TAG columns | Remaining TAG columns  | Regular columns     |
| InfluxDB    | First 4 eligible tags        | Remaining tags         | All fields          |
| OpenTSDB    | First 4 eligible tags        | Remaining tags         | Metric values       |

**Eligibility Criteria for Primary Tags**:
- NOT NULL / NOT NULLABLE
- NOT FLOAT/DOUBLE/DECIMAL/NUMERIC type (classified as float by KDTS)
- NOT over-length (VARCHAR > 128 bytes)

**Overflow Handling**:

| Scenario                           | Behavior                                       |
|------------------------------------|------------------------------------------------|
| 0 tags in source                   | ERROR: 3006 - NO_PRIMARY_TAG                   |
| All tags are FLOAT/DECIMAL/NUMERIC | ERROR: 3006 - NO_PRIMARY_TAG (all demoted)     |
| 1-4 eligible tags                  | All become PRIMARY TAGS                        |
| 5+ eligible tags                   | First 4 → PRIMARY TAGS, rest → Additional TAGS |
| Total tags > 132                   | ERROR: 3004 - TAG_LIMIT_EXCEEDED               |

#### Scenario 3: Time Series Source → Relational Target (NOT SUPPORTED)

**Restriction**: Time series sources (TDengine, InfluxDB, OpenTSDB) CANNOT migrate to RELATIONAL engine.

**Handling**:
1. Explain the restriction to user
2. Suggest alternatives:
   - Export from time series source (CSV, JSON)
   - Import to KaiwuDB relational using COPY or INSERT
   - Use custom ETL tools
3. Show supported path: Migrate to TIMESERIES engine instead

### Database Creation

**Time Series Database**:
```sql
CREATE TS DATABASE <db_name> [RETENTIONS <duration>] [PARTITION INTERVAL <interval>];
```

**Relational Database**:
```sql
CREATE DATABASE <db_name>;
```

**Detailed Reference**: See `references/ddl-syntax.md` (Complete syntax, examples, type compatibility tables, and KDTS auto-mapping implementation details)

---

## Future Extensions

### Planned Features

1. **Parallel Migration** - Migrate multiple tables concurrently
2. **Incremental Sync** - Sync only changed data
3. **Schema Validation** - Verify source and target schemas match
4. **Data Comparison** - Compare source and target data integrity
5. **Migration Templates** - Save and reuse migration configs

### Potential Enhancements

1. **Web Dashboard** - Visual migration monitoring
2. **CLI Tool** - Command-line interface for automation
3. **Scheduled Migration** - Time-based migration jobs
4. **Email Notifications** - Status updates via email
5. **Audit Logging** - Comprehensive operation logs

---

## Testing Strategy

### Test Layers

1. **Unit Tests** - Test individual methods
2. **Integration Tests** - Test component interactions
3. **End-to-End Tests** - Test complete workflows
4. **Edge Case Tests** - Test boundary conditions

### Test Coverage Goals

| Layer       | Coverage | Priority |
|-------------|----------|----------|
| Unit        | 80%      | High     |
| Integration | 70%      | High     |
| E2E         | 50%      | Medium   |
| Edge Cases  | 100%     | High     |

### Test Automation

- Automated test suite
- CI/CD integration
- Performance benchmarks
- Regression tests

---

## Security Considerations

### Authentication

1. KDTS API authentication (if enabled)
2. Database credentials handling
3. No password logging
4. Secure credential storage

### Data Protection

1. No sensitive data in logs
2. Mask passwords in error messages
3. Encrypted connections (HTTPS/TLS)
4. Network security validation

### Access Control

1. User permission verification
2. Database access validation
3. Operation authorization
4. Audit trail

---

## Documentation

### User Documentation

- SKILL.md (main skill file)
- references/api-reference.md (API docs)
- references/source-types.md (source types)
- references/config-templates.md (config examples)
- references/type-mapping.md (type mapping)
- references/error-codes.md (error codes)
- assets/migration-checklist.md (checklist)
- assets/prompt-examples.md (examples)

### Developer Documentation

- scripts/README.md (module docs)
- design specification (this document)
- test documentation (internal/tests/)

### API Documentation

- KDTS REST API specification
- Request/response examples
- Error code reference
- Rate limiting info

---

## Version History

| Version | Date       | Changes                                                                |
|---------|------------|------------------------------------------------------------------------|
| 1.0.0   | 2026-08-03 | **First Release**: Initial stable version with full migration support. |

---

## Contact

For issues, questions, or contributions:

- Internal: KWDB team
- Repository: kaiwudb-agent-skills/skills/kwdb-data-migration