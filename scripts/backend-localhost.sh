#!/usr/bin/env bash
set -e

# Find backend directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$SCRIPT_DIR/../backend"

if [ ! -d "$BACKEND" ]; then
    echo "Backend folder not found at $BACKEND"
    exit 1
fi

# Check pip
if ! command -v pip &>/dev/null; then
    echo "'pip' not found"
    exit 1
fi

# Check python
if ! command -v python &>/dev/null && ! command -v python3 &>/dev/null; then
    echo "'python' not found"
    exit 1
fi
PYTHON=$(command -v python3 || command -v python)

# Check requirements.txt
REQUIREMENTS="$BACKEND/requirements.txt"
if [ ! -f "$REQUIREMENTS" ]; then
    echo "requirements.txt not found at $REQUIREMENTS"
    exit 1
fi

echo "Upgrading pip..."
"$PYTHON" -m pip install --upgrade pip

echo "Installing dependencies..."
pip install -r "$REQUIREMENTS"

# Check main.py
MAIN="$BACKEND/main.py"
if [ ! -f "$MAIN" ]; then
    echo "main.py not found at $MAIN"
    exit 1
fi

echo ""
echo "Hosting backend locally..."
"$PYTHON" "$MAIN" --local
