# KWDB MCP Server Integration

This guide describes how to use kwdb-mcp-server to automatically discover database schema and generate accurate SQL from natural language.

## MCP Resources

### kwdb://product_info

Returns general KWDB product information including version and capabilities.

**Response fields:**
- `version` - KWDB version string
- `capabilities` - List of supported features

### kwdb://db_info/{database_name}

Returns information about a specific database.

**Response fields:**
- `database_name` - Name of the database
- `engine_type` - Storage engine type (tsdb/rdb)
- `comment` - Database description
- `tables` - Array of table names in the database

**Usage:**
```
Read resource: kwdb://db_info/{database_name}
```
If MCP is available but database_name is unknown, first query `kwdb://product_info` or ask the user.

### kwdb://table/{table_name}

Returns detailed schema for a specific table.

**Response fields:**
- `table_name` - Name of the table
- `columns` - Array of column definitions
  - Each column has: `name`, `type`, `nullable`, `primary_key`, `default_value`
- `table_type` - Table type (TIME SERIES or relational)
- `comment` - Table description
- `storage_engine` - Storage engine used
- `primary_key` - Primary key columns
- `indexes` - List of indexes on the table
- `partition_info` - Partition configuration
- `read_example_queries` - Example SELECT queries for reference
- `write_example_queries` - Example INSERT/UPDATE queries

**Usage:**
```
Read resource: kwdb://table/{table_name}
```

## MCP Tools

### read-query

Executes read-only SQL queries (SELECT, SHOW, EXPLAIN).

**Parameters:**
- `sql` (required) - The SQL query to execute

**Returns:**
```json
{
  "status": "success",
  "type": "query_result",
  "data": {
    "result_type": "table",
    "columns": ["col1", "col2"],
    "rows": [{"col1": "val1", "col2": "val2"}],
    "metadata": {
      "row_count": 1,
      "query": "SELECT ...",
      "auto_limited": false
    }
  }
}
```

**Note:** SELECT queries without LIMIT automatically get `LIMIT 20` added to prevent large result sets. Check `metadata.auto_limited` to detect this.

## Workflow: Schema-Aware SQL Generation

### Step 1: Detect MCP Availability

When the skill activates, check if kwdb-mcp-server is available by attempting to read a resource.

### Step 2: Get Database Name (if not provided)

Ask the user which database to query, or get list from `kwdb://db_info/*` pattern.

### Step 3: Discover Tables

Read `kwdb://db_info/{database_name}` to get all tables in the database.

### Step 4: Match Candidate Tables

Based on natural language keywords, identify candidate tables:
- "设备" / "device" / "传感器" / "sensor" → tables with device/sensor in name
- "温度" / "temperature" → tables with temperature-related columns
- "历史" / "history" → time-series tables

If multiple tables match, ask the user to confirm.

### Step 5: Get Table Schema

For each candidate table, read `kwdb://table/{table_name}` to get column definitions.

### Step 6: Map NL to Schema

Map natural language field references to actual column names:
- "时间" / "timestamp" → ts column
- "设备ID" / "device_id" → tag columns
- "温度" / "temperature" → measurement columns

### Step 7: Generate SQL

Use the schema information to construct accurate SQL.

## Example

**User query:** "查询最近24小时每台设备的平均温度"

**MCP-assisted workflow:**

1. Ask user for database name → "iot_db"

2. Read `kwdb://db_info/iot_db` → returns tables: ["devices", "sensor_data", "alarms"]

3. Identify candidate tables: "sensor_data" likely contains temperature readings

4. Read `kwdb://table/sensor_data`:
```json
{
  "table_name": "sensor_data",
  "table_type": "TIME SERIES",
  "columns": [
    {"name": "ts", "type": "TIMESTAMP", "nullable": false},
    {"name": "temperature", "type": "DOUBLE"},
    {"name": "humidity", "type": "DOUBLE"}
  ],
  "primary_key": ["ts"],
  "tags": ["device_id"]
}
```

5. Read `kwdb://table/devices`:
```json
{
  "table_name": "devices",
  "table_type": "relational",
  "columns": [
    {"name": "device_id", "type": "INT", "nullable": false},
    {"name": "device_name", "type": "VARCHAR"},
    {"name": "location", "type": "VARCHAR"}
  ],
  "primary_key": ["device_id"]
}
```

6. Generate SQL:
```sql
SELECT d.device_name,
       d.location,
       AVG(s.temperature) AS avg_temp
FROM devices d
INNER JOIN (
    SELECT device_id,
           AVG(temperature) AS temperature
    FROM sensor_data
    WHERE ts >= NOW() - INTERVAL '24 hour'
    GROUP BY device_id
) s ON d.device_id = s.device_id
GROUP BY d.device_name, d.location
ORDER BY d.device_name;
```

## Fallback: No MCP Available

When kwdb-mcp-server is not available:

1. Ask user to manually provide table structure
2. Or generate SQL with placeholder column names and mark as "assumed schema"
3. User should verify and adjust the generated SQL

## MCP Detection Pattern

To check if MCP is available, attempt to read `kwdb://product_info`:

```
Read resource: kwdb://product_info
```

If this fails or returns an error, MCP is unavailable.
