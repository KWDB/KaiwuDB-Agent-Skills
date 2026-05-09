# Functional Tests

## Test 1: Compression Stage Misconfiguration

**Input:** User reports slow time-series queries. MCP shows `ts.compress.stage = 0`.

**Expected Output:**
- Engine Type: time-series
- Issue: `ts.compress.stage = 0` → Severity: Critical
- Recommendation: `SET CLUSTER SETTING ts.compress.stage = 3;`
- Reason: No encoding or compression applied; wastes storage and slows range scans
- Current value: 0, Recommended value: 3

**Guardrail Check:**
- Must NOT suggest SQL rewrites
- Must show current value and recommended value
- Must explain WHY the change works

## Test 2: Compression Algorithm Mismatch

**Input:** User has a write-heavy cluster. MCP shows `ts.compress.algorithm = 'zstd'` and `ts.compress.level = 'high'`.

**Expected Output:**
- Issue: zstd with high level on write-heavy workload → Severity: Warning
- Recommendation: `SET CLUSTER SETTING ts.compress.algorithm = 'lz4';` and optionally `SET CLUSTER SETTING ts.compress.level = 'low';`
- Reason: zstd has high CPU cost for compression; lz4 is better for write-heavy workloads
- Note: existing data retains zstd compression

**Guardrail Check:**
- Must NOT suggest SQL rewrites
- Must explain algorithm change only affects new writes

## Test 3: Partition Aggregation Disabled

**Input:** User reports that COUNT queries on time-series tables are slow. MCP shows `ts.partition_agg.enabled = false` and `ts.count.use_statistics.enabled = false`.

**Expected Output:**
- Issue: `ts.partition_agg.enabled = false` → Severity: Critical
- Issue: `ts.count.use_statistics.enabled = false` → Severity: Critical
- Recommendation: `SET CLUSTER SETTING ts.partition_agg.enabled = true;` and `SET CLUSTER SETTING ts.count.use_statistics.enabled = true;`
- Reason: Both must be true for count optimization; without them, COUNT scans all rows

**Guardrail Check:**
- Must check inter-setting dependency (both settings must be true together)
- Must NOT suggest SQL rewrites like "add an index"

## Test 4: Auto Vacuum Disabled

**Input:** User reports that time-series table size keeps growing. MCP shows `ts.auto_vacuum.enabled = false`.

**Expected Output:**
- Issue: `ts.auto_vacuum.enabled = false` → Severity: Critical
- Recommendation: `SET CLUSTER SETTING ts.auto_vacuum.enabled = true;`
- Reason: Without auto vacuum, stale and deleted data accumulates, causing table bloat

**Guardrail Check:**
- Must NOT suggest SQL rewrites
- Must NOT suggest CREATE INDEX on time-series table

## Test 5: Cache Size Insufficient

**Input:** User has a medium cluster (32 GiB RAM) with many time-series tables. MCP shows all cache sizes at defaults (1.0 GiB, table_cache=1000).

**Expected Output:**
- Issue: `ts.block.lru_cache.max_limit = 1.0 GiB` → Severity: Warning (too small for 32 GiB cluster)
- Issue: `ts.last_cache_size.max_limit = 1.0 GiB` → Severity: Warning
- Issue: `ts.table_cache.capacity = 1000` → Severity: Info (may need increase for many tables)
- Recommendation: Increase cache sizes per memory sizing tiers
- Reason: Default caches are for small clusters; medium clusters need 2-4 GiB caches

**Guardrail Check:**
- Must warn if total cache allocation approaches 50% of available RAM
- Must NOT suggest SQL rewrites

## Test 6: Aggregate Recalculation Disabled

**Input:** User reports that aggregation results seem stale after data modifications. MCP shows `ts.agg_recalc.cycle = 0`.

**Expected Output:**
- Issue: `ts.agg_recalc.cycle = 0` → Severity: Warning
- Recommendation: `SET CLUSTER SETTING ts.agg_recalc.cycle = 1800;`
- Reason: Disabled aggregate recalculation causes stale partition aggregates after data modifications

**Guardrail Check:**
- Must explain the trade-off (recalculation uses background CPU)
- Must NOT suggest SQL rewrites
