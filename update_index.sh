#!/bin/bash
#
# Update the project index
# This script activates the virtual environment and runs the indexer
#

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Error: Virtual environment not found at .venv"
    echo "Please create it first with: uv venv && uv pip install -r src/requirements.txt"
    exit 1
fi

# Run the indexer
python src/index_projects.py "$@"
