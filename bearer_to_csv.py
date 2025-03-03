import csv
import re

# Input and output file names
# INPUT_FILE = "bearer_input.txt"
INPUT_FILE = "finance_output.txt"
OUTPUT_FILE = "bearer_output.csv"

# Regular expression patterns for different parts of the report
RISK_RE = re.compile(r"^(LOW|MEDIUM|HIGH):\s*(.+)$")
URL_RE = re.compile(r"^(https?://\S+)$")
MESSAGE_RE = re.compile(r"^To ignore this finding, run:\s*(.+)$")
FILE_RE = re.compile(r"^File:\s*(.+):(\d+)", re.IGNORECASE)

# This function goes through the file line-by-line and uses a simple state machine logic.
def parse_bearer_report(input_file):
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
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check if the line starts with a risk (LOW, MEDIUM, HIGH)
        risk_match = RISK_RE.match(stripped)
        if risk_match:
            # If we already have a risk in the current record, it means a new record is starting.
            if current_record["Risk Level"]:
                records.append(current_record)
                current_record = {
                    "File Name": "",
                    "Code Snippet": "",
                    "Line Number": "",
                    "Risk Level": "",
                    "Ref Link": "",
                    "Message To Fix": ""
                }
            # Set Risk Level; using just the severity word for CSV column
            current_record["Risk Level"] = risk_match.group(1)
            # Optionally store the full risk text in Code Snippet *if no code snippet is found later*
            # Here we wait for the actual code snippet, so we do not override it later.
            continue

        # Look for the reference URL
        url_match = URL_RE.match(stripped)
        if url_match:
            current_record["Ref Link"] = url_match.group(1)
            continue

        # Look for the ignore message
        message_match = MESSAGE_RE.match(stripped)
        if message_match:
            current_record["Message To Fix"] = message_match.group(1)
            continue

        # Look for the file name and line number
        file_match = FILE_RE.match(stripped)
        if file_match:
            current_record["File Name"] = file_match.group(1)
            current_record["Line Number"] = file_match.group(2)
            continue
        
        # Anything else that is not empty is assumed to be the code snippet.
        # If a code snippet is already present, we append further non-empty lines.
        if current_record["Code Snippet"]:
            current_record["Code Snippet"] += " " + stripped
        else:
            current_record["Code Snippet"] = stripped

    # Append the last record if it exists (if a risk level was set, we consider it a valid record)
    if current_record["Risk Level"]:
        records.append(current_record)
    
    return records

# Write the resulting records into a CSV file.
def write_to_csv(records, output_file):
    headers = ["File Name", "Code Snippet", "Line Number", "Risk Level", "Ref Link", "Message To Fix"]
    with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for record in records:
            writer.writerow(record)

def main():
    parsed_data = parse_bearer_report(INPUT_FILE)
    write_to_csv(parsed_data, OUTPUT_FILE)
    print(f"CSV file '{OUTPUT_FILE}' has been created successfully with {len(parsed_data)} record(s).")

if __name__ == "__main__":
    main()
