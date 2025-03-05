import csv

# Open the CSV file
with open('output.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    # Get the header
    header = next(reader)
    print(f"Header: {header}")
    print(f"Number of columns: {len(header)}")
    
    # Count the rows
    rows = list(reader)
    print(f"Number of rows: {len(rows)}")
    
    # Print the file paths
    print("\nFile paths:")
    for row in rows:
        print(f"- {row[0]}") 