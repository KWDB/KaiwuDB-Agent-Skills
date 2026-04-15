---
name: kwdb-schema-design
description: Design KWDB schemas and DDL for relational, time-series, and mixed workloads.
version: 0.3.0
---

## Tiered Reference Architecture

**Tier 1 (Always Read)** - Core rules and disambiguation:
- `references/key-rules.md` - Decision tree and core rules
- `references/disambiguation.md` - Clarifying questions

**Tier 2 (High-Frequency DDL)** - Read when designing tables/indexes/constraints:
- `references/table-ddl-ref.md` - CREATE/ALTER/DROP TABLE
- `references/index-ddl-ref.md` - CREATE/DROP INDEX
- `references/constraint-ref.md` - CHECK, UNIQUE, FOREIGN KEY

**Tier 3 (Medium-Frequency DDL)** - Read when needed:
- `references/view-ref.md` - Views and Materialized Views
- `references/sequence-ref.md` - Sequences and auto-increment
- `references/partitioning-ref.md` - LIST, RANGE, HASH partitioning
- `references/retention-ref.md` - Time-series retention policies

**Tier 4 (Low-Frequency DDL)** - Only when explicitly requested:
- `references/trigger-ref.md` - Triggers
- `references/procedure-ref.md` - Stored procedures and functions
- `references/database-ref.md` - Database and schema operations
- `references/privilege-ref.md` - User, role, and permission management

## When to Activate

**Should trigger:**
- "design a KWDB schema"
- "write KWDB DDL"
- "create a table/index/view in KWDB"
- "KWDB schema for ..."
- "add column to existing table"
- "create index on ..."
- "should I use relational or time-series in KWDB"

**Should NOT trigger:**
- Deployment, troubleshooting, migration questions
- Pure query questions (not schema design)
- Backup/restore operations
- User/permission management (unless explicitly requested)

## Supported DDL Operations

| Category | Operations |
|----------|------------|
| Tables | CREATE TABLE, ALTER TABLE, DROP TABLE |
| Indexes | CREATE INDEX, ALTER INDEX, DROP INDEX |
| Constraints | PRIMARY KEY, UNIQUE, CHECK, FOREIGN KEY |
| Views | CREATE VIEW, DROP VIEW |
| Materialized Views | CREATE MATERIALIZED VIEW, REFRESH, DROP |
| Sequences | CREATE SEQUENCE, nextval(), setval() |
| Time-Series | Tags, Primary Tags, Retention, DICT ENCODING |
| Partitioning | LIST, RANGE, HASH (relational), HASHPOINT (time-series) |

## Workflow

### Step 1: Classify Workload Type

```
Request → RELATIONAL / TIME-SERIES / MIXED
```

Ask if unclear. **Never skip this step.**

### Step 2: Gather Requirements

Use `disambiguation.md` to ask:
- What data fields are needed
- Primary key strategy
- Query patterns (filter, group, join)
- For time-series: retention needs

### Step 3: Design Schema

Apply rules from `key-rules.md` and relevant tier-2/3 references:
- Choose correct column types
- Design primary keys
- Add indexes only when needed
- For time-series: design tags and retention

### Step 4: Generate DDL

Output minimal, executable DDL:
- Use correct KWDB syntax
- Include NOT NULL where appropriate
- Add comments for clarity

### Step 5: Validate

Include validation step:
- `SHOW CREATE TABLE` to verify syntax
- `SHOW COLUMNS` to verify structure
- `SHOW INDEX` to verify indexes

## Output Format

```markdown
## Intent
[Brief description of what the schema does]

## Workload Type
[relational / time-series / mixed]

## Assumptions
[Any assumptions made - retention, primary key strategy, etc.]

## Design
[Table structure with column types and rationale]

## DDL
```sql
-- minimal executable DDL
```

## Validation
[How to verify the DDL works]
```

## Guardrails

1. **Never output DDL before classifying workload type**
2. **Never assume retention without stating it** (time-series)
3. **Never create speculative indexes** (label as optional)
4. **Prefer minimal schema** over comprehensive
5. **State all assumptions** when information is incomplete
6. **Validate DDL** before finishing
7. **FK columns must be indexed**
8. **Use appropriate types** (DECIMAL for money, not FLOAT)

## Error Handling

- If requirements unclear: ask clarifying questions first
- If DDL might be wrong: suggest validation steps
- If feature not supported: explain KWDB limitation
- If ambiguous request: classify workload type first
