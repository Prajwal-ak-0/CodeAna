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

## Configuration

The application can be configured using environment variables. You can set these variables in your shell or create a `.env` file in the project root directory.

### Available Configuration Options

| Environment Variable | Description | Default Value |
|----------------------|-------------|---------------|
| `OPENAI_API_KEY` | Your OpenAI API key | (Required) |
| `PROJECT_DIR` | Path to the target project directory that will be analyzed | (Prompted if not set) |
| `PRIVADO_CLI_PATH` | Path to the privado-cli directory (e.g., /home/user/privado-cli) | (Prompted if not set) |
| `RUN_AIDER` | Whether to run Aider scan | `true` |
| `RUN_PRIVADO` | Whether to run Privado scan | `true` |
| `RUN_BEARER` | Whether to run Bearer scan | `true` |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4o-mini` |
| `OPENAI_BATCH_SIZE` | Number of rows to process in each batch | `5` |
| `OPENAI_MAX_RETRIES` | Maximum number of retries for OpenAI API calls | `5` |

### Example .env File

```
# OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here

# Project settings
PROJECT_DIR=/path/to/your/project
PRIVADO_CLI_PATH=/path/to/privado-cli

# Feature toggles (true/false)
RUN_AIDER=true
RUN_PRIVADO=true
RUN_BEARER=true

# OpenAI settings
OPENAI_MODEL=gpt-4o-mini
OPENAI_BATCH_SIZE=5
OPENAI_MAX_RETRIES=5
```

## Project Structure

The project is organized as follows:

- `src/`: Source code directory
  - `utils/`: Utility functions
  - `scanners/`: Scanner modules for Aider, Privado, and Bearer
  - `processors/`: Data processing modules
  - `config.py`: Configuration settings
  - `main.py`: Main entry point
- `files/`: Directory for all intermediate files generated during execution
- `main.py`: Main entry point that imports from src
- `check_env.py`: Script to check environment variables
- `clean_files.py`: Script to clean up the files directory

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

## Important Requirements

### Git Repository
## ⚠️ **WARNING**

- The target repository **MUST** be a Git repository with committed changes. Aider requires a Git repository to function properly.
- The target repository must have a `.gitignore` file with `.aider*`.

### OpenAI API Key
Set the OpenAI API key as an environment variable before running:

## Usage

1. **Enter the target project directory to analyze**
   - This should be the absolute path to your Git repository (e.g., `/home/user/projects/my-repo`)
   - The directory must be a Git repository with committed changes
   - This path will be used for all scans (Aider, Privado, and Bearer)

2. The script will run an Aider scan to map the repository

3. You'll be asked if you want to run a Privado scan for data flow analysis
   - If yes, you'll need to provide the path to the Privado CLI directory
   - This should be the directory containing the `privado` executable (e.g., `/home/user/privado-cli`)

4. You'll be asked if you want to run a Bearer scan for security vulnerabilities

5. All results will be consolidated into `aider_repomap.json`

## Output Files

All output files are stored in the `files/` directory:

- `aider_repomap.txt`: Raw output from the Aider scan
- `aider_repomap.json`: Structured JSON representation of your codebase with all analysis results
- `privado.json`: Raw output from the Privado scan
- `privado_output.csv`: Processed data from the Privado scan
- `bearer_output.txt`: Raw output from the Bearer scan
- `bearer_output.csv`: Processed data from the Bearer scan
- `output.csv`: Final CSV output with all analysis results

You can clean up the files directory by running:
```bash
./clean_files.py
```

## Example Repositories

This repository includes example directories to help you understand the tool's functionality:

### test_repo
This directory contains a sample codebase that can be used as a target for scanning.

### test_repo_output
This directory contains sample output files generated by running the tool on the test_repo:
- `aider_repomap.txt`: Example output from Aider showing the repository structure
- `aider_repomap.json`: Final processed JSON representation of the test_repo repository
- `privado.json`: Sample output from Privado scan showing data flow analysis
- `privado_output.csv`: Processed data sink information
- `bearer_output.txt`: Sample output from Bearer security scan
- `bearer_output.csv`: Processed vulnerability information

## Tasks Explained

### Task 1: Repository Mapping with Aider

This task creates a map of your repository structure using Aider. It:
- Creates a shell script to run Aider
- Executes the script on your target directory
- Generates a text file with repository information

### Task 2: Convert to JSON

This task converts the Aider output to a structured JSON format that:
- Represents your directory structure
- Includes file contents and code structure
- Provides a foundation for adding more analysis data

### Task 3: Data Flow Analysis with Privado

This task analyzes data flows in your code using Privado. It:
- Runs a Privado scan on your target directory
- Processes the results to identify data sinks
- Open AI API Call for labeling the data sinks and code summary
- Updates the JSON with data sink information

### Task 4: Security Scanning with Bearer

This task scans for security vulnerabilities using Bearer. It:
- Runs a Bearer scan on your target directory
- Processes the results to identify vulnerabilities
- Updates the JSON with vulnerability information
