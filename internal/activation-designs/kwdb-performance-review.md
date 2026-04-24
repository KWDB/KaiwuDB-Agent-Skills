# kwdb-performance-review Activation Design

## Should Trigger

- slow time-series queries or time-series aggregation performance
- ts.* cluster parameter tuning questions
- time-series table performance diagnostics
- time-series compression strategy review
- time-series table memory or cache sizing questions
- queries using TIME_BUCKET, TIME_WINDOW, or time-series window functions
- time-series pagination performance (deep OFFSET issues)
- cross-model queries where time-series table join is slow

## Should Not Trigger

- relational table performance issues (index tuning, B-tree optimization, join order for relational-only queries)
- schema design requests (CREATE TABLE, ALTER TABLE, CREATE INDEX)
- deployment or cluster setup questions
- data migration questions
- DML write optimization (bulk INSERT, import performance)
- requests to add indexes on time-series tables (time-series tables do not support secondary indexes)

## False Positive Risks

- Risk: "KWDB query is slow" but the query targets a relational table only
  - Mitigation: engine detection step checks table type via `SHOW TABLES` or `DESCRIBE`; if all tables are relational, stop and state scope boundary
- Risk: "optimize this query" with no KWDB context and no time-series indicators
  - Mitigation: check for time-series keywords (ts_column, PRIMARY TAGS, TIME_BUCKET); if absent, ask user to clarify
- Risk: "add an index to speed up my query" on a time-series table
  - Mitigation: if target is time-series, explain that secondary indexes are not supported and redirect to tag filter / partition pruning optimization

## False Negative Risks

- Risk: "data write latency is high" sounds like a write-path issue but may be caused by compression or memory pressure
  - Mitigation: include latency-related symptoms in trigger scope even if the user does not mention ts.* explicitly
- Risk: "my pagination API is slow" does not mention time-series
  - Mitigation: pagination slowness on time-series tables is a common anti-pattern; include in trigger scope

## First Decision After Activation

Determine the target table type. Run engine detection:
1. If the user names a table, check `SHOW TABLES FROM <db>` or `DESCRIBE <table>` via MCP
2. If the table is a TIME SERIES TABLE, proceed with the review workflow
3. If the table is a RELATIONAL TABLE only, stop and state that this skill covers time-series tables only
4. If both table types are involved, review only the time-series portion
