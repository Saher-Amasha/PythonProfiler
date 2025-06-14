#!/bin/bash

set -e

VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"

# Create venv if doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in ./$VENV_DIR ..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists in ./$VENV_DIR"
fi

# Activate venv
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash or native Bash)
    source "$VENV_DIR/Scripts/activate"
else
    # Unix/Linux/Mac
    source "$VENV_DIR/bin/activate"
fi

# Install requirements
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing requirements from $REQUIREMENTS_FILE ..."
    pip install -r "$REQUIREMENTS_FILE"
else
    echo "ERROR: $REQUIREMENTS_FILE not found."
    exit 1
fi

echo "Environment setup complete."
