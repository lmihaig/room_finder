#!/bin/bash

# A script to start the WOKO/WGZimmer scraper inside a new TMUX session.
# This ensures the script continues to run even if you disconnect from the server.

SESSION_NAME="scraper"

# Check if the tmux session already exists
if ! tmux has-session -t $SESSION_NAME 2>/dev/null; then
  # If the session does not exist, create it and run the script
  echo "Starting new tmux session: '$SESSION_NAME'"

  # Create a new detached tmux session with the specified name
  tmux new-session -d -s $SESSION_NAME

  # --- New, More Robust Startup Sequence ---
  # This version now also ensures Playwright's browsers are installed.
  STARTUP_COMMAND="cd room_finder && \
    echo '--- Setting up environment ---' && \
    if [ ! -d 'venv' ]; then \
        echo 'Virtual environment not found. Attempting to create...' && \
        python3 -m venv venv; \
    fi && \
    if [ -f 'venv/bin/activate' ]; then \
        echo 'Activating virtual environment and installing dependencies...' && \
        source venv/bin/activate && \
        pip install -r ../requirements.txt && \
        echo '--- Ensuring Playwright browsers are installed ---' && \
        playwright install && \
        echo '--- Setup complete. Running scraper ---' && \
        python3 run.py; \
    else \
        echo '' && \
        echo '[ERROR] Failed to create or find the virtual environment!' && \
        echo 'Please ensure the python3-venv package is installed on your system.' && \
        echo 'Example for Ubuntu/Debian: sudo apt update && sudo apt install python3.8-venv' && \
        echo 'Then, try running this script again.'; \
    fi"

  # Send the entire multi-line command to the new session.
  # The 'C-m' at the end simulates pressing the Enter key.
  tmux send-keys -t $SESSION_NAME "$STARTUP_COMMAND" C-m

  echo ""
  echo "✅ Scraper startup sequence initiated inside tmux session '$SESSION_NAME'."
  echo "The script is now setting up the environment and will start running."

else
  # If the session already exists, notify the user.
  echo "⚠️ Session '$SESSION_NAME' already exists. Scraper is likely already running."
  echo "No new scraper was started."
fi

# Print usage instructions for the user
echo ""
echo "--- How to use ---"
echo "To view the live logs of the scraper, attach to the session with:"
echo "  tmux attach -t $SESSION_NAME"
echo ""
echo "To detach from the session (and keep it running), press: CTRL+B then D"
echo ""
echo "To STOP the scraper permanently, attach to the session and press: CTRL+C"
echo "---"
