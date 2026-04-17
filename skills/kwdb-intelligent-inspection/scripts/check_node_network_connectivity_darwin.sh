#!/bin/bash
#===============================================================================
# KWDB Node Network Connectivity - macOS
# macOS implementation of TCP connectivity and ping latency checks
#===============================================================================

check_tcp_connectivity() {
    local host="$1"
    local port="$2"
    local timeout=3

    if command -v nc >/dev/null 2>&1; then
        if nc -z -w "$timeout" "$host" "$port" 2>/dev/null; then
            echo "reachable"
        else
            echo "unreachable"
        fi
    elif command -v curl >/dev/null 2>&1; then
        if curl -s --connect-timeout "$timeout" "telnet://$host:$port" >/dev/null 2>&1; then
            echo "reachable"
        else
            echo "unreachable"
        fi
    else
        echo "unreachable"
    fi
}

check_ping_latency() {
    local host="$1"
    local timeout=1

    ping -c 1 -t "$timeout" "$host" 2>/dev/null | \
        sed -n 's/.*time=\([0-9.]*\).*/\1/p' | head -n 1
}