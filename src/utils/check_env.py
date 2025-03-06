#!/usr/bin/env python3
"""
Script to check if the environment variables are being loaded correctly.
"""

import os
import sys
import dotenv

def check_env():
    """
    Check if the environment variables are being loaded correctly.
    """
    # Load environment variables from .env file if it exists
    dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(dotenv_path):
        print(f"Loading environment variables from {dotenv_path}")
        dotenv.load_dotenv(dotenv_path)
    else:
        print("No .env file found. Using environment variables from the system.")
    
    # Check if the environment variables are set
    print("\nEnvironment Variables:")
    print(f"OPENAI_API_KEY: {'Set' if os.environ.get('OPENAI_API_KEY') else 'Not Set'}")
    print(f"PROJECT_DIR: {os.environ.get('PROJECT_DIR', 'Not Set')}")
    print(f"PRIVADO_CLI_PATH: {os.environ.get('PRIVADO_CLI_PATH', 'Not Set')}")
    print(f"RUN_AIDER: {os.environ.get('RUN_AIDER', 'Not Set')}")
    print(f"RUN_PRIVADO: {os.environ.get('RUN_PRIVADO', 'Not Set')}")
    print(f"RUN_BEARER: {os.environ.get('RUN_BEARER', 'Not Set')}")
    print(f"OPENAI_MODEL: {os.environ.get('OPENAI_MODEL', 'Not Set')}")
    print(f"OPENAI_BATCH_SIZE: {os.environ.get('OPENAI_BATCH_SIZE', 'Not Set')}")
    print(f"OPENAI_MAX_RETRIES: {os.environ.get('OPENAI_MAX_RETRIES', 'Not Set')}")
    
    # Check if the directories exist
    project_dir = os.environ.get('PROJECT_DIR', '')
    if project_dir:
        print(f"\nProject Directory ({project_dir}): {'Exists' if os.path.isdir(project_dir) else 'Does Not Exist'}")
    
    privado_cli_path = os.environ.get('PRIVADO_CLI_PATH', '')
    if privado_cli_path:
        print(f"Privado CLI Path ({privado_cli_path}): {'Exists' if os.path.isdir(privado_cli_path) else 'Does Not Exist'}")
        privado_executable = os.path.join(privado_cli_path, "privado")
        print(f"Privado Executable: {'Exists' if os.path.exists(privado_executable) else 'Does Not Exist'}")
    
    # Check files directory
    files_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')
    print(f"\nFiles Directory ({files_dir}): {'Exists' if os.path.isdir(files_dir) else 'Does Not Exist'}")
    if not os.path.isdir(files_dir):
        print("Creating files directory...")
        os.makedirs(files_dir, exist_ok=True)
        print(f"Files directory created at: {files_dir}")
