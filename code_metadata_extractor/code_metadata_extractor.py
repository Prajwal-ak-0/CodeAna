import os
import re
import csv
import time
import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple, Any

class CodeMetadataExtractor:
    """Extract metadata from code repositories"""
    
    # File extensions to analyze, grouped by language
    LANGUAGE_EXTENSIONS = {
        'Python': ['.py', '.pyi', '.pyx', '.ipynb'],
        'JavaScript': ['.js', '.jsx'],
        'TypeScript': ['.ts', '.tsx'],
        'HTML': ['.html', '.htm'],
        'CSS': ['.css', '.scss', '.sass', '.less'],
        'Java': ['.java'],
        'C/C++': ['.c', '.cpp', '.cc', '.h', '.hpp'],
        'Ruby': ['.rb'],
        'Go': ['.go'],
        'Rust': ['.rs'],
        'PHP': ['.php'],
        'C#': ['.cs'],
        'Shell': ['.sh', '.bash'],
        'JSON': ['.json'],
        'YAML': ['.yaml', '.yml'],
        'Markdown': ['.md', '.markdown'],
        'XML': ['.xml'],
        'SQL': ['.sql'],
    }
    
    # Regex patterns for import statements
    IMPORT_PATTERNS = {
        'Python': [
            r'^import\s+([\w.]+)',
            r'^from\s+([\w.]+)\s+import',
        ],
        'JavaScript': [
            r'import\s+[\w{}\s,*]+\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\)',
            r'export\s+\{?[\w,\s]*\}?\s+from\s+[\'"]([^\'"]+)[\'"]',
        ],
        'TypeScript': [
            r'import\s+[\w{}\s,*]+\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\)',
            r'export\s+\{?[\w,\s]*\}?\s+from\s+[\'"]([^\'"]+)[\'"]',
        ],
    }
    
    def __init__(self, repo_path: str):
        self.repo_path = os.path.abspath(repo_path)
        self.file_metadata = []
        self.language_counts = Counter()
        self.import_graph = defaultdict(set)
        
    def get_extension_language(self, extension: str) -> str:
        """Map a file extension to its language"""
        extension = extension.lower()
        for lang, exts in self.LANGUAGE_EXTENSIONS.items():
            if extension in exts:
                return lang
        return "Other"
        
    def count_lines(self, file_path: str) -> int:
        """Count the number of lines in a file"""
        try:
            with open(file_path, 'rb') as f:
                return sum(1 for _ in f)
        except Exception as e:
            print(f"Error counting lines in {file_path}: {e}")
            return 0
            
    def extract_imports(self, file_path: str, content: str, language: str) -> List[str]:
        """Extract import statements from file content based on language"""
        imports = []
        
        # Skip if language doesn't have defined patterns
        if language not in self.IMPORT_PATTERNS:
            return imports
            
        for pattern in self.IMPORT_PATTERNS[language]:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                if match.group(1):
                    imports.append(match.group(1))
                    # Add to import graph
                    self.import_graph[file_path].add(match.group(1))
                    
        return imports
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a single file to extract its metadata"""
        file_name = os.path.basename(file_path)
        extension = os.path.splitext(file_name)[1]
        language = self.get_extension_language(extension)
        
        try:
            # Get file stats
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size
            modified_time = datetime.datetime.fromtimestamp(file_stat.st_mtime)
            created_time = datetime.datetime.fromtimestamp(file_stat.st_ctime)
            
            # Count lines
            line_count = self.count_lines(file_path)
            
            # Extract imports
            imports = []
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                imports = self.extract_imports(file_path, content, language)
            
            # Update language counter
            self.language_counts[language] += 1
            
            # Create metadata record
            metadata = {
                'file_path': file_path,
                'file_name': file_name,
                'extension': extension,
                'language': language,
                'size_bytes': file_size,
                'line_count': line_count,
                'modified_time': modified_time.isoformat(),
                'created_time': created_time.isoformat(),
                'imports': ','.join(imports)
            }
            
            return metadata
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return {}
            
    def traverse_repository(self) -> None:
        """Traverse the repository and extract metadata from all files"""
        print(f"Scanning repository: {self.repo_path}")
        
        # Get all file extensions to analyze
        all_extensions = [ext for exts in self.LANGUAGE_EXTENSIONS.values() for ext in exts]
        
        # Walk through the repository
        for root, dirs, files in os.walk(self.repo_path):
            # Skip hidden directories like .git
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                file_path = os.path.join(root, file)
                extension = os.path.splitext(file)[1]
                
                # Skip hidden files and files without recognized extensions
                if file.startswith('.') or extension not in all_extensions:
                    continue
                    
                print(f"Processing: {file_path}")
                metadata = self.process_file(file_path)
                self.file_metadata.append(metadata)
    
    def generate_reports(self, output_dir: str = None) -> None:
        """Generate CSV and summary reports"""
        if output_dir is None:
            output_dir = self.repo_path
            
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate CSV report
        csv_path = os.path.join(output_dir, 'code_metadata.csv')
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            if self.file_metadata:
                fieldnames = self.file_metadata[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.file_metadata)
        
        print(f"CSV report generated: {csv_path}")
        
        # Generate summary report
        summary_path = os.path.join(output_dir, 'repo_summary.txt')
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"Repository Analysis Summary\n")
            f.write(f"=========================\n\n")
            f.write(f"Repository Path: {self.repo_path}\n")
            f.write(f"Analysis Date: {datetime.datetime.now().isoformat()}\n\n")
            
            f.write(f"File Count: {len(self.file_metadata)}\n\n")
            
            f.write(f"Language Distribution:\n")
            for language, count in self.language_counts.most_common():
                percentage = (count / len(self.file_metadata)) * 100 if self.file_metadata else 0
                f.write(f"  {language}: {count} files ({percentage:.1f}%)\n")
            
            f.write(f"\nTop 10 Largest Files:\n")
            largest_files = sorted(self.file_metadata, key=lambda x: x['size_bytes'], reverse=True)[:10]
            for file in largest_files:
                f.write(f"  {file['file_path']} - {file['size_bytes']/1024:.1f} KB\n")
                
            f.write(f"\nTop 10 Most Complex Files (by line count):\n")
            complex_files = sorted(self.file_metadata, key=lambda x: x['line_count'], reverse=True)[:10]
            for file in complex_files:
                f.write(f"  {file['file_path']} - {file['line_count']} lines\n")
        
        print(f"Summary report generated: {summary_path}")

def main():
    """Main function to run the metadata extractor"""
    # Get repository path from command line or use current directory
    import sys
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
    else:
        repo_path = os.getcwd()
    
    # Create and run extractor
    extractor = CodeMetadataExtractor(repo_path)
    extractor.traverse_repository()
    extractor.generate_reports()
    
if __name__ == "__main__":
    start_time = time.time()
    main()
    print(f"Total execution time: {time.time() - start_time:.2f} seconds")
