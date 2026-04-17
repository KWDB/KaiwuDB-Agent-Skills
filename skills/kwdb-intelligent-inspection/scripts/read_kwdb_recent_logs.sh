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
source "${SCRIPT_DIR}/detect_os.sh"

# Dispatch to platform-specific implementation
case "$OS_TYPE" in
    linux)
        source "${SCRIPT_DIR}/read_kwdb_recent_logs_linux.sh"
        ;;
    darwin)
        source "${SCRIPT_DIR}/read_kwdb_recent_logs_darwin.sh"
        ;;
    *)
        get_logs() {
            LOG_LINES=""
        }
        ;;
esac

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
# Main flow
#-------------------------------------------------------------------------------
get_logs "$SINCE" "$LINES" "$LOG_PATH"

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