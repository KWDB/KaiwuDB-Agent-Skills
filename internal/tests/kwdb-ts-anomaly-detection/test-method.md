# Test Method

本文档定义 `kwdb-ts-anomaly-detection` 技能的测试方法。

## Test Layers

1. **Trigger Tests** - 验证技能在触发类场景下的行为与终止条件（`trigger-tests.md`）
2. **Functional Tests** - 验证端到端流程与产物（`functional-tests.md`）
3. **Regression Tests** - 验证技能不会违反 `references/constraints.md`（`regression-prompts.md`）
4. **Baseline Comparison** - 验证技能相对通用回答的增量（`baseline-comparison.md`）

## Environment

| 项目 | 说明 |
|------|------|
| 数据库类型 | TIME SERIES（关系库用于反向验证） |
| 时序库 | `factory_monitor`、`ts_db` |
| 关系库 | `trade_system` |
| 表 | `factory_monitor.device_metrics`、`ts_db.charger_data`、`trade_system.orders` |
| 客户端 | `scripts/kwdb_sql_execute.py`、`scripts/3-sigma-detection.py`、`scripts/html-report-gen.py` |
| 工作目录 | 技能根目录（`skills/kwdb-ts-anomaly-detection/`） |

## Execution Order

1. 准备测试库表（见下节 SQL），确认列类型与主标签
2. 执行 `trigger-tests.md`：确认每个用例都走到预期的终止条件
3. 执行 `functional-tests.md`：确认流程串联、SQL 结构、产物路径
4. 执行 `regression-prompts.md`：确认每个禁止项都没有发生
5. 执行 `baseline-comparison.md`：逐条确认"当前目标必须"项全部满足
6. 记录每个用例的实际输出，与预期输出逐项比对

## Test Data Setup

```sql
-- 时序库
CREATE TABLE device_metrics (
    ts TIMESTAMPTZ(3) NOT NULL,
    temperature FLOAT4 NULL,
    humidity FLOAT4 NULL,
    power_consumption FLOAT8 NULL
) TAGS (
    device_id VARCHAR(32) NOT NULL,
    workshop VARCHAR(64),
    line_number INT2
) PRIMARY TAGS(device_id);
COMMENT ON COLUMN device_metrics.temperature IS 'Normal temperature range: [7, 80]';

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

-- 关系库（反向验证用）
CREATE TABLE orders (
    order_id INT8 NOT NULL DEFAULT unique_rowid(),
    user_id INT4 NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    order_status INT2 NOT NULL DEFAULT 0,
    create_time TIMESTAMP NOT NULL DEFAULT current_timestamp(),
    pay_time TIMESTAMP NULL
);
```

## Pass / Fail Criteria

### Pass

- 安全确认未通过时任务立即终止，无任何数据库操作
- 所有 SQL 经 `scripts/kwdb_sql_execute.py` 执行，元数据查询不落盘
- 无时间过滤条件时自动补 `ORDER BY <ts> DESC LIMIT 1000`
- 无 LIMIT 时执行 COUNT 检查，超过 100,000 条终止并给出建议
- 最终 SQL 在执行前展示给用户，结构符合步骤 6 包装要求
- 列注释规则参与过滤，3-sigma 异常数与最终异常数分别统计
- 报告格式先确认再生成，产物落在 `/tmp/`
- 任务结束清理全部中间文件，仅保留最终报告

### Fail

- 跳过安全确认或未确认即执行查询
- 使用 MCP 工具执行 SQL
- 擅自创建库表、写入数据或截断中间输出
- 用相近名称替代用户给定的库表列并继续执行
- 省略 `LIMIT 1000` 或省略 COUNT 检查
- 未按列注释规则过滤，或只给出单一异常计数
- 编造异常点、阈值或统计信息
- 在无异常点时继续后续步骤
- 未经确认直接生成 PDF / HTML 报告
- 未清理中间结果文件

## Real Environment Validation

- 每次测试记录：用例编号、实际输出、结果文件路径、最终报告路径
- 实际运行结果回填到各用例的"执行状态"列
- 与基线（无技能引导）各执行一次，差异填入 `baseline-comparison.md`
