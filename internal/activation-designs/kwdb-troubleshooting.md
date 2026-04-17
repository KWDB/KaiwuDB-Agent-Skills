# kwdb-troubleshooting Activation Design

## Should Trigger

- requests to diagnose a KWDB bug, fault, crash, restart, or wrong behavior
- requests that mention `errlog`, glog-style `Eyy/Wyy/Fyy` log lines such as `E260313` or `W270101`, stack traces, or KWDB log analysis
- requests to analyze KWDB performance with the `query-metrics-history` tool or metrics-history results
- requests to locate a KWDB bottleneck with `EXPLAIN ANALYZE`
- requests to correlate a KWDB log line with source code and git revision

## Should Not Trigger

- schema design requests
- deployment or installation setup without a fault symptom
- migration planning with no current failure
- generic SQL writing requests
- pure health-check or inspection requests with no incident

## False Positive Risks

- performance review requests that want tuning advice but not fault diagnosis
- generic log parsing tasks that are not about KWDB
- code review requests that mention branch and commit but no runtime failure

## False Negative Risks

- prompts that say "help me find the root cause" without naming troubleshooting
- prompts that mention `metric_history` or `errlog` but not the word "fault"
- prompts that provide only a log snippet and ask what happened

## First Decision After Activation

Classify the incident as functional, performance, or mixed, then confirm or discover the evidence roots:
fault time, log directory, metrics-history tool access, and source repo path.
