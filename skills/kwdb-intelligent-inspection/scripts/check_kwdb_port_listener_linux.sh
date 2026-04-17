#!/bin/bash
#===============================================================================
# KWDB Port Listener Check - Linux
# Linux implementation of port listening info
#===============================================================================

get_listen_info() {
    # Prefer ss
    if command -v ss >/dev/null 2>&1; then
        ss -lntp 2>/dev/null || ss -ln 2>/dev/null
    # Fallback to netstat
    elif command -v netstat >/dev/null 2>&1; then
        netstat -lntp 2>/dev/null || netstat -ln 2>/dev/null
    fi
}

get_process_by_port() {
    local port="$1"
    if command -v ss >/dev/null 2>&1; then
        ss -lntp 2>/dev/null | grep ":$port " | sed -n 's/.*users:(("\([^"]*\)".*/\1/p' | head -1
    elif command -v netstat >/dev/null 2>&1; then
        netstat -lntp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f2 | head -1
    fi
}