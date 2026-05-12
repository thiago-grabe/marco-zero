/**
 * ToolResultCard — renders structured tool results as styled cards.
 *
 * Uses a registry pattern: each tool name maps to a dedicated renderer.
 * Shared CardShell provides consistent framing.
 */

import { useState, type ReactNode } from "react";
import { Calculator, TrendingDown, BarChart3, Wallet, Calendar, ChevronDown, ChevronRight, Download } from "lucide-react";
import { formatBRL, formatMonthYear, formatRate, downloadCSV } from "@/lib/utils";
import type {
  ActionHandler,
  AmortizationResult,
  ComparisonResult,
  InstallmentResult,
  ProRataResult,
  ScenarioProjectionResult,
} from "./types";

// ── Card Shell ───────────────────────────────────────────────────────────────

function CardShell({
  icon,
  title,
  children,
  actions,
  toolName,
  raw,
}: {
  icon: ReactNode;
  title: string;
  children: ReactNode;
  actions?: ReactNode;
  toolName?: string;
  raw?: string;
}) {
  const [showExplain, setShowExplain] = useState(false);

  return (
    <div className="border border-border rounded-lg p-5 bg-card my-3">
      <p className="text-xs text-muted-foreground uppercase tracking-widest mb-3 flex items-center gap-1.5">
        {icon} {title}
      </p>
      {children}
      {actions && (
        <div className="flex flex-wrap gap-2 mt-4 pt-3 border-t border-border">
          {actions}
        </div>
      )}
      {raw && (
        <div className="mt-3 pt-3 border-t border-border">
          <button
            onClick={() => setShowExplain(!showExplain)}
            className="text-xs text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
          >
            {showExplain ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
            Como chegamos aqui
          </button>
          {showExplain && (
            <ExplainSteps toolName={toolName} raw={raw} />
          )}
        </div>
      )}
    </div>
  );
}

/** Explicação amigável dos passos do cálculo (não JSON bruto). */
function ExplainSteps({ toolName, raw }: { toolName?: string; raw: string }) {
  let data: Record<string, unknown> = {};
  try { data = JSON.parse(raw); } catch { /* */ }

  const steps = buildExplanation(toolName ?? "", data);

  return (
    <div className="mt-2 space-y-2">
      {steps.map((step, i) => (
        <div key={i} className="flex gap-2 items-start">
          <span className="text-xs text-muted-foreground shrink-0 w-4 text-right">{i + 1}.</span>
          <p className="text-xs text-muted-foreground leading-relaxed">{step}</p>
        </div>
      ))}
    </div>
  );
}

function buildExplanation(tool: string, data: Record<string, unknown>): string[] {
  switch (tool) {
    case "simular_amortizacao":
      return [
        `Calculamos o saldo devedor após subtrair o valor da amortização e somar os juros pró-rata (${formatBRL(Number(data.juros_pro_rata ?? 0))}).`,
        `O novo saldo ficou em ${formatBRL(Number(data.saldo_novo ?? 0))}.`,
        `Com o prazo recalculado, ${data.parcelas_eliminadas} parcelas foram eliminadas.`,
        `A economia total em juros foi de ${formatBRL(Number(data.juros_economizados_nominal ?? 0))} em valor nominal.`,
        `O retorno efetivo da operação é equivalente a ${formatRate(Number(data.retorno_efetivo_aa ?? 0))} a.a. — a taxa do próprio contrato.`,
        "Cálculo determinístico pelo motor SAC. A IA não participou desta conta.",
      ];
    case "projetar_cenario":
      return [
        "O motor simulou mês a mês, aplicando a amortização regular + aportes extras configurados.",
        `Projeção até a quitação: ${formatMonthYear(String(data.data_quitacao ?? ""))} (${data.prazo_meses} meses).`,
        `Total de juros pagos: ${formatBRL(Number(data.total_juros_pagos ?? 0))}.`,
        `Economia comparada ao plano sem extras: ${formatBRL(Number(data.total_juros_economizados ?? 0))}.`,
        "Cada mês: saldo = saldo anterior − amortização regular − extra mensal − (extra anual se for o mês configurado).",
        "Cálculo determinístico pelo motor SAC. Nenhum valor foi estimado pela IA.",
      ];
    case "comparar_cenarios":
      return [
        "O motor projetou cada cenário separadamente e depois comparou os resultados.",
        "A análise marginal mostra o retorno incremental de cada upgrade.",
        "Retorno marginal = (juros economizados a mais) / (extra investido a mais).",
        "Recomendação 'sim' = retorno > 0,80; 'depende' = 0,40–0,80; 'não' = < 0,40.",
        "Todos os cenários usam o mesmo saldo base e a mesma taxa.",
      ];
    case "calcular_parcela":
      return [
        "Amortização SAC = saldo devedor ÷ prazo remanescente.",
        `Juros = saldo × taxa mensal = ${formatBRL(Number(data.juros ?? 0))}.`,
        "Seguros (MIP + DFI) variam com o saldo e a idade do mutuário.",
        "Total = amortização + juros + seguros.",
      ];
    case "calcular_pro_rata":
      return [
        `Juros pró-rata calculados para ${data.dias_decorridos} dias decorridos.`,
        "Fórmula: saldo × taxa mensal × (dias / 30).",
        `Resultado: ${formatBRL(Number(data.juros_pro_rata ?? 0))} de juros adicionais.`,
        "Esses juros são cobrados junto com o valor da amortização extraordinária.",
      ];
    default:
      return ["Cálculo executado pelo motor. Detalhes não disponíveis para esta ferramenta."];
  }
}

function ActionBtn({ label, onClick }: { label: string; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="text-xs text-primary hover:text-primary/80 border border-primary/30
                 rounded px-3 py-1.5 transition-colors hover:bg-primary/5"
    >
      {label}
    </button>
  );
}

function MetricRow({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="flex justify-between items-center py-1">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className={`font-serif text-sm tabular-nums ${color ?? "text-foreground"}`}>
        {value}
      </span>
    </div>
  );
}

// ── Tool Renderers ───────────────────────────────────────────────────────────

function AmortizationCard({ data, raw, onAction }: { data: AmortizationResult; raw: string; onAction: ActionHandler }) {
  return (
    <CardShell
      icon={<TrendingDown size={12} />}
      title="Impacto da amortização"
      toolName="simular_amortizacao"
      raw={raw}
      actions={
        <>
          <ActionBtn label="Simular com outro valor" onClick={() => onAction({ type: "prefill", text: "E se eu amortizar R$ " })} />
        </>
      }
    >
      <div className="space-y-0.5">
        <MetricRow label="Saldo depois" value={formatBRL(data.saldo_novo)} />
        <MetricRow label="Total desembolsado" value={formatBRL(data.total_desembolso)} />
        <div className="border-t border-border my-2" />
        <MetricRow label="Parcelas eliminadas" value={String(data.parcelas_eliminadas)} color="text-gain" />
        <MetricRow label="Economia em juros" value={formatBRL(data.juros_economizados_nominal)} color="text-gain" />
        <MetricRow label="Nova quitação" value={formatMonthYear(data.data_nova_quitacao)} />
        <MetricRow label="Retorno efetivo" value={formatRate(data.retorno_efetivo_aa) + " a.a."} />
      </div>
    </CardShell>
  );
}

function ProjectionCard({ data, raw, onAction }: { data: ScenarioProjectionResult; raw: string; onAction: ActionHandler }) {
  const [showSchedule, setShowSchedule] = useState(false);

  function handleDownloadCSV() {
    const headers = ["Ano", "Parcela início", "Parcela fim", "Saldo início", "Saldo fim", "Amort regular", "Extra mensal", "Extra anual", "FGTS", "Juros pagos"];
    const rows = data.schedule.map((y) => [
      y.ano, y.parcela_inicio, y.parcela_fim, y.saldo_inicio, y.saldo_fim,
      y.amort_regular, y.amort_extra_mensal, y.amort_extra_anual, y.fgts_aplicado, y.juros_pagos,
    ]);
    downloadCSV(`tenor-projecao-${data.data_quitacao}.csv`, headers, rows);
  }

  return (
    <CardShell
      icon={<BarChart3 size={12} />}
      title="Projeção de cenário"
      toolName="projetar_cenario"
      raw={raw}
      actions={
        <>
          <ActionBtn label="Simular variação" onClick={() => onAction({ type: "prefill", text: "E se eu amortizar R$ " })} />
          <button
            onClick={handleDownloadCSV}
            className="text-xs text-muted-foreground hover:text-foreground border border-border
                       rounded px-3 py-1.5 transition-colors hover:bg-muted flex items-center gap-1"
          >
            <Download size={10} /> Baixar planilha
          </button>
        </>
      }
    >
      <div className="mb-3">
        <p className="font-serif text-2xl font-semibold text-primary">
          {formatMonthYear(data.data_quitacao)}
        </p>
        <p className="text-xs text-muted-foreground">
          {data.parcelas_eliminadas > 0
            ? `${data.parcelas_eliminadas} parcelas eliminadas`
            : "sem alteração no prazo"}
        </p>
      </div>
      <div className="space-y-0.5">
        <MetricRow label="Economia em juros" value={formatBRL(data.total_juros_economizados)} color="text-gain" />
        <MetricRow label="Total extra investido" value={formatBRL(data.total_extras_investidos)} />
        <MetricRow label="Comprometimento max" value={formatBRL(data.comprometimento_mensal_max) + "/mês"} />
      </div>

      {data.schedule.length > 0 && (
        <div className="mt-3">
          <button
            onClick={() => setShowSchedule(!showSchedule)}
            className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1 transition-colors"
          >
            {showSchedule ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
            Cronograma ano a ano ({data.schedule.length} anos)
          </button>
          {showSchedule && (
            <div className="border border-border rounded mt-2 overflow-hidden">
              <table className="w-full text-xs">
                <thead className="bg-muted">
                  <tr>
                    <th className="px-2 py-1.5 text-left text-muted-foreground">Ano</th>
                    <th className="px-2 py-1.5 text-right text-muted-foreground">Saldo fim</th>
                    <th className="px-2 py-1.5 text-right text-muted-foreground">Juros</th>
                    <th className="px-2 py-1.5 text-right text-muted-foreground">Extras</th>
                  </tr>
                </thead>
                <tbody>
                  {data.schedule.map((y) => (
                    <tr key={y.ano} className="border-t border-border">
                      <td className="px-2 py-1.5 font-serif">{y.ano}</td>
                      <td className="px-2 py-1.5 text-right font-serif tabular-nums">{formatBRL(y.saldo_fim)}</td>
                      <td className="px-2 py-1.5 text-right font-serif tabular-nums text-loss">{formatBRL(y.juros_pagos)}</td>
                      <td className="px-2 py-1.5 text-right font-serif tabular-nums">
                        {formatBRL(y.amort_extra_mensal + y.amort_extra_anual + y.fgts_aplicado)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </CardShell>
  );
}

function ComparisonCard({ data, raw }: { data: ComparisonResult; raw: string; onAction: ActionHandler }) {
  const recColors: Record<string, string> = { sim: "text-gain", depende: "text-warning", nao: "text-loss" };
  const recIcons: Record<string, string> = { sim: "✓", depende: "⚠", nao: "✗" };

  return (
    <CardShell icon={<BarChart3 size={12} />} title="Comparação de cenários" toolName="comparar_cenarios" raw={raw}>
      <div className="border border-border rounded overflow-hidden mb-3">
        <table className="w-full text-xs">
          <thead className="bg-muted">
            <tr>
              <th className="px-2 py-1.5 text-left text-muted-foreground">Métrica</th>
              <th className="px-2 py-1.5 text-right text-muted-foreground">Base</th>
              {data.cenarios.map((_, i) => (
                <th key={i} className="px-2 py-1.5 text-right text-muted-foreground">
                  Cenário {i + 1}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr className="border-t border-border">
              <td className="px-2 py-1.5 text-muted-foreground">Quitação</td>
              <td className="px-2 py-1.5 text-right font-serif">{formatMonthYear(data.base.data_quitacao)}</td>
              {data.cenarios.map((c, i) => (
                <td key={i} className="px-2 py-1.5 text-right font-serif text-gain">{formatMonthYear(c.data_quitacao)}</td>
              ))}
            </tr>
            <tr className="border-t border-border">
              <td className="px-2 py-1.5 text-muted-foreground">Economia</td>
              <td className="px-2 py-1.5 text-right font-serif">—</td>
              {data.cenarios.map((c, i) => (
                <td key={i} className="px-2 py-1.5 text-right font-serif tabular-nums text-gain">{formatBRL(c.total_juros_economizados)}</td>
              ))}
            </tr>
            <tr className="border-t border-border">
              <td className="px-2 py-1.5 text-muted-foreground">Extra investido</td>
              <td className="px-2 py-1.5 text-right font-serif">R$ 0</td>
              {data.cenarios.map((c, i) => (
                <td key={i} className="px-2 py-1.5 text-right font-serif tabular-nums">{formatBRL(c.total_extras_investidos)}</td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>

      {data.marginal.length > 0 && (
        <div className="space-y-1.5">
          <p className="text-xs text-muted-foreground uppercase tracking-widest">Análise marginal</p>
          {data.marginal.map((m, i) => (
            <div key={i} className="flex items-center justify-between text-xs py-1">
              <span className="text-muted-foreground">
                {i === 0 ? "Base" : `Cenário ${i}`} → Cenário {i + 1}
              </span>
              <span className={recColors[m.recomendacao] ?? "text-foreground"}>
                {recIcons[m.recomendacao]} retorno {m.retorno_marginal.toFixed(2)} — {m.recomendacao}
              </span>
            </div>
          ))}
        </div>
      )}
    </CardShell>
  );
}

function InstallmentCard({ data, raw }: { data: InstallmentResult; raw: string; onAction: ActionHandler }) {
  return (
    <CardShell icon={<Wallet size={12} />} title="Composição da parcela" toolName="calcular_parcela" raw={raw}>
      <div className="space-y-0.5">
        <MetricRow label="Amortização" value={formatBRL(data.amortizacao)} />
        <MetricRow label="Juros" value={formatBRL(data.juros)} color="text-loss" />
        <MetricRow label="MIP" value={formatBRL(data.mip)} />
        <MetricRow label="DFI" value={formatBRL(data.dfi)} />
        <div className="border-t border-border my-2" />
        <MetricRow label="Total" value={formatBRL(data.total)} color="text-foreground font-semibold" />
      </div>
    </CardShell>
  );
}

function ProRataCard({ data, raw }: { data: ProRataResult; raw: string; onAction: ActionHandler }) {
  return (
    <CardShell icon={<Calendar size={12} />} title="Juros pró-rata" toolName="calcular_pro_rata" raw={raw}>
      <div className="space-y-0.5">
        <MetricRow label="Dias decorridos" value={String(data.dias_decorridos)} />
        <MetricRow label="Juros pró-rata" value={formatBRL(data.juros_pro_rata)} color="text-loss" />
        <MetricRow label="Atualização (TR)" value={formatBRL(data.atualizacao_tr)} />
        <div className="border-t border-border my-2" />
        <MetricRow label="Total acréscimo" value={formatBRL(data.total_acrescimo)} color="text-loss" />
      </div>
    </CardShell>
  );
}

// ── Registry ─────────────────────────────────────────────────────────────────

const TOOL_RENDERERS: Record<string, React.FC<{ data: any; raw: string; onAction: ActionHandler }>> = {
  simular_amortizacao: AmortizationCard,
  projetar_cenario: ProjectionCard,
  comparar_cenarios: ComparisonCard,
  calcular_parcela: InstallmentCard,
  calcular_pro_rata: ProRataCard,
};

export function ToolResultCard({
  tool,
  data,
  raw,
  onAction,
}: {
  tool: string;
  data: unknown;
  raw: string;
  onAction: ActionHandler;
}) {
  const Renderer = TOOL_RENDERERS[tool];

  if (!Renderer) {
    return (
      <CardShell icon={<Calculator size={12} />} title={tool} raw={raw}>
        <pre className="text-xs text-muted-foreground overflow-x-auto">
          {JSON.stringify(data, null, 2)}
        </pre>
      </CardShell>
    );
  }

  return <Renderer data={data} raw={raw} onAction={onAction} />;
}
