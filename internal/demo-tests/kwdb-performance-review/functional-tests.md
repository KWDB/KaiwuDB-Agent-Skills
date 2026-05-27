# Functional Tests

## Test 1: Missing Time Filter on Time-Series

**Input Query:**
```sql
SELECT * FROM device_sensor WHERE device_id = 'D001';
```

**Expected Output:**
- Engine Type: time-series
- Anti-Pattern: Missing time range filter
- Must add: `AND ts >= '...' AND ts < '...'`
- Guardrail: Warn about full partition scan

## Test 2: Fuzzy Tag Match

**Input Query:**
```sql
SELECT * FROM device_sensor
WHERE device_id LIKE 'D00%'
  AND ts >= '2026-04-01';
```

**Expected Output:**
- Anti-Pattern: LIKE prevents hash index usage
- Suggest: Exact equality or IN list
- Must NOT suggest: CREATE INDEX

## Test 3: SELECT * on Time-Series

**Input Query:**
```sql
SELECT * FROM sensor_data WHERE ts >= '2026-04-01';
```

**Expected Output:**
- Anti-Pattern: SELECT * wastes columnar IO
- Suggest: Explicit column list

## Test 4: OFFSET Pagination

**Input Query:**
```sql
SELECT ts, temperature FROM sensor_data
WHERE device_id = 'D001'
ORDER BY ts LIMIT 20 OFFSET 10000;
```

**Expected Output:**
- Anti-Pattern: OFFSET scans 10020 rows
- Suggest: Time-based cursor pagination

## Test 5: Manual Date Truncation

**Input Query:**
```sql
SELECT DATE_TRUNC('hour', ts), AVG(temp)
FROM sensor_data WHERE ts >= NOW() - INTERVAL '7 days'
GROUP BY DATE_TRUNC('hour', ts);
```

**Expected Output:**
- Anti-Pattern: Manual truncation bypasses optimization
- Suggest: TIME_BUCKET function

## Test 6: Cross-Model Join Order

**Input Query:**
```sql
SELECT s.ts, s.temp, d.name
FROM sensor_data s
JOIN devices d ON s.device_id = d.id
WHERE d.group_id = 'G001';
```

**Expected Output:**
- Anti-Pattern: Time-series as driver
- Suggest: devices as driver table with time filter

## Test 7: Relational Missing Index

**Input Query:**
```sql
SELECT * FROM orders WHERE customer_email = 'test@example.com';
```

**Expected Output:**
- Engine Type: relational
- Suggest: CREATE INDEX on customer_email
- Note: This is a relational table (verify first!)

## Test 8: Function on Time Column

**Input Query:**
```sql
SELECT * FROM sensor_data
WHERE DATE_TRUNC('day', ts) = '2026-04-01';
```

**Expected Output:**
- Anti-Pattern: Function prevents partition pruning
- Suggest: Direct time range comparison

tor## Test 9: Storage Configuration Optimization - Memory Pressure

**Input:**
"我的KWDB内存占用过大，32 GiB总内存只剩2 GiB空闲，想通过配置优化减少内存使用。当前 ts.block.lru_cache.max_limit = 4.0 GiB, ts.last_cache_size.max_limit = 1.0 GiB"

**Expected Output:**
- Step: Step 5 (Storage Configuration Optimization)
- Trigger Condition: memory usage too high
- Reviewed Parameters: ts.block.lru_cache.max_limit, ts.last_cache_size.max_limit
- Pre-Condition Check: 32 GiB total, ~2 GiB free — confirmed
- Scope table includes both cache parameters
- Issues Found table includes Risk column with "database read/write performance may degrade" / "last query cache hit rate may decrease"
- Recommended Changes: decrease lru_cache (e.g., 2.0 GiB), decrease last_cache (e.g., 512 MiB)
- Must NOT auto-execute SET CLUSTER SETTING
- Must NOT use SHOW CLUSTER SETTINGS

## Test 10: Storage Configuration Optimization - Compression Tuning

**Input:**
"磁盘空间快满了，CPU还有余量，想调整压缩配置节省空间。当前 ts.compress.algorithm = lz4, ts.compress.level = medium, ts.compress.stage = 3"

**Expected Output:**
- Step: Step 5 (Storage Configuration Optimization)
- Trigger Condition: disk space reduction needed
- Reviewed Parameters: ts.compress.stage, ts.compress.algorithm, ts.compress.level (Compression Group — all 3 together)
- Pre-Condition Check: CPU and disk space status confirmed
- Decision Tree: "Disk space priority, CPU sufficient → algorithm=zstd, level=high, stage=3"
- Must warn that all 3 Compression Group parameters have dependencies and must be reviewed together
- Risk: "Maximum compression may reduce write throughput by 40-60%"

## Test 11: Storage Configuration Optimization - Query Performance

**Input:**
"查询性能需要优化，集群32 GiB内存，约20 GiB空闲。当前 ts.block.lru_cache.max_limit = 1.0 GiB"

**Expected Output:**
- Step: Step 5 (Storage Configuration Optimization)
- Trigger Condition: optimize query performance
- Reviewed Parameters: ts.block.lru_cache.max_limit
- Pre-Condition Check: 32 GiB total, ~20 GiB free — confirmed sufficient
- Recommended Changes: increase lru_cache (e.g., 2.0-4.0 GiB)
- Risk: "Increased memory usage"
- Must confirm free memory before suggesting increase (Guardrail #8)

## Test 12: Storage Configuration Optimization - Write Performance

**Input:**
"写入性能慢，HDD硬盘，想优化一下。"

**Expected Output:**
- Step: Step 5 (Storage Configuration Optimization)
- Trigger Condition: optimize write performance
- Reviewed Parameters: ts.compress.last_segment.enabled (first), then ts.mem_segment_size.max_limit (if needed)
- Decision Tree: "Write performance → ts.compress.last_segment.enabled (HDD: true)"
- Must check ts.compress.last_segment.enabled BEFORE ts.mem_segment_size.max_limit
- Important note: "When write performance is slow, consider this parameter first, rather than ts.mem_segment_size.max_limit"

## Test 13: SQL + Config Hybrid

**Input:**
"优化这个查询：SELECT * FROM sensor_data WHERE device_id LIKE '%D00%'"
(with follow-up: "SQL优化后查询还是有点慢，还能再快吗？32 GiB内存，20 GiB空闲")

**Expected Output:**
- Steps 1-4: Identify anti-patterns (missing time filter, fuzzy tag, SELECT *)
- Step 5: After SQL optimization, user still reports slow performance → Storage Configuration Optimization
- Trigger Condition: SQL optimization exhausted + query performance
- Reviewed Parameters: ts.block.lru_cache.max_limit
- Pre-Condition Check: memory sufficient (20 GiB free)
- Recommended Changes: increase lru_cache to improve query performance
