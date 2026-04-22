# Time Series DDL Reference

KWDB time series database and table creation patterns.

## Create Time Series Database

```sql
CREATE TS DATABASE database_name;
```

## Create Time Series Table

```sql
CREATE TABLE database_name.table_name (
    ts TIMESTAMP NOT NULL,           -- Timestamp column (required, must be first)
    column1 data_type,               -- Data column
    column2 data_type
) TAGS (
    tag1 data_type NOT NULL,        -- Tag column (device identifier)
    tag2 data_type
) PRIMARY TAGS (tag1);
```

### Example: Sensor Table

```sql
CREATE TABLE ts_db.sensors (
    ts TIMESTAMP NOT NULL,
    temperature DOUBLE,
    humidity DOUBLE,
    voltage DOUBLE
) TAGS (
    device_id INT NOT NULL,
    location VARCHAR(100),
    device_type VARCHAR(50)
) PRIMARY TAGS (device_id);
```

## Key Concepts

### Timestamp Column
- Must be `TIMESTAMP NOT NULL`
- Must be the first column
- Represents the time when data was recorded

### Tag Columns
- Device identifiers (device_id, location, etc.)
- Used for partitioning and filtering
- Can be indexed for fast lookups

### Data Columns
- Actual measurement values (temperature, humidity, etc.)
- Stored as columns in the table

### Primary Tags
- Used for data partitioning across nodes
- Should be the most frequently queried tag
- One primary tag per table

## Common Data Types

| Type | Description |
|------|-------------|
| `TIMESTAMP` | Date and time with timezone |
| `INT`, `INT4`, `INT8` | Integer numbers |
| `DOUBLE`, `FLOAT4`, `FLOAT8` | Floating point numbers |
| `VARCHAR(n)` | Variable length string |
| `BOOL` | Boolean values |

## Natural Language Mapping

| NL Pattern | SQL Pattern |
|------------|-------------|
| 创建时序数据库 | `CREATE TS DATABASE name` |
| 创建设备表 | `CREATE TABLE ... TAGS (device_id ...)` |
| 创建传感器表 | `CREATE TABLE ... (ts, temperature, humidity)` |
| 添加标签 | `TAGS (tag_name type)` |
| 设置主标签 | `PRIMARY TAGS (tag_name)` |