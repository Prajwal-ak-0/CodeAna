import os
import json
import csv
import sys

def ensure_file_exists(file_path, error_message=None):
    """
    Check if a file exists and exit with an error message if it doesn't.
    
    Args:
        file_path (str): Path to the file to check
        error_message (str, optional): Custom error message. Defaults to None.
        
    Returns:
        bool: True if the file exists, False otherwise
    """
    if not os.path.exists(file_path):
        if error_message:
            print(error_message)
        else:
            print(f"Error: File '{file_path}' not found.")
        return False
    return True

def copy_file(source_path, destination_path):
    """
    Copy a file from source to destination.
    
    Args:
        source_path (str): Path to the source file
        destination_path (str): Path to the destination file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not ensure_file_exists(source_path):
            return False
            
        with open(source_path, 'r', encoding='utf-8') as src:
            with open(destination_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        print(f"Copied {source_path} to {destination_path}")
        return True
    except Exception as e:
        print(f"Error copying file: {e}")
        return False

def read_json_file(file_path):
    """
    Read a JSON file and return its contents.
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        dict: JSON contents or None if an error occurred
    """
    try:
        if not ensure_file_exists(file_path):
            return None
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}")
        return None
    except Exception as e:
        print(f"Error reading JSON file {file_path}: {e}")
        return None

def write_json_file(file_path, data):
    """
    Write data to a JSON file.
    
    Args:
        file_path (str): Path to the JSON file
        data (dict): Data to write
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Successfully wrote to {file_path}")
        return True
    except Exception as e:
        print(f"Error writing JSON file {file_path}: {e}")
        return False

def read_csv_file(file_path):
    """
    Read a CSV file and return its contents as a list of dictionaries.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        list: List of dictionaries representing CSV rows or None if an error occurred
    """
    try:
        if not ensure_file_exists(file_path):
            return None
            
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        print(f"Error reading CSV file {file_path}: {e}")
        return None

def write_csv_file(file_path, data, fieldnames=None):
    """
    Write data to a CSV file.
    
    Args:
        file_path (str): Path to the CSV file
        data (list): List of dictionaries to write
        fieldnames (list, optional): List of field names. Defaults to None.
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not data:
            print(f"No data to write to {file_path}")
            return False
            
        if fieldnames is None:
            fieldnames = data[0].keys()
            
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"Successfully wrote to {file_path}")
        return True
    except Exception as e:
        print(f"Error writing CSV file {file_path}: {e}")
        return False 