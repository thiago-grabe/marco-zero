from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import async_session_factory
from middleware.auth import get_current_user_id


async def get_rls_session(
    user_id: str = Depends(get_current_user_id),
) -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency: abre sessão e injeta user_id via SET LOCAL.
    O Postgres usa current_setting('app.current_user_id') nas políticas RLS.
    """
    async with async_session_factory() as session:
        # SET LOCAL não aceita parâmetros posicionais no Postgres.
        # user_id já foi validado como UUID pelo middleware — interpolação é segura.
        import uuid as _uuid
        _uuid.UUID(user_id)  # levanta ValueError se não for UUID válido
        await session.execute(text(f"SET LOCAL \"app.current_user_id\" = '{user_id}'"))
        yield session
