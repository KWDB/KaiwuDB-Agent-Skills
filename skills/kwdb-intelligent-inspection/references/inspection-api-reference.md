## Time Series Query API

KaiwuDB provides a Time Series (TS) Query API for retrieving metrics data.

**Base URL:** `http://<host>:8080/ts/query`

**Method:** `POST`

**Content-Type:** `application/json`

---

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `start_nanos` | integer | Yes | Start timestamp in nanoseconds (Unix epoch). |
| `end_nanos` | integer | Yes | End timestamp in nanoseconds (Unix epoch). |
| `sample_nanos` | integer | Yes | Sampling interval in nanoseconds. |
| `queries` | array | Yes | Array of metric queries. |

#### Query Object

Each query object in the `queries` array supports the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | The metric name, constructed by prefixing `cr.node.` to the API Name listed in `references/report-template.md` (e.g., `sys.uptime` → `cr.node.sys.uptime`). |
| `downsampler` | integer | Yes | Downsampling method. |
| `source_aggregator` | integer | Yes | Aggregation method across sources. |
| `derivative` | integer | Yes | Derivative type. |

---

### Example

**Request:**

```bash
curl -X POST -H "Content-Type: application/json" -d '{
    "start_nanos": 1776729590000000000,
    "end_nanos": 1776733190000000000,
    "sample_nanos": 60000000000,
    "queries": [
      {
        "name": "cr.node.sys.cpu.user.ns",
        "downsampler": 1,
        "source_aggregator": 2,
        "derivative": 0
      }
    ]
  }' http://localhost:8080/ts/query
```

**Response:**

```json
{
  "results": [
    {
      "query": {
        "name": "cr.node.sys.cpu.user.ns",
        "downsampler": 1,
        "sourceAggregator": 2,
        "derivative": 0,
        "sources": ["1"]
      },
      "datapoints": [
        {
          "timestampNanos": "1776729540000000000",
          "value": 4052336666666.6665
        },
        {
          "timestampNanos": "1776729600000000000",
          "value": 4052820000000
        }
      ]
    }
  ]
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `results` | array | Array of query results. |
| `results[].query` | object | The original query with resolved sources. |
| `results[].query.sources` | array | List of source node IDs that returned data. |
| `results[].datapoints` | array | Array of timestamped data points. |
| `results[].datapoints[].timestampNanos` | string | Timestamp in nanoseconds (Unix epoch). |
| `results[].datapoints[].value` | number | Metric value at this timestamp. |

---

### Downsampler Values

| Value | Description |
|-------|-------------|
| 0 | LATEST |
| 1 | AVG |
| 2 | MIN |
| 3 | MAX |
| 4 | SUM |
| 5 | COUNT |

### Source Aggregator Values

| Value | Description |
|-------|-------------|
| 0 | NONE |
| 1 | AVG |
| 2 | SUM |
| 3 | MIN |
| 4 | MAX |
| 5 | COUNT |

### Derivative Values

| Value | Description |
|-------|-------------|
| 0 | NONE |
| 1 | DELTA |
| 2 | DERIVATIVE |

---

## Usage Guide

Query params (downsampler, source_aggregator, derivative) for each metric are listed in `references/metric-types.md`.
