# Test Method

## Test Layers

1. **Trigger Tests** - Verify skill activates only on appropriate requests
2. **Functional Tests** - Verify correct optimization output
3. **Regression Tests** - Verify anti-patterns are caught

## Execution Order

1. Run trigger tests (should activate / should not activate)
2. Run functional tests with sample queries
3. Run regression prompts
4. Verify output includes: Intent, Engine Type, Anti-Pattern, Original Query, Optimized Query, Expected Improvement, Validation

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

### Fail

- Suggests CREATE INDEX for time-series tables
- Misses missing time range filter
- Outputs without Engine Type classification
- Provides optimization without EXPLAIN validation
