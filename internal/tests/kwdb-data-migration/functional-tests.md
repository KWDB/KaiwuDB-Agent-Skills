# KWDB Data Migration Functional Tests

Comprehensive functional test suite for the KWDB heterogeneous database migration skill.

## Test Environment

### Prerequisites
- KDTS Server (version 2.0+) running and accessible
- Source databases with test data:
  - MySQL 5.7+ or 8.0+
  - PostgreSQL 12+
  - Oracle 12c+
  - ClickHouse 21+
  - MongoDB 4.4+
  - TDengine 2.x and 3.x
  - InfluxDB 1.x and 2.x
  - HDFS 3.x
  - FTP Server
- Target KaiwuDB (RELATIONAL and TIMESERIES engines)
- Python 3.8+ with requests library

### Test Data Sets
- Small database (10 tables, <10K rows each)
- Medium database (50 tables, 100K rows each)
- Large database (100 tables, 1M rows each)
- Tables with special types (BLOB, JSON, ARRAY, GEOMETRY)
- Tables with composite primary keys
- Tables with foreign key constraints
- Tables with triggers and stored procedures

---

## Test Cases

### T1: Basic Connectivity Tests

#### T1.1 KDTS Server Health Check
**Description**: Verify KDTS server is responding
**Steps**:
1. Call GET {base_url}/health
2. Verify response code 200
3. Verify response body contains "UP" status
**Expected**: Server is healthy and responding

#### T1.2 Source Database Connection
**Description**: Test connection to each supported source type
**Steps**:
1. Configure connection for each source type (MYSQL, ORACLE, POSTGRESQL, etc.)
2. Call POST /datasource/validate with source config
3. Verify response code 0
**Expected**: All sources return connection success

#### T1.3 Target KaiwuDB Connection
**Description**: Test connection to KaiwuDB target
**Steps**:
1. Configure KaiwuDB connection (host: 127.0.0.1, port: 26257)
2. Call POST /datasource/validate with isTarget=true
3. Verify response code 0
**Expected**: KaiwuDB target accessible

#### T1.4 Connection Failure Handling
**Description**: Verify proper error on connection failure
**Steps**:
1. Configure with invalid host/port
2. Call POST /datasource/validate
3. Verify error code and message
4. Call ErrorHandler.get_error_hint()
**Expected**: 
- Returns non-zero error code (2001)
- Error message contains connection details
- Error hint provides troubleshooting steps

---

### T2: Metadata Operations

#### T2.1 List Source Databases
**Description**: List all databases on source
**Steps**:
1. Connect to source database
2. Call POST /datasource/databases
3. Verify list contains expected databases
**Expected**: Returns list of accessible databases

#### T2.2 Read Table Metadata
**Description**: Read full table structure from source
**Steps**:
1. Configure source with dbName
2. Call POST /datasource/metadata
3. Verify response contains:
   - Table names
   - Column definitions
   - Primary key info
   - Index definitions
   - Foreign key constraints
**Expected**: Complete metadata returned

#### T2.3 Metadata Options
**Description**: Test different metadata extraction options
**Steps**:
1. Test with various metadata options:
   - primaryKey: true/false
   - constraint: true/false
   - comment: true/false
   - index: true/false
   - view: true/false
2. Verify response changes accordingly
**Expected**: Metadata filtered by options

#### T2.4 Unsupported Metadata
**Description**: Test metadata reading on unsupported sources
**Steps**:
1. Try metadata on ClickHouse (no metadata support)
2. Try metadata on TDengine 2.x (no metadata support)
3. Try metadata on HDFS (file source)
4. Verify error handling
**Expected**: Appropriate error returned (or empty metadata)

---

### T3: DDL Operations

#### T3.1 Preview DDL Generation
**Description**: Generate DDL for KaiwuDB target
**Steps**:
1. Read source metadata
2. Call POST /metadata/preview with target config and source DB
3. Verify DDL contains valid KaiwuDB syntax
4. Check table definitions match source structure
**Expected**: Valid KaiwuDB DDL generated

#### T3.2 DDL with Time Series
**Description**: Generate DDL for time series data
**Steps**:
1. Use TDengine 3.x or InfluxDB source
2. Call POST /metadata/preview with isTimeSeries=true
3. Verify DDL contains TAG definitions
4. Verify ENGINE=TIMESERIES
**Expected**: Time series DDL generated correctly

#### T3.3 Execute DDL on Target
**Description**: Create tables in KaiwuDB
**Steps**:
1. Preview DDL successfully
2. Call POST /metadata/execute with DDL script
3. Verify response code 0
4. Verify log file path returned
**Expected**: Tables created successfully in target

#### T3.4 DDL Error Handling
**Description**: Handle DDL execution errors
**Steps**:
1. Try to create table that already exists (auto_ddl=false)
2. Try to create invalid DDL
3. Try with insufficient privileges
4. Verify error messages are clear
**Expected**: Specific error for each case

---

### T4: Migration Operations

#### T4.1 Full Database Migration
**Description**: Migrate entire database schema and data
**Steps**:
1. Test connections
2. Read metadata
3. Preview and execute DDL
4. Call POST /datax/build with empty tables list
5. Call POST /datax/execute with generated scripts
6. Monitor with GET /datax/status until complete
7. Verify row counts match
**Expected**: All tables migrated with data

#### T4.2 Table-Level Migration
**Description**: Migrate specific tables only
**Steps**:
1. Define explicit table mappings
2. Call POST /datax/build with tables array
3. Execute migration
4. Verify only specified tables migrated
**Expected**: Only mapped tables migrated

#### T4.3 Schema-Only Migration
**Description**: Migrate table structure without data
**Steps**:
1. Execute DDL only (skip data migration)
2. Verify tables created but empty
**Expected**: Tables exist with correct structure, no data

#### T4.4 Data-Only Migration
**Description**: Migrate data to existing tables
**Steps**:
1. Ensure tables exist in target
2. Call POST /datax/build with tables array (no metadata needed)
3. Execute migration
4. Verify data inserted into existing tables
**Expected**: Data migrated to pre-existing tables

#### T4.5 Batch Migration
**Description**: Migrate in batches for large datasets
**Steps**:
1. Split tables into batches
2. Call workflow.run_batch_migration()
3. Verify each batch completes
4. Verify error handling if batch fails
**Expected**: All batches succeed or partial failure reported

---

### T5: Progress Monitoring

#### T5.1 Real-time Status Query
**Description**: Get current migration progress
**Steps**:
1. Start migration
2. Call GET /datax/status periodically
3. Verify progress increases
4. Check for proper state transitions
**Expected**: Correct progress and state reporting

#### T5.2 Completion Detection
**Description**: Detect migration completion
**Steps**:
1. Wait for migration to finish
2. Call workflow.wait_for_completion()
3. Verify final state is SUCCEEDED or FAILED
**Expected**: Proper completion detection

#### T5.3 Timeout Handling
**Description**: Handle migration timeout
**Steps**:
1. Set very short timeout (e.g., 10 seconds)
2. Start large migration
3. Verify timeout handling
4. Check current progress after timeout
**Expected**: Timeout reported with partial progress

---

### T6: Task Control

#### T6.1 Kill Running Task
**Description**: Terminate active migration
**Steps**:
1. Start migration
2. Verify task is RUNNING
3. Call POST /datax/control with action=KILL
4. Verify response code 0
5. Query status to confirm KILLED
**Expected**: Task terminated successfully

#### T6.2 Kill with Confirmation Flow
**Description**: Test safety guard for KILL operation
**Steps**:
1. Call workflow.kill_task() with confirm=false
2. Verify response contains warning
3. Call workflow.kill_task() with confirm=true
4. Verify actual KILL executed
**Expected**: Safety guard works correctly

#### T6.3 Control Task Error Handling
**Description**: Handle control operation errors
**Steps**:
1. Try to KILL non-existent task
2. Try to KILL already completed task
3. Verify proper error handling
**Expected**: Appropriate error for each case

---

### T7: Configuration Validation

#### T7.1 Valid Source Types
**Description**: Validate all supported source types
**Steps**:
1. Test each of 14 source types with config_validator
2. Verify all pass validation
**Expected**: All valid source types accepted

#### T7.2 Invalid Source Type
**Description**: Validate unsupported source type
**Steps**:
1. Test with made-up source type (e.g., "MYSQL8")
2. Verify validation fails
3. Check error message lists valid types
**Expected**: Clear error with valid types listed

#### T7.3 Capability Validation
**Description**: Check source capability limits
**Steps**:
1. Test full migration on SQLSERVER (table-only)
2. Verify validation fails for full migration
3. Test table-level migration on SQLSERVER
4. Verify validation passes
**Expected**: Correct capability enforcement

#### T7.4 Missing Required Fields
**Description**: Validate required field presence
**Steps**:
1. Test config missing host
2. Test config missing credentials
3. Test config missing dbName
4. Verify each returns specific error
**Expected**: Clear indication of missing fields

---

### T8: Cross-Type Compatibility

#### T8.1 MySQL to KaiwuDB Migration
**Description**: Test MySQL source compatibility
**Steps**:
1. Configure MySQL source
2. Run full migration
3. Verify data integrity
**Expected**: All MySQL types mapped correctly

#### T8.2 Oracle to KaiwuDB Migration
**Description**: Test Oracle source compatibility
**Steps**:
1. Configure Oracle source (connectType=SID and SERVICE_NAME)
2. Run full migration
3. Verify special Oracle types (CLOB, BLOB, TIMESTAMP WITH TIMEZONE)
**Expected**: Oracle-specific types handled

#### T8.3 PostgreSQL to KaiwuDB Migration
**Description**: Test PostgreSQL source compatibility
**Steps**:
1. Configure PostgreSQL source
2. Run full migration
3. Verify array, JSON, UUID types
**Expected**: PostgreSQL-specific types mapped

#### T8.4 Time Series Migration
**Description**: Test time series database sources
**Steps**:
1. Configure TDengine 3.x source
2. Run full migration with time series
3. Verify TAG and PRIMARY KEY handling
**Expected**: Time series structure preserved

#### T8.5 File Source Migration
**Description**: Test file-based source migration
**Steps**:
1. Configure FTP or HDFS source
2. Define explicit table mapping
3. Execute migration
**Expected**: File data imported correctly

---

### T9: Error Handling Integration

#### T9.1 Error Code Lookup
**Description**: Test error code mapping
**Steps**:
1. Test each error code range (1xxx, 2xxx, 3xxx, 4xxx, 5xxx, 9xxx)
2. Verify get_error_hint() returns message and suggestion
3. Verify messages are user-friendly
**Expected**: All error codes have meaningful hints

#### T9.2 Error Recovery Flow
**Description**: Test error recovery automation
**Steps**:
1. Simulate connection failure
2. Verify error handler suggests checking network
3. Simulate metadata error
4. Verify error handler suggests permissions check
5. Simulate migration failure
6. Verify error handler suggests retry or skip
**Expected**: Appropriate recovery suggestions

#### T9.3 Partial Failure Recovery
**Description**: Test recovery from partial migration failure
**Steps**:
1. Start migration with multiple tables
2. Inject failure in one table
3. Verify workflow reports partial success
4. Test retry for failed tables only
**Expected**: Partial success reported, retry works

---

### T10: Workflow Orchestration

#### T10.1 Full Workflow Execution
**Description**: Execute complete full migration workflow
**Steps**:
1. Call workflow.run_full_migration()
2. Verify all steps executed in order
3. Check step results in workflow history
4. Verify final success flag
**Expected**: Complete workflow with all step results

#### T10.2 Workflow History Tracking
**Description**: Verify step tracking
**Steps**:
1. Execute workflow
2. Call get_workflow_history()
3. Verify each step recorded
4. Check step types and results
**Expected**: Complete history available

#### T10.3 Early Termination on Failure
**Description**: Verify workflow stops on critical failure
**Steps**:
1. Start workflow
2. Force connection failure
3. Verify workflow stops after step 1
4. Check error message
**Expected**: Early termination with clear error

#### T10.4 Confirmation Gate Integration
**Description**: Verify DDL confirmation works
**Steps**:
1. Run workflow with execute_ddl_confirm callback
2. Return False from callback
3. Verify workflow stops before DDL execution
4. Check workflow state
**Expected**: DDL not executed when not confirmed

---

## Test Execution Checklist

### Before Each Test
- [ ] KDTS server running
- [ ] Source databases accessible
- [ ] Target KaiwuDB accessible
- [ ] Test data available
- [ ] Previous test data cleaned up

### After Each Test
- [ ] Verify target state
- [ ] Check logs for errors
- [ ] Clean up test data
- [ ] Document any failures

### Test Data Cleanup
```sql
-- Cleanup KaiwuDB target
DROP DATABASE IF EXISTS test_mysql;
DROP DATABASE IF EXISTS test_postgres;
DROP DATABASE IF EXISTS test_oracle;
```

---

## Known Limitations

1. **No Transaction Support**: Migration is not atomic; partial success possible
2. **No Rollback**: Failed migrations leave partial data
3. **Huge Data Types**: BLOB/CLOB > 64KB need special handling
4. **Complex Triggers**: Source triggers not migrated automatically
5. **Stored Procedures**: Need manual migration after data

---

## Test Result Template

| Test ID | Description | Status | Duration | Notes |
|---------|-------------|--------|----------|-------|
| T1.1 | Server health | PASS | 2s | - |
| T1.2 | MySQL connection | PASS | 1s | - |
| T1.2 | Oracle connection | PASS | 3s | SID vs SERVICE_NAME |
| T2.1 | List databases | PASS | 500ms | - |
| T3.1 | Preview DDL | PASS | 2s | TIMESTAMP handled |
| T4.1 | Full migration | PASS | 45s | 10 tables, 10K rows each |
| T9.1 | Error hints | PASS | - | All 18 codes tested |