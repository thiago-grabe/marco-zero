# Tenor — Motor de Cálculo & JSON Canônico

> Documento de design — versão 1
> Data: 06/05/2026
> Status: em discussão
> Depende de: `schema_01.md` (contrato de persistência)
> Alimenta: `parser_01.md` (contrato de extração)
> Mesma pasta: `technical/`

---

## Por que o motor existe separado da LLM

A LLM jamais calcula. Ela **chama funções** e **interpreta resultados**.

```
Usuário: "Quanto economizo amortizando R$ 30k?"
           │
           ▼
    [Camada de Tools]
    simular_amortizacao(saldo=429629, taxa=0.009631, valor=30000, modo='prazo')
           │
           ▼ resultado estruturado
    {
      saldo_novo: 399629,
      parcelas_eliminadas: 20,
      juros_economizados_nominal: 95400,
      juros_economizados_vp: 62300,
      nova_data_quitacao: "2041-05-21"
    }
           │
           ▼
    LLM monta a resposta em linguagem natural com esses números
```

Isso elimina alucinação matemática, garante auditabilidade ("como chegamos aqui?" mostra o input e output da função), e permite testes unitários independentes da IA.

---

## 1. Os três modos de cálculo

### 1.1 SAC — Sistema de Amortização Constante

Usado pela maioria dos bancos privados (Itaú, Bradesco, Santander) na modalidade Carteira Hipotecária.

**Matemática:**

```
amortizacao_i  = saldo_atual / prazo_remanescente   [constante se sem amort extra]
juros_i        = saldo_atual × taxa_mensal
seguros_i      = MIP_i + DFI_i                      [varia com saldo]
parcela_i      = amortizacao_i + juros_i + seguros_i [decrescente]
saldo_{i+1}    = saldo_i - amortizacao_i
```

**Amortização extraordinária — modalidade "redução de prazo":**

```
saldo_novo     = saldo_atual - valor_amort + juros_pro_rata + tr
amortizacao    = MANTIDA (igual à do plano atual)
prazo_novo     = floor(saldo_novo / amortizacao)
delta_parcelas = prazo_atual - prazo_novo
```

Resultado esperado: prazo cai, parcela cai marginalmente (menos juros, mesma amortização).

**Amortização extraordinária — modalidade "redução de parcela":**

```
saldo_novo         = saldo_atual - valor_amort + juros_pro_rata + tr
amortizacao_nova   = saldo_novo / prazo_remanescente   [diminui]
juros_novos        = saldo_novo × taxa_mensal           [diminui]
parcela_nova       = amortizacao_nova + juros_novos + seguros  [cai significativamente]
prazo              = MANTIDO
```

---

### 1.2 PRICE — Sistema Francês de Amortização

Usado pela Caixa em algumas modalidades (Minha Casa Minha Vida, parcela menor no início) e por bancos em financiamentos de veículos e crédito pessoal.

**Matemática:**

```
PMT     = PV × [taxa × (1+taxa)^n] / [(1+taxa)^n - 1]   [constante]
juros_i = saldo_i × taxa_mensal
amort_i = PMT - juros_i                                   [cresce ao longo do tempo]
saldo_{i+1} = saldo_i - amort_i
```

**Propriedades importantes:**
- Parcela total é constante (sem seguros variáveis)
- Amortização é crescente — nas primeiras parcelas, quase tudo é juros
- Para o mesmo PV, prazo e taxa, o PRICE tem parcela menor que o SAC no início e maior no fim
- Amortização extra no PRICE: recalcula PMT com novo saldo e prazo remanescente

**Amortização extraordinária PRICE:**

```
saldo_novo = saldo_atual - valor_amort
PMT_nova   = saldo_novo × [taxa × (1+taxa)^n] / [(1+taxa)^n - 1]
// Redução de prazo: manter PMT, recalcular n
// Redução de parcela: manter n, recalcular PMT
```

---

### 1.3 Modo Itaú — comportamento banco-específico

Descoberto empiricamente no contrato de referência (Itaú). Quando o usuário escolhe "redução de prazo" no app do banco, o banco não aplica o SAC padrão.

**O que deveria acontecer (SAC redução de prazo):**

```
saldo_novo     = 435.977,65  (após R$ 75k)
amortizacao    = 1.514,32    [mantida]
juros_novos    = 435.977 × 0,9631% = 4.199,07
parcela_nova   ≈ R$ 5.713    (cai ~R$ 730)
prazo_novo     = 338 - 50 = 288
```

**O que o Itaú faz de fato:**

```
saldo_novo     = 435.977,65
juros_novos    = 435.977 × 0,9631% = 4.199,07
// Banco mantém parcela ≈ constante (cai apenas R$ 11)
amortizacao_nova = parcela_anterior - juros_novos - seguros = 2.234
prazo_novo     = ceil(435.977 / 2.234) = 195 parcelas
```

O banco usa a queda dos juros para aumentar a amortização mensal em vez de reduzir a parcela. A parcela mal muda; o prazo despenca.

**Por que isso existe**: é financeiramente melhor para o mutuário disciplinado (mais juros economizados), mas a nomenclatura do banco ("reduzir prazo" vs "reduzir parcela") não descreve esse comportamento.

**Identificação do modo**: o motor identifica o modo híbrido quando, após importar um DDC pós-amortização, a amortização mensal da próxima parcela é significativamente maior do que a anterior, enquanto o valor total da parcela caiu menos de 5%.

```
if (
  nova_amortizacao > amortizacao_anterior * 1.2  AND
  abs(nova_parcela - parcela_anterior) / parcela_anterior < 0.05
) → modo = 'itau'
```

**O motor precisa registrar e replicar esse comportamento.** Quando o usuário do Itaú simula amortização, o motor usa o modo híbrido para que a projeção bata com o que o banco vai gerar.

---

## 2. Catálogo de funções (Tools)

### Separação de responsabilidades

As Tools se dividem em dois grupos que nunca se misturam:

| Grupo | Responsabilidade | Acessa DB? | Exemplos |
|---|---|---|---|
| **Data** | Lê estado do sistema e retorna contexto | Sim | `get_contract_state`, `get_market_rates` |
| **Compute** | Matemática pura dado um contexto | Não | `simulate_amortization`, `run_stress` |

A LLM sempre começa por uma Tool de Data para montar o contexto, depois chama Tools de Compute. Tools de Compute são testáveis sem banco.

---

### Tipos compartilhados

```
// Contexto completo do contrato — base de todas as Tools de Compute
ContractState {
  contract_id:               string
  banco_code:                string      // 'itau', 'caixa', ...
  banco_display:             string      // "Itaú Unibanco"
  modalidade_code:           string      // 'carteira_hipotecaria', ...
  index_rate_code:           string      // 'TR', 'IPCA', 'PREFIXADO'
  amortization_system:       'SAC' | 'PRICE'
  calculation_mode:          'SAC' | 'PRICE' | 'itau'  // detectado pelo motor
  taxa_mensal:               number
  taxa_anual_efetiva:        number
  saldo_devedor:             number      // calculado: último DDC + operações
  valor_original:            number | null
  data_inicio:               date | null
  amortizacao_mensal:        number      // componente de amortização da próxima parcela
  juros_proxima:             number      // componente de juros da próxima parcela
  mip_mensal:                number
  dfi_mensal:                number
  seguros_mensal:            number      // mip + dfi
  parcela_total:             number      // total da próxima parcela
  data_proxima_parcela:      date
  prazo_remanescente:        number      // calculado
  data_quitacao:             date        // calculado
  ultima_ddc_data:           date
  ultima_ddc_versao:         number
  numero_amortizacoes_extra: number      // quantas amort extraordinárias já fez
  total_amortizado_extra:    number      // soma de todas as amort extraordinárias
  scenario_em_execucao_id:   string | null  // cenário com status 'em_execucao'
}

// Parâmetros de um cenário — usados em project_scenario e compare_scenarios
ScenarioParams {
  aporte_mensal_extra:  number       // além da parcela normal
  aporte_anual_extra:   number
  mes_aporte_anual:     1..12 | null // null = sem aporte anual
  data_inicio_aportes:  date | null  // null = imediatamente
  fgts_eventos: FgtsEvento[]        // zero ou mais janelas FGTS ao longo do prazo
}

FgtsEvento {
  data_prevista:  date
  valor_estimado: number
}

// Retorno de projeção de cenário
ScenarioProjection {
  data_quitacao:               date
  prazo_meses:                 number
  parcelas_eliminadas:         number    // vs. plano sem extras
  total_juros_pagos:           number
  total_juros_economizados:    number    // vs. plano sem extras
  total_extras_investidos:     number
  comprometimento_mensal_max:  number    // pico mensal (parcela + extra + fgts/12)
  schedule:                    YearSummary[]
}

YearSummary {
  ano:                number
  parcelas:           [number, number]  // range [inicio, fim]
  saldo_inicio:       number
  saldo_fim:          number
  amort_regular:      number
  amort_extra_mensal: number
  amort_extra_anual:  number
  fgts_aplicado:      number
  juros_pagos:        number
}

// Enum de tipos de stress
StressType =
  | 'perda_emprego'
  | 'aumento_juros'
  | 'inflacao_alta'
  | 'despesa_inesperada'
  | 'filho_escola'
  | 'doenca_familia'
  | 'divorcio'
  | 'aposentadoria_antecipada'
  | 'desvalorizacao_imovel'
  | 'aumento_renda'
  | 'bonus_extraordinario'
  | 'heranca'
  | 'customizado'
```

---

### Tools de Data (leem banco/estado)

#### D1 — `get_contract_state`

```
get_contract_state(contract_id: string) → ContractState
```

Constrói o `ContractState` a partir do último DDC + operações declaradas após ele. É a primeira Tool que a LLM deve chamar em qualquer conversa sobre o contrato.

---

#### D2 — `get_market_rates`

```
get_market_rates() → MarketRates

MarketRates {
  selic_aa:        number          // Selic meta atual
  cdi_aa:          number          // CDI diário × 252
  ipca_12m:        number          // IPCA acumulado 12m
  ipca_focus:      number          // Expectativa Focus próximos 12m
  data_referencia: date
  bancos: BankRate[]
}

BankRate {
  banco_code:       string
  banco_display:    string
  taxa_sbpe_aa:     number | null
  taxa_pro_cotista_aa: number | null
  data_coleta:      date
}
```

Lê de tabela interna atualizada por job periódico (não em tempo real). Usada por `compare_invest_vs_amortize` e `evaluate_portability_multi`. Também alimenta alertas do Coach quando Selic muda.

---

#### D3 — `get_fgts_status`

```
get_fgts_status(contract_id: string) → FgtsStatus

FgtsStatus {
  janela_aberta:          boolean
  data_ultima_utilizacao: date | null
  data_proxima_janela:    date | null   // null se nunca usou FGTS (elegível imediato)
  dias_para_janela:       number | null // negativo se já passou
  saldo_estimado:         number | null // declarado pelo usuário em user_profiles
  elegivel:               boolean
  motivos_inelegibilidade: string[]     // ex: ["janela ainda não abriu", "imóvel não residencial"]
}
```

---

#### D4 — `list_operations_history`

```
list_operations_history(
  contract_id: string,
  limit?:      number,       // default 20
  after_date?: date
) → OperationEvent[]

OperationEvent {
  id:           string
  tipo:         string       // 'amortizacao_prazo', 'amortizacao_parcela', 'fgts', ...
  data:         date
  valor_principal:       number
  juros_pro_rata:        number | null
  atualizacao_monetaria: number | null
  valor_total:           number
  modalidade:            string | null
  fonte:                 string         // 'recurso_proprio', 'fgts', 'ambos'
  origem:                'usuario' | 'ddc'  // declarado vs. importado do DDC
}
```

Usada no Audit ("o que aconteceu?") e no Chat quando usuário pergunta sobre o histórico.

---

#### D5 — `list_active_scenarios`

```
list_active_scenarios(contract_id: string) → ScenarioSummary[]

ScenarioSummary {
  id:      string
  nome:    string
  status:  'planejado' | 'em_execucao' | 'concluido' | 'abandonado'
  params:  ScenarioParams
  criado:  date
  editado: date
}
```

---

#### D6 — `get_scenario_by_id`

```
get_scenario_by_id(scenario_id: string) → ScenarioSummary
```

Para quando o usuário referencia um cenário pelo nome no chat ("mostre o cenário 5k/mês") ou o Coach referencia o aniversário de um cenário.

---

#### D7 — `list_coach_alerts`

```
list_coach_alerts(
  contract_id: string,
  status?:     'ativo' | 'lido' | 'snoozed'   // default 'ativo'
) → CoachAlert[]

CoachAlert {
  id:         string
  tipo:       string
  titulo:     string
  corpo:      string
  prioridade: 1 | 2 | 3
  status:     string
  metadados:  object
  criado:     date
}
```

Permite à LLM ter contexto dos alertas ativos ao entrar numa conversa ("vejo que você tem um alerta de FGTS aberto — quer simular o impacto?").

---

### Tools de Compute (funções puras)

#### C1 — `compute_installment`

```
compute_installment(
  saldo:             number,
  taxa_mensal:       number,
  calculation_mode:  'SAC' | 'PRICE' | 'itau',
  prazo:             number,    // obrigatório para PRICE e itau
  amortizacao_atual: number,    // obrigatório para itau (parcela mantida ≈ constante)
  mip:               number,    // separado (do schema)
  dfi:               number
) → InstallmentBreakdown

InstallmentBreakdown {
  amortizacao: number
  juros:       number
  mip:         number
  dfi:         number
  seguros:     number    // mip + dfi
  total:       number
}
```

---

#### C2 — `compute_pro_rata`

```
compute_pro_rata(
  saldo:                   number,
  taxa_mensal:             number,
  data_ultimo_vencimento:  date,
  data_operacao:           date
) → ProRataResult

ProRataResult {
  dias_decorridos:      number
  juros_pro_rata:       number
  atualizacao_tr:       number    // estimativa TR proporcional
  total_acrescimo:      number    // pro_rata + tr
}
```

Standalone porque usuários frequentemente perguntam "quanto pago a mais se esperar 5 dias?". Também usada internamente por `simulate_amortization`.

---

#### C3 — `simulate_amortization`

```
simulate_amortization(
  state:      ContractState,
  valor:      number,
  modalidade: 'prazo' | 'parcela',
  data:       date
) → AmortizationResult

AmortizationResult {
  // desembolso real
  saldo_novo:               number
  juros_pro_rata:           number
  atualizacao_monetaria:    number
  total_desembolso:         number    // valor + pro_rata + tr

  // impacto no contrato (depende da modalidade)
  prazo_novo:               number
  parcelas_eliminadas:      number    // > 0 se 'prazo'; 0 se 'parcela'
  nova_amortizacao_mensal:  number
  nova_parcela_proxima:     number
  prazo_inalterado:         boolean   // true se 'parcela'

  // economia gerada
  seguros_economizados:     number    // MIP+DFI sobre parcelas eliminadas
  juros_economizados_nominal: number
  juros_economizados_vp:      number  // descontado à própria taxa do contrato
  retorno_efetivo_aa:         number  // TIR da operação de amortização
  data_nova_quitacao:         date
}
```

---

#### C4 — `project_scenario`

```
project_scenario(
  state:  ContractState,
  params: ScenarioParams
) → ScenarioProjection
```

---

#### C5 — `compare_scenarios`

```
compare_scenarios(
  state:         ContractState,
  scenarios:     ScenarioParams[],    // até 4; ordem define análise marginal
  scenario_ids?: string[]             // alternativa: referir por ID de cenário salvo
) → ScenarioComparison

ScenarioComparison {
  base:     ScenarioProjection    // plano atual sem extras
  cenarios: ScenarioProjection[]
  marginal: MarginalAnalysis[]    // cenário[i] vs cenário[i-1]
}

MarginalAnalysis {
  extra_investido:      number
  juros_economizados:   number
  tempo_cortado_meses:  number
  retorno_marginal:     number    // juros_econ / extra_inv
  recomendacao:         'sim' | 'depende' | 'nao'
  motivo:               string
}
```

---

#### C6 — `compare_invest_vs_amortize`

```
compare_invest_vs_amortize(
  state:      ContractState,
  valor:      number,
  horizonte:  number,      // meses (default = state.prazo_remanescente)
  rates:      MarketRates, // vem de get_market_rates()
  perfil:     'conservador' | 'moderado' | 'agressivo'
) → InvestComparison

InvestComparison {
  amortizar: {
    retorno_efetivo_aa:   number
    juros_economizados:   number
    seguros_economizados: number
    total_economizado:    number
    equivalente_bruto_aa: number    // para bater no mercado bruto com IR
    risco:                'zero'
    liquidez:             'zero'    // dinheiro vai pro banco, não tem volta fácil
  }
  alternativas: InvestOption[]
  veredicto:    'amortizar' | 'empate' | 'investir'
  motivo:       string
}

InvestOption {
  nome:                string
  tipo:                'renda_fixa' | 'renda_variavel'
  retorno_bruto_aa:    number
  ir_estimado:         number        // alíquota IR conforme prazo
  retorno_liquido_aa:  number
  retorno_vp:          number        // valor presente comparável ao de amortizar
  risco:               'zero' | 'baixo' | 'medio' | 'alto'
  liquidez:            'diaria' | 'no_vencimento' | 'variavel'
  observacao:          string | null
  supera_amortizacao:  boolean
}
```

**Nota**: a Tool recebe `rates` como parâmetro (vindo de `get_market_rates`) para manter a separação Data/Compute. A LLM chama as duas em sequência.

---

#### C7 — `evaluate_portability_multi`

Substituiu o antigo `evaluate_portability` único. Compara N bancos de uma vez, que é o que a UI de portabilidade mostra.

```
evaluate_portability_multi(
  state:           ContractState,
  rates:           MarketRates,    // vem de get_market_rates()
  custo_cartorio:  number,         // estimativa padrão R$ 3.000–5.000
  custo_avaliacao: number          // estimativa padrão R$ 800–1.500
) → PortabilityComparison

PortabilityComparison {
  elegivel:            boolean
  motivos_inelegibilidade: string[]
  opcoes:              PortabilityOption[]
  melhor_opcao:        PortabilityOption | null
  contraproposta_estimada: Contraproposta
}

PortabilityOption {
  banco_code:             string
  banco_display:          string
  nova_taxa_aa:           number
  nova_parcela:           number
  delta_parcela:          number
  economia_total_nominal: number
  economia_total_vp:      number
  custo_total_operacao:   number    // cartório + avaliação
  payback_meses:          number
  viavel:                 boolean   // payback < prazo_remanescente
  observacoes:            string[]
}

Contraproposta {
  // Banco original tem 5 dias úteis para contraproposta (Lei 9.514)
  cenario: PortabilityOption    // estimativa se banco original igualar melhor proposta
  provavel: boolean             // heurística: se delta_taxa > 100bps, banco costuma contrapor
}
```

---

#### C8 — `run_stress`

```
run_stress(
  state:     ContractState,
  scenario:  ScenarioParams,    // plano sendo testado
  stress:    StressInput,
  reserva_emergencia?: number   // override; default = user_profiles.reserva_emergencia_declarada
) → StressResult

StressInput {
  tipo: StressType

  // 'perda_emprego'
  duracao_meses?:         number    // default 6
  reducao_renda_pct?:     number    // 0–1; default 1.0 (renda zerada)

  // 'aumento_juros' (só para contratos com taxa_referencial volátil: TR, IPCA)
  delta_bps?:             number    // ex: 200

  // 'inflacao_alta'
  ipca_cenario?:          number    // ex: 0.08 (8% a.a.)

  // 'despesa_inesperada'
  valor?:                 number

  // 'filho_escola'
  custo_mensal?:          number
  inicio_data?:           date

  // 'doenca_familia'
  custo_total?:           number
  duracao_meses?:         number

  // 'divorcio'
  particao_pct?:          number    // ex: 0.5

  // 'aposentadoria_antecipada'
  reducao_renda_pct?:     number
  data_aposentadoria?:    date

  // 'desvalorizacao_imovel'
  desvalorizacao_pct?:    number    // 0–1

  // 'aumento_renda'
  aumento_pct?:           number
  data_vigencia?:         date

  // 'bonus_extraordinario'
  valor?:                 number

  // 'heranca'
  valor?:                 number
  data_prevista?:         date

  // 'customizado'
  adjustments?: {
    delta_renda_mensal?:   number
    delta_despesa_mensal?: number
    aporte_extra_pontual?: { data: date; valor: number }[]
    delta_taxa?:           number
  }
}

StressResult {
  resultado:    'cobre' | 'desliza' | 'quebra'

  impacto: {
    meses_reserva_cobertos:   number | null   // null se reserva não declarada
    delta_quitacao_meses:     number          // positivo = atrasa; negativo = adianta
    delta_juros_total:        number
    delta_comprometimento_mensal: number
  }

  recomendacao:     string
  acoes_sugeridas:  string[]

  // apenas para stress positivos (aumento_renda, bonus, heranca)
  opcoes_positivas?: {
    acelerar:         ScenarioProjection
    diversificar:     ScenarioProjection
    reforcar_reserva: ScenarioProjection
    comparacao:       MarginalAnalysis[]
  }
}
```

---

#### C9 — `check_eligibility`

```
check_eligibility(
  state:   ContractState,
  fgts:    FgtsStatus,      // vem de get_fgts_status()
  operacao: 'fgts' | 'portabilidade' | 'amortizacao_extraordinaria'
) → EligibilityResult

EligibilityResult {
  elegivel:   boolean
  motivos:    EligibilityCheck[]
}

EligibilityCheck {
  regra:      string     // ex: "Janela FGTS (24 meses)"
  status:     'ok' | 'falha' | 'aviso' | 'nao_verificavel'
  detalhe:    string     // ex: "Próxima janela: 12/03/2028"
}

// Regras verificadas por operação:
// 'fgts':
//   - janela ≥ 24 meses desde última utilização
//   - imóvel residencial (não verificável automaticamente — aviso)
//   - imóvel único financiado pelo SFH (não verificável — aviso)
//   - mínimo 3 anos de FGTS acumulado (não verificável — aviso)
//   - sem inadimplência em outro contrato SFH (não verificável — aviso)
//
// 'portabilidade':
//   - LTV < 80% (estimável: saldo / valor_original)
//   - contrato não em atraso (não verificável — aviso)
//   - prazo remanescente > 36 meses (verifica via state)
//
// 'amortizacao_extraordinaria':
//   - sem restrições legais; sempre elegível se contrato ativo
```

---

#### C10 — `reconcile_ddc`

```
reconcile_ddc(
  state:             ContractState,     // estado antes do novo DDC
  novo_snapshot_id:  string,            // ID do ddc_snapshot recém-inserido
  operacoes_periodo: OperationEvent[]   // vem de list_operations_history()
) → ReconciliationResult

ReconciliationResult {
  status:               'ok' | 'divergente'
  saldo_esperado:       number
  saldo_declarado:      number
  diff_absoluto:        number
  diff_percentual:      number
  operacoes_usadas:     string[]       // IDs das operações consideradas
  explicacoes_prováveis: string[]      // se divergente: TR acumulada, operação não declarada, erro de parser
  acao_sugerida:        string | null
}
```

---

### Resumo: 17 Tools

| # | Nome | Grupo | Propósito |
|---|---|---|---|
| D1 | `get_contract_state` | Data | Estado completo do contrato |
| D2 | `get_market_rates` | Data | Selic, CDI, IPCA, taxas de mercado |
| D3 | `get_fgts_status` | Data | Janela FGTS, elegibilidade, saldo estimado |
| D4 | `list_operations_history` | Data | Histórico de amortizações e eventos |
| D5 | `list_active_scenarios` | Data | Cenários salvos do usuário |
| D6 | `get_scenario_by_id` | Data | Cenário específico por ID |
| D7 | `list_coach_alerts` | Data | Alertas ativos do Coach |
| C1 | `compute_installment` | Compute | Decomposição de uma parcela |
| C2 | `compute_pro_rata` | Compute | Juros pró-rata entre datas |
| C3 | `simulate_amortization` | Compute | Impacto de amortizar X hoje |
| C4 | `project_scenario` | Compute | Projeção de cenário com aportes |
| C5 | `compare_scenarios` | Compute | Comparação de até 4 cenários |
| C6 | `compare_invest_vs_amortize` | Compute | Amortizar vs. investir com IR |
| C7 | `evaluate_portability_multi` | Compute | Portabilidade comparando N bancos |
| C8 | `run_stress` | Compute | Stress test positivo ou negativo |
| C9 | `check_eligibility` | Compute | Elegibilidade para FGTS/portabilidade |
| C10 | `reconcile_ddc` | Compute | Reconciliação saldo esperado vs. DDC |

---

## 3. Arquitetura: LLM + Tools

```
┌─────────────────────────────────────────────────────────┐
│                   Camada de IA (Chat)                   │
│                                                         │
│  Mensagem do usuário                                    │
│    │                                                    │
│    ▼                                                    │
│  LLM com system prompt:                                 │
│   "Você tem acesso às seguintes ferramentas de          │
│    cálculo. Use-as para obter números antes de          │
│    responder. Nunca calcule por conta própria."         │
│    │                                                    │
│    ├─── Tool call: get_contract_state(...)              │
│    ├─── Tool call: simulate_amortization(...)           │
│    ├─── Tool call: compare_invest_vs_amortize(...)      │
│    │                                                    │
│    ▼ recebe resultados estruturados                     │
│    │                                                    │
│    ▼                                                    │
│  LLM monta resposta com:                               │
│   - Resposta direta (1-2 frases)                       │
│   - Análise (cita os números retornados pelas tools)   │
│   - Caveats                                            │
│   - Botão "como chegamos aqui" → mostra tool inputs    │
│                                                        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Camada de Tools                        │
│                                                         │
│  ── Data (leem banco) ──────────────────────────────    │
│  get_contract_state()     get_market_rates()            │
│  get_fgts_status()        list_operations_history()     │
│  list_active_scenarios()  get_scenario_by_id()          │
│  list_coach_alerts()                                    │
│                                                         │
│  ── Compute (funções puras) ────────────────────────    │
│  compute_installment()    compute_pro_rata()            │
│  simulate_amortization()  project_scenario()            │
│  compare_scenarios()      compare_invest_vs_amortize()  │
│  evaluate_portability_multi()  run_stress()             │
│  check_eligibility()      reconcile_ddc()               │
│                                                         │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│          Motor SAC / PRICE / Itaú  (17 tools)           │
│          Compute tools: funções matemáticas puras        │
│          Data tools: leitores do banco de dados          │
└─────────────────────────────────────────────────────────┘
```

**O mesmo motor serve o Chat IA e a UI de Cenários.** Os sliders em tempo real do dashboard de cenários chamam `project_scenario()` diretamente, sem passar pela LLM. A LLM só entra quando o usuário abre o Chat e faz uma pergunta em linguagem natural.

---

## 4. Como o modo de cálculo é determinado

Quando um DDC é importado, o motor analisa o histórico de amortizações para identificar o padrão do banco:

```
detectar_modo(historico_operacoes, historico_parcelas):

  para cada amortização extraordinária no histórico:
    amort_antes = parcela imediatamente anterior à amortização
    amort_depois = parcela imediatamente posterior
    
    delta_parcela_pct = abs(amort_depois.total - amort_antes.total) / amort_antes.total
    delta_amort_pct   = abs(amort_depois.amortizacao - amort_antes.amortizacao) / amort_antes.amortizacao
    
    se delta_parcela_pct < 0.05 AND delta_amort_pct > 0.20:
      → modo_banco = 'itau'
    
    se delta_parcela_pct > 0.10:
      → modo_banco = 'SAC_reducao_parcela'
    
    se delta_parcela_pct < 0.10 AND delta_amort_pct < 0.10:
      → modo_banco = 'SAC_reducao_prazo_padrao'

  retorna modo mais frequente nas últimas 3 operações
```

Este modo é salvo em `contracts.modo_calculo_detectado` (campo a adicionar em `schema_01.md`). Pode ser sobrescrito manualmente pelo usuário se o banco mudar comportamento.

---

## 5. Escala: DDC installments

### O problema

420 parcelas por DDC (SAC com 35 anos de contrato — prazo máximo do SFH).
10.000 usuários. 6 DDCs/ano por usuário em média.

```
420 × 6 × 10.000 = 25,2 milhões de linhas/ano
Em 5 anos:          126 milhões de linhas
```

A 200 bytes/linha: **~25GB em 5 anos** só nessa tabela. Postgres aguenta. Mas o custo de storage e de queries que escaneiam muitas linhas cresce.

### Decisão de design: retenção em camadas

Não limitar número de DDCs — limitar quais têm parcelas completas armazenadas.

#### Camada quente: últimos N DDCs com parcelas completas

| Plano | DDCs com parcelas completas |
|---|---|
| Básico | 1 (apenas o mais recente) |
| Plus | 5 |
| Avançado | 12 (1 ano) |

Para DDCs acima do limite: as parcelas individuais são comprimidas em JSONB e movidas para `ddc_snapshots.parcelas_archive` (campo adicionado). A tabela `ddc_installments` só contém os DDCs da camada quente.

#### Camada fria: header preservado, parcelas arquivadas

O cabeçalho do DDC (`ddc_snapshots`) fica para sempre — é necessário para o audit trail ("o banco disse X na data Y"). Apenas as linhas de `ddc_installments` são removidas e substituídas por um arquivo comprimido:

```json
// ddc_snapshots.parcelas_archive (JSONB — só preenchido quando arquivado)
{
  "arquivado_em": "2027-06-01",
  "total_parcelas": 189,
  "resumo": {
    "primeira": { "numero": 5, "vencimento": "2026-05-21", "valor_total": 6578.27 },
    "ultima":   { "numero": 193, "vencimento": "2042-01-21", "valor_total": 2307.27 }
  },
  "comprimido_bytes": 12400
}
```

#### Política de arquivamento

```
a cada 24h, job de arquivamento:

  para cada contract:
    ddcs = ddc_snapshots ordenados por versao DESC
    limite = plano_usuario.ddc_limite_completo  (1, 5 ou 12)
    
    para ddcs[limite+1:]:
      comprimir parcelas em JSONB
      deletar linhas de ddc_installments
      marcar ddc_snapshot.parcelas_arquivadas = true
```

#### Impacto na escala

Após arquivamento, o volume real de `ddc_installments` por usuário ativo:

| Plano | Linhas ativas por usuário | Total (10k users) |
|---|---|---|
| Básico | 420 | 4,2M |
| Plus | 2.100 | 21M |
| Avançado | 5.040 | 50,4M |

Gerenciável. Com particionamento por `user_id` hash, queries nunca escaneiam mais de 1/N da tabela.

#### O que a reconciliação precisa

A reconciliação (`reconcile_ddc`) só precisa do DDC anterior imediato — que sempre está na camada quente. Não precisa de DDCs mais antigos.

O audit de "ver diff entre v2 e v3" (Jornada 7) funciona para DDCs quentes. Para DDCs arquivados, a UI mostra o resumo comprimido em vez das linhas individuais, com aviso: "Parcelas detalhadas foram arquivadas conforme política do plano Básico."

---

## 6. JSON Canônico — contrato de output do parser

Este é o formato exato que o parser (determinístico ou LLM fallback) deve produzir. É o contrato entre a camada de ingestão e o banco de dados.

```json
{
  "_meta": {
    "schema_version": "1.0",
    "parser_metodo": "deterministic",
    "parser_versao": "itau_v1.0",
    "parser_issues": [],
    "redaction_log": ["cpf"],
    "campos_ausentes": [],
    "campos_inferidos": []
  },

  "contrato": {
    "banco": "itau",
    "banco_display": "Itaú Unibanco",
    "numero": "10300539502",
    "modalidade": "carteira_hipotecaria",
    "sistema_amortizacao": "SAC",
    "taxa_referencial": "TR"
  },

  "taxas": {
    "mensal": 0.009631393,
    "anual_efetiva": 0.121900,
    "spread_banco": null
  },

  "snapshot": {
    "data_emissao": "2026-05-05",
    "saldo_devedor": 429629.87,
    "prazo_total_contratado": 360,
    "prazo_remanescente": 189,
    "valor_original": 536000.00
  },

  "proxima_parcela": {
    "numero": 5,
    "vencimento": "2026-05-21",
    "valor_total": 6578.27,
    "amortizacao": 2285.27,
    "juros": 4159.94,
    "mip": 94.45,
    "dfi": 38.61,
    "seguros_total": 133.06
  },

  "ultima_parcela": {
    "numero": 193,
    "vencimento": "2042-01-21",
    "valor_total": 2307.27,
    "amortizacao": 2285.27,
    "juros": 9.55,
    "seguros_total": 12.45
  },

  "parcelas": [
    {
      "numero": 5,
      "vencimento": "2026-05-21",
      "situacao": "aberta",
      "valor_total": 6578.27,
      "amortizacao": 2285.27,
      "juros": 4159.94,
      "mip": 94.45,
      "dfi": 38.61,
      "seguros_total": 133.06,
      "saldo_pos_pagamento": 427344.60
    }
    // ... até 420 objetos
  ],

  "operacoes_historicas": [
    {
      "tipo": "amortizacao_extraordinaria",
      "data": "2026-04-28",
      "valor_principal": 80000.00,
      "juros_pro_rata": 178.73,
      "atualizacao_monetaria": 31.35,
      "valor_total_debitado": 80210.08,
      "modalidade": "reducao_prazo",
      "fonte": "recurso_proprio"
    }
  ]
}
```

### Campos obrigatórios vs. nullable

| Campo | Obrigatório | Comportamento se ausente |
|---|---|---|
| `contrato.banco` | Sim | Parser falha; cai em LLM ou manual |
| `contrato.sistema_amortizacao` | Sim | Idem |
| `taxas.mensal` | Sim | Idem |
| `snapshot.saldo_devedor` | Sim | Idem |
| `snapshot.prazo_remanescente` | Sim | Idem |
| `proxima_parcela.*` | Sim | Idem |
| `ultima_parcela.*` | Sim | Idem |
| `contrato.modalidade` | Não | `null` |
| `contrato.taxa_referencial` | Não | `null` |
| `taxas.anual_efetiva` | Não | Derivado: `(1 + mensal)^12 - 1` |
| `snapshot.valor_original` | Não | `null` |
| `proxima_parcela.mip` / `.dfi` | Não | `null`; usar `seguros_total` agregado |
| `ultima_parcela.amortizacao` etc. | Não | Calcular via motor se ausente |
| `operacoes_historicas` | Não | `[]` |
| `parcelas` | Não para manual | `[]` para entrada manual |

### Campos nunca extraídos (PII)

| Campo presente no DDC | Tratamento |
|---|---|
| CPF do mutuário | Regex `\d{3}\.\d{3}\.\d{3}-\d{2}` → substituir por `[CPF_REDACTED]` no arquivo; não extrair para JSON |
| Nome do mutuário | Não extrair |
| Número da agência | Não extrair |
| Conta-corrente | Não extrair |
| Endereço do imóvel | Não extrair |

`_meta.redaction_log` lista quais campos foram detectados e removidos. Se CPF foi encontrado, `"cpf"` entra na lista.

### Validações antes de aceitar o JSON

| Regra | Verificação | Erro |
|---|---|---|
| Saldo positivo | `saldo_devedor > 0` | `SALDO_INVALIDO` |
| Taxa em range imobiliário | `0.003 < taxa_mensal < 0.018` | `TAXA_FORA_DE_RANGE` |
| Prazo positivo | `prazo_remanescente > 0` | `PRAZO_INVALIDO` |
| Parcela coerente | `abs(amort + juros + seguros - total) < 0.10` | `PARCELA_INCOERENTE` |
| Saldo decrescente | `proxima_parcela.saldo_pos < snapshot.saldo_devedor` | `SALDO_NAO_DECRESCE` |
| Data de emissão razoável | `2000-01-01 < data_emissao <= hoje` | `DATA_INVALIDA` |
| Número de parcelas condizente | `prazo_remanescente == len(parcelas)` quando array presente | `PRAZO_INCONSISTENTE` |

Se 1 validação falha → `parser_issues` recebe o erro + campo. Sistema avisa o usuário para confirmar.
Se 2+ validações falham → sistema pede revisão manual antes de persistir.

---

## 7. Mapeamento JSON → tabelas

| Campo JSON | Tabela | Coluna |
|---|---|---|
| `contrato.banco` (code) | `contracts` | `bank_id` → resolve via `ref_banks.code` |
| `contrato.numero` | `contracts` | `numero_contrato` |
| `contrato.modalidade` (code) | `contracts` | `modality_id` → resolve via `ref_modalities.code` |
| `contrato.sistema_amortizacao` (code) | `contracts` | `amortization_system_id` → resolve via `ref_amortization_systems.code` |
| `taxas.mensal` | `contracts` | `taxa_mensal` |
| `taxas.anual_efetiva` | `contracts` | `taxa_anual_efetiva` |
| `contrato.taxa_referencial` (code) | `contracts` | `index_rate_id` → resolve via `ref_index_rates.code` |
| `snapshot.data_emissao` | `ddc_snapshots` | `data_emissao` |
| `snapshot.saldo_devedor` | `ddc_snapshots` | `saldo_devedor` |
| `snapshot.prazo_remanescente` | `ddc_snapshots` | `prazo_remanescente` |
| `proxima_parcela.*` | `ddc_snapshots` | `proxima_parcela_*` |
| `ultima_parcela.*` | `ddc_snapshots` | `ultima_parcela_*` |
| `_meta.parser_metodo` | `ddc_snapshots` | `parser_metodo` (text — propriedade do ato) |
| `_meta.parser_versao` (version_code) | `ddc_snapshots` | `parser_version_id` → resolve via `ref_parser_versions.version_code` |
| `_meta.parser_issues` | `ddc_snapshots` | `parser_issues` |
| `parcelas[*]` | `ddc_installments` | uma linha por objeto |
| `operacoes_historicas[*]` | `user_operations` | importadas com `origem = 'ddc'` |

**Como a resolução de code → id funciona na ingestão:**

O parser produz o JSON com `code` (string legível). A camada de ingestão faz um lookup em memória das reference tables (carregadas no boot — são imutáveis e pequenas) e substitui o code pelo UUID antes de persistir. Nunca há JOIN em tempo de escrita; as reference tables são lidas uma vez e cacheadas.

```
ingestao(json):
  bank_id    = cache.ref_banks["itau"].id
  modality_id = cache.ref_modalities["carteira_hipotecaria"].id
  system_id   = cache.ref_amortization_systems["SAC"].id
  rate_id     = cache.ref_index_rates["TR"].id
  parser_ver_id = cache.ref_parser_versions["itau_v1.0"].id

  INSERT INTO contracts (bank_id, modality_id, ...)
  INSERT INTO ddc_snapshots (parser_version_id, ...)
```

**Nota sobre `operacoes_historicas`**: as operações encontradas no DDC são importadas para `user_operations` com `origem = 'ddc'`. Se uma operação já existe (usuário já havia declarado manualmente), o sistema faz merge: mantém o registro do usuário, atualiza `juros_pro_rata` e `atualizacao_monetaria` se estavam em branco.

**Nota sobre `contracts`**: os campos canônicos do contrato (`taxa_mensal`, `sistema_amortizacao`, etc.) só são atualizados no primeiro DDC de um contrato. Para DDCs subsequentes, se houver divergência (ex: taxa mudou), o sistema alerta e aguarda confirmação do usuário antes de sobrescrever.

---

## 8. Ajustes no schema_01.md referenciados por este documento

| Tabela | Campo | Ação | Notas |
|---|---|---|---|
| `contracts` | `calculation_mode_id` | FK → `ref_calculation_modes` | Substitui `modo_calculo_detectado text` |
| `contracts` | `calculation_mode_override_id` | FK → `ref_calculation_modes` nullable | Substitui `modo_calculo_override text` |
| `ddc_snapshots` | `parcelas_arquivadas` | boolean default false | True quando installments comprimidos |
| `ddc_snapshots` | `parcelas_archive` | jsonb nullable | Resumo comprimido quando arquivado |
| `user_operations` | tipo `'parcela_paga'` | Remover do enum | Parcelas pagas vêm do DDC; não declaradas pelo usuário |

`ref_calculation_modes` seed: `'SAC'`, `'PRICE'`, `'itau'`.

---

## Próximos documentos

Com motor e JSON definidos, as decisões pendentes são:

- [ ] **`parser_01.md`** — spec por banco: como cada banco organiza o PDF, coordenadas, regex por seção. Itaú primeiro.
- [ ] **`motor_02.md`** — implementação do motor SAC/PRICE/Itaú em TypeScript (funções puras, testáveis). Isso é código, não mais ideação.
- [ ] Decisão de stack (Next.js App Router? React + API separada?) — impacta onde o motor vive.
