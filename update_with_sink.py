import csv
import json

def find_file_node(node, target_path, current_path=""):
    """
    Recursively traverses the tree to find the file node with a full path matching target_path.
    The full path is built by joining directory names and the file's name with '/'.
    Returns the node if found, else None.
    """
    if "structure" in node:
        # This is a file node; construct its full path.
        full_path = current_path + node["name"]
        if full_path == target_path:
            return node
    if "children" in node:
        for child in node["children"]:
            new_path = current_path + child["name"] + "/" if "children" in child else current_path
            result = find_file_node(child, target_path, current_path + (child["name"] + "/") if "children" in child else current_path)
            if result:
                return result
    return None

def update_sink_details(json_tree, csv_file):
    """
    Reads the CSV file and updates the JSON tree.
    For each row in the CSV, uses the file path (column 4) to find the matching file node,
    then appends a sink_details object with the following keys:
      - "ai_sink_label" : CSV column 8,
      - "code_summary"  : CSV column 9,
      - "code_snippet"  : CSV column 3,
      - "line_number"   : CSV column 5,
      - "column_number" : CSV column 6.
    """
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # skip header row
        for row in reader:
            # CSV columns (0-indexed):
            # 0: Data Sink ID, 1: Sink Label, 2: Code Snippet, 3: File Path,
            # 4: Line Number, 5: Column Number, 6: Data Flow Path, 7: AI Sink Label, 8: Code Summary
            file_path = row[3]
            sink_detail = {
                "ai_sink_label": row[7],
                "code_summary": row[8],
                "code_snippet": row[2],
                "line_number": row[4],
                "column_number": row[5]
            }
            # Find the file node in the JSON tree that matches file_path.
            node = find_file_node(json_tree, file_path, current_path="")
            if node is not None:
                # Append the sink_detail to the node's "sink_details" list.
                node["sink_details"].append(sink_detail)
            else:
                print(f"Warning: File path '{file_path}' not found in JSON tree.")
    return json_tree

def main():
    output_json_file = "output.json"   # Existing JSON file generated from input.txt
    csv_file = "privado_output.csv"              # CSV file containing sink details
    
    # Load the current JSON tree.
    with open(output_json_file, 'r', encoding='utf-8') as f:
        json_tree = json.load(f)
    
    # Update the tree with sink details from the CSV.
    updated_tree = update_sink_details(json_tree, csv_file)
    
    # Write the updated tree back to output.json.
    with open(output_json_file, 'w', encoding='utf-8') as f:
        json.dump(updated_tree, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()
