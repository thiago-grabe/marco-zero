# Tenor — Master Context

> Formerly "Marco Zero". Renamed to Tenor — the banking term for the contractual term of a loan.

> Status: ideação completa, pronto para iniciar desenvolvimento
> Última atualização: 06/05/2026
> Próxima etapa: arquitetura técnica (schema, parsers, stack)

---

## 1. Origem do projeto

Tenor nasceu de uma série de conversas sobre o financiamento imobiliário do Thiago (usuário-referência, fundador). Em 6 trocas, ele passou por:

| Momento | Insight |
|---|---|
| Simulação de amortização de R$ 90k | Diferença SAC prazo vs. parcela mal explicada pelos bancos |
| App Itaú retornou números "estranhos" | Nomenclatura do banco mascara matemática real |
| Upload de simulação com R$ 80k | Banco mantém parcela, comprime prazo de forma híbrida |
| DDC após operação | Plano saltou de 30 para ~16 anos com R$ 80k bem aplicados |
| Cenários 5k/mês | Quitação em 5 anos, economia de R$ 267k em juros |
| Cenários 5k/mês + 60k/ano | Quitação em 3 anos — sweet spot |
| Cenários 10k/mês + 60k/ano | Piso de retorno marginal atingido |

**Insight central**: ninguém deveria passar 6 trocas com IA para entender o que vai acontecer com a maior dívida da vida dele.

---

## 2. Dados reais do contrato-referência (Thiago)

> Usado para validar modelos e wireframes. Todos os números são reais.

- **Banco**: Itaú, Carteira Hipotecária
- **Sistema**: SAC
- **Taxa**: 12,19% a.a. efetiva (0,9631393% a.m.)
- **Valor original**: R$ 536.000,00
- **Contrato**: #10300539502
- **Data de início**: dezembro/2025 (parcela #1 = 21/12/2025 aprox)
- **Saldo devedor atual** (DDC 05/05/2026): R$ 429.629,87
- **Parcelas restantes**: 189 (de 360 totais, após amortizações)
- **Próxima parcela**: #5, R$ 6.578,27, vencimento 21/05/2026
  - Amortização: R$ 2.285,27 | Juros: ~R$ 4.159 | MIP+DFI: ~R$ 134
- **Data original de quitação**: 21/01/2042
- **Amortizações realizadas**: 6 operações em ~5 meses (padrão raro)
  - Última: R$ 80.000 em 28/04/2026 (modalidade: redução de prazo)
  - Juros pró-rata + correção monetária: R$ 210,08
  - Total desembolsado: R$ 80.210,08
- **Taxa de mercado (maio/2026)**: Caixa SBPE ~11,19% a.a. → spread de ~100bps
- **FGTS**: última utilização ~12/03/2024; nova janela em ~12/03/2026 (aberta)

### Projeções validadas (DDC confirmado)

| Cenário | Quitação | Juros totais | Extras investidos |
|---|---|---|---|
| Sem extras | 21/01/2042 | R$ 391.034 | R$ 0 |
| +5k/mês | 21/04/2031 | R$ 124.082 | R$ 294.799 |
| +5k/mês +60k/ano (abril) | 21/04/2029 | R$ 82.274 | R$ 349.645 |
| +10k/mês +60k/ano | 21/07/2028 | R$ 58.729 | R$ 370.213 |

**Sweet spot**: 5k/mês + 60k/ano. Captura 93% da economia máxima, libera em 3 anos.

---

## 3. Visão do produto

### Posicionamento
> "Tenor é o copiloto de quitação imobiliária para o brasileiro que pensa em décadas."

Diferença de simulador para copiloto:
- **Simulador**: você preenche números, vê tabela, fecha a aba.
- **Copiloto**: conhece seu contrato, sua taxa, seu FGTS, sua disciplina, e te ajuda a decidir a **próxima ação agora**.

**Tagline**: "Cada parcela tem um plano. Cada plano tem um fim."

**Metáfora central**: "Tenor é o seu cofre de financiamentos."
- Nunca "upload" → sempre "guardar"
- Nunca "processar" → sempre "analisar seu contrato"

### Naming
Tenor — o ponto de quitação. Brasileiro, memorável. Venceu sobre "Soleira" e "Esquadro".

### Estética
**Dark premium** — inspirado em Cumbuca, Linear, Vercel dashboard. Técnico, moderno, premium.

- **Fundo**: quase-preto (`#0D0D0D`, não preto puro)
- **Texto**: quase-branco (`#F2F2F2`)
- **Acento primário**: âmbar (`#F59E0B`) — ganhos, CTAs, destaques
- **Semântica financeira**: verde desaturado (ganho), vermelho (perda), âmbar escuro (aviso)
- **Tipografia**: IBM Plex Serif para números e headings, Geist Sans para corpo
- **Tokens CSS completos**: `docs/technical/stack_01.md` §Decisão 8
- **Sem**: gradientes de fundo, glassmorphism, sombras coloridas, ilustrações, ornamentos
- **Microinterações**: ease-out, não bounce; números se atualizam silenciosamente

---

## 4. Features e jornadas

Documentação organizada em `docs/ux/` (jornadas), `docs/product/` (produto) e `docs/technical/` (arquitetura).

| Feature | Documento | Status |
|---|---|---|
| Onboarding | `docs/ux/journey_01_onboarding.md` | Completo |
| Cenários | `docs/ux/journey_02_cenarios.md` | Completo |
| IA Chat | `docs/ux/journey_03_ia_chat.md` | Completo |
| Modo Coach | `docs/ux/journey_04_coach.md` | Completo |
| Stress Tests | `docs/ux/journey_05_stress_tests.md` | Completo |
| Dashboard | `docs/ux/journey_06_dashboard.md` | Completo |
| Audit | `docs/ux/journey_07_audit.md` | Completo |
| Arquitetura de dados & LGPD | `docs/product/idea_01.md` | Completo |
| Schema relacional & contrato do parser | `docs/technical/schema_01.md` | Completo |
| Motor de cálculo SAC/PRICE/Itaú & JSON canônico | `docs/technical/motor_01.md` | Completo |
| Agente de extração de DDC (parser agnóstico) | `docs/technical/parser_01.md` | Completo |

### Resumo funcional por feature

**Onboarding** (< 90 segundos, landing → primeiro insight)
- Landing → Auth (magic link) → Boas-vindas → Banco → PDF ou manual → Extração → Conferência → 3 insights
- DDC redacta CPF automaticamente antes de armazenar
- Pular não pune — dashboard "cofre vazio" com CTA gentil

**Cenários** (o coração do produto)
- Sandboxes, não compromissos. Usuário explora sem medo
- Sliders com resultado em tempo real (<100ms). Sem botão "calcular"
- Cenário promovido a "plano atual" = confirmação dupla
- Salvar stress test como cenário oficial

**IA Chat**
- Acesso de leitura ao contrato ativo e somente esse
- Resposta em 3 camadas: direta → análise (com fontes) → caveats
- Limites declarados: não executa, não recomenda investimentos por nome
- Botão "como chegamos aqui" = fórmula auditável

**Coach** (produto ativo, não reativo)
- 9 tipos de alerta contextuais (FGTS, Selic, desvio de plano, etc.)
- Detecção de fadiga — reduz frequência se usuário ignora 3x seguidos
- Alerta mais novo: "aumento de renda — como agir"

**Stress Tests**
- Negativos: perda de emprego (6m/12m), aumento de juros, inflação, despesa inesperada, filho na escola, doença, divórcio, aposentadoria antecipada, desvalorização
- **Positivos** (diferencial): aumento de renda, bônus/PLR acima do esperado, herança, novo emprego
- Resultado sempre 3 níveis: ✓ cobre / ⚠ desliza / ✗ quebra
- Stress declarado ativa modo Coach correspondente

**Dashboard**
- Data de quitação = herói da tela (tipografia grande, serifa)
- Linha do tempo física: início → hoje → quitação
- 3 KPIs secundários: parcela, saldo, juros pagos
- Máximo 1 card de próxima ação (vem do Coach)
- Barra de progresso: "19,8% do caminho"

**Audit**
- Linha do tempo imutável de eventos
- Reconciliação automática: saldo esperado vs. saldo do DDC
- Logs de interações com IA (com PII já removida)
- Carta para o banco (feature avançada)
- Exportação em PDF e CSV

---

## 5. Modelo de dados

Hierarquia em 3 níveis:
```
Usuário
  └── Imóvel (apelido, endereço)
        └── Contrato (banco, número, sistema, taxa)
              ├── DDCs (snapshots imutáveis, versionados)
              ├── Operações registradas (amortizações, eventos)
              ├── Cenários planejados (versionados)
              └── Lembretes / notas
```

**Regra de ouro**: nenhuma query retorna dados de outro usuário sem `user_id` como filtro indexado no backend. Row-Level Security é o mecanismo.

**CPF**: nunca persiste. Redactado no momento do upload (`[CPF_REDACTED]`).

---

## 6. Estratégia de ingestão de dados

O produto é **standalone** — sem integração bancária. Dados chegam via:

1. **Parser determinístico** por banco (Itaú, Caixa, BB, Santander, Bradesco) — regex/coordenada
2. **LLM como fallback estruturado** — quando parser falha. JSON schema com validador semântico
3. **Entrada manual** — formulário guiado, 6-8 campos, sempre disponível
4. **Registro ad-hoc de operações** — usuário declara amortização; sistema valida com próximo DDC

Inversão de dados: parser loga qual caminho usou → casos LLM bem-sucedidos viram regras determinísticas ao longo do tempo.

---

## 7. LGPD e segurança

### Princípios-chave
- **Privacy as feature**, não como etapa final
- Direitos LGPD são **idênticos** em todos os planos (não são premium)
- DPIA vivo, atualizado a cada feature, com versão pública abreviada
- Incident response ensaiado trimestralmente

### Práticas técnicas
- Redaction de PII antes de enviar ao LLM (CPF, nome, conta, agência)
- LLM com Zero Data Retention (Anthropic API)
- PDFs em bucket privado com criptografia per-objeto (key derivada de user_id)
- URLs de acesso assinadas, curta duração
- MFA opcional (recomendado para saldo > R$ 200k)
- Magic link como default de auth (sem senha pra vazar)

### Tela "Meus Dados"
Tela completa e em destaque mostrando: identidade, contratos, cenários, consentimentos ativos (com data e botão revogar), subprocessadores em uso, histórico de acessos, ações (exportar ZIP, pausar, excluir).

### Subprocessadores
- Anthropic — LLM (Zero Data Retention)
- Vercel / Fly.io — hospedagem
- Supabase / Neon — banco de dados
- AWS S3 sa-east-1 — storage de PDFs
- Sentry — erros (com redaction de PII configurado)

---

## 8. Planos e pricing

Plano Família descartado. Estrutura atual:

| Feature | Básico (grátis) | Plus (R$ 19/mês) | Avançado (R$ 39/mês) |
|---|---|---|---|
| Contratos | 1 | 3 | Ilimitado |
| Cenários | 2 | Ilimitado | Ilimitado |
| IA Chat | 10 perguntas/mês | Ilimitado | Ilimitado |
| Coach — alertas básicos | ✓ | ✓ | ✓ |
| Coach — Selic/portabilidade | — | ✓ | ✓ |
| Stress Tests | 1 simples | Predefinidos | Todos + custom |
| Audit completo | Linha do tempo | + Reconciliação | + Logs IA + export |
| Versionamento DDC | Última versão | Últimas 5 | Ilimitado |
| Direitos LGPD | Idêntico | Idêntico | Idêntico |

**Princípios anti-dark-pattern**:
- Cancelamento = mesmo número de cliques que assinatura
- Trial só com confirmação ativa (não auto-debit)
- Sem confirm-shaming
- Pro-rata sempre
- Reajuste só na renovação anual, com aviso de 30 dias

---

## 9. Plataforma

| Camada | Pré-MVP | Produção |
|---|---|---|
| Hospedagem | Vercel | Fly.io GRU |
| BD | Supabase Pro | Neon GRU + Lucia auth |
| Storage PDFs | Cloudflare R2 | AWS S3 sa-east-1 + KMS |
| Auth | Supabase | Auth.js + Postgres + MFA |
| LLM | Anthropic ZDR | Anthropic ZDR |
| Monitoramento | Sentry + UptimeRobot | + Axiom + Better Stack |

**Regra de migração**: começar simples (Vercel + Supabase), mas com schema e separação de camadas que permitem migrar em uma sprint.

---

## 10. Concorrência — espaço em branco

Todos os simuladores existentes (Larya, Educando Seu Bolso, Calculadora Brasil, Bext, simuladores de banco):
- ✗ Não conhecem seu contrato persistentemente
- ✗ Não modelam investir vs. amortizar com IR e liquidez
- ✗ Não integram timing de FGTS
- ✗ Não detectam janela de portabilidade com taxas vivas
- ✗ Não pensam em eventos de vida
- ✗ Não têm reconciliação automática banco vs. esperado

Tenor faz tudo isso.

---

## 11. Status atual

### Concluído (ideação)
- [x] Visão, posicionamento, naming, estética
- [x] Hierarquia de dados e modelo mental do produto
- [x] Estratégia de ingestão (parsers, LLM, manual)
- [x] LGPD e segurança como produto (não compliance)
- [x] Pricing sem dark patterns
- [x] Wireframes das 7 jornadas principais
- [x] Distribuição de features por plano

### Próximas etapas (técnico)
- [x] Schema relacional concreto (tabelas, FKs, RLS policies) — `docs/technical/schema_01.md`
- [x] Motor de cálculo (SAC/PRICE/Itaú, 17 Tools) — `docs/technical/motor_01.md`
- [x] Agente de extração agnóstico (qualquer banco, qualquer PDF) — `docs/technical/parser_01.md`
- [x] Definir stack final — `docs/technical/stack_01.md`
- [x] Estrutura de projeto (`web/` + `api/`) — `docs/technical/structure_01.md`
- [ ] Modelagem do motor de cálculo SAC (determinístico, sem LLM)
- [ ] Estrutura de projeto / monorepo
- [ ] Setup do ambiente de desenvolvimento
- [ ] Estratégia de testes (especialmente do motor de cálculo)

---

## 12. Referências

| Arquivo | Conteúdo |
|---|---|
**`docs/product/`**
| `docs/product/idea_01.md` | Arquitetura de dados, estratégia LGPD, modelo de armazenamento |

**`docs/ux/`**
| `docs/ux/journey_01_onboarding.md` | Wireframes do onboarding, arco emocional, casos de borda |
| `docs/ux/journey_02_cenarios.md` | Wireframes de cenários, criação, comparação |
| `docs/ux/journey_03_ia_chat.md` | Wireframes do chat IA, princípios duros, limites |
| `docs/ux/journey_04_coach.md` | Tipos de alerta, wireframes, detecção de fadiga |
| `docs/ux/journey_05_stress_tests.md` | Catálogo de stress (negativos e positivos), wireframes |
| `docs/ux/journey_06_dashboard.md` | Wireframes do dashboard, hierarquia visual |
| `docs/ux/journey_07_audit.md` | Linha do tempo, reconciliação, logs de IA |

**`docs/technical/`**
| `docs/technical/schema_01.md` | Schema relacional, reference tables, RLS, queries críticas |
| `docs/technical/motor_01.md` | Motor SAC/PRICE/Itaú, 17 Tools, JSON canônico, escala DDC |
| `docs/technical/parser_01.md` | Agente de extração agnóstico, tiered models, prompts |
| `docs/technical/stack_01.md` | Decisões de stack (plataforma, framework, LLM, UI, hosting) |
| `docs/technical/structure_01.md` | Estrutura de pastas `web/` e `api/`, Makefile, CI |
