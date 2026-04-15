# Database Reference

Quick reference for KWDB database and schema operations. **Low-frequency DDL** - only read when user explicitly asks about database-level operations.

## DATABASE Operations

### CREATE DATABASE

```sql
CREATE DATABASE db_name;
CREATE DATABASE IF NOT EXISTS db_name;
```

### DROP DATABASE

```sql
DROP DATABASE db_name;
DROP DATABASE IF EXISTS db_name;
```

### USE/SET DATABASE

```sql
SET database = db_name;  -- or
USE db_name;
```

## SCHEMA Operations

### CREATE SCHEMA

```sql
CREATE SCHEMA schema_name;
```

### DROP SCHEMA

```sql
DROP SCHEMA schema_name;
DROP SCHEMA schema_name CASCADE;  -- Drop all objects
```

## SHOW Commands

```sql
SHOW DATABASES;
SHOW SCHEMAS FROM database_name;
SHOW TABLES FROM database_name.schema_name;
```

## When to Use

| Task | Approach |
|------|----------|
| Multi-tenant data isolation | Separate databases or schemas |
| Development/Testing | Separate schemas in same DB |
| Production deployment | Separate databases |

## Note

- Relational tables support schema prefix: `database.schema.table`
- Time-series tables only support `database.table` (always use public schema)

## Validation

```sql
SHOW CREATE DATABASE db_name;
SELECT * FROM information_schema.schemata;
```
