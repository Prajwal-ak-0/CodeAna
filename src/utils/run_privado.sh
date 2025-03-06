#!/bin/bash
# Navigate to the privado-cli directory
cd "$1"

# Run privado scan on the target directory
./privado scan "$2"

# Wait for the scan to complete
echo "Waiting for privado scan to complete..."
sleep 5

# Check if .privado directory exists in the target directory
if [ -d "$2/.privado" ]; then
    # Copy privado.json to the current directory
    cp "$2/.privado/privado.json" ./privado.json
    echo "Copied privado.json to current directory"
else
    echo "Warning: .privado directory not found in $2"
    echo "The scan might still be running or failed to create the .privado directory."
fi
