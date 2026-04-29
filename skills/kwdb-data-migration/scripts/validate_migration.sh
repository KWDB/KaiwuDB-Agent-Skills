#!/bin/bash
CONFIG="$1"

if [ ! -f "$CONFIG" ]; then
    echo "ERROR: Config file not found."
    exit 1
fi

echo "Checking migration config..."

grep -q "time_column" "$CONFIG" && echo "OK: time_column exists"
grep -q "start_time" "$CONFIG" && echo "OK: start_time exists"
grep -q "end_time" "$CONFIG" && echo "OK: end_time exists"
grep -q "target_engine" "$CONFIG" && echo "OK: target_engine defined"

echo "Validation complete."
