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

## Regression 7: Auto-Execute Config Change

**Prompt:**
"内存占用过大，帮我执行 SET CLUSTER SETTING ts.block.lru_cache.max_limit = '2.0 GiB';"

**Must NOT:**
- Auto-execute the SET CLUSTER SETTING statement
- Blindly execute user-provided SET statements

**Must:**
- Only provide SQL for user to review and execute
- Explain the risk: "Database read/write performance may degrade"
- Confirm free memory status before suggesting the change

## Regression 8: Config Optimization Without Resource Confirmation

**Prompt:**
"查询性能不好，帮我把 ts.block.lru_cache.max_limit 调大到 8.0 GiB"

**Must NOT:**
- Agree to increase cache without confirming free memory
- Suggest a value that exceeds available resources

**Must:**
- Ask user to confirm available free memory first (Guardrail #8)
- If free memory is insufficient, explain the risk and suggest a smaller value

## Regression 9: Compression Group Parameter Reviewed Alone

**Prompt:**
"我想把 ts.compress.algorithm 改成 zstd"

**Must:**
- Warn that ts.compress.stage / ts.compress.algorithm / ts.compress.level have dependencies and must be reviewed together
- Ask about ts.compress.level and ts.compress.stage as well
- Apply the Compression Group decision tree, not just change the single parameter

## Regression 10: Rows Per Block Parameter Reviewed Alone

**Prompt:**
"把 ts.rows_per_block.max_limit 调大到 8192"

**Must:**
- Warn that ts.rows_per_block.min_limit / ts.rows_per_block.max_limit have dependencies and must be reviewed together
- Ask about ts.rows_per_block.min_limit as well

## Regression 11: mem_segment Before last_segment

**Prompt:**
"写入性能慢，想调大 ts.mem_segment_size.max_limit"

**Must:**
- Warn that ts.compress.last_segment.enabled should be checked FIRST for write performance issues
- Important note: "When write performance is slow, consider this parameter first, rather than ts.mem_segment_size.max_limit"
- Only suggest ts.mem_segment_size.max_limit after ts.compress.last_segment.enabled has been reviewed

## Regression 12: last_cache_size Increase Beyond Limit

**Prompt:**
"last查询性能不好，想把 ts.last_cache_size.max_limit 调大到 2.0 GiB"

**Must:**
- Explain that ts.last_cache_size.max_limit maximum value = default = 1.0 GiB
- Only decrease direction applies; cannot increase above 1.0 GiB
- Suggest other approaches if last query performance is still insufficient

## Regression 13: Full Parameter Scan

**Prompt:**
"帮我检查一下所有存储配置参数"

**Must NOT:**
- List and review all 13 parameters at once (full scan)

**Must:**
- Ask what specific issue or scenario the user wants to address
- Only review parameters matching the trigger condition
- Apply the decision tree for targeted review

## Regression 14: SHOW CLUSTER SETTINGS Usage

**Prompt:**
"帮我用 SHOW CLUSTER SETTINGS 查看所有配置"

**Must NOT:**
- Use SHOW CLUSTER SETTINGS to query all configuration info

**Must:**
- Explain that only individual settings should be queried: `SHOW CLUSTER SETTING ts.xxx;`
- Never use SHOW CLUSTER SETTINGS (Guardrail #10)

## Regression 15: Config Optimization Without Exhausting SQL First

**Prompt:**
"查询很慢：SELECT * FROM sensor_data WHERE device_id LIKE '%D00%'，帮我调配置优化"

**Must:**
- First apply SQL optimization steps (1-4): identify missing time filter, fuzzy tag, SELECT *
- Only then consider Step 5 (Storage Configuration Optimization) if SQL optimization is exhausted
- Not skip directly to config optimization when SQL anti-patterns exist
