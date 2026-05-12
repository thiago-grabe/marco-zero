"""
Testes de frequência de amortização — meses pares, ímpares, trimestral, semestral.

Verifica que o motor aplica aportes extras somente nos meses especificados.
"""

from datetime import date

import pytest

from motor.sac import project_scenario, generate_installment_schedule

# Dados de referência simplificados para testes de frequência
SALDO = 500_000.0
TAXA = 0.0097
AMORT = 1_500.0
MIP = 40.0
DFI = 40.0
PRAZO = 420
DATA = date(2026, 5, 21)
APORTE = 5_000.0


# ── project_scenario com meses_aporte_extra ──────────────────────────────────

def test_meses_pares_quita_mais_lento_que_mensal():
    """Amortizar em meses pares (6x/ano) deve quitar mais devagar que todo mês (12x/ano)."""
    mensal = project_scenario(SALDO, PRAZO, TAXA, AMORT, MIP, DFI, DATA,
                              aporte_mensal_extra=APORTE)
    pares = project_scenario(SALDO, PRAZO, TAXA, AMORT, MIP, DFI, DATA,
                             aporte_mensal_extra=APORTE,
                             meses_aporte_extra=[2, 4, 6, 8, 10, 12])

    assert pares["prazo_meses"] > mensal["prazo_meses"]
    assert pares["total_juros_economizados"] < mensal["total_juros_economizados"]
    assert pares["total_extras_investidos"] < mensal["total_extras_investidos"]


def test_meses_pares_vs_impares_simetrico():
    """Meses pares e ímpares com mesmo aporte devem ter resultado similar (±1 mês)."""
    pares = project_scenario(SALDO, PRAZO, TAXA, AMORT, MIP, DFI, DATA,
                             aporte_mensal_extra=APORTE,
                             meses_aporte_extra=[2, 4, 6, 8, 10, 12])
    impares = project_scenario(SALDO, PRAZO, TAXA, AMORT, MIP, DFI, DATA,
                               aporte_mensal_extra=APORTE,
                               meses_aporte_extra=[1, 3, 5, 7, 9, 11])

    assert abs(pares["prazo_meses"] - impares["prazo_meses"]) <= 2


def test_trimestral_quita_mais_lento_que_bimestral():
    """Trimestral (4x/ano) mais lento que bimestral (6x/ano)."""
    bimestral = project_scenario(SALDO, PRAZO, TAXA, AMORT, MIP, DFI, DATA,
                                 aporte_mensal_extra=APORTE,
                                 meses_aporte_extra=[2, 4, 6, 8, 10, 12])
    trimestral = project_scenario(SALDO, PRAZO, TAXA, AMORT, MIP, DFI, DATA,
                                  aporte_mensal_extra=APORTE,
                                  meses_aporte_extra=[3, 6, 9, 12])

    assert trimestral["prazo_meses"] > bimestral["prazo_meses"]


def test_semestral_quita_mais_lento_que_trimestral():
    """Semestral (2x/ano) mais lento que trimestral (4x/ano)."""
    trimestral = project_scenario(SALDO, PRAZO, TAXA, AMORT, MIP, DFI, DATA,
                                  aporte_mensal_extra=APORTE,
                                  meses_aporte_extra=[3, 6, 9, 12])
    semestral = project_scenario(SALDO, PRAZO, TAXA, AMORT, MIP, DFI, DATA,
                                 aporte_mensal_extra=APORTE,
                                 meses_aporte_extra=[6, 12])

    assert semestral["prazo_meses"] > trimestral["prazo_meses"]


def test_meses_none_equivale_a_mensal():
    """meses_aporte_extra=None deve ser igual a amortizar todo mês."""
    mensal = project_scenario(SALDO, PRAZO, TAXA, AMORT, MIP, DFI, DATA,
                              aporte_mensal_extra=APORTE)
    none_meses = project_scenario(SALDO, PRAZO, TAXA, AMORT, MIP, DFI, DATA,
                                  aporte_mensal_extra=APORTE,
                                  meses_aporte_extra=None)

    assert mensal["prazo_meses"] == none_meses["prazo_meses"]
    assert mensal["total_juros_pagos"] == none_meses["total_juros_pagos"]


def test_meses_vazio_equivale_a_mensal():
    """meses_aporte_extra=[] deve ser igual a amortizar todo mês."""
    mensal = project_scenario(SALDO, PRAZO, TAXA, AMORT, MIP, DFI, DATA,
                              aporte_mensal_extra=APORTE)
    vazio = project_scenario(SALDO, PRAZO, TAXA, AMORT, MIP, DFI, DATA,
                             aporte_mensal_extra=APORTE,
                             meses_aporte_extra=[])

    assert mensal["prazo_meses"] == vazio["prazo_meses"]


def test_mes_unico_aplica_uma_vez_por_ano():
    """Aporte extra apenas em abril = 1x por ano."""
    abril = project_scenario(SALDO, PRAZO, TAXA, AMORT, MIP, DFI, DATA,
                             aporte_mensal_extra=APORTE,
                             meses_aporte_extra=[4])

    # Total investido em extras deve ser ~5000 * N_anos
    anos_projecao = abril["prazo_meses"] / 12
    extras_esperados_aprox = APORTE * anos_projecao
    assert abril["total_extras_investidos"] == pytest.approx(extras_esperados_aprox, rel=0.15)


def test_sem_aporte_extra_meses_lista_nao_importa():
    """Se aporte_mensal_extra=0, a lista de meses não faz diferença."""
    base = project_scenario(SALDO, PRAZO, TAXA, AMORT, MIP, DFI, DATA)
    com_meses = project_scenario(SALDO, PRAZO, TAXA, AMORT, MIP, DFI, DATA,
                                 meses_aporte_extra=[2, 4, 6])

    assert base["prazo_meses"] == com_meses["prazo_meses"]


# ── generate_installment_schedule com meses_aporte_extra ─────────────────────

def test_schedule_meses_pares_aplica_so_nos_pares():
    """Planilha deve ter extra_mensal > 0 apenas em fev, abr, jun, ago, out, dez."""
    rows = generate_installment_schedule(
        SALDO, PRAZO, TAXA, AMORT, MIP, DFI, DATA,
        aporte_mensal_extra=APORTE,
        meses_aporte_extra=[2, 4, 6, 8, 10, 12],
    )

    for row in rows[:24]:  # checar os primeiros 2 anos
        mes = date.fromisoformat(row["data"]).month
        if mes in (2, 4, 6, 8, 10, 12):
            # Pode ser 0 se saldo já zerou, mas se saldo > 0, deve ter extra
            if row["saldo_anterior"] > APORTE:
                assert row["extra_mensal"] > 0, f"Mês {mes} deveria ter extra, mas tem {row['extra_mensal']}"
        else:
            assert row["extra_mensal"] == 0, f"Mês {mes} NÃO deveria ter extra, mas tem {row['extra_mensal']}"


def test_schedule_trimestral():
    """Planilha trimestral: extras apenas em mar, jun, set, dez."""
    rows = generate_installment_schedule(
        SALDO, PRAZO, TAXA, AMORT, MIP, DFI, DATA,
        aporte_mensal_extra=APORTE,
        meses_aporte_extra=[3, 6, 9, 12],
    )

    meses_com_extra = set()
    for row in rows[:24]:
        if row["extra_mensal"] > 0:
            mes = date.fromisoformat(row["data"]).month
            meses_com_extra.add(mes)

    # Deve ter extras apenas nos meses 3, 6, 9, 12
    assert meses_com_extra.issubset({3, 6, 9, 12})
    assert len(meses_com_extra) > 0  # pelo menos algum


# ── Hierarquia de frequência ─────────────────────────────────────────────────

def test_hierarquia_completa_frequencias():
    """
    Hierarquia esperada de velocidade de quitação:
    mensal > bimestral > trimestral > semestral > anual > sem extras
    """
    sem_extra = project_scenario(SALDO, PRAZO, TAXA, AMORT, MIP, DFI, DATA)
    mensal = project_scenario(SALDO, PRAZO, TAXA, AMORT, MIP, DFI, DATA,
                              aporte_mensal_extra=APORTE)
    bimestral = project_scenario(SALDO, PRAZO, TAXA, AMORT, MIP, DFI, DATA,
                                 aporte_mensal_extra=APORTE,
                                 meses_aporte_extra=[2, 4, 6, 8, 10, 12])
    trimestral = project_scenario(SALDO, PRAZO, TAXA, AMORT, MIP, DFI, DATA,
                                  aporte_mensal_extra=APORTE,
                                  meses_aporte_extra=[3, 6, 9, 12])
    semestral = project_scenario(SALDO, PRAZO, TAXA, AMORT, MIP, DFI, DATA,
                                 aporte_mensal_extra=APORTE,
                                 meses_aporte_extra=[6, 12])

    prazos = [
        ("mensal", mensal["prazo_meses"]),
        ("bimestral", bimestral["prazo_meses"]),
        ("trimestral", trimestral["prazo_meses"]),
        ("semestral", semestral["prazo_meses"]),
        ("sem_extra", sem_extra["prazo_meses"]),
    ]

    for i in range(len(prazos) - 1):
        nome_a, prazo_a = prazos[i]
        nome_b, prazo_b = prazos[i + 1]
        assert prazo_a <= prazo_b, f"{nome_a} ({prazo_a}) deveria quitar antes de {nome_b} ({prazo_b})"
