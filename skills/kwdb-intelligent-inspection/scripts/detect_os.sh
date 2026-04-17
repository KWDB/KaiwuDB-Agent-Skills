#!/bin/bash
#===============================================================================
# KWDB OS Detection
# Detect operating system type for cross-platform script execution
#
# Usage: source scripts/detect_os.sh
#===============================================================================

# Detect operating system type
# Returns: linux | darwin | unknown
detect_os() {
    case "$(uname -s)" in
        Darwin*) echo "darwin" ;;
        Linux*) echo "linux" ;;
        *) echo "unknown" ;;
    esac
}

OS_TYPE=$(detect_os)