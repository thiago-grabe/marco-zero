"""
Pydantic models para o motor de cálculo.
Esses modelos são o contrato entre a API e a camada de compute.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────────────────────────

class CalculationMode(str, Enum):
    SAC = "SAC"
    PRICE = "PRICE"
    ITAU = "itau"  # mantém prestação constante, comprime prazo


class AmortizationMode(str, Enum):
    PRAZO = "prazo"      # reduz prazo, mantém amortização
    PARCELA = "parcela"  # reduz parcela, mantém prazo


# ── Estado do contrato ─────────────────────────────────────────────────────────

class ContractState(BaseModel):
    """Estado completo do contrato — base para todas as Tools de Compute."""

    contract_id: str
    banco_code: str
    banco_display: str
    modalidade_code: str | None = None
    index_rate_code: str | None = None

    amortization_system: Literal["SAC", "PRICE"]
    calculation_mode: CalculationMode

    taxa_mensal: float = Field(gt=0, lt=0.02, description="Ex: 0.009631393")
    taxa_anual_efetiva: float = Field(gt=0, lt=0.30)

    saldo_devedor: float = Field(gt=0)
    valor_original: float | None = None
    data_inicio: date | None = None

    amortizacao_mensal: float = Field(gt=0)
    juros_proxima: float = Field(gt=0)
    mip_mensal: float = Field(ge=0)
    dfi_mensal: float = Field(ge=0)
    seguros_mensal: float = Field(ge=0)
    parcela_total: float = Field(gt=0)

    data_proxima_parcela: date
    prazo_remanescente: int = Field(gt=0)
    data_quitacao: date

    ultima_ddc_data: date
    ultima_ddc_versao: int = Field(ge=1)
    numero_amortizacoes_extra: int = Field(ge=0, default=0)
    total_amortizado_extra: float = Field(ge=0, default=0.0)
    scenario_em_execucao_id: str | None = None


# ── Parcela ────────────────────────────────────────────────────────────────────

class InstallmentBreakdown(BaseModel):
    amortizacao: float
    juros: float
    mip: float
    dfi: float
    seguros: float
    total: float


# ── Pró-rata ───────────────────────────────────────────────────────────────────

class ProRataResult(BaseModel):
    dias_decorridos: int
    juros_pro_rata: float
    atualizacao_tr: float
    total_acrescimo: float


# ── Amortização extraordinária ─────────────────────────────────────────────────

class AmortizationResult(BaseModel):
    # Desembolso real
    saldo_novo: float
    juros_pro_rata: float
    atualizacao_monetaria: float
    total_desembolso: float

    # Impacto no contrato
    prazo_novo: int
    parcelas_eliminadas: int
    nova_amortizacao_mensal: float
    nova_parcela_proxima: float
    prazo_inalterado: bool

    # Economia
    seguros_economizados: float
    juros_economizados_nominal: float
    juros_economizados_vp: float
    retorno_efetivo_aa: float
    data_nova_quitacao: date


# ── Cenários ───────────────────────────────────────────────────────────────────

class FgtsEvento(BaseModel):
    data_prevista: date
    valor_estimado: float = Field(gt=0)


class ScenarioParams(BaseModel):
    aporte_mensal_extra: float = Field(ge=0, default=0.0)
    aporte_anual_extra: float = Field(ge=0, default=0.0)
    mes_aporte_anual: int | None = Field(default=None, ge=1, le=12)
    data_inicio_aportes: date | None = None
    fgts_eventos: list[FgtsEvento] = Field(default_factory=list)


class YearSummary(BaseModel):
    ano: int
    parcela_inicio: int
    parcela_fim: int
    saldo_inicio: float
    saldo_fim: float
    amort_regular: float
    amort_extra_mensal: float
    amort_extra_anual: float
    fgts_aplicado: float
    juros_pagos: float


class ScenarioProjection(BaseModel):
    data_quitacao: date
    prazo_meses: int
    parcelas_eliminadas: int
    total_juros_pagos: float
    total_juros_economizados: float
    total_extras_investidos: float
    comprometimento_mensal_max: float
    schedule: list[YearSummary]


class MarginalAnalysis(BaseModel):
    extra_investido: float
    juros_economizados: float
    tempo_cortado_meses: int
    retorno_marginal: float
    recomendacao: Literal["sim", "depende", "nao"]
    motivo: str


class ScenarioComparison(BaseModel):
    base: ScenarioProjection
    cenarios: list[ScenarioProjection]
    marginal: list[MarginalAnalysis]


# ── Requests da API ────────────────────────────────────────────────────────────

class ProjectRequest(BaseModel):
    contract_id: str
    params: ScenarioParams


class AmortizationRequest(BaseModel):
    contract_id: str
    valor: float = Field(gt=0)
    modalidade: AmortizationMode
    data: date


class CompareRequest(BaseModel):
    contract_id: str
    scenarios: list[ScenarioParams] = Field(min_length=1, max_length=4)
