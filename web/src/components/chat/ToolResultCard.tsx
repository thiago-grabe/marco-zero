/**
 * ToolResultCard — renders structured tool results as styled cards.
 *
 * Uses a registry pattern: each tool name maps to a dedicated renderer.
 * Shared CardShell provides consistent framing.
 */

import { useState, type ReactNode } from "react";
import { Calculator, TrendingDown, BarChart3, Wallet, Calendar, ChevronDown, ChevronRight } from "lucide-react";
import { formatBRL, formatMonthYear, formatRate } from "@/lib/utils";
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
  raw,
}: {
  icon: ReactNode;
  title: string;
  children: ReactNode;
  actions?: ReactNode;
  raw?: string;
}) {
  const [showRaw, setShowRaw] = useState(false);

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
            onClick={() => setShowRaw(!showRaw)}
            className="text-xs text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
          >
            {showRaw ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
            Como chegamos aqui
          </button>
          {showRaw && (
            <pre className="mt-2 bg-muted rounded p-3 text-xs text-muted-foreground overflow-x-auto max-h-48">
              {JSON.stringify(JSON.parse(raw), null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
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

  return (
    <CardShell
      icon={<BarChart3 size={12} />}
      title="Projeção de cenário"
      raw={raw}
      actions={
        <ActionBtn label="Simular variação" onClick={() => onAction({ type: "prefill", text: "E se eu amortizar R$ " })} />
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
    <CardShell icon={<BarChart3 size={12} />} title="Comparação de cenários" raw={raw}>
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
    <CardShell icon={<Wallet size={12} />} title="Composição da parcela" raw={raw}>
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
    <CardShell icon={<Calendar size={12} />} title="Juros pró-rata" raw={raw}>
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
