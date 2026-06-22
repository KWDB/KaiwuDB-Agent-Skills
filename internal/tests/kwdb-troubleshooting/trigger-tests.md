# Trigger Tests

## Positive Cases

| ID | Prompt | Expected |
| --- | --- | --- |
| TRG-P01 | Analyze this KWDB `errlog` stack and tell me which source file is responsible. | Should trigger `kwdb-troubleshooting` because the request is a KWDB functional fault diagnosis with crash evidence. |
| TRG-P02 | I have a `W270101` warning in KWDB logs. Help me find the root cause. | Should trigger because glog-style KWDB severity lines are an explicit activation signal. |
| TRG-P03 | The user says KWDB OOM happened around 2:30 PM. Use `messages` or `dmesg` to anchor the real time, then analyze the service logs. | Should trigger because OOM and system-evidence anchoring are core troubleshooting cases. |
| TRG-P04 | Use the `query-metrics-history` tool to diagnose why this KWDB query is slow. I do not have the SQL text yet. | Should trigger because this is a KWDB performance incident that depends on metrics-history analysis. |
| TRG-P05 | I already have the slow SQL. Use `EXPLAIN ANALYZE` and nearby logs to diagnose the KWDB bottleneck. | Should trigger because direct slow-SQL diagnosis is part of the performance path. |
| TRG-P06 | This KWDB incident has both timeout errors and memory growth. Follow `故障时间 -> 日志 -> 可选源码 -> 可选提交历史 -> 整体分析`. | Should trigger because the prompt explicitly asks for the troubleshooting investigation chain. |
| TRG-P07 | Here is a KWDB log snippet with `E260313` and `file.go:123`. Tell me what happened and whether it maps to source code. | Should trigger because the prompt asks for KWDB log diagnosis and optional source correlation. |

## Negative Cases

| ID | Prompt | Expected |
| --- | --- | --- |
| TRG-N01 | Design a KWDB schema for sensor telemetry. | Should not trigger because this is schema design, not incident diagnosis. |
| TRG-N02 | Show me how to deploy a single-node KWDB cluster. | Should not trigger because this is installation or deployment guidance. |
| TRG-N03 | Write SQL for a daily report. | Should not trigger because this is generic SQL authoring. |
| TRG-N04 | Review my frontend component. | Should not trigger because the task is unrelated to KWDB troubleshooting. |
| TRG-N05 | Give me general KWDB performance tuning advice for bulk import. There is no current failure. | Should not trigger because it is tuning advice with no incident evidence. |
| TRG-N06 | Parse this Linux `syslog` and summarize it. It is not related to KWDB. | Should not trigger because it is generic log parsing outside KWDB. |
| TRG-N07 | Tell me whether this KWDB commit message is good. | Should not trigger because it is repository review, not runtime fault diagnosis. |

## Boundary Cases

| ID | Prompt | Expected |
| --- | --- | --- |
| TRG-B01 | Help me find the root cause of this KWDB restart from `messages` and `dmesg`. | Should trigger even without the word `troubleshooting` because restart and system evidence imply an incident. |
| TRG-B02 | Here is a KWDB `metric_history` result export. What bottleneck does it show? | Should trigger even if the prompt does not say `fault`, because metrics-history analysis is a supported performance entry point. |
| TRG-B03 | I only have a KWDB log snippet. What happened? | Should trigger because a KWDB log-only prompt is a documented false-negative risk that the skill should catch. |
| TRG-B04 | Optimize this known slow report SQL for better speed. I do not need fault diagnosis. | Should not trigger because the user asks for optimization advice, not troubleshooting. |
| TRG-B05 | I need a daily health check checklist for KWDB nodes. | Should not trigger because there is no active incident or concrete failure symptom. |
| TRG-B06 | Help me correlate this KWDB log line with the responsible branch and commit. | Should trigger because explicit history attribution from a runtime symptom is an in-scope optional depth extension. |
