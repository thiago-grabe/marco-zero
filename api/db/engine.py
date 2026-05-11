from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import settings
from db.models.base import Base

# Importar todos os modelos para que o Base.metadata os inclua
import db.models  # noqa: F401

engine = create_async_engine(
    settings.database_url,
    echo=settings.is_dev,
    pool_size=10,
    max_overflow=20,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session
