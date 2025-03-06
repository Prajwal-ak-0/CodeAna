# Docker Environment for Code Analysis

This repository contains Docker configuration files to set up an environment with Aider, Bearer, and Privado for code analysis and security scanning.

## Files Included

- `Dockerfile`: Sets up the environment with all necessary tools
- `docker-compose.yml`: Configuration for running the Docker container
- `entrypoint.sh`: Script that runs when the container starts

## Setup Instructions

1. First, set your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

2. Build the Docker image:
   ```bash
   docker-compose build
   ```

3. Run the Docker container:
   ```bash
   docker-compose up -d
   ```

4. Access the container:
   ```bash
   docker exec -it codeana bash
   ```

## Verification

When the container starts, it automatically:
- Builds the privado-patched Docker image if it doesn't exist
- Verifies all tools are installed correctly

You can manually verify tool installations by running:
```bash
/root/verify.sh
```

## Available Tools

Inside the container, you can use:
- `aider`: For repository mapping
- `bearer`: For security vulnerability scanning
- `privado`: For data flow analysis

## Notes

- The container is set up with privileged mode to support Docker-in-Docker functionality, which is required by Privado.
- The `/workspace` directory in the container is mapped to your current directory, allowing you to share files between the container and your host system.

## Troubleshooting

If you encounter any issues with the Docker build or run process:

1. **Docker Compose Version Issues**: If you see errors about unsupported properties in docker-compose.yml, check your Docker Compose version with `docker-compose --version`. This setup requires at least Docker Compose V2.

2. **Aider Installation Issues**: The installation of Aider adds binaries to `/root/.local/bin`, which is added to the PATH in the Dockerfile.

3. **.env File Errors**: Ensure your .env file is properly formatted with only environment variable declarations in the form `KEY=value`. No paths or other content should be included.