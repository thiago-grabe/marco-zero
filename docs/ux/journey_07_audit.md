# Marco Zero — Jornada 7: Audit

> **Objetivo**: provar que a matemática bate, e dar ao usuário transparência total sobre o que aconteceu.
> **Princípio guia**: audit é a feature **menos sexy e mais defensável** do produto. É o que separa Marco Zero de qualquer simulador.

---

## Modelo mental do usuário

> "Quero ver tudo o que aconteceu, em ordem, sem mistério. Quero poder discutir com o gerente do banco com dado na mão."

Audit é a feature que a maioria dos usuários **nunca abre**. Mas saber que ela existe é o que gera confiança. E os 10% de power users que abrem viram fãs do produto pela vida inteira.

---

## Princípios duros

1. **Tudo é registrado.** Cada DDC importado, cada amortização declarada, cada cenário criado, cada interação com IA, cada acesso à conta.
2. **Nada é apagado por padrão.** Histórico é imutável dentro do prazo de retenção. Edição preserva versão anterior.
3. **Reconciliação automática.** Marco Zero compara o que esperava com o que o banco registra. Diferenças são sinalizadas, não escondidas.
4. **Tudo exportável.** Linha do tempo, reconciliação, logs — em PDF e CSV.
5. **Zero adornos.** Tom técnico-frio. Audit não tenta ser bonito — tenta ser inquestionável.

---

## Tela 7.1 — Audit (visão principal)

```
┌──────────────────────────────────────────────────────────┐
│  Apartamento Contagem ▾                                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Audit                                                   │
│                                                          │
│  Tudo o que aconteceu com este contrato.                 │
│                                                          │
│  ─── Seções ───────────────────────────────────          │
│                                                          │
│  ▼ Linha do tempo (24 eventos)                           │
│  ▸ Reconciliação                                         │
│  ▸ DDCs guardados (3 versões)                            │
│  ▸ Cenários (3 ativos, 2 arquivados)                     │
│  ▸ Acessos à conta (12 nos últimos 30 dias)              │
│  ▸ Interações com IA (8 nos últimos 30 dias)             │
│                                                          │
│  ─── Linha do tempo ───────────────────────────          │
│                                                          │
│  ┌──────────────────────────────────────────────┐        │
│  │ 05/05/2026 — DDC importado (v3)              │        │
│  │ Saldo: R$ 429.629,87                         │        │
│  │ Diff vs esperado: R$ 0,00 ✓                  │        │
│  │ [Ver DDC]  [Ver diff vs v2]                  │        │
│  └──────────────────────────────────────────────┘        │
│                                                          │
│  ┌──────────────────────────────────────────────┐        │
│  │ 28/04/2026 — Amortização R$ 80.000           │        │
│  │ Modalidade: Redução de prazo                 │        │
│  │ Juros pró-rata: R$ 178,73                    │        │
│  │ Atualização monetária: R$ 31,35              │        │
│  │ Total desembolsado: R$ 80.210,08             │        │
│  │ [Comprovante]                                │        │
│  └──────────────────────────────────────────────┘        │
│                                                          │
│  ┌──────────────────────────────────────────────┐        │
│  │ 21/04/2026 — Parcela #4 paga                 │        │
│  │ Valor: R$ 6.594,12                           │        │
│  │ Detalhamento:                                │        │
│  │   amort 1.511,77 + juros 4.935,99            │        │
│  │   + MIP 107,82 + DFI 38,54                   │        │
│  │ Saldo após: R$ 510.977,65                    │        │
│  └──────────────────────────────────────────────┘        │
│                                                          │
│  ┌──────────────────────────────────────────────┐        │
│  │ 25/03/2026 — Amortização R$ 5.000            │        │
│  │ Modalidade: Redução de prazo                 │        │
│  │ Juros pró-rata: R$ 6,18                      │        │
│  └──────────────────────────────────────────────┘        │
│                                                          │
│  [ Mostrar mais ]                                        │
│                                                          │
│  ...                                                     │
│                                                          │
│  ┌──────────────────────────────────────────────┐        │
│  │ 03/12/2025 — Contrato implantado             │        │
│  │ Valor original: R$ 536.000,00                │        │
│  │ Prazo original: 360 meses (até 12/2055)      │        │
│  │ Sistema: SAC                                  │        │
│  │ Taxa: 12,19% a.a.                            │        │
│  └──────────────────────────────────────────────┘        │
│                                                          │
│  [ Exportar linha do tempo (PDF / CSV) ]                 │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Seções colapsáveis.** Tudo cabe numa tela. Usuário expande o que interessa.
- **Linha do tempo cronológica reversa.** Mais recente no topo.
- **Cada evento é card uniforme.** Tipo + data + dados + ações.
- **Exportação no rodapé.** PDF para humano, CSV para Excel/dashboards.

---

## Tela 7.2 — Reconciliação

A feature **única** de Marco Zero. Compara o esperado com o real e mostra a matemática.

```
┌──────────────────────────────────────────────────────────┐
│  ←  Reconciliação                                        │
│                                                          │
│  Comparando o que o Marco Zero calcula com o que         │
│  o banco declara.                                        │
│                                                          │
│  Última verificação: 05/05/2026                          │
│  Status: ✓ Tudo bate                                     │
│                                                          │
│  ─── Saldo atual ───────────────────────────────         │
│                                                          │
│  Saldo esperado (Marco Zero)    R$ 429.629,87            │
│  Saldo declarado (DDC Itaú)     R$ 429.629,87            │
│  Diferença                      R$ 0,00 ✓                │
│                                                          │
│  ─── Memória de cálculo ───────────────────────          │
│                                                          │
│  Como Marco Zero chegou em R$ 429.629,87:                │
│                                                          │
│  Saldo após parcela #4 (DDC 26/04)    R$ 510.977,65     │
│  + Juros pró-rata 21/04 a 28/04        R$    178,73     │
│  + Atualização monetária 21/04 a 28/04 R$     31,35     │
│  − Amortização extra 28/04             R$ 80.000,00     │
│  ─────────────────────────────────────                   │
│  = Saldo após operação                 R$ 431.187,73     │
│                                                          │
│  + Correção monetária 28/04 a 21/05    R$    727,16     │
│  − Amortização parcela #5              R$  2.285,02     │
│  ─────────────────────────────────────                   │
│  = Saldo após parcela #5               R$ 429.629,87 ✓   │
│                                                          │
│  ─── Histórico de reconciliações ──────────────          │
│                                                          │
│  05/05/2026  ✓ R$ 0,00                                   │
│  28/04/2026  ✓ R$ 0,00                                   │
│  29/04/2026  ⚠ R$ 4,17 (correção monetária)              │
│              Esclarecido em 29/04                        │
│  29/03/2026  ✓ R$ 0,00                                   │
│                                                          │
│  [ Recalcular agora ]    [ Exportar memória ]            │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Tela quando há divergência:

```
┌──────────────────────────────────────────────────────────┐
│  ←  Reconciliação                                        │
│                                                          │
│  Status: ⚠ Diferença detectada                           │
│                                                          │
│  ─── Saldo atual ───────────────────────────────         │
│                                                          │
│  Saldo esperado (Marco Zero)    R$ 425.617,42            │
│  Saldo declarado (DDC Itaú)     R$ 426.851,98            │
│  Diferença                      R$ 1.234,56              │
│                                                          │
│  ─── Possíveis causas ─────────────────────────          │
│                                                          │
│  1. TR aplicada diferente do esperado                    │
│     • Marco Zero usa TR projetada                        │
│     • Banco usa TR efetiva publicada                     │
│     • Variações típicas: ±0,1% a 0,3% por mês            │
│     • Para saldo de R$ 426k, isso pode dar de            │
│       R$ 426 a R$ 1.278 — bate com a diferença           │
│                                                          │
│  2. Operação não registrada                              │
│     • Você fez alguma amortização que não declarou       │
│       no Marco Zero?                                     │
│                                                          │
│  3. Erro do banco (raro)                                 │
│     • Parcela cobrada errada, valor de juros             │
│       calculado errado                                   │
│                                                          │
│  ─── O que fazer ───────────────────────────────         │
│                                                          │
│  Se você acha que é correção monetária:                  │
│  [ Marcar como esclarecido — TR diferente ]              │
│                                                          │
│  Se você fez operação não declarada:                     │
│  [ Registrar operação retroativa ]                       │
│                                                          │
│  Se quer investigar com o banco:                         │
│  [ Marcar como em investigação ]                         │
│  [ Gerar carta para o banco ]                            │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Memória de cálculo aberta.** Linha por linha, com referência a operações.
- **Histórico de reconciliações.** Algumas têm diferença pequena por TR — fica registrado e esclarecido.
- **Ação "gerar carta para o banco"** é diferencial grande — gera texto pronto explicando a discrepância e o que o usuário quer que o banco verifique.

---

## Tela 7.3 — DDCs guardados

```
┌──────────────────────────────────────────────────────────┐
│  ←  DDCs guardados                                       │
│                                                          │
│  3 versões guardadas. PDFs originais preservados.        │
│                                                          │
│  ─── Versões ──────────────────────────────────          │
│                                                          │
│  ┌──────────────────────────────────────────────┐        │
│  │ v3 — 05/05/2026                              │        │
│  │                                              │        │
│  │ Saldo: R$ 429.629,87                         │        │
│  │ Parcelas restantes: 189                      │        │
│  │ Última parcela: 21/01/2042                   │        │
│  │                                              │        │
│  │ [Ver PDF]  [Baixar PDF]  [Ver diff vs v2]    │        │
│  └──────────────────────────────────────────────┘        │
│                                                          │
│  ┌──────────────────────────────────────────────┐        │
│  │ v2 — 29/04/2026                              │        │
│  │                                              │        │
│  │ Saldo: R$ 431.187,73                         │        │
│  │ Parcelas restantes: 189                      │        │
│  │ Última parcela: 21/01/2042                   │        │
│  │                                              │        │
│  │ [Ver PDF]  [Baixar PDF]  [Ver diff vs v1]    │        │
│  └──────────────────────────────────────────────┘        │
│                                                          │
│  ┌──────────────────────────────────────────────┐        │
│  │ v1 — 26/04/2026                              │        │
│  │                                              │        │
│  │ Saldo: R$ 510.977,65                         │        │
│  │ Parcelas restantes: 338                      │        │
│  │ Última parcela: 21/06/2054                   │        │
│  │                                              │        │
│  │ [Ver PDF]  [Baixar PDF]                      │        │
│  └──────────────────────────────────────────────┘        │
│                                                          │
│  + Adicionar nova versão                                 │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Tela 7.3.1 — Diff entre DDCs

```
┌──────────────────────────────────────────────────────────┐
│  ←  Diff: v2 (29/04) vs v3 (05/05)                       │
│                                                          │
│  ─── Mudou ────────────────────────────────────          │
│                                                          │
│  Saldo devedor                                           │
│   v2: R$ 431.187,73                                      │
│   v3: R$ 429.629,87                                      │
│   Δ: −R$ 1.557,86 (parcela #5 paga)                      │
│                                                          │
│  ─── Não mudou ────────────────────────────────          │
│                                                          │
│  Taxa: 12,19% a.a. ✓                                     │
│  Sistema: SAC ✓                                          │
│  Última parcela: 21/01/2042 ✓                            │
│  Parcelas restantes: 189 ✓                               │
│                                                          │
│  ─── Operações entre as versões ───────────────          │
│                                                          │
│  • 21/05/2026: Parcela #5 paga                           │
│    R$ 6.578,27 (amort 2.285,27 + juros 4.159,94          │
│    + MIP 94,45 + DFI 38,61)                              │
│                                                          │
│  ─── Resultado ────────────────────────────────          │
│                                                          │
│  ✓ Tudo consistente. Diferença explicada apenas          │
│    pela parcela paga.                                    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **PDF original sempre acessível.** Imutável.
- **Diff inteligente.** Mostra o que mudou, o que não mudou, e por quê.
- **Resultado validado.** Se a diferença é explicada por operações conhecidas, marca consistente.

---

## Tela 7.4 — Acessos à conta

```
┌──────────────────────────────────────────────────────────┐
│  ←  Acessos à conta                                      │
│                                                          │
│  Quem entrou na sua conta nos últimos 30 dias.           │
│                                                          │
│  ─── Hoje ─────────────────────────────────────          │
│                                                          │
│  13:42  Belo Horizonte, MG          Chrome/macOS         │
│         IP: 187.65.xx.xx (mascarado)                     │
│         [Detalhes]  [Não fui eu]                         │
│                                                          │
│  ─── Ontem ────────────────────────────────────          │
│                                                          │
│  09:17  Belo Horizonte, MG          iOS App / iPhone     │
│  22:04  Belo Horizonte, MG          Chrome/macOS         │
│                                                          │
│  ─── 04/05/2026 ────────────────────────────────         │
│                                                          │
│  10:22  Belo Horizonte, MG          Chrome/macOS         │
│  18:31  Belo Horizonte, MG          iOS App / iPhone     │
│                                                          │
│  ─── 03/05/2026 ────────────────────────────────         │
│                                                          │
│  14:08  Belo Horizonte, MG          Chrome/macOS         │
│                                                          │
│  ...                                                     │
│                                                          │
│  ─────────────────────────────────────                   │
│                                                          │
│  ⚠ Encerrar todas as sessões ativas                      │
│  Útil se você usou um computador público                 │
│                                                          │
│  [ Encerrar sessões ]                                    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Tela 7.4.1 — "Não fui eu"

```
┌──────────────────────────────────────────────────────────┐
│  ⚠  Acesso suspeito reportado                            │
│                                                          │
│  Marco Zero vai:                                         │
│  ✓ Encerrar todas as sessões ativas                      │
│  ✓ Bloquear novo login por 24 horas                      │
│  ✓ Forçar você a redefinir senha (e MFA se ativo)        │
│  ✓ Notificar nosso DPO para investigar                   │
│  ✓ Te enviar um e-mail com instruções                    │
│                                                          │
│  Você pode reverter isso em até 1 hora caso tenha        │
│  reportado por engano.                                   │
│                                                          │
│  [ Confirmar reporte ]    [ Cancelar ]                   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **IP mascarado** parcialmente — útil para reconhecer região, sem expor IP completo.
- **"Não fui eu"** é botão de pânico que faz coisas concretas. Não é decoração.
- **Reverter em 1 hora** previne acidente.

---

## Tela 7.5 — Interações com IA

```
┌──────────────────────────────────────────────────────────┐
│  ←  Interações com IA                                    │
│                                                          │
│  8 conversas nos últimos 30 dias.                        │
│                                                          │
│  ⓘ Conversas mais antigas que 30 dias são apagadas       │
│    automaticamente. Você pode apagar antes a qualquer    │
│    momento.                                              │
│                                                          │
│  ─── Histórico ────────────────────────────────          │
│                                                          │
│  06/05  14:23  "Vale a pena portar pro Caixa?"           │
│                Modelo: Claude (Anthropic)                │
│                Dados enviados: saldo, taxa, prazo        │
│                Dados redacted: nome, conta, agência      │
│                [Ver conversa]  [Ver dados enviados]      │
│                                                          │
│  06/05  10:08  "Quanto economizo amortizando 30k?"       │
│                [Ver conversa]  [Ver dados enviados]      │
│                                                          │
│  04/05  19:47  "Quando devo usar FGTS?"                  │
│                [Ver conversa]  [Ver dados enviados]      │
│                                                          │
│  ...                                                     │
│                                                          │
│  ─────────────────────────────────────                   │
│                                                          │
│  [ Apagar todas ]    [ Exportar histórico ]              │
│                                                          │
│  [ Desativar IA ]    Não enviar mais dados a LLMs        │
│                      externos                            │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Tela 7.5.1 — "Ver dados enviados"

```
┌──────────────────────────────────────────────────────────┐
│  ←  Dados enviados ao LLM                                │
│                                                          │
│  Pergunta: "Vale a pena portar pro Caixa?"               │
│  Data: 06/05/2026 às 14:23                               │
│  Provedor: Anthropic (Zero Data Retention)               │
│                                                          │
│  ─── Dados enviados ───────────────────────────          │
│                                                          │
│  saldo_devedor:           429629.87                      │
│  taxa_anual_efetiva:      0.1219                         │
│  taxa_mensal:             0.009631393                    │
│  prazo_remanescente:      189                            │
│  sistema_amortizacao:     "SAC"                          │
│  pergunta_usuario:        "Vale a pena portar pro Caixa?"│
│  resultado_calculo:       (objeto com simulações)        │
│                                                          │
│  ─── Dados NÃO enviados ───────────────────────          │
│                                                          │
│  ✓ Seu nome                                              │
│  ✓ CPF (já não é armazenado)                             │
│  ✓ Conta bancária                                        │
│  ✓ Agência                                               │
│  ✓ Número de contrato bancário                           │
│  ✓ Endereço de IP                                        │
│  ✓ Outros contratos da sua conta                         │
│                                                          │
│  ─── Política do provedor ─────────────────────          │
│                                                          │
│  Anthropic não usa esses dados para treinar              │
│  modelos. Contrato Zero Data Retention.                  │
│  [Política Anthropic]                                    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Dados enviados são literais.** Mesmo formato técnico, sem floreios.
- **Lista de NÃO enviados é tão importante quanto enviados.**
- **Link para política do provedor.** Auditável externamente.

---

## Tela 7.6 — Carta para o banco (gerada)

Quando o usuário aciona "Gerar carta para o banco" na reconciliação:

```
┌──────────────────────────────────────────────────────────┐
│  ←  Carta para o banco                                   │
│                                                          │
│  Marco Zero pode gerar um documento explicando a         │
│  divergência detectada. Ele serve como ponto de          │
│  partida para discutir com o banco — você revisa,        │
│  ajusta, e envia (não geramos correspondência            │
│  automaticamente).                                       │
│                                                          │
│  ─── Documento gerado ─────────────────────────          │
│                                                          │
│  Para: Itaú Unibanco — Carteira Hipotecária              │
│  Assunto: Solicitação de esclarecimento — Contrato       │
│  10300539502                                             │
│                                                          │
│  Prezados,                                               │
│                                                          │
│  Identifiquei uma divergência entre o saldo devedor      │
│  apresentado no DDC de 05/05/2026 (R$ 426.851,98) e o    │
│  saldo esperado conforme histórico de operações          │
│  (R$ 425.617,42), totalizando uma diferença de           │
│  R$ 1.234,56.                                            │
│                                                          │
│  Histórico considerado:                                  │
│   • Saldo após parcela #4 (DDC 26/04): R$ 510.977,65    │
│   • Amortização extra 28/04 de R$ 80.000,00             │
│   • Juros pró-rata 21/04 a 28/04: R$ 178,73             │
│   • Atualização monetária declarada: R$ 31,35           │
│   • Parcela #5 (DDC 05/05): amort R$ 2.285,27           │
│                                                          │
│  Solicito esclarecimento sobre:                          │
│   1. Aplicação da TR no período                          │
│   2. Eventuais correções monetárias adicionais          │
│   3. Confirmação de que todas as operações foram        │
│      registradas                                          │
│                                                          │
│  Aguardo retorno em até 5 dias úteis, conforme           │
│  resolução do Banco Central.                             │
│                                                          │
│  Atenciosamente,                                         │
│  Thiago Meireles Grabe                                   │
│  Contrato: 10300539502                                   │
│                                                          │
│  ─────────────────────────────────────                   │
│                                                          │
│  [ Editar texto ]  [ Baixar PDF ]  [ Copiar texto ]      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Marco Zero gera ponto de partida**, não envia automaticamente.
- **Texto é editável.** Usuário ajusta antes de mandar.
- **Cita resolução do BC.** Direito do consumidor reforçado.

---

## Tela 7.7 — Exportação total

```
┌──────────────────────────────────────────────────────────┐
│  ←  Exportar dados deste contrato                        │
│                                                          │
│  Você pode exportar tudo o que está guardado sobre       │
│  este contrato a qualquer momento. Direito de            │
│  portabilidade da LGPD.                                  │
│                                                          │
│  ─── O que vai ser exportado ──────────────────          │
│                                                          │
│  ✓ DDCs originais em PDF (3 versões)                     │
│  ✓ Linha do tempo completa em PDF e CSV                  │
│  ✓ Cenários salvos em JSON estruturado                   │
│  ✓ Reconciliações em CSV                                 │
│  ✓ Logs de IA em JSON                                    │
│  ✓ Logs de acesso à conta em CSV                         │
│  ✓ Notas livres em texto plano                           │
│                                                          │
│  ─── Formato ──────────────────────────────────          │
│                                                          │
│  Tudo será compactado em um arquivo ZIP com              │
│  estrutura:                                              │
│                                                          │
│   marco_zero_export_<data>/                              │
│   ├─ ddcs/                                               │
│   │   ├─ ddc_v1_2026-04-26.pdf                           │
│   │   ├─ ddc_v2_2026-04-29.pdf                           │
│   │   └─ ddc_v3_2026-05-05.pdf                           │
│   ├─ linha_do_tempo.pdf                                  │
│   ├─ linha_do_tempo.csv                                  │
│   ├─ cenarios.json                                       │
│   ├─ reconciliacoes.csv                                  │
│   ├─ interacoes_ia.json                                  │
│   ├─ acessos.csv                                         │
│   └─ notas.txt                                           │
│                                                          │
│  Tamanho estimado: ~2,4 MB                               │
│                                                          │
│  ─── Privacidade do export ────────────────────          │
│                                                          │
│  ⚠ O ZIP gerado não tem criptografia adicional.          │
│    Cuide para guardar em local seguro depois.            │
│                                                          │
│  [ Gerar e baixar ]    [ Cancelar ]                      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Lista exatamente o que vai ser exportado.** Sem surpresa.
- **Estrutura do ZIP visível.** Usuário sabe o que vai abrir.
- **Aviso sobre cuidado pós-export.** Honestidade — uma vez fora do produto, é responsabilidade do usuário.

---

## Diferenças por plano

| Funcionalidade | Básico | Plus | Avançado |
|---|---|---|---|
| Linha do tempo | ✓ | ✓ | ✓ |
| Detalhamento de parcela | ✓ | ✓ | ✓ |
| DDCs guardados (versões) | última | últimas 5 | ilimitado |
| Reconciliação automática | — | ✓ | ✓ |
| Memória de cálculo | — | ✓ | ✓ |
| Diff entre DDCs | — | ✓ | ✓ |
| Carta para o banco | — | — | ✓ |
| Logs de acesso (período) | 7 dias | 30 dias | 90 dias |
| Logs de IA | — | 30 dias | 90 dias |
| Exportação total | ✓ | ✓ | ✓ |

**Importante**: exportação total e linha do tempo básica são gratuitas — direitos LGPD não escalam por plano.

---

## Métricas que importam

| Métrica | Meta |
|---|---|
| Taxa de usuários que abrem Audit pelo menos 1× | > 40% em 90 dias |
| Taxa de uso da reconciliação (Plus+) | > 30% mensalmente |
| Taxa de exportação total | < 5% (sinal de saída) |
| Taxa de "não fui eu" disparado | < 0,1% (idealmente quase zero) |
| Diferenças detectadas vs falsas-positivas | razão > 5:1 |

---

## Relação com privacidade

Esta jornada é a mais **alinhada estruturalmente com LGPD**. Ela materializa direitos:

- **Direito de acesso (Art. 18, II)** → linha do tempo, reconciliação, todos os dados visíveis.
- **Direito de informação sobre uso (Art. 18, V)** → logs de IA com dados enviados.
- **Direito de portabilidade (Art. 18, VI)** → exportação total em formato aberto.
- **Direito à confirmação (Art. 18, I)** → tudo confirma o que existe.
- **Direito de revisão de decisão automatizada (Art. 20)** → "Como vocês chegaram nisso?" em qualquer recomendação da IA.

### Outras decisões de privacidade

- **Retenção de logs por plano**, mas direitos LGPD são iguais para todos.
- **Apagar conversas de IA** é botão único, sem fricção.
- **Desativar IA** é toggle simples — não envia mais dados externamente.
- **Carta para o banco** não é enviada por Marco Zero — usuário tem controle total.
