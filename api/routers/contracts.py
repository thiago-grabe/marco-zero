"""
Router /contracts — CRUD de contratos + estado calculado pelo motor.

Cada resposta inclui campos computados pelo motor SAC/PRICE:
  taxa_anual_efetiva, parcela_total, juros_proxima, data_quitacao.
"""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.contract import Contract, Property
from db.rls import get_rls_session
from middleware.auth import get_current_user_id
from models.contract import (
    ContractCreate,
    ContractResponse,
    ContractUpdate,
    QuickContractCreate,
    QuickContractResponse,
)
from motor import sac
from motor.estimator import estimate_from_minimal

router = APIRouter(prefix="/contracts", tags=["contracts"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_response(contract: Contract) -> ContractResponse:
    """Adiciona campos computados pelo motor ao model ORM."""
    taxa = float(contract.taxa_mensal)
    saldo = float(contract.saldo_devedor)
    amort = float(contract.amortizacao_mensal)
    mip = float(contract.mip_mensal)
    dfi = float(contract.dfi_mensal)
    prazo = contract.prazo_remanescente

    juros_proxima = round(saldo * taxa, 2)
    seguros = round(mip + dfi, 2)

    # Custos extras não mapeados
    extras_raw = contract.custos_extras or []
    from models.contract import CustoExtra
    custos_extras = [CustoExtra(**e) if isinstance(e, dict) else e for e in extras_raw]
    custos_extras_total = round(sum(e.valor if hasattr(e, 'valor') else e.get("valor", 0) for e in extras_raw), 2)

    parcela_total = round(amort + juros_proxima + seguros + custos_extras_total, 2)
    taxa_anual = round((1 + taxa) ** 12 - 1, 6)

    # Projeção base para data de quitação
    proj = sac.project_scenario(
        saldo=saldo,
        prazo_remanescente=prazo,
        taxa_mensal=taxa,
        amortizacao_mensal=amort,
        mip_mensal=mip,
        dfi_mensal=dfi,
        data_proxima_parcela=contract.data_proxima_parcela,
    )

    return ContractResponse(
        id=contract.id,
        property_id=contract.property_id,
        apelido=contract.apelido,
        banco=contract.banco,
        sistema_amortizacao=contract.sistema_amortizacao,
        taxa_mensal=taxa,
        taxa_anual_efetiva=taxa_anual,
        saldo_devedor=saldo,
        amortizacao_mensal=amort,
        mip_mensal=mip,
        dfi_mensal=dfi,
        seguros_mensal=seguros,
        custos_extras=custos_extras,
        custos_extras_total=custos_extras_total,
        parcela_total=parcela_total,
        juros_proxima=juros_proxima,
        data_proxima_parcela=contract.data_proxima_parcela,
        prazo_remanescente=prazo,
        data_quitacao=proj["data_quitacao"],
        valor_original=float(contract.valor_original) if contract.valor_original else None,
        data_inicio=contract.data_inicio,
        created_at=contract.created_at,
    )


async def _get_contract_or_404(
    contract_id: str,
    user_id: str,
    session: AsyncSession,
) -> Contract:
    result = await session.execute(
        select(Contract).where(
            Contract.id == uuid.UUID(contract_id),
            Contract.user_id == uuid.UUID(user_id),
        )
    )
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrato não encontrado")
    return contract


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[ContractResponse])
async def list_contracts(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_rls_session),
) -> list[ContractResponse]:
    result = await session.execute(
        select(Contract)
        .where(Contract.user_id == uuid.UUID(user_id))
        .order_by(Contract.created_at.desc())
    )
    contracts = result.scalars().all()
    return [_build_response(c) for c in contracts]


@router.post("", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(
    body: ContractCreate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_rls_session),
) -> ContractResponse:
    """
    Cria imóvel + contrato num único request (fluxo do onboarding).
    """
    uid = uuid.UUID(user_id)

    prop = Property(user_id=uid, apelido=body.property_apelido)
    session.add(prop)
    await session.flush()  # obtém prop.id antes de criar o contrato

    contract = Contract(
        user_id=uid,
        property_id=prop.id,
        apelido=body.apelido,
        banco=body.banco,
        sistema_amortizacao=body.sistema_amortizacao,
        taxa_mensal=body.taxa_mensal,
        saldo_devedor=body.saldo_devedor,
        amortizacao_mensal=body.amortizacao_mensal,
        mip_mensal=body.mip_mensal,
        dfi_mensal=body.dfi_mensal,
        data_proxima_parcela=body.data_proxima_parcela,
        prazo_remanescente=body.prazo_remanescente,
        custos_extras=[e.model_dump() for e in body.custos_extras],
        valor_original=body.valor_original,
        data_inicio=body.data_inicio,
    )
    session.add(contract)
    await session.commit()
    await session.refresh(contract)

    return _build_response(contract)


@router.post("/quick", response_model=QuickContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract_quick(
    body: QuickContractCreate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_rls_session),
) -> QuickContractResponse:
    """
    Caminho de massa: 3 campos obrigatórios + taxa opcional.
    Se a taxa for informada, o cálculo é exato. Se não, é estimado.
    """
    uid = uuid.UUID(user_id)

    # Estimar campos faltantes
    estimated = estimate_from_minimal(
        parcela_mensal=body.parcela_mensal,
        saldo_devedor=body.saldo_devedor,
    )

    # Se a taxa foi informada pelo usuário, usa a real e recalcula
    campos_estimados = [
        "amortizacao_mensal", "prazo_remanescente",
        "sistema_amortizacao", "data_proxima_parcela", "mip_mensal", "dfi_mensal",
    ]

    if body.taxa_mensal is not None:
        # Taxa informada → cálculo exato
        taxa = body.taxa_mensal
        import math
        from motor.sac import add_months
        from datetime import date

        juros = body.saldo_devedor * taxa
        seguros_est = body.parcela_mensal * 0.02
        amort = body.parcela_mensal - juros - seguros_est
        if amort > 0:
            prazo = max(1, round(body.saldo_devedor / amort))
        else:
            prazo = estimated["prazo_remanescente"]
            amort = estimated["amortizacao_mensal"]

        estimated["taxa_mensal"] = taxa
        estimated["amortizacao_mensal"] = round(amort, 2)
        estimated["prazo_remanescente"] = prazo
        # taxa NÃO é estimada nesse caso
    else:
        campos_estimados.insert(0, "taxa_mensal")

    prop = Property(user_id=uid, apelido="Apartamento")
    session.add(prop)
    await session.flush()

    contract = Contract(
        user_id=uid,
        property_id=prop.id,
        banco=body.banco,
        sistema_amortizacao=estimated["sistema_amortizacao"],
        taxa_mensal=estimated["taxa_mensal"],
        saldo_devedor=body.saldo_devedor,
        amortizacao_mensal=estimated["amortizacao_mensal"],
        mip_mensal=estimated["mip_mensal"],
        dfi_mensal=estimated["dfi_mensal"],
        data_proxima_parcela=estimated["data_proxima_parcela"],
        prazo_remanescente=estimated["prazo_remanescente"],
    )
    session.add(contract)
    await session.commit()
    await session.refresh(contract)

    response = _build_response(contract)
    return QuickContractResponse(
        **response.model_dump(),
        campos_estimados=campos_estimados,
    )


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: str,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_rls_session),
) -> ContractResponse:
    contract = await _get_contract_or_404(contract_id, user_id, session)
    return _build_response(contract)


@router.patch("/{contract_id}", response_model=ContractResponse)
async def update_contract(
    contract_id: str,
    body: ContractUpdate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_rls_session),
) -> ContractResponse:
    contract = await _get_contract_or_404(contract_id, user_id, session)

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(contract, field, value)

    await session.commit()
    await session.refresh(contract)
    return _build_response(contract)


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contract(
    contract_id: str,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_rls_session),
) -> None:
    contract = await _get_contract_or_404(contract_id, user_id, session)
    await session.delete(contract)
    await session.commit()
