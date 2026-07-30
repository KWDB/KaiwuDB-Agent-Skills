# Type Mapping Reference

Data type mapping between source databases and KaiwuDB.

## Mapping Principles

1. **Exact match**: Use same type name when available (VARCHAR, INT, BIGINT)
2. **Functional equivalent**: Use type with same behavior (DATETIME → TIMESTAMP)
3. **Precision preservation**: Keep source precision where possible
4. **Fallback**: Use flexible type (VARCHAR/TEXT) for unmappable types

---

## Relational Database Type Mapping

### MySQL → KaiwuDB

| MySQL | KaiwuDB | Notes |
|-------|---------|-------|
| TINYINT | TINYINT | 1 byte signed |
| SMALLINT | SMALLINT | 2 bytes signed |
| MEDIUMINT | INT | 3 bytes → 4 bytes, minor precision loss |
| INT | INT | 4 bytes signed |
| INTEGER | INT | Same |
| BIGINT | BIGINT | 8 bytes signed |
| FLOAT | FLOAT | 4 bytes |
| DOUBLE | DOUBLE | 8 bytes |
| DECIMAL(p,s) | DECIMAL(p,s) | Fixed precision |
| NUMERIC(p,s) | DECIMAL(p,s) | Same |
| CHAR(n) | CHAR(n) | Fixed string |
| VARCHAR(n) | VARCHAR(n) | Variable string |
| TINYTEXT | VARCHAR(255) | |
| TEXT | VARCHAR(65535) | |
| MEDIUMTEXT | TEXT | |
| LONGTEXT | TEXT | |
| BINARY(n) | BINARY(n) | Fixed binary |
| VARBINARY(n) | VARBINARY(n) | Variable binary |
| TINYBLOB | VARBINARY(255) | |
| BLOB | VARBINARY(65535) | |
| MEDIUMBLOB | BLOB | |
| LONGBLOB | BLOB | |
| DATE | DATE | 'YYYY-MM-DD' |
| DATETIME | DATETIME | 'YYYY-MM-DD HH:MM:SS' |
| TIMESTAMP | TIMESTAMP | Same precision |
| TIME | TIME | 'HH:MM:SS' |
| YEAR | SMALLINT | |
| ENUM | VARCHAR(n) | String values |
| SET | VARCHAR(n) | Comma-separated |
| JSON | VARCHAR(MAX) | String representation |

### Oracle → KaiwuDB

| Oracle | KaiwuDB | Notes |
|--------|---------|-------|
| NUMBER(p,0) | BIGINT | Integer |
| NUMBER(p,s) | DECIMAL(p,s) | Fixed point |
| NUMBER(p,0) float | FLOAT | Approximate |
| BINARY_FLOAT | FLOAT | 4 bytes |
| BINARY_DOUBLE | DOUBLE | 8 bytes |
| VARCHAR2(n) | VARCHAR(n) | |
| NVARCHAR2(n) | VARCHAR(n) | Unicode |
| CHAR(n) | CHAR(n) | |
| NCHAR(n) | CHAR(n) | Unicode |
| CLOB | TEXT | Character large object |
| NCLOB | TEXT | Unicode CLOB |
| BLOB | BLOB | Binary large object |
| RAW(n) | VARBINARY(n) | |
| LONG | TEXT | Deprecated Oracle type |
| LONG RAW | BLOB | Deprecated |
| DATE | DATETIME | Oracle DATE has time component |
| TIMESTAMP(n) | TIMESTAMP | Fractional seconds |
| TIMESTAMP WITH TIME ZONE | VARCHAR(32) | Timezone as string |
| INTERVAL YEAR TO MONTH | VARCHAR(32) | String representation |
| INTERVAL DAY TO SECOND | VARCHAR(32) | String representation |
| XMLTYPE | TEXT | String representation |
| SDO_GEOMETRY | BLOB | Spatial type as binary |

### PostgreSQL → KaiwuDB

| PostgreSQL | KaiwuDB | Notes |
|------------|---------|-------|
| SMALLINT | SMALLINT | 2 bytes |
| INTEGER | INT | 4 bytes |
| BIGINT | BIGINT | 8 bytes |
| DECIMAL(p,s) | DECIMAL(p,s) | |
| NUMERIC(p,s) | DECIMAL(p,s) | |
| REAL | FLOAT | 4 bytes |
| DOUBLE PRECISION | DOUBLE | 8 bytes |
| SMALLSERIAL | SMALLINT | Auto-increment |
| SERIAL | INT | Auto-increment |
| BIGSERIAL | BIGINT | Auto-increment |
| CHAR(n) | CHAR(n) | |
| VARCHAR(n) | VARCHAR(n) | |
| TEXT | TEXT | Unlimited |
| BYTEA | BLOB | Binary |
| DATE | DATE | |
| TIMESTAMP(n) | DATETIME | Without time zone |
| TIMESTAMPTZ | DATETIME | With timezone info lost |
| TIME(n) | TIME | |
| TIMETZ | VARCHAR(16) | Timezone as string |
| INTERVAL | VARCHAR(32) | String representation |
| BOOLEAN | TINYINT | 0/1 |
| POINT | VARCHAR(64) | "(x,y)" format |
| LINE | VARCHAR(64) | |
| LSEG | VARCHAR(64) | |
| BOX | VARCHAR(64) | |
| PATH | VARCHAR(256) | |
| POLYGON | VARCHAR(256) | |
| CIRCLE | VARCHAR(64) | |
| CIDR | VARCHAR(64) | IP network |
| INET | VARCHAR(64) | IP address |
| MACADDR | VARCHAR(32) | MAC address |
| JSON | TEXT | String representation |
| JSONB | TEXT | Binary JSON as string |
| ARRAY | TEXT | Comma-separated |
| HSTORE | TEXT | Key-value as string |
| UUID | VARCHAR(36) | |

### SQL Server → KaiwuDB

| SQL Server | KaiwuDB | Notes |
|------------|---------|-------|
| TINYINT | TINYINT | |
| SMALLINT | SMALLINT | |
| INT | INT | |
| BIGINT | BIGINT | |
| BIT | TINYINT | 0/1 |
| DECIMAL(p,s) | DECIMAL(p,s) | |
| NUMERIC(p,s) | DECIMAL(p,s) | |
| MONEY | DECIMAL(19,4) | |
| SMALLMONEY | DECIMAL(10,4) | |
| FLOAT | FLOAT | |
| REAL | FLOAT | 4 bytes |
| CHAR(n) | CHAR(n) | |
| VARCHAR(n) | VARCHAR(n) | |
| NCHAR(n) | CHAR(n) | Unicode |
| NVARCHAR(n) | VARCHAR(n) | Unicode |
| TEXT | TEXT | Deprecated |
| NTEXT | TEXT | Unicode text |
| IMAGE | BLOB | Deprecated |
| BINARY(n) | BINARY(n) | |
| VARBINARY(n) | VARBINARY(n) | |
| DATE | DATE | |
| DATETIME | DATETIME | |
| DATETIME2 | DATETIME | Higher precision if available |
| SMALLDATETIME | DATETIME | Minute precision |
| DATETIMEOFFSET | VARCHAR(32) | Timezone lost |
| TIME | TIME | |
| UNIQUEIDENTIFIER | VARCHAR(36) | GUID |
| TIMESTAMP | VARBINARY(8) | Row version |
| XML | TEXT | String representation |
| HIERARCHYID | BLOB | Binary |
| GEOMETRY | BLOB | Spatial |
| GEOGRAPHY | BLOB | Spatial |
| SQL_VARIANT | VARCHAR(MAX) | |

---

## Time Series Type Mapping

### TDengine → KaiwuDB

| TDengine | KaiwuDB | Notes |
|----------|---------|-------|
| TINYINT | TINYINT | |
| SMALLINT | SMALLINT | |
| INT | INT | |
| BIGINT | BIGINT | |
| FLOAT | FLOAT | |
| DOUBLE | DOUBLE | |
| VARCHAR(n) | VARCHAR(n) | |
| NCHAR(n) | CHAR(n) | |
| BINARY(n) | BINARY(n) | |
| TIMESTAMP | TIMESTAMP | |
| JSON | TEXT | |

**Special Handling**:
- TDengine super tables → KaiwuDB tables with TAGS
- TDengine child tables → identified by tag values
- Device ID/name → primary tag
- Timestamp → TIME column (automatic in KWDB time series)

### InfluxDB → KaiwuDB

| InfluxDB | KaiwuDB | Notes |
|----------|---------|-------|
| integer | BIGINT | |
| float | DOUBLE | |
| boolean | TINYINT | 0/1 |
| string | VARCHAR(n) | |
| timestamp | TIMESTAMP | |

**Special Handling**:
- InfluxDB measurement → KaiwuDB table
- InfluxDB tags → KaiwuDB primary/secondary TAGS
- InfluxDB fields → KaiwuDB value columns
- Timestamp → TIME column

### OpenTSDB → KaiwuDB

| OpenTSDB | KaiwuDB | Notes |
|----------|---------|-------|
| numeric | DOUBLE | OpenTSDB stores everything as float |
| string | VARCHAR(n) | |
| timestamp | TIMESTAMP | |

---

## Special Types Handling

### Unsupported / Complex Types

| Type | Source | Fallback | Notes |
|------|--------|----------|-------|
| GEOMETRY | MySQL/PostGIS | BLOB | Store as binary |
| POINT | MySQL | VARCHAR(64) | "x,y" format |
| LINESTRING | MySQL | VARCHAR(256) | WKT format |
| JSON | MySQL/PostgreSQL | TEXT | String representation |
| ARRAY | PostgreSQL | TEXT | Comma-separated values |
| HSTORE | PostgreSQL | TEXT | Key=value pairs |
| XML | Oracle/SQL Server | TEXT | String representation |
| BFILE | Oracle | BLOB | Binary file content |
| UDT | Oracle/SQL Server | BLOB | User-defined type |

### Auto-Increment / Identity

| Source | KaiwuDB | DDL |
|--------|---------|-----|
| MySQL AUTO_INCREMENT | BIGINT AUTO_INCREMENT | `id BIGINT AUTO_INCREMENT PRIMARY KEY` |
| Oracle IDENTITY | BIGINT | `id BIGINT GENERATED ALWAYS AS IDENTITY` |
| PostgreSQL SERIAL | INT AUTO_INCREMENT | `id INT AUTO_INCREMENT PRIMARY KEY` |
| SQL Server IDENTITY | BIGINT | `id BIGINT AUTO_INCREMENT PRIMARY KEY` |

**Note**: KaiwuDB supports `AUTO_INCREMENT` for numeric primary keys.

### Timestamps with Time Zone

KaiwuDB does NOT store time zone information. Time zone is:
- Converted to UTC during migration
- Stored as UTC timestamp
- Application should handle time zone display

If original time zone is critical:
1. Add a separate column for time zone offset
2. Store timestamp as VARCHAR with zone info
3. Application layer handles conversion

---

## Type Mapping Configuration

### Custom Type Override

If auto-mapping doesn't work, use column-level override:

```json
{
  "tables": [
    {
      "source": {
        "sourceType": "RDBMS",
        "table": "orders",
        "column": "id,birth_date"
      },
      "target": {
        "sourceType": "KAIWUDB",
        "table": "orders",
        "column": "id,birth_date",
        "writeMode": "insert",
        "columnTypeMapping": {
          "birth_date": "TIMESTAMP"
        }
      }
    }
  ]
}
```

### Type Conversion during Migration

Some conversions require runtime handling:

| Source | Target | Action |
|--------|--------|--------|
| VARCHAR → INT | `CAST(column AS INT)` | Ensure valid numbers |
| VARCHAR → DATE | `CAST(column AS DATE)` | Ensure valid dates |
| TIMESTAMP → VARCHAR | `DATE_FORMAT(column, '%Y-%m-%d')` | Format as needed |
| INT → DECIMAL | Implicit | Precision preserved |

---

## Type Size Limits

| KaiwuDB Type | Max Size | Notes |
|--------------|----------|-------|
| CHAR | 255 | Fixed |
| VARCHAR | 65535 | Variable |
| TEXT | 1GB | |
| BLOB | 1GB | |
| DECIMAL | 65 digits | p ≤ 65, s ≤ 30 |
| TAGS | 128 columns | Time series only |
| Primary Tags | 4 | Time series only |

---

## Common Type Mapping Issues

### Issue 1: VARCHAR Too Large

**Problem**: Source has VARCHAR(100000) but KaiwuDB limits to 65535

**Solution**: Map to TEXT type

```sql
-- Source
description VARCHAR(100000)

-- Target
description TEXT
```

### Issue 2: DECIMAL Precision Loss

**Problem**: Source DECIMAL(38,10) → KaiwuDB DECIMAL(38,10) may lose precision

**Check**: KaiwuDB DECIMAL supports up to 65 digits total, 30 fractional

**Solution**: Map to VARCHAR(64) if exact precision required

### Issue 3: BOOLEAN Conversion

**Problem**: Different boolean representations (1/0, true/false, Y/N)

**Solution**:
1. Check source boolean values
2. KaiwuDB uses TINYINT (0=false, 1=true)
3. Add conversion in preSql if needed:
```sql
INSERT INTO target VALUES (CASE WHEN status = 'Y' THEN 1 ELSE 0 END, ...)
```

### Issue 4: Unicode Characters

**Problem**: Source VARCHAR(n) stores multi-byte chars

**Check**: KaiwuDB VARCHAR stores UTF-8, but size limit is in bytes, not chars

**Solution**: Calculate byte size: max_chars × 4 (for UTF-8) ≤ 65535

---

## Best Practices

1. **Preview DDL first**: Always use `/metadata/preview` to check generated DDL
2. **Test with small sample**: Migrate 1 row first to verify types
3. **Check precision**: Ensure NUMERIC/DECIMAL precision preserved
4. **Handle dates explicitly**: Use ISO format for all date/time fields
5. **Document custom mappings**: Keep type mapping records for future migrations
6. **Validate after migration**: Count rows, check min/max values

---

## Reference

- KDTS Type Mapping Source: `kw-datax-utils/.../mapper/`
- KaiwuDB SQL Reference: KaiwuDB documentation
- DataX Type System: Alibaba DataX documentation
