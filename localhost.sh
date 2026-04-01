#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env.local"

# Check for .env.local
if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: .env.local not found at $ENV_FILE"
    echo "Download it from https://drive.google.com/file/d/1rV0AyDjZbgwemqVbJXlSNMSvqooPO2tW/view?usp=sharing and place it in the project directory."
    exit 1
fi

# Try tmux first (works in Codespaces and most Linux environments)
if command -v tmux &>/dev/null; then
    SESSION="ppit"

    # Kill existing session if running
    tmux kill-session -t "$SESSION" 2>/dev/null || true

    tmux new-session -d -s "$SESSION" -x 220 -y 50

    # First pane: backend
    tmux rename-window -t "$SESSION:0" "backend"
    tmux send-keys -t "$SESSION:0" "bash '$SCRIPT_DIR/scripts/backend-localhost.sh'" Enter

    # Second pane: frontend (split horizontally)
    tmux split-window -h -t "$SESSION:0"
    tmux send-keys -t "$SESSION:0.1" "bash '$SCRIPT_DIR/scripts/frontend-localhost.sh'" Enter

    echo "Started in tmux session '$SESSION'."
    echo "  Attach with: tmux attach -t $SESSION"
    echo "  Detach with: Ctrl+B then D"
    echo "  Kill with:   tmux kill-session -t $SESSION"

    # If running interactively, attach immediately
    if [ -t 0 ]; then
        tmux attach -t "$SESSION"
    fi

else
    # Fallback: run both in background, log to files
    LOGS="$SCRIPT_DIR/.logs"
    mkdir -p "$LOGS"

    echo "tmux not found — running both processes in background."
    echo "Logs: $LOGS/backend.log and $LOGS/frontend.log"
    echo "Stop with: kill \$(cat $LOGS/backend.pid) \$(cat $LOGS/frontend.pid)"

    bash "$SCRIPT_DIR/scripts/backend-localhost.sh" >"$LOGS/backend.log" 2>&1 &
    echo $! >"$LOGS/backend.pid"

    bash "$SCRIPT_DIR/scripts/frontend-localhost.sh" >"$LOGS/frontend.log" 2>&1 &
    echo $! >"$LOGS/frontend.pid"

    echo ""
    echo "Tailing logs (Ctrl+C to stop tailing — processes keep running):"
    tail -f "$LOGS/backend.log" "$LOGS/frontend.log"
fi
