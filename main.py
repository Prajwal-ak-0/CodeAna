######################## TASK 1 ########################

# GET THE PROJECT TARGET DIRECTORY FROM USER.
import csv
import os
import subprocess
import sys
import json
from repomap_to_json import parse_input_file, build_directory_tree

def get_project_directory():
    project_dir = input("Enter the project target directory: ")
    if not os.path.isdir(project_dir):
        print(f"Error: Directory '{project_dir}' does not exist.")
        sys.exit(1)
    
    # Check if the directory is a Git repository
    git_dir = os.path.join(project_dir, ".git")
    if not os.path.isdir(git_dir):
        print(f"Error: Directory '{project_dir}' is not a Git repository.")
        print("Aider requires a Git repository to function properly.")
        print("Please initialize a Git repository and commit your changes before proceeding.")
        sys.exit(1)
    
    return os.path.abspath(project_dir)

# CREATE A SHELL SCRIPT THAT WILL RUN THE BELOW COMMAND:
def create_shell_script(project_dir):
    # Get OpenAI API key from environment
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set your OpenAI API key using:")
        print("  export OPENAI_API_KEY=your_api_key_here")
        sys.exit(1)
    
    script_content = f"""#!/bin/bash
cd "$1"
# Run aider and save output to the target directory
aider --map-tokens 8000 --4o --api-key openai={openai_api_key} --show-repo-map > aider_repomap.txt
"""
    
    # Write the shell script
    with open("run_aider.sh", "w") as f:
        f.write(script_content)
    
    # Make the shell script executable
    os.chmod("run_aider.sh", 0o755)
    print("Created and made executable: run_aider.sh")

# RUN THE SHELL SCRIPT.
def run_aider_script(project_dir):
    try:
        print(f"Running aider script on directory: {project_dir}")
        subprocess.run(["./run_aider.sh", project_dir], check=True)
        remote_output_file = os.path.join(project_dir, "aider_repomap.txt")
        local_output_file = "aider_repomap.txt"
        
        if os.path.exists(remote_output_file):
            print(f"Successfully created: {remote_output_file}")
            # Copy the file to the current directory
            with open(remote_output_file, 'r', encoding='utf-8') as src:
                with open(local_output_file, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            print(f"Copied to current directory: {local_output_file}")
        else:
            print("Error: aider_repomap.txt was not created.")
            sys.exit(1)
        return local_output_file
    except subprocess.CalledProcessError as e:
        print(f"Error running shell script: {e}")
        sys.exit(1)

######################## TASK 2 ########################

# CONVERT THE aider_repomap.txt FILE TO A JSON FILE.
def convert_to_json(input_file):
    output_file = "aider_repomap.json"
    try:
        # Call the functions from repomap_to_json.py
        files = parse_input_file(input_file)
        tree = build_directory_tree(files)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(tree, f, indent=4, ensure_ascii=False)
        
        print(f"Successfully created: {output_file}")
        return output_file
    except Exception as e:
        print(f"Error converting to JSON: {e}")
        sys.exit(1)

######################## TASK 3 ########################

# DELETE THE run_aider.sh SHELL SCRIPT OF THE TASK 1. I FORGOT TO DO THIS.
def delete_aider_script():
    try:
        if os.path.exists("run_aider.sh"):
            os.remove("run_aider.sh")
            print("Deleted run_aider.sh")
        else:
            print("run_aider.sh not found, nothing to delete")
    except Exception as e:
        print(f"Error deleting run_aider.sh: {e}")

# NOW CREATE A ANOTHER SHELL SCRIPT THAT WILL EXECUTE THE BELOW COMMAND:
def create_privado_script():
    script_content = """#!/bin/bash
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
    cp .privado/privado.json "$3"
    echo "Copied privado.json to $3"
else
    echo "Error: .privado directory not found in $2"
    echo "The scan might still be running or failed to create the .privado directory."
    echo "Please check the target directory manually after the scan completes."
    exit 1
fi
"""
    
    # Write the shell script
    with open("run_privado.sh", "w") as f:
        f.write(script_content)
    
    # Make the shell script executable
    os.chmod("run_privado.sh", 0o755)
    print("Created and made executable: run_privado.sh")

def run_privado_script(project_dir):
    try:
        # Ask user for privado-cli path only (not target directory)
        privado_cli_path = input("Enter the path to privado-cli directory (e.g., /path/to/privado-cli): ")
        
        # Validate inputs
        if not os.path.isdir(privado_cli_path):
            print(f"Error: Privado CLI directory not found at '{privado_cli_path}'")
            sys.exit(1)
        
        # Check if privado executable exists in the directory
        privado_executable = os.path.join(privado_cli_path, "privado")
        if not os.path.exists(privado_executable):
            print(f"Warning: 'privado' executable not found in '{privado_cli_path}'")
            print("Will try to run the script anyway, but it might fail.")
        
        # Get current directory for copying the file back
        current_dir = os.getcwd()
        
        print(f"Running privado scan on directory: {project_dir}")
        print("This may take some time. Please wait...")
        
        # Run the script
        subprocess.run(["./run_privado.sh", privado_cli_path, project_dir, current_dir], check=True)
        
        # Verify privado.json exists in current directory
        if os.path.exists("privado.json"):
            print("Successfully copied privado.json to current directory")
            return "privado.json"
        else:
            print("Warning: privado.json was not copied to current directory.")
            print("The scan might still be running. Checking target directory...")
            
            # Check if .privado directory exists in target directory
            privado_dir = os.path.join(project_dir, ".privado")
            privado_json_path = os.path.join(privado_dir, "privado.json")
            
            if os.path.exists(privado_dir):
                print(f"Found .privado directory in {project_dir}")
                
                if os.path.exists(privado_json_path):
                    print(f"Found privado.json in {privado_dir}")
                    print("Copying to current directory...")
                    
                    # Copy the file manually
                    with open(privado_json_path, 'r', encoding='utf-8') as src:
                        with open("privado.json", 'w', encoding='utf-8') as dst:
                            dst.write(src.read())
                    
                    print("Successfully copied privado.json to current directory")
                    return "privado.json"
                else:
                    print(f"Error: privado.json not found in {privado_dir}")
                    print("The scan might still be running or failed to create the file.")
                    print("Please check the target directory manually after the scan completes.")
                    sys.exit(1)
            else:
                print(f"Error: .privado directory not found in {project_dir}")
                print("The scan might have failed or is still running.")
                print("Please check the target directory manually after the scan completes.")
                sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error running privado script: {e}")
        print("The scan might have failed or is still running.")
        print("Please check the target directory manually after the scan completes.")
        sys.exit(1)
    finally:
        # Delete the shell script
        if os.path.exists("run_privado.sh"):
            os.remove("run_privado.sh")
            print("Deleted run_privado.sh")

# Import privado_to_csv.py functions
from privado_to_csv import extract_privado_data, process_data
# Import update_with_sink.py functions
from update_with_sink import update_sink_details

def process_privado_data():
    try:
        # Extract data from privado.json
        rows = extract_privado_data()
        if not rows:
            print("No data extracted from privado.json")
            return
        
        # Process the data and create CSV
        process_data(rows)
        
        if os.path.exists("privado_output.csv"):
            print("Successfully created: privado_output.csv")
        else:
            print("Error: privado_output.csv was not created")
    except Exception as e:
        print(f"Error processing privado data: {e}")
        sys.exit(1)

def update_json_with_sink_details():
    try:
        output_json_file = "aider_repomap.json"  # JSON file generated in Task 2
        csv_file = "privado_output.csv"          # CSV file from privado processing
        
        # Check if both files exist
        if not os.path.exists(output_json_file):
            print(f"Error: {output_json_file} not found")
            sys.exit(1)
        
        if not os.path.exists(csv_file):
            print(f"Error: {csv_file} not found")
            sys.exit(1)
        
        # Load the current JSON tree
        with open(output_json_file, 'r', encoding='utf-8') as f:
            json_tree = json.load(f)
        
        # Update the tree with sink details from the CSV
        updated_tree = update_sink_details(json_tree, csv_file)
        
        # Write the updated tree back to the JSON file
        with open(output_json_file, 'w', encoding='utf-8') as f:
            json.dump(updated_tree, f, indent=4, ensure_ascii=False)
        
        print(f"Successfully updated {output_json_file} with sink details from {csv_file}")
    except Exception as e:
        print(f"Error updating JSON with sink details: {e}")
        sys.exit(1)

######################## TASK 4 ########################

# CREATE A SHELL SCRIPT THAT WILL EXECUTE THE BELOW COMMAND:
def create_bearer_script():
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
    
    # Write the shell script
    with open("run_bearer.sh", "w") as f:
        f.write(script_content)
    
    # Make the shell script executable
    os.chmod("run_bearer.sh", 0o755)
    print("Created and made executable: run_bearer.sh")

def run_bearer_script(project_dir):
    try:
        # No need to ask for target directory again
        # Get current directory for copying the file back
        current_dir = os.getcwd()
        
        print(f"Running bearer scan on directory: {project_dir}")
        print("This may take some time. Please wait...")
        
        # Run the script
        subprocess.run(["./run_bearer.sh", project_dir, current_dir], check=True)
        
        # Verify bearer_output.txt exists in current directory
        if os.path.exists("bearer_output.txt"):
            print("Successfully copied bearer_output.txt to current directory")
            return "bearer_output.txt"
        else:
            print("Error: bearer_output.txt was not copied to current directory")
            
            # Check if the file exists in the target directory
            bearer_output_path = os.path.join(project_dir, "bearer_output.txt")
            if os.path.exists(bearer_output_path):
                print(f"Found bearer_output.txt in {project_dir}")
                print("Copying to current directory...")
                
                # Copy the file manually
                with open(bearer_output_path, 'r', encoding='utf-8') as src:
                    with open("bearer_output.txt", 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                
                print("Successfully copied bearer_output.txt to current directory")
                return "bearer_output.txt"
            else:
                print(f"Error: bearer_output.txt not found in {project_dir}")
                sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error running bearer script: {e}")
        sys.exit(1)
    finally:
        # Delete the shell script
        if os.path.exists("run_bearer.sh"):
            os.remove("run_bearer.sh")
            print("Deleted run_bearer.sh")

# Import bearer_to_csv.py functions
from bearer_to_csv import parse_bearer_report, write_to_csv

def process_bearer_data():
    try:
        input_file = "bearer_output.txt"
        output_file = "bearer_output.csv"
        
        # Check if input file exists
        if not os.path.exists(input_file):
            print(f"Error: {input_file} not found")
            sys.exit(1)
        
        # Parse bearer report and write to CSV
        parsed_data = parse_bearer_report(input_file)
        write_to_csv(parsed_data, output_file)
        
        if os.path.exists(output_file):
            print(f"Successfully created: {output_file}")
        else:
            print(f"Error: {output_file} was not created")
            sys.exit(1)
        
        return output_file
    except Exception as e:
        print(f"Error processing bearer data: {e}")
        sys.exit(1)

# Import update_with_vulnerabilities.py functions
from update_with_vulnerabilities import update_vulnerabilities

def update_json_with_vulnerabilities():
    try:
        output_json_file = "aider_repomap.json"  # JSON file generated in Task 2
        csv_file = "bearer_output.csv"           # CSV file from bearer processing
        
        # Check if both files exist
        if not os.path.exists(output_json_file):
            print(f"Error: {output_json_file} not found")
            sys.exit(1)
        
        if not os.path.exists(csv_file):
            print(f"Error: {csv_file} not found")
            sys.exit(1)
        
        # Load the current JSON tree
        with open(output_json_file, 'r', encoding='utf-8') as f:
            json_tree = json.load(f)
        
        # Update the tree with vulnerabilities from the CSV
        updated_tree = update_vulnerabilities(json_tree, csv_file)
        
        # Write the updated tree back to the JSON file
        with open(output_json_file, 'w', encoding='utf-8') as f:
            json.dump(updated_tree, f, indent=4, ensure_ascii=False)
        
        print(f"Successfully updated {output_json_file} with vulnerabilities from {csv_file}")
    except Exception as e:
        print(f"Error updating JSON with vulnerabilities: {e}")
        sys.exit(1)

from json_to_csv import traverse_node

def convert_json_to_csv():
    json_file = "aider_repomap.json"
    output_file = "output.csv"
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return

    # Recursively traverse data to extract file-level rows
    rows = traverse_node(data, "")
    if not rows:
        print("No file entries were found in the provided JSON.")
        return

    # Write CSV output
    fieldnames = ["COMPLETE FILE PATH", "Code Snippet", "Sinks", "Vulnerabilities"]
    try:
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        print(f"CSV file generated successfully at: {output_file}")
    except Exception as e:
        print(f"Error writing CSV file: {e}")


def main():
    try:
        # Check if OpenAI API key is set
        if not os.environ.get("OPENAI_API_KEY"):
            print("Error: OPENAI_API_KEY environment variable not set.")
            print("Please set your OpenAI API key using:")
            print("  export OPENAI_API_KEY=your_api_key_here")
            sys.exit(1)
            
        # Task 1: Get project directory and run aider
        project_dir = get_project_directory()
        create_shell_script(project_dir)
        input_file = run_aider_script(project_dir)
        
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
                sys.exit(1)
        
        # Task 2: Convert to JSON
        json_file = convert_to_json(input_file)
        
        # Task 3: Delete aider script, run privado, and process data
        delete_aider_script()
        
        # Ask if user wants to continue with privado scan
        continue_privado = 'y'
        if continue_privado == 'y':
            create_privado_script()
            
            try:
                # Pass project_dir to run_privado_script
                privado_json = run_privado_script(project_dir)
                
                # Check if privado.json exists before proceeding
                if os.path.exists("privado.json"):
                    process_privado_data()
                    
                    # Update JSON with sink details
                    update_json_with_sink_details()
                else:
                    print("Error: privado.json not found. Skipping privado processing.")
            except Exception as e:
                print(f"Error during privado processing: {e}")
                print("Skipping privado processing.")
        else:
            print("Skipping privado scan.")
        
        # Task 4: Run bearer scan and process data
        # Ask if user wants to continue with bearer scan
        # continue_bearer = input("Do you want to continue with the bearer scan? (y/n): ").lower()
        continue_bearer = 'y'
        if continue_bearer == 'y':
            create_bearer_script()
            
            try:
                # Pass project_dir to run_bearer_script
                bearer_output = run_bearer_script(project_dir)
                
                # Check if bearer_output.txt exists before proceeding
                if os.path.exists("bearer_output.txt"):
                    process_bearer_data()
                    
                    # Update JSON with vulnerabilities
                    update_json_with_vulnerabilities()
                else:
                    print("Error: bearer_output.txt not found. Skipping bearer processing.")
            except Exception as e:
                print(f"Error during bearer processing: {e}")
                print("Skipping bearer processing.")
        else:
            print("Skipping bearer scan.")
        
        print("All requested tasks completed successfully!")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

    convert_json_to_csv()

if __name__ == "__main__":
    main()