"""
Pytest configuration
Sets up test environment with mock API key
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

# Set test environment variables BEFORE importing app
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY") or "sk-ant-test-key-for-ci-testing-only"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["CHROMA_DB_PATH"] = "./test_data/chroma_db"


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment"""
    test_data_dir = Path("./test_data/chroma_db")
    test_data_dir.mkdir(parents=True, exist_ok=True)
    
    yield
    
    # Cleanup
    import shutil
    if Path("./test_data").exists():
        shutil.rmtree("./test_data", ignore_errors=True)


@pytest.fixture(scope="module")
def client():
    """Create test client"""
    from app.main import app
    
    with TestClient(app) as test_client:
        yield test_client