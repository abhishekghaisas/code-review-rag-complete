"""
GitHub Repository Ingestion
Clones repositories and extracts code for RAG ingestion
"""

import os
import tempfile
import shutil
from typing import List, Dict, Optional
from pathlib import Path
import git
import logging

logger = logging.getLogger(__name__)


class GitHubIngestion:
    """Handle GitHub repository ingestion"""
    
    # Supported file extensions by language
    LANGUAGE_EXTENSIONS = {
        'python': ['.py'],
        'javascript': ['.js', '.jsx', '.mjs'],
        'typescript': ['.ts', '.tsx'],
        'java': ['.java'],
        'go': ['.go'],
        'rust': ['.rs'],
        'cpp': ['.cpp', '.cc', '.cxx', '.hpp', '.h'],
        'c': ['.c', '.h'],
        'ruby': ['.rb'],
        'php': ['.php'],
        'swift': ['.swift'],
        'kotlin': ['.kt', '.kts'],
        'scala': ['.scala'],
        'r': ['.r', '.R'],
        'shell': ['.sh', '.bash'],
        'sql': ['.sql'],
        'html': ['.html', '.htm'],
        'css': ['.css', '.scss', '.sass'],
        'markdown': ['.md', '.markdown'],
    }
    
    # Files/directories to ignore
    IGNORE_PATTERNS = {
        # Directories
        'node_modules', '.git', '__pycache__', '.venv', 'venv', 'env',
        'build', 'dist', 'target', '.idea', '.vscode', '.next',
        'coverage', '.pytest_cache', '.tox', 'eggs', '.eggs',
        # Files
        '.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib',
        '.class', '.log', '.lock', 'package-lock.json', 'yarn.lock',
    }
    
    def __init__(self, max_file_size_mb: int = 1):
        """
        Initialize GitHub ingestion
        
        Args:
            max_file_size_mb: Maximum file size to process (in MB)
        """
        self.max_file_size = max_file_size_mb * 1024 * 1024  # Convert to bytes
    
    def clone_repository(self, repo_url: str, target_dir: Optional[str] = None) -> str:
        """
        Clone a GitHub repository
        
        Args:
            repo_url: GitHub repository URL
            target_dir: Optional target directory (uses temp dir if not provided)
            
        Returns:
            Path to cloned repository
        """
        if target_dir is None:
            target_dir = tempfile.mkdtemp(prefix='repo_')
        
        logger.info(f"Cloning repository: {repo_url} to {target_dir}")
        
        try:
            git.Repo.clone_from(repo_url, target_dir, depth=1)
            logger.info(f"Successfully cloned repository to {target_dir}")
            return target_dir
        except Exception as e:
            logger.error(f"Failed to clone repository: {str(e)}")
            raise Exception(f"Failed to clone repository: {str(e)}")
    
    def should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed"""
        # Check if any ignore pattern matches
        for pattern in self.IGNORE_PATTERNS:
            if pattern in str(file_path):
                return False
        
        # Check file size
        try:
            if file_path.stat().st_size > self.max_file_size:
                logger.debug(f"Skipping large file: {file_path}")
                return False
        except:
            return False
        
        # Check if it's a supported code file
        extension = file_path.suffix.lower()
        for lang, extensions in self.LANGUAGE_EXTENSIONS.items():
            if extension in extensions:
                return True
        
        return False
    
    def detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension"""
        extension = file_path.suffix.lower()
        
        for lang, extensions in self.LANGUAGE_EXTENSIONS.items():
            if extension in extensions:
                return lang
        
        return 'text'
    
    def extract_code_files(self, repo_path: str) -> List[Dict[str, str]]:
        """
        Extract all code files from repository
        
        Args:
            repo_path: Path to cloned repository
            
        Returns:
            List of code files with metadata
        """
        code_files = []
        repo_root = Path(repo_path)
        
        logger.info(f"Extracting code files from: {repo_path}")
        
        for file_path in repo_root.rglob('*'):
            if not file_path.is_file():
                continue
            
            if not self.should_process_file(file_path):
                continue
            
            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Skip empty files
                if not content.strip():
                    continue
                
                # Get relative path from repo root
                relative_path = file_path.relative_to(repo_root)
                
                code_files.append({
                    'path': str(relative_path),
                    'content': content,
                    'language': self.detect_language(file_path),
                    'size': file_path.stat().st_size,
                })
                
            except Exception as e:
                logger.warning(f"Failed to read file {file_path}: {str(e)}")
                continue
        
        logger.info(f"Extracted {len(code_files)} code files")
        return code_files
    
    def chunk_code(
        self,
        content: str,
        chunk_size: int = 1000,
        overlap: int = 100
    ) -> List[str]:
        """
        Chunk code into smaller pieces with overlap
        
        Args:
            content: Code content
            chunk_size: Maximum characters per chunk
            overlap: Characters to overlap between chunks
            
        Returns:
            List of code chunks
        """
        if len(content) <= chunk_size:
            return [content]
        
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + chunk_size
            chunk = content[start:end]
            
            # Try to break at newline
            if end < len(content):
                last_newline = chunk.rfind('\n')
                if last_newline > chunk_size * 0.7:  # Only if newline is in last 30%
                    end = start + last_newline + 1
                    chunk = content[start:end]
            
            chunks.append(chunk)
            start = end - overlap if end < len(content) else end
        
        return chunks
    
    def process_repository(
        self,
        repo_url: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 100
    ) -> List[Dict[str, any]]:
        """
        Process entire repository: clone, extract, chunk
        
        Args:
            repo_url: GitHub repository URL
            chunk_size: Maximum characters per chunk
            chunk_overlap: Characters to overlap between chunks
            
        Returns:
            List of code chunks ready for ingestion
        """
        temp_dir = None
        
        try:
            # Clone repository
            temp_dir = self.clone_repository(repo_url)
            
            # Extract code files
            code_files = self.extract_code_files(temp_dir)
            
            # Process each file into chunks
            all_chunks = []
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            
            for file_data in code_files:
                # Chunk the file content
                chunks = self.chunk_code(
                    file_data['content'],
                    chunk_size=chunk_size,
                    overlap=chunk_overlap
                )
                
                # Create chunk objects
                for idx, chunk in enumerate(chunks):
                    chunk_id = f"{repo_name}_{file_data['path']}_{idx}".replace('/', '_').replace('.', '_')
                    
                    all_chunks.append({
                        'id': chunk_id,
                        'code': chunk,
                        'language': file_data['language'],
                        'metadata': {
                            'file_path': file_data['path'],
                            'repo': repo_name,
                            'repo_url': repo_url,
                            'chunk_index': idx,
                            'total_chunks': len(chunks),
                            'file_size': file_data['size'],
                        }
                    })
            
            logger.info(f"Processed repository into {len(all_chunks)} chunks")
            return all_chunks
            
        finally:
            # Cleanup temporary directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.info(f"Cleaned up temporary directory: {temp_dir}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup {temp_dir}: {str(e)}")


# Example usage
if __name__ == "__main__":
    ingestion = GitHubIngestion()
    
    # Test with a small repo
    repo_url = "https://github.com/psf/requests"
    chunks = ingestion.process_repository(repo_url)
    
    print(f"Total chunks: {len(chunks)}")
    print(f"\nFirst chunk:")
    print(chunks[0])
