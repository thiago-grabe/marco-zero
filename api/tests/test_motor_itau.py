"""Testes do modo Itaú — manutenção de prestação."""

from datetime import date

import pytest

from motor.itau import detect_itau_mode, simulate_amortization


# ── Detecção de modo ───────────────────────────────────────────────────────────

def test_detecta_modo_itau():
    """
    Itaú: amortização sobe >20%, parcela cai <5%.
    Observado empiricamente no contrato de referência.
    """
    assert detect_itau_mode(
        amortizacao_anterior=1514.32,
        amortizacao_nova=2285.27,
        parcela_anterior=6594.59,
        parcela_nova=6578.27,
    ) is True


def test_nao_detecta_sac_padrao():
    """SAC padrão: parcela cai significativamente."""
    assert detect_itau_mode(
        amortizacao_anterior=1514.32,
        amortizacao_nova=1514.32,
        parcela_anterior=6594.59,
        parcela_nova=5713.00,  # cai ~13% → não é modo Itaú
    ) is False


def test_nao_detecta_sem_dados():
    """Sem dados anteriores, não detecta."""
    assert detect_itau_mode(0, 2285.27, 6594.59, 6578.27) is False


# ── Simulação ──────────────────────────────────────────────────────────────────

def test_simulate_saldo_reduz():
    """
    Saldo deve reduzir após amortização.
    saldo_novo = saldo - amort + juros_pro_rata + TR
    7 dias de pro-rata: 429629 × 0.9631% × (7/30) ≈ R$ 965
    """
    result = simulate_amortization(
        saldo=429629.87,
        prazo_remanescente=189,
        taxa_mensal=0.009631393,
        mip_mensal=94.45,
        dfi_mensal=38.61,
        parcela_total_anterior=6578.27,
        data_ultimo_vencimento=date(2026, 4, 21),
        data_operacao=date(2026, 4, 28),
        valor_amort=80000.0,
    )
    assert result["saldo_novo"] < 429629.87
    # abs=1500 para cobrir juros pró-rata dos 7 dias (~R$ 965)
    assert result["saldo_novo"] == pytest.approx(429629.87 - 80000.0, abs=1500)


def test_simulate_prazo_reduz_mais_que_sac():
    """
    No modo Itaú, o prazo cai mais agressivamente do que no SAC padrão,
    pois a amortização mensal aumenta (parcela mantida constante).
    """
    result = simulate_amortization(
        saldo=429629.87,
        prazo_remanescente=189,
        taxa_mensal=0.009631393,
        mip_mensal=94.45,
        dfi_mensal=38.61,
        parcela_total_anterior=6578.27,
        data_ultimo_vencimento=date(2026, 4, 21),
        data_operacao=date(2026, 4, 28),
        valor_amort=80000.0,
    )
    # SAC padrão com amortização mantida eliminaria ~80000/1514 ≈ 53 parcelas
    # Modo Itaú elimin muito mais porque amortização aumenta
    assert result["parcelas_eliminadas"] > 53


def test_simulate_parcela_quase_constante():
    """
    A nova parcela deve ser próxima da anterior (≈ mesma).
    É a característica central do modo Itaú.
    """
    result = simulate_amortization(
        saldo=429629.87,
        prazo_remanescente=189,
        taxa_mensal=0.009631393,
        mip_mensal=94.45,
        dfi_mensal=38.61,
        parcela_total_anterior=6578.27,
        data_ultimo_vencimento=date(2026, 4, 21),
        data_operacao=date(2026, 4, 28),
        valor_amort=80000.0,
    )
    delta_parcela_pct = abs(result["nova_parcela_proxima"] - 6578.27) / 6578.27
    assert delta_parcela_pct < 0.05  # mudança < 5%


def test_simulate_amortizacao_nova_maior():
    """Nova amortização mensal deve ser maior que a anterior."""
    result = simulate_amortization(
        saldo=429629.87,
        prazo_remanescente=189,
        taxa_mensal=0.009631393,
        mip_mensal=94.45,
        dfi_mensal=38.61,
        parcela_total_anterior=6578.27,
        data_ultimo_vencimento=date(2026, 4, 21),
        data_operacao=date(2026, 4, 28),
        valor_amort=80000.0,
    )
    # Amortização anterior implícita: 6578.27 - juros - seguros ≈ 2285
    assert result["nova_amortizacao_mensal"] > 2285.27
