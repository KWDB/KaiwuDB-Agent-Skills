#!/bin/bash
#===============================================================================
# KWDB Restart Events Counter - macOS
# macOS implementation of restart event counting
#===============================================================================

get_restart_count() {
    local since="$1"
    local count=0

    # Check if any kwdb-related processes are running
    local kwdb_pid=$(pgrep -f "kwdb|kaiwudb" 2>/dev/null | head -n 1)

    if [ -z "$kwdb_pid" ]; then
        # Process not running
        count=0
    else
        # Process is running - try launchctl for restart count
        # Only works if KWDB was installed as a launchd service
        local found=0
        for label in "com.kaiwu.kwdb" "com.kaiwu.kaiwudb"; do
            if launchctl list | grep -q "$label" 2>/dev/null; then
                local restarts=$(launchctl print "user/$(id -u)/$label" 2>/dev/null | \
                                grep -i "last exit status" | awk '{print $NF}')
                if [ -n "$restarts" ] && [[ "$restarts" =~ ^[0-9]+$ ]]; then
                    count="$restarts"
                    found=1
                    break
                fi
            fi
        done

        # If not managed by launchd, can't determine restart count
        # Return 1 to indicate process is running (started at least once)
        if [ "$found" -eq 0 ]; then
            count=1
        fi
    fi

    echo "$count"
}