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
source "${SCRIPT_DIR}/common_functions.sh"

#-------------------------------------------------------------------------------
# Memory information (bytes)
#-------------------------------------------------------------------------------
get_memory_info() {
    if [ "$OS_TYPE" = "linux" ]; then
        MEM_TOTAL=$(awk '/MemTotal:/ {print $2*1024}' /proc/meminfo 2>/dev/null)
        MEM_AVAILABLE=$(awk '/MemAvailable:/ {print $2*1024}' /proc/meminfo 2>/dev/null)
        MEM_USED=$(awk '/MemTotal:/ {total=$2*1024} /MemAvailable:/ {avail=$2*1024} END {if (total != "" && avail != "") print total-avail}' /proc/meminfo 2>/dev/null)
        SWAP_TOTAL=$(awk '/SwapTotal:/ {print $2*1024}' /proc/meminfo 2>/dev/null)
        SWAP_FREE=$(awk '/SwapFree:/ {print $2*1024}' /proc/meminfo 2>/dev/null)
    elif [ "$OS_TYPE" = "darwin" ]; then
        # macOS: Use sysctl to get memory info
        MEM_TOTAL=$(sysctl -n hw.memsize 2>/dev/null)
        # macOS has no MemAvailable, approximate with inactive + free
        MEM_INACTIVE=$(sysctl -n vm.pageinactive 2>/dev/null)
        MEM_FREE=$(sysctl -n vm.page_free_count 2>/dev/null)
        PAGESIZE=$(sysctl -n vm.pagesize 2>/dev/null)
        if [ -n "$MEM_INACTIVE" ] && [ -n "$MEM_FREE" ] && [ -n "$PAGESIZE" ]; then
            # Multiply inactive and free pages by pagesize
            mem_inactive_bytes=$((MEM_INACTIVE * PAGESIZE))
            mem_free_bytes=$((MEM_FREE * PAGESIZE))
            MEM_AVAILABLE=$((mem_inactive_bytes + mem_free_bytes))
            MEM_USED=$((MEM_TOTAL - MEM_AVAILABLE))
        else
            MEM_AVAILABLE=0
            MEM_USED=0
        fi
        # macOS has no swap info via sysctl, need other methods
        SWAP_TOTAL=$(sysctl -n vm.swapusage 2>/dev/null | awk '{print $3}' | tr ',' '.' | awk '{print $1*1024*1024*1024}')
        SWAP_FREE=$(sysctl -n vm.swapusage 2>/dev/null | awk '{print $6}' | tr ',' '.' | awk '{print $1*1024*1024*1024}')
    else
        MEM_TOTAL="null"
        MEM_AVAILABLE="null"
        MEM_USED="null"
        SWAP_TOTAL="null"
        SWAP_FREE="null"
    fi
}

#-------------------------------------------------------------------------------
# CPU information
#-------------------------------------------------------------------------------
get_cpu_info() {
    if [ "$OS_TYPE" = "linux" ]; then
        CPU_CORES=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo "null")
        LOADAVG_1M=$(awk '{print $1}' /proc/loadavg 2>/dev/null)
    elif [ "$OS_TYPE" = "darwin" ]; then
        CPU_CORES=$(sysctl -n hw.ncpu 2>/dev/null || echo "null")
        # macOS has no /proc/loadavg, use uptime as approximation
        LOADAVG_1M=$(uptime 2>/dev/null | awk -F'load averages?: ' '{print $2}' | awk '{print $1}' | tr ',' '.')
    else
        CPU_CORES="null"
        LOADAVG_1M="null"
    fi
}

#-------------------------------------------------------------------------------
# Disk information (bytes)
#-------------------------------------------------------------------------------
get_disk_info() {
    if [ "$OS_TYPE" = "linux" ]; then
        DISK_INFO=$(df -B1 --output=size,used,avail,pcent,target / 2>/dev/null | tail -n 1)
        DISK_TOTAL=$(echo "$DISK_INFO" | awk '{print $1}')
        DISK_USED=$(echo "$DISK_INFO" | awk '{print $2}')
        DISK_AVAILABLE=$(echo "$DISK_INFO" | awk '{print $3}')
        DISK_USAGE_PCT=$(echo "$DISK_INFO" | awk '{print $4}')
        DISK_MOUNT="/"
    elif [ "$OS_TYPE" = "darwin" ]; then
        # macOS: df output format differs from GNU df
        DISK_INFO=$(df -k / 2>/dev/null | tail -n 1)
        # macOS df -k output: Filesystem 1024-blocks Used Available Capacity Mounted on
        # But actual format may vary, needs handling
        TOTAL_KB=$(echo "$DISK_INFO" | awk '{print $2}')
        USED_KB=$(echo "$DISK_INFO" | awk '{print $3}')
        AVAIL_KB=$(echo "$DISK_INFO" | awk '{print $4}')
        CAPACITY=$(echo "$DISK_INFO" | awk '{print $5}')
        DISK_MOUNT=$(echo "$DISK_INFO" | awk '{print $9}')

        # Convert to bytes
        if [ -n "$TOTAL_KB" ]; then
            DISK_TOTAL=$((TOTAL_KB * 1024))
        else
            DISK_TOTAL="null"
        fi
        if [ -n "$USED_KB" ]; then
            DISK_USED=$((USED_KB * 1024))
        else
            DISK_USED="null"
        fi
        if [ -n "$AVAIL_KB" ]; then
            DISK_AVAILABLE=$((AVAIL_KB * 1024))
        else
            DISK_AVAILABLE="null"
        fi
        # macOS capacity is in percentage format (e.g., "80%")
        DISK_USAGE_PCT="${CAPACITY%\%}"
    else
        DISK_TOTAL="null"
        DISK_USED="null"
        DISK_AVAILABLE="null"
        DISK_USAGE_PCT="null"
        DISK_MOUNT="/"
    fi
}

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
