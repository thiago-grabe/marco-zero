#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Marco Zero — Setup inicial (rodar uma vez após clonar o repo)
#
# Instala dependências Python e Node, cria o .env e roda as migrations.
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"
API_DIR="$ROOT/api"
WEB_DIR="$ROOT/web"

if [ -t 1 ]; then
  AMBER='\033[38;5;214m' GREEN='\033[0;32m' RED='\033[0;31m' BOLD='\033[1m' DIM='\033[2m' NC='\033[0m'
else
  AMBER='' GREEN='' RED='' BOLD='' DIM='' NC=''
fi

step() { echo -e "${AMBER}→${NC}  $1"; }
ok()   { echo -e "${GREEN}✓${NC}  $1"; }
fail() { echo -e "${RED}✗${NC}  $1" >&2; exit 1; }

echo ""
echo -e "${BOLD}Marco Zero — Setup inicial${NC}"
echo ""

# ── Pré-requisitos ────────────────────────────────────────────────────────────
step "Verificando pré-requisitos..."

command -v docker &>/dev/null || fail "docker não encontrado → https://docker.com"
command -v uv     &>/dev/null || fail "uv não encontrado → curl -LsSf https://astral.sh/uv/install.sh | sh"
command -v node   &>/dev/null || fail "node não encontrado → https://nodejs.org"
command -v npm    &>/dev/null || fail "npm não encontrado"

ok "Pré-requisitos verificados"

# ── API — dependências ────────────────────────────────────────────────────────
step "Instalando dependências Python..."
cd "$API_DIR"
uv sync --quiet
ok "Python deps instalados"

# ── API — .env ────────────────────────────────────────────────────────────────
if [ ! -f "$API_DIR/.env" ]; then
  cp "$API_DIR/.env.example" "$API_DIR/.env"
  ok "Criado api/.env"
  echo ""
  echo -e "  ${AMBER}Atenção:${NC} edite ${BOLD}api/.env${NC} antes de rodar:"
  echo -e "  ${DIM}  OPENAI_API_KEY=sk-...${NC}"
  echo -e "  ${DIM}  SUPABASE_JWT_SECRET=...${NC}"
  echo ""
else
  ok "api/.env já existe"
fi

# ── Frontend — dependências ───────────────────────────────────────────────────
step "Instalando dependências Node..."
cd "$WEB_DIR"
npm install --silent
ok "Node deps instalados"

# ── Banco de dados ─────────────────────────────────────────────────────────────
step "Iniciando Postgres..."
cd "$ROOT"
docker compose up -d postgres &>/dev/null

retries=20
printf "   Aguardando Postgres "
while ! docker compose exec -T postgres pg_isready -U postgres -q &>/dev/null; do
  printf "."
  retries=$((retries - 1))
  [ $retries -eq 0 ] && { echo ""; fail "Postgres não iniciou. Verifique: docker compose logs postgres"; }
  sleep 1
done
echo ""
ok "Postgres pronto"

# ── Migrations ─────────────────────────────────────────────────────────────────
step "Rodando migrations..."
cd "$API_DIR"
if uv run alembic upgrade head &>/dev/null 2>&1; then
  ok "Migrations aplicadas"
else
  echo -e "  ${DIM}Migrations pendentes (normal na v0 — schema ainda em setup)${NC}"
fi

# ── Resultado ─────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║${NC}  ${GREEN}Setup concluído!${NC}                                 ${BOLD}║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${AMBER}Antes de rodar:${NC}"
echo -e "  Edite ${BOLD}api/.env${NC} e preencha:"
echo -e "  ${DIM}  OPENAI_API_KEY=sk-...${NC}"
echo -e "  ${DIM}  SUPABASE_JWT_SECRET=... (pode deixar vazio em dev)${NC}"
echo ""
echo -e "  ${BOLD}Iniciar o ambiente:${NC}"
echo -e "  ${AMBER}\$${NC} ./scripts/dev.sh"
echo ""
echo -e "  ${BOLD}URLs após rodar dev.sh:${NC}"
echo -e "  ${DIM}  As portas reais são impressas pelo dev.sh — abaixo são os defaults${NC}"
echo ""
echo -e "  ${GREEN}○${NC}  Frontend       ${BOLD}http://localhost:5173${NC}"
echo -e "  ${GREEN}○${NC}  API            ${BOLD}http://localhost:8000${NC}"
echo -e "  ${GREEN}○${NC}  API Docs       ${BOLD}http://localhost:8000/docs${NC}"
echo -e "  ${GREEN}○${NC}  API Health     ${BOLD}http://localhost:8000/health${NC}"
echo -e "  ${GREEN}○${NC}  Postgres       ${BOLD}postgresql://postgres:postgres@localhost:5432/marco_zero_dev${NC}"
echo ""
echo -e "  ${BOLD}Outros comandos:${NC}"
echo -e "  ${AMBER}\$${NC} ./scripts/dev.sh --api-only   ${DIM}# só API, sem frontend${NC}"
echo -e "  ${AMBER}\$${NC} ./scripts/test.sh             ${DIM}# rodar todos os testes${NC}"
echo -e "  ${AMBER}\$${NC} ./scripts/stop.sh             ${DIM}# parar tudo${NC}"
echo ""
