#!/bin/sh
# Homepage Power Management Helper Script
# This script is called with elevated privileges to modify system power settings
# Compatible with both Linux (bash) and FreeBSD (sh)

set -e

# Detect OS
OS=$(uname -s)

# Validate and sanitize inputs
validate_governor() {
    gov="$1"
    # Only allow alphanumeric, underscore, and hyphen
    case "$gov" in
        *[!a-zA-Z0-9_-]*) 
            echo "Error: Invalid governor name" >&2
            exit 1
            ;;
    esac
}

validate_device() {
    dev="$1"
    # Only allow alphanumeric (no slashes or special chars)
    case "$dev" in
        *[!a-zA-Z0-9]*) 
            echo "Error: Invalid device name" >&2
            exit 1
            ;;
    esac
}

validate_scheduler() {
    sched="$1"
    # Only allow alphanumeric, underscore, and hyphen
    case "$sched" in
        *[!a-zA-Z0-9_-]*) 
            echo "Error: Invalid scheduler name" >&2
            exit 1
            ;;
    esac
}

validate_freq() {
    freq="$1"
    # Only allow numbers
    case "$freq" in
        ''|*[!0-9]*) 
            echo "Error: Invalid frequency value" >&2
            exit 1
            ;;
    esac
}

case "$1" in
    set-governor)
        if [ "$OS" != "Linux" ]; then
            echo "Error: set-governor is only supported on Linux" >&2
            exit 1
        fi
        
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
        if [ "$OS" != "Linux" ]; then
            echo "Error: set-scheduler is only supported on Linux" >&2
            exit 1
        fi
        
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
    
    set-freebsd-freq)
        if [ "$OS" != "FreeBSD" ]; then
            echo "Error: set-freebsd-freq is only supported on FreeBSD" >&2
            exit 1
        fi
        
        if [ -z "$2" ]; then
            echo "Usage: $0 set-freebsd-freq <frequency-in-mhz>" >&2
            exit 1
        fi
        
        validate_freq "$2"
        FREQ="$2"
        
        # Get CPU count
        CPU_COUNT=$(sysctl -n hw.ncpu 2>/dev/null || echo "1")
        
        # Set frequency for all CPUs
        SUCCESS=0
        i=0
        while [ $i -lt "$CPU_COUNT" ]; do
            if sysctl dev.cpu.$i.freq="$FREQ" >/dev/null 2>&1; then
                SUCCESS=$((SUCCESS + 1))
            fi
            i=$((i + 1))
        done
        
        if [ $SUCCESS -eq "$CPU_COUNT" ]; then
            echo "Successfully set CPU frequency to $FREQ MHz for all $CPU_COUNT CPUs"
            exit 0
        elif [ $SUCCESS -gt 0 ]; then
            echo "Warning: Set frequency for $SUCCESS/$CPU_COUNT CPUs" >&2
            exit 1
        else
            echo "Error: Failed to set CPU frequency (no CPUs updated)" >&2
            exit 1
        fi
        ;;
        
    *)
        echo "Usage: $0 {set-governor|set-scheduler|set-freebsd-freq} <args>" >&2
        echo "  set-governor <governor-name>           (Linux only)" >&2
        echo "  set-scheduler <device> <scheduler>     (Linux only)" >&2
        echo "  set-freebsd-freq <frequency-in-mhz>    (FreeBSD only)" >&2
        exit 1
        ;;
esac
