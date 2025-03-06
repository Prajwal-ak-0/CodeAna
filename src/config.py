"""
Configuration file for the application.
This file contains all the configuration settings for the application.

Environment Variables:
- OPENAI_API_KEY: Your OpenAI API key
- PROJECT_DIR: Path to the target project directory that will be analyzed
- PRIVADO_CLI_PATH: Path to the privado-cli directory (e.g., /home/user/privado-cli)
- RUN_AIDER: Set to "false" to skip Aider scan
- RUN_PRIVADO: Set to "false" to skip Privado scan
- RUN_BEARER: Set to "false" to skip Bearer scan
- OPENAI_MODEL: OpenAI model to use
- OPENAI_BATCH_SIZE: Number of rows to process in each batch
- OPENAI_MAX_RETRIES: Maximum number of retries for OpenAI API calls
"""

import os
import sys
import dotenv

# Load environment variables from .env file if it exists
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(dotenv_path):
    print(f"Loading environment variables from {dotenv_path}")
    dotenv.load_dotenv(dotenv_path)
else:
    print("No .env file found. Using environment variables from the system.")

# Helper function to parse boolean environment variables
def parse_bool_env(env_var, default=True):
    """
    Parse a boolean environment variable.
    
    Args:
        env_var (str): Environment variable name
        default (bool, optional): Default value. Defaults to True.
        
    Returns:
        bool: Parsed boolean value
    """
    value = os.environ.get(env_var, str(default)).lower()
    return value not in ('false', '0', 'no', 'n', 'f')

# Files directory for all intermediate files
FILES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'files')
# Create the files directory if it doesn't exist
os.makedirs(FILES_DIR, exist_ok=True)

# General settings
# PROJECT_DIR is the target directory that will be analyzed
DEFAULT_PROJECT_DIR = os.environ.get("PROJECT_DIR", "")
if DEFAULT_PROJECT_DIR:
    print(f"Using project directory from environment: {DEFAULT_PROJECT_DIR}")
    if not os.path.isdir(DEFAULT_PROJECT_DIR):
        print(f"Warning: Project directory '{DEFAULT_PROJECT_DIR}' does not exist.")

# Aider settings
RUN_AIDER = parse_bool_env("RUN_AIDER", True)
AIDER_MAP_TOKENS = int(os.environ.get("AIDER_MAP_TOKENS", "8000"))
AIDER_OUTPUT_FILE = os.path.join(FILES_DIR, "aider_repomap.txt")
AIDER_JSON_FILE = os.path.join(FILES_DIR, "aider_repomap.json")

# Privado settings
RUN_PRIVADO = parse_bool_env("RUN_PRIVADO", True)
PRIVADO_OUTPUT_FILE = os.path.join(FILES_DIR, "privado.json")
PRIVADO_CSV_FILE = os.path.join(FILES_DIR, "privado_output.csv")
# PRIVADO_CLI_PATH is the directory containing the privado executable
PRIVADO_CLI_PATH = os.environ.get("PRIVADO_CLI_PATH", "")
if PRIVADO_CLI_PATH:
    print(f"Using Privado CLI path from environment: {PRIVADO_CLI_PATH}")
    if not os.path.isdir(PRIVADO_CLI_PATH):
        print(f"Warning: Privado CLI directory '{PRIVADO_CLI_PATH}' does not exist.")

# Bearer settings
RUN_BEARER = parse_bool_env("RUN_BEARER", True)
BEARER_OUTPUT_FILE = os.path.join(FILES_DIR, "bearer_output.txt")
BEARER_CSV_FILE = os.path.join(FILES_DIR, "bearer_output.csv")

# OpenAI settings
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_BATCH_SIZE = int(os.environ.get("OPENAI_BATCH_SIZE", "5"))
OPENAI_MAX_RETRIES = int(os.environ.get("OPENAI_MAX_RETRIES", "5"))

# Output settings
FINAL_CSV_FILE = os.path.join(FILES_DIR, "output.csv")

# File paths
def get_absolute_path(file_path):
    """
    Get the absolute path of a file.
    
    Args:
        file_path (str): Relative file path
        
    Returns:
        str: Absolute file path
    """
    return os.path.join(os.getcwd(), file_path) 