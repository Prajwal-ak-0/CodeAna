import os
import csv
import re
import json

# Regular expression patterns for different parts of the report
RISK_RE = re.compile(r"^(LOW|MEDIUM|HIGH):\s*(.+)$")
URL_RE = re.compile(r"^(https?://\S+)$")
MESSAGE_RE = re.compile(r"^To ignore this finding, run:\s*(.+)$")
FILE_RE = re.compile(r"^File:\s*(.+):(\d+)", re.IGNORECASE)

def parse_bearer_report(input_file):
    """
    Parse the Bearer report file.
    
    Args:
        input_file (str): Path to the Bearer report file
        
    Returns:
        list: List of dictionaries containing vulnerability information
    """
    records = []
    # Initialize an empty record with required columns
    current_record = {
        "File Name": "",
        "Code Snippet": "",
        "Line Number": "",
        "Risk Level": "",
        "Ref Link": "",
        "Message To Fix": ""
    }
    
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # State variables for parsing
    in_code_block = False
    code_lines = []
    
    for line in lines:
        line = line.rstrip()
        
        # Check if we're entering or exiting a code block
        if line.startswith("```"):
            if in_code_block:
                # Exiting code block, save the code snippet
                current_record["Code Snippet"] = "\n".join(code_lines)
                code_lines = []
            in_code_block = not in_code_block
            continue
        
        # If we're in a code block, collect the code lines
        if in_code_block:
            code_lines.append(line)
            continue
        
        # Check for risk level and title
        risk_match = RISK_RE.match(line)
        if risk_match:
            # If we have a previous record with data, save it
            if current_record["File Name"] and current_record["Risk Level"]:
                records.append(current_record.copy())
            
            # Start a new record
            current_record = {
                "File Name": "",
                "Code Snippet": "",
                "Line Number": "",
                "Risk Level": risk_match.group(1),  # LOW, MEDIUM, or HIGH
                "Ref Link": "",
                "Message To Fix": ""
            }
            continue
        
        # Check for URL (reference link)
        url_match = URL_RE.match(line)
        if url_match and current_record["Risk Level"]:
            current_record["Ref Link"] = url_match.group(1)
            continue
        
        # Check for file information
        file_match = FILE_RE.match(line)
        if file_match and current_record["Risk Level"]:
            current_record["File Name"] = file_match.group(1)
            current_record["Line Number"] = file_match.group(2)
            continue
        
        # Check for message to fix
        message_match = MESSAGE_RE.match(line)
        if message_match and current_record["Risk Level"]:
            current_record["Message To Fix"] = message_match.group(1)
            continue
    
    # Don't forget to add the last record if it has data
    if current_record["File Name"] and current_record["Risk Level"]:
        records.append(current_record.copy())
    
    return records

def write_to_csv(records, output_file):
    """
    Write records to a CSV file.
    
    Args:
        records (list): List of dictionaries containing vulnerability information
        output_file (str): Path to the output CSV file
    """
    fieldnames = ["File Name", "Code Snippet", "Line Number", "Risk Level", "Ref Link", "Message To Fix"]
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

def process_bearer_data():
    """
    Process Bearer data and create a CSV file.
    """
    try:
        input_file = "bearer_output.txt"
        output_file = "bearer_output.csv"
        
        # Check if input file exists
        if not os.path.exists(input_file):
            print(f"Error: {input_file} not found")
            return None
        
        # Parse bearer report and write to CSV
        parsed_data = parse_bearer_report(input_file)
        write_to_csv(parsed_data, output_file)
        
        if os.path.exists(output_file):
            print(f"Successfully created: {output_file}")
        else:
            print(f"Error: {output_file} was not created")
            return None
        
        return output_file
    except Exception as e:
        print(f"Error processing bearer data: {e}")
        return None

def update_vulnerabilities(json_tree, csv_file):
    """
    Update the JSON tree with vulnerabilities from the CSV file.
    
    Args:
        json_tree (dict): JSON tree to update
        csv_file (str): Path to the CSV file
        
    Returns:
        dict: Updated JSON tree
    """
    def find_file_node(node, target, current_path=""):
        """
        Find a file node in the JSON tree.
        
        Args:
            node (dict): Current node
            target (str): Target file path
            current_path (str, optional): Current path. Defaults to "".
            
        Returns:
            dict: File node if found, None otherwise
        """
        # If this is a file node (has "structure"), compute its full path.
        if "structure" in node:
            full_path = current_path + node["name"]
            if full_path == target:
                return node
        # Prepare new path: skip adding "root" to the path.
        new_path = current_path
        if node.get("name") and node["name"] != "root":
            new_path = current_path + node["name"] + "/"
        
        # If this node has children, recursively search them.
        if "children" in node:
            for child in node["children"]:
                result = find_file_node(child, target, new_path)
                if result:
                    return result
        return None
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            file_path = row["File Name"]
            vulnerability = {
                "code_snippet": row["Code Snippet"],
                "line_number": row["Line Number"],
                "risk_level": row["Risk Level"],
                "ref_link": row["Ref Link"],
                "message_to_fix": row["Message To Fix"]
            }
            
            # Find the file node in the JSON tree.
            node = find_file_node(json_tree, file_path)
            if node:
                # Append the vulnerability to the node's "vulnerabilities" list.
                node["vulnerabilities"].append(vulnerability)
            else:
                print(f"Warning: File '{file_path}' not found in JSON tree.")
    
    return json_tree

def update_json_with_vulnerabilities():
    """
    Update the JSON tree with vulnerabilities from the CSV file.
    """
    try:
        output_json_file = "aider_repomap.json"  # JSON file generated in Task 2
        csv_file = "bearer_output.csv"           # CSV file from bearer processing
        
        # Check if both files exist
        if not os.path.exists(output_json_file):
            print(f"Error: {output_json_file} not found")
            return
        
        if not os.path.exists(csv_file):
            print(f"Error: {csv_file} not found")
            return
        
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