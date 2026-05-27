# Trigger Tests

## Positive Cases (Should Activate)

### Explicit Performance Keywords
- "optimize this KWDB query"
- "slow query analysis in KWDB"
- "explain this KWDB query: SELECT * FROM sensor_data"
- "KWDB query performance issue"
- "查询性能优化"

### Implicit Performance Keywords
- "why is my SELECT taking minutes"
- "execution plan shows full scan"
- "全表扫描问题"
- "查询超时"

### Time-Series Specific
- "时序数据查询慢"
- "传感器数据查询优化"
- "TIME_BUCKET aggregation slow"
- "时间范围查询如何优化"

### EXPLAIN/Plan Related
- "explain query: SELECT * FROM metrics WHERE ts >= '2026-04-01'"
- "查看这个SQL的执行计划"

### Storage Configuration Optimization
- "配置优化" / "参数调优"
- "内存占用过大" / "memory too high"
- "磁盘空间紧张" / "disk space tight"
- "CPU占用过高" / "CPU too high"
- "compaction积压" / "compaction backlog"
- "缓存调优" / "cache tuning"
- "压缩算法调整" / "compression optimization"
- "存储配置优化" / "storage config tuning"
- "写入性能优化" (when ts.compress.last_segment.enabled or ts.mem_segment_size.max_limit is relevant)

## Negative Cases (Should NOT Activate)

### Schema Design
- "design a time-series table for sensors"
- "create index on orders table"

### Deployment
- "how to install KWDB"

### Write Optimization
- "how to speed up bulk INSERT"
- "fast data import method"

### Non-KWDB
- "MySQL query is slow"
- "PostgreSQL performance tuning"

### Other Skills
- "design schema for my database"

### Parameter Definition Management (→ st-config-performance)
- "帮我修改参数定义" → st-config-performance
- "添加存储配置优化参数" → st-config-performance
- "参数定义变更" → st-config-performance
