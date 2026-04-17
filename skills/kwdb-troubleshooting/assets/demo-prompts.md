# Demo Prompts

- 请根据 `/var/lib/kaiwudb/logs` 下的 `errlog` 和源码目录，定位这次 KWDB 宕机的根因，并按固定七段格式输出。
- 我抓到一段 `W260416` 日志，请结合上下文和源码给出故障定位结果，输出必须包含分支和 commit。
- 我抓到一段 `W270101` 日志，请结合上下文和源码给出故障定位结果，输出必须包含分支和 commit。
- 这是一次性能问题，用户已经提供慢 SQL。请直接用 `EXPLAIN ANALYZE` 定位瓶颈。
- 这是一次性能问题，但还没有明确慢 SQL。请先调用 `kwdb-mcp-server` 的 `query-metrics-history` 工具判断是 CPU、IO、内存还是慢 SQL，再用 `EXPLAIN ANALYZE` 定位瓶颈。
- 我只给你一段 E26 日志和一个源码仓库路径。请找出最相关代码位置并按模板写 incident report。
