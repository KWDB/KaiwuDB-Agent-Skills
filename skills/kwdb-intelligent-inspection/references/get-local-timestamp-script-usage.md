---
name: get_local_timestamp.py script usage
description: Exact CLI reference for the timestamp helper. Read before calling the script for the first time.
---

# `get_local_timestamp.py` — CLI Reference

依赖: Python 标准库（`datetime`）。

Entry point: `scripts/get_local_timestamp.py` (no arguments).

## Synopsis

```
python3 scripts/get_local_timestamp.py
```

No arguments. The script exits 0 on success and prints the timestamp to stdout.

## Output

A single line on stdout: `yyyyMMddHHmmss` (local timezone).

Exit code 0 on success.

## Common Mistakes

- **Using `datetime.utcnow()` or a training-data guess**: rejected by callers
  (see `SKILL.md` workflow). Always call this script instead.
- **Reformatting the output**: the timestamp is consumed verbatim for
  `report-yyyyMMddHHmmss.*` filename segments; do not edit it.
