"""
Basic tests for Code Review RAG backend
"""

import pytest


def test_health_check(client):
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "endpoints" in data


def test_get_models(client):
    """Test models endpoint"""
    response = client.get("/api/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) > 0
    
    first_model = data["models"][0]
    assert "id" in first_model
    assert "name" in first_model
    assert "cost" in first_model


def test_get_stats(client):
    """Test stats endpoint"""
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "collection_name" in data
    assert "total_chunks" in data
    assert "embedding_model" in data
    assert "embedding_dimension" in data


def test_ingest_code(client):
    """Test code ingestion"""
    response = client.post(
        "/api/ingest",
        json={
            "code_chunks": [
                {
                    "id": "test_ci_chunk",
                    "code": "def ci_test():\n    return True",
                    "language": "python",
                    "metadata": {
                        "file_path": "ci_test.py",
                        "source": "ci"
                    }
                }
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["chunks_ingested"] == 1


def test_list_reviews(client):
    """Test reviews listing endpoint"""
    response = client.get("/api/reviews")
    assert response.status_code == 200
    data = response.json()
    assert "reviews" in data
    assert "total" in data
    assert isinstance(data["reviews"], list)


def test_get_ingestion_jobs(client):
    """Test ingestion jobs endpoint"""
    response = client.get("/api/ingestion/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert isinstance(data["jobs"], list)