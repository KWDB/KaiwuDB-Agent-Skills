# Partitioning Reference

Quick reference for KWDB partitioning. Read when designing partitions.

## Partition Types

| Type | Applies To | Use When |
|------|------------|----------|
| LIST | Relational | Categorical values (region, type) |
| RANGE | Relational | Time ranges, numeric ranges |
| HASH | Relational | Even distribution, no hotspots |
| HASHPOINT | Time-Series | Partition by tag values |

## Syntax Quick Reference

### LIST (Relational)

```sql
PARTITION BY LIST (column) (
  PARTITION name VALUES IN ('a', 'b'),
  PARTITION other VALUES IN (DEFAULT)
)
```

### RANGE (Relational)

```sql
PARTITION BY RANGE (column) (
  PARTITION q1 VALUES FROM ('2025-01-01') TO ('2025-04-01'),
  PARTITION future VALUES IN (MAXVALUE)
)
```

### HASH (Relational)

```sql
PARTITION BY HASH (column) (
  PARTITION p0 VALUES IN (0),
  PARTITION p1 VALUES IN (1)
)
```

### HASHPOINT (Time-Series)

```sql
ALTER TABLE t PARTITION BY HASHPOINT (
  PARTITION p1 VALUES IN (1, 3, 5),
  PARTITION p2 VALUES IN (2, 4, 6)
)
```

## When to Use

| Choose... | When... |
|-----------|---------|
| LIST | Data has known categories, queries filter by category |
| RANGE | Time-based data, need to drop old partitions easily |
| HASH | Hot spots on sequential IDs, need even distribution |
| HASHPOINT | TS table, want to group by device/sensor type |

## Key Rules

1. **Partition key must be first column(s) of primary key** (Relational)
2. **RANGE boundaries**: lower INCLUSIVE, upper EXCLUSIVE
3. **Use MAXVALUE** for catch-all partitions
4. **Number of partitions**: 4-16 typical (not too many)

## Common Mistakes

1. **HASH on timestamp** → Use RANGE for time data
2. **Too many partitions** → 100+ partitions is excessive
3. **Partition key not in PK** → Error or suboptimal
4. **Missing catch-all** → Out-of-range values fail

## TS vs Relational

| Aspect | HASHPOINT | HASH |
|--------|-----------|------|
| Partition Key | Tag values | Any column |
| Only TS tables? | Yes | No (Relational only) |
| Groups | Devices/sensors | N/A |

## Design Checklist

- [ ] Partition type matches access pattern
- [ ] Partition key is first in primary key
- [ ] Number of partitions is reasonable
- [ ] Catch-all partition exists (or explicit ranges cover all values)
