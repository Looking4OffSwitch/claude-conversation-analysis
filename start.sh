#!/bin/bash

# Start script for Claude Conversation Viewer Flask app
# Usage: ./start.sh

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Claude Conversation Viewer${NC}"
echo "======================================"
echo ""

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment not found.${NC}"
    echo "Running: uv sync"
    uv sync
    echo ""
fi

# Check if Flask is installed
if ! .venv/bin/python -c "import flask" 2>/dev/null; then
    echo -e "${RED}Flask not found in virtual environment.${NC}"
    echo "Running: uv sync"
    uv sync
    echo ""
fi

# Start the Flask server
echo -e "${GREEN}Starting Flask development server...${NC}"
echo ""
echo "Server will be available at:"
echo "  http://127.0.0.1:5000"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

python flask_app/app.py
