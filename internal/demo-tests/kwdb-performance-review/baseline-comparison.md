# Baseline Comparison

## What Baseline Might Output (Incorrect)

### Baseline Issue 1: Suggesting SQL Rewrites

**Prompt:** "My time-series query is slow."

**Baseline might say:**
"Add a time range filter to your query: WHERE ts >= '2026-04-01' AND ts < '2026-04-02'."

**Current target must:**
"Check ts.* settings first. If `ts.partition_agg.enabled = false` or `ts.compress.stage = 0`, fix those before suggesting SQL changes. Do NOT modify user SQL."

### Baseline Issue 2: Suggesting CREATE INDEX

**Prompt:** "My time-series COUNT query is slow."

**Baseline might say:**
"Add an index on the time column or device_id column."

**Current target must:**
"Time-series tables do not support secondary indexes. Check `ts.partition_agg.enabled` and `ts.count.use_statistics.enabled` instead."

### Baseline Issue 3: No Validation

**Prompt:** "Review my ts.* settings."

**Baseline might:**
Output a list of recommended changes without showing current values or verification queries.

**Current target must:**
"Show current value and recommended value for each change. Provide `SHOW CLUSTER SETTING` queries to verify each change took effect."

### Baseline Issue 4: Missing Inter-Setting Dependencies

**Prompt:** "I enabled partition aggregation but COUNT is still slow."

**Baseline might say:**
"Partition aggregation is enabled, so the issue must be elsewhere."

**Current target must:**
"Check both `ts.partition_agg.enabled` AND `ts.count.use_statistics.enabled`. Both must be true for count optimization. If `count_statistics = false`, that is the root cause."

## What Must Stay Consistent

1. **Output format**: Intent, Scope, Engine Type, Issues Found, Recommended Changes, Expected Improvement, Validation
2. **Guardrails followed**: no SQL rewrites, no CREATE INDEX on time-series, always show current+recommended values
3. **Inter-setting dependencies**: must be checked (e.g., partition_agg + count_statistics, compress.algorithm + compress.stage)
4. **Validation included**: every recommendation must have a verification query
5. **Severity classification**: each issue must be Critical, Warning, or Info
