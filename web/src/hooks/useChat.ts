import { useCallback, useRef, useState } from "react";
import { getToken } from "@/lib/auth";

const BASE_URL = import.meta.env.VITE_API_URL ?? "/api";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ToolCallEvent {
  tool: string;
  arguments: string;
}

interface UseChatReturn {
  messages: ChatMessage[];
  isStreaming: boolean;
  toolCalls: ToolCallEvent[];
  sendMessage: (contractId: string, message: string) => Promise<void>;
  clearMessages: () => void;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [toolCalls, setToolCalls] = useState<ToolCallEvent[]>([]);
  const abortRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(async (contractId: string, message: string) => {
    // Adiciona mensagem do usuário imediatamente
    setMessages((prev) => [...prev, { role: "user", content: message }]);
    setIsStreaming(true);
    setToolCalls([]);

    const token = await getToken();

    // Aborta stream anterior se existir
    abortRef.current?.abort();
    abortRef.current = new AbortController();

    let assistantText = "";

    try {
      const response = await fetch(`${BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ contract_id: contractId, message }),
        signal: abortRef.current.signal,
      });

      if (!response.ok || !response.body) {
        const err = await response.json().catch(() => ({ detail: "Erro na API" }));
        setMessages((prev) => [...prev, { role: "assistant", content: `Erro: ${err.detail}` }]);
        setIsStreaming(false);
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Processar linhas SSE completas
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? ""; // última linha pode estar incompleta

        let eventType = "";
        for (const line of lines) {
          if (line.startsWith("event: ")) {
            eventType = line.slice(7).trim();
          } else if (line.startsWith("data: ") && eventType) {
            const data = line.slice(6);
            try {
              const parsed = JSON.parse(data);
              handleEvent(eventType, parsed);
            } catch {
              // ignora linhas mal formadas
            }
            eventType = "";
          }
        }
      }

      // Garantir que a mensagem final é adicionada
      if (assistantText) {
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.role === "assistant") return prev;
          return [...prev, { role: "assistant", content: assistantText }];
        });
      }
    } catch (e) {
      if ((e as Error).name !== "AbortError") {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: `Erro: ${(e as Error).message}` },
        ]);
      }
    } finally {
      setIsStreaming(false);
    }

    function handleEvent(type: string, data: Record<string, unknown>) {
      switch (type) {
        case "tool_call":
          setToolCalls((prev) => [...prev, data as unknown as ToolCallEvent]);
          break;

        case "text":
          // Mensagem completa de um item
          assistantText = (data.content as string) ?? "";
          setMessages((prev) => {
            const newMessages = [...prev];
            const lastIdx = newMessages.length - 1;
            if (lastIdx >= 0 && newMessages[lastIdx].role === "assistant") {
              newMessages[lastIdx] = { role: "assistant", content: assistantText };
            } else {
              newMessages.push({ role: "assistant", content: assistantText });
            }
            return newMessages;
          });
          break;

        case "text_delta":
          // Chunk progressivo
          assistantText += (data.delta as string) ?? "";
          setMessages((prev) => {
            const newMessages = [...prev];
            const lastIdx = newMessages.length - 1;
            if (lastIdx >= 0 && newMessages[lastIdx].role === "assistant") {
              newMessages[lastIdx] = { role: "assistant", content: assistantText };
            } else {
              newMessages.push({ role: "assistant", content: assistantText });
            }
            return newMessages;
          });
          break;

        case "error":
          setMessages((prev) => [
            ...prev,
            { role: "assistant", content: `Erro: ${data.detail ?? "desconhecido"}` },
          ]);
          break;
      }
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setToolCalls([]);
  }, []);

  return { messages, isStreaming, toolCalls, sendMessage, clearMessages };
}
