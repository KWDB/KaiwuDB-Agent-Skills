# kwdb-troubleshooting Design Spec

## Use Case

Help users diagnose KWDB faults that require logs, metrics, and source-code correlation.
The primary cases are functional failures, crash or restart analysis, glog-style severity log analysis, performance bottlenecks, and slow SQL.

## Success Criteria

- classify the issue as functional, performance, or mixed before deep analysis
- require the fault time window before broad log analysis
- require or discover the log path, require access to the metrics-history tool for performance issues, and confirm the source repo path or official read-only baseline
- prefer runtime-discovered log paths from `--log-dir` or `--store`, then fall back to `/var/lib/kaiwudb/logs`
- prioritize `errlog` crash stacks, then decisive `Eyy...`, `Wyy...`, or `Fyy...` context, for functional faults
- if the user already provides the slow SQL statement, go directly to `EXPLAIN ANALYZE`
- otherwise use the `kwdb-mcp-server` `query-metrics-history` tool to decide whether the bottleneck is CPU, IO, memory, or slow SQL for performance faults
- require `EXPLAIN ANALYZE` when the bottleneck points to slow SQL and a runnable environment exists
- optionally query the official repo issues API after the local signature is clear to avoid re-analyzing known issues
- ask for user approval before local reproduction and keep section 4 limited to actual fault reproduction steps
- always answer in the fixed seven-section incident format requested by the user
- record branch and commit only when a source repo is provided or discovered

## Non-Goals

- generic database administration checklists with no fault evidence
- speculative tuning without metrics or execution evidence
- publishing a large troubleshooting knowledge base inside `SKILL.md`

## Dependencies

- filesystem access for logs and local source repos
- shell commands such as `find`, `rg`, `git`, and `ps`
- access to the `kwdb-mcp-server` `query-metrics-history` tool for performance incidents
- optional SQL access for `EXPLAIN ANALYZE` and minimal inspection queries
- user-provided or discoverable fault time, SQL text, and environment details

## Pattern Choice

Use `Pipeline` as the dominant pattern because the diagnostic stages are ordered and skipping the first decisive artifact causes bad conclusions.
Use `Tool Wrapper` as the supporting pattern because the skill depends on concrete log, source, git, and SQL handling rules.
