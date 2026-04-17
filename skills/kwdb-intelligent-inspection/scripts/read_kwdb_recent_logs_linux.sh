#!/bin/bash
#===============================================================================
# KWDB Recent Logs - Linux
# Linux implementation of log retrieval
#===============================================================================

get_logs() {
    local since="$1"
    local lines="$2"
    local log_path="$3"

    # Prefer journalctl
    if command -v journalctl >/dev/null 2>&1; then
        LOG_LINES=$(journalctl --since "$since" -u kaiwudb -u kwdb --no-pager -n "$lines" 2>/dev/null || echo "")
    fi

    # If journalctl unavailable, try reading log files
    if [ -z "$LOG_LINES" ] && [ -n "$log_path" ] && [ -f "$log_path" ]; then
        LOG_LINES=$(tail -n "$lines" "$log_path" 2>/dev/null || echo "")
    fi

    # Try common log paths
    if [ -z "$LOG_LINES" ]; then
        for path in "/var/log/kaiwudb/kwdb.log" "/var/log/kwdb.log" "/var/log/kaiwudb.log"; do
            if [ -f "$path" ]; then
                LOG_LINES=$(tail -n "$lines" "$path" 2>/dev/null || echo "")
                break
            fi
        done
    fi
}