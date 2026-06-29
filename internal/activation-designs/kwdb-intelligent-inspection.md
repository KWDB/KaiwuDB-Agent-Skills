# kwdb-intelligent-inspection Activation Design

## Should Trigger

- requests to run KaiwuDB inspection or health check
- requests to collect database metrics and generate reports
- requests to detect anomalies in database/system metrics
- requests to check database cluster status
- requests to perform database health monitoring

## Should Not Trigger

- schema design or DDL requests
- deployment or installation questions
- migration questions
- pure performance tuning questions without inspection context
- troubleshooting questions unrelated to metrics inspection

## False Positive Risks

- generic "check database status" without KaiwuDB context
- requests to "check system metrics" for non-KWDB databases

## False Negative Risks

- prompts that say "how is my KWDB doing" or "check if KWDB is healthy"
- requests that mention "inspection" or "巡检" without explicit metric language

## First Decision After Activation

Determine the inspection scope and priorities:
1. Confirm target nodes and time range
2. Identify which metrics sections are applicable
3. Determine if any threshold overrides are specified
4. Select output format (Markdown default, HTML/PDF optional)
