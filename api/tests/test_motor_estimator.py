"""
Testes do estimador de campos faltantes.

Verifica que dado parcela + saldo, o estimador retorna valores
coerentes para taxa, amortização e prazo.
"""

import pytest

from motor.estimator import estimate_from_minimal


# ── Caso de referência (Thiago — Itaú SAC 12,19% a.a.) ──────────────────────

def test_estima_contrato_referencia():
    """
    Contrato real: parcela ~R$ 6.556, saldo R$ 429.629.
    Deve estimar taxa próxima de 0,96% a.m. e prazo ~189 meses.
    """
    result = estimate_from_minimal(parcela_mensal=6556.0, saldo_devedor=429629.87)

    # Taxa deve estar entre 0.7% e 1.2% (range razoável)
    assert 0.007 < result["taxa_mensal"] < 0.012

    # Prazo deve estar entre 120 e 300 meses
    assert 120 < result["prazo_remanescente"] < 300

    # Amortização deve ser positiva e menor que a parcela
    assert result["amortizacao_mensal"] > 0
    assert result["amortizacao_mensal"] < 6556.0


# ── Parcela pequena (Minha Casa) ─────────────────────────────────────────────

def test_estima_minha_casa():
    """
    Financiamento Minha Casa: parcela R$ 800, saldo R$ 120.000.
    Taxa deve ser menor (~0.5-0.7% a.m.).
    """
    result = estimate_from_minimal(parcela_mensal=800.0, saldo_devedor=120000.0)

    assert 0.003 < result["taxa_mensal"] < 0.010
    assert result["prazo_remanescente"] > 100
    assert result["sistema_amortizacao"] == "SAC"


# ── Financiamento caro ────────────────────────────────────────────────────────

def test_estima_taxa_alta():
    """
    Financiamento caro: parcela R$ 12.000, saldo R$ 500.000.
    Taxa deve ser mais alta (~1.2-1.5% a.m.).
    """
    result = estimate_from_minimal(parcela_mensal=12000.0, saldo_devedor=500000.0)

    assert 0.008 < result["taxa_mensal"] < 0.018
    assert result["prazo_remanescente"] > 30


# ── Quase quitado ────────────────────────────────────────────────────────────

def test_quase_quitado():
    """Parcela maior que saldo → prazo = 1."""
    result = estimate_from_minimal(parcela_mensal=5000.0, saldo_devedor=3000.0)

    assert result["prazo_remanescente"] == 1


# ── Coerência interna ────────────────────────────────────────────────────────

def test_parcela_reconstruida_bate():
    """
    A parcela reconstruída (amort + juros + seguros) deve ser
    próxima da parcela informada.
    """
    parcela_informada = 6556.0
    result = estimate_from_minimal(parcela_mensal=parcela_informada, saldo_devedor=429629.87)

    amort = result["amortizacao_mensal"]
    juros = 429629.87 * result["taxa_mensal"]
    seguros_est = parcela_informada * 0.02  # mesma heurística do estimador
    parcela_reconstruida = amort + juros + seguros_est

    # Deve bater com margem de R$ 50
    assert abs(parcela_reconstruida - parcela_informada) < 50.0


def test_campos_completos():
    """O retorno tem todos os campos necessários para criar contrato."""
    result = estimate_from_minimal(parcela_mensal=2000.0, saldo_devedor=200000.0)

    assert "taxa_mensal" in result
    assert "amortizacao_mensal" in result
    assert "prazo_remanescente" in result
    assert "sistema_amortizacao" in result
    assert "data_proxima_parcela" in result
    assert "mip_mensal" in result
    assert "dfi_mensal" in result


def test_sistema_sempre_sac():
    """Estimador assume SAC (85% do mercado BR)."""
    result = estimate_from_minimal(parcela_mensal=3000.0, saldo_devedor=300000.0)
    assert result["sistema_amortizacao"] == "SAC"


# ── Erros ─────────────────────────────────────────────────────────────────────

def test_parcela_zero_levanta_erro():
    with pytest.raises(ValueError):
        estimate_from_minimal(parcela_mensal=0, saldo_devedor=100000)


def test_saldo_zero_levanta_erro():
    with pytest.raises(ValueError):
        estimate_from_minimal(parcela_mensal=1000, saldo_devedor=0)


def test_valores_negativos():
    with pytest.raises(ValueError):
        estimate_from_minimal(parcela_mensal=-500, saldo_devedor=100000)
