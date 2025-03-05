import csv

# Open the CSV file
with open('output.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    # Skip the header
    next(reader)
    
    # Process each row
    for row in reader:
        file_path = row[0]
        sinks = row[2]
        vulnerabilities = row[3]
        
        print(f"\n=== {file_path} ===")
        
        # Print sink details if available
        if sinks:
            print("\nSink Details:")
            print(sinks)
        
        # Print vulnerability details if available
        if vulnerabilities:
            print("\nVulnerabilities:")
            print(vulnerabilities) 