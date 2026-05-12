# Tenor — Arquitetura

## Visão geral

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Browser    │────▸│    nginx     │────▸│   FastAPI    │
│   (React)    │◂────│   (porta     │◂────│   (porta     │
│   SPA        │     │    3000)     │     │    8000)     │
└──────────────┘     └──────────────┘     └──────┬───────┘
                       /api → proxy              │
                       /* → index.html           │
                                          ┌──────▼───────┐
                                          │  Postgres 17 │
                                          │  (porta 5490)│
                                          │  5 tabelas   │
                                          │  RLS/user_id │
                                          └──────────────┘
```

## Componentes

### Frontend (web/)

| Tecnologia | Papel |
|---|---|
| React 18 | UI reativa |
| Vite | Build rápido, HMR |
| TanStack Router | File-based routing, type-safe |
| TanStack Query | Cache de API, invalidação automática |
| Tailwind CSS | Utility-first styling |
| shadcn/ui | Componentes headless customizados |
| react-markdown | Renderização do output da IA |
| Zustand | Estado global mínimo (contractId ativo) |

**Rotas:**

```
/                   landing page
/login              registro/login (fora do fluxo principal)
/onboarding         4 passos: banco → campos → revisão → insight
/dashboard          hero quitação + KPIs + cenário destaque
/scenarios          sliders + salvar + comparar
/chat               chat IA genérico
/chat?scenario=ID   chat contextual ao cenário
```

### Backend (api/)

| Camada | Diretório | Responsabilidade |
|---|---|---|
| **Routers** | `routers/` | Endpoints REST + SSE. Zero lógica de negócio. |
| **Motor** | `motor/` | Cálculos SAC/PRICE/Itaú. Funções puras, sem I/O. |
| **Tools** | `tools/` | Wrappers `@function_tool` que expõem o motor ao ChatAgent. |
| **Agents** | `mz_agents/` | ChatAgent (GPT-4o + 5 Tools). |
| **DB** | `db/` | SQLAlchemy 2.0 async + Alembic + RLS. |
| **Models** | `models/` | Pydantic (request/response). Separado dos ORM models. |
| **Middleware** | `middleware/` | JWT validation. |

### Motor SAC/PRICE/Itaú

```
motor/
├── sac.py          compute_installment, simulate_amortization,
│                   project_scenario, compare_scenarios,
│                   generate_installment_schedule
├── price.py        compute_pmt, compute_balance_at, simulate_amortization
└── itau.py         detect_itau_mode, simulate_amortization
```

**Propriedades:**
- Funções puras — sem estado, sem I/O, sem side effects
- Testáveis unitariamente com dados reais
- Aceita frequências customizadas (`meses_aporte_extra`)
- 37 testes dedicados (SAC + PRICE + Itaú + frequência)

### 5 Tools do ChatAgent

| Tool | O que faz | Motor |
|---|---|---|
| `simular_amortizacao` | Impacto de amortizar X agora | `sac.simulate_amortization` |
| `projetar_cenario` | Projeção mês a mês com aportes extras | `sac.project_scenario` |
| `comparar_cenarios` | Side-by-side + análise marginal | `sac.compare_scenarios` |
| `calcular_parcela` | Decomposição amort + juros + seguros | `sac.compute_installment` |
| `calcular_pro_rata` | Juros de esperar X dias | `sac.compute_pro_rata` |

A IA chama essas tools via OpenAI function calling. Nunca calcula por conta própria.

### Schema do banco

```
user_profiles ─────┐
                    │ 1:N
properties ────────┤
                    │ 1:N
contracts ─────────┤ (banco, taxa, saldo, custos_extras JSON)
    │               │
    ├── scenarios   │ (parâmetros de simulação, sem resultados)
    │               │
    └── user_operations (amortizações declaradas)
```

**RLS**: toda tabela tem `user_id` + política `WHERE user_id = current_setting('app.current_user_id')`. O middleware FastAPI injeta via `SET LOCAL` antes de cada query.

### Fluxo SSE do Chat

```
POST /chat { contract_id, message }
    │
    ▼ FastAPI StreamingResponse
    │
    ├─ event: context     { banco, saldo, parcela, prazo }
    ├─ event: tool_call   { tool, arguments }
    ├─ event: tool_result { output (JSON do motor) }
    ├─ event: text_delta  { delta (chunk de texto) }
    ├─ event: text        { content (texto completo) }
    ├─ event: done        { status: "ok" }
    └─ event: error       { detail }
```

O frontend renderiza cada tipo de evento com componentes especializados:
- `text` → `MarkdownRenderer` (react-markdown + remark-gfm)
- `tool_call` → `ToolCallIndicator` (spinner → checkmark)
- `tool_result` → `ToolResultCard` (card especializado por tool)

### Docker Compose

```yaml
services:
  postgres:   # Postgres 17 Alpine, porta 5490
  api:        # FastAPI, porta 8000, depende de postgres
  migrations: # Alembic upgrade head, roda uma vez
  web:        # React build + nginx, porta 3000, proxy /api → api:8000
```

## Testes

| Suite | Testes | O que cobre |
|---|---|---|
| `test_motor_sac.py` | 20 | Motor SAC com dados reais |
| `test_motor_price.py` | 9 | PMT, saldo residual, PRICE |
| `test_motor_itau.py` | 7 | Modo Itaú, detecção, manutenção de prestação |
| `test_motor_frequency.py` | 11 | Frequências: pares, ímpares, trimestral, hierarquia |
| `test_api_health.py` | 5 | Disponibilidade, OpenAPI |
| `test_api_auth.py` | 4 | Registro, login, senha errada |
| `test_api_contracts.py` | 11 | CRUD contratos + campos computados |
| `test_api_scenarios.py` | 12 | CRUD cenários + projeções |
| `test_api_operations.py` | 6 | Amortizações + recálculo |
| `test_e2e_flow.py` | 11 | Fluxo completo: registro → contrato → cenário → isolamento |
| **Total** | **101** | |
