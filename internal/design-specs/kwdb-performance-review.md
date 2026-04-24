# kwdb-performance-review Design Spec

## Use Case

Review KWDB time-series performance issues. Diagnose slow time-series queries, ts.* parameter misconfiguration, compression strategy problems, and memory or storage tuning gaps. Output a severity-ranked issue list with root cause analysis and executable tuning SQL.

## Success Criteria

- fetch real cluster settings and execution plans via MCP
- classify issues by severity: Critical / Warning / Info
- provide root cause and executable tuning SQL for each issue
- cover four dimensions: query optimization, compression, memory and cache, storage and background tasks

## Non-Goals

- relational table tuning
- deployment and cluster setup
- data migration
- schema design
- write-path tuning (WAL, raft log, ack-before-application)

## Dependencies

- kwdb MCP server: read-query for SHOW CLUSTER SETTINGS, EXPLAIN, and system views
- kwdb MCP server: write-query for SET CLUSTER SETTING recommendations

## Pattern Choice

Reviewer (primary) + Tool Wrapper (supporting). Review against a domain-specific checklist; use MCP tools to fetch real state.
