# KaiwuDB Inspection Scripts

## 环境准备

```bash
cd skills/kwdb-intelligent-inspection/scripts
python3 -m venv .venv
.venv/bin/pip install pytest pytest-cov -q
```

## 执行脚本

### get_kwdb_statements.py

获取慢 SQL 语句统计（通过 `/_status/statements` API）。

```bash
.venv/bin/python get_kwdb_statements.py --host <HOST> --port <PORT> [--limit N] [--min-latency-ms MS] [--json]
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--host` | KaiwuDB admin host | localhost |
| `--port` | KaiwuDB admin port | 8080 |
| `--limit N` | 显示 top N 条慢 SQL | 10 |
| `--min-latency-ms` | 最小服务延迟阈值(ms) | 0 |
| `--sort-by` | 排序字段: service_lat/run_lat/plan_lat/count | service_lat |
| `--json` | 输出原始 JSON | false |

### get_kwdb_ts_metrics.py

获取时序指标（通过 `/ts/query` API）。

```bash
.venv/bin/python get_kwdb_ts_metrics.py --host <HOST> --port <PORT> [--start TIME] [--end TIME] [--sample N] [--metric NAME] [--json]
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--host` | KaiwuDB admin host | localhost |
| `--port` | KaiwuDB admin port | 8080 |
| `--start` | 开始时间 (ISO 或 unix ns) | 1小时前 |
| `--end` | 结束时间 (ISO 或 unix ns) | now |
| `--sample` | 采样间隔(秒) | 60 |
| `--metric` | 按指标名过滤 (可重复) | 全部 |
| `--json` | 输出原始 JSON | false |

## 执行测试

```bash
.venv/bin/python -m pytest test_get_kwdb_statements.py -v
```

## 带覆盖率报告

```bash
.venv/bin/python -m pytest test_get_kwdb_statements.py -v --cov=get_kwdb_statements --cov-report=term-missing
```

## 测试结构

| 测试类 | 覆盖函数 |
|--------|----------|
| `TestParseStatements` | `parse_statements()` |
| `TestFilterAndSort` | `filter_and_sort()` |
| `TestFetchStatements` | `fetch_statements()` |
| `TestFormatStatement` | `format_statement()` |
| `TestMain` | `main()` |

## 当前覆盖率

- **98%** (仅 `if __name__ == "__main__":` 入口保护未覆盖)
