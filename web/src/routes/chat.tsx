import { createFileRoute, Link } from "@tanstack/react-router";
import { useCallback, useEffect, useRef, useState } from "react";
import { useActiveContract } from "@/hooks/useContract";
import { useChat } from "@/hooks/useChat";
import { ChatMessageView } from "@/components/chat/ChatMessage";
import { ChatInput } from "@/components/chat/ChatInput";
import type { ChatAction } from "@/components/chat/types";

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
  const { data: contract } = useActiveContract();
  const { messages, isStreaming, context, sendMessage, clearMessages } = useChat();
  const [prefill, setPrefill] = useState<string | undefined>();
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll on new messages
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
        // TODO: scenariosApi.create()
        break;
      case "expand":
        // Handled locally in ToolResultCard
        break;
    }
  }, []);

  if (!contract) return null;

  const hasMessages = messages.length > 0;

  return (
    <div className="h-screen bg-background flex flex-col">
      {/* Nav */}
      <nav className="flex items-center justify-between px-6 py-3 border-b border-border shrink-0">
        <Link to="/dashboard" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
          ← Dashboard
        </Link>
        <div className="flex items-center gap-3">
          <span className="font-serif text-sm font-semibold">Chat IA</span>
          {context && (
            <span className="text-xs text-muted-foreground">
              {context.banco.toUpperCase()} · {context.prazo_remanescente} parcelas
            </span>
          )}
        </div>
        <button
          onClick={clearMessages}
          className="text-xs text-muted-foreground hover:text-foreground transition-colors"
        >
          Limpar
        </button>
      </nav>

      {/* Messages area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-6" role="log" aria-live="polite">
        <div className="max-w-2xl mx-auto space-y-6">
          {/* Empty state */}
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

          {/* Streaming indicator when no parts yet */}
          {isStreaming && messages.length > 0 && messages[messages.length - 1].role === "user" && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <div className="w-3 h-3 border border-primary border-t-transparent rounded-full animate-spin" />
              <span>Pensando…</span>
            </div>
          )}
        </div>
      </div>

      {/* Input */}
      <ChatInput onSend={handleSend} isStreaming={isStreaming} prefill={prefill} />
    </div>
  );
}
