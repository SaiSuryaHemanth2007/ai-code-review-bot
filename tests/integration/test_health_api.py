from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_get_health_returns_healthy_status():
    health_response = {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "groq": True,
            "gemini": True,
            "cache": True,
            "database": True,
            "github": True,
        },
    }

    with patch(
        "backend.api.routes.health.health_service.get_health",
        return_value=health_response,
    ) as mock_get_health:

        response = client.get(
            "/api/v1/health"
        )

    assert response.status_code == 200
    assert response.json() == health_response

    mock_get_health.assert_called_once()


def test_get_health_reports_unavailable_services():
    health_response = {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "groq": False,
            "gemini": True,
            "cache": True,
            "database": True,
            "github": False,
        },
    }

    with patch(
        "backend.api.routes.health.health_service.get_health",
        return_value=health_response,
    ) as mock_get_health:

        response = client.get(
            "/api/v1/health"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["services"]["groq"] is False
    assert data["services"]["gemini"] is True
    assert data["services"]["github"] is False

    mock_get_health.assert_called_once()


def test_get_health_calls_health_service():
    health_response = {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "groq": True,
            "gemini": True,
            "cache": True,
            "database": True,
            "github": True,
        },
    }

    with patch(
        "backend.api.routes.health.health_service.get_health",
        return_value=health_response,
    ) as mock_get_health:

        response = client.get(
            "/api/v1/health"
        )

    assert response.status_code == 200
    assert response.json() == health_response

    mock_get_health.assert_called_once()