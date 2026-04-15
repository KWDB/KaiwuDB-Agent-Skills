# Data Type Reference

Quick reference for KWDB data types. Read when choosing column types.

## Numeric Types

| Type | Bytes | Range | Use When |
|------|-------|-------|----------|
| INT2 | 2 | ±32K | Small counts, ages |
| INT4 (INT) | 4 | ±2.1B | Default integer |
| INT8 (BIGINT) | 8 | ±9.2E18 | Large IDs, counters |
| DECIMAL(p,s) | Variable | Exact | **Money/currency** (ALWAYS) |
| FLOAT4 | 4 | ~7 digits | Low-precision measurements (temp, humidity) |
| FLOAT8 | 8 | ~17 digits | Measurements (default float) |
| BOOL | 1 | true/false | Flags |

## String Types

| Type | Max Length | Use When |
|------|------------|----------|
| VARCHAR(n) | 65,534 | **Default** for text |
| CHAR(n) | 1,023 | Fixed-length codes only |
| JSONB | - | Structured/semi-structured data |
| ARRAY[T] | 1-D | Simple lists (no index support) |
| BLOB | 64MB | Binary files |
| CLOB | 64MB | Long text |

## Time Types

| Type | Use When |
|------|----------|
| TIMESTAMPTZ | **Time-series tables**, timezone matters |
| TIMESTAMP | Business dates without timezone |
| DATE | Date only (no time) |
| TIME | Time only (rare) |

**Precision**: (3)=ms default, (6)=μs, (9)=ns

## Special Types

| Type | Use When |
|------|----------|
| UUID | Distributed IDs, global uniqueness |
| INET | IP addresses |
| GEOMETRY (TS only) | Spatial data (POINT/LINESTRING/POLYGON) |

## Type Selection Quick Table

| Data | Right | Wrong |
|------|-------|-------|
| User IDs | INT8 or UUID | VARCHAR for ID |
| Money | DECIMAL(10,2) | FLOAT/DOUBLE |
| Sensor readings | FLOAT8 | DECIMAL |
| Names | VARCHAR(100) | CHAR(1000) |
| Status codes | VARCHAR(20) or INT | - |
| JSON payloads | JSONB | VARCHAR |
| Timestamps (TS) | TIMESTAMPTZ | DATE |
| Booleans | BOOL | INT ('1'/'0') |

## Common Mistakes

1. **FLOAT for money** → Use DECIMAL(p,s)
2. **VARCHAR without length** → Specify reasonable max
3. **CHAR vs VARCHAR** → VARCHAR unless fixed-length
4. **Timestamp in TS table** → Must be first column, TIMESTAMPTZ

## Time-Series Type Support

| Supported | NOT Supported |
|-----------|---------------|
| TIMESTAMP/TIMESTAMPTZ | - |
| INT, BIGINT, FLOAT | DECIMAL |
| VARCHAR, CHAR, NCHAR | NVARCHAR |
| BOOL, GEOMETRY | JSONB, ARRAY |
