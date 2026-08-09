from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_get_metrics():
    metrics = {
        "total_reviews": 100,
        "cached_reviews": 40,
        "cache_hit_rate": 40.0,
        "providers": {
            "Groq": "available",
            "Gemini": "available",
        },
        "version": "1.0.0",
    }

    with patch(
        "backend.api.routes.metrics.metrics_service.get_metrics",
        return_value=metrics,
    ) as mock_get_metrics:

        response = client.get(
            "/api/v1/metrics"
        )

    assert response.status_code == 200
    assert response.json() == metrics

    mock_get_metrics.assert_called_once()


def test_get_metrics_returns_provider_status():
    metrics = {
        "total_reviews": 25,
        "cached_reviews": 10,
        "cache_hit_rate": 40.0,
        "providers": {
            "Groq": "available",
            "Gemini": "unavailable",
        },
        "version": "1.0.0",
    }

    with patch(
        "backend.api.routes.metrics.metrics_service.get_metrics",
        return_value=metrics,
    ):
        response = client.get(
            "/api/v1/metrics"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["providers"]["Groq"] == "available"
    assert data["providers"]["Gemini"] == "unavailable"


def test_get_metrics_returns_cache_statistics():
    metrics = {
        "total_reviews": 50,
        "cached_reviews": 20,
        "cache_hit_rate": 40.0,
        "providers": {
            "Groq": "available",
            "Gemini": "available",
        },
        "version": "1.0.0",
    }

    with patch(
        "backend.api.routes.metrics.metrics_service.get_metrics",
        return_value=metrics,
    ):
        response = client.get(
            "/api/v1/metrics"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["total_reviews"] == 50
    assert data["cached_reviews"] == 20
    assert data["cache_hit_rate"] == 40.0


def test_get_metrics_returns_application_version():
    metrics = {
        "total_reviews": 10,
        "cached_reviews": 5,
        "cache_hit_rate": 50.0,
        "providers": {
            "Groq": "available",
            "Gemini": "available",
        },
        "version": "2.0.0",
    }

    with patch(
        "backend.api.routes.metrics.metrics_service.get_metrics",
        return_value=metrics,
    ):
        response = client.get(
            "/api/v1/metrics"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["version"] == "2.0.0"