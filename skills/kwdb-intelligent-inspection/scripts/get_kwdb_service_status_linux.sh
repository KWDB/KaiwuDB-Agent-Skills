#!/bin/bash
#===============================================================================
# KWDB Service Status - Linux
# Linux (systemd) implementation
#===============================================================================

get_service_status() {
    local service_name="$1"
    ACTIVE_STATE=$(systemctl is-active kaiwudb 2>/dev/null || systemctl is-active "$service_name" 2>/dev/null || echo "unknown")
    SUB_STATE=$(systemctl show -p SubState --value kaiwudb 2>/dev/null || systemctl show -p SubState --value "$service_name" 2>/dev/null || echo "unknown")
    MAIN_PID=$(systemctl show -p MainPID --value kaiwudb 2>/dev/null || systemctl show -p MainPID --value "$service_name" 2>/dev/null || echo "")
    STARTED_AT=$(systemctl show -p ActiveEnterTimestamp --value kaiwudb 2>/dev/null || systemctl show -p ActiveEnterTimestamp --value "$service_name" 2>/dev/null || echo "")
}

get_process_clues() {
    PROCESS_MATCH=$(ps -eo pid,lstart,cmd 2>/dev/null | grep -E "kwdb|kaiwudb" | grep -v grep | head -n 1 || echo "")
}