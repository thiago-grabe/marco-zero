"""
Router /contracts/:id/scenarios — CRUD de cenários.

Resultados (projeção) são calculados em runtime pelo motor — não persistidos.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.contract import Contract
from db.models.scenario import Scenario
from db.rls import get_rls_session
from middleware.auth import get_current_user_id
from models.motor import ScenarioProjection
from models.scenario import ScenarioCreate, ScenarioResponse, ScenarioUpdate
from motor import sac

router = APIRouter(tags=["scenarios"])


class ScenarioWithProjection(ScenarioResponse):
    projecao: ScenarioProjection


async def _get_contract_or_404(contract_id: str, user_id: str, session: AsyncSession) -> Contract:
    result = await session.execute(
        select(Contract).where(
            Contract.id == uuid.UUID(contract_id),
            Contract.user_id == uuid.UUID(user_id),
        )
    )
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    return contract


async def _get_scenario_or_404(scenario_id: str, user_id: str, session: AsyncSession) -> Scenario:
    result = await session.execute(
        select(Scenario).where(
            Scenario.id == uuid.UUID(scenario_id),
            Scenario.user_id == uuid.UUID(user_id),
        )
    )
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(status_code=404, detail="Cenário não encontrado")
    return scenario


def _compute_projection(scenario: Scenario, contract: Contract) -> ScenarioProjection:
    result = sac.project_scenario(
        saldo=float(contract.saldo_devedor),
        prazo_remanescente=contract.prazo_remanescente,
        taxa_mensal=float(contract.taxa_mensal),
        amortizacao_mensal=float(contract.amortizacao_mensal),
        mip_mensal=float(contract.mip_mensal),
        dfi_mensal=float(contract.dfi_mensal),
        data_proxima_parcela=contract.data_proxima_parcela,
        aporte_mensal_extra=float(scenario.aporte_mensal_extra),
        aporte_anual_extra=float(scenario.aporte_anual_extra),
        mes_aporte_anual=scenario.mes_aporte_anual,
    )
    return ScenarioProjection(**result)


@router.get("/contracts/{contract_id}/scenarios", response_model=list[ScenarioWithProjection])
async def list_scenarios(
    contract_id: str,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_rls_session),
) -> list[ScenarioWithProjection]:
    contract = await _get_contract_or_404(contract_id, user_id, session)

    result = await session.execute(
        select(Scenario)
        .where(Scenario.contract_id == uuid.UUID(contract_id))
        .order_by(Scenario.created_at.asc())
    )
    scenarios = result.scalars().all()

    return [
        ScenarioWithProjection(
            **ScenarioResponse.model_validate(s).model_dump(),
            projecao=_compute_projection(s, contract),
        )
        for s in scenarios
    ]


@router.post(
    "/contracts/{contract_id}/scenarios",
    response_model=ScenarioWithProjection,
    status_code=status.HTTP_201_CREATED,
)
async def create_scenario(
    contract_id: str,
    body: ScenarioCreate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_rls_session),
) -> ScenarioWithProjection:
    contract = await _get_contract_or_404(contract_id, user_id, session)
    uid = uuid.UUID(user_id)

    scenario = Scenario(
        user_id=uid,
        contract_id=contract.id,
        nome=body.nome,
        aporte_mensal_extra=body.aporte_mensal_extra,
        aporte_anual_extra=body.aporte_anual_extra,
        mes_aporte_anual=body.mes_aporte_anual,
    )
    session.add(scenario)
    await session.commit()
    await session.refresh(scenario)

    return ScenarioWithProjection(
        **ScenarioResponse.model_validate(scenario).model_dump(),
        projecao=_compute_projection(scenario, contract),
    )


@router.patch("/scenarios/{scenario_id}", response_model=ScenarioWithProjection)
async def update_scenario(
    scenario_id: str,
    body: ScenarioUpdate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_rls_session),
) -> ScenarioWithProjection:
    scenario = await _get_scenario_or_404(scenario_id, user_id, session)

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(scenario, field, value)

    await session.commit()
    await session.refresh(scenario)

    # Busca o contrato para recomputar projeção
    result = await session.execute(
        select(Contract).where(Contract.id == scenario.contract_id)
    )
    contract = result.scalar_one()

    return ScenarioWithProjection(
        **ScenarioResponse.model_validate(scenario).model_dump(),
        projecao=_compute_projection(scenario, contract),
    )


@router.delete("/scenarios/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scenario(
    scenario_id: str,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_rls_session),
) -> None:
    scenario = await _get_scenario_or_404(scenario_id, user_id, session)
    await session.delete(scenario)
    await session.commit()
