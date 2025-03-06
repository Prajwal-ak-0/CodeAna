import os
import json
import csv

def extract_code_snippet(node):
    """
    Combines the code snippet parts from the file's structure.
    
    Args:
        node (dict): File node
        
    Returns:
        str: Combined code snippet
    """
    snippet_lines = []
    structure = node.get("structure", {})
    if structure:
        classes = structure.get("classes", [])
        if classes:
            for cls in classes:
                # Append the class body
                snippet_lines.append(cls.get("class_body", ""))
                # For each method in the class, append its code
                methods = cls.get("methods", [])
                for method in methods:
                    snippet_lines.append(method.get("code", ""))
        # In case there is additional code under "other", include it too.
        if structure.get("other", ""):
            snippet_lines.append(structure.get("other", ""))
    return "\n".join(snippet_lines).strip()

def extract_sinks(node):
    """
    Processes sink_details to produce a clean text block.
    
    Args:
        node (dict): File node
        
    Returns:
        str: Formatted sink details
    """
    sinks_details = node.get("sink_details", [])
    sinks_block = []
    for sink in sinks_details:
        block = "<SINK>\n"
        block += sink.get("ai_sink_label", "").strip() + "\n"
        block += sink.get("code_summary", "").strip() + "\n"
        block += sink.get("code_snippet", "").strip() + "\n"
        block += "</SINK>"
        sinks_block.append(block)
    return "\n\n".join(sinks_block).strip()

def extract_vulnerabilities(node):
    """
    Processes vulnerabilities to produce a clean text block.
    
    Args:
        node (dict): File node
        
    Returns:
        str: Formatted vulnerabilities
    """
    vulns = node.get("vulnerabilities", [])
    vuln_block = []
    for vuln in vulns:
        block = "<VULNERABILITIES>\n"
        block += vuln.get("code_snippet", "").strip() + "\n"
        block += vuln.get("risk_level", "").strip() + "\n"
        block += vuln.get("ref_link", "").strip() + "\n"
        block += vuln.get("message_to_fix", "").strip() + "\n"
        block += "</VULNERABILITIES>"
        vuln_block.append(block)
    return "\n\n".join(vuln_block).strip()

def traverse_node(node, parent_path=""):
    """
    Recursively traverse the JSON hierarchy.
    
    Args:
        node (dict): Current node
        parent_path (str, optional): Parent path. Defaults to "".
        
    Returns:
        list: List of dictionaries containing file information
    """
    rows = []
    # Build the current full path: if parent_path exists, join it with the node's name;
    # otherwise start from node["name"].
    current_path = os.path.join(parent_path, node.get("name", ""))
    # If the node has children then it is a directory – recurse.
    if node.get("children"):
        for child in node["children"]:
            rows.extend(traverse_node(child, current_path))
    else:
        # This is a file node. Prepare the row details.
        file_path = current_path  # COMPLETE FILE PATH
        
        code_snippet = extract_code_snippet(node)
        sinks_text = extract_sinks(node)
        vulnerabilities_text = extract_vulnerabilities(node)
        
        rows.append({
            "COMPLETE FILE PATH": file_path,
            "Code Snippet": code_snippet,
            "Sinks": sinks_text,
            "Vulnerabilities": vulnerabilities_text
        })
    return rows

def convert_json_to_csv():
    """
    Convert the JSON file to CSV.
    """
    json_file = "aider_repomap.json"
    output_file = "output.csv"
    try:
        # Check if the JSON file exists
        if not os.path.exists(json_file):
            print(f"Error: {json_file} not found")
            return
            
        # Load the JSON data
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