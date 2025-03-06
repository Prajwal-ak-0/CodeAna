#!/bin/bash

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Warning: OPENAI_API_KEY environment variable is not set."
    echo "Aider will not work properly without an API key."
    echo "You can set it later using: export OPENAI_API_KEY=your_api_key_here"
fi

# Build the privado-patched image if it doesn't exist
if ! docker images | grep -q "privado-patched"; then
    echo "Building privado-patched Docker image..."
    cd /root && docker build -t privado-patched:latest -f Dockerfile.patched .
    if [ $? -eq 0 ]; then
        echo "privado-patched:latest image built successfully."
    else
        echo "Error: Failed to build privado-patched image. Privado may not work correctly."
    fi
fi

# Verify all tools are installed
echo "Verifying tool installations..."
/root/verify.sh

echo "==== Environment Setup Complete ===="
echo "Aider, Bearer and Privado are now available in this container."
echo "You can start using them for your code analysis and security scanning tasks."
echo ""
echo "To use Privado, navigate to the privado-cli directory and run the privado binary:"
echo "  cd /root/privado-cli"
echo "  ./privado scan /path/to/your/code"
echo ""
echo "Or simply use the privado command from anywhere:"
echo "  privado scan /path/to/your/code"

# Execute the provided command or start a bash shell
if [ $# -eq 0 ]; then
    exec /bin/bash
else
    exec "$@"
fi 