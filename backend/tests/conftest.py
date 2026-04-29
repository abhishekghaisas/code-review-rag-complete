"""
Pytest configuration
Sets up test environment and fixtures
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from fastapi.testclient import TestClient

# Set test environment variables
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY", "test-key")
os.environ["DATABASE_URL"] = "sqlite:///:memory:"  # Use in-memory DB for tests
os.environ["CHROMA_DB_PATH"] = "./test_data/chroma_db"


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment before all tests"""
    # Create test data directory
    test_data_dir = Path("./test_data/chroma_db")
    test_data_dir.mkdir(parents=True, exist_ok=True)
    
    yield
    
    # Cleanup after tests
    import shutil
    if Path("./test_data").exists():
        shutil.rmtree("./test_data")


@pytest.fixture(scope="module")
def client():
    """Create a test client with proper initialization"""
    from app.main import app
    
    # Trigger startup event manually for tests
    with TestClient(app) as test_client:
        yield test_client