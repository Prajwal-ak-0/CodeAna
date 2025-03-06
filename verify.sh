#!/bin/bash

echo "==== Verifying Aider Installation ===="
which aider
aider --version

echo "==== Verifying Bearer Installation ===="
which bearer
bearer --version

echo "==== Verifying Privado Installation ===="
echo "1. Checking if privado binary is in PATH:"
which privado || echo "privado not found in PATH"

echo "2. Checking if privado-cli repository exists:"
ls -la /root/privado-cli

echo "3. Checking for privado-patched Docker image:"
docker images | grep privado-patched || echo "privado-patched image not found"

echo "4. Testing privado command:"
cd /root/privado-cli && ./privado --help | head -n 5

echo "==== Verifying Docker Installation ===="
docker --version
docker-compose --version

echo "==== Verifying Go Installation ===="
go version

echo "==== All tools verified ====" 