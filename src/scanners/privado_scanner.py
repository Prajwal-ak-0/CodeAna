import os
import sys
import uuid
from src.utils import create_script, run_script, copy_file

def create_privado_script():
    """
    Create a shell script to run Privado.
    
    Returns:
        str: Name of the created script
    """
    script_name = "run_privado.sh"
    script_content = """#!/bin/bash
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
        # Ask user for privado-cli path
        privado_cli_path = input("Enter the path to privado-cli directory (e.g., /path/to/privado-cli): ")
        
        # Validate inputs
        if not os.path.isdir(privado_cli_path):
            print(f"Error: Privado CLI directory not found at '{privado_cli_path}'")
            return None
        
        # Check if privado executable exists in the directory
        privado_executable = os.path.join(privado_cli_path, "privado")
        if not os.path.exists(privado_executable):
            print(f"Warning: 'privado' executable not found in '{privado_cli_path}'")
            print("Will try to run the script anyway, but it might fail.")
        
        # Get current directory for copying the file back
        current_dir = os.getcwd()
        
        # Handle existing .privado folder
        handle_existing_privado_folder(project_dir)
        
        # Create and run the script
        script_name = create_privado_script()
        print(f"Running privado scan on directory: {project_dir}")
        print("This may take some time. Please wait...")
        
        # Run the privado scan
        run_script(script_name, privado_cli_path, project_dir)
        
        # Check if the output file exists
        output_file = "privado.json"
        if not os.path.exists(output_file):
            print(f"Warning: {output_file} not found after running privado scan.")
            remote_file = os.path.join(project_dir, "privado.json")
            if os.path.exists(remote_file):
                print(f"Copying from {remote_file} to current directory...")
                copy_file(remote_file, output_file)
            else:
                print(f"Error: Could not find privado.json in {project_dir} either.")
                return None
        
        print(f"Successfully created: {output_file}")
        return output_file
    
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