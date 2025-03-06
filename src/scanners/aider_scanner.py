import os
import sys
from src.utils import create_script, run_script, copy_file

def create_aider_script(project_dir):
    """
    Create a shell script to run Aider.
    
    Args:
        project_dir (str): Path to the project directory
        
    Returns:
        str: Name of the created script
    """
    # Get OpenAI API key from environment
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set your OpenAI API key using:")
        print("  export OPENAI_API_KEY=your_api_key_here")
        sys.exit(1)
    
    script_name = "run_aider.sh"
    script_content = f"""#!/bin/bash
cd "$1"
# Run aider and save output to the target directory
aider --map-tokens 8000 --4o --api-key openai={openai_api_key} --show-repo-map > aider_repomap.txt
"""
    
    # Create the script
    create_script(script_name, script_content)
    return script_name

def run_aider_scan(project_dir):
    """
    Run Aider scan on the project directory.
    
    Args:
        project_dir (str): Path to the project directory
        
    Returns:
        str: Path to the output file or None if an error occurred
    """
    try:
        script_name = create_aider_script(project_dir)
        print(f"Running aider script on directory: {project_dir}")
        
        # Run the script
        run_script(script_name, project_dir)
        
        # Check if the output file exists in the project directory
        remote_output_file = os.path.join(project_dir, "aider_repomap.txt")
        local_output_file = "aider_repomap.txt"
        
        if os.path.exists(remote_output_file):
            print(f"Successfully created: {remote_output_file}")
            # Copy the file to the current directory
            copy_file(remote_output_file, local_output_file)
            return local_output_file
        else:
            print("Error: aider_repomap.txt was not created.")
            return None
    except Exception as e:
        print(f"Error running Aider scan: {e}")
        return None 