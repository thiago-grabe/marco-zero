# Tenor — Jornada 1: Onboarding (versão massa)

> **Objetivo**: do "tirei uma foto" ao "agora eu entendo meu financiamento" em menos de 60 segundos — **sem exigir que a pessoa saiba ler o próprio contrato**.
> **Princípio guia**: o usuário sai do onboarding sentindo que o produto **já entendeu o financiamento dele** e que pode confiar — não que ele precisa ensinar o produto nem provar que entende de finanças.
>
> Esta é a porta de entrada do público de **massa** (perfil "Confuso/Ansioso"). A versão de nicho (DDC + leitura de contrato) continua válida como fluxo avançado.

---

## Arco emocional

```
Desconfiança → Esforço mínimo → Reconhecimento → "Como ele sabe disso?" → Confiança
   landing        foto/3 campos     primeiro insight    tradução             próximo passo
```

A massa chega desconfiada ("mais um app que quer meus dados") e sem vocabulário financeiro. Cada tela é uma micro-transação de confiança: o usuário dá o mínimo, o produto devolve clareza concreta antes de pedir o próximo pedaço. **Pedir cadastro só depois do primeiro insight.**

---

## Modelo mental do usuário (massa)

> "Eu pago todo mês e não sei direito o que é aquilo. Acho que tem uns seguros que nunca pedi. Será que dá pra entender isso sem precisar ligar pro gerente — e sem dar de bandeja meus dados pro banco?"

O usuário não quer otimizar. Quer **entender** e **se sentir seguro**. A linguagem é tudo: nada de "amortização do principal", "sistema de amortização", "saldo devedor atualizado". Em vez disso: "abate a dívida", "quanto ainda falta", "quando acaba".

---

## Princípios duros

1. **Foto é o caminho padrão.** Digitar é o fallback, não o contrário.
2. **Clareza antes de cadastro.** O primeiro insight aparece antes de pedir e-mail.
3. **Tolerância à ignorância.** Aceita dados parciais; pede o resto depois; nunca pune erro de digitação.
4. **Tradução desde o primeiro número.** Todo valor vem com explicação em português.
5. **Confiança explícita.** Sem integração bancária, sem venda de dados, exclusão a um toque — dito na cara, cedo.

---

## Tela 1.1 — Landing (não autenticada)

```
┌──────────────────────────────────────────────────────────┐
│  Tenor                                                   │
│                                                          │
│                                                          │
│       Entenda seu financiamento.                         │
│       Saiba quando acaba.                                │
│       Veja se o banco está certo.                        │
│                                                          │
│       Tire uma foto do seu boleto. Em 30 segundos        │
│       a gente te mostra o que você está pagando —        │
│       e quando você se livra disso.                      │
│                                                          │
│       ┌────────────────────────────┐                     │
│       │   Começar com uma foto      │                    │
│       └────────────────────────────┘                     │
│                                                          │
│       Não tenho o boleto agora → começar pelos números   │
│       Já tenho conta? Entrar                              │
│                                                          │
│  ── Por que confiar ──────────────────────────────────   │
│                                                          │
│  • Seus dados são só seus. Sem integração bancária.      │
│  • A gente não vende seus dados pra banco nenhum.        │
│  • Você pode apagar tudo a qualquer momento.             │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões
- **Headline troca otimização por clareza/proteção** — fala com quem nunca entendeu o boleto.
- **CTA de foto em primeiro lugar**; o "pelos números" é discreto.
- **Bloco de confiança no fold inicial.** Para a massa, a barreira não é interesse — é desconfiança.

---

## Tela 1.2 — Captura por foto

```
┌──────────────────────────────────────────────────────────┐
│  ←  Vamos ler seu boleto                                 │
│                                                          │
│   ┌────────────────────────────────────────────┐         │
│   │                                              │        │
│   │            📷  Tirar foto                    │        │
│   │       do boleto ou do demonstrativo          │        │
│   │                                              │        │
│   └────────────────────────────────────────────┘         │
│                                                          │
│   [  🖼  Escolher da galeria  ]                          │
│                                                          │
│   Pode ser o boleto do mês ou o demonstrativo anual      │
│   (DDC). Quanto mais completo, melhor a leitura.         │
│                                                          │
│   Prefere digitar? São só 3 campos →                     │
│                                                          │
│   ⓘ A imagem é processada só pra extrair os números.     │
│      A gente não guarda seu nome nem seu CPF.            │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões
- **Extração assistida por IA** (modelo barato/Haiku) lê os campos; o usuário **confirma** antes de salvar (tela 1.3.1).
- **Aviso de privacidade no ponto de fricção** — exatamente onde o usuário hesita em mandar um documento.

---

## Tela 1.2.1 — Conferência da leitura (depois da foto)

```
┌──────────────────────────────────────────────────────────┐
│  ←  Confere se eu li certo                               │
│                                                          │
│  Li isso do seu boleto. Ajuste o que estiver errado:     │
│                                                          │
│  Saldo que ainda falta     [ R$ 429.629,87 ]             │
│  Parcela                   [ R$   1.247,00 ]             │
│  Parcelas restantes        [ 189 ] meses                 │
│  Tipo                      [ SAC ▾ ]   (achei no boleto) │
│                                                          │
│  Não achei: taxa de juros — posso estimar pelos números  │
│  acima, ou você informa se souber.  [ Estimar ]          │
│                                                          │
│  [  Está certo, continuar  ]                             │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões
- **Humano no controle da extração.** A IA propõe, o usuário confirma. Reduz erro e aumenta confiança.
- **Campo faltante não trava o fluxo** — o produto estima e segue.

---

## Tela 1.3 — Fallback de 3 campos

```
┌──────────────────────────────────────────────────────────┐
│  ←  Só preciso de 3 números                              │
│                                                          │
│  Você acha todos no app do seu banco, na tela do         │
│  financiamento. Não precisa acertar de primeira.         │
│                                                          │
│  Saldo devedor hoje          [  R$            ]          │
│    quanto ainda falta pagar                              │
│                                                          │
│  Valor da parcela            [  R$            ]          │
│                                                          │
│  Parcelas que faltam         [        ] meses            │
│                                                          │
│  Não sei algum desses → me ajuda a achar                 │
│                                                          │
│  [  Ver meu financiamento  ]                             │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Tela 1.3.1 — "Me ajuda a achar"

```
┌──────────────────────────────────────────────────────────┐
│  ←  Onde achar cada número                               │
│                                                          │
│  Saldo devedor                                           │
│   No app do banco → Financiamentos → seu contrato.       │
│   Pode aparecer como "saldo devedor" ou "saldo atual".   │
│                                                          │
│  Valor da parcela                                        │
│   É o valor do boleto do mês.                            │
│                                                          │
│  Parcelas que faltam                                     │
│   Costuma aparecer como "prazo restante" ou              │
│   "parcelas a vencer".                                   │
│                                                          │
│  [ Entendi, voltar ]                                     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões
- **Três campos, não dez.** A massa abandona formulário longo.
- **Ajuda contextual** reduz o abandono de quem não sabe onde achar o dado.

---

## Tela 1.4 — Primeiro insight (o "reconhecimento")

```
┌──────────────────────────────────────────────────────────┐
│  Pronto. Aqui está o seu financiamento.                  │
│                                                          │
│        Você se livra disso em                            │
│            ┌─────────────────┐                           │
│            │   Março / 2042   │   faltam 15 anos e 9 m   │
│            └─────────────────┘                           │
│                                                          │
│  Da sua parcela de R$ 1.247, hoje:                       │
│   ▓▓▓▓▓▓▓▓▓▓▓▓░░░░  R$ 812  são juros                    │
│   ▓▓▓░░░░░░░░░░░░░  R$ 341  abatem a dívida              │
│   ░░░░░░░░░░░░░░░░  R$  94  são seguros (MIP + DFI)       │
│                                                          │
│  ⓘ "Por que tão pouco abate a dívida?" → toque pra      │
│     eu te explicar.                                      │
│                                                          │
│  ── E agora? ──────────────────────────────────────      │
│  [  Conferir se o banco está certo  ]                    │
│  [  Ver o que muda se eu adiantar um pouco  ]            │
│                                                          │
│  Quer guardar isso? [ Criar conta grátis ]               │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões
- **A data de quitação é o herói.** É a resposta que a massa mais quer.
- **A quebra da parcela é o "aha".** Ver que R$ 812 de R$ 1.247 são juros é chocante e engaja.
- **Cadastro só agora**, enquadrado como "guardar" — o valor já foi entregue.
- **Duas âncoras plantadas:** guardião (conferir o banco) e adiantamento pequeno.

---

## Tela 1.5 — Criar conta (mínimo atrito)

```
┌──────────────────────────────────────────────────────────┐
│  ←  Criar conta grátis                                   │
│                                                          │
│  Pra guardar seu financiamento e conferir o banco        │
│  sempre que quiser.                                      │
│                                                          │
│  E-mail            [                          ]          │
│  Senha             [                          ]          │
│                                                          │
│  [  Criar conta  ]                                       │
│                                                          │
│  Ao criar, você aceita os Termos e a Política de         │
│  Privacidade. [ler]                                      │
│                                                          │
│  ⓘ A análise por IA é opcional e você liga/desliga       │
│     quando quiser, nas configurações.                    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões
- **E-mail + senha** (magic link como opção). Sem pedir nome/CPF — coerente com a promessa de privacidade.
- **Consentimento de IA é opt-in explícito**, não pré-marcado.

---

## Casos de borda

### Foto ilegível
```
Não consegui ler direito essa imagem.
Tenta de novo com mais luz e o boleto reto — ou
me passa os 3 números na mão.  [ Tentar foto ]  [ Digitar ]
```

### Financiamento quase quitado
```
Boa notícia: falta pouco! Você se livra disso em
Nov/2026 — daqui a 6 meses. Quer conferir se o
saldo final que o banco vai cobrar está certo?
```

### Múltiplos contratos
```
Vi que você tem mais de um financiamento nesse
demonstrativo. Quer cadastrar os dois? Você troca
entre eles lá em cima, no nome do imóvel.
[ Cadastrar os dois ]   [ Só este por enquanto ]
```

---

## Diferenças nicho × massa

| | Nicho (Quitador) | Massa (Confuso) |
|---|---|---|
| Entrada | DDC, leitura de contrato | Foto do boleto / 3 campos |
| Primeiro valor entregue | Cenário de quitação | "Quando acaba" + quebra da parcela |
| Linguagem | Técnica (SAC, amortização) | Tradução ("abate a dívida") |
| Pedido de cadastro | Cedo (já está convencido) | Só após o primeiro insight |

---

## Métricas que importam

| Métrica | Meta |
|---|---|
| Conclusão do onboarding (landing → primeiro insight) | > 60% |
| Uso da foto vs digitação | acompanhar; foto deve dominar |
| Cadastro após o primeiro insight | > 35% |
| Tempo até o primeiro insight | < 60 s |
