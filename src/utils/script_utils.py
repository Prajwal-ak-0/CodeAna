import os
import subprocess
import sys

def create_script(script_name, script_content):
    """
    Create a shell script with the given name and content.
    
    Args:
        script_name (str): Name of the script file
        script_content (str): Content of the script
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure the directory exists
        script_dir = os.path.dirname(script_name)
        if script_dir and not os.path.exists(script_dir):
            os.makedirs(script_dir, exist_ok=True)
            
        # Write the shell script
        with open(script_name, "w") as f:
            f.write(script_content)
        
        # Make the shell script executable
        os.chmod(script_name, 0o755)
        print(f"Created and made executable: {script_name}")
        return True
    except Exception as e:
        print(f"Error creating script {script_name}: {e}")
        return False

def delete_script(script_name):
    """
    Delete a shell script.
    
    Args:
        script_name (str): Name of the script file to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if os.path.exists(script_name):
            os.remove(script_name)
            print(f"Deleted {script_name}")
            return True
        else:
            print(f"{script_name} not found, nothing to delete")
            return False
    except Exception as e:
        print(f"Error deleting {script_name}: {e}")
        return False

def run_script(script_name, *args):
    """
    Run a shell script with the given arguments.
    
    Args:
        script_name (str): Name of the script file to run
        *args: Variable length argument list to pass to the script
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"Running {script_name} with arguments: {args}")
        # Get the directory and basename of the script
        script_dir = os.path.dirname(script_name)
        script_basename = os.path.basename(script_name)
        
        # Change to the script directory if it's not empty
        if script_dir:
            current_dir = os.getcwd()
            os.chdir(script_dir)
            try:
                subprocess.run([f"./{script_basename}"] + list(args), check=True)
            finally:
                # Change back to the original directory
                os.chdir(current_dir)
        else:
            # Run the script in the current directory
            subprocess.run([f"./{script_name}"] + list(args), check=True)
            
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running script {script_name}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error running script {script_name}: {e}")
        return False 