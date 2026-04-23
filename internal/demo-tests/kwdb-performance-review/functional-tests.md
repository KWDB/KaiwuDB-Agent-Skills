# Functional Tests

## Test 1: Missing Time Filter on Time-Series

**Input Query:**
```sql
SELECT * FROM device_sensor WHERE device_id = 'D001';
```

**Expected Output:**
- Engine Type: time-series
- Anti-Pattern: Missing time range filter
- Must add: `AND ts >= '...' AND ts < '...'`
- Guardrail: Warn about full partition scan

## Test 2: Fuzzy Tag Match

**Input Query:**
```sql
SELECT * FROM device_sensor
WHERE device_id LIKE 'D00%'
  AND ts >= '2026-04-01';
```

**Expected Output:**
- Anti-Pattern: LIKE prevents hash index usage
- Suggest: Exact equality or IN list
- Must NOT suggest: CREATE INDEX

## Test 3: SELECT * on Time-Series

**Input Query:**
```sql
SELECT * FROM sensor_data WHERE ts >= '2026-04-01';
```

**Expected Output:**
- Anti-Pattern: SELECT * wastes columnar IO
- Suggest: Explicit column list

## Test 4: OFFSET Pagination

**Input Query:**
```sql
SELECT ts, temperature FROM sensor_data
WHERE device_id = 'D001'
ORDER BY ts LIMIT 20 OFFSET 10000;
```

**Expected Output:**
- Anti-Pattern: OFFSET scans 10020 rows
- Suggest: Time-based cursor pagination

## Test 5: Manual Date Truncation

**Input Query:**
```sql
SELECT DATE_TRUNC('hour', ts), AVG(temp)
FROM sensor_data WHERE ts >= NOW() - INTERVAL '7 days'
GROUP BY DATE_TRUNC('hour', ts);
```

**Expected Output:**
- Anti-Pattern: Manual truncation bypasses optimization
- Suggest: TIME_BUCKET function

## Test 6: Cross-Model Join Order

**Input Query:**
```sql
SELECT s.ts, s.temp, d.name
FROM sensor_data s
JOIN devices d ON s.device_id = d.id
WHERE d.group_id = 'G001';
```

**Expected Output:**
- Anti-Pattern: Time-series as driver
- Suggest: devices as driver table with time filter

## Test 7: Relational Missing Index

**Input Query:**
```sql
SELECT * FROM orders WHERE customer_email = 'test@example.com';
```

**Expected Output:**
- Engine Type: relational
- Suggest: CREATE INDEX on customer_email
- Note: This is a relational table (verify first!)

## Test 8: Function on Time Column

**Input Query:**
```sql
SELECT * FROM sensor_data
WHERE DATE_TRUNC('day', ts) = '2026-04-01';
```

**Expected Output:**
- Anti-Pattern: Function prevents partition pruning
- Suggest: Direct time range comparison
