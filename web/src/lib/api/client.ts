/**
 * API client tipado para o backend Tenor.
 * Token injetado automaticamente via Supabase (prod) ou dev bypass.
 */

import { getToken } from "@/lib/auth";

const BASE_URL = import.meta.env.VITE_API_URL ?? "/api";

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = await getToken();

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail ?? `HTTP ${res.status}`);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

// ── Tipos ─────────────────────────────────────────────────────────────────────

export interface CustoExtra {
  nome: string;
  valor: number;
}

export interface ContractResponse {
  id: string;
  property_id: string;
  apelido: string | null;
  banco: string;
  sistema_amortizacao: string;
  taxa_mensal: number;
  taxa_anual_efetiva: number;
  saldo_devedor: number;
  amortizacao_mensal: number;
  mip_mensal: number;
  dfi_mensal: number;
  seguros_mensal: number;
  custos_extras: CustoExtra[];
  custos_extras_total: number;
  parcela_total: number;
  juros_proxima: number;
  data_proxima_parcela: string;
  prazo_remanescente: number;
  data_quitacao: string;
  valor_original: number | null;
  data_inicio: string | null;
  created_at: string;
}

export interface ContractCreate {
  property_apelido?: string;
  apelido?: string;
  banco: string;
  sistema_amortizacao: string;
  taxa_mensal: number;
  saldo_devedor: number;
  amortizacao_mensal: number;
  mip_mensal?: number;
  dfi_mensal?: number;
  data_proxima_parcela: string;
  prazo_remanescente: number;
  custos_extras?: CustoExtra[];
  valor_original?: number;
}

export interface YearSummary {
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

export interface ScenarioProjection {
  data_quitacao: string;
  prazo_meses: number;
  parcelas_eliminadas: number;
  total_juros_pagos: number;
  total_juros_economizados: number;
  total_extras_investidos: number;
  comprometimento_mensal_max: number;
  schedule: YearSummary[];
}

export interface ScenarioResponse {
  id: string;
  contract_id: string;
  nome: string;
  status: string;
  aporte_mensal_extra: number;
  aporte_anual_extra: number;
  mes_aporte_anual: number | null;
  created_at: string;
  updated_at: string;
  projecao: ScenarioProjection;
}

// ── API namespaces ────────────────────────────────────────────────────────────

export const authApi = {
  me: () => apiFetch<{ id: string; nome: string | null }>("/auth/me"),
};

export interface QuickContractCreate {
  parcela_mensal: number;
  banco: string;
  saldo_devedor: number;
}

export interface QuickContractResponse extends ContractResponse {
  campos_estimados: string[];
}

export const contractsApi = {
  list: () => apiFetch<ContractResponse[]>("/contracts"),
  get: (id: string) => apiFetch<ContractResponse>(`/contracts/${id}`),
  create: (body: ContractCreate) =>
    apiFetch<ContractResponse>("/contracts", { method: "POST", body: JSON.stringify(body) }),
  createQuick: (body: QuickContractCreate) =>
    apiFetch<QuickContractResponse>("/contracts/quick", { method: "POST", body: JSON.stringify(body) }),
  update: (id: string, body: Partial<ContractCreate>) =>
    apiFetch<ContractResponse>(`/contracts/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  delete: (id: string) => apiFetch<void>(`/contracts/${id}`, { method: "DELETE" }),
};

export const scenariosApi = {
  list: (contractId: string) =>
    apiFetch<ScenarioResponse[]>(`/contracts/${contractId}/scenarios`),
  create: (contractId: string, body: { nome: string; aporte_mensal_extra?: number; aporte_anual_extra?: number; mes_aporte_anual?: number }) =>
    apiFetch<ScenarioResponse>(`/contracts/${contractId}/scenarios`, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  update: (id: string, body: Partial<{ nome: string; aporte_mensal_extra: number; aporte_anual_extra: number; mes_aporte_anual: number; status: string }>) =>
    apiFetch<ScenarioResponse>(`/scenarios/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  delete: (id: string) => apiFetch<void>(`/scenarios/${id}`, { method: "DELETE" }),
};

export const motorApi = {
  project: (params: {
    saldo: number;
    prazo_remanescente: number;
    taxa_mensal: number;
    amortizacao_mensal: number;
    mip_mensal: number;
    dfi_mensal: number;
    data_proxima_parcela: string;
    aporte_mensal_extra?: number;
    aporte_anual_extra?: number;
    mes_aporte_anual?: number;
  }) => apiFetch<ScenarioProjection>("/motor/project", { method: "POST", body: JSON.stringify(params) }),
};

export const healthApi = {
  check: () => apiFetch<{ status: string; version: string }>("/health"),
};
