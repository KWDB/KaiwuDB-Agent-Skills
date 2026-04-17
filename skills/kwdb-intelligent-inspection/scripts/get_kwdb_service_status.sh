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
source "${SCRIPT_DIR}/common_functions.sh"

SERVICE_NAME="${1:-kwdb}"

#-------------------------------------------------------------------------------
# Linux (systemd) implementation
#-------------------------------------------------------------------------------
get_status_linux() {
    ACTIVE_STATE=$(systemctl is-active kaiwudb 2>/dev/null || systemctl is-active "$SERVICE_NAME" 2>/dev/null || echo "unknown")
    SUB_STATE=$(systemctl show -p SubState --value kaiwudb 2>/dev/null || systemctl show -p SubState --value "$SERVICE_NAME" 2>/dev/null || echo "unknown")
    MAIN_PID=$(systemctl show -p MainPID --value kaiwudb 2>/dev/null || systemctl show -p MainPID --value "$SERVICE_NAME" 2>/dev/null || echo "")
    STARTED_AT=$(systemctl show -p ActiveEnterTimestamp --value kaiwudb 2>/dev/null || systemctl show -p ActiveEnterTimestamp --value "$SERVICE_NAME" 2>/dev/null || echo "")
}

#-------------------------------------------------------------------------------
# macOS (launchctl) implementation
#-------------------------------------------------------------------------------
get_status_macos() {
    # macOS service name convention: com.kaiwu.kaiwudb or com.kaiwu.kwdb
    local label="com.kaiwu.${SERVICE_NAME}"

    # Check if service exists in launchctl
    if launchctl list | grep -q "$label" 2>/dev/null; then
        # Try to get service status
        local service_info=$(launchctl print "user/$(id -u)/$label" 2>/dev/null || launchctl print "system/$label" 2>/dev/null)

        if [ -n "$service_info" ]; then
            # Extract status from print output
            if echo "$service_info" | grep -q "state = running"; then
                ACTIVE_STATE="active"
                SUB_STATE="running"
            elif echo "$service_info" | grep -q "state = stopped"; then
                ACTIVE_STATE="inactive"
                SUB_STATE="stopped"
            else
                ACTIVE_STATE="unknown"
                SUB_STATE="unknown"
            fi

            # Extract PID (if available)
            MAIN_PID=$(echo "$service_info" | grep "pid =" | head -1 | awk '{print $NF}')
        else
            ACTIVE_STATE="unknown"
            SUB_STATE="unknown"
        fi
    else
        # Not registered in launchctl, try to detect from process directly
        ACTIVE_STATE="unknown"
        SUB_STATE="unknown"
    fi

    # If PID not obtained, try to get from process list
    if [ -z "$MAIN_PID" ]; then
        MAIN_PID=$(pgrep -f "kwdb|kaiwudb" 2>/dev/null | head -n 1 || echo "")
    fi
}

#-------------------------------------------------------------------------------
# Main flow
#-------------------------------------------------------------------------------
if [ "$OS_TYPE" = "linux" ]; then
    get_status_linux
elif [ "$OS_TYPE" = "darwin" ]; then
    get_status_macos
else
    ACTIVE_STATE="unknown"
    SUB_STATE="unknown"
    MAIN_PID=""
    STARTED_AT=""
fi

# Process clues (cross-platform)
if [ "$OS_TYPE" = "darwin" ]; then
    # macOS ps format
    PROCESS_MATCH=$(ps -eo pid,lstart,command 2>/dev/null | grep -E "kwdb|kaiwudb" | grep -v grep | head -n 1 || echo "")
else
    # Linux ps format
    PROCESS_MATCH=$(ps -eo pid,lstart,cmd 2>/dev/null | grep -E "kwdb|kaiwudb" | grep -v grep | head -n 1 || echo "")
fi

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
