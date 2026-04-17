#!/bin/bash
#===============================================================================
# KWDB Port Listener Check - macOS
# macOS implementation of port listening info
#===============================================================================

get_listen_info() {
    # macOS prefers netstat (BSD version)
    if command -v netstat >/dev/null 2>&1; then
        netstat -anv 2>/dev/null | grep LISTEN
    fi
    # Or use lsof for more detailed info
    if command -v lsof >/dev/null 2>&1; then
        lsof -i -n -P 2>/dev/null | grep LISTEN
    fi
}

get_process_by_port() {
    local port="$1"
    if command -v lsof >/dev/null 2>&1; then
        lsof -i ":$port" 2>/dev/null | grep LISTEN | awk '{print $1}' | head -1
    fi
}