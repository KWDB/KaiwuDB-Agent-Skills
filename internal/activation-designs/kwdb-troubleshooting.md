# kwdb-troubleshooting Activation Design

## Should Trigger

- requests to diagnose a KWDB bug, fault, crash, restart, or wrong behavior
- requests to diagnose KWDB OOM, process kill, native memory growth, or a restart based on logs and system timestamps
- requests that mention `errlog`, glog-style `Eyy/Wyy/Fyy` log lines such as `E260313` or `W270101`, stack traces, or KWDB log analysis
- requests that mention cluster-wide unavailability, such as all nodes failing SQL connection or multiple nodes showing the same failure symptoms
- requests to analyze KWDB performance with the `query-metrics-history` tool or metrics-history results
- requests to locate a KWDB bottleneck with `EXPLAIN ANALYZE`
- requests to correlate a KWDB log line with source code
- requests that ask for a structured KWDB diagnostic report, with or without a specific template

## Should Not Trigger

- schema design requests
- deployment or installation setup without a fault symptom
- migration planning with no current failure
- generic SQL writing requests
- pure health-check or inspection requests with no incident
- pure recovery requests that ask how to repair or rebuild a cluster without asking for diagnosis
- generic performance tuning requests with no incident evidence

## False Positive Risks

- performance review requests that want tuning advice but not fault diagnosis
- generic log parsing tasks that are not about KWDB
- code review requests that mention branch and commit but no runtime failure
- cluster recovery requests that need an operations playbook rather than diagnosis

## False Negative Risks

- prompts that say "help me find the root cause" without naming troubleshooting
- prompts that mention OOM, restart, or `messages`/`dmesg` evidence but do not say "troubleshooting"
- prompts that mention `metric_history` or `errlog` but not the word "fault"
- prompts that provide only a log snippet and ask what happened
- prompts that say all nodes cannot connect through `kwbase sql` but do not mention logs yet
- prompts that describe a long degraded-running period followed by restart stalls without using the phrase "known issue"

## First Decision After Activation

Classify the incident as functional, performance, mixed, or cluster-level availability, then run the intake gate to collect any missing hard inputs before deep analysis:
hard fault time, targeted system evidence, log directory, metrics-history tool access, and optional source access.
