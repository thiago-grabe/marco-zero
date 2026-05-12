# Tenor — MVP

> Documento de escopo — versão 1
> Data: 10/05/2026
> Status: definido, pronto para implementar

---

## Premissa

O produto completo tem 7 jornadas, 17 Tools de IA, agente de extração multi-pass,
Coach com background jobs, Stress Tests, Audit e portabilidade.

O MVP entrega somente o **aha moment** — e nada mais:

> *"Você entra com seu contrato, vê quando quita, e simula o que acontece
>  se amortizar mais."*

Isso é 5 telas. O resto vem depois, quando houver usuários para validar.

---

## O que está IN

### 1. Landing page
- Já implementada em `web/src/routes/index.tsx`
- Seção "Seus dados são seus" com padrão de negação (enzonotes-inspired)
- CTA → onboarding

### 2. Auth — magic link
- Supabase Auth, e-mail + magic link
- Sem senha, sem OAuth no MVP
- Session JWT validado no backend (já tem middleware em `api/middleware/auth.py`)

### 3. Onboarding — entrada manual
- Formulário de 6 campos: banco, sistema (SAC/PRICE), taxa mensal, saldo devedor,
  amortização mensal, vencimento da próxima parcela
- Sem DDC parser no MVP — o usuário consulta no app do banco e digita
- Apelido do contrato (ex: "Apartamento Contagem")
- Confirmação antes de salvar

### 4. Dashboard
- Herói: data de quitação em serifa grande
- Linha do tempo: início → hoje → quitação
- 3 KPIs: saldo devedor, próxima parcela, parcelas restantes
- Barra de progresso
- Card "próxima ação" (estático no MVP: lembrete de próximo vencimento)
- Dados vindos do banco de dados (não mais mock)

### 5. Cenários
- Criar cenário com sliders: aporte mensal extra, aporte anual, mês do anual
- Resultado em tempo real via `POST /motor/project` (já funciona)
- Salvar até 2 cenários (plano Básico)
- Comparar lado a lado: data quitação + juros economizados + total extra investido
- Promover cenário a "plano em execução"

---

## O que está OUT (V2)

| Feature | Motivo |
|---|---|
| DDC parser (agente OpenAI) | Complexo; entrada manual é suficiente para validar |
| ~~IA Chat~~ | ~~Diferenciação futura~~ | **IN — é o diferencial central do produto** |
| Coach (background jobs, alertas) | Útil mas não blocker para primeira sessão |
| Stress Tests | V2 — after product-market fit |
| Audit / reconciliação DDC | V2 |
| Portabilidade | V2 |
| Investir vs. amortizar | V2 |
| FGTS coach | V2 |
| Co-titular / compartilhamento | V2 |
| Upload de PDF | V2 — após validar que usuários onboardam sem ele |
| Planos pagos / billing | V2 — MVP é gratuito para primeiros 100 usuários |

---

## Schema MVP — 5 tabelas

Subconjunto do `schema_01.md`, sem reference tables complexas.

```sql
-- 1. Extensão do user (Supabase Auth gerencia auth.users)
user_profiles (
  id            uuid PK FK → auth.users
  nome          text nullable
  created_at    timestamptz
)

-- 2. Imóvel (apelido apenas)
properties (
  id            uuid PK
  user_id       uuid FK → auth.users   -- RLS
  apelido       text NOT NULL
  created_at    timestamptz
)

-- 3. Contrato (campos do motor)
contracts (
  id                    uuid PK
  user_id               uuid FK → auth.users   -- RLS
  property_id           uuid FK → properties
  apelido               text nullable
  banco                 text NOT NULL         -- 'itau', 'caixa', etc.
  sistema_amortizacao   text NOT NULL         -- 'SAC', 'PRICE'
  taxa_mensal           numeric(12,10) NOT NULL
  saldo_devedor         numeric(14,2) NOT NULL
  amortizacao_mensal    numeric(14,2) NOT NULL
  mip_mensal            numeric(14,2) DEFAULT 0
  dfi_mensal            numeric(14,2) DEFAULT 0
  data_proxima_parcela  date NOT NULL
  prazo_remanescente    int NOT NULL
  valor_original        numeric(14,2) nullable
  data_inicio           date nullable
  created_at            timestamptz
  updated_at            timestamptz
)

-- 4. Cenários
scenarios (
  id                    uuid PK
  user_id               uuid FK → auth.users   -- RLS
  contract_id           uuid FK → contracts
  nome                  text NOT NULL
  aporte_mensal_extra   numeric(14,2) DEFAULT 0
  aporte_anual_extra    numeric(14,2) DEFAULT 0
  mes_aporte_anual      int nullable           -- 1–12
  status                text DEFAULT 'planejado'
  created_at            timestamptz
  updated_at            timestamptz
)

-- 5. Operações declaradas (amortizações que o usuário registrou)
user_operations (
  id              uuid PK
  user_id         uuid FK → auth.users   -- RLS
  contract_id     uuid FK → contracts
  tipo            text NOT NULL          -- 'amortizacao_prazo', 'amortizacao_parcela'
  data_operacao   date NOT NULL
  valor_principal numeric(14,2) NOT NULL
  notas           text nullable
  created_at      timestamptz
)
```

**RLS**: todas as tabelas têm `user_id` e políticas `WHERE user_id = auth.uid()`.
O `user_id` é extraído do JWT Supabase no middleware da API.

---

## Rotas da API MVP

```
GET    /health                          ← já existe

POST   /auth/me                         ← retorna user atual (cria user_profile se não existe)

GET    /contracts                       ← lista contratos do usuário
POST   /contracts                       ← criar contrato (onboarding)
GET    /contracts/:id                   ← contrato + estado calculado
PATCH  /contracts/:id                   ← atualizar campos
DELETE /contracts/:id                   ← soft delete

GET    /contracts/:id/scenarios         ← lista cenários do contrato
POST   /contracts/:id/scenarios         ← criar cenário
PATCH  /scenarios/:id                   ← editar cenário
DELETE /scenarios/:id                   ← remover cenário

POST   /motor/project                   ← já existe (sliders em tempo real)
POST   /motor/simulate-amortization     ← já existe

GET    /contracts/:id/operations        ← histórico de amortizações
POST   /contracts/:id/operations        ← registrar nova amortização
```

---

## Rotas do Frontend MVP

```
/                   ← landing page (já existe)
/login              ← magic link form
/onboarding         ← fluxo de cadastro do contrato (4 passos)
/dashboard          ← dashboard principal (substituir mock por dados reais)
/scenarios          ← lista e criação de cenários
```

---

## Ordem de implementação

### Fase 1 — Fundação (banco + auth)
1. Alembic migration com as 5 tabelas
2. SQLAlchemy models (ORM para as 5 tabelas)
3. RLS policies no Postgres (via migration)
4. Seed das reference tables básicas (bancos)
5. Testar JWT middleware com Supabase

### Fase 2 — Backend CRUD
6. `routers/contracts.py` — CRUD + cálculo de estado (chama motor)
7. `routers/scenarios.py` — CRUD
8. `routers/operations.py` — criar operação + recalcular prazo

### Fase 3 — Frontend conectado
9. Supabase Auth no frontend (magic link + session)
10. `/login` — tela simples de magic link
11. `/onboarding` — 4 passos: banco → campos → revisão → primeiro insight
12. `/dashboard` — substituir dados mock por chamada real à API
13. `/scenarios` — sliders + salvar + comparar

### Fase 4 — Deploy + polish
14. Migrations no banco de produção (Supabase)
15. Deploy API no Railway
16. Deploy frontend no Vercel
17. Variáveis de ambiente de produção
18. Smoke test end-to-end

---

## Critério de "pronto para lançar"

Um usuário consegue, sem ajuda:
- [ ] Criar conta com e-mail
- [ ] Cadastrar seu contrato (6 campos)
- [ ] Ver a data de quitação no plano atual
- [ ] Criar um cenário "e se eu amortizar R$5k/mês?"
- [ ] Ver quanto economiza e quando quita no novo cenário
- [ ] Fechar o app e voltar 3 dias depois com os dados preservados

Isso é o MVP. Nada mais.

---

## Deploy de produção (simplificado)

| Camada | Serviço | Custo estimado |
|---|---|---|
| Frontend | Vercel Hobby (gratuito) | $0 |
| Backend | Railway Starter | ~$5/mês |
| Banco + Auth | Supabase Free | $0 |
| Total | | ~$5/mês |

Para primeiros 100 usuários, sem custo relevante. Migrar para planos pagos quando houver tração.
