from unittest.mock import patch

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from backend.core.exception_handler import (
    register_exception_handlers,
)


def test_generic_exception_handler_returns_500():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/test-error")
    async def test_error():
        raise Exception("Unexpected failure")

    client = TestClient(app, raise_server_exceptions=False)

    with patch(
        "backend.core.exception_handler.logger.exception"
    ) as mock_logger:
        response = client.get("/test-error")

    assert response.status_code == 500

    data = response.json()

    assert data["error"] == "Internal Server Error"
    assert data["message"] == (
        "An unexpected error occurred."
    )

    mock_logger.assert_called_once()


def test_http_exception_handler_returns_error_response():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/test-http-error")
    async def test_http_error():
        raise HTTPException(
            status_code=404,
            detail="Resource not found.",
        )

    client = TestClient(app)

    response = client.get("/test-http-error")

    assert response.status_code == 404

    data = response.json()

    assert data["error"] == "HTTP Error"
    assert data["message"] == "Resource not found."