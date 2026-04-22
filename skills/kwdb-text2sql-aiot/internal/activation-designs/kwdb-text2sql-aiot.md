# Activation Design: kwdb-text2sql-aiot

## Should Trigger

This skill should activate when:
1. **SQL generation requests**:
   - "帮我写 SQL", "generate SQL", "转换成 SQL"
   - "自然语言转 SQL", "NL to SQL"

2. **IoT/Time-series context with SQL intent**:
   - "传感器数据查询", "设备数据", "temperature query"
   - "降采样", "downsampling", "interpolation"
   - "最新值", "latest value", "last reading"
  
3. **ML/AI prediction**:
   - "预测未来趋势"
  
4. **Time-series specific patterns**:
   - "每小时的平均值", "hourly average"
   - "填充缺失数据", "fill gaps"
   - "按设备分组", "group by device"

## Should NOT Trigger

1. **Other database systems**:
   - "MySQL 查询优化", "PostgreSQL 连接"
   - "SELECT in MongoDB"

2. **Non-SQL tasks**:
   - "Python 连接数据库" (code, not SQL)
   - "数据库部署" (deployment)

3. **Unclear intent**:
   - "数据库很慢" (troubleshooting, not SQL generation)
   - "如何备份" (administration)



## False Positive Risks

### Risk 1: Generic "SQL" mention
**Scenario**: User says "帮我写个 SQL 查询"
**Problem**: Could be for any database
**Mitigation**: Ask "请问是 KWDB 数据库吗？" and check for KWDB-specific context

### Risk 2: Device/Sensor without database context
**Scenario**: User says "设备数据怎么查"
**Problem**: Could refer to any system with device data
**Mitigation**: If MCP available, try to read kwdb://product_info to verify KWDB is present

### Risk 3: "时间" ambiguous
**Scenario**: User says "按时间统计"
**Problem**: Could mean time-series but could also be simple GROUP BY date
**Mitigation**: Check if table is time-series table (has ts column and TAGS) before applying time-series functions

## False Negative Risks

### Risk 1: Implicit KWDB assumption
**Scenario**: User assumes Claude knows they're using KWDB and just says "查询最近温度"
**Problem**: No explicit KWDB mention, skill might not trigger
**Mitigation**: Consider context - if recent conversation was about KWDB, include it in scope

### Risk 2: English vs Chinese
**Scenario**: User mixes English and Chinese: "查询 device_id = 1 的 recent temperature"
**Problem**: Might not match trigger patterns
**Mitigation**: Support both languages in triggers, use flexible keyword matching

## First Decision After Activation

After activation, the first decision is:

```
MCP Available?
├─ Yes → Ask for database name (if not provided)
│         ├─ Get table list from kwdb://db_info/{db}
│         ├─ Match candidate tables by keywords
│         └─ Proceed to query type routing
│
└─ No → Ask user to choose:
         ├─ "Provide table schema manually" → wait for schema info
         └─ "Use assumed field names" → proceed with generic names
```

## Disambiguation Triggers

When multiple interpretations are possible, ask the user:

1. **Multiple candidate tables**: "Which table? [devices, sensor_data, device_log]"
2. **Ambiguous query type**: "Is this a time-series query or relational query?"
3. **Missing time range**: "What time range should I query?"
4. **Unknown database**: "Which database should I query?"
