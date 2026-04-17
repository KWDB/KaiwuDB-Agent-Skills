# Triage Playbook

## Functional Path

1. confirm the fault time or ask the user for the fault time window
2. determine the effective log directory from `--log-dir`, `--store/logs`, or the default path before reading logs broadly
3. inspect `errlog` first
4. if `errlog` contains a crash stack, extract the top frames, component, and file suffix, then map them to the source repo or official read-only baseline
5. if there is no crash stack, search decisive `Eyy...`, `Wyy...`, or `Fyy...` lines only within the fault time window
6. expand around the first decisive severity line to capture context, nearby retries, and preceding warnings
7. map the decisive file suffix from the log to source code
8. if the log indicates a known SQL object, include the object name, SQL text, or operation in the report

## Performance Path

1. confirm the fault time or ask the user for the fault time window
2. determine the effective log directory from `--log-dir`, `--store/logs`, or the default path so warnings can be correlated with the metric window
3. if the user already provided the slow SQL statement, go directly to `EXPLAIN ANALYZE`
4. if no slow SQL statement is confirmed, call the `kwdb-mcp-server` `query-metrics-history` tool for the fault time window
5. decide whether the first hard bottleneck is CPU, IO, memory, or slow SQL
6. if slow SQL is primary, capture the SQL text and run `EXPLAIN ANALYZE` when possible
7. use the execution plan to identify the concrete bottleneck: large scan, bad join order, sort or hash pressure, network exchange, spill, or contention
8. correlate the plan with metrics and nearby warnings before naming the root cause

## Mixed Path

1. choose the first decisive artifact by time
2. explain whether the performance symptom caused the functional symptom or vice versa
3. keep one primary root-cause candidate and move the rest to supporting hypotheses

## Minimal Verification

- functional issue: confirm the decisive log line still maps to the cited source file
- performance issue: confirm the plan and metrics point to the same bottleneck class
- mixed issue: confirm the timeline is consistent across logs, metrics, and SQL evidence

## Known-Issue Check

1. after the local signature is clear, optionally run `scripts/search_gitee_issues.sh "<signature>"`
2. search by decisive error text, file:line, function name, or slow-SQL symptom
3. if a similar issue exists, use it only as supporting context for versions, fixes, or workarounds
4. if no similar issue exists, do not block the diagnosis

## Reproduction Gate

1. after evidence analysis, decide whether the fault can be reproduced locally without unsafe data mutation
2. ask the user for approval before running any reproduction attempt
3. if approved, run the smallest reproduction that triggers the same user-visible symptom
4. if declined or not approved, do not invent reproduction steps
5. keep diagnostic commands out of section 4; put evidence commands or source references in section 7 when needed
