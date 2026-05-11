# Marco Zero — Schema Relacional & Contrato do Parser

> Documento de design — versão 1
> Data: 06/05/2026
> Status: em discussão
> Depende de: `../product/idea_01.md` (hierarquia de dados), `../ux/journey_07_audit.md` (reconciliação)

---

## Por que esses dois documentos são um só

O schema define o que precisa ser persistido. O parser define o que precisa ser extraído.
São a mesma decisão — se o schema muda, o parser muda junto.

**Regra prática**: os campos da tabela `ddc_snapshots` + `ddc_installments` são o contrato de output do parser. Qualquer campo que o parser não conseguir extrair precisa aparecer no schema como nullable com razão documentada.

---

## 1. Mapa de entidades

```
auth.users (gerenciado pelo provider)
    │
    ├── user_profiles          ← extensão de identidade
    │
    ├── properties             ← imóveis (1 usuário → N imóveis)
    │     └── contracts        ← financiamentos (1 imóvel → N contratos)
    │           │
    │           ├── ddc_snapshots        ← DDCs importados (imutáveis)
    │           │     └── ddc_installments  ← parcelas individuais do DDC
    │           │
    │           ├── user_operations      ← amortizações e eventos declarados
    │           │
    │           ├── scenarios            ← parâmetros de simulação salvos
    │           │     └── scenario_versions  ← histórico de edições
    │           │
    │           ├── stress_test_runs     ← resultados salvos de stress tests
    │           │
    │           ├── reminders            ← FGTS, PLR, datas customizadas
    │           │
    │           └── notes                ← anotações livres
    │
    ├── co_titular_access      ← permissões de compartilhamento
    │
    ├── coach_alerts           ← alertas gerados e seu estado
    │
    ├── audit_events           ← log append-only de tudo
    │
    └── ai_sessions            ← histórico de chat (30 dias, sem PII)
```

**Decisão de design**: `user_id` é desnormalizado em todas as tabelas, mesmo nas filhas (`ddc_installments`, `scenario_versions`, etc.). Isso permite que as políticas RLS sejam sempre `WHERE user_id = auth.uid()` — simples, indexável, sem joins em runtime.

---

## 2. Tabelas

### 2.0 Reference Tables

Valores lookup que antes eram strings soltas (`"itau"`, `"SAC"`, `"itau_v1.0"`) viram tabelas próprias com UUID como PK e um campo `code` único e legível por humanos. Toda FK aponta para o UUID — o `code` é só para seed data e debugging.

**Regra**: reference tables são imutáveis após seed. Não têm `user_id` (são globais). Não têm RLS. Novas entradas só via migration controlada.

---

#### `ref_banks`

| Coluna | Tipo | Restrições | Notas |
|---|---|---|---|
| `id` | `uuid` | PK, default gen_random_uuid() | |
| `code` | `text` | UNIQUE NOT NULL | `'itau'`, `'caixa'`, `'bb'`, `'bradesco'`, `'santander'`, `'outro'` |
| `display_name` | `text` | NOT NULL | "Itaú Unibanco", "Caixa Econômica Federal" |
| `short_name` | `text` | NOT NULL | "Itaú", "Caixa", "BB" |
| `ispb` | `text` | nullable | Código ISPB do Banco Central (identificador oficial) |
| `has_ddc_parser` | `boolean` | default false | Marco Zero tem parser determinístico para este banco |
| `active` | `boolean` | default true | Bancos descontinuados ficam inativos, não deletados |

**Seed inicial:**

| code | display_name | has_ddc_parser |
|---|---|---|
| `caixa` | Caixa Econômica Federal | false (v1) |
| `itau` | Itaú Unibanco | **true** (implementar primeiro) |
| `bb` | Banco do Brasil | false |
| `bradesco` | Banco Bradesco | false |
| `santander` | Santander Brasil | false |
| `outro` | Outro banco | false |

---

#### `ref_amortization_systems`

Sistema de amortização conforme registrado no contrato.

| Coluna | Tipo | Restrições | Notas |
|---|---|---|---|
| `id` | `uuid` | PK | |
| `code` | `text` | UNIQUE NOT NULL | `'SAC'`, `'PRICE'` |
| `display_name` | `text` | NOT NULL | "Sistema de Amortização Constante", "Sistema Francês (Price)" |
| `description` | `text` | nullable | Explicação para o usuário leigo |

---

#### `ref_calculation_modes`

Modo de cálculo **detectado pelo motor** — pode divergir do sistema contratual (caso do híbrido Itaú). Separado de `ref_amortization_systems` porque é comportamental, não contratual.

| Coluna | Tipo | Restrições | Notas |
|---|---|---|---|
| `id` | `uuid` | PK | |
| `code` | `text` | UNIQUE NOT NULL | `'SAC'`, `'PRICE'`, `'itau'` |
| `display_name` | `text` | NOT NULL | |
| `description` | `text` | nullable | Explicação técnica do comportamento |

---

#### `ref_modalities`

Modalidade do financiamento — define regras de FGTS, teto SFH, elegibilidade a portabilidade.

| Coluna | Tipo | Restrições | Notas |
|---|---|---|---|
| `id` | `uuid` | PK | |
| `code` | `text` | UNIQUE NOT NULL | `'carteira_hipotecaria'`, `'sbpe'`, `'pro_cotista'`, `'minha_casa'`, `'fgts_habitacional'`, `'outro'` |
| `display_name` | `text` | NOT NULL | "Carteira Hipotecária", "SBPE" |
| `eligible_fgts` | `boolean` | NOT NULL | Permite uso de FGTS para amortização |
| `sfh_ceiling_brl` | `numeric(14,2)` | nullable | Teto do SFH nessa modalidade (R$ 2,25M em 05/2026) |
| `active` | `boolean` | default true | |

---

#### `ref_index_rates`

Índice de correção do contrato (influencia stress tests e comparações de portabilidade).

| Coluna | Tipo | Restrições | Notas |
|---|---|---|---|
| `id` | `uuid` | PK | |
| `code` | `text` | UNIQUE NOT NULL | `'TR'`, `'IPCA'`, `'PREFIXADO'`, `'CDI'`, `'INCC'` |
| `display_name` | `text` | NOT NULL | "Taxa Referencial", "IPCA", "Pré-fixado" |
| `type` | `text` | NOT NULL | `'pos_fixado'`, `'pre_fixado'`, `'hibrido'` |
| `volatile` | `boolean` | NOT NULL | true = varia mês a mês (TR, IPCA); false = travado no contrato |
| `active` | `boolean` | default true | |

---

#### `ref_parser_versions`

Registro de cada versão de parser deployada. Permite rastrear qual versão extraiu qual DDC e facilita reprocessamento quando um parser é corrigido.

| Coluna | Tipo | Restrições | Notas |
|---|---|---|---|
| `id` | `uuid` | PK | |
| `bank_id` | `uuid` | FK → ref_banks, NOT NULL | A qual banco esse parser pertence |
| `version_code` | `text` | UNIQUE NOT NULL | `'itau_v1.0'`, `'itau_v1.1'`, `'caixa_v1.0'` |
| `method` | `text` | NOT NULL | `'deterministic'`, `'llm'` |
| `released_at` | `date` | NOT NULL | Quando foi deployado |
| `deprecated_at` | `date` | nullable | Quando foi substituído |
| `changelog` | `text` | nullable | O que mudou em relação à versão anterior |

**Por que isso importa**: quando o banco muda o layout do PDF e o parser é atualizado, todos os `ddc_snapshots` com `parser_version_id` apontando para a versão antiga podem ser identificados e reprocessados em batch.

---

### 2.1 `user_profiles`

Extensão da identidade criada pelo auth provider. Criada automaticamente via trigger quando `auth.users` recebe insert.

| Coluna | Tipo | Restrições | Notas |
|---|---|---|---|
| `id` | `uuid` | PK, FK → auth.users.id | Mesmo ID do auth provider |
| `nome` | `text` | nullable | Nome pode vir de OAuth ou ser preenchido depois |
| `fgts_ultima_utilizacao` | `date` | nullable | Alimenta o Coach de FGTS |
| `reserva_emergencia_declarada` | `numeric(14,2)` | nullable | Usada em stress tests; declarada pelo usuário |
| `plano` | `text` | default `'basico'` | `'basico'`, `'plus'`, `'avancado'` |
| `modo_offline_ia` | `boolean` | default `false` | Usuário optou por não usar LLM |
| `created_at` | `timestamptz` | default now() | |
| `updated_at` | `timestamptz` | | Atualizado por trigger |

**LGPD**: sem CPF, sem telefone por padrão. Telefone é coletado separado apenas se usuário ativar notificação por SMS.

---

### 2.2 `properties`

Imóveis do usuário. Um usuário pode ter N imóveis.

| Coluna | Tipo | Restrições | Notas |
|---|---|---|---|
| `id` | `uuid` | PK |  |
| `user_id` | `uuid` | FK → auth.users, NOT NULL | Desnormalizado para RLS |
| `apelido` | `text` | NOT NULL | "Apartamento Contagem", "Casa de praia" |
| `endereco_resumido` | `text` | nullable | Cidade/bairro. Sem número completo — não é necessário |
| `deleted_at` | `timestamptz` | nullable | Soft delete |
| `created_at` | `timestamptz` | default now() | |

**Decisão**: não persistir endereço completo — não é necessário para nenhuma feature e expande superfície de dados sensíveis.

---

### 2.3 `contracts`

O financiamento em si. Os campos aqui são os **campos canônicos** que o parser extrai do DDC — ou que o usuário declara manualmente.

| Coluna | Tipo | Restrições | Notas |
|---|---|---|---|
| `id` | `uuid` | PK | |
| `user_id` | `uuid` | FK → auth.users, NOT NULL | Desnormalizado para RLS |
| `property_id` | `uuid` | FK → properties, NOT NULL | |
| `apelido` | `text` | nullable | Se usuário quiser diferenciar de imóveis com múltiplos contratos |
| `bank_id` | `uuid` | FK → ref_banks, NOT NULL | Substituiu `banco` (text) |
| `bank_custom_name` | `text` | nullable | Preenchido quando bank_id aponta para `ref_banks.code = 'outro'` |
| `numero_contrato` | `text` | nullable | Extraído do DDC quando disponível |
| `modality_id` | `uuid` | FK → ref_modalities, nullable | Substituiu `modalidade` (text) |
| `amortization_system_id` | `uuid` | FK → ref_amortization_systems, NOT NULL | Substituiu `sistema_amortizacao` (text) |
| `calculation_mode_id` | `uuid` | FK → ref_calculation_modes, nullable | Modo detectado pelo motor (SAC padrão, PRICE, híbrido) |
| `calculation_mode_override_id` | `uuid` | FK → ref_calculation_modes, nullable | Sobrescrita manual pelo usuário |
| `index_rate_id` | `uuid` | FK → ref_index_rates, nullable | Substituiu `taxa_referencial` (text) |
| `taxa_mensal` | `numeric(12,10)` | NOT NULL | Ex: `0.0096313930` |
| `taxa_anual_efetiva` | `numeric(8,6)` | NOT NULL | Ex: `0.121900` |
| `valor_original` | `numeric(14,2)` | nullable | Valor do contrato no início |
| `data_inicio` | `date` | nullable | Data da primeira parcela |
| `prazo_total_original` | `integer` | nullable | Prazo contratado em meses (ex: 360) |
| `status` | `text` | default `'ativo'` | `'ativo'`, `'quitado'`, `'portado'` |
| `contrato_predecessor_id` | `uuid` | nullable, FK → contracts | Quando portabilidade: aponta pro contrato anterior |
| `input_method` | `text` | NOT NULL | `'ddc_parser'`, `'ddc_llm'`, `'manual'` — como foi criado |
| `deleted_at` | `timestamptz` | nullable | |
| `created_at` | `timestamptz` | default now() | |
| `updated_at` | `timestamptz` | | |

**Sobre taxa**: usar `numeric(12,10)` para a taxa mensal preserva a precisão necessária (0,9631393% = 0.009631393). Jamais `float` para dado financeiro.

**Sobre `calculation_mode_id` vs `amortization_system_id`**: o primeiro é o que consta no contrato (SAC ou PRICE). O segundo é o que o motor detecta que o banco está fazendo na prática (pode ser híbrido mesmo num contrato SAC). Os dois são distintos porque bancos como o Itaú aplicam comportamento híbrido sem documentar.

**Sobre `contrato_predecessor_id`**: quando o usuário faz portabilidade, o contrato novo aponta para o contrato antigo. O audit trail mostra a transição. O contrato antigo passa para `status = 'portado'`.

---

### 2.4 `ddc_snapshots`

Cada DDC importado. **Imutável após insert** — nunca sofre UPDATE. É o registro de "o que o banco disse nesta data".

| Coluna | Tipo | Restrições | Notas |
|---|---|---|---|
| `id` | `uuid` | PK | |
| `user_id` | `uuid` | FK, NOT NULL | Desnormalizado para RLS |
| `contract_id` | `uuid` | FK → contracts, NOT NULL | |
| `versao` | `integer` | NOT NULL | 1, 2, 3... por contrato. Calculado no insert |
| `data_emissao` | `date` | NOT NULL | Data em que o banco gerou o DDC |
| `data_importacao` | `timestamptz` | default now() | Quando o usuário fez o upload |
| `saldo_devedor` | `numeric(14,2)` | NOT NULL | Saldo na data de emissão |
| `prazo_remanescente` | `integer` | NOT NULL | Parcelas restantes na data de emissão |
| `proxima_parcela_numero` | `integer` | NOT NULL | Número da próxima parcela em aberto |
| `proxima_parcela_valor` | `numeric(14,2)` | NOT NULL | Valor total da próxima parcela |
| `proxima_parcela_vencimento` | `date` | NOT NULL | |
| `proxima_parcela_amortizacao` | `numeric(14,2)` | NOT NULL | |
| `proxima_parcela_juros` | `numeric(14,2)` | NOT NULL | |
| `proxima_parcela_seguros` | `numeric(14,2)` | nullable | MIP + DFI agregados |
| `ultima_parcela_numero` | `integer` | NOT NULL | |
| `ultima_parcela_vencimento` | `date` | NOT NULL | |
| `ultima_parcela_valor` | `numeric(14,2)` | NOT NULL | |
| `parser_metodo` | `text` | NOT NULL | `'deterministic'`, `'llm'`, `'manual'` — mantido como texto; é propriedade do ato, não lookup |
| `parser_version_id` | `uuid` | FK → ref_parser_versions, nullable | Null quando `parser_metodo = 'manual'` |
| `parser_issues` | `jsonb` | default `'[]'` | Lista de alertas de validação gerados no parse |
| `reconciliacao_status` | `text` | default `'pendente'` | `'pendente'`, `'ok'`, `'divergente'`, `'manual'` |
| `reconciliacao_diff` | `numeric(14,2)` | nullable | Saldo esperado − saldo declarado. Null = não computado ainda |
| `reconciliacao_explicacao` | `text` | nullable | Texto gerado quando há divergência |
| `arquivo_id` | `uuid` | nullable, FK → ddc_files | Referência ao PDF no storage |

**Por que imutável**: o usuário precisa confiar que "o DDC de 05/05 disse X" nunca vai mudar. Toda correção posterior é uma nova operação declarada pelo usuário, não uma edição do snapshot.

**Sobre `reconciliacao_*`**: esses campos são preenchidos pelo sistema quando o próximo DDC é importado. O sistema compara `saldo_devedor` do novo DDC com o saldo esperado calculado a partir deste snapshot + operações declaradas entre os dois. Ver seção 6.

---

### 2.5 `ddc_installments`

Parcelas individuais dentro de um DDC. Alta cardinalidade — até 350+ linhas por DDC.

| Coluna | Tipo | Restrições | Notas |
|---|---|---|---|
| `id` | `uuid` | PK | |
| `user_id` | `uuid` | FK, NOT NULL | Desnormalizado para RLS |
| `ddc_snapshot_id` | `uuid` | FK → ddc_snapshots, NOT NULL | |
| `contract_id` | `uuid` | FK → contracts, NOT NULL | Desnormalizado para queries |
| `numero_parcela` | `integer` | NOT NULL | Ex: 5, 6, 7… |
| `vencimento` | `date` | NOT NULL | |
| `situacao` | `text` | NOT NULL | `'paga'`, `'aberta'`, `'futura'` |
| `valor_total` | `numeric(14,2)` | NOT NULL | |
| `amortizacao` | `numeric(14,2)` | NOT NULL | |
| `juros` | `numeric(14,2)` | NOT NULL | |
| `mip` | `numeric(14,2)` | nullable | Seguro de morte e invalidez |
| `dfi` | `numeric(14,2)` | nullable | Seguro de danos físicos |
| `saldo_pos_pagamento` | `numeric(14,2)` | NOT NULL | Saldo devedor após esta parcela |
| `created_at` | `timestamptz` | default now() | |

**Índice crítico**: `(contract_id, numero_parcela)` para busca de parcela específica. `(ddc_snapshot_id)` para listar todas as parcelas de um DDC.

**Volume estimado**: 300 parcelas × 10 DDCs/ano × 10.000 usuários = 30M linhas/ano. Normal para Postgres.

**Decisão**: parcelas de DDCs gerados por entrada manual (`parser_metodo = 'manual'`) **não existem** — o usuário declarou apenas o saldo e as condições gerais, não as parcelas individuais. Nesse caso `ddc_installments` fica vazio para esse snapshot.

---

### 2.6 `user_operations`

Operações declaradas pelo usuário. São entidades de **primeira classe** — não derivadas do DDC. Alimentam a reconciliação e o motor de cálculo.

| Coluna | Tipo | Restrições | Notas |
|---|---|---|---|
| `id` | `uuid` | PK | |
| `user_id` | `uuid` | FK, NOT NULL | |
| `contract_id` | `uuid` | FK → contracts, NOT NULL | |
| `tipo` | `text` | NOT NULL | `'amortizacao_prazo'`, `'amortizacao_parcela'`, `'parcela_paga'`, `'fgts'`, `'portabilidade'`, `'outro'` |
| `data_operacao` | `date` | NOT NULL | Data em que o usuário fez a operação |
| `valor_principal` | `numeric(14,2)` | NOT NULL | Valor amortizado / pago |
| `juros_pro_rata` | `numeric(14,2)` | nullable | Juros devidos entre último vencimento e data da operação |
| `atualizacao_monetaria` | `numeric(14,2)` | nullable | Correção monetária (TR etc.) cobrada pelo banco |
| `valor_total_desembolsado` | `numeric(14,2)` | nullable | Principal + juros pró-rata + correção |
| `modalidade_amortizacao` | `text` | nullable | `'reducao_prazo'`, `'reducao_parcela'` — quando tipo = amortização |
| `fonte` | `text` | default `'recurso_proprio'` | `'recurso_proprio'`, `'fgts'`, `'ambos'` |
| `fgts_valor` | `numeric(14,2)` | nullable | Parte do FGTS no desembolso total |
| `notas` | `text` | nullable | Campo livre para o usuário |
| `comprovante_storage_id` | `uuid` | nullable | Referência a arquivo no storage |
| `deleted_at` | `timestamptz` | nullable | Soft delete |
| `created_at` | `timestamptz` | default now() | |
| `updated_at` | `timestamptz` | | |

**Fluxo de uso**: usuário amortiza R$ 80k → registra `user_operations` com `tipo = 'amortizacao_prazo'`, `valor_principal = 80000`. Quando importa o próximo DDC, o sistema calcula: saldo esperado = saldo anterior − 80000 + correções. Se bate com o DDC: reconciliação ✅.

**Sobre `deleted_at`**: operações podem ser "removidas" pelo usuário em caso de erro, mas o registro permanece com `deleted_at` preenchido. O audit mostra a operação e a remoção.

---

### 2.7 `scenarios`

Parâmetros de simulação salvos. **Não guarda resultados** — resultados são computados em runtime pelo motor de cálculo.

| Coluna | Tipo | Restrições | Notas |
|---|---|---|---|
| `id` | `uuid` | PK | |
| `user_id` | `uuid` | FK, NOT NULL | |
| `contract_id` | `uuid` | FK → contracts, NOT NULL | |
| `nome` | `text` | NOT NULL | "5k/mês + 60k/ano", definido pelo usuário |
| `status` | `text` | default `'planejado'` | `'planejado'`, `'em_execucao'`, `'concluido'`, `'abandonado'` |
| `aporte_mensal_extra` | `numeric(14,2)` | default 0 | |
| `aporte_anual_extra` | `numeric(14,2)` | default 0 | |
| `mes_aporte_anual` | `smallint` | nullable | 1–12. null = sem aporte anual |
| `usar_fgts` | `boolean` | default false | |
| `fgts_valor_estimado` | `numeric(14,2)` | nullable | Saldo FGTS que o usuário pretende usar |
| `data_execucao_prevista` | `date` | nullable | Quando o usuário planeja começar |
| `versao_atual` | `integer` | default 1 | Incrementa a cada edição |
| `deleted_at` | `timestamptz` | nullable | |
| `created_at` | `timestamptz` | default now() | |
| `updated_at` | `timestamptz` | | |

**Por que não guardar resultados**: resultados dependem do saldo *atual* do contrato, que muda com cada DDC novo e cada operação. Guardar resultados criaria stale data. O motor computa em < 100ms para qualquer projeção SAC.

---

### 2.8 `scenario_versions`

Histórico imutável de cada edição de um cenário. Quando o usuário edita um cenário, o estado anterior vira uma versão.

| Coluna | Tipo | Restrições | Notas |
|---|---|---|---|
| `id` | `uuid` | PK | |
| `user_id` | `uuid` | FK, NOT NULL | Desnormalizado |
| `scenario_id` | `uuid` | FK → scenarios, NOT NULL | |
| `versao` | `integer` | NOT NULL | |
| `snapshot` | `jsonb` | NOT NULL | Cópia exata de todos os campos de `scenarios` naquele momento |
| `editado_por` | `uuid` | FK → auth.users | Quem editou (relevante para co-titular) |
| `created_at` | `timestamptz` | default now() | |

**Decisão de usar JSONB**: o schema de `scenarios` pode evoluir (novas colunas). Guardar um snapshot em JSONB é mais flexível que colunas espelhadas. O motor de cálculo usa o snapshot inteiro — é sempre legível.

---

### 2.9 `stress_test_runs`

Resultados de stress tests salvos. Diferente de `scenarios` — aqui o resultado **é** persistido, porque é o dado de interesse (o usuário quer ver o histórico de "quanto meu plano aguenta").

| Coluna | Tipo | Restrições | Notas |
|---|---|---|---|
| `id` | `uuid` | PK | |
| `user_id` | `uuid` | FK, NOT NULL | |
| `contract_id` | `uuid` | FK → contracts, NOT NULL | |
| `scenario_id` | `uuid` | nullable, FK → scenarios | Qual cenário foi testado (null = plano atual) |
| `tipo_stress` | `text` | NOT NULL | `'perda_emprego'`, `'aumento_juros'`, `'inflacao_alta'`, `'despesa_inesperada'`, `'filho_escola'`, `'aposentadoria'`, `'desvalorizacao'`, `'aumento_renda'`, `'bonus'`, `'heranca'`, `'customizado'` |
| `parametros` | `jsonb` | NOT NULL | Parâmetros do stress: `{duracao_meses: 6, reducao_renda_pct: 1.0}` |
| `resultado` | `text` | NOT NULL | `'cobre'`, `'desliza'`, `'quebra'` |
| `resultado_detalhe` | `jsonb` | NOT NULL | Dados completos: meses de folga, novo prazo de quitação, delta em juros, recomendação |
| `reserva_emergencia_declarada` | `numeric(14,2)` | nullable | Snapshot da reserva no momento do teste |
| `ddc_snapshot_id` | `uuid` | nullable, FK → ddc_snapshots | DDC base usado no cálculo |
| `created_at` | `timestamptz` | default now() | |

**Por que persistir resultado**: a tela de stress tests mostra histórico recente com resultado (✓ ⚠ ✗). Recomputar em tempo real seria possível mas desnecessário — e perderia a rastreabilidade de "esse resultado foi calculado com o DDC de tal data".

---

### 2.10 `reminders`

Lembretes e janelas de oportunidade.

| Coluna | Tipo | Restrições | Notas |
|---|---|---|---|
| `id` | `uuid` | PK | |
| `user_id` | `uuid` | FK, NOT NULL | |
| `contract_id` | `uuid` | nullable, FK → contracts | Null = lembrete do usuário sem contrato específico |
| `tipo` | `text` | NOT NULL | `'fgts_janela'`, `'plr'`, `'portabilidade'`, `'aniversario_cenario'`, `'customizado'` |
| `titulo` | `text` | NOT NULL | Exibido na UI |
| `data_alvo` | `date` | NOT NULL | Quando disparar |
| `status` | `text` | default `'pendente'` | `'pendente'`, `'disparado'`, `'concluido'`, `'ignorado'` |
| `origem` | `text` | NOT NULL | `'sistema'`, `'usuario'` |
| `metadados` | `jsonb` | nullable | Dados específicos do tipo: `{fgts_saldo_estimado: 47300}` |
| `created_at` | `timestamptz` | default now() | |
| `updated_at` | `timestamptz` | | |

---

### 2.11 `notes`

Anotações livres do usuário por contrato.

| Coluna | Tipo | Restrições | Notas |
|---|---|---|---|
| `id` | `uuid` | PK | |
| `user_id` | `uuid` | FK, NOT NULL | |
| `contract_id` | `uuid` | FK → contracts, NOT NULL | |
| `conteudo` | `text` | NOT NULL | Sem limite arbitrário — texto livre |
| `deleted_at` | `timestamptz` | nullable | |
| `created_at` | `timestamptz` | default now() | |
| `updated_at` | `timestamptz` | | |

---

### 2.12 `co_titular_access`

Compartilhamento entre dois usuários. Co-titular tem conta separada — não é sub-usuário.

| Coluna | Tipo | Restrições | Notas |
|---|---|---|---|
| `id` | `uuid` | PK | |
| `contract_id` | `uuid` | FK → contracts, NOT NULL | |
| `owner_user_id` | `uuid` | FK → auth.users, NOT NULL | Quem compartilhou |
| `guest_user_id` | `uuid` | FK → auth.users, NOT NULL | Quem recebeu acesso |
| `permissao` | `text` | NOT NULL | `'visualizacao'`, `'edicao'` |
| `status` | `text` | default `'pendente'` | `'pendente'`, `'ativo'`, `'revogado'` |
| `created_at` | `timestamptz` | default now() | |
| `revogado_at` | `timestamptz` | nullable | |

**Restrição implícita**: apenas o `owner_user_id` pode criar ou revogar registros aqui. O guest só aceita ou recusa o convite.

---

### 2.13 `coach_alerts`

Alertas gerados pelo Coach. Gerados pelo sistema, gerenciados pelo usuário.

| Coluna | Tipo | Restrições | Notas |
|---|---|---|---|
| `id` | `uuid` | PK | |
| `user_id` | `uuid` | FK, NOT NULL | |
| `contract_id` | `uuid` | nullable, FK → contracts | |
| `tipo` | `text` | NOT NULL | `'fgts_abrindo'`, `'fgts_aberta'`, `'selic_queda'`, `'desvio_plano'`, `'revisao_trimestral'`, `'portabilidade'`, `'aumento_renda'` etc. |
| `titulo` | `text` | NOT NULL | Ex: "FGTS libera em 28 dias" |
| `corpo` | `text` | NOT NULL | Descrição completa do alerta |
| `prioridade` | `smallint` | NOT NULL | 1–3 (1=hoje, 2=semana, 3=horizonte) |
| `status` | `text` | default `'ativo'` | `'ativo'`, `'lido'`, `'snoozed'`, `'descartado'` |
| `snooze_ate` | `date` | nullable | Quando reativar se snoozed |
| `ignorado_count` | `smallint` | default 0 | Conta ignoramentos para detecção de fadiga |
| `metadados` | `jsonb` | nullable | Dados contextuais: `{saldo_fgts: 47300, parcelas_eliminadas: 19}` |
| `created_at` | `timestamptz` | default now() | |
| `updated_at` | `timestamptz` | | |

**Fadiga**: quando `ignorado_count >= 3`, o Coach reduz frequência de alertas do mesmo tipo para esse usuário. Lógica é na camada de aplicação — não no banco.

---

### 2.14 `audit_events`

Log append-only. Registra toda ação significativa. **Sem UPDATE ou DELETE** — nunca. Retenção: 6 meses por padrão (LGPD).

| Coluna | Tipo | Restrições | Notas |
|---|---|---|---|
| `id` | `uuid` | PK | |
| `user_id` | `uuid` | FK, NOT NULL | |
| `contract_id` | `uuid` | nullable, FK → contracts | |
| `tipo_evento` | `text` | NOT NULL | Ver catálogo abaixo |
| `entidade_tipo` | `text` | NOT NULL | `'contract'`, `'ddc_snapshot'`, `'user_operation'`, `'scenario'` etc. |
| `entidade_id` | `uuid` | nullable | ID da entidade afetada |
| `ator_user_id` | `uuid` | NOT NULL | Quem fez a ação (pode ser diferente de user_id se co-titular) |
| `payload` | `jsonb` | nullable | Dados relevantes do evento (sem PII) |
| `ip_hash` | `text` | nullable | Hash do IP — não o IP raw |
| `created_at` | `timestamptz` | default now() | |

**Catálogo de `tipo_evento`**:

| Valor | Quando |
|---|---|
| `contract.created` | Contrato criado |
| `contract.updated` | Campo de contrato editado |
| `ddc.imported` | DDC importado com sucesso |
| `ddc.import_failed` | DDC falhou na extração |
| `ddc.reconciled` | Reconciliação concluída (ok ou divergente) |
| `operation.created` | Amortização/operação declarada |
| `operation.deleted` | Operação removida (soft delete) |
| `scenario.created` | Cenário criado |
| `scenario.edited` | Cenário editado (versão nova criada) |
| `scenario.promoted` | Cenário promovido a plano em execução |
| `stress_test.run` | Stress test executado |
| `cotitular.invited` | Co-titular convidado |
| `cotitular.accepted` | Convite aceito |
| `cotitular.revoked` | Acesso revogado |
| `account.login` | Login realizado |
| `account.export` | Export de dados solicitado |
| `account.delete_requested` | Exclusão de conta solicitada |
| `ai.session_started` | Sessão de chat IA iniciada |

---

### 2.15 `ai_sessions`

Histórico de interações com LLM. **Retenção: 30 dias**. Sem PII após redaction pré-envio.

| Coluna | Tipo | Restrições | Notas |
|---|---|---|---|
| `id` | `uuid` | PK | |
| `user_id` | `uuid` | FK, NOT NULL | |
| `contract_id` | `uuid` | nullable, FK → contracts | |
| `mensagens` | `jsonb` | NOT NULL | Array de `{role, content, timestamp}`. CPF/nome/conta já redactados |
| `tokens_usados` | `integer` | nullable | Para monitoramento de custo |
| `modelo` | `text` | nullable | Qual modelo LLM foi usado |
| `created_at` | `timestamptz` | default now() | |
| `expires_at` | `timestamptz` | NOT NULL | `created_at + 30 days` — drive para deleção automática |

**Deleção**: job diário que deleta registros com `expires_at < now()`. Transparente para o usuário — a tela de Audit mostra "histórico disponível por 30 dias".

---

### 2.16 `ddc_files`

Metadados dos PDFs no storage. O PDF em si fica no bucket privado do S3/Cloudflare R2.

| Coluna | Tipo | Restrições | Notas |
|---|---|---|---|
| `id` | `uuid` | PK | |
| `user_id` | `uuid` | FK, NOT NULL | |
| `nome_original` | `text` | NOT NULL | Nome do arquivo como o usuário fez upload |
| `storage_bucket` | `text` | NOT NULL | Nome do bucket |
| `storage_path` | `text` | NOT NULL | Caminho dentro do bucket — nunca exposto diretamente |
| `tamanho_bytes` | `integer` | NOT NULL | |
| `cpf_redacted` | `boolean` | default false | Flag de que o CPF foi removido neste arquivo |
| `created_at` | `timestamptz` | default now() | |

**URLs**: nunca armazenadas. Sempre geradas on-demand pelo backend com assinatura temporária (15 min). Nenhum link de PDF vive no banco de dados.

---

## 3. Decisões que cruzam tabelas

### 3.1 Estado atual do contrato — derivado, não armazenado

O "estado atual" (saldo devedor hoje, parcela prevista, data de quitação) **não existe como coluna**. É computado em runtime por:

```
estado_atual = motor_sac(
  ultimo_ddc_snapshot,
  user_operations após a data do DDC
)
```

Isso é intencional. Guardar saldo atual como coluna criaria inconsistência quando o usuário declarar uma operação sem subir um DDC novo. O motor SAC computa em <10ms — não há razão para cache persistente.

### 3.2 Reconciliação automática

Quando um novo DDC é importado, o sistema executa:

```
saldo_esperado = motor_sac(
  ddc_snapshot_anterior,
  user_operations entre data_emissao_anterior e data_emissao_novo
)

diff = saldo_esperado - novo_ddc.saldo_devedor
```

Se `abs(diff) / saldo_esperado < 0.005` (< 0,5%): `reconciliacao_status = 'ok'`.
Se acima: `reconciliacao_status = 'divergente'`, preenche `reconciliacao_diff` e `reconciliacao_explicacao`.

Esse resultado atualiza `ddc_snapshots.reconciliacao_*` do **DDC anterior** (não do novo). O novo DDC fica com status `'pendente'` até que o próximo DDC confirme ele.

### 3.3 Cenários usam sempre o DDC mais recente como base

Cenários não persistem qual DDC foi base. Sempre computam a partir do `ddc_snapshots` com maior `versao` do contrato. Isso significa que um cenário salvo há 3 meses com saldo X agora computa com saldo Y (pós-amortizações). É o comportamento correto — o usuário vê "e se fizer isso *agora*".

Para o Audit, `scenario_versions.snapshot` guarda os parâmetros do cenário em cada edição, mas não o DDC base. Isso é aceitável — o audit de cenário não é "qual era o resultado em março", é "quais eram os parâmetros em março".

### 3.4 Soft delete com trilha

Todos os dados do usuário usam `deleted_at` (soft delete). Isso preserva o audit trail — se o usuário deletar uma operação por engano, o `audit_events` ainda mostra `operation.deleted`. Dentro do período de retenção, o dado continua existindo com `deleted_at` preenchido, visível apenas na tela de Audit.

Quando o usuário aciona "Excluir conta" (7 dias de cooldown), um job faz hard delete de tudo, incluindo os soft-deletados, os backups associados e os arquivos no storage.

---

## 4. Parser → Schema: o contrato de output

O parser (camadas 1 e 2 — determinístico e LLM) precisa produzir exatamente o seguinte JSON canônico. Este é o contrato de interface entre a camada de ingestão e o banco de dados.

```json
{
  "banco": "itau",
  "numero_contrato": "10300539502",
  "modalidade": "carteira_hipotecaria",
  "sistema_amortizacao": "SAC",
  "taxa_mensal": 0.009631393,
  "taxa_anual_efetiva": 0.1219,
  "taxa_referencial": "TR",

  "data_emissao": "2026-05-05",
  "saldo_devedor": 429629.87,
  "prazo_remanescente": 189,

  "proxima_parcela_numero": 5,
  "proxima_parcela_valor": 6578.27,
  "proxima_parcela_vencimento": "2026-05-21",
  "proxima_parcela_amortizacao": 2285.27,
  "proxima_parcela_juros": 4159.94,
  "proxima_parcela_seguros": 133.06,

  "ultima_parcela_numero": 193,
  "ultima_parcela_vencimento": "2042-01-21",
  "ultima_parcela_valor": 2307.27,

  "parcelas": [
    {
      "numero_parcela": 5,
      "vencimento": "2026-05-21",
      "situacao": "aberta",
      "valor_total": 6578.27,
      "amortizacao": 2285.27,
      "juros": 4159.94,
      "mip": 94.45,
      "dfi": 38.61,
      "saldo_pos_pagamento": 427344.60
    }
  ],

  "operacoes_historicas": [
    {
      "tipo": "amortizacao",
      "data": "2026-04-28",
      "valor_principal": 80000.00,
      "juros_pro_rata": 178.73,
      "atualizacao_monetaria": 31.35,
      "valor_total": 80210.08,
      "modalidade": "reducao_prazo"
    }
  ],

  "parser_metodo": "deterministic",
  "parser_versao": "itau_v1.0",
  "parser_issues": [],

  "campos_ausentes": [],
  "campos_inferidos": []
}
```

### Campos obrigatórios vs. nullable

| Campo | Obrigatório | Fallback se ausente |
|---|---|---|
| `banco`, `sistema_amortizacao`, `taxa_mensal` | Sim | Parser falha, cai em LLM ou manual |
| `saldo_devedor`, `prazo_remanescente` | Sim | Idem |
| `proxima_parcela_*` | Sim | Idem |
| `ultima_parcela_*` | Sim | Idem |
| `modalidade` | Não | null na tabela |
| `taxa_referencial` | Não | null |
| `mip`, `dfi` separados | Não | `seguros` agregado é suficiente |
| `operacoes_historicas` | Não | Array vazio |
| `parcelas` | Não para manual | Array vazio para entrada manual |

### Campos jamais persistidos

| Campo no DDC | O que fazer |
|---|---|
| CPF do mutuário | Detectar regex, substituir por `[CPF_REDACTED]` no arquivo **antes** de armazenar |
| Nome completo | Não extrair. Não persistir |
| Número da agência | Não extrair |
| Conta-corrente | Não extrair |

**Por que não extrair nome e agência**: não são necessários para nenhuma feature de cálculo. Extrair seria coletar sem finalidade — violação do princípio de necessidade da LGPD.

---

## 5. RLS — Design das políticas

Com Supabase (Postgres), Row-Level Security é ativado por tabela. A presença de `user_id` desnormalizado simplifica todas as políticas.

### Política base (para todas as tabelas com `user_id`)

```sql
-- Usuário vê apenas seus próprios dados
CREATE POLICY "users see own data"
ON <tabela>
FOR ALL
USING (user_id = auth.uid());
```

### Política estendida para co-titular

Tabelas que um co-titular também precisa ler: `contracts`, `ddc_snapshots`, `ddc_installments`, `user_operations`, `scenarios`, `stress_test_runs`, `notes`.

```sql
-- Co-titular com permissão ativa também vê
CREATE POLICY "cotitular can read"
ON contracts
FOR SELECT
USING (
  user_id = auth.uid()
  OR
  id IN (
    SELECT contract_id FROM co_titular_access
    WHERE guest_user_id = auth.uid()
    AND status = 'ativo'
  )
);
```

**Decisão**: co-titular com `permissao = 'visualizacao'` — apenas SELECT. Com `permissao = 'edicao'` — SELECT + INSERT + UPDATE nas tabelas operacionais (`user_operations`, `scenarios`, `notes`). **Nunca DELETE** — só o owner pode soft-deletar.

### `audit_events` — apenas insert e select próprio

```sql
-- Ninguém pode atualizar ou deletar audit events
CREATE POLICY "audit append only"
ON audit_events
FOR INSERT
WITH CHECK (user_id = auth.uid());

CREATE POLICY "users see own audit"
ON audit_events
FOR SELECT
USING (user_id = auth.uid());
-- Sem UPDATE policy = nenhum UPDATE é permitido via RLS
```

### `ai_sessions` — apenas select próprio, sem leitura de outros

Mesma política base. Adicionalmente, um job de backend (com service_role, que bypassa RLS) faz a deleção por `expires_at`.

---

## 6. Queries críticas e indexação

As queries mais frequentes e pesadas — definindo os índices necessários.

| Query | Tabela | Índice necessário |
|---|---|---|
| Dashboard: último DDC de um contrato | `ddc_snapshots` | `(contract_id, versao DESC)` |
| Linha do tempo de operações | `user_operations` | `(contract_id, data_operacao DESC)` |
| Parcelas de um DDC | `ddc_installments` | `(ddc_snapshot_id, numero_parcela)` |
| Parcela específica de um contrato | `ddc_installments` | `(contract_id, numero_parcela)` |
| Alertas ativos do Coach | `coach_alerts` | `(user_id, status, prioridade)` |
| Audit trail de um contrato | `audit_events` | `(contract_id, created_at DESC)` |
| AI sessions expiradas (job) | `ai_sessions` | `(expires_at)` |
| Contratos de uma property | `contracts` | `(property_id)` |
| Reminders próximos | `reminders` | `(user_id, status, data_alvo)` |

---

## 7. Conexão com o parser (spec parcial)

O parser precisa ter comportamento definido para cada banco nos seguintes aspectos. Isso alimenta `parser_metodo` e `parser_issues`.

### O que o parser Itaú (v1) precisa cobrir

Com base no DDC real do contrato de referência:

| Dado | Localização no PDF | Tipo de extração |
|---|---|---|
| Número do contrato | Cabeçalho, linha "Contrato nº" | Regex `\d{11}` |
| Data de emissão | Cabeçalho, "Data de emissão" | Regex data |
| Saldo devedor | Tabela de resumo, "Saldo do contrato" | Coordenada + regex `R\$\s+[\d.,]+` |
| Taxa mensal | Seção de condições, "Taxa de juros mensal" | Regex percentual |
| Sistema | Seção de condições, "Sistema de amortização" | Keyword match |
| Parcelas (tabela) | Tabela de evolução | Row-by-row, colunas fixas |
| Operações históricas | Seção "Histórico de amortizações" | Row-by-row |
| CPF | Cabeçalho, "CPF do mutuário" | Regex `\d{3}\.\d{3}\.\d{3}-\d{2}` → redact |

### Validações semânticas obrigatórias (antes de persistir)

Independente do banco ou método de extração:

| Validação | Regra | Erro |
|---|---|---|
| Saldo positivo | `saldo_devedor > 0` | `SALDO_NEGATIVO` |
| Taxa mensal em range | `0.003 < taxa_mensal < 0.02` | `TAXA_FORA_DE_RANGE` |
| Prazo remanescente positivo | `prazo_remanescente > 0` | `PRAZO_INVALIDO` |
| Parcela coerente | `proxima_parcela_amortizacao + juros ≈ valor_total (± 5%)` | `PARCELA_INCOERENTE` |
| Saldo consistente | `saldo_pos_pagamento ≈ saldo_devedor - amortizacao (± 0.5%)` | `SALDO_INCONSISTENTE` |
| Data emissão razoável | `data_emissao` entre 2000 e hoje | `DATA_INVALIDA` |

Se 2+ validações falharem: parser retorna `parser_issues` populado e o sistema pede ao usuário para conferir manualmente.

---

## 8. O que deliberadamente não existe

| Ausente | Por quê |
|---|---|
| Tabela de "estado atual do contrato" | Derivado do motor. Cache persistente cria inconsistência |
| Coluna de resultado em `scenarios` | Calculado em runtime. Guardar seria stale |
| CPF em qualquer tabela | Nunca persiste — redactado no parser |
| URL de arquivo no banco | Apenas path + bucket. URL é gerada on-demand com assinatura |
| Coluna `senha` em user_profiles | Gerenciada inteiramente pelo auth provider |
| Histórico de sessões web | Fora do escopo — auth provider gerencia |
| Dados agregados de outros usuários | Isolamento por design. Sem views cross-user |

---

## Próximas decisões (conexão com spec do parser)

Este documento define o **contrato de saída** do parser. O próximo documento (`parser_01.md`) vai definir:

- [ ] Layout do DDC por banco (Itaú primeiro — maior base de usuários)
- [ ] Estratégia de coordenada vs. regex por seção
- [ ] Como o LLM fallback recebe o prompt (campo-por-campo ou documento inteiro?)
- [ ] Versionamento do parser — como migrar registros antigos quando o schema do DDC muda
- [ ] Testes de regressão — conjunto mínimo de DDCs reais para CI

O schema não muda quando o parser muda (contanto que o JSON de saída respeite o contrato). O parser muda quando o banco muda o layout, sem tocar no banco de dados.
