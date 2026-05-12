"""
Motor SAC — Sistema de Amortização Constante

Funções puras: zero I/O, zero side effects, testáveis unitariamente.

Matemática:
  amortizacao_i  = saldo_atual / prazo_remanescente  (constante se sem amort extra)
  juros_i        = saldo_atual × taxa_mensal
  parcela_i      = amortizacao_i + juros_i + seguros_i  (decrescente)
  saldo_{i+1}    = saldo_i - amortizacao_i
"""

from __future__ import annotations

import math
from datetime import date, timedelta


# ── Helpers de data ─────────────────────────────────────────────────────────────

def add_months(d: date, months: int) -> date:
    """Avança N meses mantendo o dia (ajusta para fim do mês quando necessário)."""
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    last_day = _last_day_of_month(year, month)
    day = min(d.day, last_day)
    return date(year, month, day)


def _last_day_of_month(year: int, month: int) -> int:
    if month == 12:
        return 31
    return (date(year, month + 1, 1) - timedelta(days=1)).day


def days_between(start: date, end: date) -> int:
    return (end - start).days


# ── Cálculo de parcela ──────────────────────────────────────────────────────────

def compute_installment(
    saldo: float,
    prazo_remanescente: int,
    taxa_mensal: float,
    mip: float,
    dfi: float,
) -> dict:
    """
    Calcula os componentes de uma parcela SAC.

    Args:
        saldo: saldo devedor atual
        prazo_remanescente: meses restantes
        taxa_mensal: taxa de juros mensal (ex: 0.009631393)
        mip: seguro de morte e invalidez
        dfi: seguro de danos físicos

    Returns:
        dict com amortizacao, juros, mip, dfi, seguros, total
    """
    if prazo_remanescente <= 0:
        raise ValueError("prazo_remanescente deve ser > 0")

    amortizacao = saldo / prazo_remanescente
    juros = saldo * taxa_mensal
    seguros = mip + dfi
    total = amortizacao + juros + seguros

    return {
        "amortizacao": round(amortizacao, 2),
        "juros": round(juros, 2),
        "mip": round(mip, 2),
        "dfi": round(dfi, 2),
        "seguros": round(seguros, 2),
        "total": round(total, 2),
    }


# ── Pró-rata ────────────────────────────────────────────────────────────────────

def compute_pro_rata(
    saldo: float,
    taxa_mensal: float,
    data_ultimo_vencimento: date,
    data_operacao: date,
    tr_estimada_mensal: float = 0.0,
) -> dict:
    """
    Calcula juros pró-rata e correção monetária entre dois vencimentos.

    Os juros pró-rata são calculados proporcionalmente ao número de dias
    decorridos desde o último vencimento até a data da operação.

    TR estimada: a Taxa Referencial é variável e não previsível.
    Para amortizações futuras, usamos uma estimativa conservadora de 0.

    Returns:
        dict com dias_decorridos, juros_pro_rata, atualizacao_tr, total_acrescimo
    """
    dias = days_between(data_ultimo_vencimento, data_operacao)
    if dias < 0:
        raise ValueError("data_operacao deve ser >= data_ultimo_vencimento")

    # Dias num mês padrão (30 para contrato SAC com base 30/360)
    dias_no_mes = 30
    fracao = dias / dias_no_mes

    juros_pro_rata = saldo * taxa_mensal * fracao
    atualizacao_tr = saldo * tr_estimada_mensal * fracao

    return {
        "dias_decorridos": dias,
        "juros_pro_rata": round(juros_pro_rata, 2),
        "atualizacao_tr": round(atualizacao_tr, 2),
        "total_acrescimo": round(juros_pro_rata + atualizacao_tr, 2),
    }


# ── Simulação de amortização extraordinária ─────────────────────────────────────

def simulate_amortization(
    saldo: float,
    prazo_remanescente: int,
    taxa_mensal: float,
    amortizacao_mensal: float,
    mip_mensal: float,
    dfi_mensal: float,
    parcela_total: float,
    data_ultimo_vencimento: date,
    data_operacao: date,
    valor_amort: float,
    modalidade: str,  # 'prazo' | 'parcela'
    calculation_mode: str = "SAC",  # 'SAC' | 'itau'
    tr_estimada_mensal: float = 0.0,
) -> dict:
    """
    Simula o impacto de uma amortização extraordinária.

    Modos:
      SAC + prazo:   mantém amortizacao_mensal, reduz prazo
      SAC + parcela: mantém prazo, reduz amortizacao_mensal
      itau:          mantém parcela ≈ constante, aumenta amortizacao, reduz prazo

    Returns:
        AmortizationResult como dict
    """
    pro_rata = compute_pro_rata(saldo, taxa_mensal, data_ultimo_vencimento, data_operacao, tr_estimada_mensal)

    saldo_novo = saldo - valor_amort + pro_rata["juros_pro_rata"] + pro_rata["atualizacao_tr"]
    if saldo_novo < 0:
        saldo_novo = 0.0

    total_desembolso = valor_amort + pro_rata["juros_pro_rata"] + pro_rata["atualizacao_tr"]

    # Calcular nova amortização e prazo conforme o modo
    if calculation_mode == "itau":
        # Banco mantém parcela ≈ constante, aumenta amortização
        juros_novos = saldo_novo * taxa_mensal
        seguros_estimado = mip_mensal + dfi_mensal
        nova_amortizacao_mensal = parcela_total - juros_novos - seguros_estimado
        nova_amortizacao_mensal = max(nova_amortizacao_mensal, saldo_novo / prazo_remanescente)
        prazo_novo = math.ceil(saldo_novo / nova_amortizacao_mensal) if nova_amortizacao_mensal > 0 else prazo_remanescente
        prazo_inalterado = False

    elif modalidade == "prazo":
        # SAC redução de prazo: mantém amortização, comprime prazo
        nova_amortizacao_mensal = amortizacao_mensal
        prazo_novo = math.floor(saldo_novo / nova_amortizacao_mensal) if nova_amortizacao_mensal > 0 else 0
        prazo_inalterado = False

    else:
        # SAC redução de parcela: mantém prazo, reduz amortização
        nova_amortizacao_mensal = saldo_novo / prazo_remanescente
        prazo_novo = prazo_remanescente
        prazo_inalterado = True

    parcelas_eliminadas = max(0, prazo_remanescente - prazo_novo)

    # Nova parcela (próxima)
    juros_nova = saldo_novo * taxa_mensal
    nova_parcela_proxima = nova_amortizacao_mensal + juros_nova + mip_mensal + dfi_mensal

    # Data de quitação nova
    data_ultima_parcela_nova = add_months(data_operacao, prazo_novo)

    # Economia de juros (nominal)
    # Juros que teria pago sem a amortização:
    juros_sem_amort = _total_interest_sac(saldo, taxa_mensal, amortizacao_mensal, prazo_remanescente)
    # Juros que vai pagar com a amortização:
    juros_com_amort = _total_interest_sac(saldo_novo, taxa_mensal, nova_amortizacao_mensal, prazo_novo)
    juros_economizados_nominal = juros_sem_amort - juros_com_amort

    # Seguros economizados (MIP+DFI × parcelas eliminadas)
    seguros_por_parcela = (mip_mensal + dfi_mensal)
    seguros_economizados = parcelas_eliminadas * seguros_por_parcela

    # Juros economizados em valor presente (desconta à própria taxa)
    juros_economizados_vp = _present_value(juros_economizados_nominal, taxa_mensal, prazo_remanescente / 2)

    # Retorno efetivo anual da operação
    retorno_aa = (1 + taxa_mensal) ** 12 - 1

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
        "juros_economizados_nominal": round(juros_economizados_nominal, 2),
        "juros_economizados_vp": round(juros_economizados_vp, 2),
        "retorno_efetivo_aa": round(retorno_aa, 6),
        "data_nova_quitacao": data_ultima_parcela_nova,
    }


# ── Projeção de cenário ─────────────────────────────────────────────────────────

def project_scenario(
    saldo: float,
    prazo_remanescente: int,
    taxa_mensal: float,
    amortizacao_mensal: float,
    mip_mensal: float,
    dfi_mensal: float,
    data_proxima_parcela: date,
    aporte_mensal_extra: float = 0.0,
    aporte_anual_extra: float = 0.0,
    mes_aporte_anual: int | None = None,
    meses_aporte_extra: list[int] | None = None,
    data_inicio_aportes: date | None = None,
    fgts_eventos: list[dict] | None = None,
) -> dict:
    """
    Projeta o cenário mês a mês e retorna a ScenarioProjection completa.

    A projeção assume:
    - Amortização regular = amortizacao_mensal (fixa, do último DDC)
    - Aportes extras reduzem o saldo diretamente
    - Após cada aporte, o prazo é recalculado (modo SAC com redução de prazo)

    Args:
        meses_aporte_extra: lista de meses (1-12) em que o aporte_mensal_extra é aplicado.
            Se None ou vazio, aplica todo mês. Ex: [2,4,6,8,10,12] para meses pares.

    Returns:
        ScenarioProjection como dict
    """
    fgts_eventos = fgts_eventos or []
    fgts_usados = set()

    saldo_corrente = saldo
    total_juros = 0.0
    total_amort_extra_mensal = 0.0
    total_amort_extra_anual = 0.0
    total_fgts = 0.0
    comprometimento_max = 0.0

    schedule_por_ano: dict[int, dict] = {}
    data_corrente = data_proxima_parcela
    mes_atual = 0
    data_quitacao_final = data_proxima_parcela

    for mes_atual in range(prazo_remanescente + 24):  # +24 margem de segurança
        if saldo_corrente <= 0.01:
            break

        ano = data_corrente.year

        # Inicializar bucket do ano
        if ano not in schedule_por_ano:
            schedule_por_ano[ano] = {
                "ano": ano,
                "parcela_inicio": mes_atual + 1,
                "parcela_fim": mes_atual + 1,
                "saldo_inicio": saldo_corrente,
                "saldo_fim": saldo_corrente,
                "amort_regular": 0.0,
                "amort_extra_mensal": 0.0,
                "amort_extra_anual": 0.0,
                "fgts_aplicado": 0.0,
                "juros_pagos": 0.0,
            }

        # ── Parcela regular ──────────────────────────────────────────────────
        juros = saldo_corrente * taxa_mensal
        amort_reg = min(amortizacao_mensal, saldo_corrente)
        seguros = mip_mensal + dfi_mensal
        parcela = amort_reg + juros + seguros

        saldo_corrente -= amort_reg
        total_juros += juros

        schedule_por_ano[ano]["amort_regular"] += amort_reg
        schedule_por_ano[ano]["juros_pagos"] += juros
        schedule_por_ano[ano]["parcela_fim"] = mes_atual + 1
        comprometimento = parcela

        if saldo_corrente <= 0.01:
            saldo_corrente = 0.0
            data_quitacao_final = data_corrente
            schedule_por_ano[ano]["saldo_fim"] = 0.0
            break

        # ── Aportes extras ───────────────────────────────────────────────────
        aportes_ativos = data_inicio_aportes is None or data_corrente >= data_inicio_aportes

        # Aporte mensal extra: aplica todo mês OU somente nos meses listados
        mes_atual_do_ano = data_corrente.month
        aplicar_extra_mensal = (
            aportes_ativos
            and aporte_mensal_extra > 0
            and (not meses_aporte_extra or mes_atual_do_ano in meses_aporte_extra)
        )

        if aplicar_extra_mensal:
            extra_m = min(aporte_mensal_extra, saldo_corrente)
            saldo_corrente -= extra_m
            total_amort_extra_mensal += extra_m
            schedule_por_ano[ano]["amort_extra_mensal"] += extra_m
            comprometimento += extra_m

        if aportes_ativos and aporte_anual_extra > 0 and mes_aporte_anual == data_corrente.month:
            extra_a = min(aporte_anual_extra, saldo_corrente)
            saldo_corrente -= extra_a
            total_amort_extra_anual += extra_a
            schedule_por_ano[ano]["amort_extra_anual"] += extra_a
            comprometimento += extra_a

        # ── FGTS eventos ─────────────────────────────────────────────────────
        for i, fgts in enumerate(fgts_eventos):
            fgts_date = fgts["data_prevista"] if isinstance(fgts, dict) else fgts.data_prevista
            fgts_valor = fgts["valor_estimado"] if isinstance(fgts, dict) else fgts.valor_estimado
            if i not in fgts_usados and data_corrente >= fgts_date:
                fgts_aplicado = min(fgts_valor, saldo_corrente)
                saldo_corrente -= fgts_aplicado
                total_fgts += fgts_aplicado
                schedule_por_ano[ano]["fgts_aplicado"] += fgts_aplicado
                fgts_usados.add(i)

        comprometimento_max = max(comprometimento_max, comprometimento)
        schedule_por_ano[ano]["saldo_fim"] = max(0.0, saldo_corrente)
        data_quitacao_final = data_corrente

        if saldo_corrente <= 0.01:
            saldo_corrente = 0.0
            break

        data_corrente = add_months(data_corrente, 1)

    # Calcular base (sem extras) para comparação
    juros_base = _total_interest_sac(saldo, taxa_mensal, amortizacao_mensal, prazo_remanescente)
    juros_economizados = juros_base - total_juros

    total_extras = total_amort_extra_mensal + total_amort_extra_anual + total_fgts
    prazo_real = mes_atual + 1 if saldo_corrente <= 0.01 else prazo_remanescente
    parcelas_eliminadas = max(0, prazo_remanescente - prazo_real)

    schedule = [
        {**v, "saldo_inicio": round(v["saldo_inicio"], 2), "saldo_fim": round(v["saldo_fim"], 2),
         "amort_regular": round(v["amort_regular"], 2), "amort_extra_mensal": round(v["amort_extra_mensal"], 2),
         "amort_extra_anual": round(v["amort_extra_anual"], 2), "fgts_aplicado": round(v["fgts_aplicado"], 2),
         "juros_pagos": round(v["juros_pagos"], 2)}
        for v in schedule_por_ano.values()
    ]

    return {
        "data_quitacao": data_quitacao_final,
        "prazo_meses": prazo_real,
        "parcelas_eliminadas": parcelas_eliminadas,
        "total_juros_pagos": round(total_juros, 2),
        "total_juros_economizados": round(juros_economizados, 2),
        "total_extras_investidos": round(total_extras, 2),
        "comprometimento_mensal_max": round(comprometimento_max, 2),
        "schedule": schedule,
    }


def compare_scenarios(
    saldo: float,
    prazo_remanescente: int,
    taxa_mensal: float,
    amortizacao_mensal: float,
    mip_mensal: float,
    dfi_mensal: float,
    data_proxima_parcela: date,
    scenarios: list[dict],
) -> dict:
    """
    Compara até 4 cenários de amortização e retorna análise marginal.
    """
    # Cenário base (sem extras)
    base = project_scenario(
        saldo, prazo_remanescente, taxa_mensal, amortizacao_mensal,
        mip_mensal, dfi_mensal, data_proxima_parcela
    )

    resultados = []
    for params in scenarios:
        proj = project_scenario(
            saldo, prazo_remanescente, taxa_mensal, amortizacao_mensal,
            mip_mensal, dfi_mensal, data_proxima_parcela,
            aporte_mensal_extra=params.get("aporte_mensal_extra", 0),
            aporte_anual_extra=params.get("aporte_anual_extra", 0),
            mes_aporte_anual=params.get("mes_aporte_anual"),
            data_inicio_aportes=params.get("data_inicio_aportes"),
            fgts_eventos=params.get("fgts_eventos", []),
        )
        resultados.append(proj)

    # Análise marginal: cada cenário vs. anterior
    referencia = base
    marginal = []
    for proj in resultados:
        extra = proj["total_extras_investidos"]
        extra_ref = referencia["total_extras_investidos"]
        juros_econ = proj["total_juros_economizados"] - referencia["total_juros_economizados"]
        tempo_cortado = referencia["prazo_meses"] - proj["prazo_meses"]
        retorno = juros_econ / max(extra - extra_ref, 1)

        if retorno > 0.80:
            rec, motivo = "sim", "Retorno alto: cada R$1 extra economiza mais de R$0,80 em juros"
        elif retorno > 0.40:
            rec, motivo = "depende", "Retorno moderado: vale se a liquidez não for necessidade imediata"
        else:
            rec, motivo = "nao", "Retorno marginal baixo: considere diversificar em vez de amortizar"

        marginal.append({
            "extra_investido": round(extra - extra_ref, 2),
            "juros_economizados": round(juros_econ, 2),
            "tempo_cortado_meses": tempo_cortado,
            "retorno_marginal": round(retorno, 4),
            "recomendacao": rec,
            "motivo": motivo,
        })
        referencia = proj

    return {"base": base, "cenarios": resultados, "marginal": marginal}


# ── Planilha parcela a parcela ───────────────────────────────────────────────────

def generate_installment_schedule(
    saldo: float,
    prazo_remanescente: int,
    taxa_mensal: float,
    amortizacao_mensal: float,
    mip_mensal: float,
    dfi_mensal: float,
    data_proxima_parcela: date,
    aporte_mensal_extra: float = 0.0,
    aporte_anual_extra: float = 0.0,
    mes_aporte_anual: int | None = None,
    meses_aporte_extra: list[int] | None = None,
) -> list[dict]:
    """
    Gera planilha completa parcela a parcela até a quitação.
    Cada linha é um mês com: número, data, saldo, amortização, juros,
    seguros, parcela total, extra mensal, extra anual, saldo pós.

    Retorna lista de dicts prontos para CSV/download.
    """
    rows = []
    saldo_corrente = saldo
    data_corrente = data_proxima_parcela
    parcela_num = 1

    for _ in range(prazo_remanescente + 24):  # margem
        if saldo_corrente <= 0.01:
            break

        juros = round(saldo_corrente * taxa_mensal, 2)
        amort_reg = round(min(amortizacao_mensal, saldo_corrente), 2)
        seguros = round(mip_mensal + dfi_mensal, 2)
        parcela = round(amort_reg + juros + seguros, 2)

        extra_m = 0.0
        extra_a = 0.0

        saldo_pos = round(saldo_corrente - amort_reg, 2)

        aplicar_extra = (
            aporte_mensal_extra > 0
            and (not meses_aporte_extra or data_corrente.month in meses_aporte_extra)
        )
        if aplicar_extra:
            extra_m = round(min(aporte_mensal_extra, saldo_pos), 2)
            saldo_pos = round(saldo_pos - extra_m, 2)

        if aporte_anual_extra > 0 and mes_aporte_anual == data_corrente.month:
            extra_a = round(min(aporte_anual_extra, saldo_pos), 2)
            saldo_pos = round(saldo_pos - extra_a, 2)

        saldo_pos = max(0.0, saldo_pos)

        rows.append({
            "parcela": parcela_num,
            "data": str(data_corrente),
            "saldo_anterior": round(saldo_corrente, 2),
            "amortizacao": amort_reg,
            "juros": juros,
            "seguros": seguros,
            "parcela_total": parcela,
            "extra_mensal": extra_m,
            "extra_anual": extra_a,
            "saldo_pos": saldo_pos,
        })

        saldo_corrente = saldo_pos
        data_corrente = add_months(data_corrente, 1)
        parcela_num += 1

        if saldo_corrente <= 0.01:
            break

    return rows


# ── Helpers internos ────────────────────────────────────────────────────────────

def _total_interest_sac(
    saldo: float,
    taxa_mensal: float,
    amortizacao_mensal: float,
    prazo: int,
) -> float:
    """Soma todos os juros pagos num contrato SAC desde o estado atual."""
    s = saldo
    total = 0.0
    for _ in range(prazo):
        if s <= 0:
            break
        total += s * taxa_mensal
        s -= min(amortizacao_mensal, s)
    return total


def _present_value(future_value: float, taxa_mensal: float, periods: float) -> float:
    """Valor presente de um montante futuro descontado à taxa mensal."""
    if taxa_mensal == 0:
        return future_value
    return future_value / ((1 + taxa_mensal) ** periods)
