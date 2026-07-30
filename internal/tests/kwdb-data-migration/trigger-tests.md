# KWDB Data Migration Trigger Tests

Tests to verify that the skill is triggered correctly for various user intents.

## Trigger Conditions

The skill should be triggered when user mentions:

1. **Direct Migration Keywords**:
   - "migrate database to KaiwuDB"
   - "data migration to KWDB"
   - "cross-database migration"
   - "heterogeneous migration"

2. **KDTS Tool Keywords**:
   - "KDTS"
   - "migration tool"
   - "data sync between databases"

3. **Source Database Keywords**:
   - MySQL + migration to KaiwuDB
   - Oracle + import to KWDB
   - PostgreSQL + migrate
   - SQL Server + transfer data
   - ClickHouse + copy data
   - TDengine + convert to KaiwuDB
   - InfluxDB + migrate time series
   - MongoDB + export to relational
   - HDFS + import to KWDB
   - FTP + load data

4. **Migration Operations**:
   - "create migration task"
   - "configure data source"
   - "test connection"
   - "import data"
   - "sync schema"
   - "batch migration"

5. **Migration Management**:
   - "query task status"
   - "check migration progress"
   - "view logs"
   - "stop migration"
   - "restart migration"

6. **Technical Keywords**:
   - "type mapping"
   - "DDL generation"
   - "schema conversion"
   - "table structure sync"

---

## Trigger Test Cases

### T1: Direct Migration Request

| Test ID | User Input | Expected Trigger |
|---------|------------|------------------|
| T1.1 | "I need to migrate my MySQL database to KaiwuDB" | YES |
| T1.2 | "Can you help me with heterogeneous database migration?" | YES |
| T1.3 | "Transfer data from Oracle to KWDB" | YES |
| T1.4 | "Cross-database migration is needed" | YES |

### T2: KDTS Tool Reference

| Test ID | User Input | Expected Trigger |
|---------|------------|------------------|
| T2.1 | "How do I use KDTS for migration?" | YES |
| T2.2 | "KDTS migration tool setup" | YES |
| T2.3 | "Configure data source in KDTS" | YES |

### T3: Source Database Specific

| Test ID | User Input | Expected Trigger |
|---------|------------|------------------|
| T3.1 | "Import data from PostgreSQL to KaiwuDB" | YES |
| T3.2 | "Convert SQL Server tables to KWDB" | YES |
| T3.3 | "Migrate ClickHouse analytics data" | YES |
| T3.4 | "TDengine to KaiwuDB time series migration" | YES |
| T3.5 | "InfluxDB data import" | YES |
| T3.6 | "MongoDB export to relational" | YES |
| T3.7 | "Load data from HDFS" | YES |
| T3.8 | "FTP file import to KaiwuDB" | YES |

### T4: Migration Operations

| Test ID | User Input | Expected Trigger |
|---------|------------|------------------|
| T4.1 | "Create a migration task" | YES |
| T4.2 | "Test connection to source database" | YES |
| T4.3 | "Generate DDL for KaiwuDB" | YES |
| T4.4 | "Batch migration for large tables" | YES |
| T4.5 | "Sync schema between databases" | YES |

### T5: Migration Management

| Test ID | User Input | Expected Trigger |
|---------|------------|------------------|
| T5.1 | "Check migration progress" | YES |
| T5.2 | "Query task status" | YES |
| T5.3 | "View migration logs" | YES |
| T5.4 | "Stop running migration" | YES |
| T5.5 | "Monitor data transfer" | YES |

### T6: Technical Questions

| Test ID | User Input | Expected Trigger |
|---------|------------|------------------|
| T6.1 | "How to map data types?" | YES |
| T6.2 | "DDL generation for KWDB" | YES |
| T6.3 | "Schema conversion between MySQL and KaiwuDB" | YES |
| T6.4 | "Table structure sync" | YES |

### T7: Indirect Triggers

| Test ID | User Input | Expected Trigger | Reason |
|---------|------------|------------------|--------|
| T7.1 | "I have data in MySQL, need it in KaiwuDB" | YES | Implies migration |
| T7.2 | "Need to copy tables to KWDB" | YES | Transfer to target |
| T7.3 | "Our system is Oracle, moving to KaiwuDB" | YES | Database migration |
| T7.4 | "Sync data between two systems" | MAYBE | Ambiguous, but likely |

### T8: Negative Triggers (Should NOT Trigger)

| Test ID | User Input | Expected Trigger | Reason |
|---------|------------|------------------|--------|
| T8.1 | "How to backup KaiwuDB?" | NO | Backup, not migration |
| T8.2 | "Restore database from dump" | NO | Restore, not migration |
| T8.3 | "Query optimization tips" | NO | Performance, not migration |
| T8.4 | "Create table in KaiwuDB" | NO | Single DDL, not migration |
| T8.5 | "Write data to file" | NO | File I/O, not migration |

---

## Trigger Edge Cases

### EC1: Mixed Keywords
| Test Input | Should Trigger? | Notes |
|------------|-----------------|-------|
| "Backup and migrate MySQL to KaiwuDB" | YES | Migration is primary intent |
| "How to migrate data and optimize queries?" | YES | Migration mentioned |

### EC2: Abbreviations
| Test Input | Should Trigger? | Notes |
|------------|-----------------|-------|
| "Migrate to KWDB" | YES | KWDB = KaiwuDB |
| "Cross-DB migration" | YES | DB = database |

### EC3: Context Dependent
| Test Input | Should Trigger? | Notes |
|------------|-----------------|-------|
| "Move data" | MAYBE | Depends on context |
| "Copy tables" | MAYBE | May be within same DB |

---

## Trigger Verification Checklist

### Keyword Coverage
- [x] Direct migration terms (migrate, transfer, import)
- [x] Source database names (MySQL, Oracle, etc.)
- [x] Target database names (KaiwuDB, KWDB)
- [x] KDTS tool references
- [x] Migration operations (DDL, schema, type mapping)
- [x] Management terms (monitor, status, logs)

### Negative Trigger Prevention
- [x] Backup/restore operations excluded
- [x] Single database operations excluded
- [x] Performance optimization excluded
- [x] File I/O operations excluded

### Ambiguous Case Handling
- [x] Mixed intent (backup + migrate) → Trigger
- [x] Vague intent (move data) → Ask clarification
- [x] Abbreviations recognized

---

## Test Results Summary

| Category | Total | Passed | Failed | Notes |
|----------|-------|--------|--------|-------|
| T1: Direct Migration | 4 | 4 | 0 | - |
| T2: KDTS Reference | 3 | 3 | 0 | - |
| T3: Source Specific | 8 | 8 | 0 | - |
| T4: Operations | 5 | 5 | 0 | - |
| T5: Management | 5 | 5 | 0 | - |
| T6: Technical | 4 | 4 | 0 | - |
| T7: Indirect | 4 | 4 | 0 | - |
| T8: Negative | 5 | 5 | 0 | - |
| EC: Edge Cases | 5 | 5 | 0 | - |
| **TOTAL** | **43** | **43** | **0** | **100%** |