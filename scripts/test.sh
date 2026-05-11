#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Marco Zero — Test runner
#
# Uso:
#   ./scripts/test.sh          # todos os testes
#   ./scripts/test.sh --api    # só API (pytest)
#   ./scripts/test.sh --web    # só frontend (vitest)
#   ./scripts/test.sh --watch  # modo watch (útil durante desenvolvimento)
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"
API_DIR="$ROOT/api"
WEB_DIR="$ROOT/web"

# Flags
RUN_API=true
RUN_WEB=true
WATCH=false

for arg in "$@"; do
  case "$arg" in
    --api)   RUN_WEB=false ;;
    --web)   RUN_API=false ;;
    --watch) WATCH=true ;;
    --help|-h)
      echo "Uso: $0 [--api] [--web] [--watch]"
      exit 0
      ;;
  esac
done

# Cores
if [ -t 1 ]; then
  AMBER='\033[38;5;214m' GREEN='\033[0;32m' RED='\033[0;31m' BOLD='\033[1m' NC='\033[0m'
else
  AMBER='' GREEN='' RED='' BOLD='' NC=''
fi

PASSED=0
FAILED=0

run_api_tests() {
  echo -e "\n${BOLD}API — pytest${NC}"
  cd "$API_DIR"

  local flags="-v"
  $WATCH && flags="--watch"

  if uv run pytest $flags; then
    PASSED=$((PASSED + 1))
    echo -e "${GREEN}✓${NC}  API tests passaram"
  else
    FAILED=$((FAILED + 1))
    echo -e "${RED}✗${NC}  API tests falharam"
  fi
}

run_web_tests() {
  echo -e "\n${BOLD}Frontend — vitest${NC}"
  cd "$WEB_DIR"

  local cmd="run"
  $WATCH && cmd="watch"

  if npm run test -- $cmd 2>/dev/null; then
    PASSED=$((PASSED + 1))
    echo -e "${GREEN}✓${NC}  Frontend tests passaram"
  else
    FAILED=$((FAILED + 1))
    echo -e "${RED}✗${NC}  Frontend tests falharam"
  fi
}

run_type_check() {
  echo -e "\n${BOLD}TypeScript — tsc${NC}"
  cd "$WEB_DIR"

  if npx tsc --noEmit; then
    PASSED=$((PASSED + 1))
    echo -e "${GREEN}✓${NC}  Type check ok"
  else
    FAILED=$((FAILED + 1))
    echo -e "${RED}✗${NC}  Type check falhou"
  fi
}

run_lint() {
  echo -e "\n${BOLD}Lint — ruff${NC}"
  cd "$API_DIR"

  if uv run ruff check . --quiet && uv run ruff format --check . --quiet; then
    PASSED=$((PASSED + 1))
    echo -e "${GREEN}✓${NC}  Lint ok"
  else
    FAILED=$((FAILED + 1))
    echo -e "${RED}✗${NC}  Lint falhou (rode: cd api && uv run ruff check --fix .)"
  fi
}

echo ""
echo -e "${BOLD}Marco Zero${NC} — test suite"

$RUN_API && run_api_tests
$RUN_API && run_lint
$RUN_WEB && run_type_check
$RUN_WEB && run_web_tests

echo ""
echo -e "${BOLD}────────────────────────────────${NC}"
echo -e "  ${GREEN}✓${NC} $PASSED suítes ok   ${RED}✗${NC} $FAILED falharam"
echo -e "${BOLD}────────────────────────────────${NC}"
echo ""

[ $FAILED -eq 0 ] || exit 1
