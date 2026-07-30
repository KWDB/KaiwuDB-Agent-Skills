# Internal Test Scripts for kwdb-data-migration

This directory contains test helper scripts for the kwdb-data-migration skill.

## Files

- `mock_server.py`: Mock KDTS server for local testing, simulates all 10 API endpoints
- `test_migration_flow.py`: End-to-end migration flow test script

## Usage

### Start Mock Server

```bash
# Default port (8989)
python mock_server.py

# Custom port
python mock_server.py --port 9999
```

### Run Migration Flow Test

```bash
# Full test suite
python test_migration_flow.py

# With custom mock server port
python test_migration_flow.py --port 9999
```

## Directory Structure

```
internal/tests/kwdb-data-migration/
├── scripts/
│   ├── __init__.py
│   ├── mock_server.py
│   └── test_migration_flow.py
├── functional-tests.md
└── trigger-tests.md
```

## Notes

- These are internal test utilities, not part of the published skill
- The scripts import modules from `skills/kwdb-data-migration/scripts/`
- Test logs are written to `test_migration.log` in the current working directory
