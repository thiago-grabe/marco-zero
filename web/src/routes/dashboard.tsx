import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { useActiveContract, useContracts } from "@/hooks/useContract";
import { useContractStore } from "@/stores/contract";
import { scenariosApi } from "@/lib/api/client";
import { formatBRL, formatMonthYear } from "@/lib/utils";

export const Route = createFileRoute("/dashboard")({
  component: Dashboard,
});

function Dashboard() {
  const navigate = useNavigate();
  const { authenticated, logout } = useAuth();
  const { data: contracts, isLoading: loadingContracts, isError: contractsError } = useContracts();
  const { data: contract, isLoading: loadingContract } = useActiveContract();
  const { activeContractId, setActiveContractId } = useContractStore();

  // Redirecionar para login se não autenticado ou se query falhou com 401
  useEffect(() => {
    if (!authenticated || contractsError) navigate({ to: "/login" });
  }, [authenticated, contractsError, navigate]);

  // Quando contratos carregam: se não tem ativo, usar o primeiro; se não tem nenhum, ir para onboarding
  useEffect(() => {
    if (!loadingContracts && contracts !== undefined) {
      if (contracts.length === 0) {
        navigate({ to: "/onboarding" });
      } else if (!activeContractId) {
        setActiveContractId(contracts[0].id);
      }
    }
  }, [contracts, loadingContracts, activeContractId, setActiveContractId, navigate]);

  // Cenários do contrato ativo
  const { data: scenarios } = useQuery({
    queryKey: ["scenarios", activeContractId],
    queryFn: () => scenariosApi.list(activeContractId!),
    enabled: !!activeContractId && authenticated,
    retry: false,
  });

  if (!authenticated || loadingContracts || loadingContract) {
    return <LoadingScreen />;
  }

  if (!contract) return <LoadingScreen />;

  // Barra de progresso
  const dataInicio = contract.data_inicio
    ? new Date(contract.data_inicio + "T00:00:00")
    : null;
  const dataQuitacao = new Date(contract.data_quitacao + "T00:00:00");
  const hoje = new Date();

  const totalDias = dataInicio
    ? (dataQuitacao.getTime() - dataInicio.getTime()) / 86400000
    : null;
  const diasDecorridos = dataInicio
    ? (hoje.getTime() - dataInicio.getTime()) / 86400000
    : null;
  const progressoPct =
    totalDias && diasDecorridos
      ? Math.min(100, Math.max(0, (diasDecorridos / totalDias) * 100))
      : null;

  // Próximo cenário em execução (ou o primeiro salvo)
  const cenarioDestaque =
    scenarios?.find((s) => s.status === "em_execucao") ?? scenarios?.[0];

  return (
    <div className="min-h-screen bg-background">
      {/* Nav */}
      <nav className="flex items-center justify-between px-6 py-4 border-b border-border">
        <span className="font-serif text-sm font-semibold">Marco Zero</span>
        <div className="flex items-center gap-4">
          {contracts && contracts.length > 1 && (
            <select
              value={activeContractId ?? ""}
              onChange={(e) => setActiveContractId(e.target.value)}
              className="text-xs bg-transparent text-muted-foreground border border-border
                         rounded px-2 py-1 focus:outline-none"
            >
              {contracts.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.apelido || "Contrato"}
                </option>
              ))}
            </select>
          )}
          <Link to="/chat" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
            Chat IA
          </Link>
          <Link to="/scenarios" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
            Cenários
          </Link>
          <button
            onClick={() => { logout(); navigate({ to: "/login" }); }}
            className="text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            Sair
          </button>
        </div>
      </nav>

      <div className="max-w-2xl mx-auto px-6 py-10">
        {/* Hero — data de quitação */}
        <div className="mb-10">
          <p className="text-xs text-muted-foreground uppercase tracking-widest mb-3">
            {contract.apelido ?? "Contrato ativo"} · {contract.banco.toUpperCase()} · {contract.sistema_amortizacao}
          </p>
          <p className="font-serif text-5xl sm:text-6xl font-semibold text-foreground leading-none mb-2">
            {formatMonthYear(contract.data_quitacao)}
          </p>
          <p className="text-muted-foreground text-sm">
            data de quitação no plano atual
          </p>
        </div>

        {/* Linha do tempo */}
        {progressoPct !== null && (
          <div className="mb-10">
            <div className="h-1 bg-border rounded-full overflow-hidden">
              <div
                className="h-full bg-primary rounded-full transition-all"
                style={{ width: `${progressoPct}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              {progressoPct.toFixed(1)}% do caminho percorrido
            </p>
          </div>
        )}

        {/* KPIs */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <KpiCard label="Saldo devedor" value={formatBRL(contract.saldo_devedor)} />
          <KpiCard
            label="Próxima parcela"
            value={formatBRL(contract.parcela_total)}
            sub={new Date(contract.data_proxima_parcela + "T00:00:00").toLocaleDateString("pt-BR")}
          />
          <KpiCard label="Parcelas restantes" value={String(contract.prazo_remanescente)} />
        </div>

        {/* Detalhe financeiro */}
        <div className="border border-border rounded-lg p-5 mb-8">
          <p className="text-xs text-muted-foreground uppercase tracking-widest mb-4">
            Composição da parcela
          </p>
          <div className="space-y-2">
            <Row label="Amortização" value={formatBRL(contract.amortizacao_mensal)} />
            <Row label="Juros" value={formatBRL(contract.juros_proxima)} accent />
            <Row label="Seguros (MIP + DFI)" value={formatBRL(contract.seguros_mensal)} />
            <div className="border-t border-border pt-2 mt-2">
              <Row label="Total" value={formatBRL(contract.parcela_total)} bold />
            </div>
          </div>
        </div>

        {/* Cenário em destaque */}
        {cenarioDestaque ? (
          <div className="border border-primary/30 rounded-lg p-5 bg-primary/5 mb-6">
            <p className="text-xs text-primary uppercase tracking-widest mb-3">
              {cenarioDestaque.status === "em_execucao" ? "Plano em execução" : "Cenário salvo"}
            </p>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-sm text-foreground mb-1">{cenarioDestaque.nome}</p>
                <p className="text-xs text-muted-foreground">
                  {cenarioDestaque.aporte_mensal_extra > 0 &&
                    `+${formatBRL(cenarioDestaque.aporte_mensal_extra)}/mês`}
                  {cenarioDestaque.aporte_anual_extra > 0 &&
                    ` · +${formatBRL(cenarioDestaque.aporte_anual_extra)}/ano`}
                </p>
              </div>
              <div className="text-right">
                <p className="font-serif text-lg text-gain">
                  {formatMonthYear(cenarioDestaque.projecao.data_quitacao)}
                </p>
                <p className="text-xs text-muted-foreground">
                  economia de {formatBRL(cenarioDestaque.projecao.total_juros_economizados)}
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="border border-dashed border-border rounded-lg p-5 text-center mb-6">
            <p className="text-sm text-muted-foreground mb-3">
              Simule o que acontece se você amortizar mais.
            </p>
            <Link
              to="/scenarios"
              className="text-xs text-primary hover:text-primary/80 transition-colors"
            >
              Criar cenário →
            </Link>
          </div>
        )}

        {/* Ações rápidas */}
        <div className="flex gap-3">
          <Link
            to="/scenarios"
            className="flex-1 border border-border rounded-md py-3 text-sm text-center
                       text-muted-foreground hover:text-foreground hover:border-foreground/30 transition-colors"
          >
            Ver cenários
          </Link>
          <Link
            to="/onboarding"
            className="border border-border rounded-md py-3 px-4 text-sm
                       text-muted-foreground hover:text-foreground hover:border-foreground/30 transition-colors"
          >
            + Contrato
          </Link>
        </div>
      </div>
    </div>
  );
}

// ── Sub-componentes ────────────────────────────────────────────────────────────

function LoadingScreen() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="space-y-3 text-center">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-xs text-muted-foreground">Carregando seu contrato…</p>
      </div>
    </div>
  );
}

function KpiCard({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="border border-border rounded-lg p-4">
      <p className="text-xs text-muted-foreground mb-2">{label}</p>
      <p className="font-serif text-lg text-foreground tabular-nums">{value}</p>
      {sub && <p className="text-xs text-muted-foreground mt-1">{sub}</p>}
    </div>
  );
}

function Row({
  label, value, accent = false, bold = false,
}: {
  label: string; value: string; accent?: boolean; bold?: boolean;
}) {
  return (
    <div className="flex justify-between items-center">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span
        className={`font-serif text-sm tabular-nums ${
          bold ? "text-foreground font-semibold" : accent ? "text-loss" : "text-foreground"
        }`}
      >
        {value}
      </span>
    </div>
  );
}
