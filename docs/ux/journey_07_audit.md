# Tenor — Jornada 7: Audit / Guardião (versão massa)

> **Objetivo**: provar que a matemática bate e dar ao usuário a sensação de ter **alguém do lado dele conferindo o banco**.
> **Princípio guia**: para o nicho, audit é a feature menos sexy e mais defensável. Para a **massa, é o valor emocional principal** — o motivo de confiar. Reposicionar de "auditoria técnica" para **"Conferindo o banco"**.

---

## Modelo mental do usuário (massa)

> "Será que o banco está me cobrando certo? Eu não tenho como saber sozinho. Se tivesse alguém conferindo isso pra mim e me avisando se algo estivesse errado, eu dormiria mais tranquilo."

A massa não quer auditar — quer **ser protegida**. A feature precisa fazer o trabalho e comunicar proteção, não exigir que o usuário entenda a memória de cálculo.

---

## Princípios duros

1. **Linguagem de proteção, não de auditoria.** "Conferindo o banco", não "Reconciliação".
2. **Conferência automática.** O produto compara sozinho; o usuário não precisa pedir.
3. **Divergência é o momento-ouro.** Explica em português, sem alarmar, e dá ação concreta.
4. **Usuário sempre no controle.** O Tenor nunca envia nada ao banco no lugar dele.
5. **Privacidade é parte do guardião.** "Não mandamos seu nome pra IA, não vendemos pra banco."

---

## Tela 7.1 — Conferindo o banco (tudo certo)

```
┌──────────────────────────────────────────────────────────┐
│  ←  Conferindo o banco                                   │
│                                                          │
│  Última conferência: 05/05/2026                          │
│  Resultado: ✓ Está tudo certo                            │
│                                                          │
│  O que o banco diz que você deve   R$ 429.629,87         │
│  O que a nossa conta diz            R$ 429.629,87         │
│  Diferença                          R$ 0,00  ✓           │
│                                                          │
│  Como chegamos nesse número:                             │
│   Saldo após a parcela de abril     R$ 510.977,65        │
│   + juros e correção do mês         R$    937,24         │
│   − sua amortização de R$ 80.000    R$ 80.000,00         │
│   − parcela de maio                 R$  2.285,02         │
│   = saldo de hoje                   R$ 429.629,87 ✓      │
│                                                          │
│  [ Conferir de novo ]   [ Salvar essa conta em PDF ]     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões
- **Selo "está tudo certo"** é o produto entregando tranquilidade.
- **Memória de cálculo disponível, não obrigatória.** Quem quiser, vê; quem não, confia no selo.

---

## Tela 7.2 — Quando há divergência (o momento de maior valor)

```
┌──────────────────────────────────────────────────────────┐
│  ←  Conferindo o banco                                   │
│                                                          │
│  ⚠ Achei uma diferença de R$ 1.234,56                    │
│                                                          │
│  O banco está cobrando mais do que a nossa conta         │
│  esperava. Antes de assustar, as causas mais comuns:     │
│                                                          │
│   1. A TR do mês veio diferente da projetada             │
│      (diferenças de R$ 400 a R$ 1.300 são normais)       │
│   2. Alguma operação que você fez e não registrou aqui   │
│   3. Erro do banco (raro, mas acontece)                  │
│                                                          │
│  O que você quer fazer?                                  │
│  [ Foi engano meu — registrar operação ]                 │
│  [ Quero questionar o banco → gerar carta ]              │
│  [ Marcar como esclarecido ]                             │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões
- **Explica antes de alarmar.** As 3 causas em ordem de probabilidade.
- **Três ações concretas**, cobrindo os casos reais (foi o usuário / é o banco / já entendi).

---

## Tela 7.3 — Carta para o banco

```
┌──────────────────────────────────────────────────────────┐
│  ←  Carta para o banco                                   │
│                                                          │
│  Geramos um rascunho explicando a diferença, com a       │
│  conta detalhada. Você revisa, ajusta e envia — a        │
│  gente nunca manda nada no seu lugar.                    │
│                                                          │
│  ┌────────────────────────────────────────────┐         │
│  │  À [Banco],                                   │       │
│  │  Refente ao contrato de financiamento [...],  │       │
│  │  identifiquei uma divergência de R$ 1.234,56  │       │
│  │  no saldo devedor de 05/05/2026...            │       │
│  │  [conta detalhada]                            │       │
│  └────────────────────────────────────────────┘         │
│                                                          │
│  [ Copiar texto ]   [ Baixar PDF ]                       │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões
- **Rascunho, não envio.** O usuário no controle — sem ação irreversível automática.
- **Inclui a memória de cálculo** — munição para a conversa com o gerente.

---

## Tela 7.4 — Histórico de conferências

```
┌──────────────────────────────────────────────────────────┐
│  ←  Histórico de conferências                            │
│                                                          │
│  05/05/2026   ✓ R$ 0,00                                  │
│  28/04/2026   ✓ R$ 0,00                                  │
│  29/03/2026   ⚠ R$ 4,17 (correção monetária)             │
│               Esclarecido em 29/03                        │
│  29/02/2026   ✓ R$ 0,00                                  │
│                                                          │
│  [ Exportar histórico ]                                  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Tela 7.5 — Meus dados (privacidade como parte do guardião)

```
┌──────────────────────────────────────────────────────────┐
│  ←  Meus dados                                           │
│                                                          │
│  ✓ Análise por IA (Claude / Anthropic)      [ revogar ]  │
│    Dados anonimizados antes de enviar                    │
│    Enviado: saldo, taxa, prazo                           │
│    NÃO enviado: seu nome, CPF, conta, agência            │
│                                                          │
│  ── Quem processa seus dados ──────────────              │
│   • Anthropic — IA, com Zero Data Retention              │
│   • (hospedagem / banco de dados / e-mail)               │
│   [ Ver detalhes de cada um ]                            │
│                                                          │
│  ── Histórico de acesso ──────────────────               │
│   Hoje 13:42   Belo Horizonte, MG   Chrome               │
│   Ontem 09:17  Belo Horizonte, MG   App                  │
│   Suspeita de acesso indevido? [ contato ]               │
│                                                          │
│  ── Sua conta ─────────────────────────────              │
│  [ Exportar tudo (ZIP) ]                                 │
│  [ Pausar conta ]                                        │
│  [ Excluir conta ] — apaga tudo, 7 dias de cooldown      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Tela 7.5.1 — "Ver dados enviados ao LLM"

```
┌──────────────────────────────────────────────────────────┐
│  ←  Dados enviados à IA                                  │
│                                                          │
│  Pergunta: "Vale a pena portar pro Caixa?"               │
│  Data: 06/05/2026 às 14:23                               │
│  Provedor: Anthropic (Zero Data Retention)               │
│                                                          │
│  ── Enviado ──                                           │
│   saldo_devedor:      429629.87                          │
│   taxa_mensal:        0.009631393                        │
│   prazo_meses:        189                                │
│   sistema:            "SAC"                               │
│   pergunta:           (seu texto)                        │
│                                                          │
│  ── NÃO enviado ──                                       │
│   ✓ Seu nome   ✓ CPF   ✓ Conta   ✓ Agência   ✓ IP        │
│                                                          │
│  Anthropic não usa esses dados pra treinar modelos.      │
│  [ Política da Anthropic ]                               │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões
- **A privacidade é vendida como proteção** — coerente com o guardião.
- **Lista de "NÃO enviado" é tão importante quanto a de "enviado"** — comunica disciplina.
- **Provedor de IA é Anthropic/Claude (ZDR)** — alinhado à decisão de stack.

---

## Casos de borda

### Divergência recorrente
```
Essa diferença aparece todo mês? Pode ser um padrão na
forma como o banco aplica a TR. Quer que eu monte um
resumo dos últimos 6 meses pra levar ao banco?
```

### Usuário não entende a memória de cálculo
```
Não precisa entender a conta toda. O importante: o saldo
bate (✓) ou não bate (⚠). Se não bate, eu te explico o
porquê em uma frase e te ajudo a resolver.
```

---

## Diferenças nicho × massa

| | Nicho (Quitador) | Massa (Confuso) |
|---|---|---|
| Nome da feature | Reconciliação / Audit | Conferindo o banco |
| Papel | Nice-to-have, transparência | Valor emocional central |
| Memória de cálculo | Quer ver tudo | Confia no selo; vê se quiser |
| Privacidade | Disciplina técnica | Parte da proteção emocional |

---

## Métricas que importam

| Métrica | Meta |
|---|---|
| Usuários que abrem "Conferindo o banco" | menor que outras telas, mas alto valor |
| Confiança/retenção de quem viu ≥ 1 conferência ✓ | maior que a média |
| Uso de "gerar carta" em divergências | sinal de valor de proteção |
