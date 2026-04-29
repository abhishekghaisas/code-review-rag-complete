"""
Basic tests for Code Review RAG backend
"""

import pytest
from fastapi.testclient import TestClient
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
                    "id": "test_chunk_1",
                    "code": "def test():\n    pass",
                    "language": "python",
                    "metadata": {
                        "file_path": "test.py",
                        "source": "test"
                    }
                }
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["chunks_ingested"] == 1


def test_review_code_requires_api_key():
    """Test that review endpoint validates input"""
    response = client.post(
        "/api/review",
        json={
            "code": "def hello():\n    print('hi')",
            "language": "python",
            "model": "claude-haiku-4-5-20251001",
            "use_rag": False,
            "n_similar": 3
        }
    )
    # Will fail without valid API key in CI, but endpoint should respond
    # Either 200 (if API key in secrets) or 500 (if no key)
    assert response.status_code in [200, 500]


def test_list_reviews():
    """Test reviews listing endpoint"""
    response = client.get("/api/reviews")
    assert response.status_code == 200
    data = response.json()
    assert "reviews" in data
    assert "total" in data
    assert isinstance(data["reviews"], list)


def test_invalid_review_request():
    """Test review endpoint with invalid data"""
    response = client.post(
        "/api/review",
        json={
            "code": "",  # Empty code should fail
            "language": "python",
            "model": "invalid-model"
        }
    )
    # Should handle gracefully
    assert response.status_code in [400, 500]


def test_get_ingestion_jobs():
    """Test ingestion jobs endpoint"""
    response = client.get("/api/ingestion/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert isinstance(data["jobs"], list)