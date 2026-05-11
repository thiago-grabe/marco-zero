"""Testes de integração para /operations — registrar amortizações."""

import pytest


@pytest.mark.asyncio
async def test_registrar_amortizacao_prazo(client, contract):
    resp = await client.post(
        f"/contracts/{contract['id']}/operations",
        json={
            "tipo": "amortizacao_prazo",
            "data_operacao": "2026-06-01",
            "valor_principal": 30000,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["tipo"] == "amortizacao_prazo"
    assert data["valor_principal"] == pytest.approx(30000.0)


@pytest.mark.asyncio
async def test_amortizacao_atualiza_saldo(client, contract):
    """Após registrar amortização, GET /contracts/:id deve mostrar saldo menor."""
    saldo_antes = contract["saldo_devedor"]

    await client.post(
        f"/contracts/{contract['id']}/operations",
        json={
            "tipo": "amortizacao_prazo",
            "data_operacao": "2026-06-01",
            "valor_principal": 30000,
        },
    )

    resp = await client.get(f"/contracts/{contract['id']}")
    saldo_depois = resp.json()["saldo_devedor"]
    assert saldo_depois < saldo_antes
    # abs=2000 para cobrir juros pró-rata (operação em 01/06, vencimento 21/05 → 11 dias)
    assert saldo_depois == pytest.approx(saldo_antes - 30000, abs=2000)


@pytest.mark.asyncio
async def test_amortizacao_prazo_antecipa_quitacao(client, contract):
    """Amortização com redução de prazo deve antecipar data_quitacao."""
    data_antes = contract["data_quitacao"]

    await client.post(
        f"/contracts/{contract['id']}/operations",
        json={
            "tipo": "amortizacao_prazo",
            "data_operacao": "2026-06-01",
            "valor_principal": 30000,
        },
    )

    resp = await client.get(f"/contracts/{contract['id']}")
    data_depois = resp.json()["data_quitacao"]
    assert data_depois < data_antes


@pytest.mark.asyncio
async def test_listar_operacoes_apos_registro(client, contract):
    await client.post(
        f"/contracts/{contract['id']}/operations",
        json={
            "tipo": "amortizacao_prazo",
            "data_operacao": "2026-06-01",
            "valor_principal": 10000,
        },
    )
    resp = await client.get(f"/contracts/{contract['id']}/operations")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_operacao_com_notas(client, contract):
    resp = await client.post(
        f"/contracts/{contract['id']}/operations",
        json={
            "tipo": "amortizacao_parcela",
            "data_operacao": "2026-07-01",
            "valor_principal": 5000,
            "notas": "PLR de julho",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["notas"] == "PLR de julho"


@pytest.mark.asyncio
async def test_operacao_tipo_invalido_retorna_422(client, contract):
    resp = await client.post(
        f"/contracts/{contract['id']}/operations",
        json={
            "tipo": "tipo_inexistente",
            "data_operacao": "2026-06-01",
            "valor_principal": 5000,
        },
    )
    assert resp.status_code == 422
