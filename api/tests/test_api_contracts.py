"""Testes de integração para /contracts — CRUD + campos computados."""

import pytest

from tests.conftest import CONTRACT_PAYLOAD


# ── Criar contrato ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_criar_contrato_retorna_201(client):
    resp = await client.post("/contracts", json=CONTRACT_PAYLOAD)
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_criar_contrato_campos_obrigatorios(client):
    resp = await client.post("/contracts", json=CONTRACT_PAYLOAD)
    data = resp.json()
    assert data["banco"] == "itau"
    assert data["sistema_amortizacao"] == "SAC"
    assert data["prazo_remanescente"] == 189


@pytest.mark.asyncio
async def test_criar_contrato_campos_computados(client):
    """Motor deve calcular taxa_anual, parcela_total e data_quitacao."""
    resp = await client.post("/contracts", json=CONTRACT_PAYLOAD)
    data = resp.json()

    assert data["taxa_anual_efetiva"] == pytest.approx(0.1219, abs=0.001)
    assert data["seguros_mensal"] == pytest.approx(133.06, abs=0.10)
    assert data["data_quitacao"] is not None
    assert data["data_quitacao"].startswith("20")  # formato ISO


@pytest.mark.asyncio
async def test_criar_contrato_data_quitacao_correta(client):
    """Sem extras, quitação deve ser em ~dez/2041 (189 meses a partir de mai/2026)."""
    resp = await client.post("/contracts", json=CONTRACT_PAYLOAD)
    data = resp.json()
    year = int(data["data_quitacao"][:4])
    assert 2041 <= year <= 2042


@pytest.mark.asyncio
async def test_criar_contrato_taxa_invalida_retorna_422(client):
    payload = {**CONTRACT_PAYLOAD, "taxa_mensal": 0.25}  # 25% ao mês — irreal
    resp = await client.post("/contracts", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_criar_contrato_amort_maior_que_saldo_retorna_422(client):
    payload = {**CONTRACT_PAYLOAD, "amortizacao_mensal": 500000}
    resp = await client.post("/contracts", json=payload)
    assert resp.status_code == 422


# ── Listar contratos ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_listar_contratos_vazio(client):
    resp = await client.get("/contracts")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_listar_contratos_retorna_criado(client, contract):
    resp = await client.get("/contracts")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == contract["id"]


# ── Buscar contrato ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_buscar_contrato_por_id(client, contract):
    resp = await client.get(f"/contracts/{contract['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == contract["id"]


@pytest.mark.asyncio
async def test_buscar_contrato_inexistente_retorna_404(client):
    resp = await client.get("/contracts/00000000-0000-0000-0000-000000000999")
    assert resp.status_code == 404


# ── Atualizar contrato ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_atualizar_saldo(client, contract):
    resp = await client.patch(
        f"/contracts/{contract['id']}",
        json={"saldo_devedor": 400000.0},
    )
    assert resp.status_code == 200
    assert resp.json()["saldo_devedor"] == pytest.approx(400000.0)


@pytest.mark.asyncio
async def test_atualizar_saldo_recalcula_data_quitacao(client, contract):
    """Reduzir o saldo deve antecipar a data de quitação."""
    data_antes = contract["data_quitacao"]
    resp = await client.patch(
        f"/contracts/{contract['id']}",
        json={"saldo_devedor": 300000.0},
    )
    data_depois = resp.json()["data_quitacao"]
    assert data_depois < data_antes


# ── Deletar contrato ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_deletar_contrato(client, contract):
    resp = await client.delete(f"/contracts/{contract['id']}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_deletar_contrato_some_da_lista(client, contract):
    await client.delete(f"/contracts/{contract['id']}")
    resp = await client.get("/contracts")
    assert resp.json() == []


# ── Isolamento de usuário ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_usuario_nao_ve_contratos_de_outro(client, contract):
    """
    Com RLS ativo, outro user_id não deveria ver os contratos.
    Neste teste, simulamos apenas que o usuário logado vê os seus.
    """
    resp = await client.get("/contracts")
    for c in resp.json():
        # Todos os contratos retornados devem ser do usuário de teste
        assert c["id"] == contract["id"]
