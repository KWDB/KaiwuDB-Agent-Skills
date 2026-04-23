---
name: kwdb-performance-review
description: |
  Optimize SQL query performance for KaiwuDB time-series and relational engines.
  Covers: EXPLAIN analysis, time-series optimization, pagination, cross-model queries.
  Trigger keywords: optimize query, slow query, explain, execution plan, performance, 性能, 查询优化.
  NOT for: DDL, schema design, deployment, DML writes.
version: 0.2.0
---

Read the required reference files first.

## Tiered Reference Architecture

**Tier 1 (Always Read)**
- `references/key-rules.md` - Core engine differences and anti-patterns
- `references/query-analysis.md` - EXPLAIN output interpretation

**Tier 2 (High-Frequency Optimization)**
- `references/timeseries-optimization.md` - Time-series query patterns
- `references/pagination-optimization.md` - Cursor-based pagination

**Tier 3 (Medium-Frequency)**
- `references/relational-optimization.md` - B-tree indexes, join optimization
- `references/cross-model-optimization.md` - Hybrid query optimization

**Tier 4 (Low-Frequency)**
- `references/schema-tuning.md` - Partition interval, TTL, encoding
- `references/index-analysis.md` - Index review for relational tables

## When to Activate

**Should trigger:**
- "optimize this query" / "优化查询"
- "slow query" / "查询很慢" / "慢查询"
- "explain this query" / "执行计划"
- "query performance" / "查询性能"
- "KWDB query slow"
- "全表扫描" / "查询超时"
- "时序数据查询慢" / "传感器数据"
- "TIME_BUCKET" / "时间聚合"
- "索引优化" (relational tables only)

**Should NOT trigger:**
- Schema design ("create table", "add index") → kwdb-schema-design
- Deployment/configuration questions
- DML write optimization ("fast INSERT")
- Non-KWDB databases

## Engine Detection

Before optimizing, determine which engine the query targets:

```
TIME SERIES TABLE:
  - Has ts_column, primary_tags in CREATE TABLE
  - Cannot have secondary indexes
  - Query must include time range filter
  - Primary tag filter uses hash index

RELATIONAL TABLE:
  - Standard SQL table
  - Can have B-tree, inverted indexes
  - Standard SQL optimization applies
```

Ask user if unclear.

## Workflow

### Step 1: Parse EXPLAIN Output

Key indicators to look for:

| Pattern | Time-Series | Relational | Action |
|---------|-------------|------------|--------|
| Partition Filter: ts | Good | N/A | Time pruning working |
| Tag Filter: tag_col | Good | N/A | Hash index hit |
| Seq Scan in partition | Normal | Check size | Normal for small |
| Index Scan | N/A | Good | Index being used |
| Distribute: Shuffle | Warning | Varies | Cross-node traffic |

### Step 2: Identify Anti-Patterns

**Time-Series Critical Issues:**
- Missing time range filter -> full partition scan
- Fuzzy match on primary tag (LIKE, SUBSTRING) -> hash index miss
- SELECT * -> unnecessary column IO
- Large OFFSET pagination -> memory pressure
- Manual GROUP BY instead of TIME_BUCKET

**Relational Issues:**
- Seq Scan on large table -> missing index
- Nested loop on large sets -> bad join order
- Missing index on join column

### Step 3: Provide Optimized Query

Always provide:
1. The anti-pattern being fixed
2. The rewritten query
3. Expected improvement in EXPLAIN

### Step 4: Validate

Include `EXPLAIN (ANALYZE)` to verify the optimization works.

## NOT for

- **DDL operations**: Creating/dropping tables, indexes (→ kwdb-schema-design)
- **Deployment/Config**: Memory settings, installation, replication
- **Write optimization**: Bulk INSERT, import performance
- **Data migration**: Moving data between databases
- **Hardware sizing**: Server specs, disk I/O recommendations
- **Application tuning**: Connection pooling, caching (beyond SQL)

## Guardrails

1. **Never suggest CREATE INDEX on time-series tables** - they don't support secondary indexes
2. **Time-series queries MUST have time range filters** - warn if missing
3. **Never recommend OFFSET for deep pagination** - use time-based cursor
4. **Always specify SELECT columns** for time-series - no SELECT *
5. **Verify table type before index recommendations**
6. **Explain WHY the optimization works** - not just what to change
7. **Validate with EXPLAIN** before finishing

## Output Format

```markdown
## Intent
[Brief description of the optimization goal]

## Engine Type
[time-series / relational / mixed]

## Anti-Pattern Detected
[What was causing the slowness]

## Original Query
```sql
[query before optimization]
```

## Optimized Query
```sql
[rewritten query]
```

## Expected Improvement
[What should change in EXPLAIN]

## Validation
```sql
EXPLAIN (ANALYZE) [optimized query];
```
```
