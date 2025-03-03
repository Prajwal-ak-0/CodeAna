"""
This script reads the existing JSON tree (output.json) and a CSV file (bearer_input.csv)
containing vulnerability details. For each row in the CSV:
  - The "File Name" (CSV column 1) is used to locate the corresponding file node in the JSON tree.
  - A vulnerability object is created using:
      • "code_snippet": CSV column 2,
      • "line_number": CSV column 3,
      • "risk_level": CSV column 4,
      • "ref_link": CSV column 5,
      • "message_to_fix": CSV column 6.
  - The vulnerability object is then appended to the file node's "vulnerabilities" list.
The updated JSON tree is written back to output.json.
"""

import csv
import json

def find_file_node(node, target, current_path=""):
    """
    Recursively traverses the JSON tree to locate the file node whose full relative path equals target.
    The full path is built from directory names (ignoring the "root" node) and the file node's "name".
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
    # Recurse into children if any.
    if "children" in node:
        for child in node["children"]:
            result = find_file_node(child, target, new_path)
            if result:
                return result
    return None

def update_vulnerabilities(json_tree, csv_file):
    """
    Reads the CSV file and for each row, finds the corresponding file node in the JSON tree (using File Name)
    and appends a vulnerability object to that file node's "vulnerabilities" list.
    
    CSV Format (columns):
      1. File Name
      2. Code Snippet
      3. Line Number
      4. Risk Level
      5. Ref Link
      6. Message To Fix
    """
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # skip header row
        for row in reader:
            # Unpack CSV columns.
            file_name = row[0].strip()
            code_snippet = row[1].strip()
            line_number = row[2].strip()
            risk_level = row[3].strip()
            ref_link = row[4].strip()
            message_to_fix = row[5].strip()
            
            vulnerability = {
                "code_snippet": code_snippet,
                "line_number": line_number,
                "risk_level": risk_level,
                "ref_link": ref_link,
                "message_to_fix": message_to_fix
            }
            # Use file_name as the target path.
            node = find_file_node(json_tree, file_name, current_path="")
            if node is not None:
                node["vulnerabilities"].append(vulnerability)
            else:
                print(f"Warning: File '{file_name}' not found in JSON tree.")
    return json_tree

def main():
    output_json_file = "aider_repomap.json"   # Pre-generated JSON tree file
    csv_file = "bearer_output.csv"        # CSV file with vulnerability details
    
    # Load the existing JSON tree.
    with open(output_json_file, 'r', encoding='utf-8') as f:
        json_tree = json.load(f)
    
    # Update the tree with vulnerabilities.
    updated_tree = update_vulnerabilities(json_tree, csv_file)
    
    # Write the updated JSON tree back to output.json.
    with open(output_json_file, 'w', encoding='utf-8') as f:
        json.dump(updated_tree, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()
