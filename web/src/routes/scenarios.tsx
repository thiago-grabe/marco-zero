import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useEffect, useState, useCallback } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useActiveContract } from "@/hooks/useContract";
import { useContractStore } from "@/stores/contract";
import { scenariosApi, motorApi, type ScenarioProjection } from "@/lib/api/client";
import { formatBRL, formatMonthYear, debounce } from "@/lib/utils";

export const Route = createFileRoute("/scenarios")({
  component: Scenarios,
});

interface SliderParams {
  aporte_mensal_extra: number;
  aporte_anual_extra: number;
  mes_aporte_anual: number;
}

function Scenarios() {
  const navigate = useNavigate();
  const { data: contract } = useActiveContract();
  const activeContractId = useContractStore((s) => s.activeContractId);
  const queryClient = useQueryClient();

  const [showForm, setShowForm] = useState(false);
  const [nomeCenario, setNomeCenario] = useState("");
  const [sliders, setSliders] = useState<SliderParams>({
    aporte_mensal_extra: 0,
    aporte_anual_extra: 0,
    mes_aporte_anual: 4,
  });
  const [liveProjection, setLiveProjection] = useState<ScenarioProjection | null>(null);

  const { data: scenarios, isLoading } = useQuery({
    queryKey: ["scenarios", activeContractId],
    queryFn: () => scenariosApi.list(activeContractId!),
    enabled: !!activeContractId,
  });

  const createScenario = useMutation({
    mutationFn: () =>
      scenariosApi.create(activeContractId!, {
        nome: nomeCenario || "Novo cenário",
        ...sliders,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scenarios", activeContractId] });
      setShowForm(false);
      setNomeCenario("");
    },
  });

  const deleteScenario = useMutation({
    mutationFn: (id: string) => scenariosApi.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["scenarios", activeContractId] }),
  });

  const promoteScenario = useMutation({
    mutationFn: (id: string) => scenariosApi.update(id, { status: "em_execucao" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scenarios", activeContractId] });
      navigate({ to: "/dashboard" });
    },
  });

  // Projeção ao vivo com debounce para os sliders
  const fetchLiveProjection = useCallback(
    debounce(async (params: SliderParams) => {
      if (!contract) return;
      try {
        const proj = await motorApi.project({
          saldo: contract.saldo_devedor,
          prazo_remanescente: contract.prazo_remanescente,
          taxa_mensal: contract.taxa_mensal,
          amortizacao_mensal: contract.amortizacao_mensal,
          mip_mensal: contract.mip_mensal,
          dfi_mensal: contract.dfi_mensal,
          data_proxima_parcela: contract.data_proxima_parcela,
          ...params,
        });
        setLiveProjection(proj);
      } catch {
        // ignora erros de projeção durante ajuste de sliders
      }
    }, 200),
    [contract]
  );

  useEffect(() => {
    if (contract && showForm) fetchLiveProjection(sliders);
  }, [sliders, contract, showForm, fetchLiveProjection]);

  if (!contract) return null;

  // Projeção base (sem extras)
  const baseQuitacao = contract.data_quitacao;

  return (
    <div className="min-h-screen bg-background">
      <nav className="flex items-center justify-between px-6 py-4 border-b border-border">
        <Link to="/dashboard" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
          ← Dashboard
        </Link>
        <span className="font-serif text-sm font-semibold">Cenários</span>
        <button
          onClick={() => setShowForm(true)}
          className="text-xs text-primary hover:text-primary/80 transition-colors"
        >
          + Novo
        </button>
      </nav>

      <div className="max-w-2xl mx-auto px-6 py-8">
        {/* Referência base */}
        <div className="border border-border rounded-lg px-5 py-4 mb-6 flex justify-between items-center">
          <div>
            <p className="text-xs text-muted-foreground mb-1">Plano atual — sem extras</p>
            <p className="font-serif text-xl text-foreground">{formatMonthYear(baseQuitacao)}</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-muted-foreground">Parcela</p>
            <p className="font-serif text-sm tabular-nums">{formatBRL(contract.parcela_total)}</p>
          </div>
        </div>

        {/* Formulário de novo cenário */}
        {showForm && (
          <div className="border border-primary/30 rounded-lg p-6 bg-primary/5 mb-6">
            <p className="text-xs text-primary uppercase tracking-widest mb-5">Novo cenário</p>

            <div className="mb-4">
              <label className="text-xs text-muted-foreground block mb-1.5">Nome</label>
              <input
                type="text"
                value={nomeCenario}
                onChange={(e) => setNomeCenario(e.target.value)}
                placeholder="Ex: 5k/mês após PLR"
                className="w-full bg-background border border-border rounded-md px-3 py-2.5
                           text-sm text-foreground placeholder:text-muted-foreground
                           focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>

            <SliderField
              label="Aporte mensal extra"
              value={sliders.aporte_mensal_extra}
              min={0}
              max={20000}
              step={500}
              onChange={(v) => setSliders((s) => ({ ...s, aporte_mensal_extra: v }))}
            />

            <SliderField
              label="Aporte anual extra"
              value={sliders.aporte_anual_extra}
              min={0}
              max={100000}
              step={5000}
              onChange={(v) => setSliders((s) => ({ ...s, aporte_anual_extra: v }))}
            />

            {sliders.aporte_anual_extra > 0 && (
              <div className="mb-5">
                <label className="text-xs text-muted-foreground block mb-2">
                  Mês do aporte anual
                </label>
                <select
                  value={sliders.mes_aporte_anual}
                  onChange={(e) => setSliders((s) => ({ ...s, mes_aporte_anual: Number(e.target.value) }))}
                  className="bg-background border border-border rounded-md px-3 py-2 text-sm
                             text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                >
                  {["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"].map(
                    (m, i) => <option key={i} value={i + 1}>{m}</option>
                  )}
                </select>
              </div>
            )}

            {/* Preview da projeção em tempo real */}
            {liveProjection && (
              <div className="border border-border rounded-md p-4 mb-5 space-y-2">
                <p className="text-xs text-muted-foreground uppercase tracking-widest">
                  Resultado estimado
                </p>
                <div className="flex justify-between">
                  <span className="text-xs text-muted-foreground">Quitação</span>
                  <span className="font-serif text-sm text-gain">
                    {formatMonthYear(liveProjection.data_quitacao)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-xs text-muted-foreground">Economia em juros</span>
                  <span className="font-serif text-sm text-gain">
                    {formatBRL(liveProjection.total_juros_economizados)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-xs text-muted-foreground">Total extra investido</span>
                  <span className="font-serif text-sm tabular-nums">
                    {formatBRL(liveProjection.total_extras_investidos)}
                  </span>
                </div>
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={() => { setShowForm(false); setLiveProjection(null); }}
                className="flex-1 py-2.5 border border-border rounded-md text-sm
                           text-muted-foreground hover:text-foreground transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={() => createScenario.mutate()}
                disabled={createScenario.isPending}
                className="flex-1 bg-primary text-primary-foreground rounded-md py-2.5
                           text-sm font-medium disabled:opacity-50 hover:bg-primary/90 transition-colors"
              >
                {createScenario.isPending ? "Salvando…" : "Salvar cenário"}
              </button>
            </div>
          </div>
        )}

        {/* Lista de cenários */}
        {isLoading ? (
          <p className="text-sm text-muted-foreground text-center py-8">Carregando…</p>
        ) : !scenarios?.length ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground text-sm mb-4">
              Nenhum cenário salvo ainda.
            </p>
            <button
              onClick={() => setShowForm(true)}
              className="text-xs text-primary hover:text-primary/80 transition-colors"
            >
              Criar o primeiro cenário →
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {scenarios.map((s) => (
              <div
                key={s.id}
                className={`border rounded-lg p-5 ${
                  s.status === "em_execucao"
                    ? "border-primary/40 bg-primary/5"
                    : "border-border"
                }`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <p className="text-sm font-medium text-foreground">{s.nome}</p>
                      {s.status === "em_execucao" && (
                        <span className="text-xs text-primary bg-primary/10 px-2 py-0.5 rounded">
                          Em execução
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {s.aporte_mensal_extra > 0 && `+${formatBRL(s.aporte_mensal_extra)}/mês`}
                      {s.aporte_anual_extra > 0 && ` · +${formatBRL(s.aporte_anual_extra)}/ano`}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-serif text-lg text-gain">
                      {formatMonthYear(s.projecao.data_quitacao)}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      −{formatBRL(s.projecao.total_juros_economizados)} em juros
                    </p>
                  </div>
                </div>

                <div className="flex gap-2 mt-3 pt-3 border-t border-border">
                  {s.status !== "em_execucao" && (
                    <button
                      onClick={() => promoteScenario.mutate(s.id)}
                      className="text-xs text-primary hover:text-primary/80 transition-colors"
                    >
                      Executar este plano
                    </button>
                  )}
                  <button
                    onClick={() => deleteScenario.mutate(s.id)}
                    className="text-xs text-muted-foreground hover:text-loss transition-colors ml-auto"
                  >
                    Remover
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function SliderField({
  label, value, min, max, step, onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (v: number) => void;
}) {
  return (
    <div className="mb-5">
      <div className="flex justify-between items-center mb-2">
        <label className="text-xs text-muted-foreground">{label}</label>
        <span className="font-serif text-sm tabular-nums text-foreground">
          {value > 0 ? formatBRL(value) : "Sem aporte"}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-primary"
      />
      <div className="flex justify-between text-xs text-muted-foreground mt-1">
        <span>R$ 0</span>
        <span>{formatBRL(max)}</span>
      </div>
    </div>
  );
}
