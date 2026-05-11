"""Testes de integração para cenários — CRUD + projeções do motor."""

import pytest


# ── Criar cenário ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_criar_cenario_retorna_201(client, contract):
    resp = await client.post(
        f"/contracts/{contract['id']}/scenarios",
        json={"nome": "5k/mes", "aporte_mensal_extra": 5000},
    )
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_criar_cenario_inclui_projecao(client, contract):
    resp = await client.post(
        f"/contracts/{contract['id']}/scenarios",
        json={"nome": "5k/mes", "aporte_mensal_extra": 5000},
    )
    data = resp.json()
    assert "projecao" in data
    assert data["projecao"]["data_quitacao"] is not None
    assert data["projecao"]["total_juros_economizados"] > 0


@pytest.mark.asyncio
async def test_cenario_5k_antecipa_quitacao(client, contract):
    """5k/mês extra deve antecipar significativamente a quitação."""
    resp = await client.post(
        f"/contracts/{contract['id']}/scenarios",
        json={"nome": "5k/mes", "aporte_mensal_extra": 5000},
    )
    projecao = resp.json()["projecao"]
    data_base = contract["data_quitacao"]
    data_cenario = projecao["data_quitacao"]
    assert data_cenario < data_base


@pytest.mark.asyncio
async def test_cenario_5k_60k_quita_em_2029(client, contract):
    """
    5k/mês + 60k/ano em abril deve quitar por volta de abril/2029.
    Validado contra os dados reais da conversa de origem.
    """
    resp = await client.post(
        f"/contracts/{contract['id']}/scenarios",
        json={
            "nome": "otimizado",
            "aporte_mensal_extra": 5000,
            "aporte_anual_extra": 60000,
            "mes_aporte_anual": 4,
        },
    )
    data_quitacao = resp.json()["projecao"]["data_quitacao"]
    year = int(data_quitacao[:4])
    assert year in [2028, 2029, 2030]


@pytest.mark.asyncio
async def test_cenario_economia_positiva(client, contract):
    """Qualquer aporte extra deve economizar juros."""
    resp = await client.post(
        f"/contracts/{contract['id']}/scenarios",
        json={"nome": "teste", "aporte_mensal_extra": 1000},
    )
    assert resp.json()["projecao"]["total_juros_economizados"] > 0


@pytest.mark.asyncio
async def test_criar_cenario_sem_extras(client, contract):
    """Cenário sem aportes deve ter economia zero."""
    resp = await client.post(
        f"/contracts/{contract['id']}/scenarios",
        json={"nome": "base", "aporte_mensal_extra": 0},
    )
    assert resp.json()["projecao"]["total_juros_economizados"] == pytest.approx(0, abs=1)


# ── Listar cenários ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_listar_cenarios_vazio(client, contract):
    resp = await client.get(f"/contracts/{contract['id']}/scenarios")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_listar_cenarios_retorna_criados(client, contract, scenario):
    resp = await client.get(f"/contracts/{contract['id']}/scenarios")
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == scenario["id"]


# ── Atualizar cenário ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_atualizar_cenario_muda_projecao(client, contract, scenario):
    """Aumentar o aporte deve antecipar mais a quitação."""
    data_antes = scenario["projecao"]["data_quitacao"]

    resp = await client.patch(
        f"/scenarios/{scenario['id']}",
        json={"aporte_mensal_extra": 10000},
    )
    assert resp.status_code == 200
    data_depois = resp.json()["projecao"]["data_quitacao"]
    assert data_depois < data_antes


@pytest.mark.asyncio
async def test_atualizar_status_cenario(client, contract, scenario):
    resp = await client.patch(
        f"/scenarios/{scenario['id']}",
        json={"status": "em_execucao"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "em_execucao"


@pytest.mark.asyncio
async def test_atualizar_status_invalido(client, contract, scenario):
    resp = await client.patch(
        f"/scenarios/{scenario['id']}",
        json={"status": "inexistente"},
    )
    assert resp.status_code == 422


# ── Deletar cenário ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_deletar_cenario(client, contract, scenario):
    resp = await client.delete(f"/scenarios/{scenario['id']}")
    assert resp.status_code == 204
    # Confirma que sumiu
    resp = await client.get(f"/contracts/{contract['id']}/scenarios")
    assert resp.json() == []
