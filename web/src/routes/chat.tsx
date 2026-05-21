import { createFileRoute, Link, useSearch } from "@tanstack/react-router";
import { useCallback, useEffect, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useActiveContract } from "@/hooks/useContract";
import { useChat } from "@/hooks/useChat";
import { ChatMessageView } from "@/components/chat/ChatMessage";
import { ChatInput } from "@/components/chat/ChatInput";
import { scenariosApi, type ScenarioResponse } from "@/lib/api/client";
import { formatBRL, formatMonthYear } from "@/lib/utils";
import type { ChatAction } from "@/components/chat/types";
import { Sparkles } from "lucide-react";

export const Route = createFileRoute("/chat")({
  component: ChatPage,
  validateSearch: (search: Record<string, unknown>) => ({
    scenario: (search.scenario as string) || undefined,
  }),
});

const GENERIC_SUGGESTIONS = [
  "Por que minha parcela é tão alta?",
  "Esse seguro que vem na parcela é obrigatório?",
  "Vale a pena adiantar um pouquinho todo mês?",
  "Fui enganado na minha taxa de juros?",
  "O que acontece se eu pagar R$ 200 a mais por mês?",
  "Por que tão pouco da parcela abate a dívida?",
];

function buildScenarioSuggestions(s: ScenarioResponse): string[] {
  const nome = s.nome;
  return [
    `Me explica esse plano "${nome}" como se eu não entendesse nada`,
    `Se eu seguir esse plano e perder o emprego por 6 meses, o que acontece?`,
    `Esse plano "${nome}" compromete muito do meu salário?`,
    `Vale a pena aumentar um pouco o valor mensal desse plano?`,
    `Tem algum risco que eu não estou vendo nesse plano?`,
  ];
}

function buildScenarioInsightPrompt(s: ScenarioResponse, contractQuitacao: string): string {
  const meses_cortados = Math.round(
    (new Date(contractQuitacao).getTime() - new Date(s.projecao.data_quitacao).getTime()) / (30.44 * 86400000)
  );

  return (
    `Analise o cenário "${s.nome}" do meu contrato. ` +
    `Parâmetros: aporte mensal extra de R$ ${s.aporte_mensal_extra}` +
    (s.aporte_anual_extra > 0 ? `, aporte anual de R$ ${s.aporte_anual_extra} em ${s.mes_aporte_anual ? `mês ${s.mes_aporte_anual}` : "abril"}` : "") +
    `. ` +
    `Projeção: quita em ${s.projecao.data_quitacao}, economia de R$ ${s.projecao.total_juros_economizados.toFixed(0)} em juros, ` +
    `${s.projecao.parcelas_eliminadas} parcelas eliminadas (${meses_cortados} meses a menos). ` +
    `Comprometimento mensal máximo: R$ ${s.projecao.comprometimento_mensal_max.toFixed(0)}. ` +
    `Me dê 3 insights sobre este plano: pontos fortes, riscos, e uma sugestão de otimização.`
  );
}

function ChatPage() {
  const { data: contract } = useActiveContract();
  const { scenario: scenarioId } = useSearch({ from: "/chat" });
  const { messages, isStreaming, context, sendMessage, clearMessages } = useChat();
  const [prefill, setPrefill] = useState<string | undefined>();
  const scrollRef = useRef<HTMLDivElement>(null);
  const autoSentRef = useRef(false);

  // Fetch the scenario if scenarioId is present
  const { data: scenarios } = useQuery({
    queryKey: ["scenarios", contract?.id],
    queryFn: () => scenariosApi.list(contract!.id),
    enabled: !!contract?.id && !!scenarioId,
  });
  const activeScenario = scenarios?.find((s) => s.id === scenarioId);

  // Auto-send insight prompt when scenario is loaded (once)
  useEffect(() => {
    if (activeScenario && contract && !autoSentRef.current && messages.length === 0) {
      autoSentRef.current = true;
      const prompt = buildScenarioInsightPrompt(activeScenario, contract.data_quitacao);
      sendMessage(contract.id, prompt);
    }
  }, [activeScenario, contract, messages.length, sendMessage]);

  // Auto-scroll
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  function handleSend(text: string) {
    if (!contract) return;
    setPrefill(undefined);
    sendMessage(contract.id, text);
  }

  const handleAction = useCallback((action: ChatAction) => {
    switch (action.type) {
      case "prefill":
        setPrefill(action.text);
        break;
      case "save_scenario":
        break;
      case "expand":
        break;
    }
  }, []);

  if (!contract) return null;

  const hasMessages = messages.length > 0;
  const suggestions = activeScenario ? buildScenarioSuggestions(activeScenario) : GENERIC_SUGGESTIONS;
  const isScenarioMode = !!activeScenario;

  return (
    <div className="h-screen bg-background flex flex-col">
      {/* Nav */}
      <nav className="flex items-center justify-between px-6 py-3 border-b border-border shrink-0">
        <Link to="/dashboard" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
          ← Dashboard
        </Link>
        <div className="flex items-center gap-3">
          <span className="font-serif text-sm font-semibold">
            {isScenarioMode ? "Sobre o plano" : "Tire suas dúvidas"}
          </span>
          {context && (
            <span className="text-xs text-muted-foreground">
              {context.banco.toUpperCase()} · {context.prazo_remanescente} parcelas
            </span>
          )}
        </div>
        <button
          onClick={() => { clearMessages(); autoSentRef.current = false; }}
          className="text-xs text-muted-foreground hover:text-foreground transition-colors"
        >
          Limpar
        </button>
      </nav>

      {/* Scenario context banner */}
      {isScenarioMode && activeScenario && (
        <div className="px-6 py-3 bg-primary/5 border-b border-primary/20 shrink-0">
          <div className="max-w-2xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles size={14} className="text-primary" />
              <span className="text-xs text-primary font-medium">
                Conversando sobre: {activeScenario.nome}
              </span>
            </div>
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              <span>Quita em {formatMonthYear(activeScenario.projecao.data_quitacao)}</span>
              <span className="text-gain">−{formatBRL(activeScenario.projecao.total_juros_economizados)}</span>
            </div>
          </div>
        </div>
      )}

      {/* Messages area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-6" role="log" aria-live="polite">
        <div className="max-w-2xl mx-auto space-y-6">
          {/* Empty state */}
          {!hasMessages && !isScenarioMode && (
            <div className="pt-12 pb-8">
              <p className="text-xs text-primary uppercase tracking-widest mb-4 text-center">
                {contract.banco.toUpperCase()} · {contract.sistema_amortizacao} · {contract.prazo_remanescente} parcelas
              </p>
              <h2 className="font-serif text-2xl font-semibold text-center mb-2">
                Tire suas dúvidas
              </h2>
              <p className="text-sm text-muted-foreground text-center mb-8">
                Pergunte com suas palavras. Eu explico em português e mostro a conta.
              </p>
              <div className="space-y-2">
                {suggestions.map((s) => (
                  <button
                    key={s}
                    onClick={() => handleSend(s)}
                    className="w-full text-left px-4 py-3 rounded-lg border border-border
                               text-sm text-muted-foreground hover:text-foreground
                               hover:border-foreground/20 transition-colors"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Scenario auto-loading state */}
          {!hasMessages && isScenarioMode && (
            <div className="pt-16 pb-8 text-center">
              <Sparkles size={24} className="text-primary mx-auto mb-4" />
              <p className="font-serif text-xl font-semibold mb-2">
                Analisando o plano "{activeScenario?.nome}"…
              </p>
              <p className="text-sm text-muted-foreground">
                A IA está gerando insights personalizados.
              </p>
            </div>
          )}

          {/* Messages */}
          {messages.map((msg, i) => (
            <ChatMessageView
              key={i}
              message={msg}
              isStreaming={isStreaming}
              isLastMessage={i === messages.length - 1}
              onAction={handleAction}
            />
          ))}

          {/* Streaming indicator */}
          {isStreaming && messages.length > 0 && messages[messages.length - 1].role === "user" && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <div className="w-3 h-3 border border-primary border-t-transparent rounded-full animate-spin" />
              <span>Pensando…</span>
            </div>
          )}

          {/* Follow-up suggestions after scenario analysis */}
          {isScenarioMode && hasMessages && !isStreaming && messages[messages.length - 1]?.role === "assistant" && (
            <div className="pt-4">
              <p className="text-xs text-muted-foreground mb-2">Perguntas relacionadas:</p>
              <div className="flex flex-wrap gap-2">
                {suggestions.slice(0, 3).map((s) => (
                  <button
                    key={s}
                    onClick={() => handleSend(s)}
                    className="text-xs px-3 py-1.5 rounded-full border border-border
                               text-muted-foreground hover:text-foreground
                               hover:border-foreground/20 transition-colors"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input */}
      <ChatInput onSend={handleSend} isStreaming={isStreaming} prefill={prefill} />
    </div>
  );
}
