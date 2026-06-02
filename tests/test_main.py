from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_research_endpoint_requires_query():
    response = client.post("/research", json={})
    assert response.status_code == 422
