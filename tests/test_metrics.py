import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_metrics_exposure():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.get("/")
        metrics_response = await ac.get("/metrics")
    assert metrics_response.status_code == 200
    assert b"http_requests_total" in metrics_response.content
    assert b"/" in metrics_response.content or b"/metrics" in metrics_response.content