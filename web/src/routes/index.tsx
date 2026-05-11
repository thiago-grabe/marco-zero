import { createFileRoute, Link } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: Landing,
});

// ── Dados da seção "Seus dados são seus" ─────────────────────────────────────
// Padrão de negação direta inspirado em enzonotes.com:
// transformar compliance em declarações escaneáveis.
const privacyItems = [
  {
    verdict: "Não.",
    verdictColor: "text-loss",
    claim: "Não vendemos seus dados para bancos, corretoras ou anunciantes.",
    detail: "Nenhum lead. Nenhuma parceria comercial com instituições financeiras.",
  },
  {
    verdict: "Não.",
    verdictColor: "text-loss",
    claim: "Não usamos seu contrato para treinar modelos de IA.",
    detail:
      "Seus PDFs são processados com Zero Data Retention. O modelo nunca aprende com o seu contrato.",
  },
  {
    verdict: "Não.",
    verdictColor: "text-loss",
    claim: "Não armazenamos seu CPF.",
    detail:
      "Detectamos e removemos automaticamente antes de salvar. Mesmo que haja uma brecha, seu CPF não está lá.",
  },
  {
    verdict: "Sim.",
    verdictColor: "text-gain",
    claim: "Você exporta e apaga tudo, em 2 cliques, a qualquer hora.",
    detail:
      "ZIP com seus PDFs originais, cenários e histórico — em formato aberto. Conta excluída em 7 dias.",
  },
  {
    verdict: "Sim.",
    verdictColor: "text-gain",
    claim: "Os cálculos rodam no servidor, não na IA.",
    detail:
      "SAC, PRICE, projeções, stress tests — tudo determinístico e auditável. A IA só explica o que o motor calculou.",
  },
];

const howItWorks = [
  {
    n: "01",
    title: "Você guarda seu contrato",
    body: "Suba o PDF do DDC ou preencha manualmente. Marco Zero extrai saldo, taxa e parcelas.",
  },
  {
    n: "02",
    title: "Marco Zero entende a matemática",
    body: "Motor SAC/PRICE calcula cenários em tempo real. Veja quando quita com cada estratégia de amortização.",
  },
  {
    n: "03",
    title: "Você age no momento certo",
    body: "Coach alerta janelas de FGTS, quedas de Selic e desvios do plano. Sem precisar ficar verificando.",
  },
];

// ── Componentes ───────────────────────────────────────────────────────────────

function TimelineVisual() {
  return (
    <div className="relative flex items-center gap-0 w-full max-w-sm mx-auto mt-10 mb-2">
      {/* Linha de fundo */}
      <div className="absolute top-3 left-0 right-0 h-px bg-border" />

      {/* Início */}
      <div className="relative flex flex-col items-center flex-1">
        <div className="w-2.5 h-2.5 rounded-full bg-muted-foreground z-10" />
        <span className="text-xs text-muted-foreground mt-2">dez/2025</span>
      </div>

      {/* Hoje */}
      <div className="relative flex flex-col items-center flex-1">
        <div className="w-3 h-3 rounded-full bg-primary z-10 shadow-[0_0_8px_2px] shadow-primary/40" />
        <span className="text-xs text-primary mt-2 font-medium">hoje</span>
      </div>

      {/* Marco zero / quitação */}
      <div className="relative flex flex-col items-center flex-1">
        <div className="w-2.5 h-2.5 rounded-full bg-gain z-10" />
        <span className="text-xs text-gain mt-2 font-medium">marco zero</span>
      </div>

      {/* Original (tachado) */}
      <div className="relative flex flex-col items-center flex-1 opacity-35">
        <div className="w-2 h-2 rounded-full bg-muted-foreground z-10" />
        <span className="text-xs text-muted-foreground mt-2 line-through">2042</span>
      </div>
    </div>
  );
}

function SectionDivider({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-4 w-full">
      <div className="flex-1 h-px bg-border" />
      <span className="text-xs text-muted-foreground uppercase tracking-widest whitespace-nowrap">
        {label}
      </span>
      <div className="flex-1 h-px bg-border" />
    </div>
  );
}

// ── Página ────────────────────────────────────────────────────────────────────

function Landing() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* ── Nav ────────────────────────────────────────────────────────────── */}
      <nav className="flex items-center justify-between px-6 py-5 max-w-2xl mx-auto">
        <span className="font-serif text-base font-semibold tracking-tight">Marco Zero</span>
        <Link
          to="/dashboard"
          className="text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          Entrar
        </Link>
      </nav>

      {/* ── Hero ───────────────────────────────────────────────────────────── */}
      <section className="px-6 pt-16 pb-20 max-w-2xl mx-auto text-center">
        <p className="text-xs text-primary uppercase tracking-widest mb-6 font-medium">
          Financiamento imobiliário
        </p>

        <h1 className="font-serif text-4xl sm:text-5xl font-semibold leading-tight text-foreground mb-6">
          Cada parcela tem um plano.
          <br />
          <span className="text-muted-foreground">Cada plano tem um fim.</span>
        </h1>

        <p className="text-muted-foreground text-lg leading-relaxed mb-10 max-w-lg mx-auto">
          Marco Zero é o cofre privado do seu financiamento. Você guarda seu contrato,
          simula cenários e sabe exatamente quando quita.
        </p>

        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 bg-primary text-primary-foreground
                     px-8 py-3 rounded-md text-sm font-medium
                     hover:bg-primary/90 transition-colors"
        >
          Começar — é grátis
        </Link>

        <TimelineVisual />

        <p className="text-xs text-muted-foreground mt-4">
          De 2042 para 2029 — com disciplina e as decisões certas
        </p>
      </section>

      {/* ── Como funciona ──────────────────────────────────────────────────── */}
      <section className="px-6 py-16 max-w-2xl mx-auto">
        <SectionDivider label="Como funciona" />

        <div className="mt-12 space-y-10">
          {howItWorks.map((step) => (
            <div key={step.n} className="flex gap-6">
              <span className="font-serif text-3xl font-semibold text-border leading-none pt-1 select-none w-10 shrink-0">
                {step.n}
              </span>
              <div>
                <h3 className="font-medium text-foreground mb-1">{step.title}</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">{step.body}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Seus dados são seus ────────────────────────────────────────────── */}
      <section className="px-6 py-16 max-w-2xl mx-auto">
        <SectionDivider label="Seus dados são seus" />

        <p className="mt-8 mb-10 text-muted-foreground text-sm leading-relaxed max-w-lg">
          Dados financeiros são sensíveis. Antes de você perguntar, aqui estão as respostas.
        </p>

        <div className="space-y-0 border border-border rounded-lg overflow-hidden">
          {privacyItems.map((item, i) => (
            <div
              key={i}
              className={`px-6 py-5 flex gap-5 items-start
                ${i < privacyItems.length - 1 ? "border-b border-border" : ""}`}
            >
              {/* Verdict */}
              <span
                className={`font-serif text-base font-semibold shrink-0 w-10 pt-0.5 ${item.verdictColor}`}
              >
                {item.verdict}
              </span>

              {/* Content */}
              <div>
                <p className="text-sm font-medium text-foreground leading-snug mb-1">
                  {item.claim}
                </p>
                <p className="text-xs text-muted-foreground leading-relaxed">{item.detail}</p>
              </div>
            </div>
          ))}
        </div>

        <p className="mt-6 text-xs text-muted-foreground">
          Política de privacidade completa em menos de 1.500 palavras.{" "}
          <a href="#" className="text-foreground underline underline-offset-2">
            Ler agora
          </a>
        </p>
      </section>

      {/* ── CTA Final ──────────────────────────────────────────────────────── */}
      <section className="px-6 py-20 max-w-2xl mx-auto text-center">
        <h2 className="font-serif text-2xl font-semibold mb-4">
          Quando você quita?
        </h2>
        <p className="text-muted-foreground text-sm mb-8 max-w-sm mx-auto">
          Calcule em 90 segundos. Sem cadastro de cartão, sem compromisso.
        </p>
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 bg-primary text-primary-foreground
                     px-8 py-3 rounded-md text-sm font-medium
                     hover:bg-primary/90 transition-colors"
        >
          Ver meu plano de quitação
        </Link>
      </section>

      {/* ── Footer ─────────────────────────────────────────────────────────── */}
      <footer className="border-t border-border px-6 py-8 max-w-2xl mx-auto">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span className="font-serif">Marco Zero</span>
          <span>Conformidade LGPD · Dados no Brasil</span>
        </div>
      </footer>
    </div>
  );
}
