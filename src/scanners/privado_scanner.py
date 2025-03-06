import os
import sys
import uuid
from src.utils import create_script, run_script, copy_file
from src.config import PRIVADO_CLI_PATH, PRIVADO_OUTPUT_FILE, FILES_DIR

# Default Privado CLI path if not specified in config
DEFAULT_PRIVADO_CLI_PATH = "/home/prajwalak/Documents/privado-cli"

def create_privado_script():
    """
    Create a shell script to run Privado.
    
    Returns:
        str: Name of the created script
    """
    script_name = os.path.join(FILES_DIR, "run_privado.sh")
    script_content = f"""#!/bin/bash
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
"""
    
    # Create the script
    create_script(script_name, script_content)
    return script_name

def run_privado_scan(project_dir):
    """
    Run Privado scan on the project directory.
    
    Args:
        project_dir (str): Path to the project directory
        
    Returns:
        str: Path to the output file or None if an error occurred
    """
    try:
        # Get privado-cli path from config or use default
        privado_cli_path = PRIVADO_CLI_PATH
        if not privado_cli_path:
            privado_cli_path = DEFAULT_PRIVADO_CLI_PATH
            print(f"Using default Privado CLI path: {privado_cli_path}")
        else:
            print(f"Using Privado CLI path from configuration: {privado_cli_path}")
        
        # Validate inputs
        if not os.path.isdir(privado_cli_path):
            print(f"Error: Privado CLI directory not found at '{privado_cli_path}'")
            print("Please set the PRIVADO_CLI_PATH environment variable to the correct path.")
            return None
        
        # Check if privado executable exists in the directory
        privado_executable = os.path.join(privado_cli_path, "privado")
        if not os.path.exists(privado_executable):
            print(f"Warning: 'privado' executable not found in '{privado_cli_path}'")
            print("Will try to run the script anyway, but it might fail.")
        
        # Handle existing .privado folder
        handle_existing_privado_folder(project_dir)
        
        # Create and run the script
        script_name = create_privado_script()
        print(f"Running privado scan on directory: {project_dir}")
        print("This may take some time. Please wait...")
        
        # Run the privado scan with files directory as third argument
        run_script(script_name, privado_cli_path, project_dir, FILES_DIR)
        
        # Check if the output file exists in the files directory
        if not os.path.exists(PRIVADO_OUTPUT_FILE):
            print(f"Warning: {PRIVADO_OUTPUT_FILE} not found after running privado scan.")
            
            # Check if .privado directory exists in target directory
            privado_dir = os.path.join(project_dir, ".privado")
            privado_json_path = os.path.join(privado_dir, "privado.json")
            
            if os.path.exists(privado_dir):
                print(f"Found .privado directory in {project_dir}")
                
                if os.path.exists(privado_json_path):
                    print(f"Found privado.json in {privado_dir}")
                    print(f"Copying to {PRIVADO_OUTPUT_FILE}...")
                    
                    # Copy the file manually
                    copy_file(privado_json_path, PRIVADO_OUTPUT_FILE)
                    return PRIVADO_OUTPUT_FILE
                else:
                    print(f"Error: privado.json not found in {privado_dir}")
                    print("The scan might still be running or failed to create the file.")
                    return None
            else:
                print(f"Error: .privado directory not found in {project_dir}")
                print("The scan might have failed or is still running.")
                return None
        
        print(f"Successfully created: {PRIVADO_OUTPUT_FILE}")
        return PRIVADO_OUTPUT_FILE
    
    except Exception as e:
        print(f"Error running Privado scan: {e}")
        return None

def handle_existing_privado_folder(project_dir):
    """
    Handle existing .privado folder in the project directory.
    
    Args:
        project_dir (str): Path to the project directory
    """
    # Check if .privado folder exists in the project directory
    privado_folder = os.path.join(project_dir, ".privado")
    if os.path.exists(privado_folder):
        random_uuid = str(uuid.uuid4())
        new_folder_name = f".privado_{random_uuid}"
        new_folder_path = os.path.join(project_dir, new_folder_name)
        
        print(f"Found existing .privado folder. Renaming to {new_folder_name}")
        os.rename(privado_folder, new_folder_path)
        print(f"Renamed .privado folder to {new_folder_name}") 