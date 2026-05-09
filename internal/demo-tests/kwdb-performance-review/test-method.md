# Test Method

## Test Layers

1. **Trigger Tests** — Verify skill activates only on appropriate requests (configuration tuning keywords) and not on SQL rewriting, schema design, or other out-of-scope requests
2. **Functional Tests** — Verify correct configuration review output for known misconfiguration patterns
3. **Regression Tests** — Verify edge cases and guardrail enforcement (no SQL rewrites, inter-setting dependencies, cache overflow)
4. **Baseline Comparison** — Verify output quality exceeds ad-hoc advice (structured format, current+recommended values, validation)

## Execution Order

1. Run trigger tests: positive cases should activate, negative cases should not
2. Run functional tests with simulated MCP output: verify all 7 output sections are present
3. Run regression prompts: verify guardrails and edge case handling
4. Run baseline comparison: verify output quality vs ad-hoc advice
5. Verify output includes: Intent, Scope, Engine Type, Issues Found, Recommended Changes, Expected Improvement, Validation

## Pass / Fail Criteria

### Pass (all must hold)

- Correctly identifies time-series engine type
- Detects `ts.compress.stage = 0` as Critical
- Detects `ts.compress.algorithm = 'disabled'` as Critical
- Detects `ts.partition_agg.enabled = false` as Critical
- Detects `ts.auto_vacuum.enabled = false` as Critical
- Detects `ts.count.use_statistics.enabled = false` as Critical
- Detects inter-setting dependency issues (e.g., partition_agg without count_statistics)
- Detects cache sizes insufficient for data volume
- Does NOT suggest CREATE INDEX on time-series tables
- Does NOT modify user SQL statements
- Includes verification query for each recommendation
- Shows current value and recommended value for each change
- Classifies issues by severity (Critical/Warning/Info)

### Fail (any of these)

- Suggests CREATE INDEX for time-series tables
- Modifies user SQL statements
- Misses `ts.compress.stage = 0` or `ts.compress.algorithm = 'disabled'`
- Misses `ts.partition_agg.enabled = false`
- Outputs without severity classification
- Provides recommendation without current value and recommended value
- Provides recommendation without verification query
- Ignores inter-setting dependencies
