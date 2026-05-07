# KWDB Migration Official Notes

## 1. Overview

This document records official specifications, supported data sources, engine division and field type mapping rules for
KWDB same-type and heterogeneous migration, guiding users to standardize migration operation and avoid structure
mapping errors.

## 2. Migration Tool Selection Rule

1. KWDB → KWDB: Use built-in EXPORT / IMPORT command preferentially.
2. Heterogeneous → KWDB: Use KDTS migration tool, support GUI and Headless two running modes.
3. KDTS capability limit: Partial data sources support automatic table structure and type mapping; others only support
   pure data migration.

## 3. Supported Data Source Engine Classification

### 3.1 Relational Engine Auto Mapping Supported

MySQL、Oracle、PostgreSQL、KWDB

### 3.2 Time-Series Engine Auto Mapping Supported

TDengine、InfluxDB、KWDB

### 3.3 No Automatic Mapping (Manual Table Creation Required)

ClickHouse、SQL Server、OpenTSDB、MongoDB、FTP、HDFS

- No official field type mapping rules
- KDTS only migrates data automatically
- User must manually build table and match field types in advance

## 4. Official Field Type Mapping Standard

### 4.1 MySQL → KWDB

| MySQL Data Type    | KWDB Relational Engine Data Type | KWDB Time-Series Engine Data Type |
|--------------------|----------------------------------|-----------------------------------|
| BOOLEAN            | BOOL                             | BOOL                              |
| TINYINT(1)         | BOOL                             | BOOL                              |
| TINYINT            | INT2                             | INT2                              |
| SMALLINT           | INT2                             | INT2                              |
| INT                | INT4                             | INT4                              |
| MEDIUMINT          | INT4                             | INT4                              |
| TINYINT UNSIGNED   | INT2                             | INT2                              |
| SMALLINT UNSIGNED  | INT4                             | INT4                              |
| MEDIUMINT UNSIGNED | INT4                             | INT4                              |
| INT UNSIGNED       | INT8                             | INT8                              |
| BIGINT UNSIGNED    | NUMERIC(20)                      | INT8                              |
| BIGINT             | INT8                             | INT8                              |
| DECIMAL            | DECIMAL                          | FLOAT8                            |
| DOUBLE             | FLOAT8                           | FLOAT8                            |
| FLOAT              | FLOAT4                           | FLOAT4                            |
| DATE               | TIMESTAMP                        | TIMESTAMP                         |
| DATETIME           | TIMESTAMP                        | TIMESTAMP                         |
| TIMESTAMP          | TIMESTAMP                        | TIMESTAMP                         |
| TIME               | TIME                             | TIMESTAMP                         |
| CHAR               | CHAR                             | CHAR                              |
| VARCHAR            | VARCHAR                          | VARCHAR                           |
| BINARY             | BYTEA                            | VARBYTES                          |
| VARBINARY          | VARBYTES                         | VARBYTES                          |
| LONG VARBINARY     | VARBYTES                         | VARBYTES                          |
| BLOB               | BYTES                            | VARBYTES                          |
| MEDIUMBLOB         | BYTES                            | VARBYTES                          |
| LONGTEXT           | TEXT                             | NVARCHAR                          |
| JSON               | JSON                             | NVARCHAR                          |

### 4.2 PostgreSQL → KWDB

| PostgreSQL Data Type | KWDB Relational Engine Data Type | KWDB Time-Series Engine Data Type |
|----------------------|----------------------------------|-----------------------------------|
| BIT                  | BIT                              | BOOL                              |
| BOOL                 | BOOL                             | BOOL                              |
| INT2                 | INT2                             | INT2                              |
| INT4                 | INT4                             | INT4                              |
| INT8                 | INT8                             | INT8                              |
| DECIMAL              | DECIMAL                          | FLOAT8                            |
| NUMERIC              | NUMERIC                          | FLOAT8                            |
| MONEY                | DECIMAL                          | FLOAT8                            |
| FLOAT8               | FLOAT8                           | FLOAT8                            |
| FLOAT4               | FLOAT4                           | FLOAT4                            |
| DATE                 | DATE                             | TIMESTAMP                         |
| TIMESTAMP            | TIMESTAMP                        | TIMESTAMP                         |
| TIMESTAMPTZ          | TIMESTAMPTZ                      | TIMESTAMPTZ                       |
| TIME                 | TIME                             | TIMESTAMP                         |
| TIMETZ               | TIMETZ                           | TIMESTAMPTZ                       |
| BPCHAR, CHAR         | CHAR                             | CHAR                              |
| VARCHAR              | VARCHAR                          | VARCHAR                           |
| BYTEA                | BYTES                            | VARBYTES                          |
| BLOB                 | BYTES                            | VARBYTES                          |
| VARBIT               | VARBIT                           | VARCHAR                           |
| TEXT                 | TEXT                             | NVARCHAR                          |
| JSON                 | JSON                             | NVARCHAR                          |
| JSONB                | JSONB                            | NVARCHAR                          |
| UUID                 | UUID                             | VARCHAR                           |
| UNKNOWN              | UNKNOWN                          | VARCHAR                           |

### 4.3 Oracle → KWDB

| Oracle Data Type | KWDB Relational Engine Data Type | KWDB Time-Series Engine Data Type |
|------------------|----------------------------------|-----------------------------------|
| ROWID            | INT4                             | INT4                              |
| BOOLEAN          | BOOL                             | BOOL                              |
| NUMBER(5,0)      | INT2                             | INT2                              |
| NUMBER(5)        | INT2                             | INT2                              |
| NUMBER(10,0)     | INT4                             | INT4                              |
| NUMBER(10)       | INT4                             | INT4                              |
| NUMBER(19,0)     | INT8                             | INT8                              |
| NUMBER(19)       | INT8                             | INT8                              |
| NUMBER           | FLOAT4                           | FLOAT4                            |
| FLOAT            | FLOAT4                           | FLOAT4                            |
| BINARY_FLOAT     | FLOAT4                           | FLOAT4                            |
| BINARY_DOUBLE    | FLOAT8                           | FLOAT8                            |
| CHAR             | CHAR                             | CHAR                              |
| VARCHAR2         | VARCHAR                          | VARCHAR                           |
| NCHAR            | TEXT                             | NCHAR                             |
| NVARCHAR2        | TEXT                             | NVARCHAR                          |
| BLOB             | BYTES                            | VARBYTES                          |
| CLOB             | TEXT                             | NVARCHAR                          |
| RAW              | BYTES                            | VARBYTES                          |
| DATE             | TIMESTAMP                        | TIMESTAMP                         |
| TIMESTAMP        | TIMESTAMP                        | TIMESTAMP                         |
| TIMESTAMP(3)     | TIMESTAMP                        | TIMESTAMP                         |
| TIMESTAMP(6)     | TIMESTAMP                        | TIMESTAMP                         |

### 4.4 TDengine → KWDB

| TDengine Data Type | KWDB Time-Series Engine Data Type |
|--------------------|-----------------------------------|
| BOOL               | BOOL                              |
| TINYINT            | INT2                              |
| SMALLINT           | INT2                              |
| INT                | INT4                              |
| BIGINT             | INT8                              |
| DOUBLE             | FLOAT8                            |
| FLOAT              | FLOAT4                            |
| NCHAR              | NCHAR                             |
| VARCHAR            | VARCHAR                           |
| BINARY             | VARBYTES                          |
| VARBINARY          | VARBYTES                          |
| TIMESTAMP          | TIMESTAMP                         |
| JSON               | NVARCHAR                          |
| TINYINT UNSIGNED   | INT2                              |
| SMALLINT UNSIGNED  | INT4                              |
| INT UNSIGNED       | INT8                              |
| BIGINT UNSIGNED    | INT8                              |

### 4.5 InfluxDB → KWDB

| InfluxDB Data Type | KWDB Time-Series Engine Data Type |
|--------------------|-----------------------------------|
| BOOLEAN            | BOOL                              |
| INTEGER            | INT4                              |
| LONG               | INT8                              |
| DOUBLE             | FLOAT8                            |
| FLOAT              | FLOAT8                            |
| STRING             | VARCHAR                           |
| TIMESTAMP          | TIMESTAMP                         |

### 4.6 KWDB → KWDB Cross Version

Direct compatible mapping, keep original field type without manual adjustment.

## 5. KWDB-to-KWDB Migration (EXPORT/IMPORT)

### 5.1 Official Recommendation

It is the official recommended migration solution for KWDB-to-KWDB migration. It has the best compatibility,
performance, and stability, and supports full database, single table, schema-only, and data-only migration.

### 5.2 KeyNotes

1. Export Path: Supports nodelocal:// path and local absolute path. The path must have read/write permission.
2. Export File: Do not modify the file name, suffix, or content of the exported files, otherwise the import will fail.
3. Import: Import path must be consistent with the export path.
4. Failed Rows: Import failed rows are stored in the reject.txt file under the export path. After the import is
   completed, process the failed rows in time.
5. Time-Series Data: Import failure does not trigger full rollback. Successfully written data will be retained.

## 6. Heterogeneous Migration (KDTS Tool)

### 6.1 Official Recommendation

KDTS is a professional heterogeneous database migration tool specially designed for KWDB, which supports full
migration, multiple table migration, and can automatically handle data type mapping and schema conversion.

### 6.2 Supported Data Sources

- Relational: MySQL, Oracle, PostgreSQL, ClickHouse, SQL Server
- Time-Series: KWDB, TDengine, InfluxDB, OpenTSDB
- NoSQL/Files: MongoDB, FTP, HDFS

### 6.3 KeyNotes

1. Operation Mode:
    - GUI mode is recommended for users with graphical interface.
    - Headless mode is recommended for non-GUI server environments.
2. Configuration File (Headless Mode): The JSON configuration file must be correctly filled in, especially the source
   and target connection parameters and migration mode.
3. Data Mapping: KDTS automatically generates data type mapping rules. If there is a mismatch, modify it manually
   according to KWDB data type specifications.
4. Concurrent Threads: The number of concurrent threads should be adjusted according to the server performance to avoid
   affecting the source/target database performance.
5. Logs: KDTS task logs record the migration process, success rate, and failed rows. Check the logs in time when the
   task fails.

## 7. General Notes

1. Data Backup: Back up the source database and target database before migration to prevent data loss.
2. Peak Avoidance: Do not perform migration during peak business hours to reduce the impact on business.
3. Before heterogeneous migration, confirm whether the source is in auto-mapping list.
4. Unmapped source: manual table building → field type matching → execute data migration only.
5. Rollback: For KWDB-to-KWDB migration, rollback can be achieved by deleting the target data and re-importing; for
   heterogeneous migration, rollback can be achieved by restoring the target database from backup.
6. Upgrade Migration: For KWDB version upgrade migration, do not downgrade directly after upgrade; downgrade requires
   reinstalling the old version and restoring from backup.
