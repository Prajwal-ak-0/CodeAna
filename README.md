# Code Analysis and Security Scanning Tool

This repository contains a comprehensive tool for code analysis and security scanning. The tool automates several tasks including repository mapping, security vulnerability detection, and data flow analysis.

## Overview

This tool integrates multiple scanning technologies to provide a complete picture of your codebase:

1. **Repository Mapping** (using Aider): Creates a structured map of your codebase
2. **Data Flow Analysis** (using Privado): Identifies data sinks and potential data leakage points
3. **Security Vulnerability Scanning** (using Bearer): Detects security vulnerabilities in your code

All results are consolidated into a single JSON file (`aider_repomap.json`) that contains the complete analysis.

## Flowchart

```
┌─────────────────────┐
│ Start               │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ Task 1:             │
│ Run Aider Scan      │◄────┐
└──────────┬──────────┘     │
           ▼                │
┌─────────────────────┐     │
│ Task 2:             │     │
│ Convert to JSON     │     │
└──────────┬──────────┘     │
           ▼                │
┌─────────────────────┐     │
│ Run Privado Scan?   │─No──┘
└──────────┬──────────┘     
           │Yes            
           ▼                
┌─────────────────────┐     
│ Task 3:             │     
│ Run Privado Scan    │     
└──────────┬──────────┘     
           ▼                
┌─────────────────────┐     
│ Process Privado     │     
│ Data                │     
└──────────┬──────────┘     
           ▼                
┌─────────────────────┐     
│ Update JSON with    │     
│ Sink Details        │     
└──────────┬──────────┘     
           ▼                
┌─────────────────────┐     
│ Run Bearer Scan?    │─No──┐
└──────────┬──────────┘     │
           │Yes             │
           ▼                │
┌─────────────────────┐     │
│ Task 4:             │     │
│ Run Bearer Scan     │     │
└──────────┬──────────┘     │
           ▼                │
┌─────────────────────┐     │
│ Process Bearer      │     │
│ Data                │     │
└──────────┬──────────┘     │
           ▼                │
┌─────────────────────┐     │
│ Update JSON with    │     │
│ Vulnerabilities     │     │
└──────────┬──────────┘     │
           │                │
           ▼                │
┌─────────────────────┐     │
│ All Tasks Complete  │◄────┘
└─────────────────────┘
```

## Prerequisites

- Privado CLI
- Bearer CLI

## Important Requirements

### Git Repository
⚠️ **WARNING**: The target repository **MUST** be a Git repository with committed changes. Aider requires a Git repository to function properly.

### OpenAI API Key
Set the OpenAI API key as an environment variable before running:

```bash
# For Linux/macOS
export OPENAI_API_KEY=your_api_key_here

# For Windows (Command Prompt)
set OPENAI_API_KEY=your_api_key_here

# For Windows (PowerShell)
$env:OPENAI_API_KEY="your_api_key_here"
```

The tool will use this API key for the Aider scan and Privado data processing.

## Installation

1. Clone this repository:
   ```
   git clone git@github.com:Prajwal-ak-0/CodeAna.git
   cd CodeAna
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the main script:

```
python main.py
```

The script will guide you through the following steps:

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

The tool generates several output files:

- `aider_repomap.txt`: Raw output from the Aider scan
- `aider_repomap.json`: Structured JSON representation of your codebase with all analysis results
- `privado.json`: Raw output from the Privado scan
- `privado_output.csv`: Processed data from the Privado scan
- `bearer_output.txt`: Raw output from the Bearer scan
- `bearer_output.csv`: Processed data from the Bearer scan

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