#!/bin/bash
#===============================================================================
# KWDB Port Listener Check
# Check if KWDB common ports are actually listening at the OS level
# Supports Linux and macOS
#
# Usage: bash check_kwdb_port_listener.sh [PORTS]
#   PORTS: Comma-separated port list, default 26257,8080
#
# Output Format: JSON
#===============================================================================

# Source common function library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/detect_os.sh"

# Dispatch to platform-specific implementation
case "$OS_TYPE" in
    linux)
        source "${SCRIPT_DIR}/check_kwdb_port_listener_linux.sh"
        ;;
    darwin)
        source "${SCRIPT_DIR}/check_kwdb_port_listener_darwin.sh"
        ;;
    *)
        get_listen_info() { echo ""; }
        get_process_by_port() { echo ""; }
        ;;
esac

PORTS="${1:-26257,8080}"
IFS=',' read -ra PORT_ARRAY <<< "$PORTS"

#-------------------------------------------------------------------------------
# Check if port is listening (cross-platform)
#-------------------------------------------------------------------------------
check_port_listening() {
    local port="$1"
    local listen_info="$2"

    if echo "$listen_info" | grep -qE "[:.]$port[^0-9]"; then
        return 0
    else
        return 1
    fi
}

#-------------------------------------------------------------------------------
# Get listen info
#-------------------------------------------------------------------------------
LISTEN_INFO=$(get_listen_info)

#-------------------------------------------------------------------------------
# Main flow - Generate JSON output
#-------------------------------------------------------------------------------
declare -a listeners
first=true
echo "["
for PORT in "${PORT_ARRAY[@]}"; do
    PORT=$(echo "$PORT" | tr -d ' ')

    if check_port_listening "$PORT" "$LISTEN_INFO"; then
        PROCESS_HINT=$(get_process_by_port "$PORT")
        LISTENING="true"
        MATCHED_LINE=$(echo "$LISTEN_INFO" | grep -E "[:.]$PORT[^0-9]" | head -1)
    else
        PROCESS_HINT=""
        LISTENING="false"
        MATCHED_LINE=""
    fi

    if [ "$first" = true ]; then
        first=false
    else
        echo ","
    fi

    MATCHED_LINE_ESCAPED="${MATCHED_LINE//\\/\\\\}"
    MATCHED_LINE_ESCAPED="${MATCHED_LINE_ESCAPED//\"/\\\"}"
    PROCESS_HINT_ESCAPED="${PROCESS_HINT//\\/\\\\}"
    PROCESS_HINT_ESCAPED="${PROCESS_HINT_ESCAPED//\"/\\\"}"

    cat <<EOF
  {
    "port": $PORT,
    "listening": $LISTENING,
    "process_hint": "$PROCESS_HINT_ESCAPED",
    "raw_line": "$MATCHED_LINE_ESCAPED"
  }
EOF
done
echo "]"