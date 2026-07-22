# kwdb-schema-design Design Spec

## Use Case

Help users design KWDB schemas and DDL for common relational, time-series, and mixed workloads.

### Primary Use Cases

1. **Relational Schema Design**
   - Design tables for business entities (users, orders, products, etc.)
   - Choose appropriate column types and sizes
   - Design primary keys (single column, composite, UUID, auto-generated)
   - Design indexes (single column, composite, covering, function-based, inverted)
   - Design constraints (CHECK, UNIQUE, FOREIGN KEY)
   - Design table partitioning strategy (LIST, RANGE, HASH)
   - Handle advanced types (JSONB, ARRAY, INET, UUID)

2. **Time-Series Schema Design**
   - Design tables for IoT/sensor/telemetry data
   - Choose timestamp column and precision
   - Design tag columns vs data columns
   - Choose primary tags (max 4)
   - Design retention policy
   - Design tag indexes for common query patterns
   - Choose HASHPOINT partitioning strategy
   - Enable DICT ENCODING for high-cardinality strings

3. **Mixed Workload Design**
   - Combine time-series measurements with business entity metadata
   - Decide which data goes to time-series table vs relational table
   - Design JOIN strategy between time-series and relational tables

4. **Schema Review and Critique**
   - Evaluate existing schema descriptions
   - Identify missing information
   - Propose improvements or corrections

### Secondary Use Cases

5. **Incremental Schema Extension (ALTER DDL)**
   - Add/drop/modify columns
   - Add/drop indexes
   - Add/modify constraints
   - Rename tables/columns
   - Set retention on time-series tables

6. **View and Materialized View Design**
   - Create views for simplifying complex queries
   - Create materialized views for pre-computed aggregations
   - Add indexes to materialized views

7. **Sequence and Auto-Increment Design**
   - Choose ID generation strategy (unique_rowid, UUID, sequences)
   - Design for distributed scenarios

8. **Schema Migration from Other Databases**
   - Translate MySQL/PostgreSQL schema concepts to KWDB equivalents
   - Identify KWDB-specific optimizations

## Success Criteria

### Mandatory (Skill is incomplete without these)

1. **Workload Classification**: Classify as relational, time-series, or mixed BEFORE outputting DDL
2. **Assumption Transparency**: State all assumptions when information is incomplete
3. **Minimal DDL**: Output only what's necessary for the use case
4. **Executable DDL**: DDL must be syntactically correct KWDB SQL
5. **Validation**: Include at least one validation step (EXPLAIN, SHOW CREATE, etc.)

### Quality Gates (Distinguish good from bad output)

6. **Type Appropriateness**: Column types match data semantics (INT for counts, DECIMAL for money, VARCHAR for names, etc.)
7. **Size Appropriateness**: String sizes are reasonable for the data (not VARCHAR(1000) for a boolean)
8. **Key Design**: Primary key strategy is appropriate for the access pattern
9. **Index Justification**: Every secondary index has a stated purpose
10. **Retention Justification**: Time-series retention settings are justified by business requirements

## Non-Goals

- DML operations (INSERT, UPDATE, DELETE, SELECT)
- Full migration planning (data movement, downtime, rollback)
- Deep performance tuning (specific query optimization, hints)
- Deployment guidance (installation, configuration, replication)
- Data modeling theory (ER diagrams, normalization theory)
- Trigger/procedure design (low-frequency, application-level preferred)
- User/permission management (unless explicitly requested)

## Dependencies

### Tiered Reference Architecture

**Tier 1 (Core - Always)**
- `references/key-rules.md` - Core decision tree and rules
- `references/disambiguation.md` - Clarifying questions

**Tier 2 (High-Frequency DDL)**
- `references/table-ddl-ref.md` - CREATE/ALTER/DROP TABLE
- `references/index-ddl-ref.md` - CREATE/DROP INDEX
- `references/constraint-ref.md` - CHECK, UNIQUE, FOREIGN KEY

**Tier 3 (Medium-Frequency DDL)**
- `references/view-ref.md` - Views and Materialized Views
- `references/sequence-ref.md` - Sequences and auto-increment
- `references/partitioning-ref.md` - LIST, RANGE, HASH partitioning
- `references/retention-ref.md` - Time-series retention policies

**Tier 4 (Low-Frequency - Only when asked)**
- `references/trigger-ref.md` - Triggers
- `references/procedure-ref.md` - Stored procedures and functions
- `references/database-ref.md` - Database and schema operations
- `references/privilege-ref.md` - User, role, and permission management

## Edge Cases

### Ambiguous Workload Type
- User describes "logs" or "events" → clarify if time-series or relational
- User describes "sensor data" without timestamp context → assume time-series with qualification
- User describes "user activity tracking" → mixed workload candidate, needs disambiguation

### Missing Information
- No timestamp mentioned for time-series → ask user or assume `k_timestamp TIMESTAMPTZ NOT NULL`
- No primary key specified → ask user or use auto-generated `INT8 DEFAULT unique_rowid()`
- No retention mentioned → state assumption (permanent or reasonable default like 30d)
- No index requirements → create only primary key, no secondary indexes

### Type Selection Uncertainty
- Variable-length strings → prefer VARCHAR over CHAR unless fixed-length is semantically required
- Numeric IDs vs UUIDs → ask user if not specified; UUID for distributed, INT for local
- Timestamp precision → default to millisecond (3) unless microsecond/nanosecond requested

### Boundary Conditions
- Very wide tables (>100 columns) → suggest splitting into related entities
- Very long string columns (>10000 bytes) → suggest BLOB/CLOB or compression
- Many-to-many relationships → use junction table
- Hierarchical data → use self-referential foreign key or ARRAY column

## Pattern Choice

Use a small domain workflow with explicit disambiguation before DDL output.

### Workflow Steps

1. **Trigger Detection**: Recognize schema design requests
2. **Workload Classification**: Relational vs Time-Series vs Mixed
3. **Information Gathering**: Ask clarifying questions (disambiguation)
4. **Schema Design**: Propose table structure with reasoning
5. **DDL Generation**: Output executable KWDB DDL
6. **Validation**: Provide validation query or explanation

### Guardrails

- Never output DDL without classifying the workload type first
- Never assume retention requirements without stating the assumption
- Never create speculative indexes without labeling them as optional
- Prefer minimal schema over comprehensive schema
