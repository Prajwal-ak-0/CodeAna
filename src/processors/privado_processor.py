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
    Extracts data sink information from a privado.json file and returns a list of dictionaries.
    The dictionaries contain: Data Sink ID, Sink Label, Code Snippet, File Path, Line Number,
    Column Number, and Data Flow Path.
    
    Args:
        json_file_path (str): Path to the privado.json file.
    
    Returns:
        List[Dict[str, str]]: Extracted data ready for further processing.
    """
    try:
        with open(json_file_path, 'r') as f:
            privado_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: privado.json file not found at '{json_file_path}'. Please ensure the file exists in the current directory or provide the correct path.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{json_file_path}'. Please ensure the file is a valid JSON file.")
        return []

    # Build sink definitions mapping
    sink_definitions = {sink['id']: sink['name'] for sink in privado_data.get('sinks', [])}

    rows = []
    # Extract headers: Data Sink ID, Sink Label, Code Snippet, File Path, Line Number, Column Number, Data Flow Path
    # Process sinkProcessing occurrences
    for sink_processing_item in privado_data.get('sinkProcessing', []):
        sink_id = sink_processing_item.get('sinkId')
        sink_label = sink_definitions.get(sink_id, "Unknown Sink Label")
        for occurrence in sink_processing_item.get('occurrences', []):
            code_snippet = occurrence.get('sample', 'N/A').strip()
            file_path = occurrence.get('fileName', 'N/A')
            line_number = occurrence.get('lineNumber', 'N/A')
            column_number = occurrence.get('columnNumber', 'N/A')
            data_flow_path_str = "Sink Processing Occurrence - Direct Location"
            row = {
                "Data Sink ID": sink_id,
                "Sink Label": sink_label,
                "Code Snippet": code_snippet,
                "File Path": file_path,
                "Line Number": line_number,
                "Column Number": column_number,
                "Data Flow Path": data_flow_path_str
            }
            rows.append(row)

    # Process data flow paths for storages, internal_apis, and third_parties
    data_flow_sections = ["storages", "internal_apis", "third_parties"]
    for section_name in data_flow_sections:
        for data_flow_item in privado_data.get('dataFlow', {}).get(section_name, []):
            for sink_info in data_flow_item.get('sinks', []):
                sink_id_dataflow = sink_info.get('id')
                sink_label_dataflow = sink_definitions.get(sink_id_dataflow, "Unknown Sink Label")
                for path_info in sink_info.get('paths', []):
                    data_flow_path_locations = path_info.get('path', [])
                    data_flow_path_files = [location.get('fileName', 'N/A') for location in data_flow_path_locations]
                    data_flow_path_str = " -> ".join(data_flow_path_files)

                    if data_flow_path_locations:
                        sink_occurrence_location = data_flow_path_locations[-1]
                        code_snippet_dataflow = sink_occurrence_location.get('sample', 'N/A').strip()
                        file_path_dataflow = sink_occurrence_location.get('fileName', 'N/A')
                        line_number_dataflow = sink_occurrence_location.get('lineNumber', 'N/A')
                        column_number_dataflow = sink_occurrence_location.get('columnNumber', 'N/A')
                        row = {
                            "Data Sink ID": sink_id_dataflow,
                            "Sink Label": sink_label_dataflow,
                            "Code Snippet": code_snippet_dataflow,
                            "File Path": file_path_dataflow,
                            "Line Number": line_number_dataflow,
                            "Column Number": column_number_dataflow,
                            "Data Flow Path": data_flow_path_str
                        }
                        rows.append(row)
                    else:
                        row = {
                            "Data Sink ID": sink_id_dataflow,
                            "Sink Label": sink_label_dataflow,
                            "Code Snippet": "N/A",
                            "File Path": "N/A",
                            "Line Number": "N/A",
                            "Column Number": "N/A",
                            "Data Flow Path": "No Data Flow Path Available"
                        }
                        rows.append(row)

    print(f"Data extracted from '{json_file_path}'.")
    return rows

def create_prompt(row: Dict[str, str]) -> str:
    """
    Create a prompt for the OpenAI API based on the row data.
    
    Args:
        row: A dictionary containing the CSV row data.
        
    Returns:
        A formatted prompt string.
    """
    return f"""
Analyze the following code information related to a data sink:

Data Sink ID: {row.get('Data Sink ID', 'N/A')}
Current Sink Label: {row.get('Sink Label', 'N/A')}
Code Snippet: {row.get('Code Snippet', 'N/A')}
File Path: {row.get('File Path', 'N/A')}
Line Number: {row.get('Line Number', 'N/A')}
Column Number: {row.get('Column Number', 'N/A')}
Data Flow Path: {row.get('Data Flow Path', 'N/A')}

Based on this information:
1. Identify the specific type of data sink (e.g., S3 bucket, RDS instance, file, HTTP endpoint, database via ORM, API for blob/object storage, etc.)
2. Provide a concise summary of what the code is doing with this data sink.
"""

def get_system_prompt() -> str:
    """
    Returns the system prompt for the OpenAI API.
    """
    return """
You are an expert code analyzer specializing in data flow and security analysis.
Your task is to analyze code snippets related to data sinks and provide:
1. A specific label for the type of data sink (e.g., S3 bucket, RDS instance, file, HTTP endpoint, database via ORM, API for blob/object storage, etc.)
2. A concise summary of what the code is doing with this data sink.

Respond with JSON only, following the specified schema.
"""

def process_batch(client: OpenAI, rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Process a batch of rows using the OpenAI API.
    
    Args:
        client: OpenAI client.
        rows: List of dictionaries containing the row data.
        
    Returns:
        List of dictionaries with the original row data plus the AI-generated sink label and code summary.
    """
    results = []
    for row in rows:
        prompt = create_prompt(row)
        max_retries = 5
        retry_count = 0

        while retry_count < max_retries:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": get_system_prompt()},
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_schema", "json_schema": SCHEMA},
                )
                
                response_content = response.choices[0].message.content
                print(f"Processing row with Data Sink ID: {row.get('Data Sink ID', 'N/A')}")
                print(f"Response content: {response_content}")
                response_json = json.loads(response_content)
                
                row_with_response = row.copy()
                row_with_response["AI Sink Label"] = response_json.get("sink_label", "N/A")
                row_with_response["Code Summary"] = response_json.get("summary", "N/A")
                results.append(row_with_response)
                break
                
            except Exception as e:
                retry_count += 1
                if "rate limit" in str(e).lower():
                    wait_time = 2 ** retry_count  # Exponential backoff
                    print(f"Rate limit hit. Waiting for {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                else:
                    print(f"Error processing row: {e}")
                    row_with_response = row.copy()
                    row_with_response["AI Sink Label"] = "Error in processing"
                    row_with_response["Code Summary"] = "Error in processing"
                    results.append(row_with_response)
                    break
        
        if retry_count == max_retries:
            print(f"Max retries reached for row. Adding without AI analysis.")
            row_with_response = row.copy()
            row_with_response["AI Sink Label"] = "Max retries reached"
            row_with_response["Code Summary"] = "Max retries reached"
            results.append(row_with_response)
    
    return results

def process_data(rows: List[Dict[str, str]], output_file: str = "privado_output.csv", batch_size: int = 5):
    """
    Process the extracted data by sending it to the OpenAI API in batches,
    then write the final results (with additional AI Sink Label and Code Summary columns)
    to an output CSV file.
    
    Args:
        rows: List of dictionaries representing the extracted data.
        output_file: Path to the final output CSV file.
        batch_size: Number of rows to process in each batch.
    """
    # Check if OpenAI API key is set
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        return

    client = OpenAI()
    
    if not rows:
        print("No data to process.")
        return
        
    all_results = []
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        print(f"Processing batch {i // batch_size + 1} of {(len(rows) + batch_size - 1) // batch_size}...")
        batch_results = process_batch(client, batch)
        all_results.extend(batch_results)
        
        # Small delay between batches to avoid rate limits
        if i + batch_size < len(rows):
            time.sleep(1)
    
    if all_results:
        headers = list(all_results[0].keys())
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(all_results)
        print(f"Processing complete. Results saved to {output_file}")
    else:
        print("No results to write to CSV.")

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