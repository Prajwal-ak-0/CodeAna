import os
import sys
import json

from src.utils import (
    initialize_git_repository,
    verify_git_status,
    delete_script,
    copy_file
)

from src.scanners import (
    run_aider_scan,
    run_privado_scan,
    run_bearer_scan
)

from src.processors import (
    convert_to_json,
    process_privado_data,
    update_json_with_sink_details,
    process_bearer_data,
    update_json_with_vulnerabilities,
    convert_json_to_csv
)

from src.config import (
    DEFAULT_PROJECT_DIR,
    GITHUB_PROJECT_DIR,
    RUN_AIDER,
    RUN_PRIVADO,
    RUN_BEARER,
    AIDER_OUTPUT_FILE,
    AIDER_JSON_FILE,
    PRIVADO_OUTPUT_FILE,
    BEARER_OUTPUT_FILE,
    FILES_DIR
)

def get_project_directory(is_github_repo=False):
    """
    Get the project directory from the user or configuration.
    PROJECT_DIR refers to the target directory that will be analyzed.
    
    Args:
        is_github_repo (bool): Whether to use the GitHub project directory
        
    Returns:
        str: Absolute path to the project directory
    """
    if is_github_repo:
        # For GitHub repos, use the current working directory as fallback
        project_dir = os.environ.get("GITHUB_PROJECT_DIR") or os.getcwd()
        print(f"Using GitHub project directory: {project_dir}")
    else:
        if DEFAULT_PROJECT_DIR:
            project_dir = DEFAULT_PROJECT_DIR
            print(f"Using target project directory from configuration: {project_dir}")
        else:
            project_dir = input("Enter the project target directory (the directory you want to analyze): ")
    
    if not os.path.isdir(project_dir):
        print(f"Error: Directory '{project_dir}' does not exist.")
        sys.exit(1)
    
    # Check if the directory is a Git repository
    git_dir = os.path.join(project_dir, ".git")
    if not os.path.isdir(git_dir):
        print(f"Warning: Directory '{project_dir}' is not a Git repository.")
        print("Initializing Git repository...")
        
        if not initialize_git_repository(project_dir):
            sys.exit(1)
    else:
        print("Git repository found. Verifying commit status...")
        if not verify_git_status(project_dir):
            sys.exit(1)
    
    return os.path.abspath(project_dir)

def run_aider_task(project_dir):
    """
    Run the Aider task.
    
    Args:
        project_dir (str): Path to the project directory
        
    Returns:
        str: Path to the JSON file or None if an error occurred
    """
    # Run Aider scan
    input_file = run_aider_scan(project_dir)
    
    # Verify the file exists in the files directory
    if not os.path.exists(AIDER_OUTPUT_FILE):
        print(f"Warning: {AIDER_OUTPUT_FILE} not found in files directory.")
        remote_file = os.path.join(project_dir, "aider_repomap.txt")
        if os.path.exists(remote_file):
            print(f"Copying from {remote_file} to {AIDER_OUTPUT_FILE}...")
            copy_file(remote_file, AIDER_OUTPUT_FILE)
            input_file = AIDER_OUTPUT_FILE
            print("File copied successfully.")
        else:
            print(f"Error: Could not find aider_repomap.txt in {project_dir} either.")
            return None
    
    # Convert to JSON
    json_file = convert_to_json(input_file)
    
    # Delete aider script
    delete_script(os.path.join(FILES_DIR, "run_aider.sh"))
    
    return json_file

def run_privado_task(project_dir):
    """
    Run the Privado task.
    
    Args:
        project_dir (str): Path to the project directory
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Run Privado scan
        privado_json = run_privado_scan(project_dir)
        
        # Check if privado.json exists before proceeding
        if not os.path.exists(PRIVADO_OUTPUT_FILE):
            print(f"Error: {PRIVADO_OUTPUT_FILE} not found. Skipping privado processing.")
            return False
        
        # Process Privado data
        process_privado_data()
        
        # Update JSON with sink details
        update_json_with_sink_details()
        
        return True
    except Exception as e:
        print(f"Error during privado processing: {e}")
        print("Skipping privado processing.")
        return False

def run_bearer_task(project_dir):
    """
    Run the Bearer task.
    
    Args:
        project_dir (str): Path to the project directory
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Run Bearer scan
        bearer_output = run_bearer_scan(project_dir)
        
        # Check if bearer_output.txt exists before proceeding
        if not os.path.exists(BEARER_OUTPUT_FILE):
            print(f"Error: {BEARER_OUTPUT_FILE} not found. Skipping bearer processing.")
            return False
        
        # Process Bearer data
        process_bearer_data()
        
        # Update JSON with vulnerabilities
        update_json_with_vulnerabilities()
        
        return True
    except Exception as e:
        print(f"Error during bearer processing: {e}")
        print("Skipping bearer processing.")
        return False

def main(is_github_repo=False):
    """
    Main function that orchestrates the entire process.
    
    Args:
        is_github_repo (bool): Whether to use the GitHub project directory
    """
    try:
        # Ensure files directory exists
        os.makedirs(FILES_DIR, exist_ok=True)
        
        # Check if OpenAI API key is set
        if not os.environ.get("OPENAI_API_KEY"):
            print("Error: OPENAI_API_KEY environment variable not set.")
            print("Please set your OpenAI API key using:")
            print("  export OPENAI_API_KEY=your_api_key_here")
            sys.exit(1)
            
        # Task 1: Get project directory and run aider
        project_dir = get_project_directory(is_github_repo)
        
        if RUN_AIDER:
            print("Running Aider scan...")
            json_file = run_aider_task(project_dir)
            
            if not json_file:
                print("Error: Failed to create JSON file. Exiting.")
                sys.exit(1)
        else:
            print("Skipping Aider scan as per configuration.")
            if not os.path.exists(AIDER_JSON_FILE):
                print(f"Error: {AIDER_JSON_FILE} not found. Cannot proceed without it.")
                sys.exit(1)
        
        # Task 2: Run Privado scan and process data
        if RUN_PRIVADO:
            print("Running Privado scan...")
            run_privado_task(project_dir)
        else:
            print("Skipping Privado scan as per configuration.")
        
        # Task 3: Run Bearer scan and process data
        if RUN_BEARER:
            print("Running Bearer scan...")
            run_bearer_task(project_dir)
        else:
            print("Skipping Bearer scan as per configuration.")
        
        # Task 4: Convert JSON to CSV
        convert_json_to_csv()
        
        print("All requested tasks completed successfully!")
        print(f"All output files are available in the '{FILES_DIR}' directory.")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 