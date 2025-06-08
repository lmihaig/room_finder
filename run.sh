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

  # Send the commands to the new session to change directory and run the Python script.
  # The 'C-m' at the end simulates pressing the Enter key.
  # NOTE: It's crucial that the 'room_finder' directory is in the same directory as this script.
  tmux send-keys -t $SESSION_NAME "cd room_finder && python3 run.py" C-m

  echo ""
  echo "✅ Scraper started successfully inside tmux session '$SESSION_NAME'."
  echo "The script is now running in the background."

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
