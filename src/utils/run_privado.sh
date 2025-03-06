#!/bin/bash
# Navigate to the privado-cli directory
cd "$1"

# Run privado scan on the target directory
./privado scan "$2"

# Wait for the scan to complete
echo "Waiting for privado scan to complete..."
sleep 5

# Navigate to the target project directory
cd "$2"

# Check if .privado directory exists
if [ -d ".privado" ]; then
    # Copy privado.json to the original directory
    cp .privado/privado.json "$3/privado.json"
    echo "Copied privado.json to $3"
else
    echo "Error: .privado directory not found in $2"
    echo "The scan might still be running or failed to create the .privado directory."
    echo "Please check the target directory manually after the scan completes."
    exit 1
fi
