#!/bin/bash
#===============================================================================
# KWDB Service Status
# Get KWDB service running status, PID, start time, and process/container clues
# Supports Linux and macOS
#
# Usage: bash get_kwdb_service_status.sh [SERVICE_NAME]
#   SERVICE_NAME: Service name, default kwdb
#
# Output Format: JSON
#===============================================================================

# Source common function library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/detect_os.sh"

# Dispatch to platform-specific implementation
case "$OS_TYPE" in
    linux)
        source "${SCRIPT_DIR}/get_kwdb_service_status_linux.sh"
        ;;
    darwin)
        source "${SCRIPT_DIR}/get_kwdb_service_status_darwin.sh"
        ;;
    *)
        get_service_status() {
            ACTIVE_STATE="unknown"; SUB_STATE="unknown"; MAIN_PID=""; STARTED_AT=""
        }
        get_process_clues() {
            PROCESS_MATCH=""
        }
        ;;
esac

SERVICE_NAME="${1:-kwdb}"

#-------------------------------------------------------------------------------
# Main flow
#-------------------------------------------------------------------------------
get_service_status "$SERVICE_NAME"
get_process_clues

# Container clues (cross-platform)
CONTAINER_MATCH=$(docker ps --format '{{.ID}} {{.Image}} {{.Status}} {{.Names}}' 2>/dev/null | grep -Ei "kwdb|kaiwudb" | head -n 1 || echo "")

# JSON output (handle empty values)
process_hint_escaped="${PROCESS_MATCH//\"/\\\"}"
container_hint_escaped="${CONTAINER_MATCH//\"/\\\"}"

cat <<EOF
{
  "service_name": "$SERVICE_NAME",
  "active_state": "$ACTIVE_STATE",
  "sub_state": "$SUB_STATE",
  "main_pid": "${MAIN_PID:-}",
  "started_at": "$STARTED_AT",
  "process_hint": "$process_hint_escaped",
  "container_hint": "$container_hint_escaped"
}
EOF