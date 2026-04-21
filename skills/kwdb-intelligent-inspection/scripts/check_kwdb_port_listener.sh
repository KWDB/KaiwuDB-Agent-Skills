#!/bin/bash
#===============================================================================
# KWDB Port Listener Check
# Check if KWDB common ports are actually listening at the OS level
# Supports Linux and macOS
#
# Usage: bash check_kwdb_port_listener.sh [IP] [PORTS]
#   IP: IP address of the node (default: 127.0.0.1)
#   PORTS: Comma-separated port list (default: 26257,8080)
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

# Parse arguments: IP address and port list
# Usage: bash check_kwdb_port_listener.sh [IP] [PORTS]
#   IP: IP address of the node (default: 127.0.0.1)
#   PORTS: Comma-separated port list (default: 26257,8080)
TARGET_IP="${1:-127.0.0.1}"
PORTS="${2:-26257,8080}"

# Validate IP address format (basic check)
is_valid_ip() {
    local ip="$1"
    if [[ "$ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        return 0
    else
        return 1
    fi
}

# Validate port number: must be numeric and in valid range 1-65535
is_valid_port() {
    local port="$1"
    if [[ "$port" =~ ^[0-9]+$ ]] && [ "$port" -ge 1 ] && [ "$port" -le 65535 ]; then
        return 0
    else
        return 1
    fi
}

# Validate IP first - if invalid, skip port check and error out
if ! is_valid_ip "$TARGET_IP"; then
    echo "[{\"error\": \"Invalid IP address: $TARGET_IP\", \"port\": null, \"listening\": null, \"process_hint\": \"\", \"raw_line\": \"\"}]"
    exit 1
fi

IFS=',' read -ra PORT_ARRAY <<< "$PORTS"

# Filter out invalid entries (e.g., IP addresses passed by mistake as ports)
VALID_PORTS=()
for PORT in "${PORT_ARRAY[@]}"; do
    PORT=$(echo "$PORT" | tr -d ' ')
    if is_valid_port "$PORT"; then
        VALID_PORTS+=("$PORT")
    fi
done

# If no valid ports left, output error
if [ ${#VALID_PORTS[@]} -eq 0 ]; then
    echo "[{\"error\": \"No valid ports specified: $PORTS\", \"port\": null, \"listening\": null, \"process_hint\": \"\", \"raw_line\": \"\"}]"
    exit 1
fi

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
for PORT in "${VALID_PORTS[@]}"; do

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