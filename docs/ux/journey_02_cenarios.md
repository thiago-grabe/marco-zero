# Marco Zero — Jornada 2: Cenários

> **Objetivo**: brincar com possibilidades sem medo de quebrar nada.
> **Princípio guia**: cenários são **sandboxes**, não compromissos. O usuário deve sentir que pode explorar agressivamente sem consequências.

---

## Modelo mental do usuário

> "Quero ver o que acontece se eu fizer X, Y, ou Z. Sem precisar fazer cálculo, sem precisar lembrar de tudo."

Cenários são o coração do produto. É onde o usuário **vai voltar 50 vezes** ao longo da vida do contrato. Cada simulação custa nada. O retorno emocional é alto: ele sai com clareza.

---

## Tela 2.1 — Lista de cenários

```
┌──────────────────────────────────────────────────────────┐
│  Apartamento Contagem ▾                  [Coach] [⚙]    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Cenários                                                │
│                                                          │
│  ┌────────────────────────────────────────────────┐      │
│  │ +  Novo cenário                                │      │
│  └────────────────────────────────────────────────┘      │
│                                                          │
│  ─── Em execução ──────────────────────────────────      │
│                                                          │
│  ┌────────────────────────────────────────────────┐      │
│  │ ▣  Plano atual                                 │      │
│  │                                                │      │
│  │    Quitação:    21/01/2042                     │      │
│  │    Parcela:     R$ 6.578,27                    │      │
│  │    Comprometimento mensal: R$ 6.578            │      │
│  │                                                │      │
│  │    [Ver detalhes →]                            │      │
│  └────────────────────────────────────────────────┘      │
│                                                          │
│  ─── Planejados ──────────────────────────────────       │
│                                                          │
│  ┌────────────────────────────────────────────────┐      │
│  │ ▢  "5k/mês após maio"          criado 03/05    │      │
│  │                                                │      │
│  │    Quitação:    21/04/2031     −10 anos 9m     │      │
│  │    Esforço:     R$ 5k/mês extra                │      │
│  │    Economia:    R$ 267k em juros               │      │
│  │                                                │      │
│  │    [Ver]  [Editar]  [Comparar]  [×]            │      │
│  └────────────────────────────────────────────────┘      │
│                                                          │
│  ┌────────────────────────────────────────────────┐      │
│  │ ▢  "5k/mês + 60k/ano"          criado 04/05    │      │
│  │                                                │      │
│  │    Quitação:    21/04/2029     −12 anos 9m     │      │
│  │    Esforço:     R$ 5k/mês + R$ 60k anual       │      │
│  │    Economia:    R$ 309k em juros               │      │
│  │                                                │      │
│  │    [Ver]  [Editar]  [Comparar]  [×]            │      │
│  └────────────────────────────────────────────────┘      │
│                                                          │
│  ┌────────────────────────────────────────────────┐      │
│  │ ▢  "10k/mês + 60k/ano"         criado 05/05    │      │
│  │                                                │      │
│  │    Quitação:    21/07/2028     −13 anos 6m     │      │
│  │    Esforço:     R$ 10k/mês + R$ 60k anual      │      │
│  │    Economia:    R$ 332k em juros               │      │
│  │                                                │      │
│  │    [Ver]  [Editar]  [Comparar]  [×]            │      │
│  └────────────────────────────────────────────────┘      │
│                                                          │
│  ─── Arquivados (2) ──────────────────────────────       │
│                                                          │
│  [Mostrar arquivados]                                    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **3 buckets visíveis: em execução / planejados / arquivados.** A divisão deixa claro o estado de cada cenário.
- **Plano atual sempre destacado em primeiro.** É a referência contra a qual todos os cenários são comparados.
- **Cards mostram 3 KPIs**: quitação, esforço, economia. Tudo o resto está em "Ver".
- **Comparar** é ação primária — leva direto ao modo de comparação multi-cenário.
- **Arquivados ficam colapsados.** Cenários que o usuário descartou ficam acessíveis sem poluir.

---

## Tela 2.2 — Criação de cenário

```
┌──────────────────────────────────────────────────────────┐
│  ←  Novo cenário                                         │
│                                                          │
│  ─── Identificação ──────────────────────────            │
│                                                          │
│  Nome do cenário                                         │
│  ┌──────────────────────────────────────┐                │
│  │ Acelerar pós-PLR                     │                │
│  └──────────────────────────────────────┘                │
│                                                          │
│  ─── Aportes extras ─────────────────────────            │
│                                                          │
│  Aporte mensal extra                                     │
│  ──────────●──────  R$ 5.000                             │
│  R$ 0           R$ 20.000                                │
│                                                          │
│  Aporte anual extra                                      │
│  ────────────●────  R$ 60.000                            │
│  R$ 0           R$ 100.000                               │
│                                                          │
│  Mês do aporte anual                                     │
│  ⦾ Janeiro   ⦾ Fevereiro   ⦾ Março   ⦿ Abril            │
│  ⦾ Maio      ⦾ Junho       ⦾ Julho   ⦾ Agosto           │
│  ⦾ Setembro  ⦾ Outubro     ⦾ Novembro ⦾ Dezembro        │
│                                                          │
│  ─── FGTS ───────────────────────────────────            │
│                                                          │
│  Usar FGTS quando liberar?                               │
│  ⦿ Sim, automaticamente a cada janela                    │
│  ⦾ Não usar                                              │
│                                                          │
│  Saldo FGTS estimado hoje                                │
│  R$ [ 47.300 ]   ⓘ Você atualiza esse valor              │
│                                                          │
│  Próxima janela (informada por você)                     │
│  [ 12/03/2026 ▾ ]                                        │
│                                                          │
│  ─── Resultado em tempo real ────────────────            │
│                                                          │
│  Quitação                21/04/2029                      │
│  Cortou                  12 anos 9 meses                 │
│  Juros economizados      R$ 308.760                      │
│  Comprometimento mensal  ~R$ 11.500                      │
│  Reserva mínima sugerida R$ 70.000                       │
│                                                          │
│  ⚠ Comprometimento alto (35% da renda declarada).        │
│    Considere ter reserva confortável antes.              │
│                                                          │
│  [ Salvar cenário ]    [ Descartar ]                     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Sliders, não inputs por padrão.** Manipulação direta dá feedback visceral. Click no número permite digitar.
- **Ranges dos sliders são razoáveis para o contrato específico.** Pra alguém com saldo de R$ 430k, slider mensal vai até R$ 20k (quem amortiza R$ 30k/mês quita em 1 ano — caso de borda).
- **Mês do anual em radio buttons visuais**, não dropdown. Ajuda a planejar com PLR/13º.
- **FGTS é seção própria.** Tem regras específicas (24m, depósitos, etc.) que merecem espaço.
- **Resultado em tempo real (<100ms de delay).** O usuário sente a relação entre ação e consequência.
- **Avisos contextuais inline.** Comprometimento alto, reserva insuficiente — sem popup, sempre visível.
- **"Reserva mínima sugerida"** é cálculo do produto: 6× a parcela cheia atual.

---

## Tela 2.3 — Visualização de cenário

```
┌──────────────────────────────────────────────────────────┐
│  ←  "5k/mês + 60k/ano"                                   │
│                                                          │
│  [ Editar ]  [ Duplicar ]  [ Comparar com... ]  [ × ]    │
│                                                          │
│  ─── Resumo ────────────────────────────────────         │
│                                                          │
│  Quitação              21/04/2029  (vs 21/01/2042)       │
│  Tempo cortado         12 anos 9 meses                   │
│  Juros economizados    R$ 308.760                        │
│  Total investido       R$ 349.645 em extras              │
│                                                          │
│  ─── Plano ano a ano ───────────────────────────         │
│                                                          │
│  ┌──────┬──────┬──────────┬──────────┬──────────┐        │
│  │ Ano  │Meses │ Mensal+  │ Anual    │ Saldo fim│        │
│  ├──────┼──────┼──────────┼──────────┼──────────┤        │
│  │ 2026 │  7   │  35.000  │     0    │ 378.633  │        │
│  │ 2027 │ 12   │  60.000  │  60.000  │ 231.210  │        │
│  │ 2028 │ 12   │  60.000  │  60.000  │  83.786  │        │
│  │ 2029 │  4   │  20.000  │  54.645  │       0  │        │
│  └──────┴──────┴──────────┴──────────┴──────────┘        │
│                                                          │
│  ─── Saldo ao longo do tempo ───────────────────         │
│                                                          │
│       R$ 430k ╮                                          │
│              │ ╲                                         │
│              │  ╲╲ plano atual (linha pontilhada)        │
│              │   ╲╲╲                                     │
│              │     ╲╲╲                                   │
│              │       ╲╲                                  │
│              │         ╲                                 │
│       R$ 0  ╯───────────────●────────●─────●────         │
│             2026         2029       2035  2042           │
│                                                          │
│  ─── Trade-offs ────────────────────────────────         │
│                                                          │
│  Em troca dos R$ 350k investidos, você:                  │
│                                                          │
│  ✓ Termina 12 anos 9 meses antes                         │
│  ✓ Economiza R$ 309k em juros                            │
│  ✓ Libera R$ 6.578/mês a partir de 04/2029               │
│                                                          │
│  ⚠ Concentra patrimônio no imóvel por ~3 anos            │
│  ⚠ Reduz capacidade de investir em paralelo              │
│                                                          │
│  [Comparar com investir em CDI]                          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Tabela ano a ano vem antes do gráfico.** Brasileiro lê da esquerda pra direita, top-down — números antes de visualizações.
- **Gráfico mostra cenário sobreposto ao plano atual.** Sem isso, falta referência visual de "quanto encurtou".
- **Trade-offs são parte estrutural da tela.** Honestidade sobre o lado negativo. "Concentra patrimônio no imóvel" é caveat real.
- **CTA "comparar com investir"** abre análise da Jornada 3 (IA Chat) com pergunta pré-preenchida.

---

## Tela 2.4 — Comparar cenários

```
┌──────────────────────────────────────────────────────────┐
│  ←  Comparando 3 cenários                                │
│                                                          │
│  ┌────────────────┬────────────────┬────────────────┐    │
│  │ Plano atual    │ 5k/mês + 60k   │ 10k/mês + 60k  │    │
│  │                │                │                │    │
│  │ Quitação       │ Quitação       │ Quitação       │    │
│  │ 21/01/2042     │ 21/04/2029     │ 21/07/2028     │    │
│  │                │                │                │    │
│  │ Tempo restante │ Tempo restante │ Tempo restante │    │
│  │ 16 anos        │ 3 anos         │ 2 anos 3 meses │    │
│  │                │                │                │    │
│  │ Juros totais   │ Juros totais   │ Juros totais   │    │
│  │ R$ 391k        │ R$ 82k         │ R$ 59k         │    │
│  │                │                │                │    │
│  │ Esforço/mês    │ Esforço/mês    │ Esforço/mês    │    │
│  │ R$ 6.578       │ R$ 11.578      │ R$ 16.578      │    │
│  │                │                │                │    │
│  │ Investido em   │ Investido em   │ Investido em   │    │
│  │ extras         │ extras         │ extras         │    │
│  │ R$ 0           │ R$ 350k        │ R$ 370k        │    │
│  │                │                │                │    │
│  │ Comprometi-    │ Comprometi-    │ Comprometi-    │    │
│  │ mento da renda │ mento da renda │ mento da renda │    │
│  │ 22%            │ 38%            │ 55%            │    │
│  │                │                │                │    │
│  └────────────────┴────────────────┴────────────────┘    │
│                                                          │
│  ─── Visualização ──────────────────────────────         │
│                                                          │
│       R$ 430k ╮                                          │
│              │╲                                          │
│              │ ╲    ─── plano atual                      │
│              │  ╲   ─ ─ 5k/mês + 60k                     │
│              │   ╲  ──── 10k/mês + 60k                   │
│              │    ╲                                      │
│              │     ╲                                     │
│              │      ╲                                    │
│              │       ╲                                   │
│       R$ 0  ╯─────●───●───●─────────────────             │
│             26   28  29   30        ...   42             │
│                                                          │
│  ─── Análise ────────────────────────────────            │
│                                                          │
│  Você está chegando no piso de retorno marginal.         │
│                                                          │
│  De plano atual → 5k/mês: +R$ 295k investidos →          │
│    R$ 309k economizados (1:1.05)                         │
│                                                          │
│  De 5k+60k → 10k+60k: +R$ 20k investidos →               │
│    R$ 24k economizados (1:1.20)                          │
│                                                          │
│  Cada real adicional rende cada vez menos. Avalie        │
│  diversificar parte do esforço em renda variável.        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Tabela 3 colunas em desktop, swipe horizontal em mobile.** Comparação visual lado a lado.
- **Gráfico sobreposto** mostra todos os cenários junto. Cor diferente, mesma legenda.
- **"Comprometimento da renda"** depende do usuário ter declarado renda — se não, mostra "—" e botão "informar".
- **Análise de retorno marginal** é pequeno toque que vira insight: o produto pensa, não só calcula.

---

## Tela 2.5 — Promover cenário a "plano atual"

Quando o usuário clica em "Promover" num cenário planejado:

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│  ⚠  Promover "5k/mês + 60k/ano" para plano atual?        │
│                                                          │
│  Isso significa que você está se comprometendo           │
│  a executar este cenário de fato.                        │
│                                                          │
│  ─── O que acontece ───                                  │
│                                                          │
│  ✓ Marco Zero passa a usar este como referência.         │
│  ✓ Coach vai te lembrar dos aportes mensais.             │
│  ✓ Coach vai te lembrar do aporte anual em abril.        │
│  ✓ Cenário anterior (R$ 6.578/mês sem extras)            │
│    fica arquivado para referência.                       │
│                                                          │
│  ⓘ Você pode despromover a qualquer momento.             │
│                                                          │
│  [ Cancelar ]    [ Sim, promover ]                       │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Confirmação dupla.** Promover muda como o produto se comporta — coach, alertas, dashboard. Merece pausa.
- **Lista o que muda.** Sem mistério.
- **Reversibilidade explícita.** "Você pode despromover a qualquer momento" reduz ansiedade.

---

## Casos de borda

### Cenário com aporte > capacidade declarada

```
⚠ O comprometimento mensal de R$ 16.500 representa
   55% da sua renda declarada (R$ 30.000).

   Padrões saudáveis ficam abaixo de 35%. Recomendamos
   revisar reserva de emergência antes de promover.

   [Editar cenário]    [Salvar mesmo assim]
```

### Cenário que zera saldo antes de receber último aporte

```
ⓘ No último mês (abril/2029), você só precisa
   pagar R$ 54.645 do aporte anual de R$ 60.000
   para zerar o saldo.

   Os R$ 5.355 restantes ficam livres para investir.
```

### Edição de cenário em uso

Se o usuário tenta editar um cenário que está promovido:

```
Você está editando o plano em execução.

Mudanças aqui afetam alertas, dashboard e Coach
imediatamente.

Quer:
[Editar plano em execução]
[Criar novo cenário a partir deste]
```

---

## Diferenças por plano

| Funcionalidade | Básico | Plus | Avançado |
|---|---|---|---|
| Cenários simultâneos | 2 | Ilimitado | Ilimitado |
| Comparar simultâneo | 2 | 4 | 4 |
| FGTS no cenário | ✓ | ✓ | ✓ |
| Eventos de vida | — | ✓ | ✓ |
| Versionamento de cenário | última | últimas 3 | ilimitado |
| Promover cenário | ✓ | ✓ | ✓ |
| Análise de retorno marginal | — | ✓ | ✓ |
| Comparar com investir (link p/ IA) | — | ✓ | ✓ |

---

## Métricas que importam

| Métrica | Meta |
|---|---|
| Cenários criados por usuário ativo | > 3 em 30 dias |
| Tempo médio para criar 1 cenário | < 60s |
| Taxa de promoção de cenário | > 40% dos usuários ativos |
| Taxa de comparação multi-cenário | > 50% dos usuários com 2+ cenários |
| Taxa de retorno para editar cenário | > 30% em 7 dias |

---

## Relação com privacidade

- **Cenários são dados próprios do usuário.** Ficam no cofre, não vão para LLM externamente.
- **Cálculo de cenário é determinístico.** SAC é matemática conhecida — roda no servidor sem IA.
- **IA só entra se o usuário pedir explicação** ("explique o resultado", "compare com investir") — aí entra a Jornada 3.
