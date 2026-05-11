"""
Motor PRICE — Sistema Francês de Amortização

Prestação constante, amortização crescente.

PMT = PV × [taxa × (1+taxa)^n] / [(1+taxa)^n - 1]
"""

from __future__ import annotations

import math
from datetime import date

from .sac import add_months


def compute_pmt(pv: float, taxa_mensal: float, n: int) -> float:
    """Calcula a prestação constante (PMT) do sistema PRICE."""
    if taxa_mensal == 0:
        return pv / n
    factor = (1 + taxa_mensal) ** n
    return pv * (taxa_mensal * factor) / (factor - 1)


def compute_balance_at(pv: float, taxa_mensal: float, n: int, k: int) -> float:
    """Saldo devedor após k pagamentos num contrato PRICE."""
    if taxa_mensal == 0:
        return pv * (1 - k / n)
    factor_n = (1 + taxa_mensal) ** n
    factor_k = (1 + taxa_mensal) ** k
    return pv * (factor_n - factor_k) / (factor_n - 1)


def compute_installment(
    saldo: float,
    prazo_remanescente: int,
    taxa_mensal: float,
    mip: float,
    dfi: float,
) -> dict:
    """Calcula os componentes de uma parcela PRICE."""
    pmt = compute_pmt(saldo, taxa_mensal, prazo_remanescente)
    juros = saldo * taxa_mensal
    amortizacao = pmt - juros
    seguros = mip + dfi

    return {
        "amortizacao": round(amortizacao, 2),
        "juros": round(juros, 2),
        "mip": round(mip, 2),
        "dfi": round(dfi, 2),
        "seguros": round(seguros, 2),
        "total": round(pmt + seguros, 2),
    }


def simulate_amortization(
    saldo: float,
    prazo_remanescente: int,
    taxa_mensal: float,
    mip_mensal: float,
    dfi_mensal: float,
    data_ultimo_vencimento: date,
    data_operacao: date,
    valor_amort: float,
    modalidade: str,  # 'prazo' | 'parcela'
    tr_estimada_mensal: float = 0.0,
) -> dict:
    """Simula amortização extraordinária no sistema PRICE."""
    from .sac import compute_pro_rata, _present_value

    pro_rata = compute_pro_rata(saldo, taxa_mensal, data_ultimo_vencimento, data_operacao, tr_estimada_mensal)
    saldo_novo = max(0.0, saldo - valor_amort + pro_rata["juros_pro_rata"] + pro_rata["atualizacao_tr"])
    total_desembolso = valor_amort + pro_rata["juros_pro_rata"] + pro_rata["atualizacao_tr"]

    pmt_original = compute_pmt(saldo, taxa_mensal, prazo_remanescente)

    if modalidade == "prazo":
        # Manter PMT, recalcular n
        if taxa_mensal == 0:
            prazo_novo = math.ceil(saldo_novo / (pmt_original if pmt_original > 0 else 1))
        else:
            # n = log(PMT / (PMT - saldo_novo * taxa)) / log(1 + taxa)
            denom = pmt_original - saldo_novo * taxa_mensal
            if denom <= 0:
                prazo_novo = prazo_remanescente
            else:
                prazo_novo = math.ceil(math.log(pmt_original / denom) / math.log(1 + taxa_mensal))
        nova_pmt = pmt_original
        prazo_inalterado = False
    else:
        # Manter n, recalcular PMT
        prazo_novo = prazo_remanescente
        nova_pmt = compute_pmt(saldo_novo, taxa_mensal, prazo_novo)
        prazo_inalterado = True

    parcelas_eliminadas = max(0, prazo_remanescente - prazo_novo)
    nova_parcela_proxima = nova_pmt + mip_mensal + dfi_mensal
    nova_amortizacao_mensal = nova_pmt - saldo_novo * taxa_mensal

    juros_sem = _total_interest_price(saldo, taxa_mensal, prazo_remanescente)
    juros_com = _total_interest_price(saldo_novo, taxa_mensal, prazo_novo)
    juros_economizados = juros_sem - juros_com
    juros_econ_vp = _present_value(juros_economizados, taxa_mensal, prazo_remanescente / 2)
    seguros_economizados = parcelas_eliminadas * (mip_mensal + dfi_mensal)
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
        "prazo_inalterado": prazo_inalterado,
        "seguros_economizados": round(seguros_economizados, 2),
        "juros_economizados_nominal": round(juros_economizados, 2),
        "juros_economizados_vp": round(juros_econ_vp, 2),
        "retorno_efetivo_aa": round(retorno_aa, 6),
        "data_nova_quitacao": data_nova_quitacao,
    }


def _total_interest_price(saldo: float, taxa_mensal: float, prazo: int) -> float:
    pmt = compute_pmt(saldo, taxa_mensal, prazo)
    return max(0.0, pmt * prazo - saldo)


def _present_value(future_value: float, taxa_mensal: float, periods: float) -> float:
    if taxa_mensal == 0:
        return future_value
    return future_value / ((1 + taxa_mensal) ** periods)
