#!/bin/bash
#===============================================================================
# KWDB Recent Logs - macOS
# macOS implementation of log retrieval
#===============================================================================

get_logs() {
    local since="$1"
    local lines="$2"
    local log_path="$3"

    # Try using log show (macOS 10.12+)
    if command -v log >/dev/null 2>&1; then
        local predicate="process contains 'kwdb' OR process contains 'kaiwudb'"
        local duration="${since// ago/}"
        LOG_LINES=$(log show --predicate "$predicate" --last "$duration" --style compact 2>/dev/null | head -n "$lines" || echo "")
    fi

    # If log show unavailable or no data, try reading log files
    if [ -z "$LOG_LINES" ] && [ -n "$log_path" ] && [ -f "$log_path" ]; then
        LOG_LINES=$(tail -n "$lines" "$log_path" 2>/dev/null || echo "")
    fi

    # Try common log paths (macOS)
    if [ -z "$LOG_LINES" ]; then
        for path in "/usr/local/var/log/kaiwudb/kwdb.log" "/usr/local/var/log/kwdb.log" "/opt/homebrew/var/log/kwdb.log" "$HOME/.kwdb/kwdb.log"; do
            if [ -f "$path" ]; then
                LOG_LINES=$(tail -n "$lines" "$path" 2>/dev/null || echo "")
                break
            fi
        done
    fi
}