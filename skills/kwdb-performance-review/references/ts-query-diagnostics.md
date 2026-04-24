# TS Query Diagnostics

Lookup tables for diagnosing slow time-series queries in KWDB.
Run `EXPLAIN <query>` via MCP, then match indicators against the tables below.

## EXPLAIN Indicator Table

| EXPLAIN Pattern | Meaning | Severity | Action |
|-----------------|---------|----------|--------|
| `Partition Filter: ts [range]` | Time pruning working | Normal | None |
| `Partition Filter: None` | No time range filter | Critical | Add `WHERE ts >= ... AND ts < ...` |
| `Tag Filter: tag = value` | Hash index hit on PRIMARY TAG | Normal | None |
| `Tag Filter: tag ~~ pattern` | LIKE/fuzzy on tag — hash index bypassed | Critical | Replace with exact equality or `IN` list |
| `TsScan` or `TsIndexScan` | Time-series access path used | Normal | None |
| `Scan` (generic) on TS table | Optimizer did not recognize TS path | Warning | Check query syntax; verify table is TIME SERIES TABLE |
| `TsAggregate` pushed to partition | Partition-level aggregation working | Normal | None |
| `Aggregate` above scan | Aggregation not pushed down | Warning | Check `ts.partition_agg.enabled`; simplify agg expression |
| `Distribute: Local` | Data on same node | Normal | None |
| `Distribute: Shuffle` | Cross-node data movement | Warning | Check if time+tag filters can localize access |

## Slow Query Pattern Table

| Pattern | Symptom | Root Cause | Fix |
|---------|---------|------------|-----|
| Full partition scan | Latency scales with total data, not filtered range | Missing time range filter | Add `WHERE ts >= ... AND ts < ...` |
| Aggregation without pushdown | count/sum slow even on narrow range | `ts.partition_agg.enabled = false` or non-pushable expression | Set `ts.partition_agg.enabled = true`; use simple count/sum/max/min |
| Last-row slow | `LAST_ROW(...)` or last-value pattern slow | `ts.last_cache_size.max_limit` too small | Increase last cache size |
| Tag cardinality explosion | GROUP BY on tag causes memory pressure | High-cardinality tag column (thousands of distinct values) | Narrow tag filter before grouping; consider if column should be attribute |
| SELECT * waste | Slow reads on wide TS table | Columnar storage reads all columns | Specify only needed columns in SELECT |
| OFFSET pagination | Deep pages get progressively slower | OFFSET reads and discards N rows | Use time-based cursor: `WHERE ts > last_ts LIMIT n` |
| Manual GROUP BY time | Aggregation slower than expected | `DATE_TRUNC`/manual bucketing misses pushdown | Use `TIME_BUCKET(ts, interval)` |

## Partition Pruning Checklist

| Check | Pass Condition | Fail Action |
|-------|---------------|-------------|
| Time range in WHERE | `ts >= ... AND ts < ...` present | Add time range filter |
| Tag filter type | Equality (`=` or `IN`) on tag columns | Rewrite fuzzy/range filters as equality |
| Time range width | Narrow enough to hit few partitions | Narrow the range; wide ranges degrade to full scan |
| No function on time column | Direct comparison on `ts` | Rewrite `DATE_TRUNC('day', ts) = ...` as `ts >= ... AND ts < ...` |

## Tag Filter Rules

| Rule | Correct | Incorrect |
|------|---------|-----------|
| Exact match | `WHERE hostname = 'host_1'` | `WHERE hostname LIKE 'host_%'` |
| No function on tag | `WHERE hostname = 'host_1'` | `WHERE SUBSTRING(hostname,1,5) = 'host_'` |
| No function on tag | `WHERE hostname = 'host_1'` | `WHERE LOWER(hostname) = 'host_1'` |
| IN list for multiple | `WHERE hostname IN ('host_1','host_2')` | `WHERE hostname = 'host_1' OR hostname = 'host_2'` |
| All PRIMARY TAGS specified | `WHERE device_id = 'D001' AND location = 'BJ'` | `WHERE location = 'BJ'` (missing first tag) |

## Cross-Model JOIN Rules

When a query joins time-series and relational tables:

| Pattern | Correct | Why |
|---------|---------|-----|
| Driver table | Small relational table drives | Time-series as driver causes full partition scan |
| Time filter | Add `WHERE ts >= ...` on TS side | Without it, TS table scans all partitions |
| Pre-aggregate | Aggregate TS first, then JOIN | Avoids row-by-row lookups into TS table |
