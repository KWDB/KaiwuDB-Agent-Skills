# Key Rules

KWDB schema design core rules. **ALWAYS READ THIS FIRST.**

## Decision Tree

```
User request → Classify workload type:
├── 实体数据 + 需要JOIN/UPDATE → RELATIONAL
├── 时间戳为主 + 传感器/监控 + INSERT为主 → TIME-SERIES
└── 两者都有 → MIXED
```

## Rule 0: Classify BEFORE DDL

Always classify as relational / time-series / mixed BEFORE outputting DDL.

## Rule 1: Type Selection

| Choose... | When... |
|-----------|---------|
| RELATIONAL | Business entities, CRUD, JOINs, UPDATE/DELETE common |
| TIME-SERIES | Timestamp primary, sensors/metrics, INSERT-heavy, retention needed |
| MIXED | Both entity + measurement data |

## Rule 2: Column Types (Quick)

| Data | Type |
|------|------|
| IDs ≤2B | INT4 |
| IDs >2B / distributed | INT8 or UUID |
| Money/exact decimals | DECIMAL(p,s) |
| Measurements (approx) | FLOAT8 |
| Low-precision (temp, humidity) | FLOAT4 |
| Short text | VARCHAR(n) |
| JSON data | JSONB |
| Timestamps | TIMESTAMPTZ (TS tables) |
| Boolean | BOOL |

**Avoid**: FLOAT for money, VARCHAR without length for structured data

## Rule 3: Primary Keys

| Scenario | Recommendation |
|----------|---------------|
| Single table, no FK | INT8 DEFAULT unique_rowid() |
| Multi-table with FK | Explicit UUID or INT |
| Distributed | UUID DEFAULT gen_random_uuid() |
| Natural key stable | Use natural key |

**TS tables**: First column = TIMESTAMPTZ, device ID as primary tag

## Rule 4: When to Add Index

Add index when column appears in: WHERE, JOIN, ORDER BY, GROUP BY

**TS tag index**: Only on tags (max 4), types: INT/FLOAT/CHAR/NCHAR
**No index**: TIMESTAMP, GEOMETRY, primary tags

## Rule 5: Constraints

| Type | Use When |
|------|----------|
| CHECK | Value validation |
| UNIQUE | No duplicates |
| FOREIGN KEY | Refer integrity (column MUST be indexed) |

## Rule 6: Time-Series Specific

- **Tags**: Filter/GROUP BY, low cardinality preferred
- **Data columns**: Actual measurements
- **Primary tags**: Max 4, NOT NULL, no TIMESTAMP/GEOMETRY/FLOAT
- **Retention**: State assumption if not specified (default: 180d)

## Rule 7: Partitioning

| Type | Use When |
|------|----------|
| LIST | Categorical values (region, type) |
| RANGE | Time/data ranges |
| HASH | Even distribution |
| HASHPOINT (TS) | Partition by tag values |

## Rule 8: DDL Scope

This skill handles **schema DDL**, not:
- DML (INSERT, UPDATE, DELETE, SELECT)
- Database administration (backup, restore)
- User/permission management (unless explicitly requested)

## Rule 9: Design Principles

1. Start minimal
2. State assumptions
3. Validate DDL
4. Prefer NOT NULL for required fields

## Tiered References

| Tier | Files | When to Read |
|------|-------|--------------|
| Core | key-rules.md, disambiguation.md | Always |
| High-Freq | table-ddl-ref.md, index-ddl-ref.md, constraint-ref.md | Designing tables/indexes/constraints |
| Medium | view-ref.md, sequence-ref.md, partitioning-ref.md, retention-ref.md | When needed |
| Low | trigger-ref.md, procedure-ref.md, database-ref.md, privilege-ref.md | Only when asked |

---
**For detailed reference**, see the tiered reference files above.
