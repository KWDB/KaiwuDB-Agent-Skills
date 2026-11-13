# Functional Tests

本文档定义 `kwdb-ts-anomaly-detection` 技能的端到端功能测试用例，验证技能在完整流程下的输出与产物。

触发与终止类用例见 `trigger-tests.md`。

---

## FT-001: 单主标签 + 多数值列的完整检测流程

**测试目标**: 验证技能在指定主标签、多个数值列场景下的完整流程（步骤 1-15）正确串联。

**前提条件**: 时序库 `factory_monitor`，表 `device_metrics`，主标签 `device_id`，数值列 `temperature`、`humidity`。

**用户输入**:
```
请检测 factory_monitor.device_metrics 表中设备 A-001 的 temperature 和 humidity 列最近 1000 条数据是否存在异常。
```

**预期行为**:
1. 步骤 0 显示安全确认提示，用户回复 "I AGREE"
2. 步骤 1 收集 host / port / username / password，用 `SELECT 1` 验证连接
3. 步骤 2 依据用户意图生成 SQL，列名与元数据一致
4. 步骤 5 保留 `ts` + `temperature` + `humidity`，追加 `ORDER BY ts DESC LIMIT 1000`
5. 步骤 6 包装为 `SELECT * FROM (...) AS anomaly_subquery ORDER BY ts ASC`
6. 步骤 7 展示最终 SQL
7. 步骤 8 因 `refined_sql_limited` 含 `LIMIT`，跳过 COUNT 检查
8. 步骤 9 结果落盘 `/tmp/sql-result-<YYYYMMDDHHmmss>`
9. 步骤 11 执行 `python scripts/3-sigma-detection.py --input <result> --output <detect-result>`
10. 步骤 12-13 读取列注释并按规则过滤
11. 步骤 14 按用户选择的格式输出报告
12. 步骤 15 清理临时文件，仅保留最终报告

**预期输出**:
```
检测报告 - factory_monitor.device_metrics
主标签: device_id = 'A-001'
检测列: temperature, humidity

--- temperature ---
检测方法: 3-Sigma
总数据点: 1000
3-sigma 异常数: N1
最终异常数: M1

--- humidity ---
检测方法: 3-Sigma
总数据点: 1000
3-sigma 异常数: N2
最终异常数: M2
```

**验证点**:
- [x] 两列分别独立执行 3-Sigma 检测
- [x] 报告分别给出 3-sigma 异常数与规则过滤后的最终异常数
- [x] 最终 SQL 在执行前已展示给用户
- [x] 临时文件已清理，仅保留报告

---

## FT-002: 全部主标签模式的汇总检测

**测试目标**: 验证未指定主标签时，技能按步骤 4 遍历所有主标签值并汇总报告。

**用户输入**:
```
请检测 factory_monitor.device_metrics 表中所有设备的 temperature 列最近 1000 条数据是否存在异常。
```

**预期行为**:
1. 步骤 4 通过元数据查询获取主标签列名，并执行
   `SELECT DISTINCT device_id FROM factory_monitor.device_metrics`（不写结果文件）
2. 对每个主标签值追加 `AND device_id = '<value>'` 后重复步骤 5-13
3. 每次迭代的结果文件为 `/tmp/sql-result-<safe_tag_value>-<YYYYMMDDHHmmss>`
4. 步骤 14 汇总所有主标签的结果，按主标签分组输出

**预期输出**:
```
检测报告 - factory_monitor.device_metrics
检测列: temperature
主标签数量: N

--- A-001 ---
temperature: N1 个异常
--- A-002 ---
temperature: N2 个异常
...

总异常点: Total
```

**验证点**:
- [x] 元数据查询未写入结果文件
- [x] 每个主标签值独立执行检测并记录结果
- [x] 报告按主标签分组并给出汇总

---

## FT-003: HTML 报告生成流程

**测试目标**: 验证用户选择 HTML 格式时，报告生成链路完整可用。

**用户输入**:
```
请检测 factory_monitor.device_metrics 表中设备 A-001 的 temperature 列最近 1000 条数据是否存在异常，输出 HTML 报告。
```

**预期行为**:
1. 步骤 14 确认输出格式为 HTML
2. 按 `references/report-template-html.md` 填充 JSON 模板，写入 `/tmp/report-json-<YYYYMMDDHHmmss>.json`
3. 执行 `python scripts/html-report-gen.py --input /tmp/report-json-<YYYYMMDDHHmmss>.json --output /tmp/dt-report-<YYYYMMDDHHmmss>.html`
4. 确认 HTML 文件生成成功

**预期输出**:
```
检测报告已生成: /tmp/dt-report-20230603000000.html
```

**验证点**:
- [x] JSON 模板字段填充完整（db_name / table_name / detection_time / time_span / detection_method / tags）
- [x] HTML 文件确实由脚本生成，路径在 `/tmp/` 下
- [x] 报告按主标签分组展示

---

## FT-004: 步骤 7 执行前展示最终 SQL

**测试目标**: 验证技能在执行数据查询前必须展示最终 SQL，不得静默执行。

**用户输入**:
```
请检测 factory_monitor.device_metrics 表中设备 A-001 的 temperature 列最近 1000 条数据是否存在异常。
```

**预期行为**:
1. 技能在执行前输出最终 SQL
2. SQL 结构符合步骤 6 的包装要求
3. 随后才执行查询并落盘结果

**预期输出**:
```sql
SELECT * FROM (
    SELECT ts, temperature
    FROM factory_monitor.device_metrics
    WHERE device_id = 'A-001'
    ORDER BY ts DESC
    LIMIT 1000
) AS anomaly_subquery
ORDER BY ts ASC
```

**验证点**:
- [x] 最终 SQL 出现在结果文件生成之前
- [x] `LIMIT 1000` 位于子查询内部，外层仅按时间升序
- [x] SQL 中不含非检测需要的列

---

## FT-005: 元数据查询不落盘

**测试目标**: 验证所有元数据查询（库 / 表 / 列 / 主标签 / 列注释）都不写结果文件。

**用户输入**:
```
请检测 device_metrics 表中设备 A-001 的 temperature 列数据是否存在异常。
```
（未指定数据库）

**预期行为**:
1. 执行 `SHOW DATABASES;`、`SHOW TABLES FROM factory_monitor;`、`DESCRIBE factory_monitor.device_metrics;`
2. 执行 `SELECT DISTINCT device_id FROM factory_monitor.device_metrics`
3. 执行 `SHOW COLUMNS FROM factory_monitor.device_metrics WITH COMMENT`
4. 上述命令均不带输出文件参数，结果只打印到 stdout

**验证点**:
- [x] 元数据查询命令未携带结果文件参数
- [x] 未在 `/tmp/` 生成元数据结果文件
- [x] 仅数据查询结果落盘

---

## FT-006: 临时文件清理

**测试目标**: 验证步骤 15 清理所有中间文件，只保留最终报告。

**预期行为**:
1. 任务结束前检查 `/tmp/` 下的中间产物
2. 删除 `/tmp/sql-result-*`、`/tmp/detect-result-*`、`/tmp/report-json-*`
3. 保留最终报告 `/tmp/dt-report-<YYYYMMDDHHmmss>.*`

**验证点**:
- [x] 结果文件与检测结果文件已删除
- [x] 报告中间 JSON 已删除
- [x] 最终报告文件仍然存在

---

## 测试执行清单

| 测试用例 | 测试目标 | 预期结果 | 执行状态 |
|---------|---------|---------|---------|
| FT-001 | 单主标签多数值列完整流程 | 流程串联正确 | ⬜ |
| FT-002 | 全部主标签汇总检测 | 按标签分组汇总 | ⬜ |
| FT-003 | HTML 报告生成 | 产物落盘 /tmp | ⬜ |
| FT-004 | 执行前展示最终 SQL | SQL 先于执行 | ⬜ |
| FT-005 | 元数据查询不落盘 | 无元数据结果文件 | ⬜ |
| FT-006 | 临时文件清理 | 仅保留报告 | ⬜ |
