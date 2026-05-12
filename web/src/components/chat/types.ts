/**
 * Tipos do chat — mensagens, partes, e payloads tipados de cada tool.
 */

// ── Tool result payloads (tipados, não Record<string, unknown>) ──────────────

export interface AmortizationResult {
  saldo_novo: number;
  juros_pro_rata: number;
  atualizacao_monetaria: number;
  total_desembolso: number;
  prazo_novo: number;
  parcelas_eliminadas: number;
  nova_amortizacao_mensal: number;
  nova_parcela_proxima: number;
  prazo_inalterado: boolean;
  seguros_economizados: number;
  juros_economizados_nominal: number;
  juros_economizados_vp: number;
  retorno_efetivo_aa: number;
  data_nova_quitacao: string;
}

export interface YearSchedule {
  ano: number;
  parcela_inicio: number;
  parcela_fim: number;
  saldo_inicio: number;
  saldo_fim: number;
  amort_regular: number;
  amort_extra_mensal: number;
  amort_extra_anual: number;
  fgts_aplicado: number;
  juros_pagos: number;
}

export interface ScenarioProjectionResult {
  data_quitacao: string;
  prazo_meses: number;
  parcelas_eliminadas: number;
  total_juros_pagos: number;
  total_juros_economizados: number;
  total_extras_investidos: number;
  comprometimento_mensal_max: number;
  schedule: YearSchedule[];
}

export interface MarginalAnalysis {
  extra_investido: number;
  juros_economizados: number;
  tempo_cortado_meses: number;
  retorno_marginal: number;
  recomendacao: "sim" | "depende" | "nao";
  motivo: string;
}

export interface ComparisonResult {
  base: ScenarioProjectionResult;
  cenarios: ScenarioProjectionResult[];
  marginal: MarginalAnalysis[];
}

export interface InstallmentResult {
  amortizacao: number;
  juros: number;
  mip: number;
  dfi: number;
  seguros: number;
  total: number;
}

export interface ProRataResult {
  dias_decorridos: number;
  juros_pro_rata: number;
  atualizacao_tr: number;
  total_acrescimo: number;
}

// ── Message parts ────────────────────────────────────────────────────────────

export type ToolName =
  | "simular_amortizacao"
  | "projetar_cenario"
  | "comparar_cenarios"
  | "calcular_parcela"
  | "calcular_pro_rata";

export interface TextPart {
  type: "text";
  content: string;
}

export interface ToolCallPart {
  type: "tool_call";
  id: string;
  tool: ToolName;
  args: string;
  status: "pending" | "done";
}

export interface ToolResultPart {
  type: "tool_result";
  tool: ToolName;
  data: unknown; // parsed JSON — cast per tool in renderer
  raw: string;
}

export type MessagePart = TextPart | ToolCallPart | ToolResultPart;

// ── Messages ─────────────────────────────────────────────────────────────────

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  parts: MessagePart[];
}

export interface ChatContext {
  banco: string;
  saldo_devedor: number;
  parcela_total: number;
  prazo_remanescente: number;
}

// ── Actions ──────────────────────────────────────────────────────────────────

export type ChatAction =
  | { type: "prefill"; text: string }
  | { type: "save_scenario"; contractId: string; params: Record<string, unknown> }
  | { type: "expand"; partId: string };

export type ActionHandler = (action: ChatAction) => void;
