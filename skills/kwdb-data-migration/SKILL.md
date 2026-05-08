---
name: kwdb-data-migration
description: |
  Interactive guidance skill for KWDB data migration. Assist users to complete migration step by step.
  For KWDB to KWDB migration, use built-in EXPORT / IMPORT tools.
  For heterogeneous data migration, use KDTS migration tool (GUI mode recommended, Headless mode for non-interface environments).
  It provides detailed operation guidance, configuration collection, and validation suggestions to ensure smooth migration.
version: 1.0.0
---

# KWDB Data Migration

## Overview

This skill provides standardized interactive step-by-step guidance for KWDB full lifecycle data migration.

For **KWDB to KWDB migration**, recommended to use KWDB built-in EXPORT / IMPORT command tool officially.  
For **Heterogeneous database migration to KWDB**, use KDTS heterogeneous migration tool:

- GUI graphical interface operation is recommended for daily use;
- Non-interface server environment adopts KDTS Headless command-line mode.

KDTS only supports **automatic data migration** for partial heterogeneous data sources. For data sources without
official type mapping rules, the tool does not automatically map table structures and field types; users need to
manually create tables and manually correspond field types first, then perform data migration only.

This skill covers migration scenario selection, configuration collection, pre-migration check, step-by-step operation
guidance, data type mapping reference, migration verification and common constraint specifications.

## Mandatory Rules

The following rules must be strictly followed during all migration processes:

### 1. Prohibit Guessing Migration Parameters

Do not guess or assume any configuration. All parameters must be provided or confirmed by the user.

- Source/target database connection information (IP, port, username, password, database/table)
- Export path, migration mode, data object range
- Tool selection (EXPORT/IMPORT or KDTS)
- Operation mode (GUI or Headless)

### 2. Do Not Execute Migration Without Backup

Data backup of source database must be completed before starting any export, import or KDTS migration task.
Do not proceed migration without user confirmation of backup completion.

### 3. Unmapped Data Sources Require Manual Table Structure Matching

For heterogeneous data sources **without official field type mapping rules**:
KDTS only migrates business data automatically, does not create tables or map field types.
User must manually create target table and complete field type correspondence first.

### 4. Must Check Logs and Failed Rows

If any step fails:

- For EXPORT/IMPORT: Check `reject.txt` and KWDB job logs
- For KDTS: Check task logs and error records in the tool
- Clearly display error information before proceeding

### 5. Must Verify Data Consistency After Migration

After any migration task is completed, row count comparison and sampling verification must be completed;
failed rows and abnormal data must be processed in time.

### 6. Prohibit Migration During Business Peak Window

Avoid executing EXPORT/IMPORT and KDTS tasks during business peak hours to prevent performance impact on source and
target databases.

## Prerequisites

### 1. Supported Environments

#### 1.1 KWDB-to-KWDB Migration

- Source: KWDB 2.x.x / 3.x.x
- Target: KWDB 2.x.x / 3.x.x
- Network connectivity between source and target
- Read/write permissions for EXPORT/IMPORT

#### 1.2 Heterogeneous Migration (KDTS Tool)

- Target: KWDB 2.x.x / 3.x.x
- Supported sources:
    - Relational: MySQL, Oracle, PostgreSQL, ClickHouse, SQL Server
    - Time-Series: KWDB, TDengine, InfluxDB, OpenTSDB
    - NoSQL/Files: MongoDB, FTP, HDFS
    - GUI or Headless environment for KDTS

### 2. Supported Data Sources With Official Type Mapping

#### 2.1 Relational Engine Auto Mapping Supported

MySQL、Oracle、PostgreSQL、KWDB

#### 2.2 Time-Series Engine Auto Mapping Supported

TDengine、InfluxDB、KWDB

#### 2.3 No Automatic Table Mapping (Only Data Migration)

ClickHouse、SQL Server、OpenTSDB、MongoDB、FTP、HDFS
> Rule: For the above-mentioned types, the official has not yet provided the field type mapping rules.
> KDTS only migrates data; users need to manually create KWDB table structure and match field types by themselves.

### 3. Permissions Required

- Source database: read permission of migration objects
- Target KWDB: table creation and write permission
- File path: read/write permission for export/import
- Network: accessible between source, target, and KDTS server
- KDTS tool installed and available for GUI or Headless startup

## KWDB Data Type Mapping Reference

### 1. MySQL → KWDB

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

### 2. PostgreSQL → KWDB

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

### 3. Oracle → KWDB

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

### 4. TDengine → KWDB

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

### 5. InfluxDB → KWDB

| InfluxDB Data Type | KWDB Time-Series Engine Data Type |
|--------------------|-----------------------------------|
| BOOLEAN            | BOOL                              |
| INTEGER            | INT4                              |
| LONG               | INT8                              |
| DOUBLE             | FLOAT8                            |
| FLOAT              | FLOAT8                            |
| STRING             | VARCHAR                           |
| TIMESTAMP          | TIMESTAMP                         |

### 6. KWDB → KWDB Cross Version

Direct compatible mapping, keep original field type without manual adjustment.

### 7. Unmapped Source Special Rule

ClickHouse、SQL Server、OpenTSDB、MongoDB、FTP、HDFS：

- No official automatic field type mapping and table creation capability;
- KDTS only supports multiple table data migration;
- User must manually create target table and complete field type matching before migration task execution.

## Migration Guidance Steps

### Step 1: Confirm Migration Type

ASK: Please select your migration type (enter the corresponding number):

1) KWDB → KWDB (same database type migration)
2) Heterogeneous Database → KWDB (different database type migration)

#### Step 1.1: Branch According to Migration Type

If user selects 1 (KWDB → KWDB):

- Suggestion: Use KWDB built-in EXPORT / IMPORT tool (official recommended).
- Jump to Step 2 (KWDB → KWDB Migration with EXPORT/IMPORT).

If user selects 2 (Heterogeneous → KWDB):

- Suggestion: Use KDTS migration tool. It supports multiple data sources, full migration/multiple table migration.
    - For GUI environment, use graphical interface (recommended);
    - For non-GUI environment, use Headless mode.
- Jump to Step 3 (Heterogeneous Migration with KDTS Tool).

### Step 2: KWDB → KWDB Migration (EXPORT / IMPORT)

#### Step 2.1: Collect Source Database Configuration

ASK: Please provide the following source KWDB information in the specified format (do not omit any items, separate with
commas):
Format: host:port, username, password, database, table (fill in "all" if full database migration)
Example: 127.0.0.1:26257, test, kwdb@123, test_db, all
Example (single table): 127.0.0.1:26257, test, kwdb@123, test_db, user_table

#### Step 2.2: Collect Target Database Configuration

ASK: Please provide the following target KWDB information in the specified format (do not omit any items, separate with
commas):
Format: host:port, username, password, database
Example: 127.0.1.1:26257, test, kwdb@123, test_db

#### Step 2.3: Collect Export Path Configuration

ASK: Please provide the export path (supports nodelocal:// path or local absolute path) in the specified format:
Format: path_type:path
Example 1 (nodelocal path): nodelocal:/kwdb/export/data
Example 2 (local absolute path): local:/opt/kwdb/export

#### Step 2.4: Pre-Migration Check & Operation Suggestion

Suggestion: Please complete the following pre-migration checks before executing the export/import operation:

1. Back up the source database data to prevent data loss due to abnormal operation.
2. Confirm that the export path has read and write permissions.
3. Confirm that the disk space of the export path is sufficient (at least 1.2 times the size of the source data).
4. Confirm network connectivity between the source and target servers (ping test and port connectivity test).
5. Confirm that the source user has EXPORT permission and the target user has IMPORT permission.
6. Avoid performing migration during peak business hours to reduce impact on business.

ASK: Have you completed all the above pre-migration checks? (enter yes/no)

- If yes: Proceed to Step 2.5 (Execute EXPORT).
- If no: Please complete the pre-migration checks first, then enter yes to continue.

#### Step 2.5: Execute EXPORT

ASK: Confirm to start the EXPORT on the source database? (enter yes/no)

- If no: Return to Step 2.4 to recheck.
- If yes: Execute the following operations:

1. Log in to the source KWDB server using the source user.
2. Execute the EXPORT command:
    - Full database export: EXPORT INTO 'export_path' FROM source_database.*;
    - Single table export: EXPORT INTO 'export_path' FROM source_database.source_table;
3. After the export is completed, check the export log to confirm that the export is successful (no error information).
4. Copy all exported files from the export path to the target server's corresponding path.

Reminder: Do not modify the exported file name and format, otherwise the import operation will fail.

ASK: Has the EXPORT been completed successfully and the exported files have been copied to the target
server? (enter yes/no)

- If no: Check the export log, troubleshoot the problem, and re-execute the export operation.
- If yes: Proceed to Step 2.6 (Execute IMPORT).

#### Step 2.6: Execute IMPORT

ASK: Confirm to start the IMPORT on the target database? (enter yes/no)

- If no: Check the exported files and target server path, then reconfirm.
- If yes: Execute the following operations:

1. Log in to the target KWDB server using the target user.
2. Confirm that the imported files have been copied to the target path.
3. Execute the IMPORT command:
   IMPORT INTO target_database.* FROM 'export_path';
4. During the import process, view the import log in real time to monitor the import progress.

Reminder: If the import fails, the failed rows will be stored in the reject.txt file under the export path. After the
import is completed, check the reject.txt file and process the failed rows.

ASK: Has the IMPORT been completed? (enter yes/no)

- If no: Check the import log, troubleshoot the problem, and re-execute the import operation.
- If yes: Proceed to Step 2.7 (Migration Validation).

#### Step 2.7: Migration Validation

Suggestion: Please perform the following 4 verification steps to confirm the migration is successful:

1. Row count consistency check: Compare the total number of rows of the source and target databases/tables.
2. Task status check: Execute "SHOW JOBS;" on the target KWDB to check the import task status, which should be "
   SUCCEEDED".
3. Failed rows check: Check the reject.txt file under the export path. If there are failed rows, analyze the reason and
   reprocess them.
4. Sampling check: Randomly sample 10-20 rows from 3-5 key tables, compare the field values of the source and target
   tables, and ensure they are consistent.

ASK: Have all the above verification steps been completed and the results are normal? (enter yes/no)

- If no: Troubleshoot according to the verification results and re-verify after processing.
- If yes: Proceed to Step 2.8 (Migration Completed).

#### Step 2.8: Migration Completed

Output: KWDB → KWDB data migration has been completed successfully!
Reminder:

1. Keep the exported files and backup data for 7-15 days to prevent subsequent problems.
2. Confirm the availability of the target database business (test application read/write operations).
3. If you need to perform incremental migration later, you can re-execute the EXPORT/IMPORT operation (only
   export/import the newly added data).

### Step 3: Heterogeneous Database Migration (KDTS Tool)

#### Step 3.1: KDTS Tool Introduction & Operation Mode Suggestion

Suggestion:

1. Tool Introduction: KDTS is a professional heterogeneous database migration tool specially designed for KWDB, which
   supports full migration, multiple table migration, and can automatically handle data type mapping and schema
   conversion.
2. Operation Mode:
    - GUI Mode (Recommended): Suitable for environments with graphical interface, easy to operate, with real-time
      progress monitoring and visual configuration.
    - Headless Mode: Suitable for non-GUI environments (such as server command line), using JSON configuration files and
      command lines to complete migration.

ASK: Please select the KDTS operation mode (enter the corresponding number):

1) GUI Mode (graphical interface, recommended for desktop/server with GUI)
2) Headless Mode (command line, for non-GUI server environment)

#### Step 3.2: Confirm Supported Source

Output: KDTS supports the following data sources to migrate to KWDB. Please confirm that your source database is in the
supported list:

1. Relational: MySQL, Oracle, PostgreSQL, ClickHouse, SQL Server
2. Time-Series: KWDB, TDengine, InfluxDB, OpenTSDB
3. NoSQL/Files: MongoDB, FTP, HDFS

ASK: Is your source in the supported list? (enter yes/no)

- If no: The current source is not supported by KDTS. Please use other migration tools.
- If yes: Proceed to Step 3.3 (Collect Configuration).

#### Step 3.3: Collect Source & Target Configuration

##### Step 3.3.1: Collect Source Configuration

ASK: Please select your source database type (enter the corresponding number):

1) MySQL
2) Oracle
3) PostgreSQL
4) ClickHouse
5) SQL Server
6) TDengine
7) InfluxDB
8) MongoDB
9) FTP
10) HDFS

ASK: Please provide source configuration in the specified format (do not omit any items, separate with commas):
Format: host:port, username, password, database, table (fill in "all" if full database migration)
Example (MySQL): 127.0.0.1:3306, test, mysql@123, test_db, all
Example (InfluxDB): 127.0.0.1:8086, test, pwd@123, test_db, all

##### Step 3.3.2: Collect Target KWDB Configuration

ASK: Please provide target KWDB 3.x configuration in the specified format (do not omit any items, separate with commas):
Format: host:port, username, password, database
Example: 127.0.0.1:26257, test, kwdb@123, test_db

##### Step 3.3.3: Collect Migration Mode Configuration

ASK: Please select the migration mode (enter the corresponding number):

1) Full Migration (migrate all existing data once)
2) multiple table migration (migrate specified table existing data once)

#### Step 3.4: Pre-Migration Check & Suggestion

Suggestion: Please complete the following pre-migration checks before starting the KDTS migration task:

1. Back up the source database data and the target KWDB data (if the target database already has data).
2. Confirm network connectivity between the KDTS server, source database server, and target KWDB server.
3. Confirm that the source user has read permission and the target user has write permission.
4. Confirm that the KDTS tool has been installed and started.
5. For FTP/HDFS, confirm that the KDTS tool can access the FTP/HDFS server and has read permission for the target files.
6. Avoid performing migration during peak business hours.

ASK: Have you completed all the pre-migration checks? (enter yes/no)

- If no: Please complete the pre-migration checks first, then enter yes to continue.
- If yes: Proceed to Step 3.5 (GUI Mode Operation Guidance) or Step 3.6 (Headless Mode Operation Guidance) according to
  the selected operation mode.

#### Step 3.5: GUI Mode Operation Guidance

Step-by-step detailed operation guidance (follow the steps in order):

1. Open the KDTS graphical tool (double-click the desktop shortcut or run the startup command).
2. Create a new migration task: Click "New Task" in the upper left corner, enter the task name and select the task type.
3. Configure source data source:
    - Select the source type (consistent with the type you selected in Step 3.3.1).
    - Fill in the source configuration (host:port, username, password, database, table) collected in Step 3.3.1.
    - Click "Test Connection" to confirm that the KDTS tool can connect to the source successfully.
4. Configure target data source:
    - Select the target type as "KWDB".
    - Fill in the target KWDB configuration collected in Step 3.3.2.
    - Click "Test Connection" to confirm that the KDTS tool can connect to the target KWDB successfully.
5. Configure migration mode: Select the migration mode (full/multiple table) you selected in Step 3.3.3.
    - For multiple table migration: Configure the multiple table trigger condition.
6. Select migration objects: Check the databases/tables/files to be migrated.
7. Configure data mapping rules:
    - KDTS will automatically generate data type mapping rules.
    - Preview the mapping rules, and modify them manually if there is a mismatch.
8. Configure task parameters (optional):
    - Set the number of concurrent threads (adjust according to server performance, 5 threads recommended for medium
      data volume).
    - Set the batch size (number of rows per batch, 1000-2000 rows recommended).
9. Preview task configuration: Check all configuration information (source, target, migration mode, mapping rules) to
   ensure no errors.
10. Start the migration task: Click "Start Task" to start the migration.
11. During the migration:
    - Monitor the task status, and view the real-time progress on the task interface.
    - If there is an error, through log to troubleshoot, and pause/resume the task if necessary.

ASK: Has the KDTS GUI mode migration task been started and completed? (enter yes/no)

- If no: Check the task log, troubleshoot the problem, and restart the task.
- If yes: Proceed to Step 3.7 (Migration Validation).

#### Step 3.6: Headless Mode Operation Guidance

Step-by-step detailed operation guidance (follow the steps in order):

1. Prepare the KDTS Headless configuration file (JSON format), and fill in the configuration collected in Step 3.3:
    - Configuration file template (save as migration_task.json): // TODO add headless config json template
2. Upload the configuration file to the KDTS Headless server (such as /opt/kdts/config/).
3. Log in to the KDTS Headless server using the command line.
4. Start the migration task with the following command: // TODO
5. Monitor the migration progress: view the task log.
6. After the task is completed, check the task status.

ASK: Has the KDTS Headless mode migration task been started and completed? (enter yes/no)

- If no: Check the task log, troubleshoot the problem, modify the configuration file if necessary, and restart the task.
- If yes: Proceed to Step 3.7 (Migration Validation).

#### Step 3.7: Migration Validation

Suggestion: Please perform the following 5 verification steps to confirm the migration is successful:

1. Row count consistency check: Compare the total number of rows of the source and target databases/tables. The number
   of rows should be consistent (excluding failed rows recorded in the KDTS log).
2. Field-level sampling check: Randomly sample 10-20 rows from 3-5 key tables, compare the field values of the source
   and target tables, and ensure they are consistent (including data type, length, and value).
3. Migration task status check: Check the KDTS task report, and confirm the task status is "SUCCEEDED".
4. Business availability check: Test the read/write operation of the target KWDB through the application to confirm
   that the business is available.

ASK: Have all the above verification steps been completed and the results are normal? (enter yes/no)

- If no: Troubleshoot according to the verification results and re-verify after processing.
- If yes: Proceed to Step 3.8 (Migration Completed).

#### Step 3.8: Migration Completed

Output: Heterogeneous migration to KWDB completed successfully!
Reminder:

1. Keep the KDTS task configuration file and log file for 7-15 days for subsequent problem troubleshooting.
2. Keep the source database backup data until the target database runs stably for 1-2 weeks.
3. Confirm the long-term stability of the target KWDB business.

## General Notes

1. Data backup is mandatory before migration. Do not migration without backup.
2. Time-series data import (whether EXPORT/IMPORT or KDTS) does not trigger full rollback. Successfully written data
   will be retained, and failed rows will be recorded separately.
3. For KWDB IMPORT operation, failed rows are stored in reject.txt under the export path; for KDTS migration, failed
   rows are recorded in the task log.
4. Do not modify the exported data file format (EXPORT/IMPORT) or KDTS configuration file during migration.
5. After migration, it is necessary to perform data consistency verification and business availability test.
6. For KWDB version upgrade migration, do not downgrade directly after upgrade; downgrade requires reinstalling the old
   version and restoring from backup.
