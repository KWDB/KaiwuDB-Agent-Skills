# Trigger Tests - kwdb-ts-anomaly-detection

## 测试概述

本文档定义了 `kwdb-ts-anomaly-detection` 技能的触发测试用例，用于验证技能在各种场景下的正确行为。

---

## 1. 库表 DDL 元数据

### 1.1 时序库 - factory_monitor

**数据库类型**: TIME SERIES

**表: device_metrics**

```sql
CREATE TABLE device_metrics (
    ts TIMESTAMPTZ(3) NOT NULL,
    temperature FLOAT4 NULL,
    humidity FLOAT4 NULL,
    power_consumption FLOAT8 NULL
) TAGS (
    device_id VARCHAR(32) NOT NULL,
    workshop VARCHAR(64),
    line_number INT2
) PRIMARY TAGS(device_id)
COMMENT ON COLUMN device_metrics.temperature IS 'Normal temperature range: [7, 80]';
```

**列信息**:

| 列名 | 类型 | 是否标签 | 说明 |
|------|------|---------|------|
| ts | TIMESTAMPTZ(3) | 否 | 时间戳，主键 |
| temperature | FLOAT4 | 否 | 温度（数值型） |
| humidity | FLOAT4 | 否 | 湿度（数值型） |
| power_consumption | FLOAT8 | 否 | 功耗（数值型） |
| device_id | VARCHAR(32) | 是 | 设备ID（主标签） |
| workshop | VARCHAR(64) | 是 | 车间 |
| line_number | INT2 | 是 | 产线号 |

**主标签**: device_id

**数据量**: ~25,901,000 条

**示例主标签值**: A-001, B-002, C-003, A-002, A-003, A-004, A-005, A-006, A-007, A-008

---

### 1.2 时序库 - ts_db

**数据库类型**: TIME SERIES

**表: charger_data**

```sql
CREATE TABLE charger_data (
    ts TIMESTAMPTZ(3) NOT NULL,
    is_charging BOOL NULL,
    current_amp INT4 NULL,
    voltage_v FLOAT8 NULL,
    fault_info VARCHAR(128) NULL
) TAGS (
    charger_id VARCHAR(36) NOT NULL,
    station_code VARCHAR(32),
    charge_gun INT2
) PRIMARY TAGS(charger_id);
```

**列信息**:

| 列名 | 类型 | 是否标签 | 说明 |
|------|------|---------|------|
| ts | TIMESTAMPTZ(3) | 否 | 时间戳，主键 |
| is_charging | BOOL | 否 | 是否充电（非数值型） |
| current_amp | INT4 | 否 | 电流（数值型） |
| voltage_v | FLOAT8 | 否 | 电压（数值型） |
| fault_info | VARCHAR(128) | 否 | 故障信息（非数值型） |
| charger_id | VARCHAR(36) | 是 | 充电桩ID（主标签） |
| station_code | VARCHAR(32) | 是 | 站点编码 |
| charge_gun | INT2 | 是 | 充电枪编号 |

**主标签**: charger_id

**数据量**: ~778,266 条

**示例主标签值**: C0088, C0089, C0090, c001, c002, c003

---

### 1.3 关系库 - trade_system

**数据库类型**: RELATIONAL

**表: orders**

```sql
CREATE TABLE orders (
    order_id INT8 NOT NULL DEFAULT unique_rowid(),
    user_id INT4 NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    order_status INT2 NOT NULL DEFAULT 0,
    create_time TIMESTAMP NOT NULL DEFAULT current_timestamp(),
    pay_time TIMESTAMP NULL
);
```

**列信息**:

| 列名 | 类型 | 是否标签 | 说明 |
|------|------|---------|------|
| order_id | INT8 | 否 | 订单ID |
| user_id | INT4 | 否 | 用户ID |
| total_amount | DECIMAL(12,2) | 否 | 订单金额 |
| order_status | INT2 | 否 | 订单状态 |
| create_time | TIMESTAMP | 否 | 创建时间 |
| pay_time | TIMESTAMP | 否 | 支付时间 |

---

## 2. 测试用例

### TC-001: 安全确认拒绝后中止任务

**测试目标**: 验证技能能在用户拒绝安全确认时正确中止任务

**前提条件**: 用户请求执行异常检测，但拒绝安全确认

**用户输入**:
```
请检测 factory_monitor.device_metrics 表中 temperature 列的异常。
```
**安全确认回复**:
```
不同意
```
（或任意非 "I AGREE" 的回复）

**预期行为**:
1. 技能显示安全确认提示（步骤 0）
2. 用户输入非 "I AGREE" 的回复
3. 技能检测到用户未明确同意
4. 技能**永久终止任务**并显示终止信息
5. 不执行任何后续步骤

**预期输出**:
```
┌─────────────────────────────────────────────────────────────────┐
│                         🔒 安全 确认                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 数据库连接配置信息是重要敏感信息，建议用户仅在数据库非安全模式下使用该SKILL |
│                                                                 │
│ 输入 "我同意" 继续执行异常检测流程: ___________                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

用户回复: 不同意

任务已终止。
由于您未同意安全确认条款，无法执行异常检测任务。
如需继续，请重新发起请求并输入 "I AGREE"。
```

**验证点**:
- [x] 技能正确显示安全确认提示
- [x] 技能正确识别用户拒绝（非 "I AGREE"）
- [x] 技能在步骤 0 触发终止条件
- [x] 任务正确中止，不执行任何数据库操作
- [x] 技能提供清晰的终止原因说明

---

### TC-002: 错误连接凭证导致任务终止

**测试目标**: 验证技能在用户提供错误的 host、port、用户名或密码导致无法连接数据库时，能正确终止任务

**前提条件**: 用户请求执行异常检测，但提供了错误的数据库连接凭证

**用户输入**:
```
请检测 factory_monitor.device_metrics 表中设备A-001的temperature列数据是否存在异常。
```

**连接参数输入** (步骤 1.2 收集):
```
Host: 127.0.0.1
Port: 54321
Username: root
Password: wrong_password
```

**预期行为**:
1. 技能显示安全确认提示
2. 用户同意后，技能进入步骤 1.2 收集连接参数
3. 用户提供错误的连接凭证
4. 技能在步骤 1.3 执行 `SELECT 1` 测试连接
5. 连接失败，技能检测到认证失败/连接错误
6. 技能**永久终止任务**并显示错误信息

**预期输出**:
```
错误：无法连接到数据库 127.0.0.1:54321。
原因：认证失败。请检查用户名和密码是否正确。
任务已终止。
```

或

```
错误：无法连接到数据库 127.0.0.1:54321。
原因：连接被拒绝。请检查 host 和 port 是否正确。
任务已终止。
```

**验证点**:
- [x] 技能在步骤 1.3 检测到连接失败
- [x] 技能正确识别连接失败的具体原因（认证失败/连接拒绝/超时）
- [x] 技能**永久终止**任务，不执行任何后续步骤
- [x] 错误信息清晰说明失败原因

---

### TC-003: 关系库类型识别与中止

**测试目标**: 验证技能能正确识别关系库并中止任务

**前提条件**: 用户请求在关系库 `trade_system.orders` 上执行异常检测

**用户输入**:
```
请检测 trade_system.orders 表中的异常数据。
```

**预期行为**:
1. 技能显示安全确认提示
2. 用户同意后，技能执行前置验证
3. 技能识别目标数据库 `trade_system` 为 **RELATIONAL** 类型（非 TIME SERIES）
4. 技能执行**步骤 3**时检测到数据库类型不符
5. 技能**永久终止任务**并显示错误信息

**预期输出**:
```
错误：该目标数据库 trade_system 不是 TIME SERIES 数据库。
异常检测仅支持时序数据库。
任务已终止。
```

**验证点**:
- [x] 技能正确识别 `trade_system` 为关系库
- [x] 技能在步骤 3 触发终止条件 `NOT_TS_DATABASE`
- [x] 任务正确中止，无后续操作

---

### TC-004: 仅非数值型字段识别与中止

**测试目标**: 验证技能能正确识别仅有非数值型字段的表并中止

**前提条件**: 用户请求对 `ts_db.charger_data` 表的`fault_info` 列（非数值型）进行异常检测

**用户输入**:
```
请检测 ts_db.charger_data 表中charger c002的fault_info列数据是否存在异常。
```

**预期行为**:
1. 技能显示安全确认提示
2. 用户同意后，技能执行前置验证和意图分析
3. 技能识别目标列`fault_info` (VARCHAR) 均为**非数值类型**
4. 技能执行**步骤 3**时检测到所有过滤列为非数值类型
5. 技能**永久终止任务**并显示错误信息

**预期输出**:
```
错误：表 ts_db.charger_data 的所有过滤列 (fault_info) 都是非数值类型。
异常检测仅支持 INTEGER、FLOAT、DOUBLE、DECIMAL、NUMERIC 类型的列。
任务已终止。
```

**验证点**:
- [x] 技能正确识别 `fault_info` (VARCHAR) 为非数值类型
- [x] 技能在步骤 3 触发终止条件 `NO_NUMERIC_COLUMNS`
- [x] 任务正确中止

---

### TC-005: 非数值与数值型字段混合场景处理

**测试目标**: 验证技能能正确筛除非数值型字段，仅对数值型字段执行异常检测

**前提条件**: 用户请求对 `ts_db.charger_data` 表的多个列进行异常检测，包含数值型和非数值型

**用户输入**:
```
请检测 ts_db.charger_data 表中charger c002的current_amp、voltage_v和fault_info等列数据是否存在异常。
```

**预期行为**:
1. 技能显示安全确认提示
2. 用户同意后，技能执行前置验证和意图分析
3. 技能识别目标列：
   - `current_amp` (INT4) - 数值型，**参与检测**
   - `voltage_v` (FLOAT8) - 数值型，**参与检测**
   - `fault_info` (VARCHAR) - 非数值型，**将被筛除**
4. 技能在步骤 5 (SQL 优化) 移除非数值列，仅保留 `ts`, `current_amp`, `voltage_v`
5. 技能对数值型字段执行 3-Sigma 异常检测
6. 技能生成包含 `current_amp` 和 `voltage_v` 检测结果的报告

**预期输出**:
```
检测完成。
- current_amp: 检测到 N1 个异常点
- voltage_v: 检测到 N2 个异常点
注：is_charging (BOOL) 和 fault_info (VARCHAR) 为非数值类型，已自动筛除。
```

**验证点**:
- [x] 技能正确识别非数值型列并筛除
- [x] 技能正确保留数值型列进行检测
- [x] 检测结果不包含非数值型列

---

### TC-006: 库名缺失时自动查找

**测试目标**: 验证技能能在用户未提供完整库名时，自动查找表所属的数据库

**前提条件**: 用户仅提供表名，未提供库名

**用户输入**:
```
请检测 device_metrics 表中设备A-001 temperature列的数据是否存在异常。
```

**预期行为**:
1. 技能显示安全确认提示
2. 用户同意后，技能执行前置验证
3. 技能检测到用户未指定数据库，执行元数据查询
4. 技能查询所有数据库，识别 `device_metrics` 表位于 `factory_monitor` 数据库
5. 技能验证 `factory_monitor` 为 TIME SERIES 数据库
6. 技能继续执行异常检测流程
7. 技能生成检测报告

**预期输出**:
```
信息：未指定数据库，自动查找表所属库。
查询结果：device_metrics 表位于 factory_monitor 数据库。
继续执行异常检测...
```

**验证点**:
- [x] 技能能自动识别 `device_metrics` 属于 `factory_monitor`
- [x] 技能正确验证目标库为 TIME SERIES 类型
- [x] 异常检测流程正常执行

---

### TC-007: 错误库表名识别与中止

**测试目标**: 验证技能能在用户提供的库表名不存在时中止任务

**前提条件**: 用户提供了一个不存在的数据库或表名

**用户输入**:
```
请检测 factory_monitor.nonexistent_table 表中的异常数据。
```

**预期输出**:
```
错误：未找到指定的表 factory_monitor.nonexistent_table。
可用表：device_alerts, device_metrics
任务已终止。
```

**验证点**:
- [x] 技能能识别不存在的数据库
- [x] 技能能识别不存在的表
- [x] 技能在步骤 2 触发终止条件 `DB_NOT_FOUND` 或 `TABLE_NOT_FOUND`
- [x] 任务正确中止

---

### TC-008: 确定主标签下单一数值字段异常检测

**测试目标**: 验证技能能正确检测指定主标签下单个数值列的异常

**前提条件**: 用户指定特定主标签值和单个数值列

**用户输入**:
```
请检测 factory_monitor.device_metrics 表中设备A-001的humidity列最近10000条数据是否存在异常。
```

**预期行为**:
1. 技能显示安全确认提示
2. 用户同意后，技能执行前置验证
3. 技能识别：
   - 目标库: `factory_monitor` (TIME SERIES)
   - 目标表: `device_metrics`
   - 主标签: `device_id`
   - 过滤条件: `device_id = 'A-001'`
   - 检测列: `temperature` (FLOAT4)
4. 技能执行步骤 5-13（Single Tag 模式）
5. 技能生成仅包含 `temperature` 列异常检测结果的报告

**预期输出**:
```
检测报告 - factory_monitor.device_metrics
主标签: device_id = 'A-001'
检测列: temperature

检测方法: 3-Sigma
总数据点: XXXX
检测到的异常数: N

[异常点详情表格]
```

**验证点**:
- [x] 技能正确处理指定主标签过滤
- [x] 技能仅检测指定数值列
- [x] 报告格式正确

---

### TC-009: 无时间窗口时自动添加 LIMIT 1000

**测试目标**: 验证技能在用户未指定时间窗口时，能在步骤 5 自动向 SQL 添加 `LIMIT 1000` 子句，防止数据量过大

**前提条件**: 用户请求检测 `factory_monitor.device_metrics` 表的 `humidity` 列异常，但**未指定时间范围过滤条件**

**用户输入**:
```
请检测 factory_monitor.device_metrics 表中设备A-001的humidity列数据是否存在异常。
```
（注意：用户**未**指定时间范围，如 `WHERE ts > '2023-05-01' AND ts < '2023-05-31'`）

**预期行为**:
1. 技能显示安全确认提示
2. 用户同意后，技能执行前置验证
3. 技能识别目标列和过滤条件
4. 技能执行步骤 5 (SQL Refinement) 时检测到 **WHERE 子句中无时间过滤条件**
5. 技能自动添加 `ORDER BY ts DESC LIMIT 1000` 至 refined_sql_limited
6. 技能执行步骤 6 包装为子查询
7. 技能展示最终 SQL（含 LIMIT 1000）给用户确认

**预期输出**:

步骤 5 生成的 refined_sql_limited:
```sql
SELECT ts, humidity
FROM factory_monitor.device_metrics
WHERE device_id = 'A-001'
ORDER BY ts DESC
LIMIT 1000
```

步骤 6 包装后的最终 SQL (步骤 7 展示):
```sql
SELECT * FROM (
    SELECT ts, humidity
    FROM factory_monitor.device_metrics
    WHERE device_id = 'A-001'
    ORDER BY ts DESC
    LIMIT 1000
) AS anomaly_subquery
ORDER BY ts ASC
```

**验证点**:
- [x] 技能在步骤 5 检测到无时间过滤条件
- [x] 技能自动添加 `ORDER BY ts DESC LIMIT 1000`
- [x] LIMIT 1000 正确添加在原始 SELECT 语句中（非外层包装）
- [x] 步骤 6 包装后 LIMIT 1000 保留在子查询内
- [x] 步骤 7 正确展示含 LIMIT 的最终 SQL

**关键验证 — 步骤 8 跳过 COUNT 检查**:
由于 refined_sql_limited 已包含 `LIMIT 1000`，步骤 8 的数据量检查应**被跳过**，技能直接进入步骤 9 执行。

**SQL 结构验证**:
```
SELECT * FROM (
    SELECT <timestamp>, <numeric_columns>
    FROM <table>
    WHERE <primary_tag> = '<value>'
    ORDER BY <timestamp> DESC
    LIMIT 1000          <-- 自动添加，防止全表扫描
) AS anomaly_subquery
ORDER BY <timestamp> ASC
```

---

### TC-010: 数据量过大导致任务终止

**测试目标**: 验证技能在用户指定的时间范围内数据量超过 100,000 条时，能正确终止任务

**前提条件**: 用户请求检测 `factory_monitor.device_metrics` 表中 `temperature` 列异常，并指定了较大时间范围，导致查询结果超过 100,000 条

**用户输入**:
```
请检测 factory_monitor.device_metrics 表中设备A-001的 temperature 列最近两个月的数据是否存在异常。
```

**预期行为**:
1. 技能显示安全确认提示
2. 用户同意后，技能执行前置验证
3. 技能识别目标列和过滤条件
4. 技能执行步骤 5-8：
   - 生成 refined_sql_limited（包含时间范围过滤）
   - 由于有时间过滤条件，**不添加** `LIMIT 1000`
5. 技能执行步骤 8 COUNT 检查
6. 技能查询数据量，发现 **> 100,000**
7. 技能**永久终止任务**并显示错误信息

**预期输出**:
```
数据量过大（大于100,000 条），无法执行异常检测。
建议先对数据进行时间范围筛选或降采样后再试。
任务已终止。
```

**关键验证**:
- [x] 技能在步骤 5 **不自动添加** `LIMIT 1000`（因为用户已指定时间范围）
- [x] 技能正确执行步骤 8 的 COUNT 检查
- [x] 技能正确检测到数据量超过 100,000 阈值
- [x] 技能显示清晰的错误信息和改善建议

**SQL 流程示意**:
```
步骤 5: refined_sql_limited
  (用户已指定时间范围，不添加 LIMIT)
  SELECT ts, temperature
  FROM factory_monitor.device_metrics
  WHERE device_id = 'A001'
    AND ts >= '2023-04-01' AND ts < '2023-06-01'

步骤 8: COUNT 检查
  SELECT COUNT(*) FROM (...) AS count_subquery
  → 结果: 150,000 > 100,000 → 终止
```

---

### TC-011: 根据字段 COMMENT 规则过滤异常值

**测试目标**: 验证技能能正确解析 `temperature` 列 COMMENT 中的规则 "Normal temperature range: [7, 80]"，并据此过滤异常检测结果

**前提条件**: 用户请求检测 `factory_monitor.device_metrics` 表中 `temperature` 列的异常，且该列有 COMMENT 规则

**列 COMMENT 信息**:
```
COMMENT ON COLUMN device_metrics.temperature IS 'Normal temperature range: [7, 80]';
```

**用户输入**:
```
请检测 factory_monitor.device_metrics 表中设备A-001的temperatur列数据是否存在异常。
```

**预期行为**:
1. 技能显示安全确认提示
2. 用户同意后，技能执行前置验证
3. 技能识别目标列 `temperature` (FLOAT4)
4. 技能执行步骤 5-11，执行 3-Sigma 异常检测
5. 技能在步骤 12 执行 `SHOW COLUMNS FROM factory_monitor.device_metrics WITH COMMENT`
6. 技能解析 COMMENT 提取规则：`range [7, 80]`
7. 技能在步骤 13 应用规则过滤：
   - 保留 3-Sigma 检测到的**超出 [7, 80] 范围**的异常点
   - 移除 3-Sigma 检测到的**在 [7, 80] 范围内**的点（这些点不违反 COMMENT 规则）
8. 技能生成包含过滤后异常点的报告

**预期输出**:
```
检测报告 - factory_monitor.device_metrics
主标签: device_id = 'A-001'
检测列: temperature

--- temperature ---
检测方法: 3-Sigma
总数据点: XXXX

规则: Normal temperature range: [7, 80]

3-Sigma 检测异常数: N_raw
规则过滤后异常数: N_filtered

[异常点详情表格 - 仅包含超出 [7, 80] 范围的值]

注: [7, 80] 范围内但在 3-Sigma 边界外的点已根据 COMMENT 规则过滤
```

**规则解析验证**:
- [x] 技能正确执行 `SHOW COLUMNS FROM factory_monitor.device_metrics WITH COMMENT`
- [x] 技能正确解析 COMMENT 中的范围规则 `[7, 80]`
- [x] 技能正确识别 "Normal temperature range" 语义

**过滤逻辑验证**:
- [x] 技能保留超出上限 (> 80) 的异常点
- [x] 技能保留超出下限 (< 7) 的异常点
- [x] 技能移除在范围内 [7, 80] 的 3-Sigma 异常点

**示例场景**:
假设 3-Sigma 检测到以下异常点：
| 时间 | temperature | 3-Sigma判定 | 规则过滤 |
|------|-------------|-------------|---------|
| 2023-05-05 14:00:00 | 85.3 | 异常 | ✅ 保留 (>80) |
| 2023-05-08 03:00:00 | 4.2 | 异常 | ✅ 保留 (<7) |
| 2023-05-10 09:00:00 | 75.5 | 异常 | ❌ 过滤 (在[7,80]内) |
| 2023-05-15 16:00:00 | 12.3 | 异常 | ❌ 过滤 (在[7,80]内) |

---

### TC-012: 确定主标签下两个数值字段异常检测

**测试目标**: 验证技能能正确检测指定主标签下多个数值列的异常

**前提条件**: 用户指定特定主标签值和两个数值列

**用户输入**:
```
请检测factory_monitor.device_metrics表中设备A-001的temperature和humidity列数据是否存在异常。
```

**预期行为**:
1. 技能显示安全确认提示
2. 用户同意后，技能执行前置验证
3. 技能识别：
   - 目标库: `factory_monitor` (TIME SERIES)
   - 目标表: `device_metrics`
   - 主标签: `device_id`
   - 过滤条件: `device_id = 'A-001'`
   - 检测列: `temperature` (FLOAT4), `humidity` (FLOAT4)
4. 技能执行步骤 5-13（Single Tag 模式）
5. 技能分别对 `temperature` 和 `humidity` 执行 3-Sigma 检测
6. 技能生成包含两列异常检测结果的报告

**预期输出**:
```
检测报告 - factory_monitor.device_metrics
主标签: device_id = 'A-001'
检测列: temperature, humidity

--- temperature ---
检测方法: 3-Sigma
总数据点: XXXX
检测到的异常数: N1

--- humidity ---
检测方法: 3-Sigma
总数据点: XXXX
检测到的异常数: N2
```

**验证点**:
- [x] 技能正确处理两个数值列的检测
- [x] 两列独立执行异常检测
- [x] 报告包含两列各自的检测结果

---

### TC-013: 所有主标签下单一数值字段异常检测

**测试目标**: 验证技能能正确检测所有主标签值下单个数值列的异常

**前提条件**: 用户未指定主标签值，技能需遍历所有主标签

**用户输入**:
```
请检测 factory_monitor.device_metrics 表中所有设备的 temperature 列数据是否存在异常。
```

**预期行为**:
1. 技能显示安全确认提示
2. 用户同意后，技能执行前置验证
3. 技能识别：
   - 目标库: `factory_monitor` (TIME SERIES)
   - 目标表: `device_metrics`
   - 主标签: `device_id`（未指定具体值）
   - 检测列: `temperature` (FLOAT4)
4. 技能执行步骤 4（All Tags 模式）：
   - 查询所有 distinct 主标签值
   - 获取标签列表: A-001, A-002, A-003, A-004, A-005, A-006, A-007, A-008, B-002, C-003, ...
5. 技能对每个主标签值执行步骤 5-13
6. 技能聚合所有主标签的检测结果
7. 技能生成汇总报告

**预期输出**:
```
检测报告 - factory_monitor.device_metrics
检测列: temperature
主标签数量: N (已遍历所有设备)

--- 汇总 ---
A-001: 检测到 N1 个异常
A-002: 检测到 N2 个异常
...
C-003: 检测到 Nk 个异常

总异常点: Total_M
```

**验证点**:
- [x] 技能正确获取所有主标签值
- [x] 技能对每个主标签独立执行检测
- [x] 报告按主标签分组展示结果

---

### TC-014: 所有主标签下两个以上数值字段异常检测

**测试目标**: 验证技能能正确检测所有主标签值下多个数值列的异常

**前提条件**: 用户未指定主标签值，技能需遍历所有主标签，并对两个以上数值列分别检测

**用户输入**:
```
请检测 factory_monitor.device_metrics 表中所有设备的 temperature 和 humidity 列数据是否存在异常。
```

**预期行为**:
1. 技能显示安全确认提示
2. 用户同意后，技能执行前置验证
3. 技能识别：
   - 目标库: `factory_monitor` (TIME SERIES)
   - 目标表: `device_metrics`
   - 主标签: `device_id`（未指定具体值）
   - 检测列: `temperature` (FLOAT4), `humidity` (FLOAT4)
4. 技能执行步骤 4（All Tags 模式）
5. 技能对每个主标签值执行检测，分别处理两个数值列
6. 技能生成按主标签和按列分组的汇总报告

**预期输出**:
```
检测报告 - factory_monitor.device_metrics
检测列: temperature, humidity
主标签数量: N

--- device_id = A-001 ---
  temperature: N1 个异常
  humidity: M1 个异常

--- device_id = A-002 ---
  temperature: N2 个异常
  humidity: M2 个异常
...

--- 汇总 ---
temperature 总异常: Total_T
humidity 总异常: Total_H
```

**验证点**:
- [x] 技能正确处理多列多标签组合
- [x] 每个标签-列组合独立执行检测
- [x] 报告结构清晰，按标签分组

---

### TC-015: 指定格式输出异常检测报告

**测试目标**: 验证技能能按用户指定的格式输出检测报告

**前提条件**: 用户指定输出格式（Markdown 或 HTML）

**用户输入**:
```
请检测 factory_monitor.device_metrics 表中所有设备的 temperature 和 humidity 列数据是否存在异常，并以 Markdown 格式输出报告。
```

**预期行为**:
1. 技能显示安全确认提示
2. 用户同意后，技能执行前置验证
3. 技能识别目标列和过滤条件
4. 技能执行异常检测流程
5. 技能在步骤 14 询问用户确认输出格式
6. 用户确认 Markdown 格式
7. 技能使用 `report-template.md` 生成报告
8. 技能将报告保存至 `/tmp/dt-report-<timestamp>.md`
9. 技能删除临时文件，保留最终报告

**预期输出**:
```
检测报告已生成并保存至: /tmp/dt-report-20230603000000.md
```

**报告内容示例**:
```markdown
# detection report for factory_monitor.device_metrics

## basic information
- data table: factory_monitor:device_metrics
- detection time: 2023-06-03 00:00:00
- data time span: 2023-05-01 00:00:00 ~ 2023-05-31 23:59:59

## A-001

### detection column: temperature
#### detection rules:
- detection method: 3-sigma
- column comment rules: Normal temperature range: [7, 80]

#### detection result summary
- total row count: 1000
- 3-sigma anomaly count: 5
- final anomaly count: 3

#### 3-sigma statistic information
- Auto-recognized Sampling Frequency: 小时
- Calculated Period (period): 24
- Upper Threshold: 75.5
- Lower Threshold: 10.2

#### DESCRIBE 3-sigma anomaly points
| 序号 | 时间 | 值 |
|------|------|-----|
| 1 | 2023-05-05 14:00:00 | 85.3 |
...

---
*This report is generated by the KaiwuDB*
```

**验证点**:
- [x] 技能按用户指定格式生成报告
- [x] 报告包含所有必需信息
- [x] 临时文件正确清理
- [x] 最终报告保留在 `/tmp/`

---

## 附录：测试数据准备脚本

### 创建测试数据库和表

```sql
-- 时序库 factory_monitor 已存在
-- 表 device_metrics 已存在

-- 时序库 ts_db 已存在
-- 表 charger_data 已存在

-- 关系库 trade_system 已存在
-- 表 orders 已存在
```

### 验证测试环境

```sql
-- 验证数据库类型
SHOW DATABASES;

-- 验证 factory_monitor 包含 device_metrics
SHOW TABLES FROM factory_monitor;

-- 验证 ts_db 包含 charger_data
SHOW TABLES FROM ts_db;

-- 验证 trade_system 包含 orders
SHOW TABLES FROM trade_system;

-- 验证列类型
DESCRIBE factory_monitor.device_metrics;
DESCRIBE ts_db.charger_data;
DESCRIBE trade_system.orders;
```

---

## 测试执行清单

| 测试用例 | 测试目标 | 预期结果 | 执行状态 |
|---------|---------|---------|---------|
| TC-001 | 验证技能能在用户拒绝安全确认时正确中止任务 | 技能正确识别并终止 | ⬜ |
| TC-002 | 错误连接凭证导致任务终止 | 技能正确识别并终止 | ⬜ |
| TC-003 | 关系库类型识别与中止 | 技能正确识别并终止 | ⬜ |
| TC-004 | 仅非数值型字段识别与中止 | 技能正确识别并终止 | ⬜ |
| TC-005 | 非数值与数值型字段混合处理 | 技能筛除非数值列 | ⬜ |
| TC-006 | 库名缺失时自动查找 | 技能自动定位数据库 | ⬜ |
| TC-007 | 错误库表名识别与中止 | 技能正确识别并终止 | ⬜ |
| TC-008 | 确定主标签下单一数值字段检测 | 技能正确检测 | ⬜ |
| TC-009 | 无时间窗口时自动添加 LIMIT 1000 | 技能自动添加 LIMIT 子句 | ⬜ |
| TC-010 | 数据量过大导致任务终止 | 技能正确识别并终止 | ⬜ |
| TC-011 | 根据字段 COMMENT 规则过滤异常值 | 技能解析并应用规则过滤 | ⬜ |
| TC-012 | 确定主标签下两个数值字段检测 | 技能正确检测 | ⬜ |
| TC-013 | 所有主标签下单一数值字段检测 | 技能正确检测 | ⬜ |
| TC-014 | 所有主标签下两个数值字段检测 | 技能正确检测 | ⬜ |
| TC-015 | 指定格式输出报告 | 技能按格式输出 | ⬜ |

