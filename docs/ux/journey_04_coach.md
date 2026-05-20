# Tenor — Jornada 4: Coach / Avisos (versão massa)

> **Objetivo**: avisar **só do que importa**, em linguagem de tranquilidade — sem transformar o app em mais uma fonte de ansiedade e notificações.
> **Princípio guia**: para a massa, 9 alertas viram ruído e desinstalação. Menos é mais: 3–4 avisos que protegem ou abrem oportunidade real.

---

## Modelo mental do usuário (massa)

> "Não quero ser bombardeado. Só me avisa se tiver algo que eu preciso saber — tipo a parcela chegando, ou se o banco fez alguma coisa estranha."

---

## Princípios duros

1. **Quatro avisos por padrão, não nove.** O resto fica em "avançado".
2. **Cada aviso é proteção ou oportunidade**, nunca tarefa ou cobrança.
3. **Linguagem de gente.** "O banco mudou seu saldo", não "desvio de reconciliação detectado".
4. **Frequência respeitosa.** Resumo, não pingos o dia todo. Modo férias disponível.
5. **Coach não vende.** Sem "experimente o Plus" piscando.

---

## Tela 4.1 — Central de avisos

```
┌──────────────────────────────────────────────────────────┐
│  ←  Avisos                                               │
│                                                          │
│  A gente te avisa só do que importa:                     │
│                                                          │
│  ✓ Parcela chegando                      [ Ligado ]      │
│    3 dias antes de vencer                                │
│                                                          │
│  ✓ O banco mudou algo no seu saldo       [ Ligado ]      │
│    Se o valor sair do esperado, você fica sabendo        │
│                                                          │
│  ✓ Sua taxa está acima do mercado        [ Ligado ]      │
│    Pode valer a pena conversar sobre portabilidade       │
│                                                          │
│  ✓ Liberou usar o FGTS                    [ Ligado ]      │
│    A cada 2 anos você pode abater com o FGTS             │
│                                                          │
│  ── Onde receber ──────────────────────────              │
│  No app   [✓]      E-mail  [✓]      SMS  [ ]             │
│                                                          │
│  Avançado (mais avisos, frequência fina) →               │
│  Modo férias: pausar tudo até [ DD/MM/AAAA ]             │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões
- **Quatro avisos visíveis**; os 5 do nicho (revisão trimestral, aniversário de ensaio, desvios finos, etc.) ficam em "avançado".
- **Modo férias** atende quem não quer ser incomodado.

---

## Tela 4.2 — Aviso: "o banco mudou seu saldo" (o mais valioso)

```
┌──────────────────────────────────────────────────────────┐
│  🔔  O saldo do seu financiamento mudou                  │
│                                                          │
│  O banco está mostrando R$ 1.234 a mais do que a         │
│  gente esperava neste mês.                               │
│                                                          │
│  Antes de assustar: na maioria das vezes é a TR do mês.  │
│  Quer conferir junto comigo?                             │
│                                                          │
│  [ Conferir agora ]   [ Depois ]                         │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões
- **Não alarma.** Sempre traz a causa mais provável antes de sugerir problema.
- **Leva direto para o guardião** (jornada 7).

---

## Tela 4.3 — Aviso: "sua taxa está acima do mercado"

```
┌──────────────────────────────────────────────────────────┐
│  🔔  Sua taxa pode estar alta                            │
│                                                          │
│  Seu contrato está em 12,19% ao ano. A média de mercado  │
│  pra financiamento parecido hoje é ~X%.                  │
│                                                          │
│  Pode valer a pena pedir portabilidade (trocar de        │
│  banco mantendo o imóvel). A gente te mostra a conta —   │
│  e não indica banco nem ganha comissão por isso.         │
│                                                          │
│  [ Ver se compensa portar ]                              │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões
- **Reafirma a neutralidade** ("não indica banco, não ganha comissão") — base da confiança da massa.
- Liga para a simulação de portabilidade (jornada 5/2).

---

## Tela 4.4 — Aviso: FGTS liberado

```
┌──────────────────────────────────────────────────────────┐
│  🔔  Você pode usar o FGTS agora                         │
│                                                          │
│  Passaram 2 anos desde o último uso. Você pode usar o    │
│  saldo do FGTS pra abater o financiamento.               │
│                                                          │
│  Se você adicionar quanto tem de FGTS, eu simulo o       │
│  efeito (encurtar prazo ou diminuir parcela).            │
│                                                          │
│  [ Simular com meu FGTS ]                                │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Casos de borda

### Excesso de avisos no mesmo dia
```
Agrupar em um único resumo diário. Nunca mais de
1 push por dia para avisos informativos.
```

### Usuário desativou tudo
```
Ok, silêncio total. A gente continua acompanhando seu
financiamento por dentro — quando quiser, é só reativar.
```

---

## Diferenças nicho × massa

| | Nicho (Quitador) | Massa (Confuso) |
|---|---|---|
| Nº de alertas padrão | 9 (granular) | 4 |
| Tom | "desvio do plano", "aniversário de cenário" | "o banco mudou seu saldo" |
| Objetivo | Otimizar timing de aportes | Proteger e tranquilizar |

---

## Métricas que importam

| Métrica | Meta |
|---|---|
| Opt-out de notificações | < 15% |
| Clique em aviso "banco mudou saldo" | alto = valor percebido |
| Desinstalação atribuível a excesso de aviso | ~0 |
