# Functional Tests

- functional fault with `errlog` stack and a provided source repo path
- functional fault with `Eyy/Wyy/Fyy` lines but no crash stack
- functional fault with missing fault time where the skill must ask the user before scanning logs
- performance fault with a user-provided slow SQL statement where the skill goes directly to `EXPLAIN ANALYZE`
- performance fault with `query-metrics-history` tool results and no confirmed slow SQL statement
- request with no log path where the skill must inspect `ps -ef` for `--log-dir` or infer `--store/logs`
- request with no local source repo where the skill must use the official read-only source baseline
- incident where a clear local signature exists and the skill optionally checks official issues through the repo issues API as a post step
- incident analysis where the user approves local reproduction and section 4 contains only reproduction steps
- incident analysis where the user does not approve local reproduction and section 4 stays blank
