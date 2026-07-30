# KDTS Heterogeneous Database Migration Checklist

Complete migration workflow checklist to ensure every step is executed correctly.

**Note**: For Chinese version, see [migration-checklist.zh.md](./migration-checklist.zh.md)

---

## Phase 1: Pre-Migration Preparation

### 1.1 Environment Check

- [ ] KDTS Server is running and accessible
  - Access `http://{kdts_host}:{port}/kdts/api/v1/health` to confirm status
  - Default port: 8080
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
  ```json
  POST /kdts/api/v1/datasource/validate
  {
    "engine": "RELATIONAL",
    "type": "MYSQL",
    "host": "...",
    "port": 3306,
    "username": "...",
    "password": "...",
    "dbName": "...",
    "isTarget": false
  }
  ```
  - Expected response: `{"code": 0, "data": "SUCCEED"}`
- [ ] Target KaiwuDB connection test passed
  - Set `isTarget: true`

### 2.2 Source Metadata

- [ ] List source databases
  ```json
  POST /kdts/api/v1/datasource/databases
  { /* source config */ }
  ```
- [ ] Read target table metadata
  ```json
  POST /kdts/api/v1/datasource/metadata
  {
    "source": { /* source config with dbName */ },
    "metadata": { "primaryKey": true, "constraint": true, "comment": true, "index": true, "view": false }
  }
  ```
- [ ] Verify metadata completeness
  - Correct table count
  - Correct column count and types
  - Correct primary keys/constraints
  - (Optional) Comments and indexes included

### 2.3 Sources Without Metadata Support

**If source does NOT support metadata (SQL Server partial versions, TDengine 2.x, InfluxDB 2.x, MongoDB, FTP, HDFS):**

- [ ] Skip metadata step
- [ ] Manually prepare table mapping configuration
- [ ] Explicitly specify tables field in migration request

---

## Phase 3: DDL and Schema Migration

### 3.1 DDL Preview

- [ ] Preview target DDL
  ```json
  POST /kdts/api/v1/metadata/preview
  {
    "target": { /* target config */ },
    "sourceDb": { /* full Database object from /datasource/metadata */ },
    "metadata": { "primaryKey": true, "constraint": true, "comment": true, "index": true, "view": false },
    "isTimeSeries": false
  }
  ```
- [ ] Review generated DDL
  - Table names match
  - Column names and types map correctly
  - Primary keys/constraints preserved
  - Special types converted correctly

### 3.2 DDL Execution

- [ ] (If needed) Drop existing target tables
  - Confirm target table data is backed up or can be discarded
  - Use KaiwuDB DROP TABLE command
- [ ] Execute DDL
  ```json
  POST /kdts/api/v1/metadata/execute
  {
    "target": { /* target config */ },
    "ddlScript": { /* DDL from preview */ },
    "autoDdl": false
  }
  ```
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
  ```json
  POST /kdts/api/v1/datax/build
  {
    "source": { /* source config */ },
    "target": { /* target config (type=KAIWUDB) */ },
    "tables": [],
    "data": { "enable": true, "fetchSize": 1000, "batchSize": 1000 }
  }
  ```
- [ ] Record returned script filename
  - Format: `{SOURCE}2KAIWUDB_{timestamp}.json`
  - Note filename for later queries

### 4.2 Execute Migration

- [ ] Start migration
  ```json
  POST /kdts/api/v1/datax/execute
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

✅ All tables migrated successfully  
✅ Row counts match  
✅ Data sampling shows no differences  
✅ Business functionality normal  
✅ Performance meets expectations  

---

**Document Version:** v2.0  
**Last Updated:** 2024-01-15  
**Maintainer:** KDTS Development Team
