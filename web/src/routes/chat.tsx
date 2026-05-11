import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useActiveContract } from "@/hooks/useContract";
import { useChat } from "@/hooks/useChat";

export const Route = createFileRoute("/chat")({
  component: ChatPage,
});

const SUGGESTIONS = [
  "Quanto economizo amortizando R$ 30 mil?",
  "E se eu amortizar R$ 5 mil por mês?",
  "Compare cenários: 3k/mês vs 5k/mês vs 10k/mês",
  "Quanto pago a mais esperando 15 dias para amortizar?",
  "Qual a composição da minha parcela atual?",
];

function ChatPage() {
  const navigate = useNavigate();
  const { authenticated } = useAuth();
  const { data: contract } = useActiveContract();
  const { messages, isStreaming, toolCalls, sendMessage, clearMessages } = useChat();
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!authenticated) navigate({ to: "/login" });
  }, [authenticated, navigate]);

  // Auto-scroll ao receber novas mensagens
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, toolCalls]);

  function handleSend(text?: string) {
    const msg = text ?? input.trim();
    if (!msg || !contract || isStreaming) return;
    setInput("");
    sendMessage(contract.id, msg);
  }

  if (!contract) return null;

  const hasMessages = messages.length > 0;

  return (
    <div className="h-screen bg-background flex flex-col">
      {/* Nav */}
      <nav className="flex items-center justify-between px-6 py-3 border-b border-border shrink-0">
        <Link to="/dashboard" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
          ← Dashboard
        </Link>
        <span className="font-serif text-sm font-semibold">Chat IA</span>
        <button
          onClick={clearMessages}
          className="text-xs text-muted-foreground hover:text-foreground transition-colors"
        >
          Limpar
        </button>
      </nav>

      {/* Messages area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-6">
        <div className="max-w-2xl mx-auto space-y-6">
          {/* Estado vazio */}
          {!hasMessages && (
            <div className="pt-12 pb-8">
              <p className="text-xs text-primary uppercase tracking-widest mb-4 text-center">
                {contract.banco.toUpperCase()} · {contract.sistema_amortizacao} · {contract.prazo_remanescente} parcelas
              </p>
              <h2 className="font-serif text-2xl font-semibold text-center mb-2">
                Pergunte sobre seu contrato
              </h2>
              <p className="text-sm text-muted-foreground text-center mb-8">
                O motor calcula; a IA explica. Números nunca são inventados.
              </p>

              <div className="space-y-2">
                {SUGGESTIONS.map((s) => (
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

          {/* Mensagens */}
          {messages.map((msg, i) => (
            <div key={i} className={msg.role === "user" ? "flex justify-end" : ""}>
              <div
                className={
                  msg.role === "user"
                    ? "bg-primary/10 border border-primary/20 rounded-lg px-4 py-3 max-w-[80%]"
                    : "max-w-[95%]"
                }
              >
                {msg.role === "assistant" ? (
                  <div className="prose prose-invert prose-sm max-w-none text-foreground leading-relaxed whitespace-pre-wrap">
                    {msg.content}
                  </div>
                ) : (
                  <p className="text-sm text-foreground">{msg.content}</p>
                )}
              </div>
            </div>
          ))}

          {/* Indicador de tool calls ativas */}
          {isStreaming && toolCalls.length > 0 && (
            <div className="space-y-1">
              {toolCalls.map((tc, i) => (
                <div key={i} className="flex items-center gap-2 text-xs text-muted-foreground">
                  <div className="w-3 h-3 border border-primary border-t-transparent rounded-full animate-spin" />
                  <span>
                    {tc.tool === "projetar_cenario"
                      ? "Projetando cenário…"
                      : tc.tool === "simular_amortizacao"
                        ? "Simulando amortização…"
                        : tc.tool === "comparar_cenarios"
                          ? "Comparando cenários…"
                          : tc.tool === "calcular_parcela"
                            ? "Calculando parcela…"
                            : tc.tool === "calcular_pro_rata"
                              ? "Calculando pró-rata…"
                              : `Executando ${tc.tool}…`}
                  </span>
                </div>
              ))}
            </div>
          )}

          {/* Streaming sem tool calls = gerando texto */}
          {isStreaming && toolCalls.length === 0 && messages[messages.length - 1]?.role === "user" && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <div className="w-3 h-3 border border-primary border-t-transparent rounded-full animate-spin" />
              <span>Pensando…</span>
            </div>
          )}
        </div>
      </div>

      {/* Input */}
      <div className="shrink-0 border-t border-border px-6 py-4">
        <div className="max-w-2xl mx-auto flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
            placeholder="Pergunte sobre seu financiamento…"
            disabled={isStreaming}
            className="flex-1 bg-muted border border-border rounded-md px-4 py-3
                       text-sm text-foreground placeholder:text-muted-foreground
                       focus:outline-none focus:ring-1 focus:ring-primary
                       disabled:opacity-50"
          />
          <button
            onClick={() => handleSend()}
            disabled={isStreaming || !input.trim()}
            className="bg-primary text-primary-foreground px-5 py-3 rounded-md text-sm font-medium
                       hover:bg-primary/90 transition-colors disabled:opacity-40"
          >
            Enviar
          </button>
        </div>
        <p className="max-w-2xl mx-auto text-xs text-muted-foreground mt-2 text-center">
          Números calculados pelo motor SAC — a IA não calcula por conta própria.
        </p>
      </div>
    </div>
  );
}
