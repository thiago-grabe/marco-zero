.PHONY: dev dev-api dev-web db-up db-down db-migrate db-reset test test-api test-web lint lint-api lint-web generate-types setup

# ── Dev (usa script com portas dinâmicas) ─────────────────────────────────────
dev:
	./scripts/dev.sh

dev-api-only:
	./scripts/dev.sh --api-only

# Compatibilidade: permite sobrescrever portas via env
# Exemplo: API_PORT=9000 make dev-api
dev-api:
	cd api && uv run uvicorn main:app --reload --port $${API_PORT:-8000}

dev-web:
	cd web && API_PORT=$${API_PORT:-8000} WEB_PORT=$${WEB_PORT:-5173} npm run dev -- --port $${WEB_PORT:-5173}

stop:
	./scripts/stop.sh

# ── Banco (Docker, porta 5490 — sem conflito com outros projetos) ─────────────
db-up:
	docker compose up -d postgres
	@echo "Aguardando postgres..." && sleep 2

db-down:
	docker compose stop postgres

db-status:
	docker compose exec postgres pg_isready -U postgres

db-migrate:
	cd api && uv run alembic upgrade head

db-migrate-test:
	cd api && DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5490/marco_zero_test" uv run alembic upgrade head

db-reset:
	cd api && uv run alembic downgrade base && uv run alembic upgrade head

db-setup-test:
	docker compose exec postgres createdb -U postgres marco_zero_test 2>/dev/null || true
	make db-migrate-test

db-seed:
	cd api && uv run python scripts/seed_refs.py

# ── Tipos (end-to-end type safety) ───────────────────────────────────────────
# Detecta porta da API automaticamente ou usa 8000 como fallback
generate-types:
	@API_PORT=$${API_PORT:-8000}; \
	echo "Gerando tipos de http://localhost:$$API_PORT/openapi.json ..."; \
	curl -sf "http://localhost:$$API_PORT/openapi.json" \
	  | npx --yes openapi-typescript@7 - \
	  -o web/src/lib/api/generated.ts && \
	echo "✓ web/src/lib/api/generated.ts atualizado"

# ── Testes ────────────────────────────────────────────────────────────────────
test:
	./scripts/test.sh

test-api:
	cd api && uv run pytest -v

test-web:
	cd web && npm run test

# ── Lint ──────────────────────────────────────────────────────────────────────
lint:
	./scripts/test.sh --api --web 2>/dev/null || true

lint-api:
	cd api && uv run ruff check . && uv run ruff format --check .

lint-web:
	cd web && npm run lint && npm run type-check

# ── Setup inicial ─────────────────────────────────────────────────────────────
setup:
	./scripts/setup.sh
