"""
Testes E2E — fluxo completo do usuário novo.

Simula exatamente o que o frontend faz:
  1. Registrar conta
  2. Usar o token retornado para criar contrato
  3. Ver data de quitação
  4. Criar cenário
  5. Ver projeção com economia de juros

Não usa fixtures de auth — testa o auth real (JWT local).
"""

import pytest
import pytest_asyncio
from fastapi import Depends
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from main import app
from db.engine import get_session
from db.rls import get_rls_session
from middleware.auth import get_current_user_id

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5490/tenor_test"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
TestSession = async_sessionmaker(test_engine, expire_on_commit=False)

# Dados do contrato de referência (Thiago, DDC 05/05/2026)
CONTRACT_DATA = {
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
}

TABLES = ["user_operations", "scenarios", "contracts", "properties", "user_profiles"]


@pytest_asyncio.fixture(autouse=True)
async def cleanup():
    yield
    async with test_engine.begin() as conn:
        for table in TABLES:
            await conn.execute(text(f'TRUNCATE TABLE "{table}" CASCADE'))


@pytest_asyncio.fixture
async def e2e_client():
    """
    Cliente E2E: usa banco de teste para todas as sessions.
    NÃO sobrescreve auth — testa com JWT real.
    """
    async def override_session():
        async with TestSession() as session:
            yield session

    async def override_rls_session(user_id: str = Depends(get_current_user_id)):
        async with TestSession() as session:
            import uuid as _uuid
            _uuid.UUID(user_id)
            await session.execute(text(f"SET \"app.current_user_id\" = '{user_id}'"))
            yield session

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_rls_session] = override_rls_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


# ── Helpers ─────────────────────────────────────────────────────────────────────

async def register_and_get_token(client: AsyncClient, email: str = "e2e@test.com") -> str:
    """Registra e retorna o token JWT."""
    resp = await client.post("/auth/register", json={
        "email": email, "password": "senha123",
    })
    assert resp.status_code == 201, f"Register falhou: {resp.text}"
    return resp.json()["token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ── Testes ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_registro_retorna_token_e_email(e2e_client):
    resp = await e2e_client.post("/auth/register", json={
        "email": "new@test.com", "password": "abc123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "token" in data
    assert data["email"] == "new@test.com"
    assert "user_id" in data


@pytest.mark.asyncio
async def test_login_com_credenciais_corretas(e2e_client):
    await register_and_get_token(e2e_client, "login@test.com")
    resp = await e2e_client.post("/auth/login", json={
        "email": "login@test.com", "password": "senha123",
    })
    assert resp.status_code == 200
    assert "token" in resp.json()


@pytest.mark.asyncio
async def test_login_com_senha_errada(e2e_client):
    await register_and_get_token(e2e_client, "wrong@test.com")
    resp = await e2e_client.post("/auth/login", json={
        "email": "wrong@test.com", "password": "errada",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_registro_email_duplicado(e2e_client):
    await register_and_get_token(e2e_client, "dup@test.com")
    resp = await e2e_client.post("/auth/register", json={
        "email": "dup@test.com", "password": "outra123",
    })
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_endpoint_protegido_sem_token(e2e_client):
    resp = await e2e_client.get("/contracts")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_endpoint_protegido_com_token_invalido(e2e_client):
    resp = await e2e_client.get("/contracts", headers=auth_header("token.invalido.aqui"))
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_retorna_perfil(e2e_client):
    token = await register_and_get_token(e2e_client, "me@test.com")
    resp = await e2e_client.get("/auth/me", headers=auth_header(token))
    assert resp.status_code == 200
    assert resp.json()["email"] == "me@test.com"


@pytest.mark.asyncio
async def test_contratos_vazio_apos_registro(e2e_client):
    """Usuário novo não tem contratos."""
    token = await register_and_get_token(e2e_client)
    resp = await e2e_client.get("/contracts", headers=auth_header(token))
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_fluxo_completo_registro_ate_cenario(e2e_client):
    """
    Fluxo completo: registro → contrato → cenário → projeção.
    Simula exatamente o que o frontend faz.
    """
    # 1. Registrar
    token = await register_and_get_token(e2e_client, "fullflow@test.com")
    h = auth_header(token)

    # 2. Listar contratos (vazio)
    resp = await e2e_client.get("/contracts", headers=h)
    assert resp.json() == []

    # 3. Criar contrato (onboarding)
    resp = await e2e_client.post("/contracts", json=CONTRACT_DATA, headers=h)
    assert resp.status_code == 201
    contract = resp.json()
    contract_id = contract["id"]

    # 4. Verificar data de quitação calculada
    assert "data_quitacao" in contract
    quit_year = int(contract["data_quitacao"][:4])
    assert 2041 <= quit_year <= 2042

    # 5. Verificar campos computados
    assert contract["taxa_anual_efetiva"] == pytest.approx(0.1219, abs=0.001)
    assert contract["parcela_total"] > 0
    assert contract["juros_proxima"] > 0
    assert contract["seguros_mensal"] == pytest.approx(133.06, abs=0.10)

    # 6. Criar cenário +5k/mês
    resp = await e2e_client.post(
        f"/contracts/{contract_id}/scenarios",
        json={"nome": "5k/mês", "aporte_mensal_extra": 5000},
        headers=h,
    )
    assert resp.status_code == 201
    scenario = resp.json()

    # 7. Verificar projeção
    projecao = scenario["projecao"]
    assert projecao["total_juros_economizados"] > 200000  # ~R$267k
    assert projecao["parcelas_eliminadas"] > 100
    quit_year_cenario = int(projecao["data_quitacao"][:4])
    assert quit_year_cenario < quit_year  # deve ser antes de 2042

    # 8. Listar cenários
    resp = await e2e_client.get(f"/contracts/{contract_id}/scenarios", headers=h)
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_isolamento_entre_usuarios(e2e_client):
    """Usuário A não vê contratos do usuário B."""
    token_a = await register_and_get_token(e2e_client, "a@test.com")
    token_b = await register_and_get_token(e2e_client, "b@test.com")

    # A cria contrato
    resp = await e2e_client.post(
        "/contracts", json=CONTRACT_DATA, headers=auth_header(token_a)
    )
    assert resp.status_code == 201

    # B não vê
    resp = await e2e_client.get("/contracts", headers=auth_header(token_b))
    assert resp.json() == []

    # A vê
    resp = await e2e_client.get("/contracts", headers=auth_header(token_a))
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_registrar_amortizacao_atualiza_contrato(e2e_client):
    """Registrar amortização deve reduzir saldo e prazo."""
    token = await register_and_get_token(e2e_client, "amort@test.com")
    h = auth_header(token)

    # Criar contrato
    resp = await e2e_client.post("/contracts", json=CONTRACT_DATA, headers=h)
    contract = resp.json()
    saldo_antes = contract["saldo_devedor"]
    prazo_antes = contract["prazo_remanescente"]
    quitacao_antes = contract["data_quitacao"]

    # Registrar amortização de R$30k
    resp = await e2e_client.post(
        f"/contracts/{contract['id']}/operations",
        json={
            "tipo": "amortizacao_prazo",
            "data_operacao": "2026-06-01",
            "valor_principal": 30000,
        },
        headers=h,
    )
    assert resp.status_code == 201

    # Verificar contrato atualizado
    resp = await e2e_client.get(f"/contracts/{contract['id']}", headers=h)
    updated = resp.json()
    assert updated["saldo_devedor"] < saldo_antes
    assert updated["prazo_remanescente"] < prazo_antes
    assert updated["data_quitacao"] < quitacao_antes
