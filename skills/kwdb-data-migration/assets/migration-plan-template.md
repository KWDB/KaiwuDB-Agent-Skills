# KWDB Migration Plan Template

This template is used to help users formulate a standardized KWDB data migration plan, including basic information,
pre-migration preparation, migration steps, validation steps, and rollback plan, to ensure the migration is carried out
in an orderly manner.

## 1. Basic Information

| Item                           | Content                                                                 |
|--------------------------------|-------------------------------------------------------------------------|
| Migration Type                 | □ KWDB → KWDB □ Heterogeneous Database → KWDB                           |
| Source Database Information    | Host:Port: ___; Username: ___; Password: ___; Database: ___; Table: ___ |
| Target Database Information    | Host:Port: ___; Username: ___; Password: ___; Database: ___             |
| Belong to Auto Mapping         | □ Yes  □ No (need manual build table)                                   |
| Migration Tool                 | □ KWDB EXPORT/IMPORT □ KDTS (□ GUI Mode □ Headless Mode)                |
| Migration Mode (Heterogeneous) | □ Full Migration □ Multiple Table Migration                             |

## 2. Type Mapping Confirmation

- Reference official relational / time-series mapping table
- For non-mapping source: Record manual table building and field matching rules

## 3. Pre-Migration Preparation

### 3.1 Data Backup

- Source Database Backup: ___
- Target Database Backup (if any): ___
- Backup Storage Path: ___; Backup Time: ___

### 3.2 Environment Check

- Network Connectivity: Test connectivity between source, target, and KDTS server (if using KDTS), result: ___
  (Normal/Abnormal)
- Permission Check: Source read permission: ___; Target write permission: ___; KDTS permission: ___ (Normal/Abnormal)
- Disk Space: Export path disk space
- Manual table structure creation (if needed)

## 4. Migration Implementation Steps

1. Environment and parameter confirmation
2. Pre-migration check item confirmation
3. Execute export / KDTS task configuration
4. Start migration task and monitor progress
5. Post-migration data consistency verification

## 5. Rollback & Exception Handling

- Failed rows processing scheme
- Structure mismatch adjustment scheme
- Migration rollback and data recovery scheme
