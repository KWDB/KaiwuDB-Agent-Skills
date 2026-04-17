#!/bin/bash
#===============================================================================
# KWDB Restart Events Counter - Linux
# Linux implementation of restart event counting
#===============================================================================

get_restart_count() {
    local since="$1"
    local count=0

    # Linux: Use journalctl
    if command -v journalctl >/dev/null 2>&1; then
        count=$(journalctl --since "$since" -u kaiwudb -u kwdb --no-pager 2>/dev/null | \
                grep -ciE "Starting|Started|Restarting|Stopped" || true)
    fi

    # If journalctl has no data, try systemctl NRestarts
    if [ -z "$count" ] || [ "$count" -eq 0 ]; then
        if command -v systemctl >/dev/null 2>&1; then
            count=$(systemctl show -p NRestarts --value kaiwudb 2>/dev/null || \
                    systemctl show -p NRestarts --value kwdb 2>/dev/null || \
                    echo 0)
        fi
    fi

    echo "$count"
}