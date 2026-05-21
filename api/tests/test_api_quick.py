"""
Testes do endpoint POST /contracts/quick — caminho de massa (3 campos).
"""

import pytest


@pytest.mark.asyncio
async def test_quick_retorna_201(client):
    resp = await client.post("/contracts/quick", json={
        "parcela_mensal": 6556.0,
        "banco": "itau",
        "saldo_devedor": 429629.87,
    })
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_quick_retorna_data_quitacao(client):
    resp = await client.post("/contracts/quick", json={
        "parcela_mensal": 6556.0,
        "banco": "itau",
        "saldo_devedor": 429629.87,
    })
    data = resp.json()
    assert "data_quitacao" in data
    assert data["data_quitacao"].startswith("20")


@pytest.mark.asyncio
async def test_quick_retorna_campos_estimados(client):
    resp = await client.post("/contracts/quick", json={
        "parcela_mensal": 6556.0,
        "banco": "itau",
        "saldo_devedor": 429629.87,
    })
    data = resp.json()
    assert "campos_estimados" in data
    assert "taxa_mensal" in data["campos_estimados"]
    assert "prazo_remanescente" in data["campos_estimados"]


@pytest.mark.asyncio
async def test_quick_taxa_estimada_razoavel(client):
    """Taxa estimada deve estar no range de mercado BR."""
    resp = await client.post("/contracts/quick", json={
        "parcela_mensal": 6556.0,
        "banco": "itau",
        "saldo_devedor": 429629.87,
    })
    data = resp.json()
    assert 0.003 < data["taxa_mensal"] < 0.018


@pytest.mark.asyncio
async def test_quick_prazo_estimado_razoavel(client):
    resp = await client.post("/contracts/quick", json={
        "parcela_mensal": 6556.0,
        "banco": "itau",
        "saldo_devedor": 429629.87,
    })
    data = resp.json()
    assert 100 < data["prazo_remanescente"] < 400


@pytest.mark.asyncio
async def test_quick_sistema_sac(client):
    resp = await client.post("/contracts/quick", json={
        "parcela_mensal": 1200.0,
        "banco": "caixa",
        "saldo_devedor": 150000.0,
    })
    assert resp.json()["sistema_amortizacao"] == "SAC"


@pytest.mark.asyncio
async def test_quick_parcela_total_coerente(client):
    """Parcela total calculada deve ser próxima da informada."""
    parcela_informada = 6556.0
    resp = await client.post("/contracts/quick", json={
        "parcela_mensal": parcela_informada,
        "banco": "itau",
        "saldo_devedor": 429629.87,
    })
    data = resp.json()
    # Pode divergir um pouco por causa de seguros estimados
    assert abs(data["parcela_total"] - parcela_informada) < 200.0


@pytest.mark.asyncio
async def test_quick_contrato_aparece_na_lista(client):
    """Contrato criado via quick deve aparecer na listagem."""
    await client.post("/contracts/quick", json={
        "parcela_mensal": 2000.0,
        "banco": "bb",
        "saldo_devedor": 200000.0,
    })
    resp = await client.get("/contracts")
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_quick_parcela_zero_retorna_422(client):
    resp = await client.post("/contracts/quick", json={
        "parcela_mensal": 0,
        "banco": "itau",
        "saldo_devedor": 429629.87,
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_quick_saldo_zero_retorna_422(client):
    resp = await client.post("/contracts/quick", json={
        "parcela_mensal": 6556.0,
        "banco": "itau",
        "saldo_devedor": 0,
    })
    assert resp.status_code == 422
