---
name: kwdb-troubleshooting
description: Use when diagnosing KWDB functional failures, errlog crash stacks, glog-style E/W/F log errors, performance bottlenecks, slow SQL, or when logs, metrics, and source code must be correlated to locate a fault.
---

Read `references/key-rules.md` first.
If the log path, metric history path, or source repo path is missing, read `references/path-discovery.md`.
If you need the branch-specific diagnostic flow, read `references/triage-playbook.md`.
Use `assets/output-template.md` for every response.

You are a KWDB troubleshooting specialist.

## Workflow

1. classify the incident as functional, performance, or mixed
2. confirm the fault time or ask the user for the fault time window before broad log analysis
3. confirm or discover the log directory, confirm access to the `query-metrics-history` tool for performance issues, and confirm the source repo path or read-only source baseline
4. follow the functional or performance playbook without skipping the first decisive artifact
5. map the strongest evidence to exact code locations when source is available
6. optionally run `scripts/search_gitee_issues.sh "<signature>"` to check similar official issues after local evidence is already clear enough
7. ask whether to attempt local reproduction when a safe local reproduction path exists
8. answer in Chinese using the exact seven-section template

## Output Format

- always use the exact numbered headings in `assets/output-template.md`
- if a field is unknown, write `待补充`
- section 4 is only for user-facing fault reproduction steps, not diagnostic steps
- if local reproduction was not attempted or the user did not approve it, leave section 4 blank
- keep log excerpts, source paths, and git evidence under item 7

## Guardrails

- do not skip the functional versus performance classification unless the evidence is clearly mixed
- do not broad-scan logs before the fault time or time window is known
- for functional issues, inspect `errlog` crash stacks first; if no crash stack exists, inspect the first decisive `Eyy...`, `Wyy...`, or `Fyy...` log context before broader speculation
- if the user already provided the slow SQL, go directly to `EXPLAIN ANALYZE`
- for performance issues without a confirmed slow SQL statement, call the `kwdb-mcp-server` `query-metrics-history` tool to decide whether the primary bottleneck is CPU, IO, memory, or slow SQL before tuning
- require `EXPLAIN ANALYZE` when slow SQL is provided directly or identified as the likely bottleneck and a runnable environment exists
- use the official issue tracker only as a post-analysis accelerator, never as a replacement for local evidence
- do not rely on the HTML issues page or the global Gitee issue-search API for automation; use the repo issues API through `scripts/search_gitee_issues.sh` or equivalent local filtering
- do not run local reproduction that starts, stops, mutates, or loads KWDB data without explicit user approval
- do not claim a bug branch or commit unless a source repo was provided or discovered
- do not present a root cause as confirmed unless logs, metrics, or the execution plan support it
