#!/bin/bash
#===============================================================================
# KWDB Node Resource Snapshot - macOS
# macOS implementation of get_memory_info, get_cpu_info, get_disk_info
#===============================================================================

get_memory_info() {
    MEM_TOTAL=$(sysctl -n hw.memsize 2>/dev/null)
    MEM_INACTIVE=$(sysctl -n vm.pageinactive 2>/dev/null)
    MEM_FREE=$(sysctl -n vm.page_free_count 2>/dev/null)
    PAGESIZE=$(sysctl -n vm.pagesize 2>/dev/null)
    if [ -n "$MEM_INACTIVE" ] && [ -n "$MEM_FREE" ] && [ -n "$PAGESIZE" ]; then
        mem_inactive_bytes=$((MEM_INACTIVE * PAGESIZE))
        mem_free_bytes=$((MEM_FREE * PAGESIZE))
        MEM_AVAILABLE=$((mem_inactive_bytes + mem_free_bytes))
        MEM_USED=$((MEM_TOTAL - MEM_AVAILABLE))
    else
        MEM_AVAILABLE=0
        MEM_USED=0
    fi
    SWAP_TOTAL=$(sysctl -n vm.swapusage 2>/dev/null | awk '{print $3}' | tr ',' '.' | awk '{print $1*1024*1024*1024}')
    SWAP_FREE=$(sysctl -n vm.swapusage 2>/dev/null | awk '{print $6}' | tr ',' '.' | awk '{print $1*1024*1024*1024}')
}

get_cpu_info() {
    CPU_CORES=$(sysctl -n hw.ncpu 2>/dev/null || echo "null")
    LOADAVG_1M=$(uptime 2>/dev/null | awk -F'load averages?: ' '{print $2}' | awk '{print $1}' | tr ',' '.')
}

get_disk_info() {
    DISK_INFO=$(df -k / 2>/dev/null | tail -n 1)
    TOTAL_KB=$(echo "$DISK_INFO" | awk '{print $2}')
    USED_KB=$(echo "$DISK_INFO" | awk '{print $3}')
    AVAIL_KB=$(echo "$DISK_INFO" | awk '{print $4}')
    CAPACITY=$(echo "$DISK_INFO" | awk '{print $5}')
    DISK_MOUNT=$(echo "$DISK_INFO" | awk '{print $9}')

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
    DISK_USAGE_PCT="${CAPACITY%\%}"
}