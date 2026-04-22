# 测试文档

## 环境准备

```bash
cd skills/kwdb-intelligent-inspection/scripts
python3 -m venv .venv
.venv/bin/pip install pytest pytest-cov -q
```

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
