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
source "${SCRIPT_DIR}/detect_os.sh"

# Dispatch to platform-specific implementation
case "$OS_TYPE" in
    linux)
        source "${SCRIPT_DIR}/check_node_network_connectivity_linux.sh"
        ;;
    darwin)
        source "${SCRIPT_DIR}/check_node_network_connectivity_darwin.sh"
        ;;
    *)
        check_tcp_connectivity() { echo "unreachable"; }
        check_ping_latency() { echo ""; }
        ;;
esac

TARGET_HOSTS="${1:-}"
PORT="${2:-26257}"

if [ -z "$TARGET_HOSTS" ]; then
    echo '{"error": "Missing required parameter: target_hosts must be provided"}'
    exit 1
fi

IFS=',' read -ra HOSTS <<< "$TARGET_HOSTS"

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