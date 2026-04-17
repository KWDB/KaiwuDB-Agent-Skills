#!/bin/bash
#===============================================================================
# KWDB Service Status - macOS
# macOS (launchctl) implementation
#===============================================================================

get_service_status() {
    local service_name="$1"
    local label="com.kaiwu.${service_name}"

    # Check if service exists in launchctl
    if launchctl list | grep -q "$label" 2>/dev/null; then
        local service_info=$(launchctl print "user/$(id -u)/$label" 2>/dev/null || launchctl print "system/$label" 2>/dev/null)

        if [ -n "$service_info" ]; then
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
            MAIN_PID=$(echo "$service_info" | grep "pid =" | head -1 | awk '{print $NF}')
        else
            ACTIVE_STATE="unknown"
            SUB_STATE="unknown"
        fi
    else
        ACTIVE_STATE="unknown"
        SUB_STATE="unknown"
    fi

    # If PID not obtained, try to get from process list
    if [ -z "$MAIN_PID" ]; then
        MAIN_PID=$(pgrep -f "kwdb|kaiwudb" 2>/dev/null | head -n 1 || echo "")
    fi
}

get_process_clues() {
    PROCESS_MATCH=$(ps -eo pid,lstart,command 2>/dev/null | grep -E "kwdb|kaiwudb" | grep -v grep | head -n 1 || echo "")
}