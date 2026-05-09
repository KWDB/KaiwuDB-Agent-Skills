# kwdb-performance-review Activation Design

## Should Trigger

### Explicit Configuration Keywords
- "review my ts.* settings" / "审查ts.*配置"
- "ts.* parameter tuning" / "参数调优"
- "time-series configuration review" / "时序配置审查"
- "KWDB time-series performance" / "KWDB时序性能"

### Implicit Performance Issues
- "my time-series query is slow" / "时序查询很慢"
- "COUNT on time-series takes too long" / "时序表COUNT很慢"
- "aggregation query is slow" / "聚合查询慢"
- "pagination on time-series is slow" / "时序分页慢"
- "query performance degraded" / "查询性能下降"

### Compression Strategy
- "compression strategy" / "压缩策略"
- "should I use zstd or lz4" / "用zstd还是lz4"
- "storage growing too fast" / "存储增长过快"
- "compression ratio is poor" / "压缩比太低"
- "change compression algorithm" / "修改压缩算法"

### Cache and Memory
- "cache too small" / "缓存不足"
- "last-row queries slow" / "最新值查询慢"
- "too many time-series tables" / "时序表太多"
- "memory pressure" / "内存压力"

## Should Not Trigger

- SQL rewriting requests: "optimize this SQL", "rewrite this query", "add index" → different skill
- Schema design: "create table", "alter table", "create index" → kwdb-schema-design
- Deployment/configuration setup: "how to install KWDB", "set up a cluster"
- Data migration: "move data between databases"
- DML write optimization: "speed up bulk INSERT", "fast import"
- Relational table tuning: "B-tree index", "join order", "relational table slow"
- Non-KWDB databases: "MySQL query slow", "PostgreSQL tuning"
- Hardware sizing: "what server specs do I need"
- Application tuning: "connection pool settings", "application-level caching"

## False Positive Risks

- **Risk**: "KWDB query is slow" but the query targets a relational table only
  - Mitigation: engine detection step checks table type via `SHOW TABLES` or `DESCRIBE`; if all tables are relational, stop and state scope boundary

- **Risk**: "optimize this query" sounds like SQL optimization but the user may mean configuration tuning
  - Mitigation: if the user mentions ts.* settings, compression, or cache, treat as configuration review; if they provide a specific SQL to rewrite, redirect to SQL optimization skill

- **Risk**: "add an index to speed up my query" on a time-series table
  - Mitigation: if target is time-series, explain that secondary indexes are not supported and redirect to configuration tuning (partition pruning, tag filter, cache sizing)

- **Risk**: "my pagination API is slow" without time-series context
  - Mitigation: check if the paginated table is time-series; if yes, review compression and cache settings; if no, state scope boundary

## False Negative Risks

- **Risk**: "data write latency is high" sounds like a write-path issue but may be caused by compression or memory pressure
  - Mitigation: include latency-related symptoms in trigger scope even if the user does not mention ts.* explicitly

- **Risk**: "my query returns too much data" may not mention "slow" but could be caused by disabled compression or undersized cache
  - Mitigation: treat "too much data" as a trigger for compression and cache review

- **Risk**: "compression ratio is poor" sounds like a storage issue but is actually a compression strategy configuration problem
  - Mitigation: include compression-related symptoms in trigger scope

## Activation Examples

### Example 1: Explicit Configuration Review (Should Activate)
**User**: "Review my KWDB ts.* cluster settings."
**Activation**: YES
**Scope**: Full ts.* settings checklist review

### Example 2: Implicit Performance Problem (Should Activate)
**User**: "My time-series COUNT query takes minutes. Help me diagnose it."
**Activation**: YES
**Likely Issue**: `ts.partition_agg.enabled = false` or `ts.count.use_statistics.enabled = false`

### Example 3: False Positive — SQL Rewriting (Should NOT Activate)
**User**: "Optimize this SQL: SELECT * FROM device_sensor WHERE device_id = 'D001'"
**Activation**: NO
**Reason**: SQL rewriting request; this skill only provides configuration tuning

### Example 4: False Positive — Schema Design (Should NOT Activate)
**User**: "Should I add an index on my time-series table?"
**Activation**: NO (but warn about constraint)
**Reason**: Time-series tables do not support secondary indexes; redirect to configuration tuning

### Example 5: Edge Case — Mixed Request (Partial Activation)
**User**: "My time-series queries are slow AND I need to redesign my table schema."
**Activation**: YES for the configuration portion only
**Scope**: Review ts.* settings for performance; clearly state that schema design is out of scope

## First Decision After Activation

1. Determine the target table type. If the user names a table, check `SHOW TABLES FROM <db>` or `DESCRIBE <table>` via MCP
2. If the table is a TIME SERIES TABLE, proceed with the configuration review workflow
3. If the table is a RELATIONAL TABLE only, stop and state that this skill covers time-series configuration only
4. If both table types are involved, review only the time-series configuration
5. Fetch ts.* settings via MCP (`SHOW CLUSTER SETTINGS`) before making any recommendations
