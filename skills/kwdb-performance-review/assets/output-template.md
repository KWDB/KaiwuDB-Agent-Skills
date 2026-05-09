# Output Template

## Intent

[Brief description of what the user wants to achieve — e.g., "Review time-series cluster settings for a write-heavy sensor cluster"]

## Scope

- Cluster settings reviewed: Y/N
- Compression strategy reviewed: Y/N
- Memory and cache sizing reviewed: Y/N

## Engine Type

[time-series / N/A — if target is not a time-series table, state scope boundary]

## Issues Found

| Setting | Severity | Current Value | Recommended Value | Reason |
|---------|----------|---------------|-------------------|--------|
| `ts.compress.stage` | Critical | 0 | 3 | No encoding or compression applied; wastes storage and slows range scans |
| `ts.partition_agg.enabled` | Critical | false | true | Without partition aggregation, count/sum scan all rows |
| ... | ... | ... | ... | ... |

## Recommended Changes

| Setting | SQL |
|---------|-----|
| `ts.compress.stage` | `SET CLUSTER SETTING ts.compress.stage = 3;` |
| `ts.partition_agg.enabled` | `SET CLUSTER SETTING ts.partition_agg.enabled = true;` |
| ... | ... |

## Expected Improvement

[What should change after applying the settings — e.g., "Compression reduces storage by ~60%; partition aggregation reduces COUNT query latency from minutes to seconds"]

## Validation

```sql
-- Verify each setting took effect
SHOW CLUSTER SETTING ts.compress.stage;
SHOW CLUSTER SETTING ts.partition_agg.enabled;
```

---

## Severity Definitions

| Severity | Definition | Example |
|----------|-----------|---------|
| **Critical** | Causes visible performance degradation or data risk | `ts.compress.stage = 0` (no compression), `ts.auto_vacuum.enabled = false` (stale data accumulation) |
| **Warning** | Suboptimal under load | `ts.compress.algorithm = 'zstd'` on write-heavy workload (CPU overhead), `ts.block.lru_cache.max_limit` too small for data volume |
| **Info** | Tuning opportunity with no immediate risk | `ts.compress.level` could be adjusted for workload, `ts.block_filter.sampling_ratio` could be increased for better filtering |

## Notes

- For settings-only reviews, all sections apply. There are no SQL query sections because this skill does not modify user SQL.
- Each recommended change must include the current value and the recommended value (Guardrail #2).
- Each recommended change must explain why the change improves performance (Guardrail #6).
- Verification queries must be provided for each change (Guardrail #7).
