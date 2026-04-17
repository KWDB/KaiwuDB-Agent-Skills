#!/bin/bash
#===============================================================================
# KWDB Node Network Connectivity - Linux
# Linux implementation of TCP connectivity and ping latency checks
#===============================================================================

check_tcp_connectivity() {
    local host="$1"
    local port="$2"
    local timeout=3

    if timeout "$timeout" bash -lc "</dev/tcp/$host/$port" >/dev/null 2>&1; then
        echo "reachable"
    else
        echo "unreachable"
    fi
}

check_ping_latency() {
    local host="$1"
    local timeout=1

    ping -c 1 -W "$timeout" "$host" 2>/dev/null | \
        sed -n 's/.*time=\([0-9.]*\).*/\1/p' | head -n 1
}