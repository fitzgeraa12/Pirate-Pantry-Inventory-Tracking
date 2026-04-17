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

# Try to find a GUI terminal emulator
launch_terminal() {
    local title="$1"
    local cmd="$2"
    if command -v gnome-terminal &>/dev/null; then
        gnome-terminal --title="$title" -- bash -c "$cmd; read -p 'Press Enter to close...'" &
    elif command -v xfce4-terminal &>/dev/null; then
        xfce4-terminal --title="$title" -e "bash -c \"$cmd; read -p 'Press Enter to close...'\"" &
    elif command -v konsole &>/dev/null; then
        konsole --title "$title" -e bash -c "$cmd; read -p 'Press Enter to close...'" &
    elif command -v xterm &>/dev/null; then
        xterm -title "$title" -e bash -c "$cmd; read -p 'Press Enter to close...'" &
    else
        return 1
    fi
    disown
}

if launch_terminal "Pirate Pantry - Backend" "bash '$SCRIPT_DIR/scripts/backend-localhost.sh'" && \
   launch_terminal "Pirate Pantry - Frontend" "bash '$SCRIPT_DIR/scripts/frontend-localhost.sh'"; then
    echo "Launched backend and frontend in separate terminal windows."
else
    # Fallback: run both in background, log to files
    LOGS="$SCRIPT_DIR/.logs"
    mkdir -p "$LOGS"

    echo "No GUI terminal found — running both processes in background."
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
