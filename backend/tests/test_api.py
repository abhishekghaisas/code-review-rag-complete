"""
Basic tests for Code Review RAG backend
Run with: pytest tests/ -v
"""

import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient

# Now we can import app
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "endpoints" in data


def test_get_models():
    """Test models endpoint"""
    response = client.get("/api/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) > 0
    
    # Check model structure
    first_model = data["models"][0]
    assert "id" in first_model
    assert "name" in first_model
    assert "cost" in first_model


def test_get_stats():
    """Test stats endpoint"""
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "collection_name" in data
    assert "total_chunks" in data
    assert "embedding_model" in data
    assert "embedding_dimension" in data


def test_ingest_code():
    """Test code ingestion"""
    response = client.post(
        "/api/ingest",
        json={
            "code_chunks": [
                {
                    "id": "test_chunk_ci",
                    "code": "def test():\n    pass",
                    "language": "python",
                    "metadata": {
                        "file_path": "test.py",
                        "source": "ci_test"
                    }
                }
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["chunks_ingested"] == 1


def test_list_reviews():
    """Test reviews listing endpoint"""
    response = client.get("/api/reviews")
    assert response.status_code == 200
    data = response.json()
    assert "reviews" in data
    assert "total" in data
    assert isinstance(data["reviews"], list)


def test_get_ingestion_jobs():
    """Test ingestion jobs endpoint"""
    response = client.get("/api/ingestion/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert isinstance(data["jobs"], list)


# Note: We skip testing actual code review in CI unless API key is provided
# This prevents failures when running in CI without secrets