"""
Router /auth — identidade do usuário.

GET /auth/me → retorna perfil do usuário logado.
  Se for o primeiro login, cria o user_profile automaticamente.
"""

import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.user import UserProfile
from db.rls import get_rls_session
from middleware.auth import get_current_user_id

router = APIRouter(prefix="/auth", tags=["auth"])


class MeResponse(BaseModel):
    id: str
    nome: str | None


@router.get("/me", response_model=MeResponse)
async def get_me(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_rls_session),
) -> MeResponse:
    """
    Retorna o perfil do usuário autenticado.
    Cria um user_profile vazio no primeiro login.
    """
    uid = uuid.UUID(user_id)

    result = await session.execute(
        select(UserProfile).where(UserProfile.id == uid)
    )
    profile = result.scalar_one_or_none()

    if profile is None:
        profile = UserProfile(id=uid)
        session.add(profile)
        await session.commit()
        await session.refresh(profile)

    return MeResponse(id=str(profile.id), nome=profile.nome)
