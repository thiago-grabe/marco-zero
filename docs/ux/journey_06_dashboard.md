# Tenor — Jornada 6: Dashboard (versão massa)

> **Objetivo**: ser a **home** do produto de massa e responder, sem rolagem, as três perguntas universais do mutuário.
> **Princípio guia**: o herói é a **data de quitação**. O dashboard transmite tranquilidade ("está sob controle") em uma olhada.
>
> No produto de massa, o dashboard é a tela mais importante — mais até que cenários ou chat. Para o nicho, divide protagonismo com os cenários.

---

## As três perguntas universais

1. **Quando isso acaba?**
2. **Quanto eu já paguei — e quanto ainda falta?**
3. **Estou sendo enganado?** (está tudo certo com o banco?)

Tudo no dashboard serve a uma dessas três.

---

## Princípios duros

1. **Responde as 3 perguntas acima da dobra.** Sem rolar.
2. **Data de quitação como herói.** Maior elemento da tela.
3. **Reconciliação na home.** O selo "está tudo certo" gera confiança em silêncio.
4. **Uma única "ideia" por vez.** Sugestão de adiantamento pequeno, sem poluir.
5. **Sem upsell agressivo.** Upgrade tem lugar próprio, não pisca no dashboard.

---

## Tela 6.1 — Dashboard (massa)

```
┌──────────────────────────────────────────────────────────┐
│  Apartamento Contagem ▾                          ⚙       │
│                                                          │
│        Você se livra disso em                            │
│              Março / 2042                                │
│        ███████████░░░░░░░░░░░░░░░  38% pago               │
│                                                          │
│  Já paguei            R$ 187.430   (em 4 anos)           │
│  Ainda falta          R$ 429.629                          │
│  Próxima parcela      R$ 1.247  em 12 dias               │
│                                                          │
│  ── Está tudo certo? ─────────────────────────────       │
│  ✓ O saldo que o banco mostra bate com o nosso cálculo.  │
│    Última conferência: 05/05  ·  diferença R$ 0,00       │
│    [ Conferir de novo ]                                  │
│                                                          │
│  ── Uma ideia ────────────────────────────────────       │
│  💡 R$ 53 a mais por mês cortam 1 ano e 2 meses.         │
│     [ Ver como ]                                         │
│                                                          │
│  [ Entender meu boleto ]   [ Tirar uma dúvida ]          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões
- **Data de quitação + barra de progresso** = pergunta 1, resolvida no topo.
- **Já paguei / ainda falta** = pergunta 2, em linguagem direta.
- **Bloco "está tudo certo?"** = pergunta 3, com o resultado da última conferência.
- **"Uma ideia"** usa o eixo do adiantamento pequeno (jornada 2).
- **Sem cenários/stress aqui** — ficam a um toque, não na cara.

---

## Tela 6.2 — "Entender meu boleto" (tradução em um toque)

```
┌──────────────────────────────────────────────────────────┐
│  ←  Seu boleto, em português                             │
│                                                          │
│  Parcela de maio: R$ 1.247                               │
│                                                          │
│   ▓▓▓▓▓▓▓▓▓▓▓▓░░░░  R$ 812   Juros                       │
│      o "aluguel" do dinheiro que você ainda deve         │
│                                                          │
│   ▓▓▓░░░░░░░░░░░░░  R$ 341   Abate a dívida              │
│      a parte que realmente diminui o que você deve       │
│                                                          │
│   ░░░░░░░░░░░░░░░░  R$  94   Seguros (MIP + DFI)         │
│      obrigatórios por lei; toque pra entender            │
│                                                          │
│  ⓘ No começo do financiamento, a maior parte é juros.    │
│     Com o tempo, isso vira — você abate cada vez mais.   │
│                                                          │
│  [ Por que tão pouco abate? ]  [ Conferir o banco ]      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões
- **Cada componente traduzido com analogia** ("aluguel do dinheiro").
- **Explica a curva** (juros → amortização) — combate a sensação de "nunca diminui".

---

## Tela 6.3 — Linha do tempo (leve)

```
┌──────────────────────────────────────────────────────────┐
│  ←  Sua história                                         │
│                                                          │
│  Maio/2026   Parcela paga         R$ 1.247               │
│  Abr/2026    Você adiantou        R$ 80.000              │
│              → cortou ~3 anos                             │
│  Abr/2026    Parcela paga         R$ 1.243               │
│  ...                                                     │
│  Dez/2025    Financiamento começou                       │
│              R$ 536.000 · 360 meses · SAC                │
│                                                          │
│  [ Baixar tudo em PDF ]                                  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões
- **História simples e cronológica.** A massa quer ver o progresso, não auditar.
- **Adiantamentos viram conquista visível** ("cortou ~3 anos").

---

## Casos de borda

### Múltiplos contratos
```
Troca de imóvel no seletor lá em cima. Cada contrato
tem seu próprio "quando acaba" e sua própria conferência.
```

### Saldo recém-importado, sem histórico
```
Ainda não tenho histórico desse financiamento. Conforme
você for usando, eu monto sua linha do tempo aqui.
```

---

## Diferenças nicho × massa

| | Nicho (Quitador) | Massa (Confuso) |
|---|---|---|
| Protagonista | Cenários e otimização | Data de quitação + "está tudo certo?" |
| Reconciliação | Aba separada | Na home |
| "Ideia" do dia | Otimização de aporte | Adiantamento pequeno |

---

## Métricas que importam

| Métrica | Meta |
|---|---|
| Retorno ao dashboard (DAU/MAU) | acompanhar |
| Clique em "entender meu boleto" | engajamento de tradução |
| Clique em "conferir o banco" a partir da home | uso do guardião |
