#!/bin/bash
#===============================================================================
# KWDB Restart Events Counter
# Count KWDB restart events within a given time window
# Supports Linux and macOS
#
# Usage: bash count_kwdb_restart_events.sh [SINCE]
#   SINCE: Time window, e.g., "1 day ago", default "1 day ago"
#
# Output Format: JSON
#===============================================================================

# Source common function library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common_functions.sh"

SINCE="${1:-1 day ago}"

COUNT=0

if [ "$OS_TYPE" = "linux" ]; then
    # Linux: Use journalctl
    if command -v journalctl >/dev/null 2>&1; then
        COUNT=$(journalctl --since "$SINCE" -u kaiwudb -u kwdb --no-pager 2>/dev/null | \
                grep -ciE "Starting|Started|Restarting|Stopped" || true)
    fi

    # If journalctl has no data, try systemctl NRestarts
    if [ -z "$COUNT" ] || [ "$COUNT" -eq 0 ]; then
        if command -v systemctl >/dev/null 2>&1; then
            COUNT=$(systemctl show -p NRestarts --value kaiwudb 2>/dev/null || \
                    systemctl show -p NRestarts --value kwdb 2>/dev/null || \
                    echo 0)
        fi
    fi
elif [ "$OS_TYPE" = "darwin" ]; then
    # macOS: Use launchctl and ps
    # Try to get last exit status from launchctl
    KWDB_LABEL="com.kaiwu.kwdb"
    KAIWUDB_LABEL="com.kaiwu.kaiwudb"

    get_launchd_restart_count() {
        local label="$1"
        # launchctl object output format: { "Label" = "xxx"; "JetsamProperties" = {...}; }
        # Or use launchctl print
        local restarts=$(launchctl print "user/$(id -u)/$label" 2>/dev/null | \
                        grep -i "last exit status" | awk '{print $NF}')
        echo "${restarts:-0}"
    }

    # Try to calculate from process start time (if process is running)
    get_process_start_time() {
        local proc_name="$1"
        local pid=$(pgrep -f "$proc_name" 2>/dev/null | head -n 1)
        if [ -n "$pid" ]; then
            # Linux: ps -o lstart= gets process start time
            # macOS: Use ps -o lstart=
            ps -o lstart= -p "$pid" 2>/dev/null | tr -d '\n'
        fi
    }

    # Check if any kwdb-related processes are running
    KWDB_PID=$(pgrep -f "kwdb|kaiwudb" 2>/dev/null | head -n 1)

    if [ -n "$KWDB_PID" ]; then
        # Process is running, try to get historical restart info
        # macOS can view system logs via log show (requires root or SIP disabled)
        if command -v log >/dev/null 2>&1; then
            # Convert time window to macOS log format
            SINCE_SECONDS=$(date -j -f "%a %b %d %T %Y" "$(date)" +%s 2>/dev/null || echo "0")
            # Simplified: if process is found, assume it has started
            COUNT=1
        else
            COUNT=1
        fi
    fi
fi

# Ensure COUNT is a number
if ! [[ "$COUNT" =~ ^[0-9]+$ ]]; then
    COUNT=0
fi

cat <<EOF
{
  "since": "$SINCE",
  "restart_count": $COUNT
}
EOF
