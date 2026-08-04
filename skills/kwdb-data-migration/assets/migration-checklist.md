# KDTS Heterogeneous Database Migration Checklist

Complete migration workflow checklist to ensure every step is executed correctly.

## Language Versions

- **English Version**: This file (`migration-checklist.md`)
- **Chinese Version**: [migration-checklist.zh.md](./migration-checklist.zh.md)

The AI Agent will respond in the same language the user uses.

---

## Phase 1: Pre-Migration Preparation

### 1.1 Environment Check

- [ ] KDTS Server is running and accessible
    - Access `http://{kdts_host}:{port}/kdts/api/v1/health` to confirm status
    - Default port: 8989
- [ ] Source database is network-accessible from KDTS Server
    - Test connectivity: `ping {source_host}` or `telnet {source_host} {port}`
- [ ] Target KaiwuDB is installed and running
    - Test connection: `mysql -h {kwdb_host} -P {port} -u root -p`
- [ ] Python 3 is installed (on KDTS Server)
    - Run: `python3 --version`

### 1.2 Account Permissions

- [ ] Source database account has sufficient permissions
    - MySQL: SELECT on target database
    - Oracle: SELECT_CATALOG_ROLE or DBA
    - PostgreSQL: USAGE on schema
    - Other databases: refer to their documentation
- [ ] Target KaiwuDB account has sufficient permissions
    - CREATE, DROP, ALTER (for DDL)
    - INSERT, SELECT (for data migration)
    - Target database exists or auto-creation is allowed
- [ ] Network firewall/security group has required ports open

### 1.3 Backup Reminder

- [ ] Critical source data is backed up
- [ ] Existing target data is backed up (if any)
- [ ] Rollback plan is prepared for migration failure

---

## Phase 2: Connection and Metadata

### 2.1 Connection Test

- [ ] Source database connection test passed

  POST /kdts/api/v1/datasource/validate
  ```json
  {
    "engine": "RELATIONAL",
    "type": "MYSQL",
    "host": "127.0.0.1",
    "port": 3306,
    "username": "user",
    "password": "pass",
    "dbName": "example_db",
    "isTarget": false
  }
  ```
    - Expected response: `{"code": 0, "data": "SUCCEED"}`
- [ ] Target KaiwuDB connection test passed
    - Set `isTarget: true`

### 2.2 Source-side Metadata

- [ ] List source databases

  POST /kdts/api/v1/datasource/databases

  ```json
  {
    "engine": "RELATIONAL",
    "type": "MYSQL",
    "host": "127.0.0.1",
    "port": 3306,
    "username": "user",
    "password": "pass",
    "dbName": null
  }
  ```

- [ ] Read source table metadata

  POST /kdts/api/v1/datasource/metadata
  ```json
  {
    "source": {
      "engine": "RELATIONAL",
      "type": "MYSQL",
      "host": "127.0.0.1",
      "port": 3306,
      "username": "user",
      "password": "pass",
      "dbName": "example_db"
    },
    "metadata": {
      "enable": true,
      "autoDdl": false,
      "primaryKey": true,
      "constraint": true,
      "comment": true,
      "index": true,
      "view": false
    }
  }
  ```
- [ ] Verify metadata completeness
    - Correct table count
    - Correct column count and types
    - Correct primary keys/constraints
    - (Optional) Comments and indexes included

### 2.3 Sources Without Metadata Support

**If source does NOT support metadata (TDengine 2.x, OpenTSDB, MongoDB, FTP, HDFS):**

- [ ] Skip metadata step
- [ ] Manually prepare table mapping configuration
- [ ] Explicitly specify tables field in migration request

**Note:** SQL Server, InfluxDB 1.x and 2.x support metadata reading (META_AND_DATA capability), but do NOT support full migration. Use two-step migration approach for these sources.

---

## Phase 3: DDL and Schema Migration

### 3.1 DDL Preview

- [ ] Preview target DDL

  POST /kdts/api/v1/metadata/preview
  ```json
  {
    "target": {
      "engine": "RELATIONAL",
      "type": "KAIWUDB",
      "host": "127.0.0.1",
      "port": 26257,
      "username": "root",
      "password": "pass",
      "dbName": "target_db",
      "isTarget": true
    },
    "sourceDb": {
      "type": "MYSQL",
      "name": "source_db",
      "encoding": "UTF-8",
      "tableMap": {
        "example_table": {
          "tableName": "example_table",
          "columns": [
            {
              "columnName": "id",
              "columnType": "INT",
              "nullAble": false,
              "finalConvertDataType": "INT",
              "isChecked": true
            }
          ],
          "primaryKey": {
            "tableName": "example_table",
            "columns": [{"columnName": "id", "asc": true}]
          },
          "constraint": [],
          "indexes": []
        }
      },
      "viewMap": {}
    },
    "metadata": {
      "enable": true,
      "autoDdl": false,
      "primaryKey": true,
      "constraint": true,
      "comment": true,
      "index": true,
      "view": false
    },
    "isTimeSeries": false
  }
  ```

  **Note**: The `sourceDb` field must be a complete `Database` object returned from `/datasource/metadata` API.
  Do NOT pass a simplified structure - use the full response object.
- [ ] Review generated DDL
    - Table names match
    - Column names and types map correctly
    - Primary keys/constraints preserved
    - Special types converted correctly

- [ ] Verify KaiwuDB Time-Series Table Constraints (for TIMESERIES engine)
    - Total columns (Tags + Values) <= 128
    - Primary Tags count <= 4
    - Tag/Column names <= 128 bytes
    - At least 1 Primary Tag defined
    - If exceeded, consider splitting into multiple tables or migrations

### 3.2 DDL Execution

- [ ] (If needed) Drop existing target tables
    - Confirm target table data is backed up or can be discarded
    - Use KaiwuDB DROP TABLE command
- [ ] Execute DDL

  POST /kdts/api/v1/metadata/execute
  ```json
  {
    "target": {
      "engine": "RELATIONAL",
      "type": "KAIWUDB",
      "host": "127.0.0.1",
      "port": 26257,
      "username": "root",
      "password": "pass",
      "dbName": "target_db",
      "isTarget": true
    },
    "ddlScript": {
      "dbName": "SOURCE_DB",
      "createDb": "CREATE DATABASE SOURCE_DB ENGINE=TIMESERIES",
      "table": {
        "example_table": "CREATE TABLE example_table (id INT PRIMARY KEY, name VARCHAR(100))"
      },
      "view": {}
    },
    "autoDdl": false
  }
  ```

  **Note**: The `ddlScript` must be a complete `DdlScript` object returned from `/metadata/preview` API.
  Do NOT pass a simple array of SQL statements.

- [ ] Verify DDL execution result
    - Check table creation success
    - Check column type correctness

### 3.3 Data-Only Migration Scenario

**If target tables already exist and schema matches:**

- [ ] Skip DDL phase
- [ ] Confirm target table schema matches source
- [ ] Execute `TRUNCATE TABLE` if data needs clearing

---

## Phase 4: Data Migration

### 4.1 Build Migration Script

- [ ] Build DataX migration script

  POST /kdts/api/v1/datax/build
  ```json
  {
    "source": {
      "engine": "RELATIONAL",
      "type": "MYSQL",
      "host": "127.0.0.1",
      "port": 3306,
      "username": "user",
      "password": "pass",
      "dbName": "src_db"
    },
    "target": {
      "engine": "RELATIONAL",
      "type": "KAIWUDB",
      "host": "127.0.0.1",
      "port": 26257,
      "username": "root",
      "password": "pass",
      "dbName": "tgt_db",
      "isTarget": true
    },
    "tables": [],
    "data": { "enable": true, "fetchSize": 1000, "batchSize": 1000 }
  }
  ```

  **Note**: Empty `tables` array means auto-discover all tables (for sources that support full migration).
  For table-level migration, specify tables explicitly.

- [ ] Record returned script filename
    - Format: `{SOURCE}2KAIWUDB_{timestamp}.json`
    - Note filename for later queries

### 4.2 Execute Migration

- [ ] Start migration

  POST /kdts/api/v1/datax/execute
  ```json
  ["MYSQL2KAIWUDB_1719290000.json"]
  ```
- [ ] Record returned log file path

### 4.3 Monitor Progress

- [ ] Periodically query task status
  ```
  GET /kdts/api/v1/datax/status?scriptName=MYSQL2KAIWUDB_1719290000.json
  ```
- [ ] Status definitions
    - `SUBMITTED`: Submitted, waiting to execute
    - `RUNNING`: In progress
    - `SUCCEEDED`: Completed successfully
    - `FAILED`: Execution failed
    - `KILLED`: Terminated
- [ ] If failed, view detailed logs

### 4.4 Large Dataset Migration Tips

- [ ] Set `splitPk` on large tables to enable parallelism
- [ ] Adjust `fetchSize` and `batchSize`
- [ ] Set `speed.channel` to increase concurrency
- [ ] Execute migration in time-based batches

---

## Phase 5: Migration Verification

### 5.1 Row Count Verification

- [ ] Verify row count per table
  ```sql
  -- Source
  SELECT COUNT(*) FROM table_name;
  
  -- Target
  SELECT COUNT(*) FROM table_name;
  ```
- [ ] Verify counts match (or match expected difference)

### 5.2 Data Sampling Verification

- [ ] Randomly sample records for comparison
  ```sql
  -- Compare key fields
  SELECT * FROM table_name ORDER BY pk LIMIT 100;
  ```
- [ ] Verify special values (NULL, empty strings, special characters)

### 5.3 Business Verification

- [ ] Core business scenarios pass verification
- [ ] Application functionality works normally
- [ ] No noticeable performance degradation

---

## Troubleshooting Common Issues

### Q1: Connection Test Failed

**Checklist:**

- [ ] Database service is running
- [ ] Correct host/port
- [ ] Network connectivity (firewall)
- [ ] Correct username/password
- [ ] Database exists
- [ ] KDTS Server has access permissions

### Q2: DDL Preview Error

**Checklist:**

- [ ] Source type supports metadata
- [ ] No unsupported column types
- [ ] KaiwuDB version compatibility

### Q3: Migration Timeout

**Checklist:**

- [ ] Source table too large
- [ ] Batch migration needed
- [ ] Sufficient network bandwidth
- [ ] KDTS Server has sufficient resources

**Solutions:**

- Increase timeout
- Reduce migration scope
- Enable parallelism (splitPk)
- Optimize query (WHERE clause)

### Q4: Partial Data Loss

**Checklist:**

- [ ] Any error logs
- [ ] Any data filtered out
- [ ] Any write failures

**Solutions:**

- Check error logs
- Increase errorLimit percentage
- Retry failed tables

---

## Rollback Scenarios

### Scenario 1: DDL Execution Failed

1. Check target table status
2. Drop created tables (if any)
3. Fix source-side issue
4. Re-execute DDL

### Scenario 2: Data Migration Failed (Incomplete)

1. Query task status: `GET /datax/status?scriptName=...`
2. If resumable: check resume support (limited scenarios)
3. If not resumable:
    - Clear target table (TRUNCATE)
    - Rebuild and re-execute migration

### Scenario 3: Migration Completed But Data Has Issues

1. Assess impact scope
2. Fix problematic data
3. Re-migrate affected tables (needs clearing)
4. Or manually fix target data

---

## Performance Optimization

### Before Migration

- [ ] Source: Ensure statistics are up to date (ANALYZE TABLE)
- [ ] Source: Avoid peak hours
- [ ] Target: Create sufficient tablespace
- [ ] Target: Disable unnecessary triggers/constraints

### During Migration

- [ ] Use `splitPk` for parallel reads
- [ ] Adjust `speed.channel` for parallel writes
- [ ] Set appropriate `fetchSize` and `batchSize`
- [ ] Monitor system resources (CPU, memory, disk I/O)

### After Migration

- [ ] Rebuild target indexes (if disabled)
- [ ] Update statistics
- [ ] Verify data integrity

---

## Success Criteria

[OK] All tables migrated successfully  
[OK] Row counts match  
[OK] Data sampling shows no differences  
[OK] Business functionality normal  
[OK] Performance meets expectations

---

**Document Version:** v1.0.0  
**Last Updated:** 2026-08-03  
**Maintainer:** KDTS Development Team
