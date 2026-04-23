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

## Negative Cases (Should NOT Activate)

### Schema Design
- "design a time-series table for sensors"
- "create index on orders table"

### Deployment/Config
- "how to install KWDB"
- "KWDB memory configuration"

### Write Optimization
- "how to speed up bulk INSERT"
- "fast data import method"

### Non-KWDB
- "MySQL query is slow"
- "PostgreSQL performance tuning"

### Other Skills
- "design schema for my database"
