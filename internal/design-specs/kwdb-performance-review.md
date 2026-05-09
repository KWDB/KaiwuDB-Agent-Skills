# kwdb-performance-review Design Spec

## Use Case

Review and tune KWDB time-series ts.* configuration parameters for performance. Diagnose misconfigured compression settings, disabled optimizations, insufficient cache sizing, and stale data accumulation. Output a severity-ranked issue list with root cause analysis and executable tuning SQL.

### Core Problem

KaiwuDB time-series engine performance depends heavily on correct ts.* cluster parameter configuration:

- **Compression**: `ts.compress.stage` and `ts.compress.algorithm` directly affect storage usage and read/write performance. Misconfigured compression (stage=0, algorithm=disabled) wastes storage and slows range scans.
- **Aggregation**: `ts.partition_agg.enabled` and `ts.count.use_statistics.enabled` control whether COUNT/SUM/MAX/MIN use pre-aggregated metadata. Disabling them forces full data scans.
- **Cache**: `ts.block.lru_cache.max_limit`, `ts.last_cache_size.max_limit`, and `ts.table_cache.capacity` affect how much data stays in memory. Undersized caches cause repeated disk reads and metadata lookups.
- **Lifecycle**: `ts.auto_vacuum.enabled` and `ts.agg_recalc.cycle` control data cleanup and aggregate freshness. Disabling them causes table bloat and stale results.

### Non-SQL-Modification Principle

This skill does NOT modify user SQL statements. It only reviews and adjusts ts.* cluster configuration parameters. SQL query optimization belongs to a different skill.

## Primary Use Cases

1. **Query Optimization Parameters** — Review `ts.partition_agg.enabled`, `ts.count.use_statistics.enabled`, and related settings that affect query execution paths.
2. **Compression Strategy** — Review `ts.compress.algorithm`, `ts.compress.stage`, `ts.compress.level`, `ts.compress.last_segment.enabled`, and `ts.dedup.rule`.
3. **Memory and Cache Sizing** — Review `ts.block.lru_cache.max_limit`, `ts.last_cache_size.max_limit`, `ts.mem_segment_size.max_limit`, `ts.metric_schema_cache.max_limit`, `ts.table_cache.capacity`.
4. **Storage and Background Tasks** — Review `ts.auto_vacuum.enabled`, `ts.agg_recalc.cycle`, `ts.compact.max_limit`, `ts.rows_per_block` settings, `ts.block_filter.sampling_ratio`.

## Success Criteria

### Mandatory
1. **Fetch real cluster settings** via MCP (`SHOW CLUSTER SETTINGS`)
2. **Classify issues by severity**: Critical / Warning / Info
3. **Provide root cause and executable tuning SQL** for each issue
4. **Cover four dimensions**: query optimization parameters, compression, memory and cache, storage and background tasks

### Quality Gates
5. **QG1**: Every recommendation includes current value and recommended value
6. **QG2**: Every recommendation includes a `SET CLUSTER SETTING` statement
7. **QG3**: Abnormal settings are classified by severity (Critical/Warning/Info)
8. **QG4**: No SQL rewriting recommendations — only configuration parameter changes
9. **QG5**: No CREATE INDEX suggestions on time-series tables
10. **QG6**: Inter-setting dependencies are considered (e.g., partition_agg + count_statistics)
11. **QG7**: Verification method is provided for each change

## Non-Goals

- SQL query optimization or rewriting
- Relational table tuning (B-tree indexes, join order, etc.)
- Deployment and cluster setup
- Data migration
- Schema design (CREATE TABLE, ALTER TABLE, CREATE INDEX)
- Write-path tuning (WAL, raft log, ack-before-application)
- Hardware sizing recommendations
- Application-level tuning (connection pooling, caching beyond SQL)

## Dependencies

### kwdb MCP Server
- `read-query`: for `SHOW CLUSTER SETTINGS`, `SHOW TABLES`, and system views
- `write-query`: for `SET CLUSTER SETTING` recommendations

### Tiered Reference Architecture
- **Tier 1 (Always Read)**: `ts-settings-checklist.md` — parameter checklist with diagnostic queries
- **Tier 2 (High-Frequency)**: `ts-compression-review.md` — compression strategy review
- **Tier 3 (As Needed)**: `output-template.md` — output format template

## Pattern Choice

Reviewer pattern: review ts.* settings against a domain-specific checklist, classify issues by severity, provide executable tuning SQL.

### Workflow (4 Phases)

1. **Detect**: Confirm target is a time-series table; fetch ts.* settings via MCP
2. **Diagnose**: Check each setting against `ts-settings-checklist.md`; check compression against `ts-compression-review.md`; check inter-setting dependencies
3. **Fix**: For each misconfiguration, provide `SET CLUSTER SETTING` with current value, recommended value, and reason
4. **Validate**: Output severity-ranked issue list; provide verification queries

## Edge Cases

- **compress.stage=0 with explicit user reason**: User may have set stage=0 for benchmarking. Confirm the reason and document it; do not force a change if the user has an explicit justification.
- **Inter-setting contradiction**: `ts.partition_agg.enabled = true` but `ts.count.use_statistics.enabled = false`. Both must be true for count optimization. Flag as Warning and recommend enabling both.
- **Cache sum exceeds system memory**: If the total of all cache settings approaches or exceeds available RAM, flag as Critical. The system may OOM or swap.
- **Parameter not in checklist**: User asks about a ts.* parameter not covered in `ts-settings-checklist.md`. State that the parameter is outside the review scope; do not guess recommendations.
- **Algorithm change impact on existing data**: `ts.compress.algorithm` change only affects new writes. Existing data retains its original compression. Inform the user about this limitation.
- **dedup.rule and data integrity**: `ts.dedup.rule = 'filter'` can silently hide data issues. Warn about this risk unless the user has an explicit idempotent ingestion pipeline.
- **compress.last_segment.enabled trade-off**: Enabling last segment compression improves storage but slows down appends and last-row reads. Only recommend when the user's access pattern does not prioritize last-row queries.
