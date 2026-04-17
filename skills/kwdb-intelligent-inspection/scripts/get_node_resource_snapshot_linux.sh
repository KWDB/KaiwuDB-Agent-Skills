#!/bin/bash
#===============================================================================
# KWDB Node Resource Snapshot - Linux
# Linux implementation of get_memory_info, get_cpu_info, get_disk_info
#===============================================================================

get_memory_info() {
    MEM_TOTAL=$(awk '/MemTotal:/ {print $2*1024}' /proc/meminfo 2>/dev/null)
    MEM_AVAILABLE=$(awk '/MemAvailable:/ {print $2*1024}' /proc/meminfo 2>/dev/null)
    MEM_USED=$(awk '/MemTotal:/ {total=$2*1024} /MemAvailable:/ {avail=$2*1024} END {if (total != "" && avail != "") print total-avail}' /proc/meminfo 2>/dev/null)
    SWAP_TOTAL=$(awk '/SwapTotal:/ {print $2*1024}' /proc/meminfo 2>/dev/null)
    SWAP_FREE=$(awk '/SwapFree:/ {print $2*1024}' /proc/meminfo 2>/dev/null)
}

get_cpu_info() {
    CPU_CORES=$(nproc 2>/dev/null || echo "null")
    LOADAVG_1M=$(awk '{print $1}' /proc/loadavg 2>/dev/null)
}

get_disk_info() {
    DISK_INFO=$(df -B1 --output=size,used,avail,pcent,target / 2>/dev/null | tail -n 1)
    DISK_TOTAL=$(echo "$DISK_INFO" | awk '{print $1}')
    DISK_USED=$(echo "$DISK_INFO" | awk '{print $2}')
    DISK_AVAILABLE=$(echo "$DISK_INFO" | awk '{print $3}')
    DISK_USAGE_PCT=$(echo "$DISK_INFO" | awk '{print $4}')
    DISK_MOUNT="/"
}