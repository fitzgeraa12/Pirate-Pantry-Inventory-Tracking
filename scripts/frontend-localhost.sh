#!/usr/bin/env bash
set -e

# Find frontend directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND="$SCRIPT_DIR/../frontend"

if [ ! -d "$FRONTEND" ]; then
    echo "Frontend folder not found at $FRONTEND"
    exit 1
fi

cd "$FRONTEND"

echo "Installing dependencies..."
npm install
npm audit fix || true

echo ""
echo "Hosting frontend locally..."
npm run dev
