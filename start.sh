#!/bin/bash
# Brief Bridge Quick Start Script

cd "$(dirname "$0")"

# Check if Python virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "🔄 Activating virtual environment..."
    source venv/bin/activate
fi

# Start Brief Bridge with default settings
echo "🚀 Starting Brief Bridge on port 2266..."
python start.py "$@"