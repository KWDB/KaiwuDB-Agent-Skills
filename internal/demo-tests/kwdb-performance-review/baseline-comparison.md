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

**Baseline might output optimized query but no validation.

**Current target must:**
"Include EXPLAIN validation step to verify improvement."

### Baseline Issue 4: OFFSET Recommendation

**Prompt:** "My pagination is slow."

**Baseline might say:**
"Use LIMIT/OFFSET with appropriate values."

**Current target must:**
"Strongly warn against OFFSET, recommend cursor-based pagination."

## What Must Stay Consistent

1. Output format: Intent, Engine Type, Anti-Pattern, Original, Optimized, Expected, Validation
2. Guardrails must be followed (especially no INDEX on time-series)
3. Time-series queries MUST have time filter emphasized
4. EXPLAIN validation should be included
