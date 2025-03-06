import os
import sys
from src.utils import create_script, run_script, delete_script, copy_file

def create_bearer_script():
    """
    Create a shell script to run Bearer.
    
    Returns:
        str: Name of the created script
    """
    script_name = "run_bearer.sh"
    script_content = """#!/bin/bash
# Navigate to the target project directory
cd "$1"

# Run bearer scan and save output to bearer_output.txt
bearer scan ./ > bearer_output.txt

# Check if bearer_output.txt was created
if [ -f "bearer_output.txt" ]; then
    # Copy the file to the original directory
    cp bearer_output.txt "$2"
    echo "Copied bearer_output.txt to $2"
else
    echo "Error: bearer_output.txt was not created"
    exit 1
fi
"""
    
    # Create the script
    create_script(script_name, script_content)
    return script_name

def run_bearer_scan(project_dir):
    """
    Run Bearer scan on the project directory.
    
    Args:
        project_dir (str): Path to the project directory
        
    Returns:
        str: Path to the output file or None if an error occurred
    """
    try:
        # Get current directory for copying the file back
        current_dir = os.getcwd()
        
        # Create and run the script
        script_name = create_bearer_script()
        print(f"Running bearer scan on directory: {project_dir}")
        print("This may take some time. Please wait...")
        
        # Run the script
        run_script(script_name, project_dir, current_dir)
        
        # Verify bearer_output.txt exists in current directory
        output_file = "bearer_output.txt"
        if os.path.exists(output_file):
            print(f"Successfully copied {output_file} to current directory")
        else:
            print(f"Error: {output_file} was not copied to current directory")
            
            # Check if the file exists in the target directory
            bearer_output_path = os.path.join(project_dir, output_file)
            if os.path.exists(bearer_output_path):
                print(f"Found {output_file} in {project_dir}")
                print("Copying to current directory...")
                
                # Copy the file manually
                copy_file(bearer_output_path, output_file)
            else:
                print(f"Error: {output_file} not found in {project_dir}")
                return None
        
        return output_file
    except Exception as e:
        print(f"Error running Bearer scan: {e}")
        return None
    finally:
        # Delete the shell script
        delete_script(script_name) 