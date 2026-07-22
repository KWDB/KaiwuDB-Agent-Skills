# kwdb-schema-design Activation Design

## Should Trigger

### Explicit Triggers

#### Table Operations
- "design a KWDB schema"
- "write KWDB DDL"
- "create a table in KWDB"
- "KWDB schema for ..."
- "KWDB DDL for ..."
- "how to model ... in KWDB"
- "should I use relational or time-series in KWDB"
- "KWDB table design for ..."

#### ALTER TABLE Operations
- "alter table ... add column"
- "modify column in KWDB"
- "change column type in KWDB"
- "add constraint to table"
- "set retention on time-series table"
- "rename column in KWDB"

#### Index Operations
- "create index in KWDB"
- "add index to table"
- "create composite index"
- "add covering index"
- "create tag index on time-series"

#### View Operations
- "create view in KWDB"
- "create materialized view"
- "add index to materialized view"

#### DROP Operations
- "drop table in KWDB"
- "drop index in KWDB"
- "delete table from KWDB"

### Implicit Triggers

#### Time-Series
- "I have sensors that report data every minute"
- "I need to store device telemetry"
- "I want to track user behavior over time"
- "I have time-series data from IoT devices"

#### Relational
- "design database for inventory/orders/customers/products"
- "create schema for a blog/e-commerce/user management system"

### Mixed/Partial Triggers

- "help me optimize this schema" (check if KWDB context exists)
- "what's wrong with my table design" (check if KWDB-related)
- "extend the existing schema"
- "add indexes to improve performance"

## Should NOT Trigger

### Non-Schema Questions

- deployment questions ("how to install KWDB", "how to configure replication")
- troubleshooting questions ("my query is slow", "connection failed")
- migration questions ("how to migrate data from MySQL to KWDB")
- performance review questions ("analyze this query execution plan")
- backup/restore questions ("how to backup my KWDB database")
- user management questions ("how to create a user in KWDB") - unless explicitly asked

### Out of Scope

- pure SQL questions without KWDB context
- "write a SQL query" (not schema design)
- "how does SQL work in general"
- DML operations ("insert data", "update rows", "delete records")

## False Positive Risks

### High Risk

- Generic SQL schema design requests without KWDB context
  - Example: "design a schema for a blog"
  - Mitigation: Check if user explicitly mentions KWDB or asks for KWDB-specific features

- Requests that mention "schema" but mean "query schema" (JSON structure)
  - Example: "what's the JSON schema for the API response"
  - Mitigation: Look for DDL keywords like CREATE TABLE, column, index

### Medium Risk

- "how should I model this data" without explicit storage context
  - Mitigation: Ask clarifying question about KWDB usage

- "convert this MySQL schema to KWDB" without additional context
  - This IS a valid trigger, but may need disambiguation about KWDB-specific features

## False Negative Risks

### Prompt Variations to Watch

- "how should I store this in KWDB" → SHOULD trigger
- "I need to track sensor readings" (without saying KWDB) → ambiguous, lean toward asking
- "what's the best table structure for" → ambiguous, check context
- "can KWDB handle time-series data" → this is a question, not a design request, but could lead to design
- "add a column" without mentioning KWDB → ask for context

## First Decision After Activation

### Step 1: Classify Workload Type

Ask or determine:
- **Relational**: Business entities, transactional data, needs JOINs, UPDATE/DELETE
- **Time-Series**: Sensor/telemetry data, timestamp as primary access pattern, retention needs
- **Mixed**: Both entity data and time-series measurements

### Step 2: Select Relevant References

| Operation | References to Read |
|-----------|-------------------|
| CREATE TABLE (TS) | key-rules, table-ddl-ref, retention-ref, partitioning-ref |
| CREATE TABLE (Relational) | key-rules, table-ddl-ref, constraint-ref, partitioning-ref |
| ALTER TABLE | key-rules, table-ddl-ref |
| CREATE INDEX | key-rules, index-ddl-ref |
| CREATE VIEW | key-rules, view-ref |
| DROP TABLE/INDEX | key-rules, table-ddl-ref / index-ddl-ref |
| SET RETENTION | key-rules, retention-ref |

### Step 3: Check Information Completeness

If incomplete, follow disambiguation workflow before producing DDL.

### Step 4: Select Design Pattern

Based on workload type and available information:
- Relational: Standard entity modeling
- Time-Series: Tag-based modeling with optional retention
- Mixed: Separate tables with JOIN strategy

## Activation Examples

### Example 1: Clear Time-Series Trigger

**User**: "Design a KWDB schema for temperature sensors that report every minute"
**Activation**: YES
**Next Action**: Proceed with time-series schema design
**Workload Type**: Time-Series
**Assumptions**: `k_timestamp` column, sensor_id as primary tag, numeric measurements

### Example 2: Clear Relational Trigger

**User**: "Write DDL for a users and orders schema in KWDB"
**Activation**: YES
**Next Action**: Proceed with relational schema design
**Workload Type**: Relational
**Assumptions**: Standard foreign key relationships

### Example 3: ALTER TABLE Trigger

**User**: "Add a phone column to the customers table in KWDB"
**Activation**: YES
**Next Action**: Proceed with ALTER TABLE ADD COLUMN
**References**: table-ddl-ref
**Assumptions**: VARCHAR(20) for phone number

### Example 4: INDEX Trigger

**User**: "Create an index on the orders table for customer_id"
**Activation**: YES
**Next Action**: Proceed with CREATE INDEX
**References**: index-ddl-ref
**Assumptions**: Single column btree index

### Example 5: VIEW Trigger

**User**: "Create a view for active orders in KWDB"
**Activation**: YES
**Next Action**: Proceed with CREATE VIEW
**References**: view-ref
**Assumptions**: None (need WHERE condition)

### Example 6: MATERIALIZED VIEW Trigger

**User**: "Create a materialized view for monthly sales summary"
**Activation**: YES
**Next Action**: Proceed with CREATE MATERIALIZED VIEW
**References**: view-ref
**Assumptions**: GROUP BY aggregation

### Example 7: Ambiguous Trigger

**User**: "I want to track my products and their price changes over time"
**Activation**: YES
**Next Action**: Disambiguate - is price history time-series or a separate relational table?
**Workload Type**: Mixed (likely)
**Assumptions**: None until clarified

### Example 8: False Positive

**User**: "How do I write a SELECT query in KWDB"
**Activation**: NO (not schema design)
**Next Action**: Do not activate, this is a query question

### Example 9: False Negative

**User**: "should I use a time-series table or regular table for my sensor data"
**Activation**: YES
**Next Action**: This IS a schema design decision question, proceed with disambiguation
**Workload Type**: Time-Series (but needs clarification)

### Example 10: DROP TABLE Trigger

**User**: "Drop the old_logs table from KWDB"
**Activation**: YES
**Next Action**: Proceed with DROP TABLE
**References**: table-ddl-ref
**Assumptions**: IF EXISTS recommended

### Example 11: SET RETENTION Trigger

**User**: "Alter the sensor_data table to set retention to 30 days"
**Activation**: YES
**Next Action**: Proceed with ALTER TABLE SET RETENTIONS
**References**: retention-ref
**Assumptions**: Time-series table confirmed
