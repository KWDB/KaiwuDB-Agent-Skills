# Regression Prompts

- User provides a slow SQL statement. The skill must skip the `query-metrics-history` tool and go directly to `EXPLAIN ANALYZE`.
- User does not provide a slow SQL statement for a performance issue. The skill must not jump directly to SQL tuning before using the metrics-history tool.
- User provides a `Wyy` line. The skill must inspect context and map it to source instead of only paraphrasing the warning.
- User does not provide the fault time. The skill must ask for the fault time window before broad log analysis.
- User asks for the branch and commit but no source repo is available. The skill must say it cannot confirm them.
- User asks for code correlation but has no local source repo. The skill must say it is using `https://gitee.com/kwdb/kwdb` as the read-only baseline.
- User finds a similar official issue. The skill must use it as supporting context, not replace local evidence.
- User asks to search similar issues automatically. The skill must avoid the HTML issues page and the global Gitee issue-search API, and must use the repo issues API or `scripts/search_gitee_issues.sh`.
- User asks in English, but the output must still use the fixed seven-section Chinese template.
- User does not provide a log path. The skill must check `--log-dir`, then `--store`, before falling back to `/var/lib/kaiwudb/logs`.
- User asks for a diagnostic report after log analysis. The skill must not put log-grep or source-reading steps under section 4.
- User has not approved local reproduction. The skill must leave section 4 blank instead of inventing reproduction steps.
