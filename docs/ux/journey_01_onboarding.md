# Marco Zero — Jornada 1: Onboarding

> **Objetivo**: do landing ao primeiro insight em < 90 segundos.
> **Princípio guia**: o usuário sai do onboarding sentindo que o produto **já entendeu o contrato dele**, não que ele precisa ensinar o produto.

---

## Arco emocional

```
Curiosidade → Cautela → Pequeno esforço → Reconhecimento → Confiança
   landing      auth       upload          extração         primeiro insight
```

Cada tela é uma micro-transação de confiança. O usuário dá um pouco de informação; o produto devolve algo concreto antes de pedir o próximo pedaço.

---

## Tela 0.1 — Landing page (não autenticada)

> Implementada em `web/src/routes/index.tsx`
> Inspiração de layout e copy: enzonotes.com — padrão de negação direta para privacidade

```
┌──────────────────────────────────────────────────────────┐
│  Marco Zero                              [Entrar →]      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│              Financiamento imobiliário                   │  ← label âmbar, caps
│                                                          │
│         Cada parcela tem um plano.                       │  ← serifa grande
│         Cada plano tem um fim.                           │  ← muted
│                                                          │
│    Marco Zero é o cofre privado do seu                   │
│    financiamento. Você guarda seu contrato,              │
│    simula cenários e sabe quando quita.                  │
│                                                          │
│         [ Começar — é grátis ]                           │
│                                                          │
│   ●————●————●·············○                              │  ← timeline CSS
│  dez  hoje  marco zero   2042                            │  ← âmbar, gain, tachado
│                                                          │
│    De 2042 para 2029 — com disciplina e as decisões      │
│                                                          │
│                                                          │
│  ────────── Como funciona ───────────────────────────    │
│                                                          │
│  01  Você guarda seu contrato                            │
│      Suba o PDF do DDC ou preencha manualmente.          │
│                                                          │
│  02  Marco Zero entende a matemática                     │
│      Motor SAC/PRICE calcula cenários em tempo real.     │
│                                                          │
│  03  Você age no momento certo                           │
│      Coach alerta FGTS, Selic, desvios do plano.         │
│                                                          │
│                                                          │
│  ────────── Seus dados são seus ─────────────────────    │
│                                                          │
│  ┌────────────────────────────────────────────────┐      │
│  │ Não.  Não vendemos seus dados para bancos.     │      │  ← "Não." em vermelho
│  ├────────────────────────────────────────────────┤      │
│  │ Não.  Não usamos seu contrato para treinar IA. │      │
│  ├────────────────────────────────────────────────┤      │
│  │ Não.  Não armazenamos seu CPF.                 │      │
│  ├────────────────────────────────────────────────┤      │
│  │ Sim.  Você exporta e apaga tudo, 2 cliques.    │      │  ← "Sim." em verde
│  ├────────────────────────────────────────────────┤      │
│  │ Sim.  Cálculos rodam no servidor, não na IA.   │      │
│  └────────────────────────────────────────────────┘      │
│                                                          │
│  Política de privacidade em menos de 1.500 palavras.     │
│                                                          │
│                                                          │
│  ────────────────────────────────────────────────────    │
│                                                          │
│         Quando você quita?                               │
│                                                          │
│    Calcule em 90 segundos. Sem cartão, sem compromisso.  │
│                                                          │
│         [ Ver meu plano de quitação ]                    │
│                                                          │
│  ────────────────────────────────────────────────────    │
│  Marco Zero          Conformidade LGPD · Dados no Brasil │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Tagline em dois tons**: primeira linha em foreground (peso), segunda em muted (eco). Cria ritmo sem usar duas fontes diferentes.
- **Timeline CSS** no hero: visual único e on-brand que comunica a promessa ("de 2042 para 2029") sem precisar de imagem.
- **Seção "Seus dados são seus"** com padrão de negação direta (inspirado em enzonotes.com): cada item começa com "Não." ou "Sim." em serif colorido. Escaneável em 10 segundos. Sem juridiquês.
- **Label âmbar no topo** ("Financiamento imobiliário"): ancora o contexto antes do hero. Evita confusão sobre o que o produto é.
- **CTA único**: "Começar — é grátis". CTA final reframed: "Ver meu plano de quitação" — mais específico que "Começar", diminui fricção por prometer uma resposta concreta.
- **Sem social proof inventado**. Sem ícones decorativos. Sem gradientes.

---

## Tela 0.2 — Autenticação

```
┌──────────────────────────────────────────────────────────┐
│  ← Voltar                                                │
│                                                          │
│                                                          │
│        Crie sua conta                                    │
│                                                          │
│        E-mail                                            │
│        ┌────────────────────────────────────────┐        │
│        │ thiago@…                               │        │
│        └────────────────────────────────────────┘        │
│                                                          │
│        ┌────────────────────────────────────────┐        │
│        │  Receber link de acesso                │        │
│        └────────────────────────────────────────┘        │
│                                                          │
│        ─── ou ───                                        │
│                                                          │
│        Continuar com Google                              │
│        Continuar com Apple                               │
│                                                          │
│                                                          │
│        ☐ Li e aceito termos de uso e política de         │
│          privacidade. [ler — 1500 palavras]              │
│                                                          │
│                                                          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Magic link como default**. Sem senha pra vazar, sem senha pra esquecer. Mais seguro e mais rápido.
- **OAuth como conveniência**, não como única opção. Quem não quer Google/Apple tem caminho próprio.
- **Checkbox NÃO pré-marcado**. Usuário marca ativamente. Link "ler" abre a política em modal lateral, não em nova aba — ele não perde contexto.
- **Sem opt-in de marketing aqui**. Será oferecido depois, com contexto.
- **Sem CAPTCHA visível**. Rate limiting silencioso no servidor. CAPTCHA só aparece se houver sinal claro de ataque.

---

## Tela 0.3 — Boas-vindas (após primeiro login)

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│                                                          │
│              Olá, Thiago.                                │
│                                                          │
│              Vamos guardar seu                           │
│              primeiro contrato.                          │
│                                                          │
│              ─────────────                               │
│                                                          │
│              Em 90 segundos você verá                    │
│              quando termina de pagar.                    │
│                                                          │
│                                                          │
│              ┌──────────────┐                            │
│              │  Começar     │                            │
│              └──────────────┘                            │
│                                                          │
│                                                          │
│              Pular agora                                 │
│              Você pode adicionar depois.                 │
│                                                          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **"Olá, [nome]"** se conseguiu o nome via OAuth. Senão, "Olá." apenas — não inventa.
- **Promessa concreta** ("90 segundos", "quando termina de pagar"). Cria expectativa que o produto cumpre.
- **"Pular agora"** é discreto mas presente. Sem cor de alerta, sem culpa.
- **Sem barra de progresso ainda.** Aparece a partir da próxima tela, quando o usuário já optou por começar.

---

## Tela 0.4 — Seleção de banco

```
┌──────────────────────────────────────────────────────────┐
│  ●○○○○                                                   │
│                                                          │
│  Onde está seu contrato?                                 │
│                                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                   │
│  │         │  │         │  │         │                   │
│  │  Caixa  │  │  Itaú   │  │   BB    │                   │
│  │         │  │         │  │         │                   │
│  └─────────┘  └─────────┘  └─────────┘                   │
│                                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                   │
│  │         │  │         │  │         │                   │
│  │Bradesco │  │Santander│  │  Outro  │                   │
│  │         │  │         │  │         │                   │
│  └─────────┘  └─────────┘  └─────────┘                   │
│                                                          │
│                                                          │
│  ⓘ Suporte completo para os 5 maiores bancos.           │
│     Outros bancos: entrada manual.                       │
│                                                          │
│  ← Voltar                                                │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Cards visuais com logo** (não só texto). Reconhecimento é mais rápido que leitura.
- **Click no banco já avança.** Sem botão "próximo". 1 click a menos.
- **Caveat sobre cobertura visível.** Honestidade gera confiança.
- **"Outro" não é desclassificado.** Tem o mesmo peso visual dos outros — entrada manual é caminho legítimo.

---

## Tela 0.5 — Decisão: PDF ou manual

```
┌──────────────────────────────────────────────────────────┐
│  ●●○○○                                                   │
│                                                          │
│  Você tem o DDC do Itaú em PDF?                          │
│                                                          │
│  O DDC (Demonstrativo Descritivo de Crédito) tem todo    │
│  o histórico do seu contrato — parcelas, operações,      │
│  saldo. É o documento mais completo.                     │
│                                                          │
│  📎 Como pegar no app do Itaú? [tutorial]                │
│                                                          │
│                                                          │
│  ┌─────────────────────────┐  ┌─────────────────────────┐│
│  │                         │  │                         ││
│  │   Tenho o PDF           │  │   Não tenho             ││
│  │   Vou enviar            │  │   Quero entrar          ││
│  │                         │  │   manualmente           ││
│  │   Recomendado           │  │                         ││
│  │   ~30 segundos          │  │   ~2 minutos            ││
│  │                         │  │                         ││
│  └─────────────────────────┘  └─────────────────────────┘│
│                                                          │
│  ← Voltar                                                │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Educa sem ser professoral.** Uma frase explica o termo "DDC".
- **Tutorial é link, não modal.** Quem precisa, abre. Quem não, segue.
- **Tempo estimado em cada caminho.** Tira dúvida ("quanto isso vai me tomar?").
- **"Recomendado" é badge sutil**, não imposição. Alguns usuários genuinamente não têm o DDC.

---

## Tela 0.6a — Upload do DDC (caminho com PDF)

```
┌──────────────────────────────────────────────────────────┐
│  ●●●○○                                                   │
│                                                          │
│  Suba o DDC do Itaú                                      │
│                                                          │
│  ┌──────────────────────────────────────────────┐        │
│  │                                              │        │
│  │                                              │        │
│  │              📄                              │        │
│  │                                              │        │
│  │     Arraste o PDF aqui                       │        │
│  │     ou clique para escolher                  │        │
│  │                                              │        │
│  │                                              │        │
│  └──────────────────────────────────────────────┘        │
│                                                          │
│                                                          │
│  🔒 Seu PDF entra direto no seu cofre privado.           │
│     CPF é detectado e removido antes de armazenar.       │
│     [Saiba como]                                         │
│                                                          │
│  ← Voltar                                                │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Estado durante o processamento

```
┌──────────────────────────────────────────────────────────┐
│  ●●●○○                                                   │
│                                                          │
│  📄 DDC_05052026.pdf                                     │
│                                                          │
│  ✓ CPF detectado e removido                              │
│  ✓ Banco identificado: Itaú                              │
│  ✓ Saldo extraído: R$ 429.629,87                         │
│  ✓ 189 parcelas mapeadas                                 │
│  ✓ 6 operações históricas                                │
│  ◐ Validando consistência…                               │
│                                                          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Cada checkmark é um momento de confiança.** Aparecem em sequência (~200-400ms entre eles), não tudo de uma vez. Cria ritmo.
- **CPF redaction é o primeiro check** — antes de qualquer outra extração. Comunica prioridade de privacidade.
- **Validação semântica é etapa visível.** Se o saldo estiver fora de range razoável, aparece em amarelo, não verde.
- **Em caso de erro de parser**, queda graciosa: "Não conseguimos extrair tudo automaticamente. Vamos pedir alguns dados."

---

## Tela 0.6b — Entrada manual (caminho sem PDF)

```
┌──────────────────────────────────────────────────────────┐
│  ●●●○○                                                   │
│                                                          │
│  Vamos preencher o essencial                             │
│  Você consulta no app do banco.                          │
│                                                          │
│  ─── Sobre seu contrato ───────────────────────          │
│                                                          │
│  Saldo devedor atual                                     │
│  ┌──────────────────────┐                                │
│  │ R$                   │                                │
│  └──────────────────────┘                                │
│                                                          │
│  Taxa de juros mensal                                    │
│  ┌──────────────────────┐                                │
│  │            %         │      ⓘ Geralmente entre        │
│  │                      │        0,7% e 1,1%             │
│  └──────────────────────┘                                │
│                                                          │
│  Sistema de amortização                                  │
│  ⦿ SAC    ⦾ Price                                        │
│                                                          │
│  ─── Sobre as parcelas ────────────────────────          │
│                                                          │
│  Parcelas restantes                                      │
│  ┌──────────────────────┐                                │
│  │                      │                                │
│  └──────────────────────┘                                │
│                                                          │
│  Valor da próxima parcela                                │
│  ┌──────────────────────┐                                │
│  │ R$                   │                                │
│  └──────────────────────┘                                │
│                                                          │
│  Vencimento da próxima parcela                           │
│  ┌──────────────────────┐                                │
│  │ DD / MM / AAAA       │                                │
│  └──────────────────────┘                                │
│                                                          │
│  ─── Apelido (opcional) ───────────────────────          │
│                                                          │
│  Como chamar este contrato?                              │
│  ┌──────────────────────────────────┐                    │
│  │ Apartamento Contagem             │                    │
│  └──────────────────────────────────┘                    │
│                                                          │
│  ┌──────────────────────────┐                            │
│  │  Continuar               │                            │
│  └──────────────────────────┘                            │
│                                                          │
│  ← Voltar                                                │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Tudo em uma única tela com scroll.** Steps fragmentados criam fricção desnecessária.
- **Hints contextuais** ao lado de campos confusos. "Geralmente entre 0,7% e 1,1%" tira a dúvida do usuário inseguro.
- **Validação inline.** Se o usuário coloca taxa de 5% (irreal), aparece alerta amarelo: "Taxa fora do esperado. Confirma?"
- **Apelido opcional**, mas útil — usuário pode ter mais contratos no futuro.

---

## Tela 0.7 — Conferência

```
┌──────────────────────────────────────────────────────────┐
│  ●●●●○                                                   │
│                                                          │
│  Confere o que vamos guardar:                            │
│                                                          │
│  Apelido           Apartamento Contagem                  │
│  Banco             Itaú                                  │
│  Contrato          10300539502                           │
│                                                          │
│  Saldo devedor     R$ 429.629,87                         │
│  Taxa              0,9631% a.m. (12,19% a.a.)            │
│  Sistema           SAC                                   │
│                                                          │
│  Parcelas restantes      189                             │
│  Próxima parcela         R$ 6.578,27                     │
│  Vencimento              21/05/2026                      │
│  Última parcela          21/01/2042                      │
│                                                          │
│  ─────────────────────────────────────                   │
│                                                          │
│  ⓘ Algum valor errado? Edite antes de salvar.            │
│                                                          │
│  [ Editar valores ]    [ Tudo certo, guardar ]           │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **Confirmação explícita é etapa**, não ato passivo. Persistir só após confirmar.
- **Editar valores** volta para a tela 0.6 (manual) ou abre editor inline (caso PDF).
- **"Tudo certo, guardar"** é o CTA principal — mais largo, mais escuro.

---

## Tela 0.8 — Primeiro insight

```
┌──────────────────────────────────────────────────────────┐
│  ●●●●●                                                   │
│                                                          │
│                                                          │
│        Pronto, Thiago.                                   │
│                                                          │
│        Olha o que descobrimos:                           │
│                                                          │
│                                                          │
│        ●  Você quita em 21/01/2042                       │
│                                                          │
│        ●  Sua taxa (12,19% a.a.) está                    │
│           ~60bps acima da média de mercado em 2026       │
│                                                          │
│        ●  6 amortizações em 5 meses —                    │
│           padrão raro de disciplina                      │
│                                                          │
│                                                          │
│        ┌──────────────────────────┐                      │
│        │  Ver meu painel          │                      │
│        └──────────────────────────┘                      │
│                                                          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Decisões

- **3 insights, sempre.** Mais que isso vira ruído; menos parece superficial.
- **Cada insight é específico ao contrato real.** Não pode ser genérico ("Você tem um financiamento") — perde o efeito de "eles já me entenderam".
- **Tom factual, não bajulador.** "Padrão raro de disciplina" é elogio honesto, não puxa-saco.
- **Insights variam.** Se o usuário não fez amortizações, o terceiro insight é diferente — talvez "Quitando como hoje, você paga R$ 391k em juros adicionais. Veja como reduzir."

---

## O que acontece se o usuário pula

Se em qualquer ponto após a Tela 0.3 ele clica "pular agora":

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│                                                          │
│        Tudo bem.                                         │
│                                                          │
│        Seu cofre está pronto e vazio.                    │
│        Você pode adicionar contratos a qualquer          │
│        momento, sem perder nada.                         │
│                                                          │
│        ┌──────────────────────────┐                      │
│        │  Ir para o painel        │                      │
│        └──────────────────────────┘                      │
│                                                          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

E o dashboard recebe o usuário com estado vazio (não vazio-vazio — vazio-acolhedor):

```
┌──────────────────────────────────────────────────────────┐
│  Marco Zero                          [perfil] [⚙]        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│        Seu cofre está pronto.                            │
│                                                          │
│        Adicione seu primeiro contrato para               │
│        começar a usar.                                   │
│                                                          │
│        ┌──────────────────────────┐                      │
│        │  Adicionar contrato      │                      │
│        └──────────────────────────┘                      │
│                                                          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Casos de borda

### Usuário sobe PDF que não é DDC

```
⚠ Não conseguimos identificar este PDF como um DDC.

   Pode ser:
   • Um extrato (não tem todas as parcelas)
   • Um boleto de parcela
   • Outro documento bancário

   Você quer:
   [Tentar outro PDF]    [Entrar manualmente]
```

### Parser detecta valores fora de range

```
⚠ Algo parece estranho.

   Encontramos taxa mensal de 4,5% — bem acima do
   normal (0,7% a 1,1%). Pode ser que:
   • O parser leu errado
   • É um financiamento de outro tipo (não imobiliário)

   [Editar manualmente]    [Está correto, prosseguir]
```

### Usuário abandona no meio (volta depois)

Marco Zero salva o progresso na tela 0.4 em diante. Voltar abre direto na última tela alcançada, com mensagem leve no topo:

```
ⓘ Você estava cadastrando seu Itaú. Vamos continuar?
   [Continuar de onde parei]    [Recomeçar]
```

---

## Métricas que importam

| Métrica | Meta |
|---|---|
| Tempo médio do landing ao primeiro insight | < 90s |
| Taxa de conclusão do onboarding | > 70% |
| Taxa de pular o onboarding | < 15% |
| Erros de parser que caem em manual | < 10% |
| Taxa de retorno em 7 dias | > 50% |

---

## Relação com privacidade

Pontos do onboarding onde a privacidade é tornada visível:

- **Tela 0.1**: "🔒 Seus dados ficam no seu cofre" — mensagem clara.
- **Tela 0.2**: checkbox de termos NÃO pré-marcado. Sem opt-in de marketing.
- **Tela 0.6a**: "✓ CPF detectado e removido" — primeiro check, antes de tudo.
- **Tela 0.6a**: "🔒 Seu PDF entra direto no seu cofre privado" — repete mensagem.

A privacidade aparece em **3 momentos** do onboarding, sem virar palestra. Quem repara, repara. Quem não, ainda absorve subliminarmente.
