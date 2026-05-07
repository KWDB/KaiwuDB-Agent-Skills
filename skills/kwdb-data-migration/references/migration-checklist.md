# KWDB Migration Checklist

This checklist is used to help users complete all pre-migration, in-migration, and post-migration checks to ensure the
migration process is smooth and the data is consistent.

## 1. Pre-Migration Checklist (Must Complete)

| Check Item                  | Check Content                                                                                                       | Check Result (Yes/No) |
|-----------------------------|---------------------------------------------------------------------------------------------------------------------|-----------------------|
| Migration Type Confirmation | Confirm whether the migration type is KWDB→KWDB or Heterogeneous→KWDB                                               |                       |
| Data Backup                 | Back up the source database data; back up the target database data (if any)                                         |                       |
| Network Connectivity        | Confirm network connectivity between source, target, and KDTS server (if using KDTS)                                |                       |
| Permission Check            | Source user has read permission; target user has write permission; KDTS user has access permission (if using KDTS)  |                       |
| Path & Disk Space           | Export path has read/write permission and sufficient disk space (≥1.2 times source data size)                       |                       |
| Tool Preparation            | For KWDB→KWDB: Confirm KWDB service is running; For Heterogeneous: Confirm KDTS is installed and started            |                       |
| Version Compatibility       | Target KWDB version is 3.x (for heterogeneous migration); source and target versions are compatible (for KWDB→KWDB) |                       |
| Business Peak Avoidance     | Confirm migration time is not during business peak hours                                                            |                       |

## 2. Structure Mapping Check Before Heterogeneous Migration

| Check Item         | Check Content                                                            | Check Result (Yes/No) |
|--------------------|--------------------------------------------------------------------------|-----------------------|
| Relational source  | Check field type alignment refer to official mapping table               |                       |
| Time-series source | Check timestamp and metric type mapping rationality                      |                       |
| Unmapped source    | Confirm manual table structure is consistent with source business fields |                       |

## 3. In-Migration Checklist (Real-Time Monitoring)

| Check Item          | Check Content                                                          | Check Result (Normal/Abnormal) |
|---------------------|------------------------------------------------------------------------|--------------------------------|
| Task Status         | Migration task is running normally, no abnormal pause or failure       |                                |
| Progress Monitoring | Real-time view of migration progress, success rate, and processed rows |                                |
| Log Check           | Check migration logs in real time, no fatal errors                     |                                |
| Resource Usage      | Server CPU, memory, disk I/O usage is normal, no overload              |                                |
| Failed Rows         | Record failed rows in real time, no massive failure                    |                                |

## 4. Post-Migration Checklist (Must Complete)

| Check Item               | Check Content                                                                 | Check Result (Yes/No) |
|--------------------------|-------------------------------------------------------------------------------|-----------------------|
| Task Status Confirmation | Migration task is completed, status is "SUCCEEDED"                            |                       |
| Row Count Consistency    | Source and target total rows are consistent (excluding failed rows)           |                       |
| Sampling Check           | Key tables are sampled, field values are consistent between source and target |                       |
| Failed Rows Processing   | Failed rows are processed, and re-migrated successfully (if any)              |                       |
| Business Availability    | Target database business is available, application read/write is normal       |                       |
| Log Retention            | Migration logs, configuration files, and backup data are retained             |                       |

## 5. Special Notes

1. For time-series data migration, failed rows will not trigger full rollback, and successfully written data will be
   retained.
2. For KDTS Headless mode, ensure the configuration file is correct before starting the task.
3. For KWDB EXPORT/IMPORT, do not modify the exported file format.
4. After migration, retain backup data and logs for 7-15 days.
