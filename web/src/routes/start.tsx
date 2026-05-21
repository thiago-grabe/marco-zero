import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { contractsApi } from "@/lib/api/client";
import { useContractStore } from "@/stores/contract";

export const Route = createFileRoute("/start")({
  component: Start,
});

const BANCOS = [
  { code: "itau", label: "Itaú" },
  { code: "caixa", label: "Caixa" },
  { code: "bb", label: "BB" },
  { code: "bradesco", label: "Bradesco" },
  { code: "santander", label: "Santander" },
  { code: "outro", label: "Outro" },
];

function parseNumber(s: string): number {
  return parseFloat(s.replace(",", ".").replace(/[^\d.]/g, "")) || 0;
}

function Start() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const setActiveContractId = useContractStore((s) => s.setActiveContractId);

  const [parcela, setParcela] = useState("");
  const [banco, setBanco] = useState("");
  const [saldo, setSaldo] = useState("");
  const [taxa, setTaxa] = useState("");
  const [showHelp, setShowHelp] = useState(false);

  const taxaNum = parseNumber(taxa);
  const taxaDecimal = taxaNum > 0 ? taxaNum / 100 : undefined;
  const isEstimated = !taxaDecimal;

  const mutation = useMutation({
    mutationFn: () =>
      contractsApi.createQuick({
        parcela_mensal: parseNumber(parcela),
        banco,
        saldo_devedor: parseNumber(saldo),
        ...(taxaDecimal ? { taxa_mensal: taxaDecimal } : {}),
      }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["contracts"] });
      setActiveContractId(data.id);
      // Salvar alertas para a tela de insight
      if (data.alertas?.length > 0) {
        sessionStorage.setItem("tenor-alertas", JSON.stringify(data.alertas));
      } else {
        sessionStorage.removeItem("tenor-alertas");
      }
      navigate({
        to: "/insight",
        search: { estimated: isEstimated },
      });
    },
  });

  const valid = parseNumber(parcela) > 0 && banco && parseNumber(saldo) > 0;

  return (
    <div className="min-h-screen bg-background px-6 py-10 max-w-lg mx-auto">
      <Link to="/" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
        ← Voltar
      </Link>

      <div className="mt-8 mb-8">
        <h1 className="font-serif text-2xl font-semibold mb-2">
          Só preciso de alguns números
        </h1>
        <p className="text-muted-foreground text-sm leading-relaxed">
          Você acha todos no app do seu banco ou no boleto do mês.
          Não precisa acertar de primeira.
        </p>
      </div>

      <div className="space-y-6">
        {/* Parcela */}
        <div>
          <label className="text-sm text-foreground block mb-2">
            Quanto você paga por mês?
          </label>
          <div className="relative">
            <span className="absolute left-3 top-3 text-muted-foreground text-sm">R$</span>
            <input
              type="text"
              inputMode="decimal"
              value={parcela}
              onChange={(e) => setParcela(e.target.value)}
              placeholder="1.247,00"
              className="w-full bg-muted border border-border rounded-md pl-9 pr-4 py-3
                         text-sm text-foreground placeholder:text-muted-foreground
                         focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
          <p className="text-xs text-muted-foreground mt-1.5">
            É o valor do boleto do mês
          </p>
        </div>

        {/* Banco */}
        <div>
          <label className="text-sm text-foreground block mb-2">
            Qual o banco?
          </label>
          <div className="grid grid-cols-3 gap-2">
            {BANCOS.map((b) => (
              <button
                key={b.code}
                onClick={() => setBanco(b.code)}
                className={`py-3 rounded-lg border text-sm font-medium transition-all ${
                  banco === b.code
                    ? "border-primary text-primary bg-primary/5"
                    : "border-border text-muted-foreground hover:border-foreground/30 hover:text-foreground"
                }`}
              >
                {b.label}
              </button>
            ))}
          </div>
        </div>

        {/* Saldo */}
        <div>
          <label className="text-sm text-foreground block mb-2">
            Quanto ainda falta pagar?
          </label>
          <div className="relative">
            <span className="absolute left-3 top-3 text-muted-foreground text-sm">R$</span>
            <input
              type="text"
              inputMode="decimal"
              value={saldo}
              onChange={(e) => setSaldo(e.target.value)}
              placeholder="429.000,00"
              className="w-full bg-muted border border-border rounded-md pl-9 pr-4 py-3
                         text-sm text-foreground placeholder:text-muted-foreground
                         focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
          <p className="text-xs text-muted-foreground mt-1.5">
            No app do banco aparece como "saldo devedor"
          </p>
        </div>

        {/* Taxa (opcional) */}
        <div>
          <label className="text-sm text-foreground block mb-2">
            Sabe a taxa de juros? <span className="text-muted-foreground">(opcional)</span>
          </label>
          <div className="relative">
            <input
              type="text"
              inputMode="decimal"
              value={taxa}
              onChange={(e) => setTaxa(e.target.value)}
              placeholder="0,96"
              className="w-full bg-muted border border-border rounded-md pl-4 pr-12 py-3
                         text-sm text-foreground placeholder:text-muted-foreground
                         focus:outline-none focus:ring-1 focus:ring-primary"
            />
            <span className="absolute right-3 top-3 text-muted-foreground text-sm">% a.m.</span>
          </div>
          <p className="text-xs text-muted-foreground mt-1.5">
            {taxa && taxaDecimal
              ? `= ${((1 + taxaDecimal) ** 12 * 100 - 100).toFixed(2).replace(".", ",")}% ao ano`
              : "Aparece no contrato como \"taxa mensal\". Sem ela, os valores são estimados."
            }
          </p>
        </div>
      </div>

      {/* Help */}
      <button
        onClick={() => setShowHelp(!showHelp)}
        className="text-xs text-muted-foreground hover:text-foreground mt-4 transition-colors"
      >
        Não sei algum desses → me ajuda a achar
      </button>

      {showHelp && (
        <div className="mt-3 border border-border rounded-lg p-4 bg-card text-xs text-muted-foreground space-y-3">
          <div>
            <p className="text-foreground font-medium mb-1">Valor da parcela</p>
            <p>É o valor do boleto que você paga todo mês. Pode estar no e-mail do banco ou no app.</p>
          </div>
          <div>
            <p className="text-foreground font-medium mb-1">Saldo devedor</p>
            <p>No app do banco → Financiamentos → seu contrato. Aparece como "saldo devedor" ou "saldo atual".</p>
          </div>
        </div>
      )}

      {/* Submit */}
      {mutation.error && (
        <p className="text-xs text-loss mt-4">{(mutation.error as Error).message}</p>
      )}

      <button
        onClick={() => mutation.mutate()}
        disabled={!valid || mutation.isPending}
        className="w-full mt-8 bg-primary text-primary-foreground rounded-md py-3.5
                   text-sm font-medium hover:bg-primary/90 transition-colors
                   disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {mutation.isPending ? "Calculando…" : "Ver meu financiamento"}
      </button>

      <p className="text-center text-xs text-muted-foreground mt-4">
        Quer preencher todos os dados? <Link to="/onboarding" className="text-foreground underline underline-offset-2">Modo avançado</Link>
      </p>
    </div>
  );
}
