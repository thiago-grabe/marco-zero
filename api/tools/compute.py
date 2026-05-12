"""
Tools de Compute — funções puras do motor expostas como ferramentas do agente.
O agente chama estas ferramentas; a LLM nunca calcula por conta própria.
"""

from __future__ import annotations

import json
from datetime import date

from agents import function_tool

from motor import sac


@function_tool
def simular_amortizacao(
    saldo_devedor: float,
    taxa_mensal: float,
    prazo_remanescente: int,
    amortizacao_mensal: float,
    mip_mensal: float,
    dfi_mensal: float,
    parcela_total: float,
    valor_amortizar: float,
    modalidade: str,
    data_ultimo_vencimento: str,
    data_operacao: str,
) -> str:
    """
    Simula o impacto de uma amortização extraordinária no financiamento.

    Args:
        saldo_devedor: Saldo devedor atual em reais.
        taxa_mensal: Taxa de juros mensal (ex: 0.009631).
        prazo_remanescente: Número de parcelas restantes.
        amortizacao_mensal: Valor da amortização mensal regular em reais.
        mip_mensal: Seguro MIP mensal em reais.
        dfi_mensal: Seguro DFI mensal em reais.
        parcela_total: Valor total da parcela atual em reais.
        valor_amortizar: Valor a ser amortizado antecipadamente em reais.
        modalidade: 'prazo' para redução de prazo, 'parcela' para redução de parcela.
        data_ultimo_vencimento: Data do último vencimento (YYYY-MM-DD).
        data_operacao: Data da operação de amortização (YYYY-MM-DD).

    Returns:
        JSON com saldo_novo, prazo_novo, parcelas_eliminadas, juros_economizados, etc.
    """
    result = sac.simulate_amortization(
        saldo=saldo_devedor,
        prazo_remanescente=prazo_remanescente,
        taxa_mensal=taxa_mensal,
        amortizacao_mensal=amortizacao_mensal,
        mip_mensal=mip_mensal,
        dfi_mensal=dfi_mensal,
        parcela_total=parcela_total,
        data_ultimo_vencimento=date.fromisoformat(data_ultimo_vencimento),
        data_operacao=date.fromisoformat(data_operacao),
        valor_amort=valor_amortizar,
        modalidade=modalidade,
    )
    result["data_nova_quitacao"] = str(result["data_nova_quitacao"])
    return json.dumps(result, ensure_ascii=False)


@function_tool
def projetar_cenario(
    saldo_devedor: float,
    taxa_mensal: float,
    prazo_remanescente: int,
    amortizacao_mensal: float,
    mip_mensal: float,
    dfi_mensal: float,
    data_proxima_parcela: str,
    aporte_mensal_extra: float = 0.0,
    aporte_anual_extra: float = 0.0,
    mes_aporte_anual: int = 0,
    meses_aporte_extra: str = "",
) -> str:
    """
    Projeta um cenário de amortização mês a mês e retorna quando quita.

    Args:
        saldo_devedor: Saldo devedor atual em reais.
        taxa_mensal: Taxa de juros mensal (ex: 0.009631).
        prazo_remanescente: Número de parcelas restantes.
        amortizacao_mensal: Valor da amortização mensal regular em reais.
        mip_mensal: Seguro MIP mensal em reais.
        dfi_mensal: Seguro DFI mensal em reais.
        data_proxima_parcela: Data do próximo vencimento (YYYY-MM-DD).
        aporte_mensal_extra: Aporte mensal extra além da parcela (em reais). Zero se nenhum.
        aporte_anual_extra: Aporte anual extra (em reais). Zero se nenhum.
        mes_aporte_anual: Mês do aporte anual (1-12). Zero se não há aporte anual.
        meses_aporte_extra: Meses (1-12) em que o aporte extra é aplicado, separados por vírgula.
            Exemplos: "2,4,6,8,10,12" para meses pares, "1,4,7,10" para trimestral,
            "6,12" para semestral. Vazio = aplica todo mês.

    Returns:
        JSON com data_quitacao, parcelas_eliminadas, total_juros_pagos, total_juros_economizados, schedule ano a ano.
    """
    # Parse meses_aporte_extra string para lista de ints
    meses_lista: list[int] | None = None
    if meses_aporte_extra.strip():
        try:
            meses_lista = [int(m.strip()) for m in meses_aporte_extra.split(",") if m.strip()]
        except ValueError:
            meses_lista = None

    result = sac.project_scenario(
        saldo=saldo_devedor,
        prazo_remanescente=prazo_remanescente,
        taxa_mensal=taxa_mensal,
        amortizacao_mensal=amortizacao_mensal,
        mip_mensal=mip_mensal,
        dfi_mensal=dfi_mensal,
        data_proxima_parcela=date.fromisoformat(data_proxima_parcela),
        aporte_mensal_extra=aporte_mensal_extra,
        aporte_anual_extra=aporte_anual_extra,
        mes_aporte_anual=mes_aporte_anual if mes_aporte_anual > 0 else None,
        meses_aporte_extra=meses_lista,
    )
    result["data_quitacao"] = str(result["data_quitacao"])
    return json.dumps(result, ensure_ascii=False)


@function_tool
def comparar_cenarios(
    saldo_devedor: float,
    taxa_mensal: float,
    prazo_remanescente: int,
    amortizacao_mensal: float,
    mip_mensal: float,
    dfi_mensal: float,
    data_proxima_parcela: str,
    cenarios_json: str,
) -> str:
    """
    Compara até 4 cenários de amortização e retorna análise marginal.

    Args:
        saldo_devedor: Saldo devedor atual.
        taxa_mensal: Taxa de juros mensal.
        prazo_remanescente: Parcelas restantes.
        amortizacao_mensal: Amortização mensal regular.
        mip_mensal: Seguro MIP mensal.
        dfi_mensal: Seguro DFI mensal.
        data_proxima_parcela: Próximo vencimento (YYYY-MM-DD).
        cenarios_json: JSON array com objetos contendo aporte_mensal_extra, aporte_anual_extra, mes_aporte_anual.

    Returns:
        JSON com base (plano sem extras), cenarios (projeções) e marginal (análise incremental).
    """
    cenarios = json.loads(cenarios_json)
    result = sac.compare_scenarios(
        saldo=saldo_devedor,
        prazo_remanescente=prazo_remanescente,
        taxa_mensal=taxa_mensal,
        amortizacao_mensal=amortizacao_mensal,
        mip_mensal=mip_mensal,
        dfi_mensal=dfi_mensal,
        data_proxima_parcela=date.fromisoformat(data_proxima_parcela),
        scenarios=cenarios,
    )
    # Serializar datas
    for proj in [result["base"]] + result["cenarios"]:
        proj["data_quitacao"] = str(proj["data_quitacao"])
    return json.dumps(result, ensure_ascii=False)


@function_tool
def calcular_parcela(
    saldo_devedor: float,
    taxa_mensal: float,
    prazo_remanescente: int,
    mip_mensal: float,
    dfi_mensal: float,
) -> str:
    """
    Calcula os componentes de uma parcela (amortização, juros, seguros, total).

    Args:
        saldo_devedor: Saldo devedor atual.
        taxa_mensal: Taxa de juros mensal.
        prazo_remanescente: Parcelas restantes.
        mip_mensal: Seguro MIP mensal.
        dfi_mensal: Seguro DFI mensal.

    Returns:
        JSON com amortizacao, juros, mip, dfi, seguros, total.
    """
    result = sac.compute_installment(
        saldo_devedor, prazo_remanescente, taxa_mensal, mip_mensal, dfi_mensal
    )
    return json.dumps(result, ensure_ascii=False)


@function_tool
def calcular_pro_rata(
    saldo_devedor: float,
    taxa_mensal: float,
    data_ultimo_vencimento: str,
    data_operacao: str,
) -> str:
    """
    Calcula juros pró-rata entre duas datas (para saber quanto custa esperar X dias para amortizar).

    Args:
        saldo_devedor: Saldo devedor atual.
        taxa_mensal: Taxa de juros mensal.
        data_ultimo_vencimento: Data do último vencimento (YYYY-MM-DD).
        data_operacao: Data da operação pretendida (YYYY-MM-DD).

    Returns:
        JSON com dias_decorridos, juros_pro_rata, total_acrescimo.
    """
    result = sac.compute_pro_rata(
        saldo_devedor, taxa_mensal,
        date.fromisoformat(data_ultimo_vencimento),
        date.fromisoformat(data_operacao),
    )
    return json.dumps(result, ensure_ascii=False)
