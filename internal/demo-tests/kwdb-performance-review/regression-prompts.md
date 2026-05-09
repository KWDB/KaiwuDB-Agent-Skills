# Regression Prompts

These prompts test edge cases and common mistakes.

## Regression 1: SQL Rewriting Request

**Prompt:**
"My time-series query is slow: SELECT * FROM device_sensor WHERE device_id = 'D001'. Can you rewrite it?"

**Must NOT:**
- Rewrite the SQL query
- Suggest adding WHERE clauses, changing SELECT columns, or using TIME_BUCKET

**Must:**
- State that this skill only provides configuration tuning, not SQL rewrites
- Offer to review ts.* settings that may affect the query's performance
- Check for compression, aggregation, and cache misconfigurations

## Regression 2: Inter-Setting Contradiction

**Prompt:**
"I enabled partition aggregation but COUNT is still slow."

**Must:**
- Check both `ts.partition_agg.enabled` and `ts.count.use_statistics.enabled`
- Explain that both must be true for count optimization
- If `count_statistics = false`, flag as Critical and recommend enabling it

## Regression 3: Mixed Request (Configuration + SQL Rewriting)

**Prompt:**
"Help me optimize my time-series performance: I need faster queries AND I want to redesign my table schema."

**Must:**
- Only handle the configuration tuning portion
- Clearly scope the response to ts.* parameter review
- State that schema design is out of scope (→ kwdb-schema-design)
- State that SQL rewriting is out of scope

## Regression 4: Parameter Not in Checklist

**Prompt:**
"Should I change ts.wal.sync.enabled?"

**Must:**
- State that `ts.wal.sync.enabled` is outside the review scope
- Do not guess recommendations for parameters not in the checklist
- Offer to review the parameters that are covered in ts-settings-checklist.md

## Regression 5: Cache Sum Exceeds System Memory

**Prompt:**
"I increased all my caches: block.lru_cache = 8 GiB, last_cache_size = 8 GiB, mem_segment_size = 4 GiB. My cluster has 16 GiB RAM."

**Must:**
- Flag as Critical: total cache allocation (20 GiB) exceeds available RAM (16 GiB)
- Warn about OOM risk or swap thrashing
- Recommend reducing cache sizes so total stays under ~50% of available RAM
