# Tenor — Jornada 3: IA Chat

> **Objetivo**: dar ao usuário um analista financeiro disponível 24/7 que conhece o contrato dele em detalhe.
> **Princípio guia**: a IA explica e compara, **nunca decide**. Toda recomendação termina com "a decisão é sua" e mostra a matemática.

---

## Modelo mental do usuário

> "Quero perguntar em português qualquer dúvida sobre o meu contrato e receber resposta clara, sem precisar abrir 5 abas."

A IA é o lugar onde o produto mais se aproxima da promessa de "copiloto". Mas é também onde mais pode dar errado: alucinação, conselho ruim, vazamento de dados.

---

## Princípios duros

1. **A IA tem acesso de leitura aos dados do contrato ATIVO, e somente esse.** Nunca dados de outros usuários, nunca dados agregados sem opt-in.
2. **A IA explica, não decide.** Toda recomendação termina com "a decisão é sua". Toda análise mostra a matemática.
3. **A IA cita a fonte de cada número.** Se ela diz "seu saldo é R$ 429k", aparece chip discreto: "do DDC de 05/05/2026".
4. **A IA tem limites declarados.** Não recomenda investimentos por nome (CDB do banco X), não fala sobre outros produtos financeiros, não opina sobre o futuro do mercado, não dá conselho jurídico.
5. **A IA jamais executa ações.** Ela não pode amortizar, mudar plano, transferir nada. Apenas informa e simula.

---

## Tela 3.1 — Estado inicial (sem conversa)

```
┌──────────────────────────────────────────────────────────┐
│  ←  Apartamento Contagem (Itaú)         [Histórico]      │
│                                                          │
│  IA — Tenor                                         │
│                                                          │
│  ┌──────────────────────────────────────────────┐        │
│  │                                              │        │
│  │  Olá. Vou usar dados do seu contrato         │        │
│  │  para responder. Pergunte o que quiser       │        │
│  │  sobre quitação, amortização, FGTS,          │        │
│  │  portabilidade ou cenários.                  │        │
│  │                                              │        │
│  │  Sugestões:                                  │        │
│  │   ▸ Quanto economizo amortizando R$ 30k?     │        │
│  │   ▸ Vale portar pro Caixa hoje?              │        │
│  │   ▸ E se eu perder o emprego?                │        │
│  │   ▸ Quando devo usar FGTS?                   │        │
│  │   ▸ Compare meus 3 cenários                  │        │
│  │                                              │        │
│  └──────────────────────────────────────────────┘        │
│                                                          │
│                                                          │
│  ┌──────────────────────────────────────────┐  ┌──┐      │
│  │ Pergunta…                                │  │ →│      │
│  └──────────────────────────────────────────┘  └──┘      │
│                                                          │
│  🔒 Conversa não treina modelos. Histórico 30 dias.      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Sugestões de pergunta são contextuais.** Mudam conforme o estado do contrato. Se FGTS está perto da janela, sugere "quando devo usar FGTS?". Se acabou de subir DDC, sugere "o que mudou?".
- **Caveat de privacidade fica visível e curto.** Sem precisar clicar "saiba mais".
- **Botão histórico** abre lateral com conversas anteriores (até 30 dias para Plus, 90 para Avançado).
- **Sem mascote, sem balão "olá!" piscando.** Tom neutro de analista.

---

## Tela 3.2 — Estrutura de uma resposta

Quando o usuário pergunta, a resposta tem **estrutura fixa de 3 camadas**:

```
┌──────────────────────────────────────────────────────────┐
│  Você                                                    │
│  Vale a pena portar pro Caixa?                           │
│                                                          │
│  ─────────────────────────────────────────────────       │
│                                                          │
│  IA — Tenor                                         │
│                                                          │
│  ─── Resposta direta ───                                 │
│                                                          │
│  Provavelmente sim. Sua taxa de 12,19% está              │
│  ~100bps acima da média Caixa SBPE de 11,19%             │
│  em maio/2026.                                           │
│                                                          │
│  ─── Análise ───                                         │
│                                                          │
│  Saldo:        R$ 429.629,87  ⓘ DDC 05/05                │
│  Sua taxa:     12,19% a.a.    ⓘ DDC 05/05                │
│  Caixa SBPE:   11,19% a.a.    ⓘ pesquisa pública 06/05   │
│                                                          │
│  Em 189 parcelas restantes:                              │
│  • Juros se ficar:    R$ 391k                            │
│  • Juros se portar:   R$ 340k                            │
│  • Economia bruta:    R$ 51k                             │
│                                                          │
│  Custos da operação:                                     │
│  • Cartório:          ~R$ 3.500                          │
│  • Avaliação imóvel:  ~R$ 1.000                          │
│  • Total estimado:    ~R$ 4.500                          │
│                                                          │
│  Payback: 7 meses                                        │
│                                                          │
│  ─── Caveats ───                                         │
│                                                          │
│  • Caixa pode oferecer taxa diferente após análise       │
│    de crédito real. A taxa de tabela é referência.       │
│  • Itaú tem direito a contraproposta — você tem          │
│    5 dias úteis pra avaliar.                             │
│  • Não considera mudança de seguros MIP/DFI, que         │
│    podem ajudar ou atrapalhar.                           │
│  • Selic está em queda projetada (15% → 13% até          │
│    fim de 2026). Se esperar, taxas podem cair mais.      │
│                                                          │
│  ─── Ações ───                                           │
│                                                          │
│  [ Abrir simulação detalhada ]                           │
│  [ Como vocês chegaram nisso? ]                          │
│  [ Salvar como cenário ]                                 │
│                                                          │
│                                                          │
│  ┌──────────────────────────────────────────┐  ┌──┐      │
│  │ Continuar perguntando…                   │  │ →│      │
│  └──────────────────────────────────────────┘  └──┘      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Anatomia da resposta

| Seção | O que faz |
|---|---|
| **Resposta direta** | 1-2 frases. Resposta literal à pergunta. |
| **Análise** | A matemática. Cada número com fonte. |
| **Caveats** | O que pode dar errado, o que não foi considerado. Nunca omitido. |
| **Ações** | CTAs concretos: simular, ver cálculo, salvar. |

### Decisões

- **Estrutura é a mesma toda vez.** Previsibilidade gera confiança. Usuário sabe onde olhar.
- **Citações inline (`ⓘ DDC 05/05`)** abrem o documento ou fonte ao clicar.
- **"Como vocês chegaram nisso?"** abre modal com fórmula completa (Tela 3.3).
- **Sem emojis na resposta.** Tom técnico-respeitoso.
- **"Salvar como cenário"** transforma a análise em cenário oficial — integra com Jornada 2.

---

## Tela 3.3 — "Como vocês chegaram nisso?" (auditoria de resposta)

```
┌──────────────────────────────────────────────────────────┐
│  ←  Memória de cálculo                                   │
│                                                          │
│  Pergunta original:                                      │
│  "Vale a pena portar pro Caixa?"                         │
│                                                          │
│  Resposta gerada em: 06/05/2026 às 14:23                 │
│                                                          │
│  ─── Dados usados ───                                    │
│                                                          │
│  Do seu contrato (DDC 05/05/2026):                       │
│    saldo_devedor      = R$ 429.629,87                    │
│    taxa_mensal        = 0,9631393%                       │
│    taxa_anual_efetiva = 12,19%                           │
│    parcelas_restantes = 189                              │
│    sistema            = SAC                              │
│                                                          │
│  De pesquisa pública (06/05/2026):                       │
│    caixa_sbpe_taxa    = 11,19% + TR (≈ 11,5% a.a.)       │
│    fonte: tabela pública Caixa, validada                 │
│      em larya.com.br/blog/...                            │
│                                                          │
│  ─── Fórmula aplicada ───                                │
│                                                          │
│  Juros totais (cenário SAC):                             │
│    juros = Σ (saldo_t × taxa_mensal)                     │
│    onde saldo_t decresce conforme amortização SAC        │
│                                                          │
│  Cenário "ficar":                                        │
│    juros_total = R$ 391.034 (188 parcelas restantes)     │
│                                                          │
│  Cenário "portar":                                       │
│    juros_total = R$ 339.821 (mesmo prazo, taxa 11,19%)   │
│                                                          │
│  Economia bruta = 391.034 − 339.821 = R$ 51.213          │
│                                                          │
│  Custos de portabilidade (referência mercado):           │
│    cartório = R$ 3.500                                   │
│    avaliação = R$ 1.000                                  │
│    custos_total = R$ 4.500                               │
│                                                          │
│  Payback = custos_total / economia_mensal_média          │
│  Payback ≈ 7 meses                                       │
│                                                          │
│  ─── Limitações desta análise ───                        │
│                                                          │
│  • Taxa Caixa é de tabela pública; taxa real pode        │
│    diferir após análise de crédito.                      │
│  • Custos de portabilidade variam por cartório e         │
│    cidade (estimativa para Belo Horizonte).              │
│  • Não considera mudança de seguros MIP/DFI.             │
│  • Não considera tendência futura de Selic.              │
│                                                          │
│  ─── Modelo usado ───                                    │
│                                                          │
│  Cálculos: motor determinístico Tenor (Python)      │
│  Geração de texto: Claude (Anthropic) — Zero Data        │
│    Retention                                             │
│                                                          │
│  Dados enviados ao LLM (após redaction):                 │
│  • Saldo, taxas, prazo (números)                         │
│  • Pergunta original do usuário                          │
│  • Resultados dos cálculos                               │
│                                                          │
│  Dados NÃO enviados:                                     │
│  • Seu nome                                              │
│  • CPF (já não consta nos dados armazenados)             │
│  • Conta, agência                                        │
│                                                          │
│  [ Reportar erro nesta análise ]                         │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Auditoria total.** Tudo que entrou, fórmula, tudo que saiu, modelo usado.
- **"Reportar erro"** envia feedback direto para o time. Importante para detectar alucinação ou bug.
- **Lista de dados NÃO enviados** é tão importante quanto a lista de enviados — comunica disciplina.
- **Limitações listadas explicitamente.** Honestidade sobre o que a análise não cobriu.

---

## Tela 3.4 — Limites da IA

Quando o usuário faz pergunta fora do escopo:

```
┌──────────────────────────────────────────────────────────┐
│  Você                                                    │
│  Devo investir em PETR4?                                 │
│                                                          │
│  ─────────────────────────────────────────────────       │
│                                                          │
│  IA — Tenor                                         │
│                                                          │
│  Não recomendo ações específicas. Tenor foca        │
│  em decisões sobre seu financiamento imobiliário.        │
│                                                          │
│  Posso te ajudar com:                                    │
│   ▸ Comparar amortizar vs investir em renda fixa         │
│     (CDB, LCI, Tesouro) sem nomear instituições          │
│   ▸ Avaliar portabilidade do seu contrato                │
│   ▸ Simular cenários de aporte                           │
│                                                          │
│  Para análise de ações específicas, consulte um          │
│  assessor de investimentos certificado pela CVM.         │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Pergunta sobre futuro / especulação

```
Você
A Selic vai cair pra 10% até o fim do ano?

─────────────────────────────────────────────────

IA — Tenor

Não posso prever Selic futura. Posso te mostrar
o que o mercado projeta hoje (Boletim Focus do
Banco Central):

  • Selic projetada para fim de 2026: 13%
  • Selic projetada para 2027: 11%
  • Selic projetada para 2028: 10%

Fonte: Boletim Focus de 04/05/2026.

Essas projeções são estimativas, não garantias.
Eventos macroeconômicos podem mudar tudo rápido.

Quer que eu simule cenários do seu contrato em
função de diferentes níveis de Selic futura?
```

### Pergunta jurídica

```
Você
Posso parar de pagar a parcela?

─────────────────────────────────────────────────

IA — Tenor

Não posso dar conselho jurídico. Inadimplência
em financiamento imobiliário tem consequências
sérias (notificação, leilão extrajudicial, perda
do imóvel) que dependem do seu contrato e da
legislação vigente.

Se você está com dificuldade real de pagar:
• Procure o banco antes de atrasar — eles têm
  programas de renegociação.
• Considere conversar com um advogado especializado
  em direito imobiliário.
• Em casos extremos, a Defensoria Pública orienta
  mutuários em risco de perda do imóvel.

Posso te ajudar a entender como sua parcela se
comportaria em diferentes cenários de renda
(stress test).
```

### Decisões

- **Recusa é sempre construtiva.** Sugere alternativa dentro do escopo.
- **Recusa não é desculpa.** Tom firme, direto.
- **Sugere recurso externo apropriado** quando relevante (CVM, advogado, Defensoria).

---

## Tela 3.5 — Histórico de conversas

```
┌──────────────────────────────────────────────────────────┐
│  ←  Histórico de conversas                               │
│                                                          │
│  Você tem 12 conversas dos últimos 30 dias.              │
│                                                          │
│  ─── Hoje ───                                            │
│                                                          │
│  🕒 14:23  Vale a pena portar pro Caixa?                 │
│            [Reabrir]  [Apagar]                           │
│                                                          │
│  ─── Ontem ───                                           │
│                                                          │
│  🕒 19:47  Quando devo usar FGTS?                        │
│            [Reabrir]  [Apagar]                           │
│                                                          │
│  🕒 16:12  Compare meus 3 cenários                       │
│            [Reabrir]  [Apagar]                           │
│                                                          │
│  ─── Semana passada ───                                  │
│                                                          │
│  🕒 28/04  Quanto economizo amortizando R$ 80k?          │
│            [Reabrir]  [Apagar]                           │
│                                                          │
│  ...                                                     │
│                                                          │
│  ─────────────────────────────────────────               │
│                                                          │
│  ⓘ Conversas mais antigas que 30 dias são apagadas       │
│     automaticamente. (Plano Plus)                        │
│                                                          │
│  [ Apagar todas ]    [ Exportar histórico ]              │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Retenção visível.** Usuário sempre sabe quanto tempo as conversas ficam.
- **"Apagar todas"** é destrutivo, com confirmação dupla.
- **"Exportar histórico"** baixa em PDF ou JSON estruturado — direito de portabilidade da LGPD.

---

## Casos de borda

### Pergunta ambígua

```
Você
Vale a pena?

IA — Tenor

Vale a pena... o quê especificamente?

Posso te ajudar com algumas perguntas comuns:
 ▸ Vale amortizar R$ X agora?
 ▸ Vale portar pro [outro banco]?
 ▸ Vale usar FGTS desta vez?
 ▸ Vale aumentar aporte mensal pra R$ X?
```

### Pergunta com dado faltante

```
Você
Compare amortizar com investir em renda fixa.

IA — Tenor

Pra comparar com precisão, preciso saber:

 1. Qual valor você está considerando?
    [    ] R$
    
 2. Por quanto tempo ficaria investido?
    [   ] meses

 3. Você tem reserva de emergência preservada?
    ⦾ Sim   ⦾ Não   ⦾ Parcial

[Continuar com esses dados]
```

### Pergunta que requer dados não armazenados

```
Você
Considerando minha renda, posso amortizar R$ 10k/mês?

IA — Tenor

Você ainda não declarou sua renda no Tenor.
Esse dado é opcional — usado só pra avaliações
de comprometimento.

Quer informar agora?
[Informar renda] [Pular]

Se preferir, posso te dar a análise técnica sem
considerar renda: o impacto no contrato seria...
```

---

## Modo offline (privacidade extrema)

Usuário pode desativar IA na config:

```
┌──────────────────────────────────────────────────────────┐
│  IA — Tenor                                         │
│                                                          │
│  ⓘ Você desativou análise por IA.                        │
│                                                          │
│  Para usar este recurso, ative em                        │
│  Configurações → Privacidade.                            │
│                                                          │
│  Enquanto isso, você pode:                               │
│   ▸ Criar e simular cenários (sem IA)                    │
│   ▸ Usar stress tests predefinidos                       │
│   ▸ Ver auditoria do seu contrato                        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Diferenças por plano

| Funcionalidade | Básico | Plus | Avançado |
|---|---|---|---|
| Perguntas por mês | 10 | Ilimitado | Ilimitado |
| Memória de conversas | — | 30 dias | 90 dias |
| Citações com fonte | ✓ | ✓ | ✓ |
| "Como chegamos nisso?" | ✓ | ✓ | ✓ |
| Sugestões contextuais | ✓ | ✓ | ✓ |
| Modo offline (desativar IA) | ✓ | ✓ | ✓ |
| Export do histórico | ✓ | ✓ | ✓ |

---

## Métricas que importam

| Métrica | Meta |
|---|---|
| Taxa de uso da IA por usuário ativo | > 30% em 7 dias |
| Perguntas médias por sessão | 2-4 |
| Taxa de satisfação (👍/👎) por resposta | > 80% positiva |
| Taxa de "como chegamos nisso?" | > 15% (sinal saudável de auditoria) |
| Taxa de pergunta fora de escopo | < 10% |

---

## Relação com privacidade

Esta jornada tem o **maior risco de privacidade do produto**, então merece tratamento especial:

### O que é enviado ao LLM

- Saldo, taxas, prazo (números, sem identificação)
- Pergunta original do usuário (após redaction de PII se houver)
- Resultados de cálculos do motor determinístico
- Templates de prompt versionados (auditáveis internamente)

### O que NÃO é enviado

- Nome do usuário
- CPF (já não está armazenado)
- Conta, agência, número de contrato bancário
- E-mail
- Endereço IP
- Outros contratos do mesmo usuário

### Provedor

- Anthropic API com Zero Data Retention contratual
- Prompts não usados para treino
- Documentado em política pública

### Auditabilidade

- Toda interação fica em log por 30 dias (debug)
- Logs sem PII (já redacted antes do envio)
- Usuário pode ver "interações com IA" no Audit (Jornada 7)
- Usuário pode apagar histórico a qualquer momento

### Modo offline

Quem desativa IA em Privacidade:
- Nada é enviado externamente
- Chat fica desabilitado
- Restante do produto funciona normal (cenários, stress, dashboard, audit)
- Reativação restaura serviço imediatamente
