#!/usr/bin/env python3
"""Return the current local time as a 14-digit timestamp (yyyyMMddHHmmss).

Stdlib only — no project venv required. Invoke directly with:

    python3 scripts/get_local_timestamp.py

No arguments. Exits 0 on success and prints the timestamp to stdout.
"""
from datetime import datetime


def main() -> int:
    print(datetime.now().strftime("%Y%m%d%H%M%S"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
