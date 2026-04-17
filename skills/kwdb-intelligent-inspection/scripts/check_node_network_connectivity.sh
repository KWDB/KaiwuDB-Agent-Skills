#!/bin/bash
#===============================================================================
# KWDB Node Network Connectivity
# Detect TCP reachability and basic latency from current node to target nodes
# Supports Linux and macOS
#
# Usage: bash check_node_network_connectivity.sh TARGET_HOSTS [PORT]
#   TARGET_HOSTS: Comma-separated list of target hosts
#   PORT: Target port, default 26257
#
# Example: bash check_node_network_connectivity.sh "192.168.1.10,192.168.1.11" 26257
#
# Output Format: JSON
#===============================================================================

# Source common function library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common_functions.sh"

TARGET_HOSTS="${1:-}"
PORT="${2:-26257}"

if [ -z "$TARGET_HOSTS" ]; then
    echo '{"error": "Missing required parameter: target_hosts must be provided"}'
    exit 1
fi

IFS=',' read -ra HOSTS <<< "$TARGET_HOSTS"

# TCP connectivity check (cross-platform)
check_tcp_connectivity() {
    local host="$1"
    local port="$2"
    local timeout=3

    if [ "$OS_TYPE" = "linux" ]; then
        # Linux: Use /dev/tcp (bash built-in)
        if timeout "$timeout" bash -lc "</dev/tcp/$host/$port" >/dev/null 2>&1; then
            echo "reachable"
        else
            echo "unreachable"
        fi
    else
        # macOS/Others: Use nc (netcat)
        if command -v nc >/dev/null 2>&1; then
            if nc -z -w "$timeout" "$host" "$port" 2>/dev/null; then
                echo "reachable"
            else
                echo "unreachable"
            fi
        else
            # Fallback: Use curl (if available)
            if command -v curl >/dev/null 2>&1; then
                if curl -s --connect-timeout "$timeout" "telnet://$host:$port" >/dev/null 2>&1; then
                    echo "reachable"
                else
                    echo "unreachable"
                fi
            else
                echo "unreachable"
            fi
        fi
    fi
}

# Ping latency check (cross-platform)
check_ping_latency() {
    local host="$1"
    local timeout=1

    if [ "$OS_TYPE" = "linux" ]; then
        # Linux: ping -W specifies timeout in seconds
        ping -c 1 -W "$timeout" "$host" 2>/dev/null | \
            sed -n 's/.*time=\([0-9.]*\).*/\1/p' | head -n 1
    else
        # macOS: ping -t specifies timeout in seconds
        ping -c 1 -t "$timeout" "$host" 2>/dev/null | \
            sed -n 's/.*time=\([0-9.]*\).*/\1/p' | head -n 1
    fi
}

echo "{"
echo "  \"port\": $PORT,"
echo "  \"targets\": ["

first=true
for HOST in "${HOSTS[@]}"; do
    HOST=$(echo "$HOST" | tr -d ' ')

    CONNECTIVITY=$(check_tcp_connectivity "$HOST" "$PORT")
    LATENCY=$(check_ping_latency "$HOST")

    if [ "$first" = true ]; then
        first=false
    else
        echo ","
    fi

    REACHABLE="false"
    if [ "$CONNECTIVITY" = "reachable" ]; then
        REACHABLE="true"
    fi

    if [ -n "$LATENCY" ]; then
        echo "    {\"host\": \"$HOST\", \"reachable\": $REACHABLE, \"latency_ms\": $LATENCY}"
    else
        echo "    {\"host\": \"$HOST\", \"reachable\": $REACHABLE, \"latency_ms\": null}"
    fi
done

echo ""
echo "  ]"
echo "}"
