"""
Router /auth — registro e login local.

POST /auth/register → cria conta (email + senha)
POST /auth/login    → retorna JWT
GET  /auth/me       → retorna perfil do usuário logado
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
import bcrypt as _bcrypt


class _pwd:
    @staticmethod
    def hash(password: str) -> str:
        return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()

    @staticmethod
    def verify(password: str, hashed: str) -> bool:
        return _bcrypt.checkpw(password.encode(), hashed.encode())
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import async_session_factory, get_session
from db.models.user import UserProfile
from db.rls import get_rls_session
from middleware.auth import create_access_token, get_current_user_id

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: str
    password: str
    nome: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user_id: str
    email: str


class MeResponse(BaseModel):
    id: str
    email: str | None
    nome: str | None


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    body: RegisterRequest,
    session: AsyncSession = Depends(get_session),
) -> AuthResponse:
    """Cria conta com email e senha. Retorna JWT."""
    result = await session.execute(
        select(UserProfile).where(UserProfile.email == body.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="E-mail já registrado")

    user = UserProfile(
        email=body.email,
        password_hash=_pwd.hash(body.password),
        nome=body.nome,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    token = create_access_token(str(user.id))
    return AuthResponse(token=token, user_id=str(user.id), email=user.email)


@router.post("/login", response_model=AuthResponse)
async def login(
    body: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> AuthResponse:
    """Login com email e senha. Retorna JWT."""
    result = await session.execute(
        select(UserProfile).where(UserProfile.email == body.email)
    )
    user = result.scalar_one_or_none()

    if not user or not user.password_hash or not _pwd.verify(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")

    token = create_access_token(str(user.id))
    return AuthResponse(token=token, user_id=str(user.id), email=user.email)


@router.get("/me", response_model=MeResponse)
async def get_me(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_rls_session),
) -> MeResponse:
    uid = uuid.UUID(user_id)
    result = await session.execute(
        select(UserProfile).where(UserProfile.id == uid)
    )
    profile = result.scalar_one_or_none()

    if profile is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return MeResponse(id=str(profile.id), email=profile.email, nome=profile.nome)
