#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR=$(dirname "$0")

# Set PYTHONPATH to include the project root directory
export PYTHONPATH="$SCRIPT_DIR/..:$PYTHONPATH"

# Array to store the PIDs of the background Python processes
PIDS=()

# Function to run a Python script in the background
run_python_script() {
    python "$1" "$2" &
    PIDS+=($!)
}

# Function to handle Ctrl+C (SIGINT)
cleanup() {
    echo "Stopping Python processes..."
    for PID in "${PIDS[@]}"; do
        kill $PID

        # Wait for the process to terminate for up to 5 seconds
        for i in {1..5}; do
            if ! ps -p $PID > /dev/null; then
                break
            fi
            sleep 1
        done

        # If the process is still running, force kill it
        if ps -p $PID > /dev/null; then
            echo "Force killing Python process with PID $PID..."
            kill -9 $PID
        fi
    done
    echo "All Python processes stopped."
    exit 0
}

# Trap Ctrl+C (SIGINT) and call the cleanup function
trap cleanup SIGINT

# Start the motor control scripts in the background
run_python_script "$SCRIPT_DIR/../src/nodes/drive/esc.py" 0
run_python_script "$SCRIPT_DIR/../src/nodes/drive/esc.py" 1
run_python_script "$SCRIPT_DIR/../src/nodes/drive/esc.py" 2

# Wait for all background processes to finish
for PID in "${PIDS[@]}"; do
    wait $PID
done
