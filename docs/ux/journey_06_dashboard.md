# Tenor — Jornada 6: Dashboard

> **Objetivo**: ser legível em 3 segundos. Responder "como estou indo?" sem cliques.
> **Princípio guia**: a data da quitação é o herói. Tudo o mais é contexto.

---

## Modelo mental do usuário

> "Abro o app, vejo se está tudo certo, e sigo com a vida. Quando preciso ir mais fundo, sei onde achar."

Dashboard é tela mais visitada do produto. **80% das aberturas** terminam aqui mesmo — o usuário olha, fica tranquilo, fecha. As outras 20% são portais para Cenários, Coach, Chat, Stress, Audit.

---

## Princípios duros

1. **Tempo > dinheiro.** A data da quitação é maior que o saldo. As pessoas se conectam com "abril/2029" mais que com "R$ 308 mil em juros".
2. **3 segundos pra ler.** Tipografia hierarquizada brutal — uma coisa enorme, três médias, resto pequeno.
3. **Próxima ação visível, no máximo uma.** Mais que uma vira ruído — manda pro Coach.
4. **Sem widgets vazios.** Sem "0 cenários" — se não tem cenário, é onboarding leve com CTA.
5. **Mobile e desktop são iguais em conteúdo, diferentes em layout.** Mobile = stack vertical. Desktop = grid 12 colunas.

---

## Tela 6.1 — Dashboard (estado completo)

```
┌──────────────────────────────────────────────────────────┐
│  Apartamento Contagem ▾              [Coach 2] [perfil]  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│                                                          │
│              Quitação em                                 │
│                                                          │
│                  abril                                   │
│                  2029                                    │
│                                                          │
│              12 anos e 9 meses                           │
│              antes do plano original                     │
│                                                          │
│                                                          │
│  ─●────────────●───────────────────────────●──           │
│  início     hoje                       quitação          │
│  12/2025    05/2026                    04/2029           │
│                                                          │
│                                                          │
│ ─────────────────────────────────────────────────────    │
│                                                          │
│  Próxima parcela     Saldo devedor     Juros já pagos    │
│                                                          │
│  R$ 6.578,27         R$ 429.630        R$ 32.461         │
│  21/05/2026          de R$ 536.000     em 6 meses        │
│                                                          │
│ ─────────────────────────────────────────────────────    │
│                                                          │
│  Próxima ação                                            │
│                                                          │
│  ┌──────────────────────────────────────────────┐        │
│  │ ⏰  FGTS libera em 28 dias                   │        │
│  │                                              │        │
│  │ Aplicar corta ~19 parcelas e economiza       │        │
│  │ ~R$ 38.200 em juros                          │        │
│  │                                              │        │
│  │ [ Ver no Coach → ]                           │        │
│  └──────────────────────────────────────────────┘        │
│                                                          │
│ ─────────────────────────────────────────────────────    │
│                                                          │
│  Saldo ao longo do tempo                                 │
│                                                          │
│  R$ 536k ╮                                               │
│         ●╲                                               │
│           ╲ ●                                            │
│             ╲ ● ←  você está aqui                        │
│               ╲╲                                         │
│                 ╲╲                                       │
│                   ╲                                      │
│                    ╲╲                                    │
│                      ╲                                   │
│  R$ 0    ╯─────────────●────────────────────             │
│         12/25       05/26        04/29                   │
│                                                          │
│  Você já caminhou 19,8% do total.                        │
│                                                          │
│ ─────────────────────────────────────────────────────    │
│                                                          │
│  Atalhos                                                 │
│                                                          │
│  [ Cenários (3) ]   [ Chat IA ]   [ Stress ]   [ Audit ] │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **"abril 2029" é o herói.** Tipografia gigante, serifa, centralizada. O número que o usuário lembra.
- **Linha do tempo física.** Mostra início, hoje, quitação. Visual de progresso.
- **3 KPIs secundários** — parcela, saldo, juros pagos. Cobrem 90% das perguntas pontuais.
- **1 próxima ação.** Vinda do Coach. Se há mais, link manda pro Coach.
- **Gráfico simples.** Linha decrescente do saldo. Marcador "você está aqui". Sem 8 séries de dados.
- **Atalhos no rodapé** para outras seções. Não navegação principal — atalhos de uso frequente.

---

## Tela 6.2 — Dashboard (estado vazio — sem contratos)

```
┌──────────────────────────────────────────────────────────┐
│  Tenor                                  [perfil]    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│                                                          │
│                                                          │
│              Seu cofre está pronto.                      │
│                                                          │
│              Adicione seu primeiro contrato              │
│              para começar.                               │
│                                                          │
│                                                          │
│              ┌──────────────────────────┐                │
│              │  Adicionar contrato      │                │
│              └──────────────────────────┘                │
│                                                          │
│                                                          │
│              ─── O que você ganha ───                    │
│                                                          │
│              ✓ Veja quando termina de pagar              │
│              ✓ Simule cenários sem limite                │
│              ✓ Receba alertas de FGTS e Selic            │
│              ✓ Auditoria do que o banco te cobra         │
│                                                          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Vazio acolhedor**, não punitivo.
- **Reforça promessa** com 4 benefícios concretos.
- **CTA único.** Sem distração.

---

## Tela 6.3 — Dashboard (estado intermediário — sem cenários)

```
┌──────────────────────────────────────────────────────────┐
│  Apartamento Contagem ▾              [Coach 1] [perfil]  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│              Quitação em                                 │
│                                                          │
│                  janeiro                                 │
│                  2042                                    │
│                                                          │
│              No plano padrão do banco                    │
│                                                          │
│  ─●────●─────────────────────────────────────────●──     │
│  início hoje                                  quitação   │
│                                                          │
│ ─────────────────────────────────────────────────────    │
│                                                          │
│  Próxima parcela     Saldo devedor     Juros já pagos    │
│  R$ 6.578,27         R$ 429.630        R$ 32.461         │
│                                                          │
│ ─────────────────────────────────────────────────────    │
│                                                          │
│  ┌──────────────────────────────────────────────┐        │
│  │  💡 Que tal explorar?                        │        │
│  │                                              │        │
│  │  Você ainda não criou cenários. Veja como    │        │
│  │  decisões pequenas podem cortar anos do      │        │
│  │  seu contrato.                               │        │
│  │                                              │        │
│  │  [ Criar primeiro cenário ]                  │        │
│  └──────────────────────────────────────────────┘        │
│                                                          │
│ ─────────────────────────────────────────────────────    │
│                                                          │
│  Atalhos                                                 │
│                                                          │
│  [ Coach ]   [ Chat IA ]   [ Stress ]   [ Audit ]        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Sem destaque "−12 anos antes do original"** porque não há cenário em execução.
- **Convite gentil para criar cenário.** Sem pressão.

---

## Tela 6.4 — Dashboard (múltiplos contratos)

Quando o usuário tem mais de um contrato, o dashboard padrão é do contrato selecionado. Mas há uma **visão consolidada** disponível:

```
┌──────────────────────────────────────────────────────────┐
│  Visão Consolidada ▾                          [perfil]   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Você tem 2 contratos.                                   │
│                                                          │
│  ─── Apartamento Contagem (Itaú) ───────────────         │
│                                                          │
│  Saldo:           R$ 429.630                             │
│  Próxima parcela: R$ 6.578 em 21/05                      │
│  Quitação:        21/04/2029  (cenário "5k+60k")         │
│                                                          │
│  [Abrir →]                                               │
│                                                          │
│  ─── Casa de praia (Bradesco) ──────────────────         │
│                                                          │
│  Saldo:           R$ 215.000                             │
│  Próxima parcela: R$ 3.200 em 15/05                      │
│  Quitação:        15/05/2038  (plano padrão)             │
│                                                          │
│  [Abrir →]                                               │
│                                                          │
│  ─── Resumo financeiro ─────────────────────────         │
│                                                          │
│  Saldo total devedor:    R$ 644.630                      │
│  Compromisso mensal:     R$ 9.778                        │
│  Última quitação:        15/05/2038                      │
│                                                          │
│  ⓘ Esta tela é apenas leitura. Para gerenciar           │
│    cada contrato, abra individualmente.                  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Read-only.** Visão consolidada não permite ação. Forçar usuário a abrir contrato específico para gerenciar.
- **3 cards: 2 contratos + resumo.** Clareza visual.
- **Compromisso mensal e última quitação** são os 2 KPIs mais úteis na visão agregada.

---

## Tela 6.5 — Dashboard mobile (single column)

Em mobile, mesma informação em stack vertical:

```
┌──────────────────────────┐
│ Apt Contagem ▾    [⚙]    │
├──────────────────────────┤
│                          │
│      Quitação em         │
│                          │
│         abril            │
│         2029             │
│                          │
│     12a 9m antes         │
│      do original         │
│                          │
│ ●─────●──────────●       │
│ início hoje  quitação    │
│                          │
├──────────────────────────┤
│                          │
│ Próxima parcela          │
│ R$ 6.578,27              │
│ em 21/05/2026            │
│                          │
├──────────────────────────┤
│                          │
│ Saldo devedor            │
│ R$ 429.630               │
│ de R$ 536.000            │
│                          │
├──────────────────────────┤
│                          │
│ Juros já pagos           │
│ R$ 32.461                │
│ em 6 meses               │
│                          │
├──────────────────────────┤
│                          │
│ Próxima ação             │
│                          │
│ ┌──────────────────────┐ │
│ │ ⏰ FGTS em 28 dias   │ │
│ │                      │ │
│ │ Corta 19 parcelas    │ │
│ │ Economia R$ 38k      │ │
│ │                      │ │
│ │ [ Ver no Coach → ]   │ │
│ └──────────────────────┘ │
│                          │
├──────────────────────────┤
│                          │
│ Saldo no tempo           │
│                          │
│ R$ 536k ●╮               │
│        │ ╲╮              │
│        │  ╲ ●←hoje       │
│        │   ╲╲            │
│        │    ╲╲           │
│        │      ╲          │
│ R$ 0   ╯───────●───      │
│       12/25  04/29       │
│                          │
│ 19,8% do caminho         │
│                          │
├──────────────────────────┤
│                          │
│ [Cenários] [Coach]       │
│ [IA]    [Stress] [Audit] │
│                          │
└──────────────────────────┘
```

### Decisões

- **Cada KPI ganha card próprio.** Em mobile, lado a lado vira cramped.
- **Linha do tempo simplificada** mas presente.
- **Atalhos em grid 2x3** no rodapé.

---

## Tela 6.6 — Detalhe ao clicar em KPI

Cada KPI no dashboard é clicável e abre detalhe contextual.

### Clicar em "Próxima parcela":

```
┌──────────────────────────────────────────────────────────┐
│  ←  Próxima parcela                                      │
│                                                          │
│  Parcela #6                                              │
│  Vencimento: 21/05/2026                                  │
│                                                          │
│  ─── Composição ───────────────────────────────          │
│                                                          │
│  Amortização         R$ 2.285,27                         │
│  Juros               R$ 4.137,93                         │
│  Seguro MIP          R$    93,95                         │
│  Seguro DFI          R$    38,61                         │
│  ─────────────────────────────────                       │
│  Total               R$ 6.555,76                         │
│                                                          │
│  ⓘ Pequena queda em relação à parcela anterior           │
│    (R$ 6.578,27) — natural no SAC, juros caem            │
│    com saldo decrescente.                                │
│                                                          │
│  ─── Origem dos números ───────────────────────          │
│                                                          │
│  Do DDC de 05/05/2026.                                   │
│  [Ver DDC]                                               │
│                                                          │
│  ─── Forma de pagamento ───────────────────────          │
│                                                          │
│  Débito automático na conta Itaú (declarado)             │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Clicar em "Saldo devedor":

```
┌──────────────────────────────────────────────────────────┐
│  ←  Saldo devedor                                        │
│                                                          │
│  R$ 429.629,87                                           │
│  Atualizado em 05/05/2026 (DDC)                          │
│                                                          │
│  ─── Evolução ─────────────────────────────────          │
│                                                          │
│  Valor original:        R$ 536.000,00                    │
│  Já amortizado:         R$ 106.370,13 (19,8%)            │
│   • Em parcelas:        R$ 23.370,13                     │
│   • Em amortizações:    R$ 83.000,00                     │
│                                                          │
│  ─── Histórico de saldo ───────────────────────          │
│                                                          │
│  R$ 536.000  ─  03/12/2025 (implantação)                 │
│  R$ 528.964  ─  22/12/2025 (após amort R$ 8k)            │
│  R$ 527.608  ─  03/01/2026 (parcela #1)                  │
│  R$ 527.157  ─  21/02/2026 (parcela #2)                  │
│  ...                                                     │
│  R$ 510.978  ─  21/04/2026 (parcela #4)                  │
│  R$ 431.188  ─  28/04/2026 (após amort R$ 80k)           │
│  R$ 429.630  ─  05/05/2026 (atual)                       │
│                                                          │
│  [ Ver linha do tempo completa ]                         │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Clicar em "Juros já pagos":

```
┌──────────────────────────────────────────────────────────┐
│  ←  Juros já pagos                                       │
│                                                          │
│  R$ 32.461,20  em 6 meses                                │
│  (média de R$ 5.410/mês)                                 │
│                                                          │
│  ─── Detalhamento por parcela ─────────────────          │
│                                                          │
│  #1 (jan/26)   R$ 5.094,67                               │
│  #2 (fev/26)   R$ 5.090,34                               │
│  #3 (mar/26)   R$ 4.989,81                               │
│  #4 (abr/26)   R$ 4.935,99                               │
│  #5 (mai/26)   R$ 4.159,94                               │
│  ─────────────────────────                               │
│  Total                R$ 24.270,75                       │
│                                                          │
│  + Juros pró-rata em amortizações:                       │
│   • 22/12/25: R$    46,86                                │
│   • 25/02/26: R$     6,84                                │
│   • 11/03/26: R$    30,72                                │
│   • 25/03/26: R$     6,18                                │
│   • 28/04/26: R$   178,73                                │
│   ─────────                                              │
│   Total      R$   269,33                                 │
│                                                          │
│  Total geral em juros pagos: R$ 32.461,20                │
│                                                          │
│  ─── Projeção ─────────────────────────────────          │
│                                                          │
│  Se você seguir o cenário "5k/mês + 60k/ano":            │
│                                                          │
│  Juros adicionais a pagar até quitação: R$ 82.274        │
│  Juros que você economizou (vs plano original):          │
│    R$ 308.760                                            │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Cada KPI tem detalhe rico ao clicar.** Curiosidade do usuário é sempre satisfeita.
- **Detalhamento mostra fonte.** "Do DDC de 05/05/2026" — auditável.
- **Projeção quando relevante.** No "juros já pagos", mostra também o que vai pagar e o que economizou.

---

## Tela 6.7 — Seletor de contrato

Header tem dropdown de contratos. Ao clicar:

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│  Seus contratos                                          │
│                                                          │
│  ⦿  Apartamento Contagem (Itaú) — em uso                 │
│      Saldo: R$ 429.630 · Quitação: 04/2029               │
│                                                          │
│  ⦾  Casa de praia (Bradesco)                             │
│      Saldo: R$ 215.000 · Quitação: 05/2038               │
│                                                          │
│  ─────────────────────────────────────                   │
│                                                          │
│  ⦾  Visão consolidada (todos juntos)                     │
│                                                          │
│  ─────────────────────────────────────                   │
│                                                          │
│  + Adicionar contrato                                    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Radio buttons** mostram contrato em uso.
- **Visão consolidada como opção separada**, não default.
- **Adicionar contrato** sempre acessível daqui.

---

## Diferenças por plano

| Funcionalidade | Básico | Plus | Avançado |
|---|---|---|---|
| Dashboard básico | ✓ | ✓ | ✓ |
| KPIs secundários | ✓ | ✓ | ✓ |
| Gráfico de saldo | ✓ | ✓ | ✓ |
| Linha do tempo | ✓ | ✓ | ✓ |
| Próxima ação (Coach) | ✓ (1) | ✓ (1) | ✓ (1) |
| Visão consolidada multi-contrato | — | ✓ | ✓ |
| Atalhos personalizáveis | — | — | ✓ |

---

## Métricas que importam

| Métrica | Meta |
|---|---|
| Tempo médio na tela | 15-30s (ler e fechar) |
| Taxa de cliques em "próxima ação" | > 50% quando há ação |
| Taxa de retorno diário | > 15% (não é meta de engajamento, é só sinal) |
| Taxa de cliques em KPI para detalhe | > 30% pelo menos uma vez por usuário |

---

## Relação com privacidade

- **Dashboard mostra só dados do usuário ativo.** RLS scopa.
- **Sem analytics agressivo.** Eventos limitados a "viewed_dashboard", sem heatmap.
- **Atalhos não vendem nada.** Sem "experimente Plus" piscando. Upgrade tem espaço próprio em Configurações.
- **Notificações ativas mostram badge no Coach** ([Coach 2]) — sem alertar dentro do dashboard.
