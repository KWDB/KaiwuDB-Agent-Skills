# Regression Prompts

## Cluster-Level Availability Fault

| ID | Prompt | Expected behavior |
| --- | --- | --- |
| REG-C01 | 4 个节点都无法通过 `kwbase sql` 连接，且至少 2 个节点日志同时出现 `gossip stalled`、`node liveness heartbeat` 超时、`lease holder unknown`。请先判断这是否应升级为集群级系统 range 故障，并避免先把结论收缩成单节点问题。 | Should upgrade the case to cluster-level availability analysis, merge the multi-node timeline before concluding on any one node, and keep the output diagnosis-only rather than turning it into a repair runbook. |
| REG-C02 | 现场是 2.x 四节点集群，其中一个 30G 节点在 4 月 30 日凌晨 OOM 宕机；集群降级运行十多天后，在 5 月 18 日重新拉起该故障节点，出现一段时间读写卡住，随后又恢复。客户无法访问内部 issue 或已知问题库，但补充说故障节点重启后仍有 `6000+` mount 文件，占用 `20GB+` 内存。请给出最终分析。 | Should identify two layers separately: first, the restart stall is highly consistent with a 2.x HA known pattern after long degraded running and delayed node rejoin; second, persistent mount-file accumulation is a separate OOM-risk amplifier. It should not require external issue retrieval to reach the pattern-consistent conclusion, and it should not turn the analysis into a recovery plan. |
