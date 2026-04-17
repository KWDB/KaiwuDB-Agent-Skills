# Test Method

## Test Layers

1. trigger tests for troubleshooting-only prompts
2. functional tests for the functional, performance, and mixed paths
3. regression prompts for missing-path and wrong-order failures
4. runtime structure validation with `quick_validate.py`

## Execution Order

1. validate `SKILL.md` frontmatter and description
2. confirm the skill asks for the fault time before broad log analysis
3. confirm the skill checks `--log-dir`, then `--store/logs`, before falling back to the default log directory
4. confirm the performance path goes directly to `EXPLAIN ANALYZE` when the user already provides the slow SQL
5. confirm the performance path explicitly uses the `query-metrics-history` tool only when no slow SQL is confirmed
6. confirm the known-issue check is optional, only runs after a local signature is clear, and uses the repo issues API rather than the HTML page
7. confirm the workflow branches correctly between functional and performance incidents
8. confirm section 4 contains only reproduction steps, not diagnostic steps
9. confirm section 4 stays blank when local reproduction is not approved or attempted
10. confirm every final answer uses the seven-section output template
11. confirm branch and commit are only reported when backed by a discovered repo or the official read-only baseline is stated explicitly

## Pass / Fail Criteria

- pass when the response follows the path-discovery rules, triage order, and fixed format
- fail when the response skips the classification step, scans logs without a fault time window, ignores `errlog`, wrongly skips `EXPLAIN ANALYZE` when slow SQL is provided, wrongly skips the metrics-history tool when no slow SQL is known, treats issue search as primary evidence, uses the HTML issues page or global Gitee issue-search API as an automated method, invents branch and commit data, or uses section 4 for diagnostic steps

## Real Environment Validation

- validated that runtime log discovery prefers `--log-dir`, then `--store/logs`, then `/var/lib/kaiwudb/logs`
- validated that developer-local paths are not default production assumptions
- validated that source repo paths are user-provided, and that `https://gitee.com/kwdb/kwdb` is the fallback read-only baseline
- validated that performance diagnosis refers to the `kwdb-mcp-server` `query-metrics-history` tool rather than a local file path
- validated that known-issue lookup uses the repo issues API with local filtering rather than the HTML issues page
