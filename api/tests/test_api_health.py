"""Testes básicos de disponibilidade da API."""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from main import app


@pytest_asyncio.fixture
async def bare_client():
    """Cliente sem auth override — testa endpoints públicos."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_health(bare_client: AsyncClient):
    resp = await bare_client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_health_tem_versao(bare_client: AsyncClient):
    resp = await bare_client.get("/health")
    assert "version" in resp.json()


@pytest.mark.asyncio
async def test_openapi_disponivel(bare_client: AsyncClient):
    resp = await bare_client.get("/openapi.json")
    assert resp.status_code == 200
    assert "paths" in resp.json()


@pytest.mark.asyncio
async def test_rota_inexistente_retorna_404(bare_client: AsyncClient):
    """Rota não cadastrada deve retornar 404."""
    resp = await bare_client.get("/rota-que-nao-existe")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_motor_project_sem_auth_retorna_422_ou_200(bare_client: AsyncClient):
    """Endpoint do motor não requer auth — retorna 422 por body inválido (não 401)."""
    resp = await bare_client.post("/motor/project", json={})
    assert resp.status_code == 422
