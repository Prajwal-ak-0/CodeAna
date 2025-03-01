import argparse
from code_metadata_extractor import main, CodeMetadataExtractor

def parse_arguments():
    parser = argparse.ArgumentParser(description="Aider CLI")
    parser.add_argument('--map-tokens', type=int, help='Number of tokens to map')
    parser.add_argument('--show-repo-map', action='store_true', help='Show repository map')
    parser.add_argument('output_file', nargs='?', default='repo_map.md', help='Output file for the repo map')
    return parser.parse_args()

def execute_command(args):
    if args.show_repo_map:
        extractor = CodeMetadataExtractor()
        # Assuming generate_reports can handle the output file
        extractor.generate_reports(args.output_file)

def main():
    args = parse_arguments()
    execute_command(args)
    main() 
