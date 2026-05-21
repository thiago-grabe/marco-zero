import { HomeLink } from "@/components/layout/HomeLink";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { useCreateContract } from "@/hooks/useContract";
import { formatBRL, formatMonthYear } from "@/lib/utils";

export const Route = createFileRoute("/onboarding")({
  component: Onboarding,
});

const BANCOS = [
  { code: "itau", label: "Itaú" },
  { code: "caixa", label: "Caixa" },
  { code: "bb", label: "BB" },
  { code: "bradesco", label: "Bradesco" },
  { code: "santander", label: "Santander" },
  { code: "outro", label: "Outro" },
];

interface CustoExtraField {
  nome: string;
  valor: string;
}

interface Fields {
  property_apelido: string;
  banco: string;
  sistema_amortizacao: "SAC" | "PRICE";
  taxa_mensal_pct: string;
  saldo_devedor: string;
  amortizacao_mensal: string;
  mip_mensal: string;
  dfi_mensal: string;
  data_proxima_parcela: string;
  prazo_remanescente: string;
  custos_extras: CustoExtraField[];
}

const EMPTY: Fields = {
  property_apelido: "",
  banco: "",
  sistema_amortizacao: "SAC",
  taxa_mensal_pct: "",
  saldo_devedor: "",
  amortizacao_mensal: "",
  mip_mensal: "0",
  dfi_mensal: "0",
  data_proxima_parcela: "",
  prazo_remanescente: "",
  custos_extras: [],
};

function parseNumber(s: string): number {
  return parseFloat(s.replace(",", ".").replace(/[^\d.]/g, "")) || 0;
}

function ProgressDots({ step, total }: { step: number; total: number }) {
  return (
    <div className="flex gap-2 mb-8">
      {Array.from({ length: total }).map((_, i) => (
        <div
          key={i}
          className={`h-1 rounded-full transition-all ${
            i < step ? "bg-primary flex-1" : i === step ? "bg-primary/50 flex-1" : "bg-border flex-1"
          }`}
        />
      ))}
    </div>
  );
}

function Onboarding() {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [fields, setFields] = useState<Fields>(EMPTY);
  const createContract = useCreateContract();

  function set(key: keyof Fields, value: string) {
    setFields((f) => ({ ...f, [key]: value }));
  }

  // Dados computados para a tela de revisão e insight
  const taxa = parseNumber(fields.taxa_mensal_pct) / 100;
  const saldo = parseNumber(fields.saldo_devedor);
  const amort = parseNumber(fields.amortizacao_mensal);
  const prazo = parseInt(fields.prazo_remanescente) || 0;
  const mip = parseNumber(fields.mip_mensal);
  const dfi = parseNumber(fields.dfi_mensal);
  const extras_total = fields.custos_extras.reduce((s, e) => s + parseNumber(e.valor), 0);
  const juros_est = saldo * taxa;
  const parcela_est = amort + juros_est + mip + dfi + extras_total;
  const taxa_aa = taxa > 0 ? (1 + taxa) ** 12 - 1 : 0;

  function addCustoExtra() {
    setFields((f) => ({ ...f, custos_extras: [...f.custos_extras, { nome: "", valor: "" }] }));
  }

  function removeCustoExtra(index: number) {
    setFields((f) => ({ ...f, custos_extras: f.custos_extras.filter((_, i) => i !== index) }));
  }

  function updateCustoExtra(index: number, key: "nome" | "valor", value: string) {
    setFields((f) => ({
      ...f,
      custos_extras: f.custos_extras.map((e, i) => (i === index ? { ...e, [key]: value } : e)),
    }));
  }

  async function handleSubmit() {
    await createContract.mutateAsync({
      property_apelido: fields.property_apelido || "Apartamento",
      banco: fields.banco,
      sistema_amortizacao: fields.sistema_amortizacao,
      taxa_mensal: taxa,
      saldo_devedor: saldo,
      amortizacao_mensal: amort,
      mip_mensal: mip,
      dfi_mensal: dfi,
      data_proxima_parcela: fields.data_proxima_parcela,
      prazo_remanescente: prazo,
      custos_extras: fields.custos_extras
        .filter((e) => e.nome.trim() && parseNumber(e.valor) > 0)
        .map((e) => ({ nome: e.nome.trim(), valor: parseNumber(e.valor) })),
    });
    setStep(3);
  }

  // ── Passo 0 — Banco + Sistema ──────────────────────────────────────────────
  if (step === 0) {
    return (
      <div className="min-h-screen bg-background px-6 py-10 max-w-lg mx-auto">
        <HomeLink />
        <div className="mt-4" />
        <ProgressDots step={0} total={4} />
        <p className="text-xs text-muted-foreground uppercase tracking-widest mb-2">Passo 1 de 4</p>
        <h1 className="font-serif text-2xl font-semibold mb-1">Onde está seu contrato?</h1>
        <p className="text-muted-foreground text-sm mb-8">Selecione o banco do seu financiamento.</p>

        <div className="grid grid-cols-3 gap-3 mb-8">
          {BANCOS.map((b) => (
            <button
              key={b.code}
              onClick={() => { set("banco", b.code); }}
              className={`py-4 rounded-lg border text-sm font-medium transition-all ${
                fields.banco === b.code
                  ? "border-primary text-primary bg-primary/5"
                  : "border-border text-muted-foreground hover:border-foreground/30 hover:text-foreground"
              }`}
            >
              {b.label}
            </button>
          ))}
        </div>

        <div className="mb-8">
          <p className="text-xs text-muted-foreground uppercase tracking-wide mb-3">
            Sistema de amortização
          </p>
          <div className="flex gap-3">
            {(["SAC", "PRICE"] as const).map((s) => (
              <button
                key={s}
                onClick={() => set("sistema_amortizacao", s)}
                className={`flex-1 py-3 rounded-lg border text-sm font-medium transition-all ${
                  fields.sistema_amortizacao === s
                    ? "border-primary text-primary bg-primary/5"
                    : "border-border text-muted-foreground hover:border-foreground/30 hover:text-foreground"
                }`}
              >
                {s}
              </button>
            ))}
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            {fields.sistema_amortizacao === "SAC"
              ? "Amortização constante — parcela decrescente. Mais comum em bancos privados."
              : "Prestação constante — amortização crescente. Caixa (MCMV)."}
          </p>
        </div>

        <button
          disabled={!fields.banco}
          onClick={() => setStep(1)}
          className="w-full bg-primary text-primary-foreground rounded-md py-3
                     text-sm font-medium disabled:opacity-40 hover:bg-primary/90 transition-colors"
        >
          Continuar
        </button>
      </div>
    );
  }

  // ── Passo 1 — Números do contrato ──────────────────────────────────────────
  if (step === 1) {
    const valid =
      taxa > 0 && saldo > 0 && amort > 0 && amort < saldo &&
      fields.data_proxima_parcela && prazo > 0;

    return (
      <div className="min-h-screen bg-background px-6 py-10 max-w-lg mx-auto">
        <ProgressDots step={1} total={4} />
        <p className="text-xs text-muted-foreground uppercase tracking-widest mb-2">Passo 2 de 4</p>
        <h1 className="font-serif text-2xl font-semibold mb-1">Dados do contrato</h1>
        <p className="text-muted-foreground text-sm mb-8">
          Consulte no app do {BANCOS.find((b) => b.code === fields.banco)?.label || "banco"}.
        </p>

        <div className="space-y-5">
          <Field label="Apelido do imóvel (opcional)" hint="Ex: Apartamento, Casa praia">
            <input
              type="text"
              value={fields.property_apelido}
              onChange={(e) => set("property_apelido", e.target.value)}
              placeholder="Apartamento"
              className={inputCls}
            />
          </Field>

          <Field label="Taxa de juros mensal" hint="Ex: 0,9631 — em percentual">
            <div className="relative">
              <input
                type="text"
                inputMode="decimal"
                value={fields.taxa_mensal_pct}
                onChange={(e) => set("taxa_mensal_pct", e.target.value)}
                placeholder="0,9631"
                className={inputCls + " pr-8"}
              />
              <span className="absolute right-3 top-3 text-muted-foreground text-sm">%</span>
            </div>
            {taxa > 0 && (
              <p className="text-xs text-muted-foreground mt-1">
                = {(taxa_aa * 100).toFixed(2).replace(".", ",")}% a.a. efetiva
              </p>
            )}
          </Field>

          <div className="grid grid-cols-2 gap-4">
            <Field label="Saldo devedor">
              <div className="relative">
                <span className="absolute left-3 top-3 text-muted-foreground text-sm">R$</span>
                <input
                  type="text"
                  inputMode="decimal"
                  value={fields.saldo_devedor}
                  onChange={(e) => set("saldo_devedor", e.target.value)}
                  placeholder="429.629"
                  className={inputCls + " pl-9"}
                />
              </div>
            </Field>

            <Field label="Amortização mensal">
              <div className="relative">
                <span className="absolute left-3 top-3 text-muted-foreground text-sm">R$</span>
                <input
                  type="text"
                  inputMode="decimal"
                  value={fields.amortizacao_mensal}
                  onChange={(e) => set("amortizacao_mensal", e.target.value)}
                  placeholder="2.285"
                  className={inputCls + " pl-9"}
                />
              </div>
            </Field>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Field label="Parcelas restantes">
              <input
                type="number"
                value={fields.prazo_remanescente}
                onChange={(e) => set("prazo_remanescente", e.target.value)}
                placeholder="189"
                className={inputCls}
              />
            </Field>

            <Field label="Próximo vencimento">
              <input
                type="date"
                value={fields.data_proxima_parcela}
                onChange={(e) => set("data_proxima_parcela", e.target.value)}
                className={inputCls}
              />
            </Field>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Field label="Seguro MIP (opcional)" hint="Morte/invalidez">
              <div className="relative">
                <span className="absolute left-3 top-3 text-muted-foreground text-sm">R$</span>
                <input
                  type="text"
                  inputMode="decimal"
                  value={fields.mip_mensal}
                  onChange={(e) => set("mip_mensal", e.target.value)}
                  placeholder="94,45"
                  className={inputCls + " pl-9"}
                />
              </div>
            </Field>

            <Field label="Seguro DFI (opcional)" hint="Danos físicos">
              <div className="relative">
                <span className="absolute left-3 top-3 text-muted-foreground text-sm">R$</span>
                <input
                  type="text"
                  inputMode="decimal"
                  value={fields.dfi_mensal}
                  onChange={(e) => set("dfi_mensal", e.target.value)}
                  placeholder="38,61"
                  className={inputCls + " pl-9"}
                />
              </div>
            </Field>
          </div>
        </div>

        {/* Custos extras */}
        <div className="mt-6 pt-5 border-t border-border">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wide">
                Custos extras mensais
              </p>
              <p className="text-xs text-muted-foreground/60 mt-0.5">
                Taxas, condomínio, ou outros custos não mapeados acima
              </p>
            </div>
            <button
              type="button"
              onClick={addCustoExtra}
              className="text-xs text-primary hover:text-primary/80 transition-colors"
            >
              + Adicionar
            </button>
          </div>

          {fields.custos_extras.map((extra, i) => (
            <div key={i} className="flex gap-2 mb-2 items-start">
              <input
                type="text"
                value={extra.nome}
                onChange={(e) => updateCustoExtra(i, "nome", e.target.value)}
                placeholder="Nome do custo"
                className={inputCls + " flex-1"}
              />
              <div className="relative w-32">
                <span className="absolute left-3 top-3 text-muted-foreground text-sm">R$</span>
                <input
                  type="text"
                  inputMode="decimal"
                  value={extra.valor}
                  onChange={(e) => updateCustoExtra(i, "valor", e.target.value)}
                  placeholder="0"
                  className={inputCls + " pl-9"}
                />
              </div>
              <button
                type="button"
                onClick={() => removeCustoExtra(i)}
                className="text-xs text-muted-foreground hover:text-loss transition-colors pt-3 px-1"
              >
                ✕
              </button>
            </div>
          ))}

          {extras_total > 0 && (
            <p className="text-xs text-muted-foreground mt-2">
              Total custos extras: <span className="text-foreground font-medium">{formatBRL(extras_total)}/mês</span>
            </p>
          )}
        </div>

        <div className="flex gap-3 mt-8">
          <button
            onClick={() => setStep(0)}
            className="flex-1 py-3 rounded-md border border-border text-sm text-muted-foreground
                       hover:text-foreground hover:border-foreground/30 transition-colors"
          >
            Voltar
          </button>
          <button
            disabled={!valid}
            onClick={() => setStep(2)}
            className="flex-1 bg-primary text-primary-foreground rounded-md py-3
                       text-sm font-medium disabled:opacity-40 hover:bg-primary/90 transition-colors"
          >
            Revisar
          </button>
        </div>
      </div>
    );
  }

  // ── Passo 2 — Revisão ──────────────────────────────────────────────────────
  if (step === 2) {
    return (
      <div className="min-h-screen bg-background px-6 py-10 max-w-lg mx-auto">
        <ProgressDots step={2} total={4} />
        <p className="text-xs text-muted-foreground uppercase tracking-widest mb-2">Passo 3 de 4</p>
        <h1 className="font-serif text-2xl font-semibold mb-1">Confere os dados</h1>
        <p className="text-muted-foreground text-sm mb-8">
          Algum valor errado? Volte e corrija.
        </p>

        <div className="border border-border rounded-lg overflow-hidden mb-6">
          {[
            ["Banco", BANCOS.find((b) => b.code === fields.banco)?.label ?? fields.banco],
            ["Sistema", fields.sistema_amortizacao],
            ["Taxa mensal", `${fields.taxa_mensal_pct}% a.m. (${(taxa_aa * 100).toFixed(2).replace(".", ",")}% a.a.)`],
            ["Saldo devedor", formatBRL(saldo)],
            ["Amortização mensal", formatBRL(amort)],
            ["Juros estimados", formatBRL(juros_est)],
            ["Seguros", formatBRL(mip + dfi)],
            ...(extras_total > 0
              ? fields.custos_extras
                  .filter((e) => e.nome.trim() && parseNumber(e.valor) > 0)
                  .map((e) => [`Extra: ${e.nome}`, formatBRL(parseNumber(e.valor))])
              : []),
            ["Parcela total estimada", formatBRL(parcela_est)],
            ["Parcelas restantes", String(prazo)],
            ["Próximo vencimento", fields.data_proxima_parcela],
          ].map(([label, value], i, arr) => (
            <div
              key={label}
              className={`flex justify-between px-5 py-3 ${
                i < arr.length - 1 ? "border-b border-border" : ""
              }`}
            >
              <span className="text-xs text-muted-foreground">{label}</span>
              <span className="text-sm text-foreground font-medium">{value}</span>
            </div>
          ))}
        </div>

        {createContract.error && (
          <p className="text-xs text-loss mb-4">
            {(createContract.error as Error).message}
          </p>
        )}

        <div className="flex gap-3">
          <button
            onClick={() => setStep(1)}
            className="flex-1 py-3 rounded-md border border-border text-sm text-muted-foreground
                       hover:text-foreground hover:border-foreground/30 transition-colors"
          >
            Editar
          </button>
          <button
            onClick={handleSubmit}
            disabled={createContract.isPending}
            className="flex-1 bg-primary text-primary-foreground rounded-md py-3
                       text-sm font-medium disabled:opacity-50 hover:bg-primary/90 transition-colors"
          >
            {createContract.isPending ? "Salvando…" : "Guardar contrato"}
          </button>
        </div>
      </div>
    );
  }

  // ── Passo 3 — Primeiro insight ─────────────────────────────────────────────
  const contract = createContract.data;
  return (
    <div className="min-h-screen bg-background px-6 py-10 max-w-lg mx-auto flex flex-col items-center justify-center text-center">
      <ProgressDots step={3} total={4} />
      <p className="text-xs text-primary uppercase tracking-widest mb-6">Pronto</p>
      <h1 className="font-serif text-3xl font-semibold mb-8">
        Olha o que descobrimos
      </h1>

      <div className="space-y-4 w-full text-left mb-10">
        <InsightItem
          label="Você quita em"
          value={contract ? formatMonthYear(contract.data_quitacao) : "…"}
          highlight
        />
        <InsightItem
          label="Sua taxa"
          value={`${(taxa * 100).toFixed(4).replace(".", ",")}% a.m. (${(taxa_aa * 100).toFixed(2).replace(".", ",")}% a.a.)`}
        />
        <InsightItem
          label="Próxima parcela"
          value={contract ? formatBRL(contract.parcela_total) : "…"}
        />
      </div>

      <button
        onClick={() => navigate({ to: "/dashboard" })}
        className="w-full bg-primary text-primary-foreground rounded-md py-3
                   text-sm font-medium hover:bg-primary/90 transition-colors"
      >
        Ver meu painel
      </button>
    </div>
  );
}

// ── Sub-componentes ────────────────────────────────────────────────────────────

const inputCls =
  "w-full bg-muted border border-border rounded-md px-3 py-3 text-sm text-foreground " +
  "placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary";

function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="text-xs text-muted-foreground uppercase tracking-wide block mb-1.5">
        {label}
        {hint && <span className="normal-case ml-1 text-muted-foreground/60">— {hint}</span>}
      </label>
      {children}
    </div>
  );
}

function InsightItem({
  label,
  value,
  highlight = false,
}: {
  label: string;
  value: string;
  highlight?: boolean;
}) {
  return (
    <div className="border border-border rounded-lg px-5 py-4 flex items-center justify-between">
      <span className="text-sm text-muted-foreground">{label}</span>
      <span
        className={`font-serif font-semibold tabular-nums ${
          highlight ? "text-xl text-primary" : "text-base text-foreground"
        }`}
      >
        {value}
      </span>
    </div>
  );
}
