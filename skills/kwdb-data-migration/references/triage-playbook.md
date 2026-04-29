# Troubleshooting Playbook

1. Connection failed
    - Check network, port, firewall
    - Verify username/password
    - Check whitelist

2. Type mismatch
    - Check engine selection
    - Check official mapping
    - Watch UNSIGNED BIGINT, DECIMAL, JSON

3. Missing parameters
    - Time-series needs time_column, start_time, end_time

4. Time format error
    - Use yyyy-MM-dd HH:mm:ss

5. Slow migration / timeout
    - Increase channels
    - Reduce split interval
    - Add JVM memory

6. Data loss or inconsistency
    - Check WHERE filters
    - Switch to UPSERT
    - Check NULL / special chars
