from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_metrics_endpoint():
    response = client.get("/api/v1/metrics")

    assert response.status_code == 200

    data = response.json()

    assert "total_reviews" in data
    assert "cached_reviews" in data
    assert "cache_hit_rate" in data
    assert "providers" in data
    assert "version" in data

    assert "Groq" in data["providers"]
    assert "Gemini" in data["providers"]