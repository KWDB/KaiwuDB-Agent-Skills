# Time Series Downsampling

Downsampling time-series data by fixed time intervals using `time_bucket()`.

## When to Use

Use for: "每小时的平均值", "每天的统计", "降采样到1分钟"

**Do NOT use `TIME_WINDOW()` here** — use `time_bucket()` for fixed-interval downsampling (performance optimized).

## time_bucket Function

```sql
time_bucket(timestamp_column, 'interval')
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| timestamp_column | The timestamp column (e.g., `ts`) |
| interval | `10ms`, `1s`, `1m`, `1h`, `1d`, `1w`, `1mon`, `1y` |

## Examples

**Hourly Average:**
```sql
SELECT time_bucket(ts, '1h') AS hour, avg(temperature) AS avg_temp
FROM sensor_data
WHERE ts >= NOW() - INTERVAL '1 day'
GROUP BY hour
ORDER BY hour;
```

**Daily Max/Min:**
```sql
SELECT time_bucket(ts, '1d') AS day,
       max(temperature) AS max_temp,
       min(temperature) AS min_temp
FROM sensor_data
WHERE ts >= NOW() - INTERVAL '7 days'
GROUP BY day
ORDER BY day;
```

**15-Minute Intervals:**
```sql
SELECT time_bucket(ts, '15m') AS bucket,
       device_id,
       avg(humidity) AS avg_humidity
FROM sensor_data
WHERE ts >= NOW() - INTERVAL '24 hours'
GROUP BY bucket, device_id
ORDER BY bucket, device_id;
```

## Template

```sql
SELECT
    time_bucket(ts, '<interval>') AS period,
    <group_column>,
    <aggregation>(<metric>) AS <alias>
FROM <table_name>
WHERE ts >= NOW() - INTERVAL '<duration>'
GROUP BY period, <group_column>
ORDER BY period, <group_column>;
```

## Time Intervals

| Interval | Keyword | Use Case |
|----------|---------|----------|
| 1 second | `'1s'` | High-frequency data |
| 1 minute | `'1m'` | Real-time monitoring |
| 5 minutes | `'5m'` | Standard monitoring |
| 1 hour | `'1h'` | Hourly reports |
| 1 day | `'1d'` | Daily aggregation |
| 1 week | `'1w'` | Weekly reports |
| 1 month | `'1mon'` | Monthly analysis |

## Notes

1. Use `time_bucket()` for fixed-interval downsampling (not `TIME_WINDOW`)
2. Always include `GROUP BY time_bucket(...)`
3. Use `ORDER BY` for predictable output ordering
4. Combine with aggregate functions: `avg`, `sum`, `count`, `min`, `max`, `stddev`
