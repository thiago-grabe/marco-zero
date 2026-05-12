# Tenor — Jornada 5: Stress Tests

> **Objetivo**: responder honestamente a pergunta "e se as coisas derem errado (ou certo)?".
> **Princípio guia**: stress test não é alarme — é exercício mental que **prepara** o usuário para realidade incerta.

---

## Modelo mental do usuário

> "Quero saber se meu plano aguenta uma pancada antes de a pancada acontecer. E quero saber o que faço se sobrar dinheiro."

A maioria dos simuladores assume vida estável e juros constantes. Isso é fantasia. Stress test traz realidade pra dentro do produto: emprego pode acabar, renda pode aumentar, IPCA pode disparar, filho pode entrar na escola particular.

---

## Princípios duros

1. **Stress não é defeito do plano** — é validação. Um plano que sobrevive a stress é um plano sólido.
2. **3 níveis de resultado: ✓ ⚠ ✗** (cobre / desliza / quebra). Mais nuance que isso confunde.
3. **Recomendação é específica e acionável.** Sem "diversifique seus investimentos" genérico. Sempre "mude X para Y".
4. **Stress positivos importam tanto quanto negativos.** Aumento de renda e herança merecem o mesmo planejamento.
5. **Stress declarado vira modo declarado.** Se o usuário marca "perdi emprego", Coach automaticamente entra em modo apropriado.

---

## Catálogo de stress tests

### Stress negativos

| Stress | Pergunta que responde |
|---|---|
| **Perda de emprego (6m / 12m)** | Reserva resiste? Por quanto tempo? |
| **Aumento de juros (200bps)** | Se taxa virar 14,19%, parcela pula quanto? |
| **Inflação alta (IPCA 8%)** | Custo real da dívida muda? |
| **Despesa inesperada (R$ 30k / 50k)** | Atrasa quitação em quanto? |
| **Filho na escola particular** | Compromisso novo de R$ 4k/mês a partir de quando? |
| **Doença na família** | Custos médicos não cobertos por plano |
| **Divórcio** | Partilha de bens, recálculo do contrato |
| **Aposentadoria antecipada** | Renda cai 40% em 2032, plano sobrevive? |
| **Imóvel desvaloriza 20%** | Posso ainda portar? |

### Stress positivos

| Stress | Pergunta que responde |
|---|---|
| **Aumento de renda (10% / 25% / 50%)** | O que fazer com a folga? |
| **Bônus / PLR maior que esperado** | Aplicar tudo na hipoteca ou diversificar? |
| **Herança / venda de outro ativo** | Quitar tudo, parte, ou investir? |
| **Novo emprego com renda muito superior** | Replanejar quitação |

### Stress customizado

| Stress | Pergunta que responde |
|---|---|
| **Cenário livre** | "E se [eu definir condições específicas]?" |

---

## Tela 5.1 — Lista de stress tests

```
┌──────────────────────────────────────────────────────────┐
│  Apartamento Contagem ▾                                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Stress Tests                                            │
│                                                          │
│  Plano sendo testado:  "5k/mês + 60k/ano"                │
│  Cenário base:         Quitação 21/04/2029               │
│                                                          │
│  ─── Histórico recente ─────────────────────────         │
│                                                          │
│  06/05  Perda de emprego (6m)         ✓ Cobre            │
│         [Ver]                                            │
│                                                          │
│  04/05  Aumento de juros (+200bps)    ⚠ Desliza          │
│         [Ver]                                            │
│                                                          │
│  ─── Stress disponíveis ────────────────────────         │
│                                                          │
│  ▸ Perda de emprego                                      │
│  ▸ Aumento de juros                                      │
│  ▸ Inflação alta                                         │
│  ▸ Despesa inesperada                                    │
│  ▸ Filho na escola particular                            │
│  ▸ Aposentadoria antecipada                              │
│  ▸ Imóvel desvaloriza                                    │
│                                                          │
│  ─── Stress positivos ──────────────────────────         │
│                                                          │
│  ▸ Aumento de renda                                      │
│  ▸ Bônus extraordinário                                  │
│  ▸ Herança ou venda de ativo                             │
│                                                          │
│  ─── Customizado ───────────────────────────────         │
│                                                          │
│  ▸ Definir meu próprio cenário                           │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Histórico recente no topo.** Stress já rodados ficam visíveis pra revisão.
- **Resultado em ícone simples** (✓ ⚠ ✗). Cor reforça mas não substitui símbolo (acessibilidade).
- **Stress agrupados em 3 categorias.** Negativos, positivos, customizado.

---

## Tela 5.2 — Stress: Perda de emprego

```
┌──────────────────────────────────────────────────────────┐
│  ←  Stress: Perda de emprego                             │
│                                                          │
│  ─── Parâmetros ───────────────────────────────          │
│                                                          │
│  Duração da perda                                        │
│  ──●─────────  6 meses                                   │
│  1 mês    24 meses                                       │
│                                                          │
│  Reserva de emergência atual                             │
│  R$ [ 35.000 ]   ⓘ Atualizar valor                       │
│                                                          │
│  Despesas mensais essenciais (sem hipoteca)              │
│  R$ [ 8.500 ]                                            │
│                                                          │
│  Comportamento durante o desemprego:                     │
│  ⦿ Pausar amortizações extras, manter parcela            │
│  ⦾ Pausar tudo (negociar com banco — risco alto)         │
│                                                          │
│  ─── Resultado ────────────────────────────────          │
│                                                          │
│  ✓ Plano sobrevive 6 meses                               │
│                                                          │
│  Reserva cobre:                                          │
│   • 6 meses de despesas essenciais     R$ 51.000         │
│   • 6 meses de parcela cheia           R$ 39.469         │
│   • Total necessário                   R$ 90.469         │
│   • Reserva atual                      R$ 35.000         │
│   • Cobertura                          39%               │
│                                                          │
│  ⚠ Reserva insuficiente para 6 meses sem renda.          │
│    Faltam R$ 55.469.                                     │
│                                                          │
│  Cenário sem renda durante 6 meses:                      │
│   • Reserva esgota no mês 3 (agosto/2026)                │
│   • A partir do mês 4, sem como pagar parcela            │
│   • Risco de inadimplência alto                          │
│                                                          │
│  ─── Recomendação ─────────────────────────────          │
│                                                          │
│  Antes de manter aporte de R$ 5k/mês, reforçar           │
│  reserva de emergência:                                  │
│                                                          │
│  • Reserva mínima alvo:        R$ 90.000                 │
│  • Aporte sugerido:            R$ 5.000/mês              │
│  • Tempo para alcançar:        12 meses                  │
│                                                          │
│  Em paralelo, pode manter o cenário "5k/mês +            │
│  60k/ano" — só aporta no aniversário (abril) e           │
│  redireciona o mensal para reserva por 12 meses.         │
│                                                          │
│  Após 12 meses (com reserva ok), retomar plano           │
│  agressivo. Quitação adia ~1 ano (de 04/2029             │
│  para ~04/2030), mas plano fica robusto.                 │
│                                                          │
│  [ Salvar como cenário "Reforçar reserva" ]              │
│  [ Aceitar risco e manter plano atual ]                  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Parâmetros editáveis.** Duração, reserva, despesas — tudo customizável.
- **2 comportamentos de stress.** Pausar amortizações vs pausar tudo (caso extremo).
- **Resultado é honesto.** Mostra exatamente quando reserva esgota.
- **Recomendação sugere ajuste no plano**, não abandono. Construtivo.
- **2 ações finais**: salvar novo cenário ou aceitar risco. Decisão é do usuário.

---

## Tela 5.3 — Stress: Aumento de renda

```
┌──────────────────────────────────────────────────────────┐
│  ←  Stress: Aumento de renda                             │
│                                                          │
│  ─── Parâmetros ───────────────────────────────          │
│                                                          │
│  Renda atual declarada                                   │
│  R$ [ 30.000 ]                                           │
│                                                          │
│  Aumento esperado                                        │
│  ──●─────────  +27% (R$ 38.000)                          │
│  +5%      +100%                                          │
│                                                          │
│  Quando o aumento entra                                  │
│  [ Junho 2026 ▾ ]                                        │
│                                                          │
│  Permanência esperada do aumento                         │
│  ⦿ Permanente   ⦾ Temporário (quanto tempo? [   ] meses) │
│                                                          │
│  ─── 3 caminhos para a folga ──────────────────          │
│                                                          │
│  Você ganha R$ 8.000/mês adicionais. O que fazer?        │
│                                                          │
│  ┌──────────────────────┬──────────────────────┐         │
│  │ A — Acelerar         │ B — Diversificar     │         │
│  │   hipoteca           │                      │         │
│  ├──────────────────────┼──────────────────────┤         │
│  │ Aumentar aporte      │ Manter aporte de 5k  │         │
│  │ mensal de 5k → 8k    │ e investir 3k em CDI │         │
│  │                      │                      │         │
│  │ Quitação:            │ Quitação:            │         │
│  │ 21/04/2028           │ 21/04/2029 (mantém)  │         │
│  │                      │                      │         │
│  │ Economia em juros:   │ Patrimônio em 3 anos:│         │
│  │ +R$ 24k              │ +R$ 130k em CDI      │         │
│  │                      │                      │         │
│  │ Comprometimento:     │ Comprometimento:     │         │
│  │ 38% da renda nova    │ 30% da renda nova    │         │
│  │                      │                      │         │
│  └──────────────────────┴──────────────────────┘         │
│                                                          │
│  ┌──────────────────────────────────────────────┐        │
│  │ C — Reforçar reserva primeiro                │        │
│  ├──────────────────────────────────────────────┤        │
│  │ Reserva atual: R$ 35.000                     │        │
│  │ Reserva ideal: R$ 90.000 (6× parcela cheia)  │        │
│  │                                              │        │
│  │ Aplicar R$ 8k/mês em reserva por 7 meses     │        │
│  │ Em janeiro/2027: reserva confortável         │        │
│  │ Depois: voltar a B ou A                      │        │
│  │                                              │        │
│  │ Quitação: ~21/06/2029 (2 meses a mais)       │        │
│  └──────────────────────────────────────────────┘        │
│                                                          │
│  ─── Recomendação contextual ──────────────────          │
│                                                          │
│  Sua reserva ainda está abaixo do ideal (39% do          │
│  necessário pra cobrir 6 meses). Recomendamos:           │
│                                                          │
│  1. Curto prazo (até 2027): caminho C — reforçar         │
│     reserva. Custo: 2 meses extras na quitação.          │
│  2. Após reserva ok: caminho A ou B, conforme            │
│     apetite a risco.                                     │
│                                                          │
│  Caminho A é matematicamente superior se você tem        │
│  perfil conservador. Caminho B é matematicamente         │
│  similar com benefício de diversificação se a Selic      │
│  cair menos do que projetado.                            │
│                                                          │
│  [ Aplicar caminho A ]  [ Aplicar caminho B ]            │
│  [ Aplicar caminho C ]  [ Decidir depois ]               │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **3 caminhos visualizados lado a lado.** Sem assumir que mais aporte é sempre a resposta.
- **Caminho C (reserva) tem peso visual igual.** Educar que reserva é objetivo legítimo.
- **Recomendação considera estado atual da reserva.** Personalizada.

---

## Tela 5.4 — Stress: Inflação alta

```
┌──────────────────────────────────────────────────────────┐
│  ←  Stress: Inflação alta                                │
│                                                          │
│  ─── Parâmetros ───────────────────────────────          │
│                                                          │
│  IPCA esperado nos próximos 12 meses                     │
│  ──────●───  8% (vs 4,89% projetado pelo Focus)          │
│  3%       12%                                            │
│                                                          │
│  Sua taxa nominal: 12,19% a.a.                           │
│  Sua taxa real (com IPCA 4,89%): 6,96%                   │
│  Sua taxa real (com IPCA 8%): 3,88%                      │
│                                                          │
│  ─── Resultado ────────────────────────────────          │
│                                                          │
│  ⓘ Sua taxa é fixa nominal. IPCA alta na verdade         │
│    melhora seu custo real da dívida.                     │
│                                                          │
│  Em IPCA 8%:                                             │
│   • Seu valor de parcela em poder de compra cai          │
│   • Dívida nominal vira menos significativa              │
│   • Capacidade de aporte real precisa crescer            │
│     pelo menos no ritmo da inflação                      │
│                                                          │
│  ─── Risco indireto ───────────────────────────          │
│                                                          │
│  ⚠ IPCA alta tipicamente vem com Selic alta              │
│    (que você não vê direto, mas afeta:)                  │
│                                                          │
│  • Seus aportes em CDI rendem mais (bom)                 │
│  • Crédito fica mais caro (impacta refinanciamento)      │
│  • Custo de vida sobe (despesas essenciais ↑)            │
│                                                          │
│  Se sua renda não acompanha IPCA, comprometimento        │
│  real aumenta:                                           │
│                                                          │
│   Renda atual: R$ 30.000                                 │
│   Renda ajustada por IPCA 8%: R$ 32.400 (esperado)       │
│   Se ficar em R$ 30.000: perda real de 7,4% do poder     │
│   de compra                                              │
│                                                          │
│  ─── Recomendação ─────────────────────────────          │
│                                                          │
│  Em cenário de IPCA alta:                                │
│   ✓ Manter taxa fixa do contrato é vantagem              │
│   ⚠ Garantir que renda acompanhe inflação                │
│   ⚠ Aportes em CDI/Selic protegem poder de compra        │
│     melhor que continuar amortizando agressivamente      │
│                                                          │
│  Considere caminho B do stress "Aumento de renda":       │
│  parte em hipoteca, parte em CDI. Diversifica.           │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Mostra que inflação alta com taxa fixa NÃO é sempre ruim.** Educação econômica.
- **Apresenta riscos indiretos** que o usuário pode não ter pensado.
- **Conexão entre stress tests.** Sugere caminho B do stress de aumento de renda — produtos pensam juntos.

---

## Tela 5.5 — Stress: Filho na escola particular

```
┌──────────────────────────────────────────────────────────┐
│  ←  Stress: Filho na escola particular                   │
│                                                          │
│  ─── Parâmetros ───────────────────────────────          │
│                                                          │
│  Mensalidade da escola                                   │
│  R$ [ 4.000 ]                                            │
│                                                          │
│  Quando começa                                           │
│  [ Fevereiro 2027 ▾ ]                                    │
│                                                          │
│  Por quantos anos                                        │
│  ──────●───  12 anos (até filho ter 18)                  │
│  1         18                                            │
│                                                          │
│  Reajuste anual estimado                                 │
│  ──●─────────  IPCA + 2% a.a.                            │
│  IPCA      IPCA + 6%                                     │
│                                                          │
│  ─── Impacto no plano ──────────────────────────         │
│                                                          │
│  Compromisso novo: R$ 4.000/mês                          │
│  Comprometimento total atual: 38% da renda               │
│  Com escola: 51%                                         │
│                                                          │
│  ⚠ Acima do limite saudável (35%).                       │
│                                                          │
│  ─── Cenário A: manter plano + escola ─────────          │
│                                                          │
│  Você precisa de R$ 4.000/mês adicionais a partir        │
│  de fev/2027. Se vier de aumento de renda, OK.           │
│  Se não, alguma coisa cede:                              │
│                                                          │
│  • Reduzir aporte mensal de 5k → 1k:                     │
│    Quitação adia para ~21/04/2031 (2 anos a mais)        │
│                                                          │
│  • Pular aporte anual de 60k:                            │
│    Quitação adia para ~21/04/2030 (1 ano a mais)         │
│                                                          │
│  • Combinação:                                           │
│    Reduzir mensal pra 3k + manter anual                  │
│    Quitação adia para ~21/01/2030 (9 meses a mais)       │
│                                                          │
│  ─── Cenário B: pausar aporte extra durante escola ──    │
│                                                          │
│  De 02/2027 a 12/2038: só parcela base (R$ 6.578)        │
│  De 01/2039 em diante: retomar aporte normal             │
│                                                          │
│  Quitação adia para ~03/2034 (5 anos a mais)             │
│                                                          │
│  ─── Recomendação ─────────────────────────────          │
│                                                          │
│  Filho na escola particular é compromisso de longo       │
│  prazo. Provavelmente justifica desacelerar a hipoteca   │
│  durante o período escolar.                              │
│                                                          │
│  Combinação balanceada: reduzir mensal pra 3k + manter   │
│  anual de 60k.                                           │
│                                                          │
│  [ Salvar como cenário "Família" ]  [ Decidir depois ]   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Reajuste anual incluído.** Escolas reajustam acima de inflação.
- **3 cenários de adaptação.** Reduzir mensal, pular anual, combinar.
- **Recomendação prática.** Combinação balanceada como ponto de partida.

---

## Tela 5.6 — Stress customizado

```
┌──────────────────────────────────────────────────────────┐
│  ←  Stress customizado                                   │
│                                                          │
│  Defina condições do cenário:                            │
│                                                          │
│  ─── Mudanças na renda ──────────────────────            │
│                                                          │
│  [+] Adicionar evento de renda                           │
│                                                          │
│  ─ Novo emprego em mar/2027: +R$ 12k/mês  [editar] [×]   │
│  ─ Aposentadoria em 2035: -40% da renda    [editar] [×]  │
│                                                          │
│  ─── Novas despesas ────────────────────────             │
│                                                          │
│  [+] Adicionar evento de despesa                         │
│                                                          │
│  ─ Carro em jan/2027: -R$ 2.500/mês × 36m  [editar] [×]  │
│  ─ Faculdade em 2030: -R$ 5.000/mês × 4a   [editar] [×]  │
│                                                          │
│  ─── Mudanças em parâmetros ─────────────────            │
│                                                          │
│  [+] Adicionar mudança                                   │
│                                                          │
│  ─ IPCA 6% a.a. nos próximos 5 anos        [editar] [×]  │
│                                                          │
│  ─── Resultado projetado ────────────────────            │
│                                                          │
│  Quitação:               21/04/2031 (vs 21/04/2029)      │
│  Atraso:                 24 meses                        │
│  Pico de comprometimento: 58% (em 2030)                  │
│  Risco:                  ⚠ Alto                          │
│                                                          │
│  Janelas de stress:                                      │
│   • 2027 — comprometimento de 48% (carro+escola)         │
│   • 2030 — pico de 58% (faculdade entra)                 │
│   • 2035 — aposentadoria reduz capacidade pra 35%        │
│                                                          │
│  [ Salvar como cenário ]  [ Visualizar timeline ]        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Builder de cenário com eventos.** Cada evento tem tipo, data, valor, duração.
- **Múltiplos eventos compostos.** Realidade tem várias coisas acontecendo.
- **Timeline visual** mostra picos de stress ao longo do tempo.

---

## Tela 5.7 — Reservas e parâmetros declarados

Esta tela aparece automaticamente quando o usuário tenta rodar stress test pela primeira vez:

```
┌──────────────────────────────────────────────────────────┐
│  ←  Configurar parâmetros para stress tests              │
│                                                          │
│  Pra rodar stress tests com precisão, precisamos de      │
│  alguns dados. Tudo opcional, mas quanto mais completo,  │
│  melhor a análise.                                       │
│                                                          │
│  ─── Reserva de emergência ────────────────────          │
│                                                          │
│  Quanto você tem disponível para emergências?            │
│  R$ [ 35.000 ]                                           │
│                                                          │
│  ⓘ Liquidez imediata (poupança, CDB liquidez D+1,        │
│    Tesouro Selic). Não conta investimentos travados.     │
│                                                          │
│  ─── Renda mensal líquida ─────────────────────          │
│                                                          │
│  Renda atual aproximada                                  │
│  R$ [ 30.000 ]                                           │
│                                                          │
│  ─── Despesas essenciais ──────────────────────          │
│                                                          │
│  Despesas que você não pode evitar                       │
│  (excluindo a parcela do imóvel)                         │
│  R$ [ 8.500 ]                                            │
│                                                          │
│  ⓘ Conta, comida, transporte, plano de saúde, escola     │
│                                                          │
│  ─── Atualização ──────────────────────────────          │
│                                                          │
│  Recomendamos revisar esses valores a cada 6 meses.      │
│  Tenor vai te lembrar.                              │
│                                                          │
│  [ Salvar e rodar stress ]                               │
│                                                          │
│  ─── Privacidade ──────────────────────────────          │
│                                                          │
│  🔒 Esses dados ficam só no seu cofre. Não são           │
│  enviados a terceiros. Servem apenas para cálculos       │
│  de stress dentro do seu plano.                          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Pede só o necessário.** 3 valores: reserva, renda, despesas essenciais.
- **Tudo opcional**, mas explica que análise fica mais precisa com cada campo.
- **Lembra de atualizar.** A cada 6 meses, Coach manda lembrete.

---

## Diferenças por plano

| Funcionalidade | Básico | Plus | Avançado |
|---|---|---|---|
| Stress tests por mês | 1 simples | Todos predefinidos | Todos + customizado |
| Perda de emprego | ✓ | ✓ | ✓ |
| Aumento de juros | — | ✓ | ✓ |
| Inflação alta | — | ✓ | ✓ |
| Despesa inesperada | — | ✓ | ✓ |
| Filho na escola | — | ✓ | ✓ |
| Aposentadoria | — | ✓ | ✓ |
| Stress positivos (renda, herança) | — | ✓ | ✓ |
| Stress customizado | — | — | ✓ |
| Combinação de múltiplos stress | — | — | ✓ |

---

## Métricas que importam

| Métrica | Meta |
|---|---|
| Usuários que rodam pelo menos 1 stress | > 50% em 30 dias |
| Stress por usuário ativo (Plus+) | > 3 em 90 dias |
| Taxa de "salvar como cenário" pós-stress | > 30% |
| Taxa de revisão de parâmetros declarados (semestral) | > 60% |
| Taxa de descoberta de cenário "quebra" | importante medir — produto educou usuário |

---

## Relação com privacidade

- **Parâmetros declarados (renda, reserva, despesas) são dados sensíveis adicionais.** Tratamento idêntico ao contrato: criptografia em repouso, RLS, sem envio externo.
- **Stress tests são determinísticos.** Cálculo no servidor sem IA.
- **IA pode ser usada para explicar resultado** (Jornada 3), mas nunca recebe o valor declarado de renda — recebe apenas razões agregadas (ex: "comprometimento subiu de 38% para 51%"), nunca os absolutos.
- **Resultado de stress é privado por padrão.** Mesmo no plano Família, parâmetros pessoais (renda) só aparecem para o titular que declarou — co-titular vê impacto agregado, não os números brutos, a menos que titular libere.
