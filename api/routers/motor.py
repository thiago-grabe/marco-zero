"""
Router /motor — endpoints de cálculo (chamados pelos sliders do frontend).

Todos os endpoints recebem ContractState diretamente (sem DB lookup)
para máxima performance nos sliders com debounce.
"""

from datetime import date

from fastapi import APIRouter
from pydantic import BaseModel

from models.motor import (
    AmortizationMode,
    AmortizationResult,
    CompareRequest,
    InstallmentBreakdown,
    ProjectRequest,
    ScenarioComparison,
    ScenarioProjection,
)
from motor import sac

router = APIRouter(prefix="/motor", tags=["motor"])


class InstallmentRequest(BaseModel):
    saldo: float
    prazo_remanescente: int
    taxa_mensal: float
    mip: float
    dfi: float


class ProRataRequest(BaseModel):
    saldo: float
    taxa_mensal: float
    data_ultimo_vencimento: date
    data_operacao: date


class AmortizationSimRequest(BaseModel):
    saldo: float
    prazo_remanescente: int
    taxa_mensal: float
    amortizacao_mensal: float
    mip_mensal: float
    dfi_mensal: float
    parcela_total: float
    data_ultimo_vencimento: date
    data_operacao: date
    valor_amort: float
    modalidade: AmortizationMode
    calculation_mode: str = "SAC"


class ProjectDirectRequest(BaseModel):
    """Projeção direto dos parâmetros (sem buscar DB — para sliders)."""
    saldo: float
    prazo_remanescente: int
    taxa_mensal: float
    amortizacao_mensal: float
    mip_mensal: float
    dfi_mensal: float
    data_proxima_parcela: date
    aporte_mensal_extra: float = 0.0
    aporte_anual_extra: float = 0.0
    mes_aporte_anual: int | None = None
    fgts_eventos: list[dict] = []


@router.post("/installment", response_model=InstallmentBreakdown)
async def compute_installment(req: InstallmentRequest):
    """Calcula os componentes de uma parcela SAC."""
    result = sac.compute_installment(
        req.saldo, req.prazo_remanescente, req.taxa_mensal, req.mip, req.dfi
    )
    return result


@router.post("/pro-rata")
async def compute_pro_rata(req: ProRataRequest):
    """Calcula juros pró-rata entre dois vencimentos."""
    return sac.compute_pro_rata(
        req.saldo, req.taxa_mensal,
        req.data_ultimo_vencimento, req.data_operacao
    )


@router.post("/simulate-amortization")
async def simulate_amortization(req: AmortizationSimRequest):
    """Simula o impacto de uma amortização extraordinária."""
    return sac.simulate_amortization(
        saldo=req.saldo,
        prazo_remanescente=req.prazo_remanescente,
        taxa_mensal=req.taxa_mensal,
        amortizacao_mensal=req.amortizacao_mensal,
        mip_mensal=req.mip_mensal,
        dfi_mensal=req.dfi_mensal,
        parcela_total=req.parcela_total,
        data_ultimo_vencimento=req.data_ultimo_vencimento,
        data_operacao=req.data_operacao,
        valor_amort=req.valor_amort,
        modalidade=req.modalidade.value,
        calculation_mode=req.calculation_mode,
    )


@router.post("/project", response_model=ScenarioProjection)
async def project_scenario(req: ProjectDirectRequest):
    """
    Projeta cenário de amortização mês a mês.
    Usado pelos sliders em tempo real (com debounce de 200ms no frontend).
    """
    result = sac.project_scenario(
        saldo=req.saldo,
        prazo_remanescente=req.prazo_remanescente,
        taxa_mensal=req.taxa_mensal,
        amortizacao_mensal=req.amortizacao_mensal,
        mip_mensal=req.mip_mensal,
        dfi_mensal=req.dfi_mensal,
        data_proxima_parcela=req.data_proxima_parcela,
        aporte_mensal_extra=req.aporte_mensal_extra,
        aporte_anual_extra=req.aporte_anual_extra,
        mes_aporte_anual=req.mes_aporte_anual,
        fgts_eventos=req.fgts_eventos,
    )
    return result


@router.post("/compare")
async def compare_scenarios(req: CompareRequest):
    """Compara até 4 cenários e retorna análise marginal."""
    # TODO: buscar ContractState do DB pelo contract_id
    return {"detail": "Implementar: buscar ContractState do DB para compare_scenarios"}


@router.post("/schedule")
async def generate_schedule(req: ProjectDirectRequest):
    """
    Gera planilha completa parcela a parcela até a quitação.
    Retorna array com uma linha por mês: parcela, data, saldo, amortização,
    juros, seguros, extras, saldo pós-pagamento.

    Usado pelo frontend para download de CSV.
    """
    rows = sac.generate_installment_schedule(
        saldo=req.saldo,
        prazo_remanescente=req.prazo_remanescente,
        taxa_mensal=req.taxa_mensal,
        amortizacao_mensal=req.amortizacao_mensal,
        mip_mensal=req.mip_mensal,
        dfi_mensal=req.dfi_mensal,
        data_proxima_parcela=req.data_proxima_parcela,
        aporte_mensal_extra=req.aporte_mensal_extra,
        aporte_anual_extra=req.aporte_anual_extra,
        mes_aporte_anual=req.mes_aporte_anual,
    )
    return rows
