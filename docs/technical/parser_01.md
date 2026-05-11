# Marco Zero — Agente de Extração de DDC

> Documento de design — versão 1
> Data: 06/05/2026
> Status: em discussão
> Depende de: `motor_01.md` (JSON canônico), `schema_01.md` (persistência)
> Alimenta: `../ux/journey_01_onboarding.md` (telas 0.6a e 0.7)
> Mesma pasta: `technical/`

---

## Decisão de arquitetura

**Antes (descartado):** parsers determinísticos por banco + LLM como fallback.

**Agora:** um único agente de extração que recebe qualquer PDF de qualquer banco e produz o JSON canônico definido em `motor_01.md`.

### Por que

| Problema do parser por banco | Como o agente resolve |
|---|---|
| Quebra quando banco muda o layout | Agente lida com variação sem código novo |
| Precisa de um parser novo para cada banco | Funciona para qualquer banco desde o dia 1 |
| Alto custo de manutenção | Custo de manutenção praticamente zero |
| 5 bancos cobre ~80% do mercado | Cobertura de 100% do mercado |

### O que não muda

- O JSON canônico de saída é idêntico — o schema de `motor_01.md` é o contrato de output do agente
- As validações semânticas são idênticas — saldo positivo, taxa em range, parcela coerente
- A confirmação com o usuário (Tela 0.7) é idêntica — nada persiste sem user approval
- O motor de cálculo não sabe como os dados chegaram

---

## 1. Visão geral do agente

```
┌──────────────────────────────────────────────────────────────────┐
│                      Agente de Extração                          │
│                                                                  │
│  PDF do usuário                                                  │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │ Pré-processamento (sem LLM)                             │     │
│  │  - Extrair texto do PDF (pdfjs / pdf-parse)             │     │
│  │  - Detectar banco (keyword match)                       │     │
│  │  - Redactar PII: CPF, nome, agência, conta              │     │
│  └─────────────────────────────────────────────────────────┘     │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │ Passe 1 — Campos de Cabeçalho          [SONNET]  ~2s   │     │
│  │  Extrai: banco, contrato, sistema, taxas, saldo,        │     │
│  │  prazo, próxima parcela, última parcela                 │     │
│  │  Output: ExtractionHeader + excerpts + confiança        │     │
│  └─────────────────────────────────────────────────────────┘     │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │ Passe 2a — Anchor da Tabela            [SONNET]  ~2s   │     │
│  │  Primeiras 20 linhas + identificação de column_map      │     │
│  │  Output: parcelas[0..19] + ColumnMap (mapa de colunas)  │     │
│  └─────────────────────────────────────────────────────────┘     │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │ Passe 2b — Bulk da Tabela (N chunks)   [HAIKU]   ~2s   │     │
│  │  Linhas 21–420 em chunks de 50, usando column_map       │     │
│  │  Output: parcelas[20..N]                                │     │
│  │  Fallback automático para SONNET se schema inválido     │     │
│  └─────────────────────────────────────────────────────────┘     │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │ Passe 3 — Operações Históricas         [SONNET]  ~1s   │     │
│  │  Amortizações extraordinárias, pagamentos especiais     │     │
│  │  Output: operacoes_historicas[]                         │     │
│  └─────────────────────────────────────────────────────────┘     │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │ Confirmação Cruzada                    [HAIKU]  <0.5s  │     │
│  │  Passe 1 vs Passe 2: proxima_parcela bate com           │     │
│  │  parcelas[0]? prazo_remanescente == len(parcelas)?      │     │
│  └─────────────────────────────────────────────────────────┘     │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │ Validação Semântica (determinístico, <50ms)             │     │
│  │  SAC/PRICE math check — zero LLM                        │     │
│  └─────────────────────────────────────────────────────────┘     │
│       │                                                          │
│       ▼                                                          │
│  Resultado com confiança por campo + excerpts                    │
│  → UI para confirmação do usuário                                │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Por que 3 passes em vez de 1:**
- Contexto menor por chamada = menos alucinação, mais precisão
- Permite mostrar checkmarks em sequência na UI (UX desenhada no onboarding)
- Se o Passe 2 falhar (DDC não tem tabela de parcelas), Passes 1 e 3 ainda persistem
- Routing de modelo por custo de erro: campos críticos no modelo forte; extração repetitiva no modelo leve

---

## 2. Pré-processamento (sem LLM)

### 2.1 Extração de texto do PDF

```
extrair_texto(arquivo_pdf) → TextoEstruturado

TextoEstruturado {
  paginas:    PaginaTexto[]
  texto_flat: string          // concatenação com separadores de página
  tem_ocr:    boolean         // true se foi necessário OCR (PDF escaneado)
}

PaginaTexto {
  numero:   number
  texto:    string
  tem_tabelas: boolean       // heurística: linhas com múltiplas colunas
}
```

Ferramentas: `pdfjs-dist` para PDFs nativos. Se `tem_ocr = true` (PDF escaneado sem texto selecionável), usar Tesseract.js ou serviço OCR externo.

Importante: esta etapa roda **no servidor**, nunca no cliente. O PDF bruto não trafega para serviços externos além do LLM com ZDR.

### 2.2 Redação de PII

Antes de qualquer processamento downstream (incluindo LLM), substituir por tokens opacos:

```
redactar_pii(texto) → TextoRedactado

Substituições:
  CPF:     \d{3}\.\d{3}\.\d{3}-\d{2}  →  [CPF_REDACTED]
  CNPJ:    \d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}  →  [CNPJ_REDACTED]
  Agência: "Ag[ência]?\.?\s+\d{4}"  →  [AGENCIA_REDACTED]
  Conta:   "C[/c]\.?\s+\d{5,12}-\d"  →  [CONTA_REDACTED]
  Nome:    não redactar agora — extraído como campo mas nunca persistido
```

O arquivo redactado é o que vai para o LLM e para o storage.

`_meta.redaction_log` lista quais tokens foram encontrados e substituídos.

### 2.3 Detecção de banco (heurística, sem LLM)

Keyword matching no texto antes de chamar o LLM. Não é obrigatório — o agente funciona sem isso — mas quando detectado, inclui dicas no prompt do Passe 1 (ver seção 4).

```
detectar_banco(texto) → { banco_code: string | null, confianca: number }

Keywords por banco:
  'itau':     ["Itaú Unibanco", "ITAU UNIBANCO S.A.", "Demonstrativo Descritivo de Crédito"]
  'caixa':    ["Caixa Econômica Federal", "CAIXA ECONÔMICA FEDERAL", "SIAPI"]
  'bb':       ["Banco do Brasil", "BANCO DO BRASIL S.A."]
  'bradesco': ["Banco Bradesco", "BRADESCO S.A."]
  'santander':["Santander Brasil", "BANCO SANTANDER"]
```

---

## 3. Passe 1 — Campos de Cabeçalho

### Input do LLM

```
system_prompt: |
  Você extrai dados financeiros de documentos bancários brasileiros.
  
  REGRAS OBRIGATÓRIAS:
  1. Extraia APENAS valores que estão literalmente no documento.
     Nunca calcule, infira ou estime — se não encontrar, use null.
  2. Valores monetários: extraia como número decimal (R$ 429.629,87 → 429629.87).
  3. Taxas: extraia como decimal (0,9631393% → 0.009631393).
  4. Datas: extraia como ISO 8601 (21/05/2026 → "2026-05-21").
  5. NUNCA inclua CPF, nome, agência ou conta na extração.
  6. Para cada campo extraído, inclua o trecho exato do documento em `excerpts`.

  SCHEMA DE SAÍDA (JSON Schema):
  [schema do objeto ExtractionHeader abaixo]

  [DICAS DO BANCO se detectado — ver seção 4]

user_prompt: |
  Documento:
  ---
  [texto_flat redactado do PDF]
  ---
  Extraia os campos do cabeçalho conforme o schema.
```

### Schema de saída — `ExtractionHeader`

```json
{
  "contrato": {
    "banco": "string | null",
    "numero": "string | null",
    "modalidade": "string | null",
    "sistema_amortizacao": "SAC | PRICE | null",
    "taxa_referencial": "string | null"
  },
  "taxas": {
    "mensal": "number | null",
    "anual_efetiva": "number | null"
  },
  "snapshot": {
    "data_emissao": "date | null",
    "saldo_devedor": "number | null",
    "prazo_total_contratado": "number | null",
    "prazo_remanescente": "number | null",
    "valor_original": "number | null"
  },
  "proxima_parcela": {
    "numero": "number | null",
    "vencimento": "date | null",
    "valor_total": "number | null",
    "amortizacao": "number | null",
    "juros": "number | null",
    "mip": "number | null",
    "dfi": "number | null",
    "seguros_total": "number | null"
  },
  "ultima_parcela": {
    "numero": "number | null",
    "vencimento": "date | null",
    "valor_total": "number | null"
  },
  "excerpts": {
    "banco": "string | null",
    "taxa_mensal": "string | null",
    "saldo_devedor": "string | null",
    "proxima_parcela_valor": "string | null"
  },
  "confianca": {
    "overall": "number",
    "por_campo": {
      "taxa_mensal": "number",
      "saldo_devedor": "number"
    }
  }
}
```

**Por que `excerpts`:** cada valor extraído acompanha o trecho exato do documento onde foi encontrado. Na Tela 0.7 (confirmação), o usuário pode ver `"encontrado: 'Taxa de juros mensal: 0,9631393% a.m.'"` — elimina dúvida sobre se o sistema inventou o número.

**Por que `confianca`:** campos com `confianca < 0.7` ficam destacados na UI de confirmação com flag "verifique este campo". Não bloqueiam — o usuário confirma manualmente.

---

## 4. Dicas por banco (Bank Hints)

Não são parsers. São fragmentos de contexto injetados no system prompt quando o banco é detectado. Aumentam precisão sem criar dependência de layout.

```
hints['itau'] = """
  Banco: Itaú Unibanco.
  Documento típico: "Demonstrativo Descritivo de Crédito" (DDC).
  Taxa mensal está em seção "Dados do Contrato", linha "Taxa de Juros Mensal".
  Saldo devedor está em seção "Posição Atual", linha "Saldo do Contrato".
  Próxima parcela está em tabela "Próximos Vencimentos", primeira linha com situação "A VENCER".
  Parcelas históricas estão em tabela "Evolução do Financiamento".
  Amortizações extraordinárias estão em seção "Histórico de Amortizações".
  Sistema é sempre SAC para Carteira Hipotecária.
  Seguros MIP e DFI aparecem separados nas colunas da tabela de parcelas.
"""

hints['caixa'] = """
  Banco: Caixa Econômica Federal.
  Documento típico: extrato de financiamento SIAPI.
  ...
"""
```

**Política de manutenção:** hints são atualizados quando usuários reportam falhas de extração para um banco específico. A atualização de uma hint não é uma nova versão do agente — é uma atualização de dados.

---

## 5. Passe 2 — Tabela de Parcelas

Executado somente se `passe_1.snapshot.prazo_remanescente > 0` e `tem_tabelas = true` em pelo menos uma página.

### Estratégia: anchor → bulk em paralelo

```
// Passe 2a: Anchor (Sonnet)
anchor = sonnet(prompt_anchor, primeiras_20_linhas)
column_map = anchor.column_map    // "col_3 = amortizacao, col_4 = juros..."
parcelas = anchor.parcelas        // primeiras 20 linhas extraídas

// Passe 2b: Bulk paralelo (Haiku)
chunks_restantes = dividir_em_chunks(linhas[20:], tamanho=50)

resultados = await Promise.all(
  chunks_restantes.map(chunk =>
    haiku(prompt_bulk(column_map), chunk)
      .then(validar_chunk)
      .catch(() => sonnet(prompt_bulk(column_map), chunk))  // fallback
  )
)

parcelas.extend(...resultados)
// checkmark de progresso na UI a cada chunk completado
```

**Por que paralelo:** os chunks do bulk são independentes entre si — não há dependência de estado entre a linha 100 e a linha 150. Rodar em paralelo com Promise.all reduz latência de O(N chunks × 1s) para próximo de O(1s) com rate limiting do provider.

### Schema de saída — `ExtractionInstallment` (por parcela)

```json
{
  "numero": "number",
  "vencimento": "date",
  "situacao": "aberta | paga | futura",
  "valor_total": "number",
  "amortizacao": "number",
  "juros": "number",
  "mip": "number | null",
  "dfi": "number | null",
  "seguros_total": "number | null",
  "saldo_pos_pagamento": "number"
}
```

### Validação de completude

Após todos os chunks:

```
if len(parcelas_extraidas) != prazo_remanescente:
  → parser_issues.push({
      code: "PRAZO_INCONSISTENTE",
      esperado: prazo_remanescente,
      encontrado: len(parcelas_extraidas)
    })
```

Se diferença > 5%: flag para o usuário na confirmação. Se diferença ≤ 5%: aviso discreto (pode ser parcela final parcial ou parcela já paga no mesmo mês).

---

## 6. Passe 3 — Operações Históricas

Executado somente se o texto contém keywords como "Histórico de Amortizações", "Amortizações Realizadas", "Operações Extraordinárias".

### Schema de saída — `ExtractionOperation` (por operação)

```json
{
  "tipo": "amortizacao_extraordinaria | pagamento_especial | outro",
  "data": "date",
  "valor_principal": "number",
  "juros_pro_rata": "number | null",
  "atualizacao_monetaria": "number | null",
  "valor_total_debitado": "number | null",
  "modalidade": "reducao_prazo | reducao_parcela | null",
  "fonte": "recurso_proprio | fgts | ambos | null"
}
```

---

## 7. Validação semântica (determinístico)

Idêntica às regras de `motor_01.md §6 "Validações antes de aceitar o JSON"`. Roda após os 3 passes, antes de apresentar ao usuário.

```
validar(extracao_completa) → ValidationResult

ValidationResult {
  passou:  boolean
  issues:  ValidationIssue[]
}

ValidationIssue {
  code:     string          // 'SALDO_INVALIDO', 'TAXA_FORA_DE_RANGE', ...
  campo:    string
  valor:    any
  mensagem: string          // em português, para mostrar ao usuário
  bloqueia: boolean         // true = não pode persistir sem correção manual
}
```

**Regras:**

| Regra | Código | Bloqueia? |
|---|---|---|
| `saldo_devedor > 0` | `SALDO_INVALIDO` | Sim |
| `0.003 < taxa_mensal < 0.018` | `TAXA_FORA_DE_RANGE` | Sim |
| `prazo_remanescente > 0` | `PRAZO_INVALIDO` | Sim |
| `abs(amort + juros + seguros - total) < 0.10` | `PARCELA_INCOERENTE` | Sim |
| `saldo_pos < saldo_devedor` | `SALDO_NAO_DECRESCE` | Sim |
| `len(parcelas) == prazo_remanescente` | `PRAZO_INCONSISTENTE` | Não |
| `data_emissao` entre 2000 e hoje | `DATA_INVALIDA` | Sim |
| Confiança de campo crítico < 0.7 | `BAIXA_CONFIANCA` | Não |

Regras com `bloqueia = false` geram aviso, não bloqueio. O usuário vê e decide.

---

## 8. Confirmação com o usuário (Tela 0.7 estendida)

A Tela 0.7 do onboarding (`../ux/journey_01_onboarding.md`) já descreve o fluxo de conferência. Aqui, o detalhe de como os dados chegam lá.

### O que a UI recebe do agente

```json
{
  "status": "ok | com_avisos | requer_revisao",
  "campos_criticos": {
    "banco": {
      "valor": "itau",
      "excerpt": "Itaú Unibanco S.A. — Demonstrativo Descritivo de Crédito",
      "confianca": 0.99
    },
    "taxa_mensal": {
      "valor": 0.009631393,
      "excerpt": "Taxa de Juros Mensal: 0,9631393% a.m.",
      "confianca": 0.99
    },
    "saldo_devedor": {
      "valor": 429629.87,
      "excerpt": "Saldo do Contrato: R$ 429.629,87",
      "confianca": 0.99
    },
    "prazo_remanescente": {
      "valor": 189,
      "excerpt": "Prazo Remanescente: 189 meses",
      "confianca": 0.97
    }
  },
  "issues": [],
  "parcelas_extraidas": 189,
  "operacoes_extraidas": 6
}
```

### Como a UI renderiza

```
┌──────────────────────────────────────────────────────────┐
│  Confere o que encontramos:                              │
│                                                          │
│  Banco         Itaú Unibanco              ✓ 99%          │
│                "Itaú Unibanco S.A. —                     │
│                 Demonstrativo..."          [ver trecho]   │
│                                                          │
│  Saldo         R$ 429.629,87              ✓ 99%          │
│                "Saldo do Contrato:                        │
│                 R$ 429.629,87"             [ver trecho]   │
│                                                          │
│  Taxa          0,9631% a.m. (12,19% a.a.) ✓ 99%          │
│                "Taxa de Juros Mensal:                     │
│                 0,9631393% a.m."           [ver trecho]   │
│                                                          │
│  Parcelas restantes  189                  ✓ 97%          │
│                                                          │
│  189 parcelas mapeadas                                   │
│  6 operações históricas encontradas                      │
│                                                          │
│  ─────────────────────────────────────                   │
│  ⓘ Algum valor errado? Edite antes de salvar.            │
│                                                          │
│  [ Editar valores ]    [ Tudo certo, guardar ]           │
└──────────────────────────────────────────────────────────┘
```

**Campos com confiança baixa (< 0.7):**

```
┌──────────────────────────────────────────────────────────┐
│  ⚠  Prazo remanescente   [         ]   ← verifique       │
│     Não encontramos esse campo com clareza.              │
│     Consulte seu app do banco.                           │
└──────────────────────────────────────────────────────────┘
```

---

## 9. Persistência condicional

O agente nunca persiste diretamente. O fluxo completo:

```
Agente extrai → UI apresenta → Usuário confirma → Backend persiste

Regras:
  - Se há issues bloqueantes não resolvidos: botão "guardar" desabilitado
  - Se usuário editou campo manualmente: `confianca[campo] = 1.0` (usuário é fonte)
  - Campos que o usuário não editou: mantêm confiança original
  - `parser_metodo = 'agent'` sempre (independente de quantos passes rodaram)
  - `parser_version_id` → versão do agente atual em `ref_parser_versions`
```

---

## 10. Impacto no schema_01.md

| Tabela | Campo | Mudança |
|---|---|---|
| `ddc_snapshots` | `parser_metodo` | Valores: `'agent'` \| `'manual'` (remover `'deterministic'` e `'llm'`) |
| `ddc_snapshots` | `parser_version_id` | FK → `ref_parser_versions`; agora rastreia versão do agente |
| `ddc_snapshots` | `extraction_confianca` | `jsonb nullable` — confiança por campo após confirmação do usuário |
| `ref_parser_versions` | `bank_id` | Tornar `nullable` — agente não é específico por banco |
| `ref_parser_versions` | `method` | Valor: `'agent'` (remover `'deterministic'` e `'llm'`) |
| `ref_banks` | `has_ddc_parser` | Renomear para `has_extraction_hints` — indica se temos hints que melhoram precisão |

---

## 11. Gestão de versões do agente

Versão do agente = combinação de `(modelo_llm, system_prompt_hash, hints_hash)`. Quando qualquer um muda, uma nova entrada em `ref_parser_versions` é criada.

```
ref_parser_versions seed (agente):
  bank_id:       null
  version_code:  'agent_v1.0'
  method:        'agent'
  released_at:   2026-XX-XX
  changelog:     "Versão inicial. Suporte a todos os bancos via extração agnóstica."
```

**Por que rastrear versão do agente:** se o modelo LLM mudar e a extração melhorar (ou regredir), é possível identificar quais DDCs foram extraídos com qual versão e reprocessar em batch se necessário. Mesma lógica de antes, mas agora por versão de agente em vez de versão de parser por banco.

---

## 12. Casos de borda

### PDF escaneado (imagem, sem texto selecionável)

```
if tem_ocr_necessario:
  → aplicar OCR (Tesseract.js local ou serviço externo)
  → _meta.ocr_usado = true
  → confiança geral penalizada em 10% (OCR introduz erros de leitura)
  → avisar o usuário: "Este PDF não tem texto digital. A extração pode ter imprecisões."
```

### PDF protegido por senha

```
if pdf_protegido:
  → retornar erro imediato: "Este PDF está protegido. 
    Abra-o no app do banco, exporte como PDF sem senha, e tente novamente."
```

### PDF que não é DDC

```
if nenhum_campo_critico_encontrado:
  → retornar:
    "Não conseguimos identificar este documento como um DDC.
     Pode ser um extrato, boleto ou outro documento bancário.
     Quer tentar outro arquivo ou inserir os dados manualmente?"
```

### Banco não detectado (sem hints)

```
if banco_code == null:
  → agente funciona normalmente sem hints
  → _meta.banco_detectado = false
  → confiança do campo 'banco' é derivada da extração, não da detecção
```

---

## 13. Estratégia de modelos por camada

### Princípio de roteamento

> Roteie pelo **custo de erro**, não pelo custo de token.

Um erro no Passe 1 (taxa mensal errada) invalida todos os cálculos do contrato. Um erro em uma linha do Passe 2 bulk é detectado pela validação semântica e pode ser re-extraído no fallback. Essa assimetria justifica modelos diferentes.

### Tabela de decisão

| Etapa | Modelo | Justificativa | Custo por DDC |
|---|---|---|---|
| Passe 1 (cabeçalho) | **Sonnet** | Campos não-repetitivos, custo de erro altíssimo, contexto pequeno (~2 páginas) | ~$0.003 |
| Passe 2a (anchor 20 linhas) | **Sonnet** | Estabelece o `column_map` — erro aqui contamina todas as 400 linhas seguintes | ~$0.003 |
| Passe 2b (bulk, chunks de 50) | **Haiku** | Estrutura repetitiva e conhecida; column_map já estabelecido; validação determinística fecha o gap | ~$0.004 total |
| Passe 3 (operações históricas) | **Sonnet** | Semi-estruturado, contexto pequeno, impacto direto na reconciliação | ~$0.002 |
| Confirmação cruzada | **Haiku** | Classificação binária (bate / não bate), não extração | ~$0.001 |
| **Total por DDC** | | | **~$0.013** |

### Estimativa de custo anual

```
10.000 usuários × 6 DDCs/ano = 60.000 DDCs/ano
60.000 × $0.013 = $780/ano (~R$ 4.000/ano)
```

Irrelevante comparado ao CAC e ao valor entregue. Com todo Opus: ~$3.000/ano — ainda irrelevante, mas 4× maior sem benefício proporcional.

---

### Por que o Haiku funciona no bulk

A tarefa do Passe 2b não é "entender o documento". É "aplique este mapeamento a estas linhas":

```
PROMPT HAIKU (bulk):
  Mapeamento estabelecido:
    col_1 = numero_parcela
    col_2 = vencimento (DD/MM/AAAA)
    col_3 = valor_total (R$ X.XXX,XX)
    col_4 = amortizacao
    col_5 = juros
    col_6 = mip
    col_7 = dfi
    col_8 = saldo_pos_pagamento
    col_9 = situacao (A VENCER / PAGO)

  Extraia as linhas abaixo neste formato JSON. 
  Valores monetários como número decimal. Datas como YYYY-MM-DD.
  Se uma coluna estiver vazia, use null.
  Responda APENAS com o array JSON, sem texto adicional.

  LINHAS:
  [texto das 50 linhas]
```

Este prompt funciona bem no Haiku porque:
1. Zero ambiguidade — o mapeamento já foi estabelecido pelo Sonnet
2. Saída estritamente estruturada — sem raciocínio, sem explicação
3. Valores são cópia direta do texto — não há inferência

### Fallback automático por chunk

Cada chunk do Passe 2b passa por validação imediata após a resposta do Haiku:

```
validar_chunk(chunk_resultado, column_map):
  para cada parcela em chunk_resultado:
    se amortizacao + juros + seguros - valor_total > 0.10:
      → chunk inválido
    se numero_parcela não sequencial:
      → chunk inválido
    se saldo_pos_pagamento <= 0:
      → chunk inválido
  
  se chunk inválido:
    → re-extrair com SONNET (1 retry)
    → se ainda inválido: marcar como `baixa_confianca`, continuar
```

Na prática, fallbacks para Sonnet devem ser raros (<5% dos chunks) porque a estrutura de tabela bancária é altamente regular.

### Prompt de Confirmação Cruzada (Haiku)

Depois de todos os passes, uma única chamada Haiku verifica consistência entre eles:

```
PROMPT HAIKU (confirmação cruzada):
  Dados extraídos:
  - Passe 1: prazo_remanescente = 189, proxima_parcela = {numero: 5, valor: 6578.27}
  - Passe 2: 189 parcelas extraídas, parcelas[0] = {numero: 5, valor_total: 6578.27}
  - Passe 3: 6 operações extraídas

  Responda em JSON:
  {
    "prazo_vs_parcelas": "ok | divergente",
    "proxima_parcela_vs_array": "ok | divergente",
    "notas": "string | null"
  }
```

Qualquer `divergente` eleva o campo correspondente para `baixa_confianca` na UI de confirmação, pedindo que o usuário verifique.

---

### Decisão de modelo por contexto do produto

Além do agente de extração, o produto usa LLM em outros lugares. Tabela de roteamento completa:

| Feature | Modelo | Razão |
|---|---|---|
| Passe 1 extração | Sonnet | Crítico, contexto pequeno |
| Passe 2b bulk | Haiku | Repetitivo, estruturado, validação fecha gap |
| Passe 3 operações | Sonnet | Semi-estruturado, importante |
| Confirmação cruzada | Haiku | Classificação simples |
| IA Chat (Tool calls) | Sonnet | Equilíbrio qualidade/custo; Tools reduzem erro |
| Explicação de resultado complexo | Sonnet | Qualidade de linguagem importa |
| Sugestões rápidas do Coach | Haiku | Template-like, contexto pequeno |
| Extração de campos de PDFs escaneados (OCR) | Sonnet | Qualidade crítica, texto ruidoso |

---

## 14. Trade-offs documentados

| Trade-off | Decisão | Raciocínio |
|---|---|---|
| Latência (~5–7s total) vs. precisão | Aceitar a latência | DDC é importado poucas vezes por ano. Checkmarks em sequência na UI tornam a espera tolerável |
| Custo LLM por DDC (~$0.013) | Aceitar | 10k usuários × 6 DDCs/ano = ~$780/ano. Irrelevante vs. CAC. Tiered model reduz custo em 4× vs. todo-Opus |
| Privacidade (dados ao LLM) | Mitigado | Redaction antes do envio. ZDR contratual com Anthropic. Documentado na política de privacidade |
| Não-determinismo | Aceito + mitigado | User validation é o gate final. Versão do agente rastreada para reprodutibilidade. Haiku só confirma, não extrai criticamente |
| PDFs escaneados | Degradação graciosa | OCR com aviso. Usuário tem entrada manual como fallback sempre disponível |
| Fallback Haiku → Sonnet | Raro mas automático | Validação semântica detecta chunks inválidos e re-extrai com Sonnet. Esperado em < 5% dos chunks |
| Chunks paralelos vs. sequenciais | Paralelo | Os N chunks do Passe 2b são independentes entre si. Rodar em paralelo reduz latência de O(N) para O(1) com rate limiting |

---

## 15. O que o `parser_01.md` NÃO precisa mais

Com a abordagem agnóstica, os seguintes itens do planejamento original foram descartados:

- ~~Spec de coordenadas por seção do DDC Itaú~~
- ~~Regex específico por campo por banco~~
- ~~Estratégia de fallback parser → LLM~~
- ~~Manutenção de parsers quando banco muda layout~~

O único artefato "por banco" que resta são as **hints** — fragmentos de texto que melhoram precisão e podem ser atualizados sem deploy.
