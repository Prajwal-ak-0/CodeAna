import argparse
import os
from code_metadata_extractor import CodeMetadataExtractor

def parse_arguments():
    parser = argparse.ArgumentParser(description="Code Metadata Extractor")
    parser.add_argument('--map-tokens', type=int, default=8000, help='Number of tokens to map')
    parser.add_argument('--show-repo-map', action='store_true', help='Show repository map')
    parser.add_argument('--repo-path', default='.', help='Path to repository')
    return parser.parse_args()

def execute_command(args):
    if args.show_repo_map:
        extractor = CodeMetadataExtractor(args.repo_path)
        extractor.traverse_repository()
        extractor.generate_reports()

if __name__ == "__main__":
    args = parse_arguments()
    execute_command(args)
