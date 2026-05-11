# Marco Zero

**Copiloto de quitação de financiamento imobiliário para o Brasil.**

Simule cenários de amortização, veja quando quita, e converse com uma IA que entende seu contrato — sem enviar seus dados para treinar modelos.

---

## Início rápido

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/marco-zero.git
cd marco-zero

# 2. Copie o .env e adicione sua chave OpenAI
cp .env.example .env
# Edite .env e preencha: OPENAI_API_KEY=sk-...

# 3. Suba tudo
docker compose up -d

# 4. Acesse
# http://localhost:3000
```

Isso sobe Postgres, API e frontend. A única dependência externa é a API da OpenAI.

---

## O que faz

- **Motor SAC/PRICE/Itaú** — cálculos determinísticos de amortização, projeção de cenários e comparação de estratégias
- **Chat IA** — pergunte qualquer coisa sobre seu contrato. A IA chama ferramentas de cálculo (nunca inventa números)
- **Cenários** — sliders em tempo real: "e se eu amortizar R$5k/mês?"
- **Privacidade** — CPF nunca armazenado, dados nunca usados para treino, tudo auditável

---

## Seus dados são seus

| | |
|---|---|
| **Não.** | Não vendemos seus dados. |
| **Não.** | Não usamos seu contrato para treinar IA. |
| **Não.** | Não armazenamos seu CPF. |
| **Sim.** | Você exporta e apaga tudo, a qualquer hora. |
| **Sim.** | Os cálculos rodam no servidor, não na IA. |

---

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | React 18, Vite, TanStack Router/Query, Tailwind, shadcn/ui |
| Backend | Python 3.13, FastAPI, SQLAlchemy 2.0 async |
| Motor | SAC/PRICE/Itaú — funções puras, zero I/O, testáveis |
| IA | OpenAI Agents SDK (GPT-4o), SSE streaming |
| Banco | Postgres 17 |
| Auth | JWT local (bcrypt + python-jose) |

---

## Desenvolvimento local (sem Docker)

```bash
# Pré-requisitos: uv, node 22+, docker (para Postgres)
./scripts/setup.sh
./scripts/dev.sh
```

**Testes:**
```bash
cd api && uv run pytest -v   # 76 testes
```

---

## Arquitetura

```
marco-zero/
├── api/                  ← FastAPI + motor + agentes
│   ├── motor/            ← SAC, PRICE, Itaú (funções puras)
│   ├── tools/            ← Tools de compute (chamadas pela IA)
│   ├── mz_agents/        ← ChatAgent (OpenAI Agents SDK)
│   ├── routers/          ← endpoints REST + SSE
│   └── db/               ← SQLAlchemy + Alembic + RLS
├── web/                  ← React + Vite
│   └── src/routes/       ← landing, login, onboarding, dashboard, cenários, chat
├── docs/                 ← documentação de produto, UX e arquitetura
└── docker-compose.yml    ← docker compose up -d
```

---

## Documentação

| Área | Arquivo |
|---|---|
| Visão e LGPD | `docs/product/idea_01.md` |
| Wireframes (7 jornadas) | `docs/ux/journey_*.md` |
| Schema relacional | `docs/technical/schema_01.md` |
| Motor SAC/PRICE/Itaú + 17 Tools | `docs/technical/motor_01.md` |
| Agente de extração | `docs/technical/parser_01.md` |
| Decisões de stack | `docs/technical/stack_01.md` |
| MVP scope | `docs/technical/mvp_01.md` |

---

## Contribuindo

1. Fork o repositório
2. Crie uma branch (`git checkout -b feat/minha-feature`)
3. Faça suas mudanças com testes
4. Abra um PR

---

## Licença

MIT
