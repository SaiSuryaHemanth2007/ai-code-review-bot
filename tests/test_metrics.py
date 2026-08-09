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

from unittest.mock import patch

from backend.services.metrics_service import MetricsService


def test_get_metrics_calculates_cache_hit_rate():
    service = MetricsService()

    with patch(
        "backend.services.metrics_service.cache_db.get_total_reviews",
        return_value=20,
    ), patch(
        "backend.services.metrics_service.cache_db.get_cached_reviews",
        return_value=5,
    ), patch(
        "backend.services.metrics_service.groq_provider.health_check",
        return_value=True,
    ), patch(
        "backend.services.metrics_service.gemini_provider.health_check",
        return_value=False,
    ):

        result = service.get_metrics()

    assert result.total_reviews == 20
    assert result.cached_reviews == 5
    assert result.cache_hit_rate == 25.0
    assert result.providers.Groq == "available"
    assert result.providers.Gemini == "unavailable"

