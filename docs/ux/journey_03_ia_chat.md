# Tenor — Jornada 3: Chat IA (versão massa)

> **Objetivo**: ser o **tradutor** do financiamento — substituir o "ligar pro gerente e não entender a resposta" por uma explicação em português, com a conta à mostra.
> **Princípio guia**: para a massa, esta é provavelmente a **feature killer**. As perguntas de ouro são de **tradução e desconfiança**, não de otimização.
>
> Invariante do produto (vale para todos os públicos): **a IA nunca calcula**. Todo número vem do motor determinístico, via tool. A IA escolhe a tool e explica o resultado.

---

## Modelo mental do usuário (massa)

> "Eu queria perguntar uma coisa boba sem o gerente me olhar torto. Por que minha parcela subiu? Esse seguro é obrigatório mesmo? Será que me enganaram na taxa?"

O usuário quer fazer a pergunta com as palavras dele, sem vergonha, e receber resposta clara — e quer sentir que tem alguém do lado dele, não do lado do banco.

---

## Princípios duros

1. **Tradução primeiro.** Explicar o contrato em português é o valor central.
2. **Mostre a conta.** Toda resposta numérica exibe a conta e oferece "como chegou nisso?".
3. **Tom acolhedor, não técnico-frio.** A massa chega insegura; recusa nunca humilha.
4. **Ponte natural para o guardião.** Quase toda dúvida termina em "quer que eu confira com o banco?".
5. **Recusa construtiva.** Investimento específico, jurídico e previsão de Selic: recusa + alternativa no escopo.

---

## Tela 3.1 — Chat com sugestões de massa

```
┌──────────────────────────────────────────────────────────┐
│  ←  Tire suas dúvidas                                    │
│                                                          │
│  Pergunte com suas palavras. Eu explico em português     │
│  e mostro a conta.                                       │
│                                                          │
│  Perguntas comuns:                                       │
│   ▸ Por que minha parcela aumentou esse mês?             │
│   ▸ Esse seguro (MIP/DFI) é obrigatório?                 │
│   ▸ Fui enganado nessa taxa de juros?                    │
│   ▸ Vale a pena adiantar um pouquinho?                   │
│   ▸ O que é essa "TR" que aparece no meu contrato?       │
│   ▸ Por que tão pouco da parcela abate a dívida?         │
│                                                          │
│  [  Escrever minha pergunta...                        ]  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões
- **Sugestões são perguntas reais de massa.** Tradução e desconfiança, nunca "compare meus 3 cenários".
- **Campo aberto convida pergunta com as próprias palavras.**

---

## Tela 3.2 — Resposta de tradução (com a conta)

```
┌──────────────────────────────────────────────────────────┐
│  Você                                                    │
│  Por que minha parcela subiu de R$ 1.210 pra R$ 1.247?   │
│                                                          │
│  ──────────────────────────────────────────────────      │
│  Tenor                                                   │
│                                                          │
│  Subiu R$ 37. Quase tudo é correção monetária — a TR     │
│  aplicada sobre o saldo. Veja:                           │
│                                                          │
│    Correção do saldo (TR)        + R$ 31                 │
│    Reajuste dos seguros          + R$  6                 │
│    ─────────────────────────────────────                 │
│    Aumento total                 + R$ 37  ✓              │
│                                                          │
│  Isso é normal e previsto em contrato — não é erro.      │
│  Quer que eu confira se a TR aplicada bate com a TR      │
│  oficial do período?                                     │
│                                                          │
│  [ Sim, conferir ]   [ Como chegou nesse número? ]       │
│                              👍   👎                      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões
- **A conta aparece sempre.** Transparência é o que diferencia de "perguntar pro gerente".
- **Ponte para o guardião** ("quer que eu confira?") fecha a resposta.
- **Feedback 👍/👎** por resposta — detecta alucinação e mede satisfação.

---

## Tela 3.2.1 — "Como chegou nesse número?"

```
┌──────────────────────────────────────────────────────────┐
│  ←  Como chegamos nisso                                  │
│                                                          │
│  Você perguntou: por que a parcela subiu R$ 37?          │
│                                                          │
│  Eu usei o cálculo do Tenor (não "chutei"):              │
│                                                          │
│   Saldo do mês anterior        R$ 431.200,00             │
│   TR do período                0,0723%                   │
│   Correção (saldo × TR)        R$ 31,18                  │
│   Reajuste anual dos seguros   R$ 5,90                   │
│   ───────────────────────────────────                    │
│   Diferença na parcela         R$ 37,08                  │
│                                                          │
│  Os números do contrato vêm de você/do seu boleto.       │
│  O cálculo é determinístico — não é a IA inventando.     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões
- **Rastreabilidade total.** Toda recomendação/explicação tem o caminho do número.
- **Reforça a separação IA × motor** — combate a desconfiança de "a IA inventou".

---

## Tela 3.3 — "Esse seguro é obrigatório?" (tradução de armadilha comum)

```
┌──────────────────────────────────────────────────────────┐
│  Você                                                    │
│  Esse MIP e DFI são obrigatórios? Posso tirar?           │
│                                                          │
│  ──────────────────────────────────────────────────      │
│  Tenor                                                   │
│                                                          │
│  São dois seguros obrigatórios por lei em financiamento  │
│  imobiliário:                                            │
│   • MIP (R$ 94/mês): cobre morte/invalidez — se algo     │
│     te acontecer, quita o saldo.                         │
│   • DFI (R$ 39/mês): cobre danos ao imóvel.              │
│                                                          │
│  Não dá pra tirar, mas você PODE contratar com outra     │
│  seguradora (portabilidade de seguro) — às vezes sai     │
│  mais barato que a do banco. Quer entender como?         │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões
- **Traduz a sigla e o valor**, depois dá a saída prática (portabilidade de seguro) — informação que o banco não oferece.
- **Honestidade**: "é obrigatório" sem enrolação, mas com o caminho útil.

---

## Tela 3.4 — Recusa construtiva (tom de massa)

```
┌──────────────────────────────────────────────────────────┐
│  Você                                                    │
│  Devo investir em PETR4 em vez de adiantar?              │
│                                                          │
│  ──────────────────────────────────────────────────      │
│  Tenor                                                   │
│                                                          │
│  Não recomendo ações específicas — não é o meu papel     │
│  e seria leviano. Mas posso te mostrar, com a sua        │
│  conta:                                                  │
│   ▸ o que acontece se você adiantar um pouco             │
│   ▸ adiantar vs deixar numa renda fixa simples           │
│     (sem indicar instituição)                            │
│                                                          │
│  Pra ações específicas, vale falar com um assessor       │
│  certificado pela CVM.                                   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Outras recusas (mesmo padrão)

**Previsão de Selic** → não prevê; mostra o que o mercado projeta hoje (Boletim Focus, com fonte e data) e oferece simular o contrato em diferentes níveis de Selic.

**Conselho jurídico** ("posso parar de pagar?") → não dá conselho jurídico; explica as consequências em linguagem simples, sugere procurar o banco antes de atrasar e, em risco real, a Defensoria.

### Decisões
- **Recusa sempre vira alternativa no escopo.** Nunca é beco sem saída.
- **Tom firme, mas acolhedor** — a massa não pode se sentir burra por perguntar.

---

## Tela 3.5 — Histórico de conversas

```
┌──────────────────────────────────────────────────────────┐
│  ←  Suas dúvidas                                         │
│                                                          │
│  ── Hoje ──                                              │
│   🕒 14:23  Por que minha parcela subiu?                 │
│             [ Reabrir ]  [ Apagar ]                      │
│                                                          │
│  ── Semana passada ──                                    │
│   🕒 28/04  Esse seguro é obrigatório?                   │
│             [ Reabrir ]  [ Apagar ]                      │
│                                                          │
│  ⓘ Conversas mais antigas que 30 dias são apagadas       │
│     automaticamente (plano Tranquilo).                   │
│                                                          │
│  [ Apagar todas ]   [ Exportar histórico ]               │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões
- **Retenção visível** — direito da LGPD tratado como feature.
- **Exportar** (PDF/JSON) = portabilidade.

---

## Modo privacidade (IA desligada)

```
ⓘ Você desativou a análise por IA. Você ainda pode:
  ▸ ver quando seu financiamento acaba
  ▸ conferir o banco
  ▸ rodar ensaios de adiantamento
Pra reativar: Configurações → Privacidade.
```

---

## Diferenças nicho × massa

| | Nicho (Quitador) | Massa (Confuso) |
|---|---|---|
| Perguntas-âncora | "Compare meus cenários", "vale portar?" | "Por que subiu?", "esse seguro é obrigatório?" |
| Papel | Consultor de otimização | Tradutor + guardião |
| Tom | Técnico, direto | Acolhedor, antijargão |

---

## Métricas que importam

| Métrica | Meta |
|---|---|
| Uso do chat por usuário ativo (7 dias) | > 30% |
| Perguntas por sessão | 2–4 |
| Satisfação (👍) por resposta | > 80% |
| Uso de "como chegamos nisso?" | sinal de confiança |
