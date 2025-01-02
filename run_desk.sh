#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Create empty message queue file
echo -n > message_queue.txt

echo "Starting desk app loop..."

# Start the Python script with stdin redirected to /dev/null to prevent tty input
python3 live_api_starter_desk.py --mode screen < /dev/null &
PYTHON_PID=$!

# Start the overlay application
python3 overlay.py &
OVERLAY_PID=$!

# Function to process messages
process_messages() {
    if [ -s message_queue.txt ]; then
        while IFS= read -r message; do
            echo "USER: $message"
        done < message_queue.txt
        # Clear the queue after processing
        echo -n > message_queue.txt
    fi
}

# Cleanup function
cleanup() {
    echo "Cleaning up..."
    kill $PYTHON_PID 2>/dev/null
    kill $OVERLAY_PID 2>/dev/null
    deactivate  # Deactivate virtual environment
    exit 0
}

# Set up trap for cleanup
trap cleanup SIGINT SIGTERM

# Main loop
while true; do
    # Process any pending messages
    process_messages
    
    # Check if Python script is still running
    if ! kill -0 $PYTHON_PID 2>/dev/null; then
        echo "Python script stopped, restarting..."
        python3 live_api_starter_desk.py --mode screen < /dev/null &
        PYTHON_PID=$!
    fi
    
    # Check if overlay is still running
    if ! kill -0 $OVERLAY_PID 2>/dev/null; then
        echo "Overlay stopped, restarting..."
        python3 overlay.py &
        OVERLAY_PID=$!
    fi
    
    # Small delay to prevent excessive CPU usage
    sleep 0.5
done
