import os
import sys
import json

from src.utils import (
    initialize_git_repository,
    verify_git_status,
    delete_script
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

def get_project_directory():
    """
    Get the project directory from the user and ensure it's a Git repository.
    
    Returns:
        str: Absolute path to the project directory
    """
    project_dir = input("Enter the project target directory: ")
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
    
    # Verify the file exists in the current directory
    if not os.path.exists("aider_repomap.txt"):
        print("Warning: aider_repomap.txt not found in current directory.")
        remote_file = os.path.join(project_dir, "aider_repomap.txt")
        if os.path.exists(remote_file):
            print(f"Copying from {remote_file} to current directory...")
            with open(remote_file, 'r', encoding='utf-8') as src:
                with open("aider_repomap.txt", 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            input_file = "aider_repomap.txt"
            print("File copied successfully.")
        else:
            print(f"Error: Could not find aider_repomap.txt in {project_dir} either.")
            return None
    
    # Convert to JSON
    json_file = convert_to_json(input_file)
    
    # Delete aider script
    delete_script("run_aider.sh")
    
    return json_file

def run_privado_task(project_dir):
    """
    Run the Privado task.
    
    Args:
        project_dir (str): Path to the project directory
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Ask if user wants to continue with privado scan
    continue_privado = input("Do you want to continue with the privado scan? (y/n): ").lower()
    if continue_privado != 'y':
        print("Skipping privado scan.")
        return False
    
    try:
        # Run Privado scan
        privado_json = run_privado_scan(project_dir)
        
        # Check if privado.json exists before proceeding
        if not os.path.exists("privado.json"):
            print("Error: privado.json not found. Skipping privado processing.")
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
    # Ask if user wants to continue with bearer scan
    continue_bearer = input("Do you want to continue with the bearer scan? (y/n): ").lower()
    if continue_bearer != 'y':
        print("Skipping bearer scan.")
        return False
    
    try:
        # Run Bearer scan
        bearer_output = run_bearer_scan(project_dir)
        
        # Check if bearer_output.txt exists before proceeding
        if not os.path.exists("bearer_output.txt"):
            print("Error: bearer_output.txt not found. Skipping bearer processing.")
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

def main():
    """
    Main function that orchestrates the entire process.
    """
    try:
        # Check if OpenAI API key is set
        if not os.environ.get("OPENAI_API_KEY"):
            print("Error: OPENAI_API_KEY environment variable not set.")
            print("Please set your OpenAI API key using:")
            print("  export OPENAI_API_KEY=your_api_key_here")
            sys.exit(1)
            
        # Task 1: Get project directory and run aider
        project_dir = get_project_directory()
        json_file = run_aider_task(project_dir)
        
        if not json_file:
            print("Error: Failed to create JSON file. Exiting.")
            sys.exit(1)
        
        # Task 2: Run Privado scan and process data
        run_privado_task(project_dir)
        
        # Task 3: Run Bearer scan and process data
        run_bearer_task(project_dir)
        
        # Task 4: Convert JSON to CSV
        convert_json_to_csv()
        
        print("All requested tasks completed successfully!")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 