# Key Rules

Required inputs:

- fault type or symptom
- fault time or time window
- log directory, startup arguments, or permission to discover them
- source repo path, or permission to use the official read-only source baseline at `https://gitee.com/kwdb/kwdb`
- access to the `kwdb-mcp-server` `query-metrics-history` tool or its returned results for performance incidents
- failing SQL or operation when the problem involves query latency or execution failure

Decision order:

1. classify the issue as functional, performance, or mixed
2. confirm the fault time; if missing, ask the user before broad log analysis
3. locate the evidence roots
4. pick the first decisive artifact
5. correlate that artifact with nearby context
6. map the decisive evidence to source code and git revision when possible
7. optionally search the official issue tracker for a matching known issue after the local signature is clear
8. decide whether a local reproduction attempt is safe and ask the user before running it
9. produce the fixed incident report

First decisive artifact rules:

- functional issue with `errlog` stack: start from the stack
- functional issue without crash stack: start from the first decisive `Eyy...`, `Wyy...`, or `Fyy...` line in the failure window
- performance issue with a user-provided slow SQL statement: start from `EXPLAIN ANALYZE`
- performance issue without a confirmed slow SQL statement: start from the `query-metrics-history` tool results
- slow SQL identified after metrics analysis: use `EXPLAIN ANALYZE`

Evidence rules:

- use the failure time to limit the log window before reading broadly
- if the fault time is missing, ask the user first instead of scanning the full log history
- prefer `--log-dir` over inferred paths, and prefer `--store/logs` over generic filesystem search when `--log-dir` is absent
- prefer the first log line that contains both a severity token and a source file suffix
- treat the year fragment in glog-style prefixes as variable: `E26...` and `W26...` are 2026 examples, while January 1, 2027 and later will typically appear as `E27...`, `W27...`, or `F27...`
- when citing code, include the source path and the log path or SQL evidence that led to it
- if multiple source repos exist, state which one was used and why

Metric rules:

- for performance incidents with no confirmed slow SQL statement, explicitly call the `kwdb-mcp-server` `query-metrics-history` tool
- do not treat `metric_history` as a filesystem path or local file
- if the metrics-history tool is unavailable, say so directly and ask the user for its results or access

SQL rules:

- if the user already provides the slow SQL statement, skip the metrics-history tool and go directly to `EXPLAIN ANALYZE`
- if `EXPLAIN ANALYZE` is not runnable, say so directly and ask for plan output or execution access

Source rules:

- prefer the user-provided local source repo when available
- if no local source repo is available, use `https://gitee.com/kwdb/kwdb` as the read-only source baseline for code-location analysis
- state clearly whether item 1 is based on a local repo or the official read-only baseline

Issue-tracker rules:

- use the issue tracker only after you already have a concrete local signature such as an error string, file:line, function name, or plan symptom
- prefer `scripts/search_gitee_issues.sh "<signature>"`, which calls `https://gitee.com/api/v5/repos/kwdb/kwdb/issues` and filters `title/body` locally
- do not rely on the HTML issues page or `https://gitee.com/api/v5/search/issues` for automated diagnosis because those paths are noisy or unstable for repo-scoped matching
- use the issue tracker to find similar known cases, fixes, or workarounds
- if no similar issue is found, continue with the local evidence only
- do not treat a similar issue as proof unless the local evidence matches

Reproduction rules:

- section 4 must describe how to reproduce the fault, not how the agent diagnosed it
- ask the user before attempting local reproduction
- if the user approves local reproduction, record only the minimal steps that reproduce the user-visible fault
- if the user declines, does not answer, or local reproduction is unsafe, leave section 4 blank
- do not include log-grep, source-reading, or root-cause-analysis steps in section 4

Output rules:

- always reply in Chinese
- always use the seven numbered headings from `assets/output-template.md`
- if the user did not provide enough data, keep the format and fill unknown fields with `待补充`, except section 4 when reproduction was not approved or attempted
- item 1 must stay evidence-based: if branch and commit cannot be confirmed, say so directly
