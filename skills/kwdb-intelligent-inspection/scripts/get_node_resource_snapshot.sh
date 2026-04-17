#!/bin/bash
#===============================================================================
# KWDB Node Resource Snapshot
# Get host-level CPU, memory, Swap, and disk metrics
# Supports Linux and macOS
#
# Usage: bash get_node_resource_snapshot.sh
#
# Output Format: JSON
#
# Dependencies:
#   Linux: /proc/meminfo, df (GNU), nproc
#   macOS: sysctl, df (BSD), system_profiler
#===============================================================================

# Source common function library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/detect_os.sh"

# Dispatch to platform-specific implementation
case "$OS_TYPE" in
    linux)
        source "${SCRIPT_DIR}/get_node_resource_snapshot_linux.sh"
        ;;
    darwin)
        source "${SCRIPT_DIR}/get_node_resource_snapshot_darwin.sh"
        ;;
    *)
        # Unknown OS - provide null values
        get_memory_info() {
            MEM_TOTAL="null"; MEM_AVAILABLE="null"; MEM_USED="null"; SWAP_TOTAL="null"; SWAP_FREE="null"
        }
        get_cpu_info() {
            CPU_CORES="null"; LOADAVG_1M="null"
        }
        get_disk_info() {
            DISK_TOTAL="null"; DISK_USED="null"; DISK_AVAILABLE="null"; DISK_USAGE_PCT="null"; DISK_MOUNT="/"
        }
        ;;
esac

#-------------------------------------------------------------------------------
# Main flow
#-------------------------------------------------------------------------------
get_memory_info
get_cpu_info
get_disk_info

# Calculate memory usage percentage
if [ -n "$MEM_TOTAL" ] && [ "$MEM_TOTAL" != "null" ] && [ "$MEM_TOTAL" -gt 0 ]; then
    if [ -n "$MEM_AVAILABLE" ] && [ "$MEM_AVAILABLE" != "null" ] && [ "$MEM_AVAILABLE" -gt 0 ]; then
        EFFECTIVE_MEM_USED=$((MEM_TOTAL - MEM_AVAILABLE))
    else
        EFFECTIVE_MEM_USED="${MEM_USED:-0}"
    fi
    MEMORY_USAGE_PCT=$(awk "BEGIN {printf \"%.2f\", ($EFFECTIVE_MEM_USED / $MEM_TOTAL) * 100}")
else
    MEMORY_USAGE_PCT="null"
fi

# Calculate Swap usage percentage
if [ -n "$SWAP_TOTAL" ] && [ "$SWAP_TOTAL" != "null" ] && [ "$SWAP_TOTAL" -gt 0 ]; then
    SWAP_USED=$((SWAP_TOTAL - SWAP_FREE))
    SWAP_USAGE_PCT=$(awk "BEGIN {printf \"%.2f\", ($SWAP_USED / $SWAP_TOTAL) * 100}")
else
    SWAP_USAGE_PCT="null"
fi

# Output JSON
cat <<EOF
{
  "os": "$OS_TYPE",
  "memory": {
    "total_bytes": ${MEM_TOTAL:-null},
    "available_bytes": ${MEM_AVAILABLE:-null},
    "used_bytes": ${EFFECTIVE_MEM_USED:-null},
    "usage_pct": ${MEMORY_USAGE_PCT}
  },
  "swap": {
    "total_bytes": ${SWAP_TOTAL:-null},
    "free_bytes": ${SWAP_FREE:-null},
    "usage_pct": ${SWAP_USAGE_PCT}
  },
  "disk": {
    "mount": "${DISK_MOUNT:-/}",
    "total_bytes": ${DISK_TOTAL:-null},
    "used_bytes": ${DISK_USED:-null},
    "available_bytes": ${DISK_AVAILABLE:-null},
    "usage_pct": ${DISK_USAGE_PCT:-null}
  },
  "cpu": {
    "cores": ${CPU_CORES:-null},
    "loadavg_1m": ${LOADAVG_1M:-null}
  }
}
EOF