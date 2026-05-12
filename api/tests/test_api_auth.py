"""Testes do auth local (registro + login + /me)."""

import pytest


@pytest.mark.asyncio
async def test_registro_retorna_201(client):
    resp = await client.post("/auth/register", json={
        "email": "newuser@tenor.dev",
        "password": "senhasegura123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "token" in data
    assert data["email"] == "newuser@tenor.dev"


@pytest.mark.asyncio
async def test_registro_duplicado_retorna_409(client):
    await client.post("/auth/register", json={
        "email": "dup@tenor.dev", "password": "123456",
    })
    resp = await client.post("/auth/register", json={
        "email": "dup@tenor.dev", "password": "654321",
    })
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_correto(client):
    await client.post("/auth/register", json={
        "email": "login@tenor.dev", "password": "minhasenha",
    })
    resp = await client.post("/auth/login", json={
        "email": "login@tenor.dev", "password": "minhasenha",
    })
    assert resp.status_code == 200
    assert "token" in resp.json()


@pytest.mark.asyncio
async def test_login_senha_errada_retorna_401(client):
    await client.post("/auth/register", json={
        "email": "wrong@tenor.dev", "password": "correta",
    })
    resp = await client.post("/auth/login", json={
        "email": "wrong@tenor.dev", "password": "errada",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_com_token_valido(client):
    """GET /auth/me deve retornar o perfil do usuário autenticado."""
    resp = await client.get("/auth/me")
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
