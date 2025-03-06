#!/usr/bin/env python3
"""
Script to process GitHub repositories.
This script clones a GitHub repository and runs the analysis pipeline on it.
"""

import os
import sys
import subprocess
import shutil
import re
from urllib.parse import urlparse

# Import the main function from the main module
from src.main import main as run_main_pipeline
from src.config import FILES_DIR

# Directory to store GitHub repositories
GITHUB_REPOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'github_repos')

def validate_github_url(url):
    """
    Validate that the URL is a GitHub repository URL.
    
    Args:
        url (str): GitHub repository URL
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Check if the URL is a GitHub URL
    parsed_url = urlparse(url)
    if parsed_url.netloc != 'github.com':
        print(f"Error: Not a GitHub URL: {url}")
        return False
    
    # Check if the URL has a path (username/repo)
    path_parts = parsed_url.path.strip('/').split('/')
    if len(path_parts) < 2:
        print(f"Error: Invalid GitHub repository URL: {url}")
        return False
    
    return True

def get_repo_name_from_url(url):
    """
    Extract the repository name from a GitHub URL.
    
    Args:
        url (str): GitHub repository URL
        
    Returns:
        str: Repository name
    """
    # Parse the URL
    parsed_url = urlparse(url)
    
    # Get the path parts
    path_parts = parsed_url.path.strip('/').split('/')
    
    # The repository name is the second part of the path
    repo_name = path_parts[1]
    
    # Remove .git extension if present
    if repo_name.endswith('.git'):
        repo_name = repo_name[:-4]
    
    return repo_name

def clone_github_repo(url):
    """
    Clone a GitHub repository.
    
    Args:
        url (str): GitHub repository URL
        
    Returns:
        str: Path to the cloned repository or None if an error occurred
    """
    # Create the GitHub repositories directory if it doesn't exist
    os.makedirs(GITHUB_REPOS_DIR, exist_ok=True)
    
    # Get the repository name from the URL
    repo_name = get_repo_name_from_url(url)
    
    # Create a directory for the repository
    repo_dir = os.path.join(GITHUB_REPOS_DIR, repo_name)
    
    # Check if the repository directory already exists
    if os.path.exists(repo_dir):
        print(f"Repository directory already exists: {repo_dir}")
        confirm = input("Do you want to delete it and clone again? (y/n): ").lower()
        if confirm == 'y':
            print(f"Deleting existing repository directory: {repo_dir}")
            shutil.rmtree(repo_dir)
        else:
            print("Using existing repository directory.")
            return repo_dir
    
    # Clone the repository
    try:
        print(f"Cloning repository from {url} to {repo_dir}...")
        subprocess.run(['git', 'clone', url, repo_dir], check=True)
        print(f"Repository cloned successfully to {repo_dir}")
        return repo_dir
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def setup_github_repo_files_dir(repo_dir):
    """
    Set up the files directory inside the GitHub repository.
    
    Args:
        repo_dir (str): Path to the cloned repository
        
    Returns:
        str: Path to the files directory
    """
    # Create the files directory inside the repository
    files_dir = os.path.join(repo_dir, 'files')
    os.makedirs(files_dir, exist_ok=True)
    print(f"Created files directory: {files_dir}")
    return files_dir

def main():
    """
    Main function to process a GitHub repository.
    """
    try:
        # Get the GitHub repository URL from the user
        github_url = input("Enter the GitHub repository URL: ")
        
        # Validate the URL
        if not validate_github_url(github_url):
            print("Please provide a valid GitHub repository URL.")
            sys.exit(1)
        
        # Clone the repository
        repo_dir = clone_github_repo(github_url)
        if not repo_dir:
            print("Failed to clone the repository.")
            sys.exit(1)
        
        # Set up the files directory inside the repository
        files_dir = setup_github_repo_files_dir(repo_dir)
        
        # Set the GITHUB_PROJECT_DIR environment variable
        os.environ['GITHUB_PROJECT_DIR'] = repo_dir
        print(f"Set GITHUB_PROJECT_DIR environment variable to: {repo_dir}")
        
        # Set the FILES_DIR environment variable to the files directory inside the repository
        os.environ['FILES_DIR'] = files_dir
        print(f"Set FILES_DIR environment variable to: {files_dir}")
        
        # Run the main pipeline
        print("\nRunning analysis pipeline on the GitHub repository...")
        run_main_pipeline(is_github_repo=True)
        
        print("\nAnalysis completed successfully!")
        print(f"All output files are available in the '{files_dir}' directory.")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 