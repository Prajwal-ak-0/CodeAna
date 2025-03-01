import argparse
import os
from code_metadata_extractor import CodeMetadataExtractor

def parse_arguments():
    parser = argparse.ArgumentParser(description="Code Metadata Extractor")
    parser.add_argument('--map-tokens', type=int, default=8000, help='Number of tokens to map')
    parser.add_argument('--show-repo-map', action='store_true', help='Show repository map')
    parser.add_argument('--repo-path', default='.', help='Path to repository')
    parser.add_argument('--output', default='repo_map.md', help='Output file path')
    return parser.parse_args()

def generate_repo_map(extractor, output_file):
    """Generate a repository map in markdown format"""
    with open(output_file, 'w') as f:
        f.write("# Repository Map\n\n")
        
        # Write repository structure
        f.write("## Directory Structure\n```\n")
        for root, dirs, files in os.walk(extractor.repo_path):
            level = root.replace(extractor.repo_path, '').count(os.sep)
            indent = '  ' * level
            f.write(f"{indent}{os.path.basename(root)}/\n")
            for file in files:
                if not file.startswith('.'):
                    f.write(f"{indent}  {file}\n")
        f.write("```\n\n")
        
        # Write language statistics
        f.write("## Language Distribution\n")
        for lang, count in extractor.language_counts.most_common():
            f.write(f"- {lang}: {count} files\n")
        f.write("\n")
        
        # Write file summaries
        f.write("## File Summaries\n")
        for metadata in extractor.file_metadata:
            if metadata:  # Skip empty metadata
                f.write(f"\n### {metadata['file_path']}\n")
                f.write(f"- Language: {metadata['language']}\n")
                f.write(f"- Lines: {metadata['line_count']}\n")
                if metadata['imports']:
                    f.write(f"- Imports: {metadata['imports']}\n")

def execute_command(args):
    if args.show_repo_map:
        extractor = CodeMetadataExtractor(args.repo_path)
        extractor.traverse_repository()
        generate_repo_map(extractor, args.output)
        print(f"Repository map generated at: {args.output}")

if __name__ == "__main__":
    args = parse_arguments()
    execute_command(args)
