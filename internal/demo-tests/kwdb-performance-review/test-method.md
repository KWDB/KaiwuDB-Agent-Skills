# Test Method

## Test Layers

1. **Trigger Tests** - Verify skill activates only on appropriate requests
2. **Functional Tests** - Verify correct optimization output
3. **Regression Tests** - Verify anti-patterns are caught
4. **Storage Configuration Optimization Tests** - Verify config tuning workflow

## Execution Order

1. Run trigger tests (should activate / should not activate)
2. Run functional tests with sample queries
3. Run regression prompts
4. Run configuration optimization tests
5. Verify SQL output includes: Intent, Engine Type, Anti-Pattern, Original Query, Optimized Query, Expected Improvement, Validation
6. Verify config output includes: Intent, Pre-Condition Check, Scope, Issues Found (with Risk column), Recommended Changes, Expected Improvement, Validation, Notes

## Pass / Fail Criteria

### Pass

- Correctly identifies time-series vs relational engine
- Detects missing time filter on time-series queries
- Detects fuzzy tag match that bypasses hash index
- Detects SELECT * on time-series
- Detects OFFSET pagination on time-series
- Recommends TIME_BUCKET instead of DATE_TRUNC
- Corrects cross-model join order
- Does NOT suggest CREATE INDEX on time-series tables

### Storage Configuration Optimization Pass Criteria

- Step 5 only activates when user explicitly requests config optimization OR SQL optimization is exhausted
- Confirms memory/disk/CPU resources before suggesting config changes
- Never auto-executes SET CLUSTER SETTING — only provides SQL for user review
- Never uses SHOW CLUSTER SETTINGS — always queries specific settings individually
- Only reviews parameters matching the user's trigger condition (on-demand, not full scan)
- Includes Risk column in Issues Found table
- Warns about group dependencies (Compression Group: 3 params together; Rows Per Block Group: 2 params together)
- Checks ts.compress.last_segment.enabled before ts.mem_segment_size.max_limit for write performance issues
- Notes that ts.last_cache_size.max_limit cannot exceed default (1.0 GiB)
- Includes risk warning when recommending reduced values for memory/CPU-impact parameters

### Storage Configuration Optimization Fail Criteria

- Auto-executes SET CLUSTER SETTING
- Uses SHOW CLUSTER SETTINGS
- Suggests config changes without confirming available resources
- Reviews all parameters instead of only triggered ones
- Misses Risk column in Issues Found table
- Reviews Compression Group parameter without warning about group dependency
- Suggests increasing ts.last_cache_size.max_limit above 1.0 GiB
- Suggests ts.mem_segment_size.max_limit before ts.compress.last_segment.enabled for write performance

### Fail

- Suggests CREATE INDEX for time-series tables
- Misses missing time range filter
- Outputs without Engine Type classification
- Provides optimization without EXPLAIN validation
