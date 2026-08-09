from fastapi.testclient import TestClient

from backend.main import app, lifespan


def test_root_endpoint():
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["application"] is not None
    assert data["version"] is not None
    assert "debug" in data


def test_lifespan():
    async def run_lifespan():
        async with lifespan(app):
            pass

    import asyncio

    asyncio.run(run_lifespan())