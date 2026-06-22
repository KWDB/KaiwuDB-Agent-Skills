# Functional Tests

## Core Classification And Entry

| ID | Scenario | Expected behavior |
| --- | --- | --- |
| FNC-C01 | Functional fault with `errlog` stack and a provided local source repo path. | Classify as functional, start from the stack, map to the smallest useful source call chain, and use the general diagnostic report unless the user explicitly asks for another template. |
| FNC-C02 | Functional fault with `Eyy/Wyy/Fyy` lines but no crash stack. | Classify as functional and start from the first decisive severity line inside the fault window instead of speculating broadly. |
| FNC-C03 | Performance fault with a user-provided slow SQL statement. | Classify as performance and go directly to `EXPLAIN ANALYZE` instead of calling metrics-history first. |
| FNC-C04 | Performance fault with no confirmed slow SQL statement, but `query-metrics-history` results are available. | Classify as performance, use the metrics result first, identify CPU, IO, memory, or slow SQL as the primary bottleneck, then decide whether `EXPLAIN ANALYZE` is required. |
| FNC-C05 | Mixed incident where memory growth appears before query timeout errors. | Classify as mixed, choose the first decisive artifact by time, explain the causal chain, and keep one primary root-cause candidate. |
| FNC-C06 | Cluster-wide availability incident where all nodes temporarily fail `kwbase sql` after a degraded-running period. | Upgrade to cluster-level availability analysis and build the merged node timeline before concluding on one node. |

## Intake Gate And Large-Log Slicing

| ID | Scenario | Expected behavior |
| --- | --- | --- |
| FNC-I01 | Functional fault with missing fault time. | Ask for the fault time or time window before broad log scanning. |
| FNC-I02 | OOM or process-kill fault where the user gives only an approximate time. | Verify the user report with targeted `messages`, `syslog`, or `dmesg` checks for `oom` and `kwbase` before trusting the reported time. |
| FNC-I03 | Performance fault without SQL text and without metrics-history access. | Ask for the smallest missing blocker, such as slow SQL text or metrics-history results, before deep diagnosis. |
| FNC-I04 | Source-level localization is impossible because the user provides no repo path and does not approve downloading one. | Stop at the evidence conclusion and state that source correlation was not performed. |
| FNC-I05 | Large-log incident with a confirmed hard timestamp and very high log volume. | Narrow the read path through `30 minutes`, `10 minutes`, and `1 minute` windows before broader reading. |
| FNC-I06 | User-reported fault time conflicts with the hard OOM timestamp from system evidence. | Report both times, use the hard time as the main analysis anchor, and say that the user-reported time was approximate. |
| FNC-I07 | Large-log incident with repeated retries, `context canceled`, and repeated table names near the fault time. | Cluster repeated amplifier events and business objects before mapping to source or history. |

## Path Discovery And Evidence Roots

| ID | Scenario | Expected behavior |
| --- | --- | --- |
| FNC-P01 | Request with no log path, but process arguments are readable. | Inspect `ps -ef` for `--log-dir` first, then `--store`, and prefer `STORE_PATH/logs` over generic filesystem search. |
| FNC-P02 | Request with no log path and no readable startup arguments. | Fall back to default KWDB log paths and state that runtime-discovered paths were unavailable. |
| FNC-P03 | OOM incident with no explicit system-log path, but a case directory contains exported `messages` or `dmesg`. | Prefer the case-level system evidence export before host-level defaults. |
| FNC-P04 | Multiple candidate log directories exist. | Prefer the directory whose timestamps match the fault window and say which one was chosen. |
| FNC-P05 | Performance request refers to `metric_history` as if it were a local file path. | Do not treat it as a filesystem path; require the `query-metrics-history` tool or exported results instead. |

## Source Localization And Optional History Attribution

| ID | Scenario | Expected behavior |
| --- | --- | --- |
| FNC-S01 | Request with no local source repo where the user declines downloading the official repo. | Continue with logs and metrics only, and state that source correlation was not performed. |
| FNC-S02 | Request with no local source repo where the user approves downloading the official repo. | Use the approved official repo for source-level localization and state that the conclusion relies on the downloaded repo rather than a local tree. |
| FNC-S03 | Incident where decisive log evidence maps cleanly to a source path and the code path is confirmed. | Build the smallest useful call chain and stop at source-level localization unless the user explicitly asked for history attribution. |
| FNC-S04 | Incident where the log gives only a file suffix and multiple local repos could match. | State which repo was selected and why, instead of silently choosing one. |
| FNC-S05 | Incident where source evidence is sufficient for a suspicious module, but not for a single causal commit. | Do not claim one exact branch or commit; say that branch or commit cannot be uniquely confirmed. |
| FNC-S06 | Incident where the user explicitly asks for branch or commit tracing after the code path is confirmed. | Extend from source-level localization to `git blame` / `git log` only after the code path is grounded. |

## Performance-Specific Guardrails

| ID | Scenario | Expected behavior |
| --- | --- | --- |
| FNC-Q01 | Performance fault without SQL text and without metrics-history tool access. | Say the tool is unavailable, ask for its results or access, and avoid speculative tuning. |
| FNC-Q02 | Slow SQL is identified after metrics analysis, but `EXPLAIN ANALYZE` cannot be run in the current environment. | Ask for plan output or execution access and avoid claiming a confirmed SQL root cause without plan evidence. |
| FNC-Q03 | Metrics indicate CPU pressure, but nearby logs show repeated spill or sort warnings. | Correlate metrics and log warnings before naming the bottleneck class. |

## Output Modes And Constraints

| ID | Scenario | Expected behavior |
| --- | --- | --- |
| FNC-O01 | Standard incident analysis with partial data and no requested template. | Use the general diagnostic report, fill unknown fields with `待补充`, and keep the conclusion at the evidence or source-localization level supported by the inputs. |
| FNC-O02 | Incident analysis where the user explicitly asks for the fixed seven-section test-case template. | Use the seven-section template and keep unsupported fields as `待补充`. |
| FNC-O03 | Seven-section output request where the user does not provide or confirm reproduction steps. | Keep section 4 blank. |
| FNC-O04 | Incident where a clear local signature exists and the skill optionally checks official issues through the repo issues API as a post step. | Use issue search only after local evidence is grounded and treat matching issues as supporting context, not proof. |
| FNC-O05 | Any normal successful response path. | Reply in Chinese and do not add recovery runbooks, repair sequencing, or reproduction plans. |
| FNC-O06 | No-source incident with a strong version, timeline, and symptom match to a known pattern, but no externally retrievable issue link. | Mark the result as `高度吻合某类已知问题模式` and distinguish that from full external confirmation. |

## Cluster-Level And Known-Pattern Handling

| ID | Scenario | Expected behavior |
| --- | --- | --- |
| FNC-K01 | A 2.x four-node cluster loses one 30G node to OOM, runs degraded for 10+ days, then stalls for a period after that node is restarted; all nodes are temporarily unavailable through `kwbase sql`, and the customer cannot access internal issue systems. | Upgrade to cluster-level availability analysis, reconstruct `initial failure -> degraded running period -> restart symptom -> recovery behavior`, conclude that the restart stall is highly consistent with a known 2.x HA pattern without requiring external issue retrieval, and separately report persistent mount-file accumulation as an OOM-risk amplifier rather than the same root cause. |
