import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { useActiveContract, useContracts } from "@/hooks/useContract";
import { useContractStore } from "@/stores/contract";
import { scenariosApi } from "@/lib/api/client";
import { formatBRL, formatMonthYear } from "@/lib/utils";
import { MessageSquare, Sparkles, BarChart3, Plus, TrendingDown } from "lucide-react";

export const Route = createFileRoute("/dashboard")({
  component: Dashboard,
});

function Dashboard() {
  const navigate = useNavigate();
  const { data: contracts, isLoading: loadingContracts } = useContracts();
  const { data: contract, isLoading: loadingContract } = useActiveContract();
  const { activeContractId, setActiveContractId } = useContractStore();

  useEffect(() => {
    if (!loadingContracts && contracts !== undefined) {
      if (contracts.length === 0) {
        navigate({ to: "/onboarding" });
      } else if (!activeContractId) {
        setActiveContractId(contracts[0].id);
      }
    }
  }, [contracts, loadingContracts, activeContractId, setActiveContractId, navigate]);

  const { data: scenarios } = useQuery({
    queryKey: ["scenarios", activeContractId],
    queryFn: () => scenariosApi.list(activeContractId!),
    enabled: !!activeContractId,
    retry: false,
  });

  if (loadingContracts || loadingContract) return <LoadingScreen />;
  if (!contract) return <LoadingScreen />;

  const dataInicio = contract.data_inicio ? new Date(contract.data_inicio + "T00:00:00") : null;
  const dataQuitacao = new Date(contract.data_quitacao + "T00:00:00");
  const hoje = new Date();
  const totalDias = dataInicio ? (dataQuitacao.getTime() - dataInicio.getTime()) / 86400000 : null;
  const diasDecorridos = dataInicio ? (hoje.getTime() - dataInicio.getTime()) / 86400000 : null;
  const progressoPct = totalDias && diasDecorridos
    ? Math.min(100, Math.max(0, (diasDecorridos / totalDias) * 100)) : null;

  const cenarioDestaque = scenarios?.find((s) => s.status === "em_execucao") ?? scenarios?.[0];

  return (
    <div className="min-h-screen bg-background">
      <nav className="flex items-center justify-between px-6 py-4 border-b border-border">
        <img src="/brand/logo-dark.svg" alt="Tenor" className="h-5" />
        {contracts && contracts.length > 1 && (
          <select
            value={activeContractId ?? ""}
            onChange={(e) => setActiveContractId(e.target.value)}
            className="text-xs bg-transparent text-muted-foreground border border-border rounded px-2 py-1 focus:outline-none"
          >
            {contracts.map((c) => (
              <option key={c.id} value={c.id}>{c.apelido || "Contrato"}</option>
            ))}
          </select>
        )}
      </nav>

      <div className="max-w-2xl mx-auto px-6 py-10">
        {/* Hero */}
        <div className="mb-10">
          <p className="text-xs text-muted-foreground uppercase tracking-widest mb-3">
            {contract.apelido ?? "Contrato ativo"} · {contract.banco.toUpperCase()} · {contract.sistema_amortizacao}
          </p>
          <p className="font-serif text-5xl sm:text-6xl font-semibold text-foreground leading-none mb-2">
            {formatMonthYear(contract.data_quitacao)}
          </p>
          <p className="text-muted-foreground text-sm">data de quitação no plano atual</p>
        </div>

        {/* Progress */}
        {progressoPct !== null && (
          <div className="mb-10">
            <div className="h-1 bg-border rounded-full overflow-hidden">
              <div className="h-full bg-primary rounded-full transition-all" style={{ width: `${progressoPct}%` }} />
            </div>
            <p className="text-xs text-muted-foreground mt-2">{progressoPct.toFixed(1)}% do caminho percorrido</p>
          </div>
        )}

        {/* KPIs */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <KpiCard label="Saldo devedor" value={formatBRL(contract.saldo_devedor)} />
          <KpiCard label="Próxima parcela" value={formatBRL(contract.parcela_total)}
            sub={new Date(contract.data_proxima_parcela + "T00:00:00").toLocaleDateString("pt-BR")} />
          <KpiCard label="Parcelas restantes" value={String(contract.prazo_remanescente)} />
        </div>

        {/* Composição da parcela */}
        <div className="border border-border rounded-lg p-5 mb-8">
          <p className="text-xs text-muted-foreground uppercase tracking-widest mb-4">Composição da parcela</p>
          <div className="space-y-2">
            <Row label="Amortização" value={formatBRL(contract.amortizacao_mensal)} />
            <Row label="Juros" value={formatBRL(contract.juros_proxima)} accent />
            <Row label="Seguros (MIP + DFI)" value={formatBRL(contract.seguros_mensal)} />
            {contract.custos_extras.length > 0 && contract.custos_extras.map((e, i) => (
              <Row key={i} label={e.nome} value={formatBRL(e.valor)} />
            ))}
            <div className="border-t border-border pt-2 mt-2">
              <Row label="Total" value={formatBRL(contract.parcela_total)} bold />
            </div>
          </div>
        </div>

        {/* Cenário em destaque + chat contextual */}
        {cenarioDestaque ? (
          <div className="border border-primary/30 rounded-lg bg-primary/5 mb-8 overflow-hidden">
            <div className="p-5">
              <p className="text-xs text-primary uppercase tracking-widest mb-3">
                {cenarioDestaque.status === "em_execucao" ? "Plano em execução" : "Cenário salvo"}
              </p>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="font-medium text-sm text-foreground mb-1">{cenarioDestaque.nome}</p>
                  <p className="text-xs text-muted-foreground">
                    {cenarioDestaque.aporte_mensal_extra > 0 && `+${formatBRL(cenarioDestaque.aporte_mensal_extra)}/mês`}
                    {cenarioDestaque.aporte_anual_extra > 0 && ` · +${formatBRL(cenarioDestaque.aporte_anual_extra)}/ano`}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-serif text-xl text-gain">{formatMonthYear(cenarioDestaque.projecao.data_quitacao)}</p>
                  <p className="text-xs text-muted-foreground">
                    economia de {formatBRL(cenarioDestaque.projecao.total_juros_economizados)}
                  </p>
                </div>
              </div>
              <Link
                to="/chat"
                search={{ scenario: cenarioDestaque.id }}
                className="flex items-center gap-2 w-full justify-center py-2.5 rounded-md
                           bg-primary/10 border border-primary/20 text-primary text-xs font-medium
                           hover:bg-primary/20 transition-colors"
              >
                <Sparkles size={13} />
                Conversar com a IA sobre este plano
              </Link>
            </div>
          </div>
        ) : (
          <div className="border border-dashed border-primary/30 rounded-lg p-8 text-center mb-8 bg-primary/5">
            <TrendingDown size={28} className="text-primary mx-auto mb-3 opacity-60" />
            <p className="text-sm text-foreground font-medium mb-2">Crie seu primeiro cenário de amortização</p>
            <p className="text-xs text-muted-foreground mb-4">
              Simule o impacto de amortizar R$ 5 mil por mês e veja quando quita.
            </p>
            <Link to="/scenarios"
              className="inline-flex items-center gap-2 bg-primary text-primary-foreground px-5 py-2.5 rounded-md text-xs font-medium hover:bg-primary/90 transition-colors">
              <Plus size={14} /> Criar cenário
            </Link>
          </div>
        )}

        {/* Ações principais */}
        <div className="grid grid-cols-3 gap-3">
          <Link to="/chat" search={{ scenario: undefined }}
            className="flex flex-col items-center gap-2 border border-border rounded-lg py-5 px-3 hover:border-primary/40 hover:bg-primary/5 transition-all group">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
              <MessageSquare size={18} className="text-primary" />
            </div>
            <span className="text-xs text-muted-foreground group-hover:text-foreground transition-colors">Chat IA</span>
          </Link>

          <Link to="/scenarios"
            className="flex flex-col items-center gap-2 border border-border rounded-lg py-5 px-3 hover:border-primary/40 hover:bg-primary/5 transition-all group">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
              <BarChart3 size={18} className="text-primary" />
            </div>
            <span className="text-xs text-muted-foreground group-hover:text-foreground transition-colors">Cenários</span>
          </Link>

          <Link to="/onboarding"
            className="flex flex-col items-center gap-2 border border-border rounded-lg py-5 px-3 hover:border-primary/40 hover:bg-primary/5 transition-all group">
            <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center group-hover:bg-primary/10 transition-colors">
              <Plus size={18} className="text-muted-foreground group-hover:text-primary transition-colors" />
            </div>
            <span className="text-xs text-muted-foreground group-hover:text-foreground transition-colors">Novo contrato</span>
          </Link>
        </div>
      </div>
    </div>
  );
}

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

function Row({ label, value, accent = false, bold = false }: { label: string; value: string; accent?: boolean; bold?: boolean }) {
  return (
    <div className="flex justify-between items-center">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className={`font-serif text-sm tabular-nums ${bold ? "text-foreground font-semibold" : accent ? "text-loss" : "text-foreground"}`}>
        {value}
      </span>
    </div>
  );
}
