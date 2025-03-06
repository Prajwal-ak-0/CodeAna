import os
import subprocess
import sys

def initialize_git_repository(project_dir):
    """
    Initialize a Git repository in the specified directory if it doesn't exist.
    
    Args:
        project_dir (str): Path to the project directory
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Change to the project directory
        os.chdir(project_dir)
        
        # Initialize Git repository
        subprocess.run(["git", "init"], check=True)
        print("Git repository initialized successfully.")
        
        # Create or update .gitignore file
        update_gitignore(project_dir)
        
        # Add all files and make initial commit
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-m", "Aider Commit"], check=True)
        print("Initial commit created successfully.")
        
        # Change back to original directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error setting up Git repository: {e}")
        return False

def update_gitignore(project_dir):
    """
    Create or update .gitignore file with .aider* entry.
    
    Args:
        project_dir (str): Path to the project directory
    """
    gitignore_path = os.path.join(project_dir, ".gitignore")
    gitignore_content = ".aider*\n"
    
    # If .gitignore exists, check if .aider* is already in it
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            existing_content = f.read()
        
        if ".aider*" not in existing_content:
            with open(gitignore_path, 'a') as f:
                f.write("\n" + gitignore_content)
            print("Added .aider* to existing .gitignore file.")
    else:
        # Create new .gitignore file
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)
        print("Created .gitignore file with .aider* entry.")

def verify_git_status(project_dir):
    """
    Verify Git repository status and commit any changes if needed.
    
    Args:
        project_dir (str): Path to the project directory
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Change to the project directory
        os.chdir(project_dir)
        
        # Check if there are uncommitted changes
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        if result.stdout.strip():
            print("Uncommitted changes found. Committing changes...")
            
            # Update .gitignore if needed
            update_gitignore(project_dir)
            
            # Add all files and commit
            subprocess.run(["git", "add", "-A"], check=True)
            subprocess.run(["git", "commit", "-m", "Aider Commit"], check=True)
            print("Changes committed successfully.")
        else:
            print("No uncommitted changes found.")
            
            # Still check and update .gitignore if needed
            gitignore_path = os.path.join(project_dir, ".gitignore")
            if os.path.exists(gitignore_path):
                with open(gitignore_path, 'r') as f:
                    existing_content = f.read()
                
                if ".aider*" not in existing_content:
                    with open(gitignore_path, 'a') as f:
                        f.write("\n.aider*\n")
                    # Commit the .gitignore update
                    subprocess.run(["git", "add", ".gitignore"], check=True)
                    subprocess.run(["git", "commit", "-m", "Add .aider* to .gitignore"], check=True)
                    print("Added .aider* to .gitignore and committed.")
            else:
                # Create new .gitignore file
                update_gitignore(project_dir)
                # Commit the new .gitignore
                subprocess.run(["git", "add", ".gitignore"], check=True)
                subprocess.run(["git", "commit", "-m", "Add .gitignore with .aider* entry"], check=True)
                print("Created .gitignore with .aider* entry and committed.")
        
        # Change back to original directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error verifying Git repository: {e}")
        return False 