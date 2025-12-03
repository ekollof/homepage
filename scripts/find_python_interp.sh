#!/bin/sh
# find_latest_python.sh
# Portable across Linux, FreeBSD, OpenBSD
# Returns the full path to the newest python3.x binary available in standard locations
# Exits with status 1 if none found

set -u  # No unset variables

# Common directories where Python binaries live on all three OS families
SEARCH_PATHS="
    /usr/bin
    /usr/local/bin
    /usr/pkg/bin
    /usr/local/pkg/bin
    /opt/local/bin
"

best_path=""
best_ver="0.0.0"

# Helper: compare two X.Y.Z version strings, return 0 if v1 > v2
version_gt() {
    [ "$1" = "$2" ] && return 1
    printf '%s\n%s\n' "$1" "$2" | sort -t '.' -n -k1,1 -k2,2 -k3,3 | head -n1 | grep -qx "$2"
}

for dir in $SEARCH_PATHS; do
    [ -d "$dir" ] || continue

    # Find all python3.* executables (python3, python3.8, python3.11, python3.12, etc.)
    for bin in "$dir"/python3 "$dir"/python3.*; do
        # Skip if not a regular file or if glob didn't match anything
        [ -f "$bin" ] || continue
        # Skip if executable bit is not set (some systems ship symlinks without +x)
        [ -x "$bin" ] || continue

        # Extract version directly from filename when possible (fast & reliable)
        case "$bin" in
            */python3)
                ver="3.0.0"  # fallback, will be overridden if real version is higher
                ;;
            */python3.*)
                # Extract the X.Y part from filename
                basename=$(basename "$bin")
                ver="${basename#python3.}"
                # Normalize: python3.11 → 3.11.0, python3.9 → 3.9.0
                case "$ver" in
                    *.*.*) ;;                 # already X.Y.Z
                    *.*)   ver="$ver.0" ;;    # X.Y   → X.Y.0
                    *)     ver="$ver.0.0" ;;  # X     → X.0.0
                esac
                ver="3.$ver"
                ;;
            *) continue ;;
        esac

        # If filename gave us nothing useful (e.g. just "python3"), fall back to --version
        if [ "$ver" = "3.0.0" ]; then
            if ! version_output=$( "$bin" --version 2>/dev/null ); then
                continue
            fi
            ver=$(echo "$version_output" | grep '^Python ' | sed 's/^Python //')
        fi

        # Validate we got a sane version
        case "$ver" in
            [0-9].[0-9]*.*) ;;
            [0-9][0-9].[0-9]*.*) ;;
            *) continue ;;
        esac

        # Keep the best one
        if [ -z "$best_ver" ] || version_gt "$ver" "$best_ver"; then
            best_ver="$ver"
            best_path="$bin"
        fi
    done
done

if [ -n "$best_path" ]; then
    printf '%s\n' "$best_path"
    exit 0
else
    # Optional: also check plain "python" as last resort (some minimal systems)
    for bin in /usr/bin/python /usr/local/bin/python; do
        [ -x "$bin" ] || continue
        ver=$( "$bin" --version 2>/dev/null | grep '^Python ' | sed 's/^Python //' )
        case "$ver" in 3.*) printf '%s\n' "$bin"; exit 0; esac
    done
    exit 1
fi
