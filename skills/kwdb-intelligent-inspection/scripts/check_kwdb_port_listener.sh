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
source "${SCRIPT_DIR}/common_functions.sh"

PORTS="${1:-26257,8080}"
IFS=',' read -ra PORT_ARRAY <<< "$PORTS"

#-------------------------------------------------------------------------------
# Linux implementation (ss or netstat)
#-------------------------------------------------------------------------------
get_listen_info_linux() {
    # Prefer ss
    if command -v ss >/dev/null 2>&1; then
        ss -lntp 2>/dev/null || ss -ln 2>/dev/null
    # Fallback to netstat
    elif command -v netstat >/dev/null 2>&1; then
        netstat -lntp 2>/dev/null || netstat -ln 2>/dev/null
    fi
}

#-------------------------------------------------------------------------------
# macOS implementation (netstat or lsof)
#-------------------------------------------------------------------------------
get_listen_info_macos() {
    # macOS prefers netstat (BSD version)
    if command -v netstat >/dev/null 2>&1; then
        netstat -anv 2>/dev/null | grep LISTEN
    fi

    # Or use lsof for more detailed info
    if command -v lsof >/dev/null 2>&1; then
        lsof -i -n -P 2>/dev/null | grep LISTEN
    fi
}

#-------------------------------------------------------------------------------
# Get process by port (cross-platform)
#-------------------------------------------------------------------------------
get_process_by_port() {
    local port="$1"

    if [ "$OS_TYPE" = "linux" ]; then
        # Linux: Extract from ss/netstat output
        if command -v ss >/dev/null 2>&1; then
            ss -lntp 2>/dev/null | grep ":$port " | sed -n 's/.*users:(("\([^"]*\)".*/\1/p' | head -1
        elif command -v netstat >/dev/null 2>&1; then
            netstat -lntp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f2 | head -1
        fi
    elif [ "$OS_TYPE" = "darwin" ]; then
        # macOS: Use lsof
        if command -v lsof >/dev/null 2>&1; then
            lsof -i ":$port" 2>/dev/null | grep LISTEN | awk '{print $1}' | head -1
        fi
    fi
}

#-------------------------------------------------------------------------------
# Check if port is listening (cross-platform)
#-------------------------------------------------------------------------------
check_port_listening() {
    local port="$1"
    local listen_info="$2"

    # Check if output contains this port
    if echo "$listen_info" | grep -qE "[:.]$port[^0-9]"; then
        return 0
    else
        return 1
    fi
}

#-------------------------------------------------------------------------------
# Get listen info
#-------------------------------------------------------------------------------
if [ "$OS_TYPE" = "linux" ]; then
    LISTEN_INFO=$(get_listen_info_linux)
elif [ "$OS_TYPE" = "darwin" ]; then
    LISTEN_INFO=$(get_listen_info_macos)
else
    LISTEN_INFO=""
fi

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
        # Get original matching line
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

    # JSON escaping
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
