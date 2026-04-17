#!/bin/bash
#===============================================================================
# KWDB Common Functions
# Common function library for all inspection scripts
#
# Usage: source scripts/common_functions.sh
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
