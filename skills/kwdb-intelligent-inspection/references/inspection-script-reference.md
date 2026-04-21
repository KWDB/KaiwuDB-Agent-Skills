# kwdb-intelligent-inspection Script Reference

This document describes the shell scripts available to the kwdb-intelligent-inspection skill for collecting metrics that cannot be obtained via the `/ts/query` API.

## Shell Scripts under `scripts/`

### check_kwdb_port_listener.sh

Check if KWDB common ports are actually listening at the OS level.

**Purpose**: Verify port binding status and confirm SQL/UI port availability.

**Usage**:
```bash
bash scripts/check_kwdb_port_listener.sh [PORTS]
```

**Parameters**:
- `PORTS`: Optional, comma-separated port list, defaults to `26257,8080`

**Returns**:
```json
[
  {
    "port": "number",
    "listening": "boolean",
    "process_hint": "string",
    "raw_line": "string"
  }
]
```
