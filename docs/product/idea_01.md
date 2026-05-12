# Tenor — Arquitetura de Dados & Estratégia LGPD

> Documento de ideação — versão 1
> Data: 06/05/2026
> Status: em discussão

## Contexto

Tenor é um copiloto de quitação de financiamento imobiliário. Sem integração bancária, opera como **standalone app** que recebe dados estruturados e não estruturados do próprio usuário (PDFs de DDC, entradas manuais, registros de operações). Cada usuário tem um ou mais contratos, possivelmente atrelados a um ou mais imóveis.

Este documento define as decisões de produto sobre arquitetura de dados, ingestão e privacidade — sem entrar em implementação técnica.

---

## 1. O modelo mental do produto

Antes de qualquer arquitetura, fixar a metáfora certa pro usuário:

> **"Tenor é o seu cofre de financiamentos. Você guarda seus contratos aqui. A inteligência mora dentro."**

Isso muda tudo:

- O usuário não está "subindo dados" para um SaaS analítico. Ele está **organizando documentos importantes em um cofre privado**.
- A IA não é o produto. **O cofre é o produto.** A IA é um serviço *dentro* do cofre.
- Isso resolve narrativa de privacidade (cofre = seguro, intuitivo) e justifica a arquitetura técnica (dados isolados por usuário).

A escolha de palavras importa: nunca "upload", sempre "guardar". Nunca "processar", sempre "analisar seu contrato".

---

## 2. Hierarquia de dados

```
Usuário (auth_id, e-mail, nome)
  │
  ├── Imóvel A — "Apartamento Contagem"
  │     │
  │     ├── Contrato Itaú 10300539502  ←  contrato ativo
  │     │     ├── DDC 26/04/2026 (snapshot)
  │     │     ├── DDC 29/04/2026 (snapshot)
  │     │     ├── DDC 05/05/2026 (snapshot)  ← mais recente
  │     │     ├── Operações registradas
  │     │     │   ├── Amort R$ 8.000  (22/12/2025)
  │     │     │   ├── Amort R$ 5.000  (25/02/2026)
  │     │     │   ├── ...
  │     │     ├── Cenários planejados
  │     │     │   ├── "5k/mês + 60k/ano"
  │     │     │   ├── "10k/mês + 60k/ano"
  │     │     ├── Lembretes
  │     │     │   ├── FGTS libera 12/03/2026
  │     │     │   ├── PLR Bain ~abril
  │     │     ├── Notas livres do usuário
  │     │
  │     └── (futuro) Contrato portado, se houver
  │
  └── Imóvel B — "Casa de praia" (futuro)

Usuário (cônjuge — visão compartilhada opcional)
  └── ... acessa Imóvel A em modo "co-titular"
```

**Decisões implícitas dessa estrutura:**

1. **Hierarquia em 3 níveis**: usuário → imóvel → contrato. Permite múltiplos contratos no mesmo imóvel (caso de portabilidade — o histórico do anterior fica preservado ao lado do novo).
2. **DDC é tratado como "snapshot" imutável**, não como "dado atualizado". Cada DDC é uma versão preservada para auditoria histórica. O usuário precisa confiar que o registro do que o banco disse num determinado dia não vai sumir.
3. **Operações são entidades de primeira classe** (não derivadas do DDC). Quando o usuário faz uma amortização, ele registra isso *antes* de subir o novo DDC. Isso permite ao sistema validar que o DDC novo bate com o esperado (auditoria automática).
4. **Cenários são salvos**, não voláteis. Usuário pode voltar e ver "o plano que eu desenhei em março" e comparar com a realidade.
5. **Compartilhamento explícito**: cônjuge é um segundo usuário com permissão de visualização (ou edição). Ninguém edita conta do outro.

---

## 3. Estratégia para dados não estruturados de banco

Cada banco tem layout próprio (e cada banco muda layout sem aviso). Atacar em camadas:

### 3.1. Camada 1 — Parsers determinísticos por banco

Para os 5 principais (Caixa, Itaú, BB, Santander, Bradesco), construir parsers regex/coordenada-baseados que extraem campos canônicos de DDC: saldo, taxa, parcelas, operações.

Vantagens: rápido, previsível, barato, sem alucinação. Desvantagem: refém do layout.

### 3.2. Camada 2 — LLM como fallback estruturado

Se o parser falhar (banco novo, layout mudou, PDF anômalo), cair em LLM com saída estruturada (JSON schema). Princípios:

- O prompt **nunca pede inferência criativa**. Pede mapeamento literal.
- Saída passa por validador semântico (saldo > 0, taxas em range razoável, etc).
- Se 2+ validações falham, sistema pede ao usuário para conferir manualmente.
- Logs guardam qual parser foi usado para promover casos LLM-bem-sucedidos para regras determinísticas ao longo do tempo.

### 3.3. Camada 3 — Entrada manual sempre disponível

Há casos em que o usuário não tem o DDC. UI tem caminho explícito de "informar contrato manualmente": 6-8 campos críticos em formulário guiado. Sem dependência de PDF.

### 3.4. Camada 4 — Registro de operações ad-hoc

Operações são auto-declarativas. Usuário registra "amortizei R$ 80k em 28/04/2026" e o sistema:

- Recalcula saldo esperado.
- Quando o próximo DDC for subido, valida se bate ("DDC mostra R$ 429.629,87 — coincide com o esperado de R$ 429.612,50 ± 0,1% considerando juros pró-rata. ✅")
- Se não bate (diff > 1%): alerta amarelo: "encontramos uma divergência. Pode ser correção monetária do banco. Confira."

Esse loop de verificação é um dos maiores diferenciais — auditoria contínua que nenhum simulador faz.

### 3.5. Camada 5 — Onboarding incremental

Usuário não precisa subir tudo de uma vez:

1. *"Qual banco?"* → 1 click
2. *"Você tem o DDC em PDF?"* → sim/não
3. Sim → upload + extração para conferência. Não → 6 campos manuais.
4. *"Quer adicionar histórico de amortizações?"* → opcional, pula sem culpa.
5. *"Pronto. Aqui está seu painel."*

Tempo até primeiro valor: **< 90 segundos**.

---

## 4. Modelo de armazenamento

Três tipos de dados, com tratamento diferente:

| Tipo | Exemplos | Onde mora | Criptografia |
|---|---|---|---|
| Identidade | nome, e-mail, telefone | Tabela usuários | em repouso (TDE) |
| Sensível estruturado | saldo, taxa, parcelas, contrato | Tabela contratos, scopada por user_id | em repouso + por usuário |
| Sensível bruto | PDFs originais do DDC | Storage isolado, bucket por usuário | per-object key derivada do user_id |

**Regra de ouro**: nenhuma query do banco de dados pode retornar dados de outro usuário sem o user_id explícito como filtro indexado e validado pelo backend. Row-Level Security é o mecanismo certo.

PDFs originais ficam isolados em bucket privado, com URLs assinadas de curta duração. Nunca públicos, nunca indexados.

**CPF**: aparece no DDC. Decisão: **não persistir**. Parser detecta padrão `XXX.XXX.XXX-XX` e:

- Substitui por `[CPF_REDACTED]` no PDF antes de armazenar.
- Confirma com o usuário no upload: "Detectamos CPF no documento. Vamos remover antes de salvar. ✓"

Defesa em profundidade: mesmo que haja vazamento, CPF não está lá.

---

## 5. LGPD — não como compliance, como produto

Compliance e UX não são adversários. As exigências da LGPD na verdade *forçam* boas decisões de produto.

### 5.1. Bases legais aplicáveis

| Operação | Base legal |
|---|---|
| Criar conta | Execução de contrato (Art. 7º, V) |
| Armazenar DDC | Execução de contrato + consentimento explícito |
| Gerar simulações | Execução de contrato |
| Notificações de oportunidade (Selic, FGTS) | Consentimento (opt-in claro) |
| Marketing | Consentimento separado, opt-out fácil |
| Compartilhamento com cônjuge | Consentimento + autorização explícita do co-titular |
| Telemetria/analytics | Legítimo interesse (mínimo necessário) |

Os dois últimos especialmente: opt-in granular, não pacotão.

### 5.2. Princípios LGPD traduzidos em UI

- **Finalidade**: tela de consentimento explica em 3 linhas para que cada dado é usado.
- **Adequação e necessidade**: não pede dados que não usa. Telefone só se usuário ativar SMS. Renda só para feature específica.
- **Livre acesso**: aba "Meus Dados" mostrando exatamente o que o sistema sabe.
- **Qualidade dos dados**: usuário pode editar qualquer campo extraído. Histórico de edições preservado.
- **Transparência**: política de privacidade curta (< 1500 palavras). Versionada. Usuário avisado de mudanças materiais.
- **Segurança**: lista pública das medidas técnicas. Confiança vem da especificidade.
- **Prevenção**: rate-limiting, MFA opcional, alertas de login suspeito.
- **Não-discriminação**: produto não vende lead. Recomendação de portabilidade é matemática auditável.
- **Responsabilização**: DPO público. Canal de privacidade ativo. SLA exposto.

### 5.3. Direitos do titular como interface

| Direito | UI |
|---|---|
| Confirmação | Login mostra. |
| Acesso | Aba "Meus Dados" sempre visível. |
| Correção | Edit inline em qualquer campo. |
| Anonimização / bloqueio | Toggle "pausar conta". |
| Eliminação | Botão "Excluir conta": cooldown de 7 dias, e-mail de confirmação, purge irreversível incluindo backups. |
| Portabilidade | Export ZIP completo (PDFs + JSON + cenários). Padrão aberto. |
| Informação sobre compartilhamento | Página "Quem vê meus dados". |
| Revogação de consentimento | Toggles na config, instantâneos. |
| Revisão de decisão automatizada | Botão "como chegamos aqui" mostra a fórmula de qualquer recomendação. |

### 5.4. LLM e LGPD — o ponto delicado

Quando o produto manda um DDC para um LLM extrair campos, dados pessoais financeiros estão saindo da infraestrutura. Decisões:

1. **Redact antes de enviar**: nome, CPF, conta, agência removidos por regex no servidor antes de ir para LLM. Modelo recebe `[USUARIO]`, `[CPF]`, `[AGENCIA]`. Números financeiros vão crus.
2. **Provedor com Zero Data Retention**: contrato comercial garante que prompts não são usados para treino. Documentar na política de privacidade.
3. **Subprocessadores listados**: política tem seção visível "Quem mais processa seus dados" com links.
4. **Operações sensíveis ficam local**: cálculo de amortização SAC, projeção de cenários, comparação investir-vs-amortizar — tudo determinístico, roda sem LLM. LLM só entra em (a) extração de PDF mal estruturado, (b) explicação em linguagem natural, (c) chat de dúvidas.
5. **Modo offline**: usuário avesso a LLM pode marcar "não enviar meus dados a IA externa". Produto continua funcional com features determinísticas; chat com IA fica desabilitado para essa conta.

### 5.5. Retenção e ciclo de vida

| Categoria | Retenção |
|---|---|
| Conta ativa | Indefinida |
| Conta inativa > 24 meses | E-mail de aviso aos 18, 22 e 24 meses; arquivamento aos 24 |
| Conta excluída | Hard delete em 7 dias pós cooldown, incluindo backups |
| Logs de auditoria | 6 meses |
| PDFs de DDC | Mesma vida da conta; exportável a qualquer momento |
| Histórico de interações com LLM | 30 dias para debug; sem PII após redaction |

---

## 6. UI/UX que reflete tudo isso

### 6.1. O moment of trust no upload

Quando usuário arrasta o DDC:

```
[arrastando DDC.pdf]
   ↓
┌───────────────────────────────────┐
│ Estamos analisando seu contrato.  │
│                                   │
│ ✓ CPF detectado e removido        │
│ ✓ Saldo extraído: R$ 429.629,87  │
│ ✓ 188 parcelas mapeadas          │
│                                   │
│ ⓘ Seu PDF original fica no seu   │
│   cofre privado. Apenas você     │
│   acessa.                         │
│                                   │
│ Algo errado? Editar valores      │
└───────────────────────────────────┘
```

Cada checkmark constrói confiança. O caveat sobre CPF aparece automaticamente — sem o usuário pedir — e isso comunica competência mais do que qualquer texto da home page.

### 6.2. Onboarding sem pressão

Tela de criação de conta tem o mínimo absoluto: e-mail, senha (ou magic link), checkbox de termos com links. Sem opt-in de marketing pré-marcado. Sem perguntar telefone, idade, profissão. Tudo isso é coletado depois, no momento da feature que precisa, com explicação contextual.

### 6.3. Multi-financiamento, multi-imóvel

Header tem seletor explícito do contrato ativo. Cada visualização é scopada ao contrato selecionado. Não há "agregação automática" entre contratos — porque a estratégia ótima por contrato pode ser diferente.

Existe tela opcional "Visão Consolidada" read-only mostrando resumo de todos os contratos juntos.

### 6.4. Compartilhamento com cônjuge

Co-titular cria conta separada. Não é "sub-usuário". Os dois têm a mesma posição legal, ambos têm direitos LGPD plenos sobre os dados compartilhados.

Convite por e-mail. Permissões: visualização ou edição completa. Audit trail de quem alterou o quê.

### 6.5. Tela "Meus Dados"

A maioria dos produtos esconde isso. Tenor dá destaque com uma tela completa mostrando identidade, contratos armazenados, cenários salvos, consentimentos ativos, subprocessadores em uso, e ações (exportar, pausar, excluir).

---

## 7. Riscos e mitigações

| Risco | Mitigação |
|---|---|
| Banco muda layout do DDC | Camada de fallback LLM + monitoramento de taxa de sucesso |
| Usuário sobe DDC com dados errados | Validação semântica detecta inconsistências antes de salvar |
| Vazamento por engenharia social | Suporte nunca pede senha, MFA recomendado, auditoria de admins |
| Vazamento de bucket | Bucket privado, URLs assinadas curtas, criptografia per-objeto |
| Subpoena / pedido judicial | Política transparente, notifica usuário quando legalmente possível |
| LLM "alucina" análise errada | LLM nunca calcula — só extrai e explica. Cálculo determinístico |
| ANPD multa por incidente | Plano de resposta documentado, comunicação em 72h, registro de incidentes |
| Concorrente copia | Moat real é parser robusto + UX do coach + confiança acumulada |

---

## 8. Síntese

Três pontos pra fixar:

1. **Arquitetura trata cada usuário como dono de um cofre isolado**, não como linha numa tabela compartilhada. Esse rigor técnico vira narrativa de marca.
2. **LGPD é como o produto se estrutura desde o dia 1**, não etapa final. Cada decisão de privacidade vira affordance visível na UI. "Privacy as feature" é diferenciação real.
3. **Parser de DDC é estratégico, não tático**. 3 meses construindo parsers robustos para os 5 maiores bancos cria fosso difícil de copiar. Network effect de dados (anonimizados) reforça vantagem competitiva.

A combinação dessas três coisas transforma o produto de "simulador bonito" em "infraestrutura privada de planejamento de hipoteca" — categoria nova, defensável, alinhada com a estética de "sofisticação tropical" que privilegia confiança e calma sobre estímulo.

---

## Próximas ideações pendentes

- [ ] Fluxo de incident response e DPIA (Relatório de Impacto)
- [ ] Wireframes detalhados: onboarding e tela "Meus Dados"
- [ ] Modelo de preços que respeita LGPD (sem dark patterns)
- [ ] Schema relacional concreto (depois)
- [ ] Spec funcional do parser por banco (depois)
