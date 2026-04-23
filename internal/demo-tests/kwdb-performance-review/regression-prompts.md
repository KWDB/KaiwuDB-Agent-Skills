# Regression Prompts

These prompts test edge cases and common mistakes.

## Regression 1: Time-Series with Index Suggestion

**Prompt:**
"My time-series query is slow: SELECT * FROM sensor_data WHERE device_id = 'D001'. Should I add an index?"

**Must NOT:**
- Suggest CREATE INDEX on time-series table
- Must explain: time-series tables don't support secondary indexes

**Must:**
- Explain the real issue: missing time filter
- Explain partition pruning and tag hash index

## Regression 2: Ambiguous Table Type

**Prompt:**
"Why is my query slow: SELECT * FROM metrics WHERE status = 'active';"

**Must:**
- Ask or determine if table is time-series or relational
- Cannot assume either way without table definition context

## Regression 3: Mixed Performance Request

**Prompt:**
"Help me optimize this database: I need faster queries AND better schema design."

**Must:**
- Only handle the query optimization part
- Clearly scope to performance review
- Suggest kwdb-schema-design for schema portion

## Regression 4: Very Large OFFSET

**Prompt:**
"My paginated API is slow: SELECT * FROM sensor_data ORDER BY ts LIMIT 20 OFFSET 5000000;"

**Must:**
- Warn about massive OFFSET
- Strongly recommend cursor-based pagination
- Show how to implement time-based cursor

## Regression 5: Partial Tag Filter

**Prompt:**
"Optimize: SELECT * FROM sensor_data WHERE ts >= '2026-04-01' AND location = 'Beijing';"
(Assuming PRIMARY TAGS = 'device_id, location')

**Must:**
- Check if device_id is missing
- Warn that only location tag is filtered, device_id is not
- All PRIMARY TAGS should ideally be specified

## Regression 6: Multiple Time Ranges

**Prompt:**
"SELECT * FROM sensor_data WHERE ts >= '2026-04-01' AND ts <= '2026-03-01';"

**Must:**
- Catch the logical error (ts >= '2026-04-01' AND ts <= '2026-03-01' is impossible)
- Point out the date range is backwards
