# Index DDL Reference

Quick reference for KWDB index operations. Read when adding or modifying indexes.

## CREATE INDEX

```sql
-- Single column
CREATE INDEX idx_name ON table_name (column);

-- Composite (multi-column)
CREATE INDEX idx_name ON table_name (col1, col2);

-- Unique
CREATE UNIQUE INDEX idx_name ON table_name (column);

-- Covering (with STORING columns)
CREATE INDEX idx_name ON table_name (col1) STORING (col2, col3);

-- Function-based
CREATE INDEX idx_name ON table_name (abs(column));

-- Inverted (JSONB)
CREATE INDEX idx_name ON table_name USING GIN (jsonb_column);
-- or
CREATE INVERTED INDEX idx_name ON table_name (jsonb_column);
```

## DROP INDEX

```sql
DROP INDEX table_name@index_name;           -- Error if not exists
DROP INDEX IF EXISTS table_name@index_name; -- Silent if not exists
DROP INDEX table_name@index_name CASCADE;   -- Drop dependent objects
```

## ALTER INDEX

```sql
-- Rename
ALTER INDEX table_name@old_idx RENAME TO new_idx;

-- Split at row (for performance)
ALTER INDEX table_name@idx_name SPLIT AT SELECT col FROM table_name;
```

## SHOW INDEX

```sql
SHOW INDEX FROM table_name;
```

Output columns: table_name, index_name, non_unique, seq_in_index, column_name, direction, storing, implicit

## When to Add Index

**Add index when column appears in**:
- WHERE clause
- JOIN condition
- ORDER BY
- GROUP BY

**Do NOT add index when**:
- Column has low selectivity (boolean, status codes with few values)
- Table is small (< 1000 rows)
- Query returns > 10% of table

## Index Types

| Type | Syntax | Use When |
|------|--------|----------|
| B-tree (default) | `USING BTREE` | Equality, range queries |
| Composite | `(col1, col2)` | Multi-column filters |
| Covering | `STORING (col)` | SELECT columns not in WHERE |
| Unique | `UNIQUE INDEX` | Enforce uniqueness |
| Function | `(abs(col))` | Computed column access |
| Inverted | `USING GIN` | JSONB full-text search |

## Time-Series Tag Index

```sql
-- Tag index for TS table queries filtering by tag
CREATE INDEX ON ts_table (tag_column);
```

**TS Tag Index Rules**:
- Only on tags (max 4 primary tags)
- Tag types: INT, FLOAT, CHAR, VARCHAR, NCHAR
- No index on: TIMESTAMP, GEOMETRY, FLOAT primary tags

## Composite Index Column Order

```
(col1, col2) -- Use when:
- Query filters by col1 AND col2
- Query filters by col1 only

(col2, col1) -- Wrong order for above queries
```

**Rule**: Put high-selectivity column first.

## Covering Index Example

```sql
-- Query: SELECT name, price FROM products WHERE category = 'electronics'
-- Instead of scanning table, index covers all columns:

CREATE INDEX idx_products_category ON products (category) STORING (name, price);
```

## Validation

```sql
-- Verify index exists
SHOW INDEX FROM table_name;

-- Verify index is used (check query plan)
EXPLAIN SELECT * FROM table_name WHERE col = 'value';
```

## Common Mistakes

| Wrong | Right |
|-------|-------|
| Index on low-cardinality column | Don't index boolean/status columns |
| Random index names | `idx_tablename_column` pattern |
| Index everything "for performance" | Index based on actual query patterns |
| Forgetting to index FK columns | FK columns MUST be indexed |

## Design Checklist

- [ ] Query patterns analyzed
- [ ] Index column selectivity evaluated
- [ ] Composite index column order correct
- [ ] Covering index for SELECT optimization
- [ ] FK columns indexed
- [ ] Index name follows convention
