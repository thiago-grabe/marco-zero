"""
Estimador de campos faltantes — dado parcela + saldo, infere o resto.

Usado no caminho de massa (3 campos) onde o usuário não sabe a taxa,
o prazo ou o sistema de amortização.

Lógica: para SAC, parcela = amort + juros + seguros.
  amort = saldo / prazo
  juros = saldo * taxa
  parcela ≈ (saldo / prazo) + (saldo * taxa)

Dado parcela e saldo, buscamos (taxa, prazo) que satisfaçam a equação.
Usamos busca binária na taxa (range 0.3% a 1.8% a.m.) — para cada taxa
candidata, calculamos o prazo que geraria aquela parcela.
"""

from __future__ import annotations

import math
from datetime import date, timedelta


def estimate_from_minimal(
    parcela_mensal: float,
    saldo_devedor: float,
) -> dict:
    """
    Estima campos faltantes a partir de parcela mensal + saldo devedor.

    Assume SAC (85% do mercado BR). Busca a taxa mensal que, combinada
    com o saldo, produz a parcela informada pelo usuário.

    Returns:
        dict com: taxa_mensal, amortizacao_mensal, prazo_remanescente,
        sistema_amortizacao, data_proxima_parcela, mip_mensal, dfi_mensal
    """
    if parcela_mensal <= 0 or saldo_devedor <= 0:
        raise ValueError("parcela_mensal e saldo_devedor devem ser > 0")

    # Validação de coerência: a parcela precisa cobrir ao menos os juros mínimos
    # Taxa mínima do mercado BR: ~0.3% a.m. (Minha Casa subsidiado)
    juros_minimos = saldo_devedor * 0.003
    if parcela_mensal < juros_minimos:
        raise ValueError(
            f"A parcela de R$ {parcela_mensal:,.2f} parece baixa para um saldo "
            f"de R$ {saldo_devedor:,.2f}. Confira os valores — a parcela precisa "
            f"cobrir ao menos os juros mensais (mínimo estimado: R$ {juros_minimos:,.2f})."
        )

    if parcela_mensal >= saldo_devedor:
        # Parcela maior que saldo = quase quitado
        return {
            "taxa_mensal": 0.008,
            "amortizacao_mensal": saldo_devedor,
            "prazo_remanescente": 1,
            "sistema_amortizacao": "SAC",
            "data_proxima_parcela": _next_month(),
            "mip_mensal": 0.0,
            "dfi_mensal": 0.0,
        }

    # Estimativa de seguros: ~2% da parcela (heurística conservadora)
    seguros_estimados = parcela_mensal * 0.02
    parcela_sem_seguros = parcela_mensal - seguros_estimados

    # Busca binária na taxa mensal
    # Range: 0.3% a 1.8% a.m. (cobre de Minha Casa a financiamento caro)
    taxa_low = 0.003
    taxa_high = 0.018
    taxa_best = 0.008  # fallback
    prazo_best = 360

    for _ in range(50):  # 50 iterações de bisseção = precisão de ~10^-15
        taxa_mid = (taxa_low + taxa_high) / 2

        # Para SAC na primeira parcela: parcela = (saldo/prazo) + (saldo*taxa)
        # Reescrevendo: prazo = saldo / (parcela_sem_seguros - saldo*taxa)
        juros_estimados = saldo_devedor * taxa_mid
        amort_estimada = parcela_sem_seguros - juros_estimados

        if amort_estimada <= 0:
            # Taxa muito alta — a parcela toda é juros
            taxa_high = taxa_mid
            continue

        prazo_estimado = saldo_devedor / amort_estimada

        if prazo_estimado < 1:
            taxa_high = taxa_mid
            continue

        # Verificação: parcela SAC na primeira parcela
        amort_check = saldo_devedor / round(prazo_estimado)
        parcela_check = amort_check + juros_estimados + seguros_estimados

        if abs(parcela_check - parcela_mensal) < 1.0:
            # Convergiu
            taxa_best = taxa_mid
            prazo_best = round(prazo_estimado)
            break

        if parcela_check > parcela_mensal:
            # Parcela calculada maior que informada → taxa está alta demais
            taxa_high = taxa_mid
        else:
            taxa_low = taxa_mid

        taxa_best = taxa_mid
        prazo_best = max(1, round(prazo_estimado))

    # Garantir prazo mínimo
    prazo_best = max(1, min(prazo_best, 600))

    amort_final = saldo_devedor / prazo_best
    juros_final = saldo_devedor * taxa_best

    return {
        "taxa_mensal": round(taxa_best, 10),
        "amortizacao_mensal": round(amort_final, 2),
        "prazo_remanescente": prazo_best,
        "sistema_amortizacao": "SAC",
        "data_proxima_parcela": _next_month(),
        "mip_mensal": 0.0,
        "dfi_mensal": 0.0,
    }


def _next_month() -> date:
    """Retorna o dia 21 do próximo mês (dia típico de vencimento)."""
    today = date.today()
    if today.month == 12:
        return date(today.year + 1, 1, 21)
    return date(today.year, today.month + 1, 21)
