"""Testes do endpoint /auth/me."""

import pytest


@pytest.mark.asyncio
async def test_me_cria_perfil_no_primeiro_login(client):
    """Primeiro acesso deve criar o user_profile automaticamente."""
    resp = await client.get("/auth/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "00000000-0000-0000-0000-000000000001"
    assert data["nome"] is None


@pytest.mark.asyncio
async def test_me_idempotente(client):
    """Chamar /me várias vezes não cria perfis duplicados."""
    r1 = await client.get("/auth/me")
    r2 = await client.get("/auth/me")
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["id"] == r2.json()["id"]
