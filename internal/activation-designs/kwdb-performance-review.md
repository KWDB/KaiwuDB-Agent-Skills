# kwdb-performance-review Activation Design

## Should Trigger

### Explicit Performance Triggers
- "optimize this query" / "优化这个查询"
- "slow query analysis" / "慢查询分析"
- "explain analyze" / "执行计划"
- "query performance" / "查询性能"
- "KWDB query slow" / "KWDB查询慢"
- "SQL性能分析"

### Implicit Performance Keywords
- "SELECT is slow" / "查询很慢"
- "taking minutes" / "需要几分钟"
- "execution plan" / "执行计划"
- "全表扫描" / "查询超时"

### Time-Series Specific
- "时序数据查询慢"
- "传感器数据查询优化"
- "时间范围查询"
- "TIME_BUCKET"
- "时间聚合查询"
- "时间裁剪" / "partition pruning"

### Index Triggers (Relational Only)
- "add index for this query"
- "create index to speed up"
- "索引优化" / "索引建议"

### Storage Configuration Optimization
- "config optimization" / "配置优化"
- "parameter tuning" / "参数调优"
- "存储配置" / "参数调整"
- "内存占用过大" / "memory too high"
- "磁盘空间紧张" / "disk space tight"
- "CPU占用过高" / "CPU too high"
- "compaction积压" / "compaction backlog"
- "缓存调优" / "cache tuning"
- "压缩算法调整" / "compression algorithm"
- SQL optimization exhausted and performance issues persist

## Should NOT Trigger

### Schema Design
- "design a table" / "create table" / "create index" → kwdb-schema-design
- "add column" / "alter table" / "drop index" → kwdb-schema-design

### Deployment
- "how to install KWDB"

### DML Write Optimization
- "INSERT performance" / "bulk insert"
- "import data fast" / "批量导入"

### Non-KWDB Context
- "MySQL query slow"
- "PostgreSQL optimization"

## False Positive Risks

### High Risk
- Generic "why is my query slow" without KWDB context
  - Mitigation: Check for KWDB-specific keywords or time-series patterns

### Medium Risk
- Questions about "indexes" in KWDB context
  - Must distinguish: relational tables CAN have indexes, time-series CANNOT
  - Mitigation: First determine table type

## First Decision After Activation

### Step 1: Detect Engine Type

Ask or determine:
- **Time-Series Engine**: Table uses `ts_column`, `primary_tags`, or time-series keywords
- **Relational Engine**: Standard SQL table with optional indexes
- **Mixed**: Query involves both

### Step 2: Parse EXPLAIN Output

| Indicator | Time-Series | Relational |
|-----------|-------------|------------|
| Partition Filter | Good: time pruning | N/A |
| Tag Filter | Good: hash index hit | N/A |
| Seq Scan | Normal in partition | Problem if large table |
| Index Scan | N/A | Good if selective |
| Distribute: Shuffle | Problem: cross-node | Varies |

### Step 3: Identify Anti-Pattern

**Time-Series Anti-Patterns**:
- Missing time range filter → major issue
- Fuzzy match on primary tag (LIKE, SUBSTRING) → hash index miss
- Large OFFSET → memory issue
- SELECT * → unnecessary IO
- No TIME_BUCKET on aggregation → missed optimization

**Relational Anti-Patterns**:
- Seq Scan on large table → suggest index
- Nested loop on large sets → suggest hash join
- Missing index on join column → suggest index

### Step 4: Provide Recommendations

Output specific SQL rewrites or configuration suggestions.

### Step 5: Storage Configuration Optimization (Conditional)

Only activate when:
1. User explicitly mentions "config optimization" / "parameter tuning" / "配置优化" / "参数调优", OR
2. SQL optimization steps (1-4) are exhausted and performance issues persist

**Per-Parameter Trigger (review on demand, not full scan):**

| Parameter | Config Group | Trigger Condition |
|-----------|-------------|-------------------|
| ts.compress.stage | Compression Group | User wants compression optimization or smaller disk space usage |
| ts.compress.algorithm | Compression Group | User wants compression optimization or smaller disk space usage |
| ts.compress.level | Compression Group | User wants compression optimization or smaller disk space usage |
| ts.rows_per_block.min_limit | Rows Per Block Group | User reports excessive small blocks from flushing, long write visibility delay, or high per-device data volume with low compression ratio |
| ts.rows_per_block.max_limit | Rows Per Block Group | User reports excessive small blocks from flushing, long write visibility delay, or high per-device data volume with low compression ratio |
| ts.compress.last_segment.enabled | Independent | User wants compression optimization or smaller disk space usage, or needs to optimize write performance |
| ts.block.lru_cache.max_limit | Independent | User wants to optimize overall query performance, or memory usage is too high |
| ts.last_cache_size.max_limit | Independent | User wants to optimize last-related SQL query performance, or memory usage is too high |
| ts.mem_segment_size.max_limit | Independent | Write performance optimization (after ts.compress.last_segment.enabled reviewed), or memory usage is too high (after ts.block.lru_cache.max_limit and ts.last_cache_size.max_limit reviewed) |
| ts.reserved_last_segment.max_limit | Independent | Frequent compaction triggers or disk space is tight |
| ts.compact.max_limit | Independent | User reports compaction backlog with significant CPU idle, or CPU usage is too high |
| ts.auto_vacuum.enabled | Independent | User wants to clean up data |
| ts.block_filter.sampling_ratio | Independent | User reports poor query performance with range conditions or null checks, suspects inefficient filter pushdown |

**Decision Tree:**

1. Compression optimization / disk space reduction → Compression Group
   - Performance priority, disk sufficient → snappy/lz4, level=any, stage=1; extreme: stage=0
   - Disk space priority, CPU sufficient → zstd, level=high, stage=3
   - CPU usage too high → lz4, level=any, stage=1; if still high → stage=0
2. Excessive small blocks / write visibility delay / low compression ratio → Rows Per Block Group
   - High-throughput write → increase max (8192-16384)
   - Memory constrained → decrease max (2048)
   - Point queries → decrease max
   - Sequential scan → increase max
   - Low-latency small batch → increase min (1024+)
3. Write performance → ts.compress.last_segment.enabled (SSD: false, HDD: true)
4. Query performance / high memory → ts.block.lru_cache.max_limit
5. Last query performance / high memory → ts.last_cache_size.max_limit
6. Write performance (after #3) / high memory (after #4,#5) → ts.mem_segment_size.max_limit
7. Frequent compaction / disk tight → ts.reserved_last_segment.max_limit
8. Compaction backlog / high CPU → ts.compact.max_limit
9. Data cleanup → ts.auto_vacuum.enabled
10. Poor filter pushdown → ts.block_filter.sampling_ratio

**Pre-conditions (confirm relevant resources before suggesting):**
- Memory-related params: confirm available free memory with user
- Disk-related params: confirm available disk space with user
- CPU-related params: confirm CPU availability with user

**Important:**
- NEVER execute `SET CLUSTER SETTING` automatically
- Only provide SQL statements for user to review and execute
- NEVER use `SHOW CLUSTER SETTINGS` — always query specific settings individually
- Always include risk warning when recommending reduced values for memory/CPU-impact parameters

## Activation Examples

### Example 1: Time-Series Query Without Time Filter
**User**: "Why is my sensor query slow: SELECT * FROM device_sensor WHERE device_id = 'D001'"
**Activation**: YES
**Anti-Pattern**: Missing time range filter

### Example 2: Deep Pagination on Time-Series
**User**: "My paginated query is slow: SELECT * FROM metrics ORDER BY ts LIMIT 10000, 20"
**Activation**: YES
**Anti-Pattern**: Large OFFSET

### Example 3: Relational Index Suggestion
**User**: "This user query is slow: SELECT * FROM users WHERE email = 'x@y.com'"
**Activation**: YES
**Table Type**: Relational

### Example 4: False Positive - Schema Question
**User**: "Should I add an index on my time-series table"
**Activation**: YES (but warn about constraint)
**Table Type**: Verify if actually time-series

### Example 5: No Trigger - DML
**User**: "How to speed up my bulk INSERT"
**Activation**: NO
**Reason**: Write optimization, not read performance

### Example 6: Storage Configuration Optimization - Memory Pressure
**User**: "我的KWDB内存占用过大，想通过配置优化减少内存使用"
**Activation**: YES
**Step**: Step 5 (Storage Configuration Optimization)
**Trigger Condition**: ts.block.lru_cache.max_limit, ts.last_cache_size.max_limit
**Pre-condition**: Confirm available free memory

### Example 7: Storage Configuration Optimization - Disk Space
**User**: "磁盘空间快满了，想调整压缩算法节省空间"
**Activation**: YES
**Step**: Step 5 (Storage Configuration Optimization)
**Trigger Condition**: ts.compress.algorithm, ts.compress.level, ts.compress.stage (Compression Group)
**Pre-condition**: Confirm CPU and disk space status

### Example 8: SQL + Config Hybrid
**User**: "查询优化后还是有点慢，还能再快吗？"
**Activation**: YES
**Step**: Steps 1-4 first, then Step 5 if SQL optimization exhausted
**Reason**: SQL optimization may not fully resolve the issue; config tuning (e.g., cache increase) may help

### Example 9: Config Optimization - Compaction
**User**: "compaction积压严重，CPU比较空闲"
**Activation**: YES
**Step**: Step 5 (Storage Configuration Optimization)
**Trigger Condition**: ts.compact.max_limit, ts.reserved_last_segment.max_limit
**Pre-condition**: Confirm compaction backlog and CPU idle level
