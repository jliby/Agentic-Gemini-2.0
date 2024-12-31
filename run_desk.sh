#!/bin/bash

echo "Starting desk app loop..."

while true; do
    echo "Running desk app..."
    python live_api_starter_desk.py --mode screen
    echo ""  # Simulates pressing the Enter key
    echo "App stopped, restarting in 2 seconds..."
    sleep 2
done
