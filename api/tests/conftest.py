"""
Fixtures de teste para Marco Zero API.

Estratégia de isolamento:
  - NullPool: cada teste usa uma conexão fresh, sem estado de pool.
  - Truncate autouse: tabelas limpas após cada teste.
  - Dependency override: auth e sessão de DB injetados nos testes.

Banco: postgresql+asyncpg://73983@localhost:5432/marco_zero_test
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from main import app
from middleware.auth import get_current_user_id
from db.rls import get_rls_session
from db.engine import get_session
import db.models  # noqa — registra todos os models no Base.metadata

# ── Config de teste ────────────────────────────────────────────────────────────

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5490/marco_zero_test"
TEST_USER_ID = "00000000-0000-0000-0000-000000000001"

# NullPool: conexão fresh por operação, zero estado entre testes
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
TestSession = async_sessionmaker(test_engine, expire_on_commit=False)

# ── Contrato de referência (dados reais do Thiago, DDC 05/05/2026) ─────────────

CONTRACT_PAYLOAD = {
    "property_apelido": "Apartamento Contagem",
    "banco": "itau",
    "sistema_amortizacao": "SAC",
    "taxa_mensal": 0.009631393,
    "saldo_devedor": 429629.87,
    "amortizacao_mensal": 2285.27,
    "mip_mensal": 94.45,
    "dfi_mensal": 38.61,
    "data_proxima_parcela": "2026-05-21",
    "prazo_remanescente": 189,
    "valor_original": 536000.0,
    "data_inicio": "2025-12-21",
}

# Tabelas em ordem topológica (FK-safe para truncate)
TABLES_TO_TRUNCATE = [
    "user_operations",
    "scenarios",
    "contracts",
    "properties",
    "user_profiles",
]


# ── Limpeza automática após cada teste ────────────────────────────────────────

@pytest_asyncio.fixture(autouse=True)
async def truncate_tables():
    """Limpa todas as tabelas após cada teste. Roda automaticamente."""
    yield
    async with test_engine.begin() as conn:
        for table in TABLES_TO_TRUNCATE:
            await conn.execute(text(f'TRUNCATE TABLE "{table}" CASCADE'))


# ── Fixtures de banco e cliente ────────────────────────────────────────────────

@pytest_asyncio.fixture
async def client():
    """
    AsyncClient com auth fixo (TEST_USER_ID) e sessão de test_engine.
    O SET LOCAL para RLS é feito dentro de cada sessão aberta pela dependency.
    """

    async def override_user_id() -> str:
        return TEST_USER_ID

    async def override_rls() -> AsyncSession:
        """
        Sessão com RLS configurado para o usuário de teste.

        Usa SET (não SET LOCAL) porque:
        - SET persiste durante toda a vida da conexão, independente de transações
        - Com NullPool cada sessão tem sua própria conexão — zero contaminação
        - Compatível com session.commit() dentro dos routers (não conflita)
        """
        async with TestSession() as session:
            await session.execute(
                text(f"SET \"app.current_user_id\" = '{TEST_USER_ID}'")
            )
            yield session

    async def override_plain_session() -> AsyncSession:
        """Session sem RLS — usada por /auth/register e /auth/login."""
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_current_user_id] = override_user_id
    app.dependency_overrides[get_rls_session] = override_rls
    app.dependency_overrides[get_session] = override_plain_session

    # Criar o usuário de teste no banco (necessário para /auth/me e RLS)
    async with TestSession() as seed_session:
        await seed_session.execute(
            text(f"SET \"app.current_user_id\" = '{TEST_USER_ID}'")
        )
        from db.models.user import UserProfile
        import uuid as _uuid
        existing = await seed_session.execute(
            select(UserProfile).where(UserProfile.id == _uuid.UUID(TEST_USER_ID))
        )
        if not existing.scalar_one_or_none():
            seed_session.add(UserProfile(
                id=_uuid.UUID(TEST_USER_ID),
                email="test@marco-zero.dev",
                nome="Test User",
            ))
            await seed_session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c

    app.dependency_overrides.clear()


# ── Fixtures de dados ──────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def contract(client: AsyncClient) -> dict:
    """Cria e retorna o contrato de referência."""
    resp = await client.post("/contracts", json=CONTRACT_PAYLOAD)
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest_asyncio.fixture
async def scenario(client: AsyncClient, contract: dict) -> dict:
    """Cria e retorna um cenário +5k/mês."""
    resp = await client.post(
        f"/contracts/{contract['id']}/scenarios",
        json={"nome": "5k/mes", "aporte_mensal_extra": 5000},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()
