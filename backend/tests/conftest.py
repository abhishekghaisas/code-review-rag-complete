"""
Pytest configuration
Adds the parent directory to sys.path so tests can import app
"""

import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))