# Tenor — Decisões de Stack

> Documento de design — versão 2
> Data: 06/05/2026
> Status: em discussão — revisado após decisões de OpenAI + separação frontend/backend
> Depende de: `schema_01.md`, `motor_01.md`, `parser_01.md`

---

## Referência de design — Cumbuca

O site https://www.cumbuca.com/launchweek/ foi citado como referência visual. O que esse design tem:
- Dark theme: fundo preto puro, tipografia branca, alto contraste
- Density respeitosa: componentes espaçados, hierarquia clara sem poluição
- Premium e técnico: sem ilustrações, sem gradientes, sem ornamentos
- Estrutura modular: cards, grid, separadores claros

**Tensão com o design atual:** `product/idea_01.md` define "sofisticação tropical" com bege quente, off-white e verde-mata — paleta oposta. O que o Cumbuca inspira é provavelmente a **estrutura e a densidade** (não a paleta escura).

**Decisão pendente:** manter paleta clara ("Alpendre") ou migrar para dark mode como modo principal? Dois caminhos viáveis:
- **Alpendre (claro):** bege + off-white + verde-mata — único no mercado, mais acolhedor
- **Dark premium (Cumbuca):** preto + branco + âmbar — mais técnico, mais moderno

Qualquer um funciona com a tipografia e os padrões de componente definidos. A decisão impacta apenas tokens de cor — não a arquitetura de UI.

---

## Como usar este documento

Cada seção é uma **decisão independente**. Cada decisão tem:
- O contexto do problema
- As opções realistas (não todas — só as que fazem sentido para este produto)
- Trade-offs explícitos
- Uma recomendação fundamentada

As decisões têm dependências entre si — a ordem abaixo reflete essa precedência.

---

## Decisão 1 — Alvo de plataforma

**Pergunta:** Web, mobile ou ambos? Se ambos, qual vem primeiro?

**Contexto do produto:**
- 80% das interações são de "check rápido" (dashboard, próxima parcela) → mobile
- 20% das interações são de planejamento profundo (cenários, comparações) → desktop
- Ambos foram tratados como co-iguais no design (`journey_06_dashboard.md`)

**Opções:**

| Opção | O que é | Prós | Contras |
|---|---|---|---|
| **Web first, PWA depois** | Começa como web app; adiciona manifest+SW para instalar no celular | Um codebase, deploy simples, funciona no desktop | Experiência mobile menos nativa (sem haptics, câmera direta, etc.) |
| **React Native / Expo** | App nativo desde o início | Experiência nativa no celular | Dois ambientes (web + native), complexidade dobrada para MVP |
| **Web only (sem PWA)** | Só web, sem instalar | Zero overhead | Usuário mobile fica com experiência inferior |

**Recomendação:** Web first com PWA progressivo.

Tenor não tem features que exigem APIs nativas (câmera, sensores, notificações push podem ser web push). O ganho de PWA sobre web é a instalabilidade — o usuário adiciona à tela inicial e abre como app. Para um produto financeiro com uso de baixa frequência (poucos acessos por mês, mas cada acesso é importante), isso é suficiente.

React Native adiciona complexidade de manutenção antes de validar product-market fit. Quando o produto tiver 10k+ usuários ativos e houver evidência de que a experiência nativa importa, vale migrar o mobile para RN/Expo mantendo o web.

**→ Decisão:** Web app + PWA. Native mobile é fase 2.

---

## Decisão 2 — Separação frontend / backend

**Contexto:** a arquitetura agêntica com OpenAI exige um backend Python persistente. Agentes com tool loops, multi-pass extraction, e background jobs do Coach não se encaixam em serverless Route Handlers com timeout de 30s. A separação é consequência natural, não preferência estética.

**Por que Python no backend:**
- OpenAI Python SDK é o mais completo e bem documentado para tool_use e structured outputs
- OpenAI Agents SDK é Python-first (open-source, GA)
- Thiago já conhece FastAPI (projetos `alpendre/`, `investment-simulation/`)
- Async FastAPI com SSE suporta streaming de chat nativamente
- `uv` como package manager — já é o padrão do workspace

**Divisão de responsabilidades:**

```
Frontend (React + Vite, TypeScript)
  → Toda a UI, zero lógica de negócio
  → Comunica via REST + SSE com o backend
  → Não conhece OpenAI, não conhece o banco diretamente

Backend (Python + FastAPI)
  → Todos os agentes OpenAI
  → Motor de cálculo SAC/PRICE/Itaú
  → Acesso ao banco (Supabase, via asyncpg + RLS)
  → Agente de extração de DDC
  → Coach background jobs
  → Emite SSE para streaming do chat
```

**O problema dos sliders — resolvido com debounce:**

Com frontend/backend separados, sliders de cenário fazem chamadas à API (`POST /api/motor/project`). A preocupação de latência é real mas gerenciável:
- RTT Fly.io GRU → usuário SP: ~15–25ms
- FastAPI async + motor Python puro: ~5ms de processamento
- Total por chamada: ~20–30ms
- Com debounce de 200ms no slider: usuário percebe como "tempo real"

300ms de debounce (conservador) + 30ms de RTT = resultado aparece ~330ms após parar de mover. Imperceptível no contexto de um planejamento financeiro.

**→ Decisão:** Frontend React + Vite separado do Backend Python + FastAPI.

---

## Decisão 3 — Motor de cálculo

**Contexto:** com backend Python, o motor vive em Python. Não há razão para manter TypeScript client-side se o backend é Python — seria duplicar a matemática em duas linguagens.

**→ Decisão:** Motor em Python puro, no backend em `api/motor/`. Funções puras, sem I/O, testáveis com pytest. Sliders usam API com debounce de 200ms.

**Estrutura do motor:**

```python
# api/motor/sac.py        — cálculos SAC
# api/motor/price.py      — cálculos PRICE  
# api/motor/itau.py       — modo Itaú (manutenção de prestação)
# api/motor/scenario.py   — projeções e comparações
# api/motor/stress.py     — stress tests
# api/motor/portability.py — portabilidade
```

Cada módulo exporta funções puras: `compute_installment(saldo, taxa, mode) -> InstallmentBreakdown`. Zero dependências externas. Testadas com casos reais do contrato de referência do Thiago.

---

## Decisão 4 — Estrutura do repositório

**Contexto:** frontend TypeScript + backend Python num mesmo repo. Não é um monorepo clássico (sem pacotes compartilhados entre linguagens), mas ter tudo junto simplifica deploys, PRs e contexto.

**→ Decisão:** Repositório único, sem monorepo tooling. Duas pastas top-level: `web/` e `api/`.

```
marco-zero/
├── web/                        ← React + Vite (TypeScript)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── lib/                ← API client (fetch wrappers tipados)
│   ├── package.json
│   └── vite.config.ts
│
├── api/                        ← FastAPI (Python)
│   ├── agents/                 ← OpenAI agents
│   │   ├── chat.py             ← ChatAgent (IA Chat)
│   │   ├── extraction.py       ← ExtractionAgent (DDC parser)
│   │   ├── coach.py            ← CoachAgent (background)
│   │   └── reconciliation.py  ← ReconciliationAgent
│   ├── tools/                  ← 17 Tools como funções Python
│   │   ├── data.py             ← D1–D7 (lêem banco)
│   │   └── compute.py         ← C1–C10 (funções puras)
│   ├── motor/                  ← SAC/PRICE/Itaú (funções puras)
│   ├── routers/                ← FastAPI routers (chat, ddc, scenarios, etc.)
│   ├── db/                     ← asyncpg + queries + RLS helpers
│   ├── models/                 ← Pydantic models (ContractState, etc.)
│   ├── pyproject.toml
│   └── main.py
│
├── docs/                       ← Este diretório
└── README.md
```

---

## Decisão 5 — Banco de dados (backend Python)

**Contexto:** Schema em Postgres com RLS. Backend agora é Python.

**Opções:**

| Opção | O que é | Prós | Contras |
|---|---|---|---|
| **asyncpg + SQL puro** | Driver async Postgres sem ORM | Controle total, máximo performance, SQL idêntico ao `schema_01.md` | Sem migrations automáticas, sem type safety integrado |
| **SQLAlchemy async + asyncpg** | ORM maduro com suporte async | Type-safe, migrations via Alembic, amplamente adotado | ORM overhead, Alembic é mais verboso que Drizzle |
| **Supabase Python SDK** | Client Supabase para Python | Integração nativa com Auth e RLS | Menos maduro que o JS SDK; queries via PostgREST têm limitações |

**Recomendação:** SQLAlchemy async + Alembic + asyncpg.

SQLAlchemy 2.0 async é maduro, tem suporte a RLS via `set_config('app.current_user_id', ...)` antes de cada query, e Alembic gera migrations versionadas em SQL puro — compatível com o schema desenhado em `schema_01.md`. Para Supabase Auth, o backend valida o JWT do Supabase e extrai o `user_id` — sem chamar o Supabase SDK para cada request.

**→ Decisão:** SQLAlchemy 2.0 async + Alembic + asyncpg. Supabase apenas para Auth JWT validation.

---

## Decisão 6 — Autenticação (fluxo frontend/backend)

**Contexto:** Supabase Auth no frontend emite JWTs. O backend Python precisa validar esses JWTs e extrair o `user_id` para RLS.

**Fluxo:**

```
Frontend
  1. Login via Supabase Auth (magic link / OAuth)
  2. Recebe access_token (JWT assinado pelo Supabase)
  3. Envia em cada request: Authorization: Bearer <token>

Backend (FastAPI)
  4. Middleware valida JWT usando chave pública do Supabase (JWKS)
  5. Extrai user_id do claim `sub`
  6. Injeta como dependency em todos os endpoints
  7. Passa para SQLAlchemy via: SET LOCAL app.current_user_id = '<uuid>'
  8. RLS policies lêem current_setting('app.current_user_id')
```

Biblioteca: `python-jose` para validação de JWT. Zero chamadas ao Supabase API por request — apenas validação local da assinatura.

**→ Decisão:** Supabase Auth no frontend + JWT validation no backend Python.

---

## Decisão 7 — LLM: OpenAI + arquitetura agêntica

**Contexto:** produto é agentic-first. Todos os modelos são OpenAI.

### 7.1 Tiering de modelos (revisado)

Substitui a tabela anterior (que usava Sonnet/Haiku):

| Tarefa | Modelo | Razão |
|---|---|---|
| Passe 1 extração (cabeçalho) | **GPT-4o** | Crítico, contexto pequeno |
| Passe 2a anchor (tabela) | **GPT-4o** | Estabelece column_map |
| Passe 2b bulk (chunks de 50) | **GPT-4o-mini** | Repetitivo, estruturado |
| Passe 3 (operações históricas) | **GPT-4o** | Semi-estruturado, importante |
| Confirmação cruzada | **GPT-4o-mini** | Classificação binária |
| Chat Agent (ferramenta tools) | **GPT-4o** | Qualidade de raciocínio importa |
| Coach alert gerado por LLM | **GPT-4o-mini** | Template-like, baixo custo |
| Structured output (JSON schema) | **GPT-4o** | Suporte nativo no OpenAI |

### 7.2 OpenAI Agents SDK

O OpenAI Agents SDK (Python, open-source) é a abstração primária para todos os agentes do produto. Abstrai o loop de tool calls, tracing, handoffs e state management.

```python
from agents import Agent, Runner, function_tool

# Exemplo: Chat Agent
chat_agent = Agent(
    name="MarcoZeroChat",
    model="gpt-4o",
    instructions=CHAT_SYSTEM_PROMPT,
    tools=[
        get_contract_state,      # D1
        get_market_rates,        # D2
        get_fgts_status,         # D3
        simulate_amortization,   # C3
        project_scenario,        # C4
        compare_scenarios,       # C5
        compare_invest_vs_amortize, # C6
        evaluate_portability_multi, # C7
        run_stress,              # C8
        # ... todos os 17 Tools
    ]
)

result = await Runner.run(chat_agent, messages, context={"user_id": user_id})
```

### 7.3 Os 4 agentes do produto

```
┌─────────────────────────────────────────────────────────┐
│                    Agentes Tenor                    │
│                                                         │
│  ChatAgent               ExtractionAgent                │
│  ──────────              ─────────────────              │
│  model: GPT-4o           Orchestrator (GPT-4o)          │
│  tools: 17 Tools           ├─ HeaderAgent (GPT-4o)      │
│  trigger: user message     ├─ AnchorAgent (GPT-4o)      │
│  state: thread/session     ├─ BulkAgent (GPT-4o-mini)   │
│                            └─ OpsAgent (GPT-4o)         │
│                                                         │
│  CoachAgent              ReconciliationAgent            │
│  ──────────              ─────────────────              │
│  model: GPT-4o-mini      model: GPT-4o                  │
│  tools: D1, D2, D3,      tools: D1, D4, C10             │
│         list_scenarios   trigger: post-DDC import       │
│  trigger: cron (daily)   output: reconciliation result  │
│  output: coach_alerts    + natural language explanation │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**ChatAgent** — IA Chat da jornada 3:
- Recebe mensagem do usuário + `contract_id`
- Chama `get_contract_state` automaticamente no início de toda conversa
- Tool calls para responder perguntas
- Streaming via SSE para o frontend
- Threads persistem na sessão (não entre sessões)

**ExtractionAgent** — agente de extração do `parser_01.md`:
- Orchestrator coordena os 4 sub-agentes via handoffs
- Cada sub-agente faz um passe com modelo e prompt específicos
- Structured outputs com JSON schema para cada passe
- Output final: JSON canônico + confidence scores + excerpts

**CoachAgent** — background job diário:
- Roda como cron (APScheduler dentro do FastAPI, ou worker separado)
- Para cada contrato ativo: avalia as 9 regras de alerta (`motor_01.md` §Coach)
- Cria/atualiza `coach_alerts` no banco
- Usa `GPT-4o-mini` para gerar o corpo do alerta em linguagem natural

**ReconciliationAgent** — disparado após cada DDC importado:
- Recebe `contract_id` + `new_ddc_snapshot_id`
- Chama `reconcile_ddc` (Tool C10)
- Se divergente: usa LLM para explicar a divergência em linguagem natural
- Atualiza `ddc_snapshots.reconciliacao_*`

### 7.4 Comunicação frontend → backend para chat (SSE)

```
Frontend: POST /api/chat
  body: { contract_id, message, session_id? }

Backend: StreamingResponse (SSE)
  event: tool_call    → { tool: "simulate_amortization", args: {...} }
  event: tool_result  → { tool: "simulate_amortization", result: {...} }
  event: text_delta   → { delta: "Amortizando R$ 30k hoje..." }
  event: done         → { session_id: "..." }

Frontend: recebe stream, renderiza progressive
```

O frontend mostra ao usuário quando uma Tool está sendo chamada ("calculando amortização…") — isso é o "como chegamos aqui" em tempo real, não só no final.

**→ Decisão:** OpenAI Python SDK + OpenAI Agents SDK. GPT-4o para crítico, GPT-4o-mini para bulk/coach.

---

## Decisão 8 — Estilo e componentes UI

**→ Decisão:** shadcn/ui + Tailwind. **Paleta: dark premium.**

Inspiração: Cumbuca, Linear, Vercel dashboard. Fundo quase-preto, tipografia quase-branca, âmbar como acento primário.

### Design tokens (CSS variables para shadcn/ui)

```css
/* globals.css — dark mode only (sem light mode toggle) */
:root {
  /* Superfícies */
  --background:       0 0% 5%;    /* #0D0D0D — não preto puro */
  --card:             0 0% 8%;    /* #141414 — cards e modais */
  --popover:          0 0% 10%;   /* #1A1A1A — dropdowns */

  /* Texto */
  --foreground:       0 0% 95%;   /* #F2F2F2 — texto primário */
  --muted-foreground: 0 0% 52%;   /* #858585 — labels, metadados */

  /* Bordas */
  --border:           0 0% 16%;   /* #292929 */
  --input:            0 0% 14%;   /* #242424 */
  --muted:            0 0% 14%;   /* #242424 — fundo de inputs */

  /* Âmbar — acento primário (ganho, ação, destaque) */
  --primary:          38 92% 50%; /* #F59E0B */
  --primary-foreground: 0 0% 5%;  /* texto sobre âmbar */
  --accent:           38 92% 50%;
  --accent-foreground: 0 0% 5%;

  /* Semântica financeira */
  --gain:             142 60% 42%; /* #22A45D — verde desaturado */
  --loss:             0   65% 52%; /* #E04040 — vermelho */
  --warning:          35  90% 50%; /* #F0900A — âmbar escuro */

  /* Estado */
  --ring:             38 92% 50%;  /* focus ring: âmbar */
  --destructive:      0  65% 52%;
  --radius:           0.5rem;
}
```

### Tipografia

```css
/* layout.tsx */
import { IBM_Plex_Serif, Geist } from 'next/font/google'

const serif = IBM_Plex_Serif({ weight: ['400', '600'], subsets: ['latin'] })
const sans  = Geist({ subsets: ['latin'] })

/* Uso:
   Números grandes (data de quitação, saldo):  font-serif, text-5xl, font-semibold
   Títulos de seção:                           font-serif, text-xl
   Corpo, labels, botões:                      font-sans
   Valores monetários inline:                  font-serif, tabular-nums
*/
```

### Padrões visuais definidos

| Elemento | Estilo |
|---|---|
| Data de quitação (hero do dashboard) | `font-serif text-6xl font-semibold text-foreground` |
| Valor monetário grande (saldo) | `font-serif text-3xl tabular-nums text-foreground` |
| Valor monetário inline | `font-serif tabular-nums` |
| Ganho (+economia de juros) | `text-[hsl(var(--gain))]` |
| Perda / alerta | `text-[hsl(var(--loss))]` |
| Badge de confiança (%) | `bg-card border border-border text-muted-foreground text-xs` |
| Card principal | `bg-card border border-border rounded-lg p-6` |
| Separador | `border-border` (sem cor forte) |
| Sem: gradientes de fundo, sombras coloridas, glassmorphism | |

### O que torna este dark premium distinto do genérico

- **Âmbar como acento**, não azul/roxo. Incomum em fintech, imediatamente reconhecível.
- **Serifa nos números**. A maioria dos dashboards financeiros usa monospace ou sans; serifa dá sofisticação analógica (como um relatório de banco de alta qualidade).
- **Fundo 5%, não 0%**. Preto puro (`#000`) é agressivo em monitores modernos. 5% é indistinguível do preto mas mais confortável.
- **Densidade respeitosa**: componentes espaçados com `gap-6` / `p-6` por padrão. Sem poluição de widgets.
- **Zero ornamentos**: sem ícones decorativos em botões, sem ilustrações, sem animações de entrada desnecessárias. Microinterações apenas onde comunicam estado.

---

## Decisão 9 — Hosting e deploy

| Camada | MVP | Beta (dados reais) |
|---|---|---|
| Frontend (`web/`) | Vercel | Vercel |
| Backend (`api/`) | Railway ou Fly.io | **Fly.io GRU** (São Paulo) |
| BD | Supabase Pro | Supabase Pro (região sa-east-1) |
| Storage PDFs | Cloudflare R2 | AWS S3 sa-east-1 |

**Nota:** com frontend/backend separados, o deploy do backend é independente. Railway é conveniente para MVP (zero infra config, deploy do `api/` direto). Fly.io GRU para beta por latência e soberania.

**→ Decisão:** Vercel (frontend) + Railway (backend MVP) → Fly.io GRU (backend beta).

---

## Resumo das decisões — versão 2

| # | Decisão | Escolha |
|---|---|---|
| 1 | Plataforma | Web + PWA. Native mobile fase 2. |
| 2 | Separação | **Frontend React + Vite / Backend Python + FastAPI** |
| 3 | Motor | **Python puro** em `api/motor/`. Sliders com debounce 200ms. |
| 4 | Repo | **Único repo**, duas pastas: `web/` e `api/`. Sem monorepo tooling. |
| 5 | Banco | **SQLAlchemy 2.0 async + Alembic + asyncpg** |
| 6 | Auth | **Supabase Auth** (frontend) + JWT validation (backend Python) |
| 7 | LLM + Agentes | **OpenAI SDK + OpenAI Agents SDK**. GPT-4o/GPT-4o-mini. 4 agentes. |
| 8 | UI | **shadcn/ui + Tailwind**. Paleta a definir (Alpendre vs. dark premium). |
| 9 | Hosting | Vercel (frontend) + Railway MVP → Fly.io GRU (backend). |

---

## Próximas decisões

- [x] **Paleta de cores** — dark premium (âmbar + quase-preto). Tokens definidos na §Decisão 8.
- [ ] Estratégia de testes: pytest para motor, Playwright para E2E, mocking de OpenAI
- [ ] CI/CD: GitHub Actions com lint + test + type-check + deploy preview
- [ ] Observabilidade: Sentry, Axiom (logs), PostHog (produto), OpenAI tracing nativo
- [ ] Estrutura detalhada de `web/src/` e `api/` com conventions
