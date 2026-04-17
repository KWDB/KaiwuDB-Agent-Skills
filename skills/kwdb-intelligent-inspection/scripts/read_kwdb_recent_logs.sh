#!/bin/bash
#===============================================================================
# KWDB Recent Logs
# Read recent KWDB log summary within a time window
# Supports Linux and macOS
#
# Usage: bash read_kwdb_recent_logs.sh SINCE [LINES] [LOG_PATH]
#   SINCE: Time window, e.g., "1 hour ago", default "1 hour ago"
#   LINES: Maximum lines, default 200
#   LOG_PATH: Optional log file path
#
# Output Format: JSON
#===============================================================================

# Source common function library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common_functions.sh"

SINCE="${1:-1 hour ago}"
LINES="${2:-200}"
LOG_PATH="${3:-}"

# Sanitize line count
if ! [[ "$LINES" =~ ^[0-9]+$ ]]; then
    LINES=200
fi
LINES=$((LINES > 500 ? 500 : LINES))
LINES=$((LINES < 1 ? 1 : LINES))

LOG_LINES=""
COUNT=0

#-------------------------------------------------------------------------------
# Linux implementation (journalctl or log files)
#-------------------------------------------------------------------------------
get_logs_linux() {
    # Prefer journalctl
    if command -v journalctl >/dev/null 2>&1; then
        LOG_LINES=$(journalctl --since "$SINCE" -u kaiwudb -u kwdb --no-pager -n "$LINES" 2>/dev/null || echo "")
    fi

    # If journalctl unavailable, try reading log files
    if [ -z "$LOG_LINES" ] && [ -n "$LOG_PATH" ] && [ -f "$LOG_PATH" ]; then
        LOG_LINES=$(tail -n "$LINES" "$LOG_PATH" 2>/dev/null || echo "")
    fi

    # Try common log paths
    if [ -z "$LOG_LINES" ]; then
        for path in "/var/log/kaiwudb/kwdb.log" "/var/log/kwdb.log" "/var/log/kaiwudb.log"; do
            if [ -f "$path" ]; then
                LOG_LINES=$(tail -n "$LINES" "$path" 2>/dev/null || echo "")
                break
            fi
        done
    fi
}

#-------------------------------------------------------------------------------
# macOS implementation (log show or log files)
#-------------------------------------------------------------------------------
get_logs_macos() {
    # Try using log show (macOS 10.12+)
    if command -v log >/dev/null 2>&1; then
        # Convert "1 hour ago" to macOS log format
        # Note: log show requires admin privileges to access system logs
        local predicate="process contains 'kwdb' OR process contains 'kaiwudb'"
        local duration="${SINCE// ago/}"

        # Try to get from unified logging system
        LOG_LINES=$(log show --predicate "$predicate" --last "$duration" --style compact 2>/dev/null | head -n "$LINES" || echo "")
    fi

    # If log show unavailable or no data, try reading log files
    if [ -z "$LOG_LINES" ] && [ -n "$LOG_PATH" ] && [ -f "$LOG_PATH" ]; then
        LOG_LINES=$(tail -n "$LINES" "$LOG_PATH" 2>/dev/null || echo "")
    fi

    # Try common log paths (macOS)
    if [ -z "$LOG_LINES" ]; then
        for path in "/usr/local/var/log/kaiwudb/kwdb.log" "/usr/local/var/log/kwdb.log" "/opt/homebrew/var/log/kwdb.log" "$HOME/.kwdb/kwdb.log"; do
            if [ -f "$path" ]; then
                LOG_LINES=$(tail -n "$LINES" "$path" 2>/dev/null || echo "")
                break
            fi
        done
    fi
}

#-------------------------------------------------------------------------------
# Main flow
#-------------------------------------------------------------------------------
if [ "$OS_TYPE" = "linux" ]; then
    get_logs_linux
elif [ "$OS_TYPE" = "darwin" ]; then
    get_logs_macos
else
    LOG_LINES=""
fi

# Build JSON array
echo "{"
echo "  \"since\": \"$SINCE\","

# Calculate actual line count
if [ -n "$LOG_LINES" ]; then
    ACTUAL_LINES=$(echo "$LOG_LINES" | wc -l | tr -d ' ')
else
    ACTUAL_LINES=0
fi
echo "  \"line_count\": $ACTUAL_LINES,"
echo "  \"logs\": ["

first=true
while IFS= read -r line && [ $COUNT -lt $LINES ]; do
    if [ -n "$line" ]; then
        COUNT=$((COUNT + 1))
        if [ "$first" = true ]; then
            first=false
        else
            echo ","
        fi
        # JSON string escaping
        escaped=$(echo "$line" | sed 's/\\/\\\\/g; s/"/\\"/g')
        echo "    \"$escaped\""
    fi
done <<< "$LOG_LINES"

echo ""
echo "  ]"
echo "}"
