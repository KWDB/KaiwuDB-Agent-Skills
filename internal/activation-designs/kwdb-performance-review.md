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

## Should NOT Trigger

### Schema Design
- "design a table" / "create table" / "create index" → kwdb-schema-design
- "add column" / "alter table" / "drop index" → kwdb-schema-design

### Deployment/Config
- "how to install KWDB"
- "memory settings" / "配置调优"

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
