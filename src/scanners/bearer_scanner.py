import os
import sys
from src.utils import create_script, run_script, delete_script, copy_file
from src.config import BEARER_OUTPUT_FILE, FILES_DIR

def create_bearer_script():
    """
    Create a shell script to run Bearer.
    
    Returns:
        str: Name of the created script
    """
    script_name = os.path.join(FILES_DIR, "run_bearer.sh")
    script_content = f"""#!/bin/bash
# Navigate to the target project directory
cd "$1"

# Run bearer scan and save output to bearer_output.txt
bearer scan ./ > bearer_output.txt

# Check if bearer_output.txt was created
if [ -f "bearer_output.txt" ]; then
    # Copy the file to the original directory
    cp bearer_output.txt "$2/bearer_output.txt"
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
        # Create and run the script
        script_name = create_bearer_script()
        print(f"Running bearer scan on directory: {project_dir}")
        print("This may take some time. Please wait...")
        
        # Run the script with files directory as the second argument
        run_script(script_name, project_dir, FILES_DIR)
        
        # Verify bearer_output.txt exists in files directory
        if os.path.exists(BEARER_OUTPUT_FILE):
            print(f"Successfully copied bearer_output.txt to {FILES_DIR}")
            return BEARER_OUTPUT_FILE
        else:
            print(f"Error: bearer_output.txt was not copied to {FILES_DIR}")
            
            # Check if the file exists in the target directory
            bearer_output_path = os.path.join(project_dir, "bearer_output.txt")
            if os.path.exists(bearer_output_path):
                print(f"Found bearer_output.txt in {project_dir}")
                print(f"Copying to {BEARER_OUTPUT_FILE}...")
                
                # Copy the file manually
                copy_file(bearer_output_path, BEARER_OUTPUT_FILE)
                return BEARER_OUTPUT_FILE
            else:
                print(f"Error: bearer_output.txt not found in {project_dir}")
                return None
    except Exception as e:
        print(f"Error running Bearer scan: {e}")
        return None
    finally:
        # Delete the shell script
        delete_script(script_name) 