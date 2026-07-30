# Supported Source Types

Complete reference of all source types supported by KDTS, their capabilities, and configuration requirements.

## Capability Legend

| Symbol | Meaning |
|--------|---------|
| Full Migration | Can migrate entire database (all tables auto-discovered) |
| Metadata | Supports reading table structure for DDL generation |
| Table-Level | Can migrate specific tables (without auto-discovery) |
| Time Series | Special handling for time-series data |

---

## Source Type Matrix

| Source Type | Engine | Full Migration | Metadata | Time Series | Notes |
|-------------|--------|----------------|----------|-------------|-------|
| **MYSQL** | RELATIONAL | ✅ | ✅ | ❌ | Most common source |
| **ORACLE** | RELATIONAL | ✅ | ✅ | ❌ | Enterprise DB |
| **POSTGRESQL** | RELATIONAL | ✅ | ✅ | ❌ | Open-source alternative |
| **SQLSERVER** | RELATIONAL | ❌ | ✅ | ❌ | Table-level only |
| **CLICKHOUSE** | RELATIONAL | ✅ | ❌ | ❌ | Analytics DB, no metadata |
| **KAIWUDB** | BOTH | ✅ | ✅ | ✅ | KWDB-to-KWDB direct |
| **TDENGINE3X** | TIMESERIES | ✅ | ✅ | ✅ | Recommended TDengine version |
| **TDENGINE2X** | TIMESERIES | ❌ | ❌ | ✅ | Legacy version |
| **INFLUXDB1X** | TIMESERIES | ❌ | ✅ | ✅ | Old InfluxDB |
| **INFLUXDB2X** | TIMESERIES | ❌ | ❌ | ✅ | New InfluxDB |
| **OPENTSDB** | TIMESERIES | ❌ | ❌ | ✅ | Time-series DB |
| **MONGODB** | - | ❌ | ❌ | ❌ | Document DB |
| **FTP** | - | ❌ | ❌ | ❌ | File transfer |
| **HDFS** | - | ❌ | ❌ | ❌ | Hadoop filesystem |

---

## Target Configuration

**IMPORTANT**: Target is **ALWAYS** KaiwuDB with type = `KAIWUDB`.

| Target | Engine | Required |
|--------|--------|----------|
| Relational KWDB | RELATIONAL | ✅ |
| Time Series KWDB | TIMESERIES | ✅ |

Cannot migrate to other database types. For other targets, use native database tools or ETL solutions.

---

## sourceType Mapping

When building migration scripts, use the correct `sourceType` based on KDTS source type:

| KDTS Source Type | sourceType Value | Description |
|------------------|------------------|-------------|
| MYSQL | `RDBMS` | Relational DB (MySQL) |
| ORACLE | `RDBMS` | Relational DB (Oracle) |
| POSTGRESQL | `RDBMS` | Relational DB (PostgreSQL) |
| SQLSERVER | `RDBMS` | Relational DB (SQL Server) |
| CLICKHOUSE | `RDBMS` | Relational DB (ClickHouse) |
| KAIWUDB | `KAIWUDB` | KaiwuDB (source or target) |
| TDENGINE2X | `TDENGINE` | TDengine time-series |
| TDENGINE3X | `TDENGINE` | TDengine time-series |
| INFLUXDB1X | `INFLUXDB` | InfluxDB time-series |
| INFLUXDB2X | `INFLUXDB` | InfluxDB time-series |
| OPENTSDB | `OPENTSDB` | OpenTSDB time-series |
| MONGODB | `MONGODB` | MongoDB document |
| FTP | `FTP` | File transfer |
| HDFS | `HDFS` | Hadoop filesystem |

---

## Per-Source Configuration Templates

### Relational Sources (MYSQL, ORACLE, POSTGRESQL, SQLSERVER, CLICKHOUSE)

**sourceType for migration**: `RDBMS`

```json
{
  "engine": "RELATIONAL",
  "type": "MYSQL",
  "host": "127.0.0.1",
  "port": 3306,
  "username": "root",
  "password": "secret",
  "dbName": "source_database"
}
```

**Table-Level Mapping** (for build API):
```json
{
  "source": {
    "sourceType": "RDBMS",
    "table": "users",
    "column": "*"
  },
  "target": {
    "sourceType": "KAIWUDB",
    "table": "users",
    "column": "*",
    "writeMode": "insert"
  }
}
```

**RDBMS-specific options** (in source config):
- `splitPk`: Primary key column for splitting (enables parallel reads)
- `where`: SQL WHERE clause for filtering source data
- `querySql`: Custom SQL query (overrides table + column)

### KaiwuDB Source

**sourceType for migration**: `KAIWUDB`

```json
{
  "engine": "RELATIONAL",
  "type": "KAIWUDB",
  "host": "127.0.0.1",
  "port": 26257,
  "username": "root",
  "password": "secret",
  "dbName": "source_kwdb"
}
```

**Table-Level Mapping**:
```json
{
  "source": {
    "sourceType": "KAIWUDB",
    "table": "source_table",
    "column": "*",
    "writeMode": "read"
  },
  "target": {
    "sourceType": "KAIWUDB",
    "table": "target_table",
    "column": "*",
    "writeMode": "insert"
  }
}
```

**KAIWUDB-specific options**:
- `writeMode`: "read" for source, "insert" for target
- `preSql`: SQL to execute before migration
- `postSql`: SQL to execute after migration

### Time Series Sources (TDENGINE, INFLUXDB, OPENTSDB)

**sourceType for migration**: `TDENGINE`, `INFLUXDB`, or `OPENTSDB`

```json
{
  "engine": "TIMESERIES",
  "type": "TDENGINE3X",
  "host": "127.0.0.1",
  "port": 6030,
  "username": "root",
  "password": "secret",
  "dbName": "source_ts"
}
```

**Table-Level Mapping**:
```json
{
  "source": {
    "sourceType": "TDENGINE",
    "table": "sensor_data",
    "column": "*",
    "beginDateTime": "2024-01-01 00:00:00",
    "endDateTime": "2024-12-31 23:59:59"
  },
  "target": {
    "sourceType": "KAIWUDB",
    "table": "sensor_data",
    "column": "*",
    "writeMode": "insert"
  }
}
```

**Time Series-specific options**:
- `beginDateTime`: Start of time range (ISO format)
- `endDateTime`: End of time range (ISO format)

### MongoDB Source

**sourceType for migration**: `MONGODB`

```json
{
  "engine": "DOCUMENT",
  "type": "MONGODB",
  "host": "127.0.0.1",
  "port": 27017,
  "username": "root",
  "password": "secret",
  "dbName": "source_mongo"
}
```

**Table-Level Mapping**:
```json
{
  "source": {
    "sourceType": "MONGODB",
    "collectionName": "users",
    "column": "*",
    "query": "{\"status\": \"active\"}"
  },
  "target": {
    "sourceType": "KAIWUDB",
    "table": "users",
    "column": "*",
    "writeMode": "insert"
  }
}
```

**MongoDB-specific options**:
- `collectionName`: MongoDB collection name
- `query`: JSON query filter
- `column`: Field selection (comma-separated or "*")

### File Sources (FTP, HDFS)

**sourceType for migration**: `FTP` or `HDFS`

```json
{
  "engine": "FILE",
  "type": "FTP",
  "host": "ftp.example.com",
  "port": 21,
  "username": "anonymous",
  "password": "user@example.com"
}
```

**Table-Level Mapping**:
```json
{
  "source": {
    "sourceType": "FTP",
    "path": "/data/export.csv",
    "fieldDelimiter": ",",
    "connectPattern": "",
    "column": "id,name,value"
  },
  "target": {
    "sourceType": "KAIWUDB",
    "table": "import_data",
    "column": "id,name,value",
    "writeMode": "insert"
  }
}
```

**FTP-specific options**:
- `path`: File path on FTP server
- `fieldDelimiter`: Field separator character
- `connectPattern`: FTP connection pattern

**HDFS-specific options**:
- `defaultFS`: Hadoop NameNode URI (e.g., hdfs://namenode:8020)
- `path`: HDFS file path
- `fileType`: File format (csv, json, etc.)

---

## Common Issues

### 1. Port Numbers

| Source Type | Default Port |
|-------------|--------------|
| MySQL | 3306 |
| Oracle | 1521 |
| PostgreSQL | 5432 |
| SQL Server | 1433 |
| ClickHouse | 9000 |
| KaiwuDB | 26257 |
| TDengine | 6030 |
| InfluxDB | 8086 |
| MongoDB | 27017 |
| FTP | 21 |
| HDFS | 8020 |

### 2. Authentication

- Some sources (MongoDB, InfluxDB) may require authentication even with empty username/password
- Ensure database user has SELECT on source and CREATE/INSERT on target
- For FTP: anonymous access may not require credentials

### 3. Schema Requirements

- Target KaiwuDB must have the correct engine (RELATIONAL or TIMESERIES)
- Table structure must match between source and target
- Time-series tables in KWDB require primary tag(s)

---

## Reference

- KDTS API: `references/api-reference.md`
- Type Mapping: `references/type-mapping.md`
- Source Code: `kw-datax-utils/.../constant/SourceTypes.java`
