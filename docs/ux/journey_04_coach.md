# Tenor — Jornada 4: Modo Coach

> **Objetivo**: deixar o produto de **reativo** (responde quando o usuário pergunta) para **ativo** (avisa quando há janela de oportunidade ou risco).
> **Princípio guia**: o Coach respeita atenção. Avisa quando importa, fica em silêncio quando não importa.

---

## Modelo mental do usuário

> "O Tenor olha pro meu contrato 24/7 e me chama quando algo importante acontece."

O Coach é o motor de **engajamento sustentável**. Faz o usuário voltar não por hábito vazio, mas porque há informação relevante esperando.

---

## Princípios duros

1. **Frequência respeitosa**. Coach nunca avisa duas vezes a mesma coisa. Nunca empurra "abra o app". Nunca faz "você esqueceu de mim".
2. **Acionabilidade**. Todo alerta tem ação primária ("Ver detalhes", "Simular", "Confirmar"). Sem alerta passivo de "olha só".
3. **Reversibilidade**. Toda preferência de notificação pode ser ajustada em 2 cliques. Toda categoria pode ser silenciada.
4. **Contexto pessoal**. Coach usa dados do contrato real do usuário. Genérico ("Selic caiu, vale conferir") não é Coach — é newsletter.
5. **Detecção de fadiga**. Se o usuário ignorou 3 alertas seguidos do mesmo tipo, Coach reduz frequência sozinho.

---

## Tipos de alerta

| Tipo | Trigger | Frequência máxima |
|---|---|---|
| **FGTS — janela abrindo** | 30 dias antes do interstício de 24m | 1× por janela |
| **FGTS — janela aberta** | No dia da liberação | 1× por janela |
| **Selic em queda significativa** | Queda agregada >50bps em 3 meses | 1× por evento |
| **Aniversário de cenário** | Cenário marcado com data de execução | 7 dias antes + dia |
| **Desvio do plano** | Saldo real difere do esperado em >2% | 1× por detecção |
| **Aniversário de revisão** | 90 dias da última revisão | 1× por trimestre |
| **Janela regulatória** | Mudança de teto SFH, regra FGTS, etc. | 1× por evento |
| **Próxima parcela** | 3 dias antes do vencimento | 1× por parcela |
| **Reserva de emergência baixa** | Após declaração ou cenário agressivo | 1× a cada 30 dias |

---

## Tela 4.1 — Coach (visão principal)

```
┌──────────────────────────────────────────────────────────┐
│  Apartamento Contagem ▾                                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Coach                                                   │
│                                                          │
│  ─── Hoje (2 alertas) ──────────────────────────         │
│                                                          │
│  ┌──────────────────────────────────────────────┐        │
│  │ ⏰  FGTS libera em 28 dias                   │        │
│  │                                              │        │
│  │ Saldo estimado: R$ 47.300                    │        │
│  │ Aplicar agora corta ~19 parcelas             │        │
│  │ e economiza ~R$ 38.200 em juros              │        │
│  │                                              │        │
│  │ [ Ver detalhes ]  [ Lembrar daqui 14 dias ]  │        │
│  └──────────────────────────────────────────────┘        │
│                                                          │
│  ┌──────────────────────────────────────────────┐        │
│  │ 📉  Selic caiu 75bps em 3 meses              │        │
│  │                                              │        │
│  │ Sua taxa: 12,19% a.a.                        │        │
│  │ Caixa SBPE atual: 11,19% a.a.                │        │
│  │ Economia potencial: ~R$ 51k em juros         │        │
│  │                                              │        │
│  │ [ Simular portabilidade ]                    │        │
│  └──────────────────────────────────────────────┘        │
│                                                          │
│  ─── Esta semana ───────────────────────────────         │
│                                                          │
│  ┌──────────────────────────────────────────────┐        │
│  │ ✓  Próxima parcela: 21/05                    │        │
│  │                                              │        │
│  │ R$ 6.578,27 — débito automático              │        │
│  │ Saldo após: R$ 427.345                       │        │
│  │                                              │        │
│  │ [ Ver detalhamento ]                         │        │
│  └──────────────────────────────────────────────┘        │
│                                                          │
│  ─── Próximos 90 dias ──────────────────────────         │
│                                                          │
│  ┌──────────────────────────────────────────────┐        │
│  │ 📅  PLR Bain prevista para abril/2027        │        │
│  │                                              │        │
│  │ Você planejou amortizar R$ 60k anuais        │        │
│  │ no cenário "5k/mês + 60k/ano"                │        │
│  │                                              │        │
│  │ [ Confirmar plano ]  [ Editar cenário ]      │        │
│  └──────────────────────────────────────────────┘        │
│                                                          │
│  ┌──────────────────────────────────────────────┐        │
│  │ 📋  3 meses sem revisar cenários             │        │
│  │                                              │        │
│  │ Última revisão: 06/02/2026                   │        │
│  │ Algo mudou na sua vida ou nas suas metas?    │        │
│  │                                              │        │
│  │ [ Revisar agora ]  [ Tudo igual, OK ]        │        │
│  └──────────────────────────────────────────────┘        │
│                                                          │
│                                                          │
│  ⚙ Configurar quais alertas quero receber                │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **3 buckets temporais.** Hoje, semana, próximos 90 dias. Prioridade visual decai.
- **Cada alerta é card com ação primária e secundária.** Sem alertas "informativos vazios".
- **Botão "Lembrar daqui X dias"** posterga sem cancelar — postpone honesto.
- **"Configurar"** sempre visível embaixo. Usuário sempre pode ajustar.
- **Vazio é OK.** Se não há alertas, tela mostra: "Tudo tranquilo. Próxima revisão em 23 dias."

---

## Tela 4.2 — Detalhe de alerta (FGTS)

```
┌──────────────────────────────────────────────────────────┐
│  ←  Coach                                                │
│                                                          │
│  FGTS — janela abrindo em 28 dias                        │
│                                                          │
│  ─── Onde estamos ──────────────────────────────         │
│                                                          │
│  Última utilização do FGTS: 12/03/2024                   │
│  Interstício mínimo:        24 meses                     │
│  Próxima janela aberta:     12/03/2026                   │
│  Hoje:                      06/05/2026                   │
│                                                          │
│  ⚠ Janela já está aberta há 55 dias.                     │
│    Você ainda não usou.                                  │
│                                                          │
│  ─── Saldo estimado ────────────────────────────         │
│                                                          │
│  Você declarou saldo de R$ 35.000 em 12/03/2024.         │
│                                                          │
│  Considerando depósitos mensais médios de                │
│  R$ 583 (8% sobre salário declarado):                    │
│                                                          │
│  Saldo estimado hoje: R$ 47.300                          │
│  ⓘ Confira no app FGTS o valor exato                     │
│                                                          │
│  ─── Impacto se aplicar agora ──────────────────         │
│                                                          │
│  Saldo do contrato hoje:     R$ 429.629,87               │
│  Após amortizar R$ 47.300:   R$ 382.330                  │
│                                                          │
│  Cenário: redução de prazo                               │
│  Parcelas eliminadas:        ~31                         │
│  Quitação adiantada para:    ~junho/2039                 │
│  Economia em juros:          ~R$ 38.200                  │
│                                                          │
│  ─── Cenário: redução de parcela ───────────────         │
│                                                          │
│  Nova parcela mensal:        R$ 6.012                    │
│  (cai R$ 566/mês)                                        │
│  Quitação:                   mantém 21/01/2042           │
│                                                          │
│  ─── Recomendação ──────────────────────────────         │
│                                                          │
│  Pelo seu padrão (você prefere redução de prazo),        │
│  redução de prazo continua sendo a opção                 │
│  matematicamente superior.                               │
│                                                          │
│  [ Atualizar saldo do FGTS ]  [ Simular cenário ]        │
│                                                          │
│  [ Lembrar em 14 dias ]  [ Já apliquei ]                 │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Reconstrói o cálculo na frente do usuário.** Sem caixa-preta.
- **Estimativa do saldo é declarada como estimativa.** Pede atualização.
- **Mostra ambos os cenários (prazo vs parcela)** mesmo que o usuário tenha preferência — educação contínua.
- **"Já apliquei"** abre fluxo de registro de operação (integra com Audit).

---

## Tela 4.3 — Detalhe de alerta (Selic)

```
┌──────────────────────────────────────────────────────────┐
│  ←  Coach                                                │
│                                                          │
│  Selic em queda — vale considerar portabilidade          │
│                                                          │
│  ─── Movimento recente ─────────────────────────         │
│                                                          │
│  Selic há 3 meses (fev/2026):    15,50%                  │
│  Selic atual (mai/2026):         14,75%                  │
│  Variação:                       −75 bps                 │
│                                                          │
│  Projeção do mercado (Focus):                            │
│   • Fim de 2026: 13,00%                                  │
│   • Fim de 2027: 11,00%                                  │
│                                                          │
│  ─── Sua taxa vs mercado ───────────────────────         │
│                                                          │
│  Sua taxa Itaú:           12,19% a.a.                    │
│                                                          │
│  Tabelas públicas atuais:                                │
│   • Caixa SBPE:           11,19% + TR (~11,50% efetivo)  │
│   • Caixa pró-cotista:     9,01% + TR (~9,30% efetivo)   │
│     (requer FGTS na entrada)                             │
│   • Itaú habitacional:    11,60% + TR                    │
│   • BB:                   ~11,30%                        │
│                                                          │
│  Você está pagando ~70-100bps acima do mercado.          │
│                                                          │
│  ─── Vale fazer agora? ─────────────────────────         │
│                                                          │
│  Estimativa de portabilidade pro Caixa SBPE:             │
│                                                          │
│   Saldo a portar:        R$ 429.630                      │
│   Custos (cartório+aval): ~R$ 4.500                      │
│   Economia em juros:     ~R$ 51.000 (188 parcelas)       │
│   Payback:               ~7 meses                        │
│                                                          │
│  ─── Considerações ─────────────────────────────         │
│                                                          │
│  ✓ Selic em queda projetada — pode ser bom               │
│    travar agora antes que portabilidade saia             │
│  ⚠ Se Selic cair mais 100bps, taxas podem                │
│    cair junto. Esperar pode ser melhor.                  │
│  ⚠ Banco original (Itaú) pode contraproposta —           │
│    você tem 5 dias úteis pra avaliar                     │
│                                                          │
│  [ Iniciar simulação detalhada ]                         │
│  [ Lembrar daqui 60 dias ]                               │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Mostra projeções como projeções**, não como certezas.
- **Lista todas as opções de mercado**, não só a mais barata. Pró-cotista da Caixa tem caveat (requer FGTS na entrada) explicitado.
- **Não recomenda — informa.** "Vale fazer agora?" abre análise, não conclusão.

---

## Tela 4.4 — Detalhe de alerta (Desvio do plano)

```
┌──────────────────────────────────────────────────────────┐
│  ←  Coach                                                │
│                                                          │
│  ⚠  Detectamos um desvio no seu plano                    │
│                                                          │
│  ─── O que aconteceu ───────────────────────────         │
│                                                          │
│  Você estava executando o cenário                        │
│  "5k/mês + 60k/ano" desde 04/05/2026.                    │
│                                                          │
│  Em 21/06/2026 (parcela #6), o saldo esperado era:       │
│   R$ 422.345                                             │
│                                                          │
│  Mas o saldo declarado pelo banco foi:                   │
│   R$ 427.345                                             │
│                                                          │
│  Diferença: +R$ 5.000                                    │
│                                                          │
│  ─── Possíveis causas ──────────────────────────         │
│                                                          │
│  • Você pulou a amortização extra de R$ 5k este mês      │
│  • A amortização extra não foi aplicada por erro         │
│    operacional do banco                                  │
│  • O mês teve correção monetária diferente do            │
│    esperado (improvável — diferença é grande demais)     │
│                                                          │
│  ─── O que fazer ───────────────────────────────         │
│                                                          │
│  Se você pulou intencionalmente:                         │
│   [ Está tudo bem, ajustar plano ]                       │
│                                                          │
│  Se não pulou e quer corrigir:                           │
│   [ Aplicar R$ 5k extra agora ]                          │
│                                                          │
│  Se quer investigar com o banco:                         │
│   [ Marcar como em investigação ]                        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Detecção é o que diferencia Tenor de simuladores.** Audita o real contra o planejado.
- **Lista causas plausíveis.** Sem assumir má-fé do banco nem do usuário.
- **3 ações possíveis.** Aceitar desvio, corrigir, investigar.

---

## Tela 4.5 — Detalhe de alerta (Aumento de renda)

```
┌──────────────────────────────────────────────────────────┐
│  ←  Coach                                                │
│                                                          │
│  💰  Sua renda aumentou — o que fazer?                   │
│                                                          │
│  Você atualizou sua renda de R$ 30.000 para              │
│  R$ 38.000 em 06/05/2026 (+27%).                         │
│                                                          │
│  ─── O cenário atual ───────────────────────────         │
│                                                          │
│  Cenário em execução: "5k/mês + 60k/ano"                 │
│                                                          │
│  Comprometimento sobre renda antiga: 38%                 │
│  Comprometimento sobre renda nova: 30%                   │
│                                                          │
│  ✓ Você ganhou folga financeira.                         │
│                                                          │
│  ─── Possibilidades ────────────────────────────         │
│                                                          │
│  Cenário A — Aumentar aporte                             │
│  Você manteria o mesmo comprometimento de 38%            │
│  e poderia aumentar aporte mensal para R$ 8.000.         │
│                                                          │
│   • Quitação:    21/04/2028 (1 ano antes)                │
│   • Economia:    +R$ 24k em juros                        │
│                                                          │
│  Cenário B — Manter aporte e diversificar                │
│  Você mantém R$ 5k/mês na hipoteca e aplica              │
│  os R$ 3.000 a mais em renda fixa (CDI).                 │
│                                                          │
│   • Em 3 anos: ~R$ 130k acumulados em CDI líquido        │
│   • Quitação: mantém 21/04/2029                          │
│                                                          │
│  Cenário C — Manter aporte e melhorar reserva            │
│  Você reforça reserva de emergência ou outros            │
│  objetivos pessoais primeiro.                            │
│                                                          │
│   • Reserva atual declarada: R$ 35.000                   │
│   • Reserva ideal pro plano atual: R$ 70.000             │
│   • Em 12 meses: cobertura completa                      │
│                                                          │
│  ─── Recomendação contextual ───────────────────         │
│                                                          │
│  Se sua reserva ainda não está em nível                  │
│  confortável (6× parcela), C primeiro. Depois            │
│  reavaliar entre A e B conforme apetite a risco.         │
│                                                          │
│  [ Quero aumentar aporte ]  [ Quero diversificar ]       │
│  [ Quero reforçar reserva ]  [ Decidir depois ]          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Trigger é declaração explícita** de mudança de renda pelo usuário.
- **3 cenários, não decisão única.** Aumentar aporte é só uma opção entre três.
- **Recomendação contextual considera reserva.** Sem assumir que dinheiro extra deve ir na hipoteca.

---

## Tela 4.6 — Configuração de alertas

```
┌──────────────────────────────────────────────────────────┐
│  ←  Coach                                                │
│                                                          │
│  Configurar alertas                                      │
│                                                          │
│  ─── Ativar / desativar ────────────────────────         │
│                                                          │
│  ✓ FGTS                                  [✓ Ligado]      │
│    Janela abrindo, janela aberta                         │
│                                                          │
│  ✓ Selic e portabilidade                 [✓ Ligado]      │
│    Quedas significativas, mudanças regulatórias          │
│                                                          │
│  ✓ Próxima parcela                       [✓ Ligado]      │
│    3 dias antes de cada vencimento                       │
│                                                          │
│  ✓ Cenários e aniversários               [✓ Ligado]      │
│    Aporte planejado se aproxima                          │
│                                                          │
│  ✓ Desvios do plano                      [✓ Ligado]      │
│    Saldo real difere do esperado                         │
│                                                          │
│  ✓ Revisão trimestral                    [✓ Ligado]      │
│    Lembre de revisar se algo mudou na vida               │
│                                                          │
│  ─── Onde receber ──────────────────────────────         │
│                                                          │
│  Dentro do app                            [✓ Ligado]     │
│  E-mail                                   [✓ Ligado]     │
│  Push (mobile)                            [✓ Ligado]     │
│  SMS                                      [✗ Desligado]  │
│                                                          │
│  ─── Frequência ────────────────────────────────         │
│                                                          │
│  Alertas críticos (parcela, FGTS aberto):                │
│  ⦿ Sempre   ⦾ 1× ao dia (resumo)                         │
│                                                          │
│  Alertas informativos (Selic, eventos):                  │
│  ⦾ Sempre   ⦿ 1× por semana (resumo)                     │
│                                                          │
│  ─── Modo "férias" ─────────────────────────────         │
│                                                          │
│  Pausar todos os alertas até:                            │
│  [ DD/MM/AAAA ]                                          │
│                                                          │
│  Coach continua monitorando, mas não envia               │
│  notificações. Você vê tudo quando voltar.               │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Granularidade real.** Cada categoria pode ser ligada/desligada separadamente.
- **Múltiplos canais.** Usuário escolhe onde receber.
- **Frequência por nível de criticidade.** Alertas críticos sempre; informativos podem virar resumo semanal.
- **Modo férias.** Pausa total com data de retorno. Viagem, lua-de-mel, recuperação médica.

---

## Tela 4.7 — Estado vazio (sem alertas)

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│  Coach                                                   │
│                                                          │
│                                                          │
│        ┌──────────────────┐                              │
│        │       ☼          │                              │
│        │                  │                              │
│        │   Tudo tranquilo │                              │
│        │                  │                              │
│        └──────────────────┘                              │
│                                                          │
│        Não há alertas ativos.                            │
│                                                          │
│        Próxima revisão programada para                   │
│        06/08/2026 (em 91 dias).                          │
│                                                          │
│        ─── Próximos eventos no calendário ───            │
│                                                          │
│        21/05  Parcela #5 — R$ 6.578                      │
│        12/03  Janela FGTS abre                           │
│        04/27  Aniversário aporte anual                   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Estado vazio é informativo, não punitivo.** Mostra calendário de eventos.
- **Sem mensagens "volte amanhã"** ou call-to-action falso. Tudo bem estar tranquilo.

---

## Detecção de fadiga

Se o usuário ignorou 3 alertas seguidos do mesmo tipo (sem clicar, sem ação), o Coach se adapta:

```
Você tem ignorado os alertas de Selic.

Quer que eu reduza a frequência ou pare de
enviar esse tipo?

[ Reduzir para mensal ]
[ Parar de enviar ]
[ Continuar como está ]
```

### Decisão

- **Pergunta é direta.** Sem culpa, sem manipulação.
- **3 opções honestas.** Inclui "continuar como está" caso o usuário queira manter mas só não tem agido.

---

## Diferenças por plano

| Funcionalidade | Básico | Plus | Avançado |
|---|---|---|---|
| FGTS coach | ✓ | ✓ | ✓ |
| Próxima parcela | ✓ | ✓ | ✓ |
| Selic e portabilidade | — | ✓ | ✓ |
| Eventos de vida | — | ✓ | ✓ |
| Desvio do plano | — | ✓ | ✓ |
| Revisão trimestral | — | ✓ | ✓ |
| Aumento de renda | — | ✓ | ✓ |
| Alertas customizáveis | — | — | ✓ |
| Modo férias | ✓ | ✓ | ✓ |

---

## Métricas que importam

| Métrica | Meta |
|---|---|
| Alertas processados / semana | depende do contrato (esperado 0-3) |
| Taxa de ação por alerta | > 40% |
| Taxa de "lembrar depois" | < 30% |
| Taxa de desativação de categoria | < 10% |
| Taxa de uso semanal do Coach | > 60% dos usuários ativos |

---

## Relação com privacidade

- **Coach roda do lado servidor.** Tem acesso ao contrato do usuário (RLS scopado), nada cruza para outros usuários.
- **Cálculos de alertas são determinísticos.** SAC, FGTS, datas — tudo matemática conhecida, sem IA.
- **Notificações externas** (e-mail, SMS, push) **não levam dados sensíveis no corpo.** Mensagem genérica + link autenticado para o app. "Você tem um novo alerta no Tenor" — não "Sua taxa de 12,19% está acima da Caixa de 11,19%".
- **Dados de Selic, taxas de mercado** vêm de fontes públicas, não vinculados ao usuário.
- **Trigger de alerta** roda em batch (job recorrente), não em tempo real — reduz superfície de ataque.
