"""
Motor Itaú — Modo de manutenção de prestação

Comportamento observado empiricamente: quando o usuário faz amortização
extraordinária com "redução de prazo", o banco mantém a prestação total
quase constante e usa a queda dos juros para aumentar a amortização mensal,
comprimindo o prazo agressivamente.

Identificação automática (em motor/__init__.py):
  se (nova_amort / amort_anterior > 1.20) AND (delta_parcela < 5%):
    → modo = 'itau'
"""

from __future__ import annotations

import math
from datetime import date

from .sac import _present_value, add_months, compute_pro_rata


def detect_itau_mode(
    amortizacao_anterior: float,
    amortizacao_nova: float,
    parcela_anterior: float,
    parcela_nova: float,
) -> bool:
    """
    Detecta se o banco está operando no modo Itaú.
    Retorna True se amortização subiu >20% e parcela mudou <5%.
    """
    if amortizacao_anterior <= 0 or parcela_anterior <= 0:
        return False

    delta_amort = (amortizacao_nova - amortizacao_anterior) / amortizacao_anterior
    delta_parcela = abs(parcela_nova - parcela_anterior) / parcela_anterior

    return delta_amort > 0.20 and delta_parcela < 0.05


def simulate_amortization(
    saldo: float,
    prazo_remanescente: int,
    taxa_mensal: float,
    mip_mensal: float,
    dfi_mensal: float,
    parcela_total_anterior: float,
    data_ultimo_vencimento: date,
    data_operacao: date,
    valor_amort: float,
    tr_estimada_mensal: float = 0.0,
) -> dict:
    """
    Simula amortização no modo Itaú.

    O banco:
    1. Calcula novo saldo após amortização
    2. Calcula os novos juros sobre o novo saldo
    3. Define nova amortização = parcela_anterior - novos_juros - seguros
    4. Recalcula prazo = ceil(saldo_novo / nova_amortizacao)

    Resultado: parcela cai minimamente (~R$10-20), mas prazo despenca.
    """
    pro_rata = compute_pro_rata(
        saldo, taxa_mensal, data_ultimo_vencimento, data_operacao, tr_estimada_mensal
    )
    saldo_novo = max(0.0, saldo - valor_amort + pro_rata["juros_pro_rata"] + pro_rata["atualizacao_tr"])
    total_desembolso = valor_amort + pro_rata["juros_pro_rata"] + pro_rata["atualizacao_tr"]

    # Banco calcula nova amortização para manter parcela ≈ constante
    juros_novos = saldo_novo * taxa_mensal
    seguros = mip_mensal + dfi_mensal
    nova_amortizacao_mensal = parcela_total_anterior - juros_novos - seguros

    # Garantia: nova amortização >= mínimo SAC
    amort_minimo_sac = saldo_novo / prazo_remanescente if prazo_remanescente > 0 else saldo_novo
    nova_amortizacao_mensal = max(nova_amortizacao_mensal, amort_minimo_sac)

    prazo_novo = math.ceil(saldo_novo / nova_amortizacao_mensal) if nova_amortizacao_mensal > 0 else 0
    prazo_novo = max(1, prazo_novo)

    nova_parcela_proxima = nova_amortizacao_mensal + juros_novos + seguros
    parcelas_eliminadas = max(0, prazo_remanescente - prazo_novo)

    # Economia vs. SAC sem amortização
    from .sac import _total_interest_sac
    juros_sem = _total_interest_sac(saldo, taxa_mensal, saldo / prazo_remanescente, prazo_remanescente)
    juros_com = _total_interest_sac(saldo_novo, taxa_mensal, nova_amortizacao_mensal, prazo_novo)
    juros_economizados = juros_sem - juros_com
    juros_econ_vp = _present_value(juros_economizados, taxa_mensal, prazo_remanescente / 2)
    seguros_economizados = parcelas_eliminadas * seguros
    retorno_aa = (1 + taxa_mensal) ** 12 - 1
    data_nova_quitacao = add_months(data_operacao, prazo_novo)

    return {
        "saldo_novo": round(saldo_novo, 2),
        "juros_pro_rata": pro_rata["juros_pro_rata"],
        "atualizacao_monetaria": pro_rata["atualizacao_tr"],
        "total_desembolso": round(total_desembolso, 2),
        "prazo_novo": prazo_novo,
        "parcelas_eliminadas": parcelas_eliminadas,
        "nova_amortizacao_mensal": round(nova_amortizacao_mensal, 2),
        "nova_parcela_proxima": round(nova_parcela_proxima, 2),
        "prazo_inalterado": False,
        "seguros_economizados": round(seguros_economizados, 2),
        "juros_economizados_nominal": round(juros_economizados, 2),
        "juros_economizados_vp": round(juros_econ_vp, 2),
        "retorno_efetivo_aa": round(retorno_aa, 6),
        "data_nova_quitacao": data_nova_quitacao,
    }
