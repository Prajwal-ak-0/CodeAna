import os
import json
import csv
import time
from openai import OpenAI
from typing import List, Dict, Any

# JSON schema for the OpenAI response
SCHEMA = {
    "name": "data_sink",
    "schema": {
        "type": "object",
        "properties": {
            "sink_label": {
                "type": "string",
                "description": "A label representing the data sink, which could be any type such as S3 buckets, RDS instances, files, HTTP endpoints, etc."
            },
            "summary": {
                "type": "string",
                "description": "A summary of the code related to the data sink."
            }
        },
        "required": [
            "sink_label",
            "summary"
        ],
        "additionalProperties": False
    },
    "strict": True
}

def extract_privado_data(json_file_path: str = "privado.json") -> List[Dict[str, str]]:
    """
    Extract data from the Privado JSON file.
    
    Args:
        json_file_path (str, optional): Path to the Privado JSON file. Defaults to "privado.json".
        
    Returns:
        List[Dict[str, str]]: List of dictionaries containing extracted data
    """
    try:
        # Check if the file exists
        if not os.path.exists(json_file_path):
            print(f"Error: {json_file_path} not found")
            return []
        
        # Load the JSON data
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract data sinks
        rows = []
        if "dataSinks" in data:
            for sink in data["dataSinks"]:
                sink_id = sink.get("id", "")
                sink_label = sink.get("name", "")
                
                # Extract code snippets
                for source in sink.get("sources", []):
                    for flow in source.get("flows", []):
                        for sink_flow in flow.get("sinks", []):
                            # Extract file path and line number
                            file_path = sink_flow.get("fileName", "")
                            line_number = sink_flow.get("lineNumber", "")
                            column_number = sink_flow.get("columnNumber", "")
                            
                            # Extract code snippet
                            code_snippet = sink_flow.get("code", "")
                            
                            # Extract data flow path
                            data_flow_path = flow.get("flowPath", "")
                            
                            # Create a row for the CSV
                            row = {
                                "Data Sink ID": sink_id,
                                "Sink Label": sink_label,
                                "Code Snippet": code_snippet,
                                "File Path": file_path,
                                "Line Number": line_number,
                                "Column Number": column_number,
                                "Data Flow Path": data_flow_path,
                                "AI Sink Label": "",  # Will be filled by OpenAI
                                "Code Summary": ""    # Will be filled by OpenAI
                            }
                            rows.append(row)
        
        print(f"Extracted {len(rows)} data sink entries from {json_file_path}")
        return rows
    except Exception as e:
        print(f"Error extracting data from {json_file_path}: {e}")
        return []

def create_prompt(row: Dict[str, str]) -> str:
    """
    Create a prompt for OpenAI to analyze a data sink.
    
    Args:
        row (Dict[str, str]): Dictionary containing data sink information
        
    Returns:
        str: Prompt for OpenAI
    """
    return f"""
Analyze the following code snippet that represents a data sink in a software application:

Code Snippet:
```
{row['Code Snippet']}
```

File Path: {row['File Path']}
Line Number: {row['Line Number']}
Data Flow Path: {row['Data Flow Path']}

Based on the code snippet and context, identify:
1. What type of data sink is this (e.g., S3 bucket, database, file system, HTTP endpoint)?
2. Provide a brief summary of what this code is doing with the data.

Your response should be concise and focused on the data handling aspects.
"""

def get_system_prompt() -> str:
    """
    Get the system prompt for OpenAI.
    
    Returns:
        str: System prompt
    """
    return """
You are a security analyst specializing in data flow analysis. Your task is to analyze code snippets 
that represent data sinks in applications. For each snippet, identify the type of data sink and 
provide a brief summary of what the code is doing with the data.
"""

def process_batch(client: OpenAI, rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Process a batch of rows using OpenAI.
    
    Args:
        client (OpenAI): OpenAI client
        rows (List[Dict[str, str]]): List of dictionaries containing data sink information
        
    Returns:
        List[Dict[str, Any]]: List of processed rows
    """
    processed_rows = []
    
    for row in rows:
        try:
            # Create the prompt for this row
            prompt = create_prompt(row)
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                tools=[{"type": "function", "function": SCHEMA}],
                tool_choice={"type": "function", "function": {"name": "data_sink"}}
            )
            
            # Extract the response
            tool_call = response.choices[0].message.tool_calls[0]
            result = json.loads(tool_call.function.arguments)
            
            # Update the row with AI-generated information
            row_copy = row.copy()
            row_copy["AI Sink Label"] = result.get("sink_label", "")
            row_copy["Code Summary"] = result.get("summary", "")
            
            processed_rows.append(row_copy)
            
            # Sleep to avoid rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error processing row: {e}")
            # Still include the row, but without AI-generated information
            processed_rows.append(row)
    
    return processed_rows

def process_data(rows: List[Dict[str, str]], output_file: str = "privado_output.csv", batch_size: int = 5):
    """
    Process data using OpenAI and write to CSV.
    
    Args:
        rows (List[Dict[str, str]]): List of dictionaries containing data sink information
        output_file (str, optional): Path to the output CSV file. Defaults to "privado_output.csv".
        batch_size (int, optional): Number of rows to process in each batch. Defaults to 5.
    """
    if not rows:
        print("No data to process")
        return
    
    # Get OpenAI API key from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Writing CSV without AI-generated information")
        write_csv(rows, output_file)
        return
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Process rows in batches
    all_processed_rows = []
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(rows) + batch_size - 1)//batch_size}")
        processed_batch = process_batch(client, batch)
        all_processed_rows.extend(processed_batch)
    
    # Write to CSV
    write_csv(all_processed_rows, output_file)

def write_csv(rows: List[Dict[str, str]], output_file: str):
    """
    Write rows to a CSV file.
    
    Args:
        rows (List[Dict[str, str]]): List of dictionaries containing data sink information
        output_file (str): Path to the output CSV file
    """
    try:
        fieldnames = [
            "Data Sink ID", "Sink Label", "Code Snippet", "File Path",
            "Line Number", "Column Number", "Data Flow Path",
            "AI Sink Label", "Code Summary"
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"Successfully wrote {len(rows)} rows to {output_file}")
    except Exception as e:
        print(f"Error writing CSV: {e}")

def update_sink_details(json_tree, csv_file):
    """
    Update the JSON tree with sink details from the CSV file.
    
    Args:
        json_tree (dict): JSON tree to update
        csv_file (str): Path to the CSV file
        
    Returns:
        dict: Updated JSON tree
    """
    def find_file_node(node, target_path, current_path=""):
        """
        Find a file node in the JSON tree.
        
        Args:
            node (dict): Current node
            target_path (str): Target file path
            current_path (str, optional): Current path. Defaults to "".
            
        Returns:
            dict: File node if found, None otherwise
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

def process_privado_data():
    """
    Process Privado data and create a CSV file.
    """
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

def update_json_with_sink_details():
    """
    Update the JSON tree with sink details from the CSV file.
    """
    try:
        output_json_file = "aider_repomap.json"  # JSON file generated in Task 2
        csv_file = "privado_output.csv"          # CSV file from privado processing
        
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
        
        # Update the tree with sink details from the CSV
        updated_tree = update_sink_details(json_tree, csv_file)
        
        # Write the updated tree back to the JSON file
        with open(output_json_file, 'w', encoding='utf-8') as f:
            json.dump(updated_tree, f, indent=4, ensure_ascii=False)
        
        print(f"Successfully updated {output_json_file} with sink details from {csv_file}")
    except Exception as e:
        print(f"Error updating JSON with sink details: {e}") 