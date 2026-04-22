# KWDB Functions Quick Reference

Function syntax reference. For query scenarios and routing, see `scenarios.md`.

## Time Functions

| Function | Syntax | Description |
|----------|--------|-------------|
| `time_bucket` | `time_bucket(ts, 'interval')` | Align timestamps to fixed intervals |
| `time_bucket_gapfill` | `time_bucket_gapfill(ts, 'interval')` | Align timestamps and fill gaps |
| `date_trunc` | `date_trunc('precision', ts)` | Truncate timestamp to precision |
| `now` | `now()` | Current timestamp (returns TIMESTAMPTZ) |

### date_trunc precision values
`millennium`, `century`, `decade`, `year`, `quarter`, `month`, `week`, `day`, `hour`, `minute`, `second`, `millisecond`, `microsecond`

## Time Intervals

Used with `time_bucket` and `time_bucket_gapfill`:

| Unit | Keyword | Example |
|------|---------|---------|
| Millisecond | `'ms'` | `'500ms'` |
| Second | `'s'` | `'30s'` |
| Minute | `'m'` | `'5m'` |
| Hour | `'h'` | `'1h'` |
| Day | `'d'` | `'7d'` |
| Week | `'w'` | `'2w'` |
| Month | `'mon'` | `'3mon'` |
| Year | `'y'` | `'1y'` |

## Aggregation Functions

| Function | Syntax | Description |
|----------|--------|-------------|
| `avg` | `avg(col)` | Average |
| `sum` | `sum(col)` | Sum |
| `count` | `count(*)` or `count(col)` | Count |
| `min` | `min(col)` | Minimum |
| `max` | `max(col)` | Maximum |
| `stddev` | `stddev(col)` | Standard deviation |

## First/Last Functions

| Function | Syntax | Description |
|----------|--------|-------------|
| `first` | `first(col)` | First non-null value by timestamp |
| `last` | `last(col)` | Last non-null value by timestamp |
| `first_row` | `first_row(col)` | First value including nulls |
| `last_row` | `last_row(col)` | Last value including nulls |

## Interpolation

| Function | Syntax | Description |
|----------|--------|-------------|
| `interpolate` | `interpolate(agg_func, mode)` | Fill missing values. Modes: `PREV`, `NEXT`, `'linear'`, `'constant'`, `NULL` |

Must be used with `time_bucket_gapfill()`. The `method` parameter must be an aggregate function with numeric data type.

## Time-Series Analysis

| Function | Syntax | Description |
|----------|--------|-------------|
| `TWA` | `TWA(ts, expr)` | Time-weighted average |
| `diff` | `diff(col) OVER (...)` | Difference from previous row |
| `ELAPSED` | `ELAPSED(ts [, unit])` | Time coverage in units |

## Window Functions

| Function | Syntax | Description |
|----------|--------|-------------|
| `TIME_WINDOW` | `TIME_WINDOW(ts, 'interval' [, 'slide'])` | Sliding time windows |
| `COUNT_WINDOW` | `COUNT_WINDOW(n [, slide])` | Fixed row count windows |
| `SESSION_WINDOW` | `SESSION_WINDOW(ts, 'interval')` | Session-based windows (time gaps) |
| `EVENT_WINDOW` | `EVENT_WINDOW(start_cond, end_cond)` | Event-based windows |
| `STATE_WINDOW` | `STATE_WINDOW(col)` | State-change windows |

## Date/Time Extraction

| Function | Syntax | Description |
|----------|--------|-------------|
| `extract` | `EXTRACT(field FROM ts)` | Extract timestamp part |
| `date_part` | `date_part('field', ts)` | Alternative extraction |

### extract/date_part fields
`year`, `month`, `day`, `hour`, `minute`, `second`, `epoch`, `millennium`, `century`, `decade`, `quarter`, `week`, `isoyear`, `dayofweek`, `isodow`, `dayofyear`, `julian`, `millisecond`, `microsecond`, `timezone`, `timezone_hour`, `timezone_minute`

## Math Functions

| Function | Description |
|----------|-------------|
| `abs(x)` | Absolute value |
| `round(x)` | Round to nearest |
| `floor(x)` | Round down |
| `ceil(x)` | Round up |
| `sqrt(x)` | Square root |
| `power(x, y)` | x to the power of y |
| `log(x)` | Base-10 logarithm |
| `ln(x)` | Natural logarithm |

## String Functions


| Function | Description |
|----------|-------------|
| `lower(x)` | Convert to lowercase |
| `upper(x)` | Convert to uppercase |
| `substring(x, start, len)` | Extract substring |
| `length(x)` | String length |
| `trim(x)` | Remove whitespace |
| `concat(x, y, ...)` | Concatenate strings (variadic — takes 2+ args) |

## Conditional Functions

| Function | Description |
|----------|-------------|
| `COALESCE(x, ...)` | First non-null value |
| `NULLIF(x, y)` | NULL if x equals y |
| `IFNULL(x, y)` | x if not null, else y |
| `CASE WHEN ... END` | Conditional expression |

## Type Casting

Use `::type` for casting:

```sql
-- Cast to integer
value::INT
value::INT4
value::INT8

-- Cast to float
value::FLOAT4
value::FLOAT8
value::DOUBLE

-- Cast to string
value::VARCHAR
value::STRING
value::CHAR

-- Cast to timestamp
value::TIMESTAMP
value::TIMESTAMPTZ

-- Cast to boolean
value::BOOL
```

**Note on timestamp casting**: When the timestamp column in a time-series table is set to TIMESTAMP type, the system automatically converts it to TIMESTAMPTZ. Casting operations on this column will be processed according to the database timezone setting.

**Common patterns:**
```sql
-- String to timestamp
'2024-01-15'::TIMESTAMP

-- Integer to timestamp (Unix epoch)
1705315200::TIMESTAMP

-- Timestamp to date
ts::DATE

-- Keep only date part
date_trunc('day', ts)
```

## Common Pitfalls

1. **SUM overflow**: Avoid letting SUM results exceed the maximum supported range
2. **Avoid escape character `+` in SUBSTRING regex**: Use `substr()` or `substring()` without regex patterns containing `+`
3. **time_bucket interval format**: Do NOT use 复合 interval format like `'1d1h'` 
4. **NULL handling**: `last()` ignores NULLs, `last_row()` includes NULLs — choose based on data characteristics
