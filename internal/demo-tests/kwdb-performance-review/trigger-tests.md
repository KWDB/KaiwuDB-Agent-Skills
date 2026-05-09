# Trigger Tests

## Positive Cases

### Explicit Configuration Keywords
- "Review my KWDB ts.* cluster settings."
  - Reason: explicit ts.* settings review request
- "审查我的KWDB时序表配置参数"
  - Reason: Chinese configuration review keyword

### Implicit Performance Issues
- "My time-series COUNT query takes minutes."
  - Reason: implicit performance issue likely caused by configuration
- "时序查询很慢，帮我看看"
  - Reason: Chinese implicit performance keyword + time-series context

### Compression-Related
- "Should I switch from lz4 to zstd compression?"
  - Reason: explicit compression strategy question
- "My time-series storage is growing too fast."
  - Reason: storage growth may indicate compression misconfiguration

### Cache-Related
- "My last-row queries on time-series tables are slow."
  - Reason: last-row performance may indicate cache sizing issue
- "KWDB cluster with many time-series tables is slow."
  - Reason: many tables may indicate table_cache or schema_cache issue

## Negative Cases

- "Optimize this SQL: SELECT * FROM device_sensor WHERE device_id = 'D001'"
  - Reason: SQL rewriting request, not configuration tuning
- "Design a KWDB schema for sensor data."
  - Reason: schema design → kwdb-schema-design
- "How do I deploy a KWDB cluster?"
  - Reason: deployment setup, not configuration tuning
- "How to speed up bulk INSERT into my time-series table?"
  - Reason: write-path optimization, not read performance configuration
- "My relational table join is slow."
  - Reason: relational table tuning, out of scope
- "MySQL query performance tuning."
  - Reason: non-KWDB database
- "Add an index on my time-series table to speed up queries."
  - Reason: time-series tables do not support secondary indexes; this is a scope boundary, not a trigger
