# Baseline Comparison

## What Baseline Might Output (Incorrect)

### Baseline Issue 1: Missing Engine Detection

**Prompt:** "My sensor query is slow: SELECT * FROM sensor_data WHERE device_id = 'D001';"

**Baseline might say:**
"Add an index on device_id column."

**Current target must:**
"First determine table type. If time-series: explain no-index constraint, check for time filter."

### Baseline Issue 2: Missing Time Filter Warning

**Prompt:** "Why is this query slow?"

**Baseline might say:**
"Suggest some general optimization tips."

**Current target must:**
"Explicitly warn about missing time range filter on time-series queries."

### Baseline Issue 3: No Validation

**Prompt:** "Optimize: SELECT * FROM sensor_data WHERE ts >= '2026-04-01';"

**Baseline might say:**
"Output optimized query but no validation."

**Current target must:**
"Include EXPLAIN validation step to verify improvement."

### Baseline Issue 4: OFFSET Recommendation

**Prompt:** "My pagination is slow."

**Baseline might say:**
"Use LIMIT/OFFSET with appropriate values."

**Current target must:**
"Strongly warn against OFFSET, recommend cursor-based pagination."

### Baseline Issue 5: Auto-executing Configuration Changes

**Prompt:** "内存占用过大，帮我调一下缓存大小"

**Baseline might say:**
"执行 SET CLUSTER SETTING ts.block.lru_cache.max_limit = '2.0 GiB';" (auto-executes the change)

**Current target must:**
"Only provide SQL for user to review and execute. Never auto-execute SET CLUSTER SETTING."

### Baseline Issue 6: Config Optimization Without Resource Confirmation

**Prompt:** "查询性能不好，帮我调大缓存"

**Baseline might say:**
"将 ts.block.lru_cache.max_limit 调大到 4.0 GiB" (without checking free memory)

**Current target must:**
"Confirm available free memory before suggesting cache/memory size increases. Never suggest increases without confirmed free resources (Guardrail #8)."

### Baseline Issue 7: Full Parameter Scan

**Prompt:** "配置优化"

**Baseline might say:**
Lists all 13 parameters and their current values, suggesting a full review.

**Current target must:**
"Only review parameters matching the user's trigger condition (on-demand, not full scan). Ask what specific issue the user wants to address, then apply the decision tree."

### Baseline Issue 8: Missing Risk Warning for Config Changes

**Prompt:** "内存占用过大，需要调低缓存"

**Baseline might say:**
"ts.block.lru_cache.max_limit 调低到 2.0 GiB" (without mentioning performance risk)

**Current target must:**
"Include risk warning: 'Database read/write performance may degrade.' Risk column in Issues Found table must be populated for all config recommendations."

## What Must Stay Consistent

1. Output format: Intent, Engine Type, Anti-Pattern, Original, Optimized, Expected, Validation
2. Guardrails must be followed (especially no INDEX on time-series)
3. Time-series queries MUST have time filter emphasized
4. EXPLAIN validation should be included
5. Config output format: Intent, Pre-Condition Check, Scope, Issues Found (with Risk column), Recommended Changes, Expected Improvement, Validation, Notes
6. Never auto-execute SET CLUSTER SETTING — only provide SQL for user review
7. Never use SHOW CLUSTER SETTINGS — always query specific settings individually
8. Always confirm resources (memory/disk/CPU) before suggesting config changes
9. Always include risk warning for memory/CPU-impact parameter changes
10. Only review triggered parameters, not full scan
