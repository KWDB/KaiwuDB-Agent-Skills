# Functional Tests

- Run a full KWDB inspection with all default metrics and anomaly rules enabled.
- Inspect a KWDB cluster on specific nodes `192.168.1.10:26257` and `192.168.1.11:26257` with the default ports confirmed by the user.
- Perform a KWDB inspection with only Basic Metrics and System Resources categories selected.
- Run an inspection with a custom CPU alert threshold set to 85% and replication lag threshold set to 8 seconds.
- Generate an HTML-format inspection report for a KWDB cluster.
- Execute a KWDB inspection that involves only slow query analysis.
- Run an inspection on a KWDB cluster deployed in non-TLS mode, verifying all metrics are collected successfully.
- Inspect KWDB with Configurable Anomaly Rules disabled (alerting skipped), reporting only raw metrics.
- Run a KWDB inspection and verify that port listening status for ports 26257 and 8080 is included in the report.
- Perform a KWDB inspection with Data Distribution Balance and Replica Status anomaly rules enabled, with thresholds confirmed by the user.
