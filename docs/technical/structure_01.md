# Marco Zero — Estrutura do Projeto

> Documento de design — versão 1
> Data: 06/05/2026
> Status: definido
> Depende de: `stack_01.md`

---

## Visão geral

```
marco-zero/
├── web/          ← React + Vite + TypeScript (frontend)
├── api/          ← Python + FastAPI + OpenAI Agents SDK (backend)
├── docs/         ← Documentação (este diretório)
├── .github/      ← CI/CD workflows
├── docker-compose.yml
├── Makefile
└── README.md
```

Repositório único, duas pastas top-level. Sem monorepo tooling — sem Turborepo, sem pnpm workspaces. Cada pasta tem seu próprio package manager (`npm` para `web/`, `uv` para `api/`).

---

## `web/` — Frontend

```
web/
├── src/
│   ├── routes/                   ← TanStack Router (file-based, type-safe)
│   │   ├── __root.tsx            ← root layout (auth check, dark theme, fonts)
│   │   ├── index.tsx             ← redirect para /dashboard
│   │   ├── onboarding/
│   │   │   └── index.tsx
│   │   ├── dashboard/
│   │   │   ├── index.tsx         ← Dashboard (journey_06)
│   │   │   └── $contractId.tsx   ← contrato específico
│   │   ├── scenarios/
│   │   │   ├── index.tsx         ← lista de cenários (journey_02)
│   │   │   └── $scenarioId.tsx
│   │   ├── chat/
│   │   │   └── index.tsx         ← IA Chat (journey_03)
│   │   ├── coach/
│   │   │   └── index.tsx         ← Modo Coach (journey_04)
│   │   ├── stress/
│   │   │   └── index.tsx         ← Stress Tests (journey_05)
│   │   └── audit/
│   │       └── index.tsx         ← Audit (journey_07)
│   │
│   ├── components/
│   │   ├── ui/                   ← shadcn/ui (copiados e customizados)
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── slider.tsx
│   │   │   └── ...
│   │   ├── contract/             ← componentes de contrato
│   │   │   ├── ContractSelector.tsx
│   │   │   └── ContractBadge.tsx
│   │   ├── motor/                ← componentes dos cálculos
│   │   │   ├── ScenarioSliders.tsx   ← sliders com debounce
│   │   │   ├── ScenarioCard.tsx
│   │   │   ├── ProjectionChart.tsx   ← linha do tempo de quitação
│   │   │   └── YearScheduleTable.tsx
│   │   ├── chat/
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── ToolCallIndicator.tsx ← "calculando amortização..."
│   │   │   └── SourceChip.tsx        ← "do DDC de 05/05/2026"
│   │   ├── ddc/
│   │   │   ├── DdcDropzone.tsx       ← upload com checkmarks
│   │   │   └── ExtractionReview.tsx  ← Tela 0.7: confirmação
│   │   └── layout/
│   │       ├── AppShell.tsx
│   │       ├── Sidebar.tsx
│   │       └── ContractHeader.tsx    ← seletor de contrato no topo
│   │
│   ├── hooks/
│   │   ├── useContract.ts        ← TanStack Query: contrato ativo
│   │   ├── useScenarios.ts
│   │   ├── useCoachAlerts.ts
│   │   ├── useMotor.ts           ← debounced motor calls
│   │   └── useChat.ts            ← SSE stream do chat
│   │
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts         ← openapi-fetch client tipado
│   │   │   ├── generated.ts      ← AUTO-GERADO de /openapi.json (não editar)
│   │   │   └── sse.ts            ← helper para SSE streaming
│   │   ├── auth.ts               ← Supabase Auth client
│   │   ├── query-client.ts       ← TanStack Query config
│   │   └── utils.ts              ← cn(), formatBRL(), formatDate()
│   │
│   ├── stores/
│   │   ├── contract.ts           ← Zustand: contractId ativo
│   │   └── ui.ts                 ← Zustand: sidebar, modais
│   │
│   ├── styles/
│   │   └── globals.css           ← CSS variables dark premium (stack_01.md §D8)
│   │
│   ├── main.tsx
│   └── router.tsx                ← TanStack Router: definição das rotas
│
├── public/
│   ├── manifest.json             ← PWA manifest
│   └── icons/                   ← app icons (192, 512)
│
├── index.html
├── vite.config.ts
├── tailwind.config.ts
├── components.json               ← shadcn/ui config
├── tsconfig.json
└── package.json
```

### Decisões de frontend

**TanStack Router** (não React Router v6): type-safe, file-based, sem string de URL em nenhum lugar. Cada rota é um componente tipado — parâmetros (`$contractId`) são validados no tipo.

**TanStack Query** para todo estado de servidor (contratos, DDCs, cenários, alertas). Zero `useEffect` para fetch. Cache automático, invalidação por mutation.

**Zustand** apenas para estado global de UI — qual contrato está ativo, estado de sidebar. Não duplica estado de servidor.

**Type safety end-to-end**: FastAPI gera OpenAPI spec em `/openapi.json`. `openapi-typescript` gera `generated.ts` a partir dessa spec. `openapi-fetch` usa os tipos gerados. Resultado: sem duplicação de tipos entre Python e TypeScript.

```bash
# Comando para regenerar tipos (roda depois de mudar a API)
make generate-types
# faz: curl localhost:8000/openapi.json | npx openapi-typescript - -o web/src/lib/api/generated.ts
```

**Sliders com debounce** (`useMotor.ts`):

```typescript
const useMotor = (contractId: string) => {
  const [params, setParams] = useState<ScenarioParams>(defaultParams)
  const debouncedParams = useDebounce(params, 200)  // 200ms

  const { data: projection } = useQuery({
    queryKey: ['motor', 'project', contractId, debouncedParams],
    queryFn: () => api.POST('/motor/project', { body: { contractId, params: debouncedParams } }),
    staleTime: Infinity,   // resultado é determinístico — não precisa refetch
  })

  return { params, setParams, projection }
}
```

---

## `api/` — Backend

```
api/
├── agents/                          ← OpenAI Agents SDK
│   ├── __init__.py
│   ├── chat.py                      ← ChatAgent
│   ├── extraction/
│   │   ├── __init__.py
│   │   ├── orchestrator.py          ← ExtractionAgent (coordena os passes)
│   │   ├── header_agent.py          ← Passe 1: GPT-4o
│   │   ├── anchor_agent.py          ← Passe 2a: GPT-4o
│   │   ├── bulk_agent.py            ← Passe 2b: GPT-4o-mini
│   │   └── ops_agent.py             ← Passe 3: GPT-4o
│   ├── coach.py                     ← CoachAgent
│   └── reconciliation.py           ← ReconciliationAgent
│
├── tools/                           ← 17 Tools (motor_01.md)
│   ├── __init__.py
│   ├── data.py                      ← D1–D7: lêem banco, recebem db_session
│   └── compute.py                   ← C1–C10: funções puras, recebem ContractState
│
├── motor/                           ← SAC/PRICE/Itaú — funções puras, zero I/O
│   ├── __init__.py
│   ├── sac.py                       ← compute_installment_sac, project_sac
│   ├── price.py                     ← compute_installment_price, project_price
│   ├── itau.py                      ← modo Itaú (manutenção de prestação)
│   ├── scenario.py                  ← project_scenario, compare_scenarios
│   ├── stress.py                    ← run_stress (todos os tipos)
│   └── portability.py              ← evaluate_portability_multi
│
├── routers/                         ← FastAPI APIRouter
│   ├── __init__.py
│   ├── contracts.py                 ← CRUD contratos + imóveis
│   ├── ddc.py                       ← upload PDF, trigger ExtractionAgent
│   ├── scenarios.py                 ← CRUD cenários + versões
│   ├── chat.py                      ← POST /chat → SSE StreamingResponse
│   ├── motor.py                     ← POST /motor/project, /motor/amortize, etc.
│   ├── coach.py                     ← GET /coach/alerts, PATCH status
│   ├── stress.py                    ← POST /stress/run
│   ├── audit.py                     ← GET /audit/timeline, /audit/reconciliation
│   └── me.py                        ← GET /me, PATCH perfil, DELETE conta
│
├── db/
│   ├── __init__.py
│   ├── engine.py                    ← SQLAlchemy async engine + session factory
│   ├── rls.py                       ← dependency: injeta user_id no SET LOCAL
│   ├── models/                      ← SQLAlchemy ORM (mapeiam schema_01.md)
│   │   ├── __init__.py
│   │   ├── refs.py                  ← ref_banks, ref_amortization_systems, etc.
│   │   ├── user.py                  ← user_profiles
│   │   ├── property.py              ← properties
│   │   ├── contract.py              ← contracts
│   │   ├── ddc.py                   ← ddc_snapshots, ddc_installments, ddc_files
│   │   ├── operation.py             ← user_operations
│   │   ├── scenario.py              ← scenarios, scenario_versions
│   │   ├── stress.py                ← stress_test_runs
│   │   ├── coach.py                 ← coach_alerts, reminders
│   │   └── audit.py                 ← audit_events, ai_sessions
│   └── queries/                     ← queries complexas reutilizáveis
│       ├── contract_state.py        ← constrói ContractState (Tool D1)
│       └── scenarios.py
│
├── models/                          ← Pydantic (request/response)
│   ├── __init__.py
│   ├── contract.py                  ← ContractCreate, ContractResponse
│   ├── scenario.py                  ← ScenarioCreate, ScenarioParams
│   ├── motor.py                     ← ContractState, ProjectionResult, etc.
│   ├── chat.py                      ← ChatRequest, ChatSSEEvent
│   ├── ddc.py                       ← DdcExtractionResult, ExtractionHeader
│   └── coach.py                     ← CoachAlert, AlertStatus
│
├── jobs/                            ← Background jobs (APScheduler)
│   ├── __init__.py
│   ├── scheduler.py                 ← setup + registro de jobs
│   ├── coach_eval.py                ← daily: avalia regras + cria alerts
│   └── ddc_archive.py              ← daily: arquiva installments além do limite
│
├── middleware/
│   ├── auth.py                      ← JWT validation, extrai user_id
│   └── logging.py                   ← structured logging (sem PII)
│
├── config.py                        ← pydantic-settings: DATABASE_URL, OPENAI_API_KEY, etc.
├── main.py                          ← app = FastAPI(...); inclui routers
├── pyproject.toml                   ← uv + dependências
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/                   ← migrations SQL
└── .env.example
```

### Decisões de backend

**Separação ORM vs Pydantic**: `api/db/models/` são SQLAlchemy (falam com banco); `api/models/` são Pydantic (falam com a API). Nunca retornar um SQLAlchemy model diretamente — sempre converter para Pydantic antes de serializar.

**RLS como dependency FastAPI**:

```python
# db/rls.py
async def get_db_session(
    request: Request,
    user: User = Depends(get_current_user),  # JWT validated
) -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        # Injeta user_id para RLS policies do Postgres
        await session.execute(
            text("SET LOCAL app.current_user_id = :uid"),
            {"uid": str(user.id)}
        )
        yield session
```

Toda query no banco usa `session = Depends(get_db_session)`. RLS policies em `schema_01.md` lêem `current_setting('app.current_user_id')`. Zero chance de query cross-user.

**Tools são funções Python com `@function_tool`**:

```python
# tools/data.py
from agents import function_tool

@function_tool
async def get_contract_state(contract_id: str) -> ContractState:
    """Retorna o estado atual do contrato incluindo saldo calculado e próxima parcela."""
    # usa db_session do contexto (injetado pelo runner)
    ...

# agents/chat.py
from agents import Agent
from tools.data import get_contract_state, get_market_rates, get_fgts_status
from tools.compute import simulate_amortization, project_scenario, ...

chat_agent = Agent(
    name="MarcoZeroChat",
    model="gpt-4o",
    instructions=SYSTEM_PROMPT,
    tools=[
        get_contract_state,
        get_market_rates,
        get_fgts_status,
        simulate_amortization,
        project_scenario,
        compare_scenarios,
        compare_invest_vs_amortize,
        evaluate_portability_multi,
        run_stress,
        check_eligibility,
        reconcile_ddc,
        list_operations_history,
        list_active_scenarios,
        get_scenario_by_id,
        list_coach_alerts,
        compute_pro_rata,
    ]
)
```

**SSE para chat** (`routers/chat.py`):

```python
@router.post("/chat")
async def chat(
    request: ChatRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> StreamingResponse:
    async def stream():
        async for event in Runner.run_streamed(
            chat_agent,
            messages=[{"role": "user", "content": request.message}],
            context={"user_id": user.id, "contract_id": request.contract_id, "db": session},
        ):
            if event.type == "tool_call":
                yield f"event: tool_call\ndata: {event.json()}\n\n"
            elif event.type == "text_delta":
                yield f"event: text_delta\ndata: {event.json()}\n\n"
            elif event.type == "done":
                yield f"event: done\ndata: {event.json()}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")
```

---

## Root — arquivos de suporte

```
marco-zero/
├── docker-compose.yml              ← Postgres local para desenvolvimento
├── Makefile                        ← comandos de dev unificados
└── .github/
    └── workflows/
        ├── ci.yml                  ← lint + test em todo PR
        └── deploy.yml              ← deploy automático em merge na main
```

### `docker-compose.yml`

```yaml
services:
  postgres:
    image: postgres:17-alpine
    environment:
      POSTGRES_DB: marco_zero_dev
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### `Makefile`

```makefile
.PHONY: dev dev-api dev-web db-up db-migrate test lint generate-types

# ── Dev ─────────────────────────────────────────────────────────────
dev: db-up
	make -j2 dev-api dev-web

dev-api:
	cd api && uv run uvicorn main:app --reload --port 8000

dev-web:
	cd web && npm run dev

# ── Banco ────────────────────────────────────────────────────────────
db-up:
	docker-compose up -d postgres

db-migrate:
	cd api && uv run alembic upgrade head

db-reset:
	cd api && uv run alembic downgrade base && uv run alembic upgrade head

db-seed:
	cd api && uv run python scripts/seed.py

# ── Tipos ────────────────────────────────────────────────────────────
generate-types:
	curl -s http://localhost:8000/openapi.json \
	  | npx --yes openapi-typescript - \
	  -o web/src/lib/api/generated.ts
	@echo "✓ web/src/lib/api/generated.ts atualizado"

# ── Testes ───────────────────────────────────────────────────────────
test: test-api test-web

test-api:
	cd api && uv run pytest

test-web:
	cd web && npm run test

# ── Lint ─────────────────────────────────────────────────────────────
lint: lint-api lint-web

lint-api:
	cd api && uv run ruff check . && uv run ruff format --check .

lint-web:
	cd web && npm run lint && npm run type-check
```

### CI (`ci.yml`) — em todo PR

```yaml
on: [pull_request]
jobs:
  api:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:17-alpine
        env: { POSTGRES_PASSWORD: postgres }
        ports: ["5432:5432"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: cd api && uv sync && uv run ruff check . && uv run pytest

  web:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22 }
      - run: cd web && npm ci && npm run lint && npm run type-check && npm run test
```

---

## Fluxo de desenvolvimento típico

```
Nova feature → branch → PR
  1. Mudar modelos Pydantic em api/models/
  2. Mudar ORM em api/db/models/ (se preciso)
  3. make db-migrate (gera migration Alembic)
  4. Implementar router em api/routers/
  5. make generate-types (regenera TS types)
  6. Implementar componente em web/src/
  7. Testes: make test
  8. Lint: make lint
  9. PR → CI → deploy preview (Vercel)
```

O passo 5 (`generate-types`) é o que mantém frontend e backend em sync automaticamente. Sem esse passo, o CI falha no `type-check` do frontend se a API mudou.

---

## Próximo: setup do ambiente

Com estrutura definida, o próximo passo é:
- [ ] Inicializar `web/` com Vite + React + TanStack Router + shadcn/ui
- [ ] Inicializar `api/` com FastAPI + SQLAlchemy + Alembic
- [ ] Aplicar migrations do `schema_01.md`
- [ ] Seed das reference tables (`ref_banks`, `ref_amortization_systems`, etc.)
- [ ] Implementar motor (`api/motor/sac.py` primeiro — base de tudo)
