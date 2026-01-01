#!/bin/bash
# Homepage Power Management Helper Script
# This script is called with elevated privileges to modify system power settings

set -e

# Validate and sanitize inputs
validate_governor() {
    local gov="$1"
    # Only allow alphanumeric, underscore, and hyphen
    if [[ ! "$gov" =~ ^[a-zA-Z0-9_-]+$ ]]; then
        echo "Error: Invalid governor name" >&2
        exit 1
    fi
}

validate_device() {
    local dev="$1"
    # Only allow alphanumeric (no slashes or special chars)
    if [[ ! "$dev" =~ ^[a-zA-Z0-9]+$ ]]; then
        echo "Error: Invalid device name" >&2
        exit 1
    fi
}

validate_scheduler() {
    local sched="$1"
    # Only allow alphanumeric, underscore, and hyphen
    if [[ ! "$sched" =~ ^[a-zA-Z0-9_-]+$ ]]; then
        echo "Error: Invalid scheduler name" >&2
        exit 1
    fi
}

case "$1" in
    set-governor)
        if [ -z "$2" ]; then
            echo "Usage: $0 set-governor <governor-name>" >&2
            exit 1
        fi
        
        validate_governor "$2"
        GOVERNOR="$2"
        
        # Set governor for all CPUs
        SUCCESS=0
        TOTAL=0
        for cpu in /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor; do
            if [ -f "$cpu" ]; then
                TOTAL=$((TOTAL + 1))
                if echo "$GOVERNOR" > "$cpu" 2>/dev/null; then
                    SUCCESS=$((SUCCESS + 1))
                fi
            fi
        done
        
        if [ $SUCCESS -eq $TOTAL ] && [ $TOTAL -gt 0 ]; then
            echo "Successfully set governor to $GOVERNOR for all $TOTAL CPUs"
            exit 0
        elif [ $SUCCESS -gt 0 ]; then
            echo "Warning: Set governor for $SUCCESS/$TOTAL CPUs" >&2
            exit 1
        else
            echo "Error: Failed to set governor (no CPUs updated)" >&2
            exit 1
        fi
        ;;
        
    set-scheduler)
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "Usage: $0 set-scheduler <device> <scheduler>" >&2
            exit 1
        fi
        
        validate_device "$2"
        validate_scheduler "$3"
        
        DEVICE="$2"
        SCHEDULER="$3"
        SCHEDULER_PATH="/sys/block/$DEVICE/queue/scheduler"
        
        if [ ! -f "$SCHEDULER_PATH" ]; then
            echo "Error: Device $DEVICE not found" >&2
            exit 1
        fi
        
        if echo "$SCHEDULER" > "$SCHEDULER_PATH" 2>/dev/null; then
            echo "Successfully set I/O scheduler to $SCHEDULER for $DEVICE"
            exit 0
        else
            echo "Error: Failed to set I/O scheduler" >&2
            exit 1
        fi
        ;;
        
    *)
        echo "Usage: $0 {set-governor|set-scheduler} <args>" >&2
        echo "  set-governor <governor-name>" >&2
        echo "  set-scheduler <device> <scheduler-name>" >&2
        exit 1
        ;;
esac
