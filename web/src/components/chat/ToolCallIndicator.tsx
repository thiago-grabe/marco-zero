import { Calculator, TrendingDown, BarChart3, Wallet, Calendar, Check } from "lucide-react";

const TOOL_CONFIG: Record<string, { label: string; icon: React.ReactNode }> = {
  simular_amortizacao: { label: "Simulando amortização", icon: <TrendingDown size={12} /> },
  projetar_cenario: { label: "Projetando cenário", icon: <BarChart3 size={12} /> },
  comparar_cenarios: { label: "Comparando cenários", icon: <BarChart3 size={12} /> },
  calcular_parcela: { label: "Calculando parcela", icon: <Wallet size={12} /> },
  calcular_pro_rata: { label: "Calculando pró-rata", icon: <Calendar size={12} /> },
};

export function ToolCallIndicator({
  tool,
  status,
}: {
  tool: string;
  status: "pending" | "done";
}) {
  const config = TOOL_CONFIG[tool] ?? { label: tool, icon: <Calculator size={12} /> };

  return (
    <div className="flex items-center gap-2 text-xs text-muted-foreground py-1.5">
      {status === "pending" ? (
        <div className="w-3 h-3 border border-primary border-t-transparent rounded-full animate-spin" />
      ) : (
        <Check size={12} className="text-gain" />
      )}
      <span className="flex items-center gap-1">
        {config.icon}
        {status === "pending" ? `${config.label}…` : `${config.label} concluída`}
      </span>
    </div>
  );
}
