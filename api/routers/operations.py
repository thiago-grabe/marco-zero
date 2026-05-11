"""
Router /contracts/:id/operations — amortizações declaradas pelo usuário.

Quando uma operação é registrada, o contrato é atualizado automaticamente:
  - saldo_devedor -= valor_principal
  - prazo_remanescente recalculado via motor (modo redução de prazo SAC)
"""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.contract import Contract
from db.models.operation import UserOperation
from db.rls import get_rls_session
from middleware.auth import get_current_user_id
from models.contract import OperationCreate, OperationResponse
from motor import sac

router = APIRouter(tags=["operations"])


async def _get_contract_or_404(contract_id: str, user_id: str, session: AsyncSession) -> Contract:
    from fastapi import HTTPException
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


@router.get("/contracts/{contract_id}/operations", response_model=list[OperationResponse])
async def list_operations(
    contract_id: str,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_rls_session),
) -> list[OperationResponse]:
    await _get_contract_or_404(contract_id, user_id, session)

    result = await session.execute(
        select(UserOperation)
        .where(UserOperation.contract_id == uuid.UUID(contract_id))
        .order_by(UserOperation.data_operacao.desc())
    )
    return result.scalars().all()


@router.post(
    "/contracts/{contract_id}/operations",
    response_model=OperationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_operation(
    contract_id: str,
    body: OperationCreate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_rls_session),
) -> OperationResponse:
    """
    Registra uma amortização extraordinária e atualiza o contrato.

    Após registrar:
      - saldo_devedor é reduzido pelo valor_principal
      - prazo_remanescente é recalculado pelo motor SAC
      - data_proxima_parcela avança para o próximo vencimento
    """
    contract = await _get_contract_or_404(contract_id, user_id, session)

    # Persistir a operação
    op = UserOperation(
        user_id=uuid.UUID(user_id),
        contract_id=contract.id,
        tipo=body.tipo,
        data_operacao=body.data_operacao,
        valor_principal=body.valor_principal,
        notas=body.notas,
    )
    session.add(op)

    # Atualizar estado do contrato via motor
    sim = sac.simulate_amortization(
        saldo=float(contract.saldo_devedor),
        prazo_remanescente=contract.prazo_remanescente,
        taxa_mensal=float(contract.taxa_mensal),
        amortizacao_mensal=float(contract.amortizacao_mensal),
        mip_mensal=float(contract.mip_mensal),
        dfi_mensal=float(contract.dfi_mensal),
        parcela_total=float(contract.amortizacao_mensal)
                       + float(contract.taxa_mensal) * float(contract.saldo_devedor)
                       + float(contract.mip_mensal) + float(contract.dfi_mensal),
        data_ultimo_vencimento=contract.data_proxima_parcela,
        data_operacao=body.data_operacao,
        valor_amort=body.valor_principal,
        modalidade=body.tipo.replace("amortizacao_", ""),  # prazo | parcela
        calculation_mode="SAC",
    )

    contract.saldo_devedor = sim["saldo_novo"]
    contract.prazo_remanescente = sim["prazo_novo"]
    contract.amortizacao_mensal = sim["nova_amortizacao_mensal"]

    await session.commit()
    await session.refresh(op)

    return op
