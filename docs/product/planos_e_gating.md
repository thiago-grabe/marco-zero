# Tenor — Planos e gating (versão massa)

> Define o que cada plano libera, feature a feature, para travar o escopo do MVP de massa. Princípio: **o grátis precisa entregar as três perguntas universais** (quando acaba, quanto falta, está certo?) — clareza suficiente para valer o cadastro e gerar confiança. O pago vende **sem limite + proteção contínua + caixa rápido**.

---

## Resumo dos planos

| Plano | Preço | Para quem |
|---|---|---|
| **Grátis** | R$ 0 | Massa que quer entender e conferir 1 financiamento |
| **Tranquilo** | R$ 9–12 / mês | Massa que quer uso ilimitado + avisos + carta |
| **Vitalício** | R$ 297 (uma vez) | Quem prefere pagar uma vez (destrava caixa, evita churn) |
| **Avançado (nicho)** | R$ 39 / mês | Quitador: cenários comparados, granularidade fina |

> O "Avançado" é o antigo plano de nicho; convive com os de massa. No MVP de massa, o foco é Grátis + Tranquilo + Vitalício.

---

## Tabela de gating — feature a feature

| Feature | Grátis | Tranquilo (R$ 9–12) | Vitalício (R$ 297) | Avançado/Nicho (R$ 39) |
|---|:--:|:--:|:--:|:--:|
| **Onboarding por foto / 3 campos** | ✓ | ✓ | ✓ | ✓ |
| Tradução do boleto ("entender meu boleto") | ✓ | ✓ | ✓ | ✓ |
| Data de quitação + "já paguei / falta" | ✓ | ✓ | ✓ | ✓ |
| Contratos cadastrados | 1 | 3 | 3 | Ilimitado |
| **Conferindo o banco (reconciliação)** | 1 contrato | ✓ todos | ✓ todos | ✓ todos |
| Conferência automática mensal | — | ✓ | ✓ | ✓ |
| Memória de cálculo detalhada | ✓ | ✓ | ✓ | ✓ |
| Gerar carta para o banco | — | ✓ | ✓ | ✓ |
| Histórico de conferências | última | 12 meses | ilimitado | ilimitado |
| **Chat IA (tradutor)** | 10 perguntas/mês | Ilimitado | Ilimitado | Ilimitado |
| "Como chegamos nisso?" | ✓ | ✓ | ✓ | ✓ |
| Histórico de conversas | — | 30 dias | 90 dias | 90 dias |
| **Ensaios de adiantamento (slider)** | 2 salvos | Ilimitado | Ilimitado | Ilimitado |
| Adiantar vs guardar (renda fixa) | ✓ | ✓ | ✓ | ✓ |
| **Stress tests predefinidos** (3) | ✓ | ✓ | ✓ | ✓ |
| Stress tests custom | — | — | — | ✓ |
| **Cenários comparados lado a lado** | — | 2 | 2 | até 4 |
| **Avisos** | parcela só | 4 (massa) | 4 (massa) | 9 (granular) |
| Aviso "taxa acima do mercado" | — | ✓ | ✓ | ✓ |
| Aviso "banco mudou seu saldo" | — | ✓ | ✓ | ✓ |
| Simulação de portabilidade | ✓ (resultado) | ✓ + carta | ✓ + carta | ✓ + carta |
| **Exportar tudo (ZIP/PDF)** — LGPD | ✓ | ✓ | ✓ | ✓ |
| Excluir/pausar conta | ✓ | ✓ | ✓ | ✓ |
| Modo privacidade (desligar IA) | ✓ | ✓ | ✓ | ✓ |

> Direitos da LGPD (exportar, excluir, pausar, desligar IA) **nunca** são gated — estão em todos os planos, inclusive grátis.

---

## Regras de gating e upgrade

1. **O grátis tem que ser bom sozinho.** Entrega as 3 perguntas universais e 1 conferência. Sem isso, não há confiança nem boca a boca.
2. **O gatilho de upgrade da massa é a proteção contínua**, não a otimização: conferência automática mensal, aviso "o banco mudou seu saldo" e a carta para o banco moram no Tranquilo.
3. **Limite de perguntas do chat (10/mês)** é o teto mais provável de ser atingido pela massa engajada → principal gancho de conversão para o Tranquilo.
4. **Vitalício existe por causa do churn.** A massa usa pouco por mês (decisão mensal); assinatura recorrente sofre. R$ 297 uma vez destrava caixa e remove a fricção de "mais uma mensalidade".
5. **Upsell tem lugar próprio** (tela de planos, fim de fluxo de valor) — nunca piscando no dashboard.
6. **Sem dark patterns.** Downgrade fácil; sem reativação enganosa; cancelamento em 1 toque.

---

## Onde o upgrade aparece (momentos honestos)

| Momento | Mensagem |
|---|---|
| 11ª pergunta no chat do grátis | "Você usou suas 10 perguntas do mês. No Tranquilo, é ilimitado." |
| Divergência detectada no grátis | "Quer gerar uma carta pro banco com a conta detalhada? Isso está no Tranquilo." |
| Aviso de taxa alta (não disponível no grátis) | "No Tranquilo, eu te aviso quando sua taxa estiver acima do mercado." |
| 2º contrato no grátis | "O grátis cobre 1 financiamento. Pra cadastrar mais, veja o Tranquilo." |

---

## Monetização indireta (portabilidade) — fora por ora

A parceria com quem oferece portabilidade gera receita, mas **conflita com a promessa "não vendemos seus dados pra banco"**, que é a base da confiança da massa. Decisão: **manter fora do modelo no MVP de massa.** Se um dia entrar, precisa ser:
- **opt-in explícito** do usuário,
- **sem venda de lead** (o usuário escolhe contatar, não o contrário),
- **transparente** ("o Tenor recebe X se você seguir por aqui"),
- e nunca enviesar a recomendação matemática de portabilidade.
