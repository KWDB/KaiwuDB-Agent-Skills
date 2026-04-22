# Design Spec: kwdb-text2sql-aiot

## Use Case

Convert natural language queries into precise KWDB SQL for AIoT (Artificial Intelligence of Things) scenarios. The skill handles:

- Time-series data queries
- Relational table queries
- Cross-model queries joining time-series and relational tables
- Downsampling, interpolation, and latest value queries

Primary users: developers and operators working with KWDB in IoT monitoring, industrial automation, and smart infrastructure applications.

## Success Criteria

1. **Query Type Routing**: Correctly identify query type (time-series DDL, time-series query, relational, cross-model) with >90% accuracy
2. **SQL Syntax Correctness**: Generated SQL follows KWDB syntax (time_bucket, time_bucket_gapfill, interpolate, etc.)
3. **Schema Accuracy**: When MCP is available, column names match actual database schema
4. **MCP Integration**: Successfully detect MCP availability and use it for schema discovery when present
5. **Fallback Handling**: Gracefully handle MCP unavailability with user-prompted schema or assumed field names

## Non-Goals

- Does not generate ML/AI prediction queries (use KAT for that)
- Does not optimize query performance (that's kwdb-performance-review)
- Does not handle schema design (that's kwdb-schema-design)
- Does not support other database dialects (MySQL, PostgreSQL, etc.)

## Dependencies

- KWDB documentation (docs/sql-reference/)
- kwdb-mcp-server (optional but recommended for schema accuracy)
  - read-query tool for SQL execution
  - kwdb://product_info, kwdb://db_info/{db}, kwdb://table/{table} resources
- kwdb-schema-design skill for DDL generation scenarios

## Pattern Choice

### Routing-Based Architecture

```
User NL Query
      │
      ▼
┌─────────────────┐
│ MCP Available?  │──No──→ Ask user for schema OR use assumed fields
└────────┬────────┘
         │Yes
         ▼
┌─────────────────┐
│ Get Database    │
│  (ask user)     │
└────────┬────────┘
         ▼
┌─────────────────┐
│ List Tables     │──kwdb://db_info/{db}
└────────┬────────┘
         ▼
┌─────────────────┐
│ Identify Target │──keyword matching + user confirmation
│ Table(s)        │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Get Column      │──kwdb://table/{table}
│ Schema          │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Route Query     │──scenarios.md decision tree
│ Type            │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Generate SQL    │──reference files for syntax
│ with Schema     │
└─────────────────┘
```

### Query Type Routing (from scenarios.md)

1. **Latest Value**: NL mentions "最近"/"latest"/"最新"
2. **Window/Event**: NL mentions sliding window/session/event
3. **Interpolation**: NL mentions "填充"/"fill"/"gap"/"插值"
4. **Downsampling**: NL mentions "每小时"/"每天" + aggregate
5. **Cross-Model**: JOIN time-series + relational tables
6. **Relational**: Default for standard SQL

### Reference File Selection

| Scenario | Primary Reference |
|----------|-------------------|
| Query Routing (entry) | scenarios.md |
| TS DDL | ts-ddl.md |
| Downsampling | ts-downsampling.md (time_bucket) |
| Interpolation | ts-interpolation.md (time_bucket_gapfill + interpolate) |
| Latest Value | ts-latest-value.md (first/last/last_row) |
| Window/Event | ts-window-events.md (TIME_WINDOW, SESSION_WINDOW, EVENT_WINDOW, TWA, diff) |
| Relational | relational.md |
| Cross-Model | cross-model.md |
| Function Lookup | functions.md |
| MCP Integration | mcp-integration.md |

## Key Design Decisions

1. **MCP is optional but recommended**: Without MCP, skill falls back to user-provided or assumed schema
2. **Explicit database name**: User must confirm database name even with MCP available (supports multi-database)
3. **Candidate table disambiguation**: Multiple matching tables require user confirmation
4. **Preserve original NL context**: Keep user-provided field names as comments in generated SQL for verification
