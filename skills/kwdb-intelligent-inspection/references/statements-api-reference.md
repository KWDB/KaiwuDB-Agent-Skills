## Statements API

KaiwuDB provides a Statements API for retrieving SQL statement execution statistics.

**Base URL:** `http://<host>:8080/_status/statements`

**Method:** `GET`

**⚠️ Mandatory curl Parameter:** All API calls MUST use `--insecure` flag (or `-k`).

---

### Important Notes

- **Time Window**: The API returns aggregated statement statistics collected over a time window controlled by the cluster setting `sql.stats.aggregation.interval`. **Default: 1 hour**.
- **Limitation**: This API is **not supported in TLS mode** because authentication requires the AdminUI login endpoint which needs captcha verification that cannot be solved in non-interactive script mode.

---

### Example

**Request:**

```bash
curl --insecure http://localhost:8080/_status/statements
```

**Response:**

```json
{
  "statements": [
    {
      "key": {
        "keyData": {
          "query": "SELECT * FROM table_name",
          "app": "$ cmdlineflags",
          "distSQL": false,
          "failed": false,
          "opt": true,
          "implicitTxn": false,
          "user": "root",
          "database": "defaultdb"
        },
        "nodeId": 1
      },
      "stats": {
        "count": "42",
        "firstAttemptCount": "42",
        "maxRetries": "0",
        "legacyLastErr": "",
        "numRows": { "mean": 10.5, "squaredDiffs": 0 },
        "parseLat": { "mean": 0.000123, "squaredDiffs": 0 },
        "planLat": { "mean": 0.000456, "squaredDiffs": 0 },
        "runLat": { "mean": 0.001234, "squaredDiffs": 0 },
        "serviceLat": { "mean": 0.002000, "squaredDiffs": 0 },
        "overheadLat": { "mean": 0.000187, "squaredDiffs": 0 },
        "sensitiveInfo": {
          "lastErr": "",
          "mostRecentPlanDescription": { "name": "scan", "attrs": [], "children": [] },
          "mostRecentPlanTimestamp": "2026-04-22T10:00:00Z"
        },
        "bytesRead": "1024",
        "rowsRead": "42",
        "failedCount": "0"
      }
    }
  ],
  "lastReset": "2026-04-22T09:00:00Z",
  "internalAppNamePrefix": "$"
}
```

---

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `statements` | array | Array of statement statistics. |
| `statements[].key.keyData.query` | string | The SQL query string (may be truncated/redacted). |
| `statements[].key.keyData.app` | string | Application name that executed the statement. |
| `statements[].key.keyData.distSQL` | boolean | Whether the statement used distributed SQL. |
| `statements[].key.keyData.failed` | boolean | Whether the statement failed. |
| `statements[].key.keyData.implicitTxn` | boolean | Whether the statement ran in implicit transaction. |
| `statements[].key.keyData.user` | string | User who executed the statement. |
| `statements[].key.keyData.database` | string | Database context for the statement. |
| `statements[].key.nodeId` | integer | Node ID where the statement was executed. |
| `statements[].stats.count` | string | Total number of executions. |
| `statements[].stats.firstAttemptCount` | string | Executions on first attempt (no retries). |
| `statements[].stats.maxRetries` | string | Maximum retry count across all executions. |
| `statements[].stats.numRows.mean` | number | Average number of rows processed. |
| `statements[].stats.parseLat.mean` | number | Average parse latency in seconds. |
| `statements[].stats.planLat.mean` | number | Average planning latency in seconds. |
| `statements[].stats.runLat.mean` | number | Average run latency in seconds. |
| `statements[].stats.serviceLat.mean` | number | Average total service latency in seconds (parse + plan + run + overhead). |
| `statements[].stats.overheadLat.mean` | number | Average overhead latency in seconds. |
| `statements[].stats.bytesRead` | string | Total bytes read. |
| `statements[].stats.rowsRead` | string | Total rows read. |
| `statements[].stats.failedCount` | string | Number of failed executions. |
| `statements[].stats.sensitiveInfo.lastErr` | string | Last error message (if any). |
| `statements[].stats.sensitiveInfo.mostRecentPlanDescription` | object | Most recent execution plan (name + attributes + children). |
| `statements[].stats.sensitiveInfo.mostRecentPlanTimestamp` | string | Timestamp of most recent plan. |
| `lastReset` | string | Timestamp when statement statistics were last reset. |
| `internalAppNamePrefix` | string | Prefix for internal application names. |

---

### Latency Fields (in seconds)

| Field | Description |
|-------|-------------|
| `parseLat.mean` | Time to parse the SQL statement. |
| `planLat.mean` | Time to generate the execution plan. |
| `runLat.mean` | Time to execute the statement. |
| `serviceLat.mean` | Total time (parse + plan + run + overhead). |
| `overheadLat.mean` | Internal overhead (contention, etc.). |

**Note**: `serviceLat = parseLat + planLat + runLat + overheadLat`

---

### Helper Script

A Python script is provided for easier access to slow statement analysis:

```bash
python3 scripts/get_kwdb_statements.py --help
```

**Usage Examples:**

```bash
# Get top 10 slowest statements (by service latency)
python3 scripts/get_kwdb_statements.py --host localhost --port 8080

# Filter statements with latency > 100ms
python3 scripts/get_kwdb_statements.py --min-latency-ms 100

# Sort by run latency instead of service latency
python3 scripts/get_kwdb_statements.py --sort-by run_lat

# Output raw JSON
python3 scripts/get_kwdb_statements.py --json
```

---

### Slow Query Identification

To identify slow queries, look for statements where:

1. **`serviceLat.mean`** is high (total time per execution)
2. **`runLat.mean`** is high relative to other phases (execution is the bottleneck)
3. **`planLat.mean`** is high (planning is slow, may indicate complex queries)
4. **`count`** is high with moderate latency (frequently executed slow queries)