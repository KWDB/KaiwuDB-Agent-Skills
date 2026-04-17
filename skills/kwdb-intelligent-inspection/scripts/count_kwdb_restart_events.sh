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
source "${SCRIPT_DIR}/detect_os.sh"

# Dispatch to platform-specific implementation
case "$OS_TYPE" in
    linux)
        source "${SCRIPT_DIR}/count_kwdb_restart_events_linux.sh"
        ;;
    darwin)
        source "${SCRIPT_DIR}/count_kwdb_restart_events_darwin.sh"
        ;;
    *)
        get_restart_count() {
            echo "0"
        }
        ;;
esac

SINCE="${1:-1 day ago}"

#-------------------------------------------------------------------------------
# Main flow
#-------------------------------------------------------------------------------
COUNT=$(get_restart_count "$SINCE")

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