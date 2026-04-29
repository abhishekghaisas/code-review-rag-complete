"""
Simplified GitHub Repository Ingestion - No tree-sitter dependency
"""

import os
import tempfile
import shutil
from typing import List, Dict
from git import Repo

class GitHubIngestion:
    def __init__(self):
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php'
        }
    
    def ingest_repository(self, repo_url: str) -> List[Dict[str, str]]:
        """Clone and extract code from a GitHub repository"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Clone the repository
            print(f"Cloning repository: {repo_url}")
            repo = Repo.clone_from(repo_url, temp_dir, depth=1)
            
            # Extract code files
            code_files = self._extract_code_files(temp_dir)
            
            print(f"Found {len(code_files)} code files")
            return code_files
        
        finally:
            # Cleanup
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    def _extract_code_files(self, repo_path: str) -> List[Dict[str, str]]:
        """Extract all code files from repository"""
        code_files = []
        
        for root, dirs, files in os.walk(repo_path):
            # Skip common non-code directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
                'node_modules', '__pycache__', 'venv', 'env', 'dist', 'build', 'target'
            ]]
            
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext in self.supported_extensions:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        # Only include files < 100KB
                        if len(content) < 100000:
                            code_files.append({
                                "filename": file,
                                "filepath": file_path.replace(repo_path, ''),
                                "language": self.supported_extensions[ext],
                                "code": content,
                                "size": len(content)
                            })
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
                        continue
        
        return code_files
    
    def chunk_code_file(self, code: str, language: str) -> List[str]:
        """Simple code chunking by line count"""
        lines = code.split('\n')
        chunks = []
        chunk_size = 50
        
        for i in range(0, len(lines), chunk_size):
            chunk = '\n'.join(lines[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks