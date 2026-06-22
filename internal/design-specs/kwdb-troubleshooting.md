# kwdb-troubleshooting Design Spec

## Use Case

Help users diagnose KWDB incidents from logs, metrics, system evidence, and optional source-code correlation.
The skill is a general KWDB diagnostic surface for functional faults, OOM or process-kill incidents, restarts, slow SQL, performance bottlenecks, and cluster-wide availability symptoms.

## Success Criteria

- classify the incident as functional, performance, mixed, or cluster-level availability before deep analysis
- run an intake gate first and ask for missing hard inputs before deep diagnosis
- require the fault time window before broad log analysis, and use targeted system-evidence checks for OOM or process-kill incidents
- require or discover the log path, require access to the metrics-history tool for performance issues, and confirm whether source access is available
- prefer runtime-discovered log paths from `--log-dir` or `--store`, then fall back to `/var/lib/kaiwudb/logs`
- when logs from multiple nodes or symptoms imply cluster-wide unavailability, merge the node timeline before concluding on one node
- narrow high-volume incidents through `30 minutes`, `10 minutes`, and `1 minute` windows before broad reading
- prioritize `errlog` crash stacks, then decisive `Eyy...`, `Wyy...`, or `Fyy...` context, for functional faults
- if the user already provides the slow SQL statement, go directly to `EXPLAIN ANALYZE`
- otherwise use the `kwdb-mcp-server` `query-metrics-history` tool to decide whether the bottleneck is CPU, IO, memory, or slow SQL for performance faults
- require `EXPLAIN ANALYZE` when the bottleneck points to slow SQL and a runnable environment exists
- cluster repeated business objects, amplifier events, or node transitions before mapping to code
- if source access is available, extend the result from an evidence conclusion to a source-level localization with the smallest useful call chain
- if source access is unavailable, stop at the evidence conclusion and say that source correlation was not performed
- do not default to branch or commit tracing; use git history only when the user explicitly asks for history attribution and the code path is already confirmed
- optionally query the official repo issues API after the local signature is clear to avoid re-analyzing known issues
- when the customer cannot access issue trackers or internal bug systems, allow version + timeline + symptom matching to conclude that a case is highly consistent with a known fault pattern
- distinguish `pattern-consistent` from `confirmed by issue lookup`
- when a case contains both a primary fault and a risk amplifier, report them separately
- default to a general diagnostic report
- use the seven-section test-case template only when the user explicitly asks for it
- stay diagnosis-only: do not produce recovery runbooks, repair sequencing, or reproduction plans by default

## Non-Goals

- generic database administration checklists with no fault evidence
- speculative tuning without metrics or execution evidence
- recovery plans, decommission advice, or repair sequencing
- reproduction planning as a default diagnostic output
- default branch or commit hunting when the user asked only for diagnosis
- publishing a large troubleshooting knowledge base inside `SKILL.md`

## Dependencies

- filesystem access for logs and local source repos
- shell commands such as `find`, `rg`, `git`, and `ps`
- access to the `kwdb-mcp-server` `query-metrics-history` tool for performance incidents
- optional SQL access for `EXPLAIN ANALYZE` and minimal inspection queries
- user-provided or discoverable fault time, SQL text, and environment details

## Pattern Choice

Use `Pipeline` as the dominant pattern because the intake gate, routed triage paths, and evidence order are mandatory and cannot be skipped safely.
Use `Generator` as the supporting pattern because the skill must produce a stable diagnostic report by default and optionally a fixed seven-section test-case report when explicitly requested.
Keep the intake questioning as a gate inside the pipeline rather than a separate full `Inversion` pattern.
Runtime references still act in a tool-wrapper style by holding domain rules and path-specific constraints, but they are supporting reference surfaces rather than a third dominant pattern.
