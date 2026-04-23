# kwdb-performance-review Design Spec

## Use Case

Optimize SQL query performance for KaiwuDB time-series and relational engines. KaiwuDB is a distributed multi-model database with fundamentally different indexing mechanisms for each engine.

### Core Problem

KaiwuDB has two completely separate execution engines:
- **Time-Series Engine**: NO manual secondary indexes allowed. Performance relies on partition pruning, built-in hash index on PRIMARY TAG, and columnar storage.
- **Relational Engine**: Supports B-tree, inverted, and composite indexes. Standard SQL optimization applies.

This skill helps users optimize queries by following the correct engine-specific patterns.

### Primary Use Cases

1. **Time-Series Query Optimization**
   - Ensure time range filter for partition pruning
   - Use exact equality on PRIMARY TAG for hash index hit
   - Avoid fuzzy match (LIKE, SUBSTRING) on tags
   - Optimize deep pagination with time-based cursor
   - Use TIME_BUCKET instead of manual GROUP BY

2. **Relational Query Optimization**
   - Analyze EXPLAIN output for index usage
   - Recommend appropriate indexes (B-tree, inverted, composite)
   - Optimize JOIN strategies
   - Handle correlated subqueries

3. **Cross-Model Query Optimization**
   - Drive from small relational table first
   - Add time filter on time-series table in JOIN
   - Avoid time-series table as driver (causes full scan)

4. **Schema-Level Performance Tuning**
   - Partition interval settings
   - TTL configurations
   - DICT ENCODING for high-cardinality strings

## Success Criteria

### Mandatory
1. **Engine Detection**: Determine time-series vs relational BEFORE optimization
2. **Partition Pruning Validation**: Verify time-based filters enable partition pruning
3. **Tag Filter Validation**: Verify primary tag filters are exact equality matches
4. **No Index for Time-Series**: Never suggest CREATE INDEX on time-series tables
5. **Validation**: Include EXPLAIN analysis to verify optimization

### Quality Gates
6. **Time Range Required**: Time-series queries MUST have time range filters
7. **No SELECT***: Always recommend explicit column lists for time-series
8. **Pagination Correct**: Deep pagination must use time-based cursors, not OFFSET
9. **Join Order**: For cross-model, small relational table must be driver
10. **TIME_BUCKET**: Prefer specialized function over manual GROUP BY for time aggregation

## Non-Goals

- DDL operations (schema design, index creation for relational tables) → kwdb-schema-design
- Deployment and configuration
- Data migration planning
- Write optimization (bulk INSERT, import)
- Hardware sizing recommendations
- Non-KWDB databases

## Dependencies

### Tiered Reference Architecture

**Tier 1 (Core - Always Read)**
- `references/key-rules.md` - Engine differences and anti-patterns
- `references/query-analysis.md` - EXPLAIN output interpretation

**Tier 2 (High-Frequency)**
- `references/timeseries-optimization.md` - Time-series query patterns
- `references/pagination-optimization.md` - Cursor-based pagination

**Tier 3 (Medium-Frequency)**
- `references/relational-optimization.md` - B-tree indexes, join optimization
- `references/cross-model-optimization.md` - Hybrid query optimization

**Tier 4 (Low-Frequency)**
- `references/schema-tuning.md` - Partition interval, TTL, encoding
- `references/index-analysis.md` - Index review for relational tables

## Pattern Choice

Diagnosis-first workflow: analyze query and EXPLAIN output, identify bottleneck pattern, then apply targeted fixes.

### Workflow Steps

1. **Engine Detection**: Determine time-series vs relational
2. **EXPLAIN Analysis**: Parse execution plan for key indicators
3. **Pattern Matching**: Identify anti-pattern
4. **Recommendation**: Provide specific SQL rewrite or schema suggestion
5. **Validation**: Show expected EXPLAIN improvement

## Edge Cases

### Time-Series Edge Cases
- Query without time filter → MUST warn about full partition scan
- Fuzzy/tag function on primary tag → MUST warn about hash index miss
- Large OFFSET pagination → recommend time-based cursor
- Aggregation without TIME_BUCKET → recommend TIME_BUCKET
- Missing primary tag filter → warn about IO waste

### Relational Edge Cases
- Index-only scan vs index scan decision
- Composite index column order
- Foreign key index requirements

### Cross-Model Edge Cases
- Join with time-series as driver → warn about full scan
- Missing time filter in joined query → warn about excessive data
