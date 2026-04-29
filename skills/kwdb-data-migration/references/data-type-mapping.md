# Official Standard Data Type Mapping

## MySQL → KaiwuDB

| MySQL Type      | Relational  | Time-Series | Note          |
|-----------------|-------------|-------------|---------------|
| INT             | INT         | INT         |               |
| BIGINT          | INT8        | INT8        |               |
| BIGINT UNSIGNED | NUMERIC(20) | INT8        | Overflow risk |
| DECIMAL         | DECIMAL     | FLOAT8      |               |
| DATE            | DATE        | TIMESTAMP   |               |
| DATETIME        | TIMESTAMP   | TIMESTAMP   |               |
| TIME            | TIME        | TIMESTAMP   |               |
| VARCHAR         | VARCHAR     | NVARCHAR    |               |
| JSON            | JSON        | NVARCHAR    |               |
| BLOB            | BYTES       | BYTES       |               |

## PostgreSQL → KaiwuDB

| PostgreSQL Type | Relational | Time-Series |
|-----------------|------------|-------------|
| INTEGER         | INT        | INT         |
| BIGINT          | INT8       | INT8        |
| NUMERIC         | DECIMAL    | FLOAT8      |
| TIMESTAMP       | TIMESTAMP  | TIMESTAMP   |
| JSONB           | JSONB      | NVARCHAR    |
| TEXT            | TEXT       | NVARCHAR    |
| BYTEA           | BYTES      | BYTES       |

## Oracle → KaiwuDB

| Oracle Type | Relational  | Time-Series |
|-------------|-------------|-------------|
| NUMBER      | DECIMAL/INT | INT8/FLOAT8 |
| DATE        | TIMESTAMP   | TIMESTAMP   |
| CLOB        | TEXT        | NVARCHAR    |
| BLOB        | BYTES       | BYTES       |

## TDengine → KaiwuDB (Time-Series Only)

| TDengine Type | Time-Series |
|---------------|-------------|
| INT           | INT         |
| BIGINT        | INT8        |
| FLOAT         | FLOAT       |
| DOUBLE        | FLOAT8      |
| TIMESTAMP     | TIMESTAMP   |
| VARCHAR       | NVARCHAR    |
| JSON          | NVARCHAR    |

## InfluxDB → KaiwuDB (Time-Series Only)

| InfluxDB Type | Time-Series |
|---------------|-------------|
| int           | INT8        |
| float         | FLOAT8      |
| string        | NVARCHAR    |
| boolean       | BOOL        |
| time          | TIMESTAMP   |
