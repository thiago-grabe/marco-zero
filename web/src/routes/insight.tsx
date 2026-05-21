import { HomeLink } from "@/components/layout/HomeLink";
import { createFileRoute, Link, useSearch } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { useActiveContract } from "@/hooks/useContract";
import { formatBRL, formatMonthYear } from "@/lib/utils";
import { Shield, BarChart3, MessageSquare, AlertTriangle, X } from "lucide-react";
import type { DataAlert } from "@/lib/api/client";

export const Route = createFileRoute("/insight")({
  component: Insight,
  validateSearch: (search: Record<string, unknown>) => ({
    estimated: search.estimated === true || search.estimated === "true",
  }),
});

function Insight() {
  const { data: contract } = useActiveContract();
  const { estimated } = useSearch({ from: "/insight" });
  const [alertas, setAlertas] = useState<DataAlert[]>([]);
  const [dismissedAlerts, setDismissedAlerts] = useState<Set<string>>(new Set());

  useEffect(() => {
    const raw = sessionStorage.getItem("tenor-alertas");
    if (raw) {
      try { setAlertas(JSON.parse(raw)); } catch { /* */ }
      sessionStorage.removeItem("tenor-alertas");
    }
  }, []);

  if (!contract) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const juros = contract.juros_proxima;
  const amort = contract.amortizacao_mensal;
  const seguros = contract.seguros_mensal;
  const extras = contract.custos_extras_total;
  const total = contract.parcela_total;

  const pctJuros = total > 0 ? Math.round((juros / total) * 100) : 0;
  const pctAmort = total > 0 ? Math.round((amort / total) * 100) : 0;
  const pctSeguros = total > 0 ? Math.round((seguros / total) * 100) : 0;

  // Calcular anos e meses restantes
  const meses = contract.prazo_remanescente;
  const anos = Math.floor(meses / 12);
  const mesesRestantes = meses % 12;
  const tempoTexto = anos > 0
    ? `faltam ${anos} ano${anos > 1 ? "s" : ""}${mesesRestantes > 0 ? ` e ${mesesRestantes} mese${mesesRestantes > 1 ? "s" : ""}` : ""}`
    : `faltam ${mesesRestantes} mese${mesesRestantes > 1 ? "s" : ""}`;

  return (
    <div className="min-h-screen bg-background px-6 py-10 max-w-lg mx-auto">
      <div className="flex items-center justify-between mb-6">
        <HomeLink />
        <p className="text-xs text-muted-foreground">
          {contract.banco.toUpperCase()} · {contract.sistema_amortizacao}
        </p>
      </div>

      {/* Alertas de dados fora do padrão */}
      {alertas.filter((a) => !dismissedAlerts.has(a.tipo)).map((alerta) => (
        <div
          key={alerta.tipo}
          className="mb-4 border border-warning/40 rounded-lg p-4 bg-warning/5 flex gap-3 items-start"
        >
          <AlertTriangle size={16} className="text-warning shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm text-foreground leading-relaxed">{alerta.mensagem}</p>
          </div>
          <button
            onClick={() => setDismissedAlerts((s) => new Set(s).add(alerta.tipo))}
            className="text-muted-foreground hover:text-foreground shrink-0"
          >
            <X size={14} />
          </button>
        </div>
      ))}

      {/* Hero — data de quitação */}
      <div className="text-center mb-10">
        <p className="text-muted-foreground text-sm mb-2">Você se livra disso em</p>
        <p className="font-serif text-5xl font-semibold text-primary leading-none mb-2">
          {formatMonthYear(contract.data_quitacao)}
        </p>
        <p className="text-muted-foreground text-sm">{tempoTexto}</p>
      </div>

      {/* Barra visual da composição da parcela */}
      <div className="border border-border rounded-lg p-5 mb-8">
        <p className="text-xs text-muted-foreground mb-4">
          Da sua parcela de {formatBRL(total)}:
        </p>

        <div className="space-y-3">
          <BarRow
            label="são juros"
            value={formatBRL(juros)}
            pct={pctJuros}
            color="bg-loss"
            textColor="text-loss"
          />
          <BarRow
            label="abatem a dívida"
            value={formatBRL(amort)}
            pct={pctAmort}
            color="bg-gain"
            textColor="text-gain"
          />
          <BarRow
            label="são seguros"
            value={formatBRL(seguros)}
            pct={pctSeguros}
            color="bg-muted-foreground/30"
            textColor="text-muted-foreground"
          />
          {extras > 0 && (
            <BarRow
              label="custos extras"
              value={formatBRL(extras)}
              pct={total > 0 ? Math.round((extras / total) * 100) : 0}
              color="bg-muted-foreground/20"
              textColor="text-muted-foreground"
            />
          )}
        </div>

        <p className="text-xs text-muted-foreground mt-4 border-t border-border pt-3">
          <span className="text-foreground font-medium">{pctJuros}% da sua parcela são juros.</span>{" "}
          Só {pctAmort}% abate a dívida de verdade.
        </p>
      </div>

      {/* Hooks — próximos passos */}
      <div className="space-y-3 mb-8">
        <p className="text-xs text-muted-foreground uppercase tracking-widest mb-1">E agora?</p>

        <Link
          to="/scenarios"
          className="flex items-center gap-3 p-4 border border-border rounded-lg
                     hover:border-primary/40 hover:bg-primary/5 transition-all group"
        >
          <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center shrink-0
                          group-hover:bg-primary/20 transition-colors">
            <BarChart3 size={16} className="text-primary" />
          </div>
          <div>
            <p className="text-sm text-foreground font-medium">Ver o que muda se eu adiantar</p>
            <p className="text-xs text-muted-foreground">Simule: "R$ 200 a mais por mês cortam quantos anos?"</p>
          </div>
        </Link>

        <Link
          to="/chat"
          search={{ scenario: undefined }}
          className="flex items-center gap-3 p-4 border border-border rounded-lg
                     hover:border-primary/40 hover:bg-primary/5 transition-all group"
        >
          <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center shrink-0
                          group-hover:bg-primary/20 transition-colors">
            <MessageSquare size={16} className="text-primary" />
          </div>
          <div>
            <p className="text-sm text-foreground font-medium">Perguntar pra IA sobre meu contrato</p>
            <p className="text-xs text-muted-foreground">"Por que tão pouco abate a dívida?"</p>
          </div>
        </Link>

        <Link
          to="/dashboard"
          className="flex items-center gap-3 p-4 border border-border rounded-lg
                     hover:border-primary/40 hover:bg-primary/5 transition-all group"
        >
          <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center shrink-0
                          group-hover:bg-primary/20 transition-colors">
            <Shield size={16} className="text-primary" />
          </div>
          <div>
            <p className="text-sm text-foreground font-medium">Ir para o painel completo</p>
            <p className="text-xs text-muted-foreground">Dashboard com KPIs, cenários e chat</p>
          </div>
        </Link>
      </div>

      {/* Estimated values warning */}
      {estimated && (
        <div className="border border-warning/30 rounded-lg p-4 bg-warning/5 mb-6">
          <p className="text-xs text-warning font-medium mb-1">Alguns valores foram estimados</p>
          <p className="text-xs text-muted-foreground">
            Para ter os números exatos, suba o demonstrativo do banco (DDC).{" "}
            <Link to="/onboarding" className="text-foreground underline underline-offset-2">
              Preencher dados completos
            </Link>
          </p>
        </div>
      )}

      {/* Footer */}
      <p className="text-center text-xs text-muted-foreground mt-6">
        Números calculados pelo motor SAC. A IA não participa desta conta.
      </p>
    </div>
  );
}

function BarRow({
  label, value, pct, color, textColor,
}: {
  label: string; value: string; pct: number; color: string; textColor: string;
}) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className={`text-xs ${textColor}`}>{value} {label}</span>
        <span className="text-xs text-muted-foreground">{pct}%</span>
      </div>
      <div className="h-2 bg-border rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full ${color} transition-all`}
          style={{ width: `${Math.max(pct, 2)}%` }}
        />
      </div>
    </div>
  );
}
