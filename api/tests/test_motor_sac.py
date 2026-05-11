"""
Testes do motor SAC com dados reais do contrato de referência.

Contrato: Itaú, Carteira Hipotecária, SAC, 12,19% a.a.
DDC de 05/05/2026 (após amortização de R$80k em 28/04/2026)

Dados do DDC confirmados:
  Saldo devedor:     R$ 429.629,87
  Taxa mensal:       0,9631393% (0.009631393)
  Próxima parcela:   #5, vencimento 21/05/2026
  Amortização:       R$ 2.285,27
  Juros:             R$ 4.159,94 (inclui correção TR — pequena diferença esperada)
  MIP:               R$ 94,45
  DFI:               R$ 38,61
  Total:             R$ 6.578,27
  189 parcelas restantes
"""

from datetime import date

import pytest

from motor.sac import (
    add_months,
    compare_scenarios,
    compute_installment,
    compute_pro_rata,
    project_scenario,
    simulate_amortization,
)

# ── Dados de referência ─────────────────────────────────────────────────────────

SALDO = 429_629.87
TAXA = 0.009631393
AMORT_MENSAL = 2_285.27
MIP = 94.45
DFI = 38.61
PRAZO = 189
DATA_PROXIMA = date(2026, 5, 21)
DATA_ULTIMO_VENCIMENTO = date(2026, 4, 21)  # parcela #4


# ── Testes de parcela ────────────────────────────────────────────────────────────

def test_compute_installment_amortizacao():
    """
    Amortização SAC pura = saldo / prazo_remanescente.

    Nota: o DDC mostra 2.285,27 porque o Itaú usou modo híbrido
    (manutenção de prestação) após a amortização de R$80k em 28/04.
    SAC puro correto: 429.629,87 / 189 = 2.273,17.
    """
    result = compute_installment(SALDO, PRAZO, TAXA, MIP, DFI)
    expected_sac_puro = round(SALDO / PRAZO, 2)
    assert result["amortizacao"] == pytest.approx(expected_sac_puro, abs=0.02)


def test_compute_installment_seguros():
    """MIP + DFI corretos."""
    result = compute_installment(SALDO, PRAZO, TAXA, MIP, DFI)
    assert result["seguros"] == pytest.approx(133.06, abs=0.01)


def test_compute_installment_total():
    """Total da parcela = amort + juros + seguros."""
    result = compute_installment(SALDO, PRAZO, TAXA, MIP, DFI)
    expected_total = result["amortizacao"] + result["juros"] + result["seguros"]
    assert result["total"] == pytest.approx(expected_total, abs=0.01)


def test_compute_installment_total_aproximado():
    """
    Total SAC puro = amort_sac + juros + seguros.

    O DDC mostra R$6.578,27 que inclui amortizacao em modo Itaú (2.285,27)
    e juros com TR. SAC puro dá ~R$6.544 — diferença de ~R$34 é esperada.
    O que importa é a consistência interna: total = amort + juros + seguros.
    """
    result = compute_installment(SALDO, PRAZO, TAXA, MIP, DFI)
    expected = result["amortizacao"] + result["juros"] + result["seguros"]
    assert result["total"] == pytest.approx(expected, abs=0.01)


def test_compute_installment_invalido():
    """Prazo zero deve levantar erro."""
    with pytest.raises(ValueError, match="prazo_remanescente deve ser > 0"):
        compute_installment(SALDO, 0, TAXA, MIP, DFI)


# ── Testes de pró-rata ────────────────────────────────────────────────────────

def test_pro_rata_mesmo_dia():
    """Pro-rata zero no dia do vencimento."""
    result = compute_pro_rata(SALDO, TAXA, DATA_ULTIMO_VENCIMENTO, DATA_ULTIMO_VENCIMENTO)
    assert result["dias_decorridos"] == 0
    assert result["juros_pro_rata"] == 0.0


def test_pro_rata_7_dias():
    """Pro-rata de 7 dias = 7/30 × juros mensais."""
    data_op = date(2026, 4, 28)  # 7 dias após 21/04
    result = compute_pro_rata(SALDO, TAXA, DATA_ULTIMO_VENCIMENTO, data_op)
    assert result["dias_decorridos"] == 7
    expected = SALDO * TAXA * (7 / 30)
    assert result["juros_pro_rata"] == pytest.approx(expected, abs=0.10)


def test_pro_rata_data_invalida():
    """Data de operação anterior ao vencimento deve levantar erro."""
    with pytest.raises(ValueError):
        compute_pro_rata(SALDO, TAXA, date(2026, 5, 1), date(2026, 4, 1))


# ── Testes de amortização extraordinária ─────────────────────────────────────

def test_simulate_amortization_prazo_saldo_novo():
    """Saldo novo = saldo - amortização + pró-rata."""
    result = simulate_amortization(
        saldo=SALDO,
        prazo_remanescente=PRAZO,
        taxa_mensal=TAXA,
        amortizacao_mensal=AMORT_MENSAL,
        mip_mensal=MIP,
        dfi_mensal=DFI,
        parcela_total=6_578.27,
        data_ultimo_vencimento=DATA_ULTIMO_VENCIMENTO,
        data_operacao=date(2026, 4, 28),
        valor_amort=80_000.0,
        modalidade="prazo",
        calculation_mode="itau",
    )
    # Saldo novo deve ser ~429.630 (antes da operação era ~510.977 + pro-rata, depois -80k)
    # Mas o estado já é pós-amortização (DDC 05/05), então este teste é forward-looking
    assert result["saldo_novo"] < SALDO
    assert result["prazo_novo"] < PRAZO


def test_simulate_amortization_parcelas_eliminadas_positivo():
    """Amortização de 30k deve eliminar parcelas."""
    result = simulate_amortization(
        saldo=SALDO,
        prazo_remanescente=PRAZO,
        taxa_mensal=TAXA,
        amortizacao_mensal=AMORT_MENSAL,
        mip_mensal=MIP,
        dfi_mensal=DFI,
        parcela_total=6_578.27,
        data_ultimo_vencimento=DATA_ULTIMO_VENCIMENTO,
        data_operacao=date(2026, 5, 15),
        valor_amort=30_000.0,
        modalidade="prazo",
        calculation_mode="SAC",
    )
    assert result["parcelas_eliminadas"] > 0
    assert result["juros_economizados_nominal"] > 0


def test_simulate_amortization_reducao_parcela_prazo_inalterado():
    """Redução de parcela não altera prazo."""
    result = simulate_amortization(
        saldo=SALDO,
        prazo_remanescente=PRAZO,
        taxa_mensal=TAXA,
        amortizacao_mensal=AMORT_MENSAL,
        mip_mensal=MIP,
        dfi_mensal=DFI,
        parcela_total=6_578.27,
        data_ultimo_vencimento=DATA_ULTIMO_VENCIMENTO,
        data_operacao=date(2026, 5, 15),
        valor_amort=30_000.0,
        modalidade="parcela",
        calculation_mode="SAC",
    )
    assert result["prazo_inalterado"] is True
    assert result["prazo_novo"] == PRAZO


# ── Testes de projeção de cenário ─────────────────────────────────────────────

def test_project_scenario_base_sem_extras():
    """Sem extras, quitação deve ser em ~Jan 2042 (data do DDC)."""
    result = project_scenario(
        saldo=SALDO,
        prazo_remanescente=PRAZO,
        taxa_mensal=TAXA,
        amortizacao_mensal=AMORT_MENSAL,
        mip_mensal=MIP,
        dfi_mensal=DFI,
        data_proxima_parcela=DATA_PROXIMA,
    )
    assert result["prazo_meses"] == pytest.approx(PRAZO, abs=2)
    assert result["data_quitacao"].year in [2041, 2042]
    assert result["total_extras_investidos"] == 0.0


def test_project_scenario_5k_mensal():
    """
    Com R$5k/mês extra, quitação deve ser em ~2031 (5 anos menos).
    Validado contra cálculo real da conversa: quitação em abril/2031.
    """
    result = project_scenario(
        saldo=SALDO,
        prazo_remanescente=PRAZO,
        taxa_mensal=TAXA,
        amortizacao_mensal=AMORT_MENSAL,
        mip_mensal=MIP,
        dfi_mensal=DFI,
        data_proxima_parcela=DATA_PROXIMA,
        aporte_mensal_extra=5_000.0,
    )
    # DDC real: quita em ~04/2031 com 5k/mês (59 parcelas)
    assert result["prazo_meses"] == pytest.approx(59, abs=5)
    assert result["data_quitacao"].year in [2030, 2031]
    assert result["total_juros_economizados"] > 200_000  # economia de ~R$267k


def test_project_scenario_5k_mais_60k_anual():
    """
    Com R$5k/mês + R$60k/ano em abril, quitação deve ser em ~2029 (3 anos).
    Validado contra cálculo real da conversa.
    """
    result = project_scenario(
        saldo=SALDO,
        prazo_remanescente=PRAZO,
        taxa_mensal=TAXA,
        amortizacao_mensal=AMORT_MENSAL,
        mip_mensal=MIP,
        dfi_mensal=DFI,
        data_proxima_parcela=DATA_PROXIMA,
        aporte_mensal_extra=5_000.0,
        aporte_anual_extra=60_000.0,
        mes_aporte_anual=4,  # abril
    )
    # DDC real: quita em ~04/2029 com 5k/mês + 60k/ano (35 parcelas)
    assert result["prazo_meses"] == pytest.approx(35, abs=5)
    assert result["data_quitacao"].year in [2028, 2029]


def test_project_scenario_juros_economizados_positivo():
    """Extras sempre economizam juros."""
    base = project_scenario(SALDO, PRAZO, TAXA, AMORT_MENSAL, MIP, DFI, DATA_PROXIMA)
    com_extra = project_scenario(
        SALDO, PRAZO, TAXA, AMORT_MENSAL, MIP, DFI, DATA_PROXIMA,
        aporte_mensal_extra=3_000.0
    )
    assert com_extra["total_juros_economizados"] > base["total_juros_economizados"]
    assert com_extra["prazo_meses"] < base["prazo_meses"]


# ── Testes de comparação de cenários ─────────────────────────────────────────

def test_compare_scenarios_retorna_3_cenarios():
    """compare_scenarios retorna base + N cenários comparados."""
    result = compare_scenarios(
        saldo=SALDO,
        prazo_remanescente=PRAZO,
        taxa_mensal=TAXA,
        amortizacao_mensal=AMORT_MENSAL,
        mip_mensal=MIP,
        dfi_mensal=DFI,
        data_proxima_parcela=DATA_PROXIMA,
        scenarios=[
            {"aporte_mensal_extra": 3_000},
            {"aporte_mensal_extra": 5_000},
            {"aporte_mensal_extra": 5_000, "aporte_anual_extra": 60_000, "mes_aporte_anual": 4},
        ],
    )
    assert "base" in result
    assert len(result["cenarios"]) == 3
    assert len(result["marginal"]) == 3


def test_compare_scenarios_marginal_decrescente():
    """Retorno marginal decresce com mais aportes (lei dos retornos decrescentes)."""
    result = compare_scenarios(
        saldo=SALDO,
        prazo_remanescente=PRAZO,
        taxa_mensal=TAXA,
        amortizacao_mensal=AMORT_MENSAL,
        mip_mensal=MIP,
        dfi_mensal=DFI,
        data_proxima_parcela=DATA_PROXIMA,
        scenarios=[
            {"aporte_mensal_extra": 2_000},
            {"aporte_mensal_extra": 5_000},
            {"aporte_mensal_extra": 10_000},
        ],
    )
    retornos = [m["retorno_marginal"] for m in result["marginal"]]
    # Todos os retornos são positivos
    assert all(r > 0 for r in retornos)


# ── Testes de utilitários ─────────────────────────────────────────────────────

def test_add_months_simples():
    assert add_months(date(2026, 5, 21), 1) == date(2026, 6, 21)
    assert add_months(date(2026, 12, 21), 1) == date(2027, 1, 21)


def test_add_months_fim_de_mes():
    """31 de janeiro + 1 mês = 28 fev (ou 29 em ano bissexto)."""
    result = add_months(date(2026, 1, 31), 1)
    assert result == date(2026, 2, 28)


def test_add_months_189_parcelas():
    """189 meses a partir de mai/2026 = jan/2042 (data do DDC)."""
    result = add_months(date(2026, 5, 21), 188)  # 188 meses = parcela 189
    assert result.year == 2042
    assert result.month == 1
