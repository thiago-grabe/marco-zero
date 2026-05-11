#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Marco Zero — Dev launcher com portas dinâmicas
#
# Portas são alocadas automaticamente a partir dos defaults, evitando
# conflitos com outros apps rodando na mesma máquina.
#
# Uso:
#   ./scripts/dev.sh                  # aloca portas livres automaticamente
#   ./scripts/dev.sh --api-only       # só API, sem frontend
#   ./scripts/dev.sh --no-db          # sem Docker (Postgres externo)
#   API_PORT=9000 ./scripts/dev.sh    # forçar porta da API
#   WEB_PORT=4000 ./scripts/dev.sh    # forçar porta do frontend
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# ── Caminhos ──────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"
LOGS="$ROOT/logs"
API_DIR="$ROOT/api"
WEB_DIR="$ROOT/web"

# ── Flags ─────────────────────────────────────────────────────────────────────
NO_DB=false
API_ONLY=false

for arg in "$@"; do
  case "$arg" in
    --no-db)    NO_DB=true ;;
    --api-only) API_ONLY=true ;;
    --help|-h)
      echo "Uso: $0 [--no-db] [--api-only]"
      echo "Env: API_PORT=XXXX WEB_PORT=XXXX ./scripts/dev.sh"
      exit 0
      ;;
  esac
done

# ── Cores (só se for terminal interativo) ─────────────────────────────────────
if [ -t 1 ]; then
  AMBER='\033[38;5;214m'
  GREEN='\033[0;32m'
  RED='\033[0;31m'
  DIM='\033[2m'
  BOLD='\033[1m'
  NC='\033[0m'
else
  AMBER='' GREEN='' RED='' DIM='' BOLD='' NC=''
fi

step()   { echo -e "${AMBER}→${NC}  $1"; }
ok()     { echo -e "${GREEN}✓${NC}  $1"; }
fail()   { echo -e "${RED}✗${NC}  $1" >&2; }
dim()    { echo -e "${DIM}$1${NC}"; }
header() { echo -e "\n${BOLD}$1${NC}"; }

# ── PIDs para cleanup ─────────────────────────────────────────────────────────
API_PID=""
WEB_PID=""
TAIL_PID=""

cleanup() {
  echo ""
  step "Encerrando..."
  [ -n "$TAIL_PID" ] && kill "$TAIL_PID" 2>/dev/null || true
  [ -n "$WEB_PID"  ] && kill "$WEB_PID"  2>/dev/null && wait "$WEB_PID"  2>/dev/null || true
  [ -n "$API_PID"  ] && kill "$API_PID"  2>/dev/null && wait "$API_PID"  2>/dev/null || true
  ok "Encerrado."
  exit 0
}
trap cleanup SIGINT SIGTERM

# ── Porta livre ───────────────────────────────────────────────────────────────
# Usa Python (já disponível no .venv) para encontrar porta TCP livre.
# Aceita como env var para permitir override manual.
find_free_port() {
  local start="${1:-8000}"
  python3 -c "
import socket, sys
port = $start
while port < 65535:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(('', port))
            print(port)
            sys.exit(0)
        except OSError:
            port += 1
sys.exit(1)
"
}

# Permite override via env var; se não definido, acha porta livre
resolve_ports() {
  header "Alocando portas"

  # API
  if [ -n "${API_PORT:-}" ]; then
    step "API_PORT=$API_PORT (override manual)"
  else
    API_PORT=$(find_free_port 8000)
  fi
  ok "API  → porta $API_PORT"

  # Frontend (só se necessário)
  if ! $API_ONLY; then
    if [ -n "${WEB_PORT:-}" ]; then
      step "WEB_PORT=$WEB_PORT (override manual)"
    else
      WEB_PORT=$(find_free_port 5173)
    fi
    ok "Web  → porta $WEB_PORT"
  fi
}

# ── Pré-requisitos ────────────────────────────────────────────────────────────
check_prereqs() {
  header "Verificando pré-requisitos"

  local missing=0
  command -v docker  &>/dev/null || { fail "docker não encontrado → https://docker.com";          missing=1; }
  command -v uv      &>/dev/null || { fail "uv não encontrado → curl -LsSf https://astral.sh/uv/install.sh | sh"; missing=1; }
  command -v node    &>/dev/null || { fail "node não encontrado → https://nodejs.org";            missing=1; }
  command -v python3 &>/dev/null || { fail "python3 não encontrado";                              missing=1; }

  ok "docker $(docker --version | awk '{print $3}' | tr -d ',')"
  ok "uv $(uv --version 2>&1 | awk '{print $2}')"
  ok "node $(node --version)"

  if [ $missing -ne 0 ]; then exit 1; fi
}

# ── Banco de dados ────────────────────────────────────────────────────────────
start_db() {
  if $NO_DB; then return 0; fi

  header "Banco de dados (Docker, porta 5490)"
  DB_HOST_PORT=5490

  cd "$ROOT"
  step "Iniciando Postgres via Docker..."
  docker compose up -d postgres &>/dev/null

  local retries=25
  printf "   Aguardando "
  while ! docker compose exec -T postgres pg_isready -U postgres -q &>/dev/null; do
    printf "."
    retries=$((retries - 1))
    if [ $retries -eq 0 ]; then
      echo ""
      fail "Postgres não iniciou. Veja: docker compose logs postgres"
      exit 1
    fi
    sleep 1
  done
  echo ""
  ok "Postgres pronto → localhost:5490"
}

# ── API ───────────────────────────────────────────────────────────────────────
setup_api() {
  header "API — Python + FastAPI"

  if [ ! -d "$API_DIR/.venv" ]; then
    step "Instalando dependências Python..."
    cd "$API_DIR" && uv sync --quiet
    ok "Dependências instaladas"
  else
    ok "Dependências ok"
  fi

  if [ ! -f "$API_DIR/.env" ]; then
    cp "$API_DIR/.env.example" "$API_DIR/.env"
    step "Criado api/.env — configure OPENAI_API_KEY e SUPABASE_JWT_SECRET"
  fi
}

start_api() {
  step "Iniciando API na porta $API_PORT..."
  mkdir -p "$LOGS"
  cd "$API_DIR"

  uv run uvicorn main:app \
    --reload \
    --port "$API_PORT" \
    --host 0.0.0.0 \
    > "$LOGS/api.log" 2>&1 &
  API_PID=$!

  local retries=20
  printf "   Aguardando health check "
  while ! curl -sf "http://localhost:$API_PORT/health" &>/dev/null; do
    printf "."
    retries=$((retries - 1))
    if [ $retries -eq 0 ]; then
      echo ""
      fail "API não respondeu. Veja: tail -f logs/api.log"
      tail -15 "$LOGS/api.log" >&2
      exit 1
    fi
    # Se o processo morreu, não adianta esperar
    if ! kill -0 "$API_PID" 2>/dev/null; then
      echo ""
      fail "Processo da API encerrou inesperadamente."
      tail -15 "$LOGS/api.log" >&2
      exit 1
    fi
    sleep 1
  done
  echo ""
  ok "API pronta → http://localhost:$API_PORT"
  dim "   Docs: http://localhost:$API_PORT/docs"
  dim "   Logs: tail -f logs/api.log"
}

# ── Frontend ──────────────────────────────────────────────────────────────────
setup_web() {
  if $API_ONLY; then return 0; fi

  header "Frontend — React + Vite"

  if [ ! -d "$WEB_DIR/node_modules" ]; then
    step "Instalando dependências Node..."
    cd "$WEB_DIR" && npm install --silent
    ok "Dependências instaladas"
  else
    ok "Dependências ok"
  fi
}

start_web() {
  if $API_ONLY; then return 0; fi

  step "Iniciando frontend na porta $WEB_PORT..."
  mkdir -p "$LOGS"
  cd "$WEB_DIR"

  # Passa as portas como variáveis de ambiente para o processo Vite.
  # vite.config.ts lê API_PORT (para o proxy) e WEB_PORT (para server.port).
  API_PORT="$API_PORT" \
  WEB_PORT="$WEB_PORT" \
  npm run dev -- --port "$WEB_PORT" \
    > "$LOGS/web.log" 2>&1 &
  WEB_PID=$!

  # Vite pode escolher outra porta se WEB_PORT estiver ocupada (strictPort: false).
  # Lê a porta real do log de saída do Vite.
  local retries=20
  local actual_web_port=""
  printf "   Aguardando Vite "
  while [ $retries -gt 0 ]; do
    printf "."
    sleep 1
    retries=$((retries - 1))

    # Extrai a porta real do log ("Local: http://localhost:XXXX/")
    if [ -f "$LOGS/web.log" ]; then
      actual_web_port=$(grep -oE 'localhost:[0-9]+' "$LOGS/web.log" 2>/dev/null \
        | head -1 | cut -d: -f2 || true)
    fi

    if [ -n "$actual_web_port" ]; then
      # Confirma que a porta está respondendo
      if curl -sf "http://localhost:$actual_web_port" &>/dev/null; then
        WEB_PORT="$actual_web_port"
        break
      fi
    fi

    if ! kill -0 "$WEB_PID" 2>/dev/null; then
      echo ""
      fail "Processo do Vite encerrou inesperadamente."
      tail -15 "$LOGS/web.log" >&2
      exit 1
    fi
  done

  if [ -z "$actual_web_port" ]; then
    echo ""
    fail "Frontend não respondeu. Veja: tail -f logs/web.log"
    exit 1
  fi

  echo ""
  ok "Frontend pronto → http://localhost:$WEB_PORT"
  dim "   Logs: tail -f logs/web.log"
}

# ── Status ────────────────────────────────────────────────────────────────────
print_status() {
  local db_port="${DB_HOST_PORT:-5432}"

  echo ""
  echo -e "${BOLD}─────────────────────────────────────────────────${NC}"
  echo -e "  ${AMBER}Marco Zero${NC} — ambiente de desenvolvimento"
  echo -e "${BOLD}─────────────────────────────────────────────────${NC}"
  echo ""

  if ! $API_ONLY; then
    echo -e "  ${GREEN}●${NC}  Frontend"
    echo -e "     ${BOLD}http://localhost:${WEB_PORT}${NC}"
    echo ""
  fi

  echo -e "  ${GREEN}●${NC}  API"
  echo -e "     ${BOLD}http://localhost:${API_PORT}${NC}"
  echo ""
  echo -e "  ${GREEN}●${NC}  API Docs (Swagger)"
  echo -e "     ${BOLD}http://localhost:${API_PORT}/docs${NC}"
  echo ""
  echo -e "  ${GREEN}●${NC}  API Health"
  echo -e "     ${BOLD}http://localhost:${API_PORT}/health${NC}"
  echo ""

  if ! $NO_DB; then
    echo -e "  ${GREEN}●${NC}  Postgres"
    echo -e "     ${BOLD}postgresql://postgres:postgres@localhost:${db_port}/marco_zero_dev${NC}"
    echo ""
  fi

  echo -e "${BOLD}─────────────────────────────────────────────────${NC}"
  echo -e "  ${DIM}Logs:  tail -f logs/api.log logs/web.log${NC}"
  echo -e "  ${DIM}Parar: Ctrl+C${NC}"
  echo -e "${BOLD}─────────────────────────────────────────────────${NC}"
  echo ""
}

# ── Main ──────────────────────────────────────────────────────────────────────
main() {
  echo ""
  echo -e "${BOLD}Marco Zero${NC} ${DIM}— iniciando ambiente de desenvolvimento${NC}"

  check_prereqs
  resolve_ports
  start_db
  setup_api
  start_api
  setup_web
  start_web
  print_status

  # Tail dos logs em tempo real (processo separado para não bloquear o trap)
  if ! $API_ONLY; then
    tail -f "$LOGS/api.log" "$LOGS/web.log" 2>/dev/null &
  else
    tail -f "$LOGS/api.log" 2>/dev/null &
  fi
  TAIL_PID=$!

  # Aguarda qualquer sinal de encerramento
  wait "$API_PID" 2>/dev/null || true
}

main "$@"
