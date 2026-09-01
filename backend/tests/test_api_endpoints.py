import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_project_and_list():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create project
        resp = await ac.post("/api/projects", json={
            "name": "Test Domain",
            "base_url": "https://example.com",
            "description": "Integration test project"
        })
        assert resp.status_code == 201
        project_data = resp.json()
        assert project_data["name"] == "Test Domain"
        project_id = project_data["id"]

        # List projects
        list_resp = await ac.get("/api/projects")
        assert list_resp.status_code == 200
        projects = list_resp.json()
        assert any(p["id"] == project_id for p in projects)

        # Delete project
        del_resp = await ac.delete(f"/api/projects/{project_id}")
        assert del_resp.status_code == 204
