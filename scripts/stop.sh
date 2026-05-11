#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Marco Zero — Para todos os serviços
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"

if [ -t 1 ]; then
  GREEN='\033[0;32m' AMBER='\033[38;5;214m' NC='\033[0m'
else
  GREEN='' AMBER='' NC=''
fi

echo -e "${AMBER}→${NC}  Encerrando serviços Marco Zero..."

# Matar processos nas portas 8000 e 5173
for port in 8000 5173; do
  pid=$(lsof -ti tcp:"$port" 2>/dev/null || true)
  if [ -n "$pid" ]; then
    kill "$pid" 2>/dev/null && echo -e "${GREEN}✓${NC}  Porta $port liberada (PID $pid)" || true
  fi
done

# Parar docker compose
cd "$ROOT"
if docker compose ps --quiet 2>/dev/null | grep -q .; then
  docker compose stop &>/dev/null && echo -e "${GREEN}✓${NC}  Postgres parado"
fi

echo -e "${GREEN}✓${NC}  Tudo parado."
