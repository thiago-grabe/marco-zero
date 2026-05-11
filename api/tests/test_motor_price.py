"""Testes do motor PRICE."""

import math
from datetime import date

import pytest

from motor.price import compute_balance_at, compute_installment, compute_pmt


# ── PMT ────────────────────────────────────────────────────────────────────────

def test_pmt_formula_basica():
    """PMT deve ser constante ao longo do contrato."""
    pmt = compute_pmt(pv=100_000, taxa_mensal=0.01, n=120)
    assert pmt == pytest.approx(1434.71, abs=0.10)


def test_pmt_taxa_zero():
    """Taxa zero → PMT = PV / n."""
    pmt = compute_pmt(pv=120_000, taxa_mensal=0.0, n=120)
    assert pmt == pytest.approx(1000.0, abs=0.01)


def test_pmt_parcela_menor_que_sac():
    """
    PRICE tem parcela menor que SAC nas primeiras parcelas.
    Parcela SAC inicial = amort + juros = (pv/n) + (pv * taxa).
    """
    pv, taxa, n = 100_000, 0.01, 120
    pmt_price = compute_pmt(pv, taxa, n)
    parcela_sac_inicial = (pv / n) + (pv * taxa)
    assert pmt_price < parcela_sac_inicial


# ── Saldo residual ─────────────────────────────────────────────────────────────

def test_balance_at_zero_pagamentos():
    """Antes do primeiro pagamento, saldo = PV."""
    saldo = compute_balance_at(pv=100_000, taxa_mensal=0.01, n=120, k=0)
    assert saldo == pytest.approx(100_000, abs=0.01)


def test_balance_at_quitacao():
    """Após n pagamentos, saldo deve ser ~0."""
    saldo = compute_balance_at(pv=100_000, taxa_mensal=0.01, n=120, k=120)
    assert abs(saldo) < 0.10


def test_balance_decresce():
    """Saldo deve decrescer a cada pagamento."""
    for k in range(0, 120, 10):
        s_k = compute_balance_at(100_000, 0.01, 120, k)
        s_k10 = compute_balance_at(100_000, 0.01, 120, k + 10)
        assert s_k > s_k10


# ── Parcela ────────────────────────────────────────────────────────────────────

def test_compute_installment_total_consistente():
    """amort + juros + seguros = total."""
    result = compute_installment(100_000, 50, 0.01, mip=50, dfi=20)
    assert result["total"] == pytest.approx(
        result["amortizacao"] + result["juros"] + result["seguros"], abs=0.01
    )


def test_compute_installment_juros_primeira_parcela():
    """Juros da 1ª parcela PRICE = saldo * taxa."""
    result = compute_installment(100_000, 120, 0.01, mip=0, dfi=0)
    assert result["juros"] == pytest.approx(100_000 * 0.01, abs=0.01)


def test_compute_installment_amortizacao_positiva():
    """Amortização deve ser positiva — dívida decrescente."""
    result = compute_installment(100_000, 120, 0.01, mip=0, dfi=0)
    assert result["amortizacao"] > 0
