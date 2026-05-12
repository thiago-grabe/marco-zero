# Tenor

**Tenor é o cofre privado do seu financiamento imobiliário.** O nome vem de *tenor* — o termo técnico em banking para o prazo contratual de um empréstimo. Quando um analista diz "a 30-year tenor", está falando exatamente do horizonte que define a vida financeira do mutuário. É isso que o Tenor te ajuda a entender, encurtar e otimizar.

Ninguém deveria precisar de planilhas complexas ou 6 conversas com uma IA para entender o que vai acontecer com a maior dívida da vida. Tenor resolve isso com um motor de cálculo determinístico (SAC/PRICE/modo Itaú), uma IA que chama esse motor em vez de inventar números, e uma interface dark premium que trata dinheiro como assunto sério. Cadastre seu contrato, simule cenários, converse sobre seus planos — tudo open source, sem vender dados, sem intermediários.

---

## O que é e para quem

Tenor é para o brasileiro que comprou um imóvel financiado e quer tomar decisões melhores sobre a maior dívida da vida. Profissional de TI que recebeu o bônus e não sabe se amortiza ou investe. Jovem casal que quer saber quando quita se amortizar R$ 5 mil por mês. Consultor que recebe PLR anual e quer ver o impacto de jogar tudo no financiamento em abril.

O produto nasceu de uma situação real: uma série de conversas sobre amortização que revelou que os simuladores de banco são enganosos, a nomenclatura é confusa ("reduzir prazo" vs "reduzir parcela" significam coisas diferentes do que o nome sugere), e nenhuma ferramenta existente persiste o contrato ou calcula de verdade.

---

## Início rápido

```bash
git clone https://github.com/seu-usuario/tenor.git
cd tenor
cp .env.example .env
# Edite .env → preencha OPENAI_API_KEY=sk-...
docker compose up -d
# Acesse http://localhost:3000
```

4 containers: Postgres, API, migrations e frontend. A única dependência externa é a API da OpenAI.

| Serviço | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Postgres | localhost:5490 |

---

## O que faz

| Feature | O que resolve |
|---|---|
| **Dashboard** | Veja quando quita, quanto paga, e quanto é juros — em uma tela |
| **Cenários** | "E se eu amortizar R$ 5k/mês?" — sliders em tempo real |
| **Chat IA** | Pergunte qualquer coisa. A IA chama o motor, não inventa |
| **Chat contextual** | Ao criar um cenário, a IA analisa proativamente |
| **Frequências** | Meses pares, trimestral, semestral — qualquer padrão |
| **Planilha CSV** | Baixe tabela parcela a parcela até a quitação |
| **Custos extras** | Cadastre taxas que o banco não mostra |
| **Modo Itaú** | Detecta o comportamento híbrido (manutenção de prestação) |
| **Privacidade** | CPF nunca armazenado. Dados nunca usados para treino |

---

## Seus dados são seus

| | |
|---|---|
| **Não.** | Não vendemos seus dados para bancos, corretoras ou anunciantes. |
| **Não.** | Não usamos seu contrato para treinar modelos de IA. |
| **Não.** | Não armazenamos seu CPF. |
| **Sim.** | Você exporta e apaga tudo, a qualquer hora. |
| **Sim.** | Os cálculos rodam no servidor, não na IA. |

---

## Arquitetura

Documentação completa em [`docs/`](./docs/).

```
┌──────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                          │
│  Landing · Dashboard · Onboarding · Cenários · Chat IA           │
│  React 18 · Vite · TanStack Router/Query · Tailwind · shadcn    │
└────────────────────────┬─────────────────────────────────────────┘
                         │ REST + SSE (streaming)
                         │ nginx proxy em /api
┌────────────────────────▼─────────────────────────────────────────┐
│                         API (FastAPI)                             │
│                                                                  │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │  Routers    │  │  ChatAgent   │  │   Motor SAC/PRICE/Itaú │  │
│  │             │  │  (OpenAI)    │  │                        │  │
│  │ /contracts  │  │              │  │  Funções puras         │  │
│  │ /scenarios  │  │  5 Tools de  │  │  Zero I/O              │  │
│  │ /operations │  │  Compute   ──│──│  101 testes            │  │
│  │ /chat (SSE) │  │              │  │                        │  │
│  │ /motor      │  │  GPT-4o      │  │  compute_installment   │  │
│  │ /auth       │  │              │  │  simulate_amortize     │  │
│  └──────┬──────┘  └──────────────┘  │  project_scenario      │  │
│         │                           │  compare_scenarios      │  │
│         │ SQLAlchemy + RLS          │  generate_schedule      │  │
│  ┌──────▼──────┐                    └────────────────────────┘  │
│  │ Postgres 17 │                                                 │
│  │ 5 tabelas   │                                                 │
│  │ RLS/user_id │                                                 │
│  └─────────────┘                                                 │
└──────────────────────────────────────────────────────────────────┘
```

### Como o Chat IA funciona

A IA nunca calcula. O motor calcula. A IA explica.

```
Usuário: "Quanto economizo amortizando R$ 30 mil?"
    │
    ▼
ChatAgent (GPT-4o) lê o contexto do contrato
    │
    ▼ tool call
simular_amortizacao(saldo=429629, valor=30000, modalidade='prazo')
    │
    ▼ motor SAC (Python puro, determinístico)
{ saldo_novo: 399629, parcelas_eliminadas: 13, economia: 95400 }
    │
    ▼
GPT-4o monta resposta com esses números + card visual no frontend
```

### Motor de cálculo

O motor suporta três modos de cálculo:

- **SAC** — amortização constante, parcela decrescente. Usado pela maioria dos bancos privados.
- **PRICE** — prestação constante, amortização crescente. Usado pela Caixa (MCMV).
- **Modo Itaú** — detectado automaticamente. O Itaú mantém a prestação quase constante e aumenta a amortização mensal, comprimindo o prazo mais agressivamente que o SAC padrão.

O motor aceita frequências customizadas (`meses_aporte_extra`): meses pares, trimestral, semestral, ou qualquer combinação.

---

## Stack

| Camada | Tecnologia | Por quê |
|---|---|---|
| Frontend | React 18, Vite, TanStack | SPA rápido, type-safe |
| UI | Tailwind + shadcn/ui | Dark premium, IBM Plex Serif |
| Backend | Python 3.13, FastAPI | Async, OpenAI SDK nativo |
| Motor | Python puro | Determinístico, testável |
| IA | OpenAI Agents SDK, GPT-4o | Tool calling + streaming |
| Chat render | react-markdown, remark-gfm | Tabelas BRL, tool cards |
| Banco | Postgres 17, Alembic, RLS | Isolamento por user_id |
| Auth | JWT local (bcrypt) | Zero dependência externa |
| Infra | Docker Compose | Um comando |

---

## Estrutura do projeto

```
tenor/
├── api/                          ← Backend (Python + FastAPI)
│   ├── motor/                    ← SAC/PRICE/Itaú (funções puras)
│   ├── tools/                    ← 5 Tools para o ChatAgent
│   ├── mz_agents/                ← ChatAgent (OpenAI Agents SDK)
│   ├── routers/                  ← REST + SSE
│   ├── db/                       ← SQLAlchemy + Alembic + RLS
│   └── tests/                    ← 101 testes
│
├── web/                          ← Frontend (React + Vite)
│   └── src/
│       ├── routes/               ← 7 páginas
│       ├── components/chat/      ← 6 componentes do chat
│       ├── hooks/                ← useChat, useContract, useAuth
│       └── lib/                  ← API client, auth, utils
│
├── docs/                         ← Documentação
│   ├── product/                  ← Visão, LGPD, modelo de dados
│   ├── ux/                       ← Wireframes das 7 jornadas
│   └── technical/                ← Schema, motor, parser, stack, MVP
│
├── docker-compose.yml
├── .env.example                  ← Só precisa de OPENAI_API_KEY
└── scripts/                      ← dev.sh, test.sh, setup.sh
```

---

## Desenvolvimento

```bash
./scripts/setup.sh       # instala deps + cria bancos + migrations
./scripts/dev.sh         # sobe tudo com portas dinâmicas
./scripts/test.sh        # 101 testes
```

**Testes:**
```bash
cd api && uv run pytest -v    # 101 testes em ~13s
```

---

## Sobre o nome

*Tenor* é um termo técnico de banking que significa o prazo contratual de um empréstimo ou financiamento. Para profissionais de finanças, o nome carrega significado técnico imediato. Para o usuário comum, é uma palavra curta e sonora.

O nome conversa com a marca-irmã **Alpendre** dentro do portfólio: ambos são palavras curtas, com cadência suave, que evocam algo construído com cuidado — Alpendre traz a hospitalidade da casa brasileira, Tenor traz a precisão do instrumento financeiro.

---

## Contribuindo

1. Fork o repositório
2. Crie uma branch (`git checkout -b feat/minha-feature`)
3. Faça suas mudanças com testes
4. Rode `cd api && uv run pytest` (101 testes devem passar)
5. Abra um PR

---

## Licença

MIT
