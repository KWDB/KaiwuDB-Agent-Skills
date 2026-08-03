# Configuration Templates

Ready-to-use JSON templates for KDTS migration requests.

---

## 1. DataSource Templates

### 1.1 MySQL Source

```json
{
  "engine": "RELATIONAL",
  "type": "MYSQL",
  "host": "127.0.0.1",
  "port": 3306,
  "username": "root",
  "password": "mysql_password",
  "dbName": "source_database"
}
```

**Alternative with JDBC URL**:

```json
{
  "engine": "RELATIONAL",
  "type": "MYSQL",
  "url": "jdbc:mysql://127.0.0.1:3306/source_database?useSSL=false&serverTimezone=UTC",
  "username": "root",
  "password": "mysql_password",
  "dbName": "source_database"
}
```

### 1.2 Oracle Source

```json
{
  "engine": "RELATIONAL",
  "type": "ORACLE",
  "host": "192.168.1.100",
  "port": 1521,
  "username": "ORACLE_USER",
  "password": "oracle_password",
  "dbName": "ORCL"
}
```

### 1.3 PostgreSQL Source

```json
{
  "engine": "RELATIONAL",
  "type": "POSTGRESQL",
  "host": "192.168.1.101",
  "port": 5432,
  "username": "postgres",
  "password": "pg_password",
  "dbName": "source_db"
}
```

### 1.4 TDengine Source (Time Series)

```json
{
  "engine": "TIMESERIES",
  "type": "TDENGINE3X",
  "host": "192.168.1.103",
  "port": 6030,
  "username": "root",
  "password": "taos_password",
  "dbName": "sensor_db"
}
```

### 1.5 KaiwuDB Target

```json
{
  "engine": "RELATIONAL",
  "type": "KAIWUDB",
  "host": "127.0.0.1",
  "port": 26257,
  "username": "root",
  "password": "kwdb_password",
  "dbName": "target_database"
}
```

**Time Series Target**:

```json
{
  "engine": "TIMESERIES",
  "type": "KAIWUDB",
  "host": "127.0.0.1",
  "port": 26257,
  "username": "root",
  "password": "kwdb_password",
  "dbName": "target_ts"
}
```

---

## 2. Migration Request Templates

### 2.1 Full Database Migration (Relational)

For sources that support full migration: MySQL, Oracle, PostgreSQL, KaiwuDB, ClickHouse.

```json
{
  "source": {
    "type": "MYSQL",
    "host": "192.168.1.100",
    "port": 3306,
    "username": "root",
    "password": "source_password",
    "dbName": "source_database"
  },
  "target": {
    "engine": "RELATIONAL",
    "type": "KAIWUDB",
    "host": "127.0.0.1",
    "port": 26257,
    "username": "root",
    "password": "kwdb_password",
    "dbName": "target_database"
  },
  "tables": [],
  "data": {
    "enable": true,
    "fetchSize": 1000,
    "batchSize": 1000,
    "setting": {
      "speed": {
        "channel": 2
      },
      "errorLimit": {
        "percentage": 0.02
      }
    }
  }
}
```

**Key Points**:

- Empty `tables` array = auto-discover all tables
- `speed.channel` = parallel read/write threads
- `errorLimit.percentage` = % of rows that can fail before stopping

### 2.2 Table-Level Migration

For sources that don't support full migration: SQL Server, TDengine 2.x, InfluxDB 2.x, MongoDB, FTP, HDFS.

```json
{
  "source": {
    "type": "SQLSERVER",
    "host": "192.168.1.102",
    "port": 1433,
    "username": "sa",
    "password": "source_password",
    "dbName": "source_database"
  },
  "target": {
    "engine": "RELATIONAL",
    "type": "KAIWUDB",
    "host": "127.0.0.1",
    "port": 26257,
    "username": "root",
    "password": "kwdb_password",
    "dbName": "target_database"
  },
  "tables": [
    {
      "source": {
        "sourceType": "RDBMS",
        "table": "customers",
        "column": "*"
      },
      "target": {
        "sourceType": "KAIWUDB",
        "table": "customers",
        "column": "*",
        "writeMode": "insert"
      }
    }
  ],
  "data": {
    "enable": true,
    "fetchSize": 1000,
    "batchSize": 1000
  }
}
```

### 2.3 Time Series Migration

```json
{
  "source": {
    "type": "TDENGINE3X",
    "host": "192.168.1.103",
    "port": 6030,
    "username": "root",
    "password": "taos_password",
    "dbName": "sensor_db"
  },
  "target": {
    "engine": "TIMESERIES",
    "type": "KAIWUDB",
    "host": "127.0.0.1",
    "port": 26257,
    "username": "root",
    "password": "kwdb_password",
    "dbName": "sensor_target"
  },
  "tables": [
    {
      "source": {
        "sourceType": "TDENGINE",
        "table": "temperature_readings",
        "column": "*",
        "beginDateTime": "2024-01-01 00:00:00",
        "endDateTime": "2024-12-31 23:59:59"
      },
      "target": {
        "sourceType": "KAIWUDB",
        "table": "temperature_readings",
        "column": "*",
        "writeMode": "insert"
      }
    }
  ],
  "data": {
    "enable": true,
    "fetchSize": 5000,
    "batchSize": 5000
  }
}
```

### 2.4 Migration with WHERE Filter

```json
{
  "source": {
    "type": "MYSQL",
    "host": "192.168.1.100",
    "port": 3306,
    "username": "root",
    "password": "source_password",
    "dbName": "source_db"
  },
  "target": {
    "engine": "RELATIONAL",
    "type": "KAIWUDB",
    "host": "127.0.0.1",
    "port": 26257,
    "username": "root",
    "password": "kwdb_password",
    "dbName": "target_db"
  },
  "tables": [
    {
      "source": {
        "sourceType": "RDBMS",
        "table": "orders",
        "column": "*",
        "where": "order_date >= '2024-01-01' AND status = 'completed'"
      },
      "target": {
        "sourceType": "KAIWUDB",
        "table": "orders_2024",
        "column": "*",
        "writeMode": "insert"
      }
    }
  ],
  "data": {
    "enable": true,
    "fetchSize": 1000,
    "batchSize": 1000
  }
}
```

### 2.5 Parallel Migration with splitPk

```json
{
  "source": {
    "type": "MYSQL",
    "host": "192.168.1.100",
    "port": 3306,
    "username": "root",
    "password": "source_password",
    "dbName": "large_db"
  },
  "target": {
    "engine": "RELATIONAL",
    "type": "KAIWUDB",
    "host": "127.0.0.1",
    "port": 26257,
    "username": "root",
    "password": "kwdb_password",
    "dbName": "target_db"
  },
  "tables": [
    {
      "source": {
        "sourceType": "RDBMS",
        "table": "big_table",
        "column": "*",
        "splitPk": "id"
      },
      "target": {
        "sourceType": "KAIWUDB",
        "table": "big_table",
        "column": "*",
        "writeMode": "insert"
      }
    }
  ],
  "data": {
    "enable": true,
    "fetchSize": 5000,
    "batchSize": 5000,
    "setting": {
      "speed": {
        "channel": 8
      }
    }
  }
}
```

### 2.6 Data-Only Migration (Tables Exist)

Skip DDL steps, go directly to build.

```json
{
  "source": {
    "type": "MYSQL",
    "host": "192.168.1.100",
    "port": 3306,
    "username": "root",
    "password": "source_password",
    "dbName": "source_db"
  },
  "target": {
    "engine": "RELATIONAL",
    "type": "KAIWUDB",
    "host": "127.0.0.1",
    "port": 26257,
    "username": "root",
    "password": "kwdb_password",
    "dbName": "target_db"
  },
  "tables": [
    {
      "source": {
        "sourceType": "RDBMS",
        "table": "existing_table",
        "column": "*"
      },
      "target": {
        "sourceType": "KAIWUDB",
        "table": "existing_table",
        "column": "*",
        "writeMode": "insert"
      }
    }
  ],
  "data": {
    "enable": true,
    "fetchSize": 1000,
    "batchSize": 1000
  }
}
```

---

## 3. Metadata Configuration

Metadata config uses `MetaData` fields from KDTS API. Full field reference:

- `enable` (boolean): Enable metadata extraction, default `true`
- `autoDdl` (boolean): Auto-generate DDL statements, default `true`
- `primaryKey` (boolean): Include primary key definitions, default `true`
- `constraint` (boolean): Include constraint definitions, default `true`
- `comment` (boolean): Include table/column comments, default `true`
- `index` (boolean): Include index definitions, default `true`
- `view` (boolean): Include view definitions, default `false`

### Full Metadata (Slower, Complete)

```json
{
  "enable": true,
  "autoDdl": true,
  "primaryKey": true,
  "constraint": true,
  "comment": true,
  "index": true,
  "view": true
}
```

### Minimal Metadata (Faster)

```json
{
  "enable": true,
  "autoDdl": true,
  "primaryKey": true,
  "constraint": false,
  "comment": false,
  "index": false,
  "view": false
}
```

---

## 4. DDL Execution

### Preview DDL Request

The `sourceDb` field must be a complete `Database` object returned from `/datasource/metadata` API.
Do NOT pass a string - use the full object structure.

```json
{
  "target": {
    "engine": "RELATIONAL",
    "type": "KAIWUDB",
    "host": "127.0.0.1",
    "port": 26257,
    "username": "root",
    "password": "kwdb_password",
    "dbName": "target_db",
    "isTarget": true
  },
  "sourceDb": {
    "type": "MYSQL",
    "name": "source_db",
    "encoding": "UTF-8",
    "tableMap": {
      "users": {
        "tableName": "users",
        "columns": {
          "id": {
            "columnName": "id",
            "dataType": "BIGINT",
            "nullable": false,
            "primaryKey": true
          },
          "name": {
            "columnName": "name",
            "dataType": "VARCHAR(100)",
            "nullable": true
          }
        }
      }
    },
    "viewMap": {}
  },
  "metadata": {
    "primaryKey": true,
    "constraint": true,
    "comment": true,
    "index": true,
    "view": false
  },
  "isTimeSeries": false
}
```

### Execute DDL Request

The `ddlScript` must be a `DdlScript` object returned from `/metadata/preview` API.

```json
{
  "target": {
    "engine": "RELATIONAL",
    "type": "KAIWUDB",
    "host": "127.0.0.1",
    "port": 26257,
    "username": "root",
    "password": "kwdb_password",
    "dbName": "target_db",
    "isTarget": true
  },
  "ddlScript": {
    "dbName": "SOURCE_DB",
    "createDb": "CREATE DATABASE \"SOURCE_DB\"",
    "table": {
      "users": "CREATE TABLE \"users\" (\"id\" BIGINT NOT NULL, \"name\" VARCHAR(100), PRIMARY KEY (\"id\"))"
    },
    "view": {}
  },
  "autoDdl": true
}
```

**Response**: Returns absolute path of executed SQL file, e.g., `/data/kwdb/logs/ddl_20240115_143022.sql`

---

## 5. Task Control

### Query Status

```
GET /kdts/api/v1/datax/status?scriptName=MYSQL2KAIWUDB_1719290000.json
```

### Kill Task

POST /kdts/api/v1/datax/control

```json
{
  "scriptName": "MYSQL2KAIWUDB_1719290000.json",
  "action": "KILL"
}
```

---

## 6. Data Source Compatibility Matrix

| Source Type | Full Migration | Metadata | Time Filter | Custom SQL | Notes                              |
|-------------|----------------|----------|-------------|------------|------------------------------------|
| MYSQL       | Yes            | Yes      | No          | Yes        | Full support                       |
| ORACLE      | Yes            | Yes      | No          | Yes        | Full support                       |
| POSTGRESQL  | Yes            | Yes      | No          | Yes        | Full support                       |
| SQLSERVER   | No             | Yes      | No          | Yes        | Metadata + Data only               |
| CLICKHOUSE  | Yes            | No       | No          | Yes        | Full migration, no metadata        |
| KAIWUDB     | No             | No       | No          | Yes        | Data migration only (as source)    |
| TDENGINE3X  | Yes            | Yes      | Yes         | No         | Full support                       |
| TDENGINE2X  | No             | No       | Yes         | No         | Data migration only                |
| INFLUXDB1X  | No             | Yes      | Yes         | No         | Metadata + Data, no full migration |
| INFLUXDB2X  | No             | Yes      | Yes         | No         | Metadata + Data, no full migration |
| OPENTSDB    | No             | No       | Yes         | No         | Data migration only                |
| MONGODB     | No             | No       | No          | Yes        | Data migration only                |
| FTP         | No             | No       | No          | No         | Data migration only                |
| HDFS        | No             | No       | No          | No         | Data migration only                |

---

## 7. KaiwuDB Time-Series Table Constraints

When migrating to KaiwuDB with TIMESERIES engine, the following constraints apply:

| Constraint                       | Limit     | Error Code | Description                       |
|----------------------------------|-----------|------------|-----------------------------------|
| Maximum columns per table        | 128       | 3004       | Total of Tag + Value columns      |
| Maximum primary tags             | 4         | 3004       | Cannot exceed 4 primary tags      |
| Maximum tag/column name length   | 128 bytes | 3005       | Each name must be within limit    |
| Must have at least 1 primary tag | 1         | 3006       | Required for time-series indexing |

### Solutions for Exceeding Constraints

1. Reduce columns to meet the limit
2. Split data into multiple tables or migrations
3. Convert some primary tags to secondary tags
4. Shorten column names if too long

### Example Time-Series Table Design

```sql
CREATE TABLE sensor_data
(
    ts         TIMESTAMP,
    device_id  INT,          -- Primary tag
    metric     VARCHAR(32),  -- Primary tag
    value      DOUBLE,       -- Value field
    quality    INT           -- Secondary tag
) TAGS(quality);
```

---

## 8. Performance Tips

### Large Data Sets

```json
{
  "data": {
    "enable": true,
    "fetchSize": 5000,
    "batchSize": 5000,
    "setting": {
      "speed": {
        "channel": 4,
        "record": -1
      },
      "errorLimit": {
        "percentage": 0.01
      }
    }
  }
}
```

### Time Series Optimization

```json
{
  "tables": [
    {
      "source": {
        "sourceType": "TDENGINE",
        "table": "sensor_data",
        "column": "*",
        "beginDateTime": "2024-01-01",
        "endDateTime": "2024-06-30"
      },
      "target": {
        "sourceType": "KAIWUDB",
        "table": "sensor_data_2024h1",
        "column": "*",
        "writeMode": "insert"
      }
    }
  ]
}
```

### Error Tolerant Migration

```json
{
  "data": {
    "enable": true,
    "fetchSize": 1000,
    "batchSize": 1000,
    "setting": {
      "speed": {
        "channel": 1
      },
      "errorLimit": {
        "percentage": 5.0,
        "record": 1000
      }
    }
  }
}
```
