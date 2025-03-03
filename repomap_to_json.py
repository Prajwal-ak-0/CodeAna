import os
import re
import json

def parse_file_content(content: str) -> dict:
    """
    Parses the content of a file summary and extracts classes and their methods.
    
    Returns a dictionary with two keys:
      - "classes": a list of objects for each class found.
          Each class object has:
              "name": class name,
              "class_body": code lines within the class outside any method,
              "methods": a list of methods with "name" and "code".
      - "other": any code outside of any class definition.
    """
    lines = content.splitlines()
    classes = []
    file_other_lines = []
    
    current_class = None
    current_method = None

    # Patterns to detect class and method definitions.
    class_pattern = re.compile(r'^[\s│]*class\s+(\w+)\s*[:\(]')
    method_pattern = re.compile(r'^[\s│]*def\s+(\w+)\s*\(')

    for line in lines:
        class_match = class_pattern.match(line)
        method_match = method_pattern.match(line)
        
        if class_match:
            # Close any open method.
            if current_method is not None and current_class is not None:
                current_class["methods"].append(current_method)
                current_method = None
            # Save the previous class if exists.
            if current_class is not None:
                classes.append(current_class)
            # Start a new class.
            class_name = class_match.group(1)
            current_class = {
                "name": class_name,
                "class_body": line + "\n",
                "methods": []
            }
        elif method_match and current_class is not None:
            # Found a method within a class.
            if current_method is not None:
                current_class["methods"].append(current_method)
            method_name = method_match.group(1)
            current_method = {
                "name": method_name,
                "code": line + "\n"
            }
        else:
            # Ordinary line.
            if current_method is not None:
                current_method["code"] += line + "\n"
            elif current_class is not None:
                current_class["class_body"] += line + "\n"
            else:
                file_other_lines.append(line)

    # Close any open blocks.
    if current_method is not None and current_class is not None:
        current_class["methods"].append(current_method)
    if current_class is not None:
        classes.append(current_class)

    result = {}
    if classes:
        result["classes"] = classes
    if file_other_lines:
        result["other"] = "\n".join(file_other_lines).strip()
    return result

def parse_input_file(input_file: str):
    """
    Parses the input file and returns a list of tuples (filepath, content).
    The file is assumed to start with a preamble and then file sections identified
    by headers (lines that contain a file path ending in .gitignore, .py, .sh, or .json).
    """
    file_header_re = re.compile(r'^([a-zA-Z0-9._/\-]+(?:\.gitignore|\.py|\.sh|\.json))\:?\s*$')
    
    files = []
    current_filepath = None
    current_content_lines = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    in_file_section = False
    for line in lines:
        stripped_line = line.rstrip('\n')
        header_match = file_header_re.match(stripped_line)
        if not in_file_section:
            if header_match:
                in_file_section = True
            else:
                continue  # Skip preamble lines
        if header_match:
            if current_filepath is not None:
                files.append((current_filepath, "\n".join(current_content_lines).strip()))
            current_filepath = header_match.group(1)
            current_content_lines = []
        else:
            if current_filepath is not None:
                current_content_lines.append(stripped_line)
    if current_filepath is not None:
        files.append((current_filepath, "\n".join(current_content_lines).strip()))
    
    return files

def insert_into_tree(root: dict, filepath: str, content: str) -> None:
    """
    Inserts a file (with its relative filepath and parsed content) into the directory tree.
    Each file node includes:
      - "structure": parsed content (classes, methods, etc.)
      - "source": empty list,
      - "data_model": empty list,
      - "third_party_dependencies": empty list,
      - "sink_details": empty list,
      - "vulnerabilities": empty list.
    """
    parts = filepath.split('/')
    current_node = root
    for i, part in enumerate(parts):
        if i == len(parts) - 1:
            # File leaf node.
            file_node = {
                "name": part,
                "structure": parse_file_content(content),
                "source": [],
                "data_model": [],
                "third_party_dependencies": [],
                "sink_details": [],
                "vulnerabilities": []
            }
            if "children" not in current_node:
                current_node["children"] = []
            current_node["children"].append(file_node)
        else:
            # Directory node.
            if "children" not in current_node:
                current_node["children"] = []
            dir_node = next((child for child in current_node["children"] 
                             if child["name"] == part and "children" in child), None)
            if dir_node is None:
                dir_node = {"name": part, "children": []}
                current_node["children"].append(dir_node)
            current_node = dir_node

def build_directory_tree(files):
    """
    Builds and returns the full directory tree from a list of (filepath, content) tuples.
    """
    root = {"name": "root", "children": []}
    for filepath, content in files:
        insert_into_tree(root, filepath, content)
    return root

def main():
    input_file = "input.txt"    # Assumes the input file is named input.txt
    output_file = "output.json"   # The output file to be generated

    files = parse_input_file(input_file)
    tree = build_directory_tree(files)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tree, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()
