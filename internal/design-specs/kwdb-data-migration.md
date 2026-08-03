# KWDB Data Migration Skill Design Specification

## Overview

This document defines the design specification for the KWDB heterogeneous database migration skill.

**Status**: Phase 3-5 Completed  
**Version**: 2.1.0  
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
| Range | Category | Examples |
|-------|----------|----------|
| 1xxx | Parameter | 1001, 1002, 1003 |
| 2xxx | Connection | 2001, 2002 |
| 3xxx | Metadata | 3001, 3004 |
| 4xxx | DataX | 4001, 4002, 4003 |
| 5xxx | Resource | 5001, 5002 |
| 9xxx | System | 9999 |

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
    - Input: source, target, tables=[], data_config
    - Returns: Script name(s)
    ↓
[9] Execute Migration (api_client)
    - POST /datax/execute
    - Input: Script name(s)
    - Returns: Task ID(s), Log file path(s)
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

**Source Configuration** (engine is auto-detected, no need to specify):

```json
{
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

| Version | Date       | Changes                                                                                                                                 |
|---------|------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| 2.1.0   | 2026-08-03 | Simplified Engine types (RELATIONAL/TIMESERIES only); Fixed InfluxDB 1.x/2.x full migration support; Updated documentation and examples |
| 2.0.0   | 2025-07-30 | Complete rewrite: 5 modules, full workflow, AI agent integration                                                                        |
| 1.0.0   | 2025-06-01 | Initial version: manual migration guide                                                                                                 |

---

## Contact

For issues, questions, or contributions:

- Internal: KWDB team
- Repository: kaiwudb-agent-skills/skills/kwdb-data-migration